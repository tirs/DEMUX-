import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
DOWNLOAD_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"

for directory in [UPLOAD_DIR, OUTPUT_DIR, DOWNLOAD_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))

DEVICE = os.getenv("DEVICE", "cpu")
SEPARATOR_MODEL = os.getenv("SEPARATOR_MODEL", "htdemucs_ft")

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
SUPPORTED_FORMATS = ["wav", "mp3", "flac", "ogg"]

TARGET_DB = float(os.getenv("TARGET_DB", "-20.0"))

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

JOB_RETENTION_DAYS = int(os.getenv("JOB_RETENTION_DAYS", "30"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

__all__ = [
    "BASE_DIR",
    "UPLOAD_DIR",
    "OUTPUT_DIR",
    "DOWNLOAD_DIR",
    "LOGS_DIR",
    "API_HOST",
    "API_PORT",
    "UI_PORT",
    "DEVICE",
    "SEPARATOR_MODEL",
    "MAX_FILE_SIZE_MB",
    "SUPPORTED_FORMATS",
    "TARGET_DB",
    "LOGGING_LEVEL",
    "LOGGING_FORMAT",
    "JOB_RETENTION_DAYS",
    "CORS_ORIGINS",
    "DEBUG_MODE"
]