Audio Pipeline API Documentation

BASE URL
http://localhost:8000

ENDPOINTS

1. Health Check
GET /health

Returns system health status.

Response (200 OK):
{
 "status": "healthy",
 "version": "1.0.0",
 "pipeline_stages": 4
}

Example:
curl http://localhost:8000/health

2. Configuration
GET /config

Returns system configuration and supported formats.

Response (200 OK):
{
 "max_file_size_mb": 500,
 "supported_formats": ["wav", "mp3", "flac", "ogg"],
 "pipeline_stages": [
 {
 "name": "audio_separation",
 "processor_type": "separator"
 },
 {
 "name": "harmonic_percussive_separation",
 "processor_type": "decomposition"
 },
 {
 "name": "composite_track_creation",
 "processor_type": "composition"
 },
 {
 "name": "normalization",
 "processor_type": "audio_processing"
 }
 ]
}

Example:
curl http://localhost:8000/config

3. Process Audio
POST /process

Upload audio file and start processing pipeline.

Request:
- Method: POST
- Content-Type: multipart/form-data
- Body: file (binary audio file)

Response (200 OK):
{
 "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
 "status": "processing",
 "created_at": "2024-01-15T10:30:45.123456",
 "stages": [
 {
 "name": "audio_separation",
 "processor_type": "separator",
 "status": "processing",
 "started_at": "2024-01-15T10:30:46.123456",
 "completed_at": null,
 "error": null,
 "duration_seconds": null
 },
 {
 "name": "harmonic_percussive_separation",
 "processor_type": "decomposition",
 "status": "pending",
 "started_at": null,
 "completed_at": null,
 "error": null,
 "duration_seconds": null
 },
 {
 "name": "composite_track_creation",
 "processor_type": "composition",
 "status": "pending",
 "started_at": null,
 "completed_at": null,
 "error": null,
 "duration_seconds": null
 },
 {
 "name": "normalization",
 "processor_type": "audio_processing",
 "status": "pending",
 "started_at": null,
 "completed_at": null,
 "error": null,
 "duration_seconds": null
 }
 ],
 "outputs": {}
}

Response (400 Bad Request):
{
 "detail": "No filename provided"
}

Response (500 Internal Server Error):
{
 "detail": "Unsupported audio format:.aac"
}

Examples:

cURL:
curl -X POST http://localhost:8000/process \
 -F "file=@song.wav"

Python:
import requests

with open("song.wav", "rb") as f:
 files = {"file": f}
 response = requests.post("http://localhost:8000/process", files=files)
 data = response.json()
 job_id = data["job_id"]

JavaScript:
const formData = new FormData();
formData.append('file', fileInput.files[0]);
const response = await fetch('http://localhost:8000/process', {
 method: 'POST',
 body: formData
});
const data = await response.json();

4. Get Job Status
GET /job/{job_id}

Retrieve processing status for a job.

Path Parameters:
- job_id (string, required): Job identifier returned from /process

Response (200 OK):
{
 "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
 "status": "completed",
 "created_at": "2024-01-15T10:30:45.123456",
 "stages": [
 {
 "name": "audio_separation",
 "processor_type": "separator",
 "status": "completed",
 "started_at": "2024-01-15T10:30:46.123456",
 "completed_at": "2024-01-15T10:35:12.654321",
 "error": null,
 "duration_seconds": 286.531
 }
 ],
 "outputs": {
 "vocals": "/app/outputs/a1b2c3d4.../demucs_output/vocals.wav",
 "drums": "/app/outputs/a1b2c3d4.../demucs_output/drums.wav",
 "bass": "/app/outputs/a1b2c3d4.../demucs_output/bass.wav",
 "other": "/app/outputs/a1b2c3d4.../demucs_output/other.wav",
 "harmonic": "/app/outputs/a1b2c3d4.../harmonic_percussive/harmonic.wav",
 "percussive": "/app/outputs/a1b2c3d4.../harmonic_percussive/percussive.wav",
 "main": "/app/outputs/a1b2c3d4.../composite/main.wav",
 "main_harmonic": "/app/outputs/a1b2c3d4.../composite/main_harmonic.wav",
 "main_percussive": "/app/outputs/a1b2c3d4.../composite/main_percussive.wav"
 }
}

Response (404 Not Found):
{
 "detail": "Job not found"
}

Examples:

cURL:
curl http://localhost:8000/job/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6

Python:
response = requests.get("http://localhost:8000/job/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6")
status = response.json()

5. Get Job Outputs
GET /job/{job_id}/outputs

Get only the output file paths for a job.

Path Parameters:
- job_id (string, required): Job identifier

Response (200 OK):
{
 "vocals": "/app/outputs/.../vocals.wav",
 "drums": "/app/outputs/.../drums.wav",
 "bass": "/app/outputs/.../bass.wav",
 "other": "/app/outputs/.../other.wav",
 "harmonic": "/app/outputs/.../harmonic.wav",
 "percussive": "/app/outputs/.../percussive.wav",
 "main": "/app/outputs/.../main.wav",
 "main_harmonic": "/app/outputs/.../main_harmonic.wav",
 "main_percussive": "/app/outputs/.../main_percussive.wav"
}

Response (404 Not Found):
{
 "detail": "Job not found"
}

Example:
curl http://localhost:8000/job/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6/outputs

6. Download Track
GET /download/{job_id}/{track_name}

Download individual audio track.

Path Parameters:
- job_id (string, required): Job identifier
- track_name (string, required): Track name (vocals, drums, bass, etc.)

Response (200 OK):
Binary audio file (audio/wav)

Response (404 Not Found):
{
 "detail": "Track not found"
}

Examples:

cURL:
curl http://localhost:8000/download/a1b2c3d4.../vocals > vocals.wav

Python:
response = requests.get("http://localhost:8000/download/a1b2c3d4.../vocals")
with open("vocals.wav", "wb") as f:
 f.write(response.content)

JavaScript:
const response = await fetch('http://localhost:8000/download/a1b2c3d4.../vocals');
const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'vocals.wav';
a.click();

7. Download All Tracks
GET /download/{job_id}/all

Download all output tracks as ZIP file.

Path Parameters:
- job_id (string, required): Job identifier

Response (200 OK):
Binary ZIP file (application/zip)

Response (404 Not Found):
{
 "detail": "Job not found"
}

Examples:

cURL:
curl http://localhost:8000/download/a1b2c3d4.../all > tracks.zip

Python:
response = requests.get("http://localhost:8000/download/a1b2c3d4.../all")
with open("tracks.zip", "wb") as f:
 f.write(response.content)

ERROR HANDLING

All errors follow standard HTTP status codes:

400 Bad Request
- Invalid file upload
- Missing required parameters
- File format not supported

404 Not Found
- Job does not exist
- Track not found
- Invalid job_id

500 Internal Server Error
- Processing failed
- Model loading error
- System resource exhaustion

Error Response Format:
{
 "detail": "Human-readable error message"
}

RATE LIMITING

Currently unlimited. For production:
- Implement rate limiting per IP
- Queue long-running jobs
- Add authentication tokens

RESPONSE TIMES

Typical response times:
- /health: <10ms
- /config: <10ms
- /process (upload): 1-2 seconds
- /job/{id} (polling): <50ms
- /download: Depends on file size

Processing times:
- 3-min audio file: 2-5 minutes (CPU)
- 10-min audio file: 7-15 minutes (CPU)
- With GPU: 3-5x faster

STATUS VALUES

Processing stages can have these statuses:
- pending: Waiting to execute
- processing: Currently executing
- completed: Successfully finished
- failed: Encountered error

Overall job status:
- processing: Pipeline in progress
- completed: All stages succeeded
- failed: One or more stages failed

OUTPUT TRACKS

9 output tracks generated:
1. vocals: Vocal track from separation
2. drums: Drum track from separation
3. bass: Bass track from separation
4. other: Other instruments from separation
5. harmonic: Harmonic components from decomposition
6. percussive: Percussive components from decomposition
7. main: Original audio (composite)
8. main_harmonic: Harmonic from original
9. main_percussive: Percussive from original

AUTHENTICATION

Currently no authentication. For production implementation:
- API key headers
- JWT tokens
- OAuth2 flow
- Rate limiting per user

VERSIONING

API version: 1.0.0
- Backward compatible changes in minor versions
- Breaking changes in major versions
- Version included in responses

CORS

Enabled for all origins. Configure in production:
```python
CORSMiddleware(
 allow_origins=["https://yourdomain.com"],
 allow_credentials=True,
 allow_methods=["POST", "GET"],
 allow_headers=["*"],
)
```

WEBHOOKS

Future feature for real-time notifications:
- POST to callback URL on completion
- Include job manifest in payload
- Retry logic for failed webhooks