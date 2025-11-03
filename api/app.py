import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import SEPARATOR_MODEL, DEVICE, TARGET_DB
from core.pipeline import AudioPipeline
from core.processors import (
    SeparationStage,
    HarmonicPercussiveStage,
    CompositeTrackStage,
    SeparatedTrackHarmonicPercussiveStage,
    NormalizationStage
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audio Pipeline API",
    description="Modular audio separation and processing pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
OUTPUT_DIR = Path("./outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

pipeline = AudioPipeline(output_base_dir=str(OUTPUT_DIR))


def _initialize_pipeline():
    pipeline.add_stage(SeparationStage(separator_type="demucs", separator_model=SEPARATOR_MODEL, device=DEVICE))
    pipeline.add_stage(SeparatedTrackHarmonicPercussiveStage())
    pipeline.add_stage(HarmonicPercussiveStage())
    pipeline.add_stage(CompositeTrackStage())
    pipeline.add_stage(NormalizationStage(target_db=TARGET_DB))


_initialize_pipeline()


@app.on_event("startup")
async def startup_event():
    logger.info("API startup - Pipeline initialized")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "pipeline_stages": len(pipeline.stages)
    }


@app.get("/config")
async def get_config():
    return {
        "max_file_size_mb": 500,
        "supported_formats": ["wav", "mp3", "flac", "ogg"],
        "pipeline_stages": [
            {
                "name": stage.name,
                "processor_type": stage.processor_type
            }
            for stage in pipeline.stages
        ]
    }


@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_path = UPLOAD_DIR / file.filename

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Processing file: {file.filename}")
        manifest = pipeline.process(str(file_path))

        return JSONResponse({
            "job_id": manifest.job_id,
            "status": manifest.status,
            "created_at": manifest.created_at,
            "stages": [s.to_dict() for s in manifest.stages],
            "outputs": manifest.outputs
        })

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if file_path.exists():
            file_path.unlink()


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    manifest = pipeline.get_job_status(job_id)

    if not manifest:
        raise HTTPException(status_code=404, detail="Job not found")

    return JSONResponse({
        "job_id": manifest.job_id,
        "status": manifest.status,
        "created_at": manifest.created_at,
        "stages": [s.to_dict() for s in manifest.stages],
        "outputs": manifest.outputs
    })


@app.get("/job/{job_id}/outputs")
async def get_job_outputs(job_id: str):
    outputs = pipeline.get_outputs(job_id)

    if outputs is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JSONResponse(outputs)


@app.get("/download/{job_id}/{track_name}")
async def download_track(job_id: str, track_name: str):
    output_dir = OUTPUT_DIR / job_id
    track_path = None

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if track_name in file and file.endswith(".wav"):
                track_path = Path(root) / file
                break

    if not track_path or not track_path.exists():
        raise HTTPException(status_code=404, detail="Track not found")

    return FileResponse(
        path=track_path,
        filename=f"{track_name}.wav",
        media_type="audio/wav"
    )


@app.get("/download/{job_id}/all")
async def download_all_tracks(job_id: str):
    import zipfile
    import io

    output_dir = OUTPUT_DIR / job_id

    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".wav"):
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(output_dir)
                    zip_file.write(file_path, arcname)

    zip_buffer.seek(0)

    return FileResponse(
        content=zip_buffer.getvalue(),
        filename=f"audio_tracks_{job_id}.zip",
        media_type="application/zip"
    )


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )