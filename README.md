Audio Pipeline - Modular Audio Separation and Processing System

QUICK START

Prerequisites
- Docker and Docker Compose
- OR: Python 3.11+, FFmpeg, libsndfile1

Option 1: Docker (Recommended)

docker-compose up --build

Access:
- UI: http://localhost:8501
- API: http://localhost:8000

Option 2: Local Installation

1. Install dependencies:
pip install -r requirements.txt

2. Create required directories:
mkdir -p uploads outputs downloads

3. Start API (Terminal 1):
python -m uvicorn api.app:app --reload

4. Start UI (Terminal 2):
streamlit run ui/app.py

API Endpoints

Health Check
GET /health
Response: {status, version, pipeline_stages}

Configuration
GET /config
Response: {max_file_size_mb, supported_formats, pipeline_stages}

Process Audio
POST /process
Body: multipart/form-data (file)
Response: {job_id, status, created_at, stages, outputs}

Job Status
GET /job/{job_id}
Response: {job_id, status, created_at, stages, outputs}

Get Outputs
GET /job/{job_id}/outputs
Response: {track_name: file_path}

Download Track
GET /download/{job_id}/{track_name}
Returns: audio/wav file

Download All
GET /download/{job_id}/all
Returns: application/zip file

Output Tracks

The system generates these output files:
- vocals.wav
- drums.wav
- bass.wav
- other_harmonic.wav
- other_percussive.wav
- main.wav
- main_harmonic.wav
- main_percussive.wav
- piano.wav (optional, model-dependent)

Supported Input Formats
- WAV
- MP3
- FLAC
- OGG

Constraints
- Maximum file size: 500 MB
- Supported sample rates: 16kHz to 48kHz
- Processing time: 1-5 minutes depending on file length

Usage Examples

Using the UI
1. Navigate to http://localhost:8501
2. Upload an audio file
3. Click "Process Audio"
4. Wait for processing to complete
5. Download individual tracks or all tracks as ZIP

Using the API (cURL)

Process audio:
curl -X POST http://localhost:8000/process \
 -F "file=@song.wav"

Get status:
curl http://localhost:8000/job/{job_id}

Download track:
curl http://localhost:8000/download/{job_id}/vocals > vocals.wav

Python Example

import requests

# Upload and process
files = {"file": open("song.wav", "rb")}
response = requests.post("http://localhost:8000/process", files=files)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/job/{job_id}")
print(status.json())

# Download track
track = requests.get(f"http://localhost:8000/download/{job_id}/vocals")
with open("vocals.wav", "wb") as f:
 f.write(track.content)

Troubleshooting

API Connection Failed
- Ensure API is running: python -m uvicorn api.app:app
- Check port 8000 is not in use
- Verify firewall settings

Out of Memory
- Use CPU processing (default)
- Process smaller files first
- Increase Docker memory allocation

Model Download Issues
- First run downloads models (~2GB)
- Ensure internet connection
- Check disk space

File Upload Failed
- Check file size is under 500MB
- Verify audio format is supported
- Ensure file has read permissions

Configuration

Environment Variables
- DEVICE: "cpu" or "cuda" (default: "cpu")
- OUTPUT_DIR: Output directory path
- UPLOAD_DIR: Upload directory path

Customization

Changing Separator Model
In api/app.py:
pipeline.add_stage(SeparationStage(
 separator_type="demucs",
 separator_model="htdemucs_ft",
 device="cpu"
))

Available models:
- htdemucs_ft (default)
- htdemucs
- demucs

Adding Custom Stages
1. Create class extending PipelineStage
2. Implement execute() and validate_input()
3. Add to pipeline in api/app.py

Documentation

- ARCHITECTURE.md: System design and modularity
- API_DOCS.md: Detailed API reference
- SCREENING_ANSWERS.md: Design decision rationale

Performance

Typical Processing Times
- 3-minute audio: 2-5 minutes (CPU)
- 10-minute audio: 7-15 minutes (CPU)
- With GPU: 3-5x faster

Optimization Tips
- Use WAV format (faster than MP3)
- Process during off-peak hours
- Monitor system resources

Error Handling

The system provides detailed error messages:
- Validation errors (format, size)
- Processing errors (models, audio issues)
- Download errors (file not found)

All errors are logged and included in job manifest.

Support

For issues:
1. Check logs: logs/pipeline.log
2. Review job manifest: outputs/{job_id}/manifest.json
3. Verify configuration: GET /config
4. Check system resources

License

MIT

Author

Audio Pipeline Development Team