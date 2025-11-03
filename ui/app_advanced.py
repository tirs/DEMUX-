import sys
import os

# Set matplotlib backend IMMEDIATELY, before any other imports
import matplotlib
matplotlib.use('Agg')
# Force matplotlib to initialize all submodules
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.axes
from matplotlib.figure import Figure

import streamlit as st
import requests
import time
import json
from pathlib import Path
from typing import Dict, Optional, List
import numpy as np
import librosa
import librosa.display
import soundfile as sf
from datetime import datetime
import base64
from io import BytesIO

API_URL = "http://localhost:8000"
DOWNLOAD_DIR = Path("./downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Audio Pipeline - Advanced",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .stage-completed { color: #00AA00; font-weight: bold; }
        .stage-processing { color: #FF9900; font-weight: bold; }
        .stage-failed { color: #FF0000; font-weight: bold; }
        .visualization-title { font-size: 18px; font-weight: bold; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("Audio Track Separator - Advanced")
st.markdown("Professional audio separation with visualization and analysis")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

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


def download_track(job_id: str, track_name: str) -> Optional[bytes]:
    try:
        response = requests.get(
            f"{API_URL}/download/{job_id}/{track_name}",
            timeout=60,
            stream=True
        )
        if response.status_code == 200:
            return response.content
        return None
    except requests.exceptions.RequestException:
        return None


def download_all_tracks(job_id: str) -> Optional[bytes]:
    try:
        response = requests.get(
            f"{API_URL}/download/{job_id}/all",
            timeout=60,
            stream=True
        )
        if response.status_code == 200:
            return response.content
        return None
    except requests.exceptions.RequestException:
        return None


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

@st.cache_data
def load_audio_for_viz(audio_bytes: bytes) -> tuple:
    """Load audio and return waveform data"""
    try:
        audio_array, sr = librosa.load(BytesIO(audio_bytes), sr=None)
        return audio_array, sr
    except Exception as e:
        st.error(f"Could not load audio: {e}")
        return None, None


def plot_waveform(audio_array: np.ndarray, sr: int, title: str = "Waveform") -> Figure:
    """Create waveform visualization"""
    try:
        # Create new figure explicitly
        fig = Figure(figsize=(12, 4))
        ax = fig.add_subplot(111)

        times = np.arange(len(audio_array)) / sr
        ax.plot(times, audio_array, linewidth=0.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating waveform: {str(e)}")
        return None


def plot_spectrogram(audio_array: np.ndarray, sr: int, title: str = "Spectrogram") -> Figure:
    """Create spectrogram visualization"""
    try:
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)

        # Compute STFT
        D = librosa.stft(audio_array)
        S_db = librosa.power_to_db(np.abs(D), ref=np.max)

        # Plot spectrogram
        img = librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', ax=ax, cmap='viridis')
        ax.set_title(title)
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        fig.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating spectrogram: {str(e)}")
        return None


def get_audio_stats(audio_array: np.ndarray, sr: int) -> Dict:
    """Calculate audio statistics"""
    duration = len(audio_array) / sr
    rms = np.sqrt(np.mean(audio_array ** 2))
    peak = np.max(np.abs(audio_array))

    return {
        "Duration (s)": f"{duration:.2f}",
        "Sample Rate": f"{sr} Hz",
        "Samples": f"{len(audio_array):,}",
        "RMS": f"{rms:.4f}",
        "Peak": f"{peak:.4f}",
        "Channels": "Mono" if audio_array.ndim == 1 else f"Multi ({audio_array.shape[0]})"
    }


def generate_report(job_id: str, status: Dict, audio_stats: Dict = None) -> str:
    """Generate analysis report"""
    report = f"""
    # Audio Processing Report

    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Job ID: {job_id}

    ## Processing Status
    - Status: {status.get('status', 'unknown').upper()}
    - Total Stages: {len(status.get('stages', []))}
    - Completed Stages: {sum(1 for s in status.get('stages', []) if s.get('status') == 'completed')}

    ## Stage Details
    """

    for stage in status.get('stages', []):
        duration = stage.get('duration_seconds', 0)
        report += f"\n### {stage.get('name')} ({stage.get('status')})\n"
        report += f"- Type: {stage.get('processor_type', 'N/A')}\n"
        report += f"- Duration: {duration:.2f}s\n"
        if stage.get('error'):
            report += f"- Error: {stage.get('error')}\n"

    if audio_stats:
        report += "\n## Audio Statistics\n"
        for key, value in audio_stats.items():
            report += f"- {key}: {value}\n"

    outputs = status.get('outputs', {})
    if outputs:
        report += "\n## Output Tracks\n"
        for track in outputs.keys():
            report += f"- {track}\n"

    return report


# ============================================================================
# MAIN UI
# ============================================================================

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    api_config = get_api_config()

    if api_config:
        st.success("API Connected")
        st.metric("Max File Size", f"{api_config.get('max_file_size_mb', 'N/A')} MB")
        st.metric("Supported Formats", ", ".join(api_config.get('supported_formats', [])))
    else:
        st.error("API Connection Failed")
        st.info(f"Make sure API is running at {API_URL}")

    st.divider()
    st.markdown("### Display Options")
    show_waveforms = st.checkbox("Show Waveforms", value=True)
    show_spectrograms = st.checkbox("Show Spectrograms", value=True)
    show_stats = st.checkbox("Show Audio Stats", value=True)
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)


# Main Tabs
tab1, tab2, tab3 = st.tabs(["Upload & Process", "Results & Visualization", "Help & Info"])

# ============================================================================
# TAB 1: UPLOAD & PROCESS
# ============================================================================

with tab1:
    st.subheader("Upload Audio File")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["wav", "mp3", "flac", "ogg", "m4a"],
            help="Select an audio file to process (max 500MB)"
        )

    with col2:
        if uploaded_file is not None:
            st.metric("File Name", uploaded_file.name)
            st.metric("File Size", f"{uploaded_file.size / (1024*1024):.2f} MB")

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Process Audio", type="primary", use_container_width=True):
            if uploaded_file is None:
                st.error("Please upload a file first")
            else:
                with st.spinner("Uploading and processing..."):
                    job_id = upload_and_process(uploaded_file)

                    if job_id:
                        st.success("Processing started!")
                        st.session_state.job_id = job_id
                        st.session_state.uploaded_file = uploaded_file
                        time.sleep(1)
                        st.switch_to_tab("Results & Visualization")
                        st.rerun()

    with col2:
        st.markdown("")
        if st.button("Save Example", use_container_width=True):
            st.info("Example audio file saved to /Audio folder")

    st.divider()
    st.markdown("### Processing Pipeline Stages:")
    st.markdown("""
    1. **Audio Loading** - Load and validate audio file
    2. **Audio Separation** - Use Demucs to separate tracks
    3. **Normalization** - Normalize and optimize audio
    4. **Post-processing** - Final adjustments
    """)


# ============================================================================
# TAB 2: RESULTS & VISUALIZATION
# ============================================================================

with tab2:
    if "job_id" in st.session_state:
        job_id = st.session_state.job_id

        # Auto-refresh logic
        if auto_refresh:
            status_placeholder = st.empty()
            status_placeholder.info("Auto-refreshing every 5 seconds...")
            time.sleep(2)

        with st.spinner("Fetching job status..."):
            status = get_job_status(job_id)

        if status:
            # Header with Job Info
            st.subheader(f"Job: `{job_id}`")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                status_text = status.get("status", "unknown").upper()
                st.metric("Status", status_text)

            with col2:
                total_stages = len(status.get("stages", []))
                completed_stages = sum(1 for s in status.get("stages", []) if s.get("status") == "completed")
                st.metric("Progress", f"{completed_stages}/{total_stages}")

            with col3:
                total_time = sum(s.get("duration_seconds", 0) for s in status.get("stages", []))
                st.metric("Total Time", f"{total_time:.1f}s")

            with col4:
                output_count = len(status.get("outputs", {}))
                st.metric("Outputs", output_count)

            st.divider()

            # Pipeline Progress
            st.markdown("### Pipeline Progress")

            for stage in status.get("stages", []):
                stage_status = stage.get("status")
                status_text = {
                    "completed": "[DONE]",
                    "processing": "[RUNNING]",
                    "pending": "[PENDING]",
                    "failed": "[FAILED]"
                }.get(stage_status, "[?]")

                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        st.write(f"{status_text} **{stage.get('name')}**")

                    with col2:
                        st.caption(stage.get("processor_type", ""))

                    with col3:
                        duration = stage.get("duration_seconds")
                        if duration:
                            st.caption(f"Time: {duration:.2f}s")

                    with col4:
                        if stage_status == "completed":
                            st.caption("DONE")
                        elif stage_status == "processing":
                            st.caption("RUNNING")

                    if stage.get("error"):
                        st.error(f"Error: {stage.get('error')}")

            # Results Section
            if status.get("status") == "completed":
                st.divider()
                st.markdown("### Separated Tracks")

                outputs = status.get("outputs", {})

                if outputs:
                    # Create tabs for each track
                    track_tabs = st.tabs([f"{track}" for track in outputs.keys()])

                    for tab_idx, (track_name, track_data) in enumerate(outputs.items()):
                        with track_tabs[tab_idx]:
                            audio_content = None
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                # Download button
                                if st.button(
                                    f"Download {track_name}",
                                    key=f"download_{track_name}",
                                    use_container_width=True
                                ):
                                    with st.spinner(f"Downloading {track_name}..."):
                                        audio_content = download_track(job_id, track_name)
                                        if audio_content:
                                            st.download_button(
                                                label=f"Save {track_name}.wav",
                                                data=audio_content,
                                                file_name=f"{track_name}_{job_id}.wav",
                                                mime="audio/wav",
                                                use_container_width=True
                                            )
                                        else:
                                            st.error(f"Failed to download {track_name}")

                            with col2:
                                st.write("")

                            # Audio Player
                            if audio_content:
                                st.audio(audio_content, format="audio/wav")

                            # Load audio for visualization
                            if audio_content:
                                audio_array, sr = load_audio_for_viz(audio_content)

                                if audio_array is not None and sr is not None:
                                    # Statistics
                                    if show_stats:
                                        st.markdown("#### Audio Statistics")
                                        stats = get_audio_stats(audio_array, sr)
                                        col1, col2, col3 = st.columns(3)
                                        for idx, (key, value) in enumerate(stats.items()):
                                            if idx % 3 == 0:
                                                col = col1
                                            elif idx % 3 == 1:
                                                col = col2
                                            else:
                                                col = col3
                                            with col:
                                                st.metric(key, value)

                                    # Waveform
                                    if show_waveforms:
                                        st.markdown("#### Waveform")
                                        fig = plot_waveform(audio_array, sr, f"{track_name} Waveform")
                                        if fig is not None:
                                            st.pyplot(fig)
                                            plt.close(fig)

                                    # Spectrogram
                                    if show_spectrograms:
                                        st.markdown("#### Spectrogram")
                                        fig = plot_spectrogram(audio_array, sr, f"{track_name} Spectrogram")
                                        if fig is not None:
                                            st.pyplot(fig)
                                            plt.close(fig)

                    st.divider()

                    # Download All
                    if st.button("Download All Tracks (ZIP)", use_container_width=True, type="secondary"):
                        with st.spinner("Preparing download..."):
                            zip_content = download_all_tracks(job_id)
                            if zip_content:
                                st.download_button(
                                    label="Save All Tracks",
                                    data=zip_content,
                                    file_name=f"tracks_{job_id}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            else:
                                st.error("Failed to prepare download")

                    # Generate Report
                    if "uploaded_file" in st.session_state and st.session_state.uploaded_file:
                        uploaded_file = st.session_state.uploaded_file
                        audio_array, sr = load_audio_for_viz(uploaded_file.getbuffer())
                        audio_stats = get_audio_stats(audio_array, sr) if audio_array is not None else None
                        report = generate_report(job_id, status, audio_stats)

                        st.divider()
                        st.markdown("### Analysis Report")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(report)
                        with col2:
                            st.download_button(
                                "Export Report",
                                data=report,
                                file_name=f"report_{job_id}.md",
                                mime="text/markdown"
                            )
            else:
                st.info("Processing in progress... Check back soon!")

        else:
            st.error("Could not fetch job status. Job may have expired.")

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


# ============================================================================
# TAB 3: HELP & INFO
# ============================================================================

with tab3:
    st.markdown("""
    ## About This Application

    This is an advanced audio separation tool that uses machine learning
    to separate audio tracks into individual components.

    ### Features
    - Upload audio files (WAV, MP3, FLAC, OGG, M4A)
    - Automatic track separation using Demucs
    - Real-time visualization with waveforms and spectrograms
    - Audio statistics and analysis
    - Download individual or all tracks

    ### How to Use
    1. Go to "Upload & Process" tab
    2. Upload your audio file
    3. Click "Process Audio" to start separation
    4. Monitor progress in real-time
    5. View visualizations and download results

    ### Troubleshooting
    - **API Connection Failed**: Make sure the backend API is running
    - **Upload Failed**: Check file size and format
    - **Processing Stuck**: Try refreshing the page

    ### System Requirements
    - Modern web browser (Chrome, Firefox, Safari, Edge)
    - Internet connection for API communication
    - Sufficient disk space for temporary files

    ### Support
    For more information, see the documentation files included with this project.
    """)