import streamlit as st
import requests
import time
from pathlib import Path
from typing import Dict, Optional

API_URL = "http://localhost:8000"
DOWNLOAD_DIR = Path("./downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Audio Pipeline",
    page_icon="",
    layout="wide"
)

st.title("Audio Track Separator")
st.markdown("Upload an audio file to separate it into multiple tracks")


def get_api_config() -> Optional[Dict]:
    try:
        response = requests.get(f"{API_URL}/config", timeout=5)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None


def upload_and_process(uploaded_file) -> Optional[str]:
    if uploaded_file is None:
        return None

    try:
        files = {"file": (uploaded_file.name, uploaded_file, "audio/wav")}
        response = requests.post(f"{API_URL}/process", files=files, timeout=300)

        if response.status_code == 200:
            data = response.json()
            return data.get("job_id")
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None


def get_job_status(job_id: str) -> Optional[Dict]:
    try:
        response = requests.get(f"{API_URL}/job/{job_id}", timeout=10)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None


def download_track(job_id: str, track_name: str) -> bool:
    try:
        response = requests.get(
            f"{API_URL}/download/{job_id}/{track_name}",
            timeout=60,
            stream=True
        )

        if response.status_code == 200:
            file_path = DOWNLOAD_DIR / f"{track_name}.wav"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return True
        return False

    except requests.exceptions.RequestException:
        return False


def download_all_tracks(job_id: str) -> bool:
    try:
        response = requests.get(
            f"{API_URL}/download/{job_id}/all",
            timeout=60,
            stream=True
        )

        if response.status_code == 200:
            file_path = DOWNLOAD_DIR / f"tracks_{job_id}.zip"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return True
        return False

    except requests.exceptions.RequestException:
        return False


with st.sidebar:
    st.header("Configuration")
    api_config = get_api_config()

    if api_config:
        st.success("API Connected")
        st.write(f"Max file size: {api_config.get('max_file_size_mb', 'N/A')} MB")
        st.write(f"Supported formats: {', '.join(api_config.get('supported_formats', []))}")
    else:
        st.error("API Connection Failed")
        st.info(f"Make sure API is running at {API_URL}")

tab1, tab2 = st.tabs(["Upload & Process", "View Results"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["wav", "mp3", "flac", "ogg"],
            help="Select an audio file to process"
        )

    with col2:
        if uploaded_file is not None:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / (1024*1024):.2f} MB")

    if st.button("Process Audio", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.error("Please upload a file first")
        else:
            with st.spinner("Uploading and processing..."):
                job_id = upload_and_process(uploaded_file)

                if job_id:
                    st.success(f"Processing started! Job ID: {job_id}")
                    st.session_state.job_id = job_id
                    st.rerun()

with tab2:
    if "job_id" in st.session_state:
        job_id = st.session_state.job_id
        st.write(f"**Job ID:** `{job_id}`")

        with st.spinner("Fetching status..."):
            status = get_job_status(job_id)

        if status:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Status", status.get("status", "unknown").upper())

            with col2:
                total_stages = len(status.get("stages", []))
                completed_stages = sum(
                    1 for s in status.get("stages", [])
                    if s.get("status") == "completed"
                )
                st.metric("Stages", f"{completed_stages}/{total_stages}")

            st.subheader("Pipeline Progress")

            for stage in status.get("stages", []):
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])

                    status_emoji = {
                        "completed": "[DONE]",
                        "processing": "[RUNNING]",
                        "pending": "[PENDING]",
                        "failed": "[FAILED]"
                    }.get(stage.get("status"), "[?]")

                    with col1:
                        st.write(f"{status_emoji} **{stage.get('name')}**")

                    with col2:
                        st.caption(stage.get("processor_type", ""))

                    with col3:
                        duration = stage.get("duration_seconds")
                        if duration:
                            st.caption(f"{duration:.1f}s")

                    if stage.get("error"):
                        st.error(stage.get("error"))

            if status.get("status") == "completed":
                st.subheader("Output Tracks")

                outputs = status.get("outputs", {})

                if outputs:
                    cols = st.columns(3)
                    track_names = list(outputs.keys())

                    for idx, track_name in enumerate(track_names):
                        with cols[idx % 3]:
                            if st.button(
                                f"Download {track_name}",
                                key=f"btn_{track_name}",
                                use_container_width=True
                            ):
                                with st.spinner(f"Downloading {track_name}..."):
                                    if download_track(job_id, track_name):
                                        st.success(f"Downloaded {track_name}.wav")
                                    else:
                                        st.error(f"Failed to download {track_name}")

                    st.divider()

                    if st.button(
                        "Download All Tracks (ZIP)",
                        use_container_width=True,
                        type="secondary"
                    ):
                        with st.spinner("Preparing download..."):
                            if download_all_tracks(job_id):
                                st.success(f"Downloaded tracks_{job_id}.zip")
                            else:
                                st.error("Failed to download tracks")

                    st.info(f"Downloaded files are available in: {DOWNLOAD_DIR.absolute()}")

    else:
        st.info("Upload and process an audio file to view results")

    st.divider()

    st.subheader("Load Previous Job")
    job_id_input = st.text_input(
        "Enter Job ID",
        placeholder="Paste a previous job ID here"
    )

    if st.button("Load Job", use_container_width=True):
        if job_id_input:
            st.session_state.job_id = job_id_input
            st.rerun()