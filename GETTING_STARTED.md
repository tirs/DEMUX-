Audio Pipeline - 5-Minute Quick Start

FASTEST WAY TO GET RUNNING

Option 1: Docker (Recommended - 2 minutes)

Requirements:
- Docker installed
- 10 GB free disk space

Steps:
1. Navigate to project directory:
 cd c:\Users\simba\Desktop\Modular

2. Start the system:
 docker-compose up --build

3. Wait for it to say "Application startup complete"

4. Open in browser:
 UI: http://localhost:8501
 API: http://localhost:8000

Done! Upload an audio file in the UI.

First run note: Downloads ~2GB of models (takes 5-10 min)

Stop when done:
 Ctrl+C
 docker-compose down

Option 2: Local Python (15 minutes)

Requirements:
- Python 3.11+
- FFmpeg installed

Steps:
1. Create virtual environment:
 python -m venv venv
 venv\Scripts\activate

2. Install dependencies:
 pip install -r requirements.txt

3. Create directories:
 mkdir uploads outputs downloads logs

4. Terminal 1 - Start API:
 python -m uvicorn api.app:app --reload

5. Terminal 2 - Start UI:
 streamlit run ui/app.py

6. Open browser:
 http://localhost:8501

Done!

USING THE SYSTEM

Via Web Interface:

1. Go to http://localhost:8501
2. Click "Browse files" and select audio file
3. Click "Process Audio"
4. Wait for completion (see progress bar)
5. Click " Download vocals" (or other tracks)
6. Download all as ZIP with " Download All Tracks (ZIP)"

Via API:

Upload file:
curl -X POST http://localhost:8000/process \
 -F "file=@song.wav"

Response: {"job_id": "abc123..."}

Check status:
curl http://localhost:8000/job/abc123...

Download track:
curl http://localhost:8000/download/abc123.../vocals > vocals.wav

TROUBLESHOOTING - QUICK FIXES

"Connection refused"
→ Make sure docker-compose is running
 docker-compose ps

"Port already in use"
→ Stop existing container:
 docker-compose down
 or use different port in docker-compose.yml

"File too large"
→ Maximum is 500MB
 Check file size and use smaller file

"API not responding"
→ Give it time on first run (downloading models)
 Check logs: docker-compose logs

WHAT GETS GENERATED

9 output tracks from each audio file:
1. vocals.wav - Vocal track
2. drums.wav - Drum track
3. bass.wav - Bass track
4. other.wav - Other instruments
5. harmonic.wav - Harmonic components
6. percussive.wav - Percussive components
7. main.wav - Full audio (original)
8. main_harmonic.wav - Harmonic from original
9. main_percussive.wav - Percussive from original

All downloaded as individual files or ZIP.

TYPICAL PERFORMANCE

3-minute audio file:
- Processing time: 4-5 minutes (CPU)
- With GPU: 1-2 minutes
- Disk space needed: ~1-2GB temporary

Supported formats:
- WAV (recommended)
- MP3
- FLAC
- OGG

NEXT STEPS

After getting running:
1. Try with different audio files
2. Read README.md for full documentation
3. Check API_DOCS.md for API details
4. Review ARCHITECTURE.md for system design
5. See EXAMPLES.md for code examples

INTEGRATION WITH YOUR SYSTEM

To integrate this into an existing webpage:

Frontend code:
const jobId = "123abc...";
const response = await fetch('http://localhost:8000/download/' + jobId + '/all');
const blob = await response.blob();
// Download or process blob

Backend integration:
import requests

response = requests.post(
 "http://localhost:8000/process",
 files={"file": open("song.wav", "rb")}
)
job_id = response.json()["job_id"]

COMMON OPERATIONS

Get API info:
curl http://localhost:8000/health

Check what's supported:
curl http://localhost:8000/config

Check if old job is done:
curl http://localhost:8000/job/old-job-id-here

Download track from old job:
curl http://localhost:8000/download/old-job-id-here/vocals > vocals.wav

TIPS AND TRICKS

Process multiple files:
- Open UI in multiple browser tabs
- Each can upload and track separately

Batch processing via API:
for file in *.wav; do
 curl -X POST http://localhost:8000/process -F "file=@$file"
done

Get job history:
ls -la outputs/ # See all job directories
cat outputs/job-id/manifest.json # See job details

Free up space:
rm -rf outputs/old-job-id

SETTING PROCESSING MODE

For GPU (if you have NVIDIA card):
Update docker-compose.yml:
environment:
 - DEVICE=cuda

Then rebuild:
docker-compose up --build

Default is CPU (works on any machine).

PRODUCTION DEPLOYMENT

For putting on a server:
1. Follow INSTALLATION.md
2. Follow DEPLOYMENT_GUIDE.md
3. Configure Nginx/Apache
4. Set up HTTPS
5. Add authentication
6. Enable monitoring

GETTING HELP

Files to read:
- README.md: Overview
- INSTALLATION.md: Setup details
- API_DOCS.md: API endpoints
- EXAMPLES.md: Code samples
- ARCHITECTURE.md: How it works

Check logs:
docker-compose logs -f

Check job details:
cat outputs/job-id/manifest.json

IMPORTANT NOTES

First run:
- Downloaded models are ~2GB
- Stored in ~/.cache or Docker volume
- Subsequent runs are much faster

Storage:
- Each audio file can be 1-5GB during processing
- Make sure you have 20GB+ free space
- Old files can be deleted from outputs/ folder

Performance:
- CPU version: Good for testing
- GPU version: 3-5x faster (if available)
- Multi-core CPU recommended

That's it! You're ready to go.

For questions, check the README.md or other documentation files.