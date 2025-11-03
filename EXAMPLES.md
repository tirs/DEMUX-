Audio Pipeline - Usage Examples

PYTHON API EXAMPLES

Basic Processing

import requests
import json

API_URL = "http://localhost:8000"

# Check API health
response = requests.get(f"{API_URL}/health")
print(response.json())

# Get configuration
response = requests.get(f"{API_URL}/config")
config = response.json()
print(f"Max file size: {config['max_file_size_mb']}MB")
print(f"Supported formats: {config['supported_formats']}")

# Upload and process audio
with open("song.wav", "rb") as f:
 files = {"file": f}
 response = requests.post(f"{API_URL}/process", files=files)
 result = response.json()
 job_id = result["job_id"]
 print(f"Job started: {job_id}")
 print(f"Status: {result['status']}")

# Get job status
response = requests.get(f"{API_URL}/job/{job_id}")
status = response.json()
print(f"Overall status: {status['status']}")

for stage in status['stages']:
 print(f" {stage['name']}: {stage['status']}")
 if stage['duration_seconds']:
 print(f" Duration: {stage['duration_seconds']:.1f}s")

# Get output tracks
response = requests.get(f"{API_URL}/job/{job_id}/outputs")
outputs = response.json()
print("Output tracks:")
for track_name, path in outputs.items():
 print(f" {track_name}: {path}")

Downloading Tracks

import requests
import os

# Download single track
track_name = "vocals"
response = requests.get(
 f"http://localhost:8000/download/{job_id}/{track_name}",
 stream=True
)

if response.status_code == 200:
 with open(f"{track_name}.wav", "wb") as f:
 f.write(response.content)
 print(f"Downloaded {track_name}.wav")

# Download all tracks as ZIP
response = requests.get(
 f"http://localhost:8000/download/{job_id}/all",
 stream=True
)

if response.status_code == 200:
 with open(f"tracks_{job_id}.zip", "wb") as f:
 f.write(response.content)
 print(f"Downloaded all tracks as ZIP")

Batch Processing

import requests
import time
from pathlib import Path

audio_files = list(Path("./audio_library").glob("*.wav"))

for audio_file in audio_files:
 print(f"Processing: {audio_file.name}")

 with open(audio_file, "rb") as f:
 response = requests.post(
 "http://localhost:8000/process",
 files={"file": f}
 )
 result = response.json()
 job_id = result["job_id"]
 print(f" Job ID: {job_id}")

 # Poll for completion
 while True:
 status_response = requests.get(
 f"http://localhost:8000/job/{job_id}"
 )
 status = status_response.json()

 if status["status"] == "completed":
 print(f" Completed! Processing time:")
 total_time = sum(
 s.get("duration_seconds", 0)
 for s in status["stages"]
 )
 print(f" Total: {total_time:.1f}s")
 break
 elif status["status"] == "failed":
 print(f" FAILED!")
 for stage in status["stages"]:
 if stage["error"]:
 print(f" Error in {stage['name']}: {stage['error']}")
 break
 else:
 completed = sum(
 1 for s in status["stages"]
 if s["status"] == "completed"
 )
 total = len(status["stages"])
 print(f" Progress: {completed}/{total} stages")
 time.sleep(5)

Monitoring Performance

import requests
import time

start_time = time.time()

# Submit job
with open("song.wav", "rb") as f:
 response = requests.post(
 "http://localhost:8000/process",
 files={"file": f}
 )
 job_id = response.json()["job_id"]

# Monitor stages
previous_completed = 0

while True:
 status_response = requests.get(
 f"http://localhost:8000/job/{job_id}"
 )
 status = status_response.json()

 completed = sum(
 1 for s in status["stages"]
 if s["status"] == "completed"
 )

 if completed > previous_completed:
 for stage in status["stages"]:
 if stage["status"] == "completed" and stage["duration_seconds"]:
 print(f"{stage['name']}: {stage['duration_seconds']:.1f}s")

 previous_completed = completed

 if status["status"] in ["completed", "failed"]:
 break

 time.sleep(2)

total_time = time.time() - start_time
print(f"Total time: {total_time:.1f}s")

CURL EXAMPLES

Check API Status

curl http://localhost:8000/health

Expected output:
{"status":"healthy","version":"1.0.0","pipeline_stages":4}

Get Configuration

curl http://localhost:8000/config

Upload and Process

curl -X POST http://localhost:8000/process \
 -F "file=@song.wav"

Response includes job_id.

Check Job Status

curl http://localhost:8000/job/abc123def456

Response includes stages, outputs, and status.

Get Output Tracks List

curl http://localhost:8000/job/abc123def456/outputs

Response includes all output file paths.

Download Single Track

curl http://localhost:8000/download/abc123def456/vocals \
 -o vocals.wav

Download All Tracks

curl http://localhost:8000/download/abc123def456/all \
 -o tracks.zip

Unzip results:
unzip tracks.zip

JAVASCRIPT/FETCH EXAMPLES

Upload and Process

const uploadFile = async (file) => {
 const formData = new FormData();
 formData.append('file', file);

 const response = await fetch('http://localhost:8000/process', {
 method: 'POST',
 body: formData
 });

 return await response.json();
};

Get Job Status

const getJobStatus = async (jobId) => {
 const response = await fetch(
 `http://localhost:8000/job/${jobId}`
 );
 return await response.json();
};

Download Track

const downloadTrack = async (jobId, trackName) => {
 const response = await fetch(
 `http://localhost:8000/download/${jobId}/${trackName}`
 );

 const blob = await response.blob();
 const url = window.URL.createObjectURL(blob);
 const a = document.createElement('a');
 a.href = url;
 a.download = `${trackName}.wav`;
 a.click();
 window.URL.revokeObjectURL(url);
};

Monitor Progress

const monitorJob = async (jobId, onProgress) => {
 let isComplete = false;

 while (!isComplete) {
 const status = await getJobStatus(jobId);

 if (onProgress) {
 const completedStages = status.stages.filter(
 s => s.status === 'completed'
 ).length;
 onProgress(completedStages, status.stages.length);
 }

 if (status.status === 'completed') {
 isComplete = true;
 return status;
 } else if (status.status === 'failed') {
 throw new Error('Processing failed');
 }

 await new Promise(r => setTimeout(r, 2000));
 }
};

SHELL SCRIPT EXAMPLES

Batch Process Directory

#!/bin/bash
API_URL="http://localhost:8000"
INPUT_DIR="./audio_files"
OUTPUT_DIR="./outputs"

mkdir -p "$OUTPUT_DIR"

for audio_file in "$INPUT_DIR"/*.wav; do
 filename=$(basename "$audio_file")
 echo "Processing: $filename"

 response=$(curl -s -X POST "$API_URL/process" \
 -F "file=@$audio_file")

 job_id=$(echo "$response" | jq -r '.job_id')
 echo "Job ID: $job_id"

 # Poll for completion
 while true; do
 status=$(curl -s "$API_URL/job/$job_id")
 job_status=$(echo "$status" | jq -r '.status')

 if [ "$job_status" = "completed" ]; then
 echo "Completed!"

 # Download all tracks
 curl -s "$API_URL/download/$job_id/all" \
 -o "$OUTPUT_DIR/tracks_$job_id.zip"

 break
 elif [ "$job_status" = "failed" ]; then
 echo "Failed!"
 break
 fi

 sleep 5
 done
done

Download All Tracks

#!/bin/bash
JOB_ID=$1
OUTPUT_DIR="./downloads"

mkdir -p "$OUTPUT_DIR"

echo "Downloading tracks for job: $JOB_ID"

curl -s "http://localhost:8000/download/$JOB_ID/all" \
 -o "$OUTPUT_DIR/tracks.zip"

echo "Extracting..."
unzip -q "$OUTPUT_DIR/tracks.zip" -d "$OUTPUT_DIR/$JOB_ID"

echo "Done! Files in: $OUTPUT_DIR/$JOB_ID"

DATA RECOVERY EXAMPLES

Retrieve Job Info

import json
from pathlib import Path

job_id = "your-job-id"
manifest_path = Path(f"outputs/{job_id}/manifest.json")

with open(manifest_path, "r") as f:
 manifest = json.load(f)

print(f"Job Status: {manifest['status']}")
print(f"Created: {manifest['created_at']}")
print(f"Input: {manifest['input_file']}")

print("\nStages:")
for stage in manifest['stages']:
 print(f" {stage['name']}: {stage['status']}")
 if stage['error']:
 print(f" Error: {stage['error']}")
 if stage['duration_seconds']:
 print(f" Duration: {stage['duration_seconds']:.1f}s")

print("\nOutputs:")
for name, path in manifest['outputs'].items():
 print(f" {name}: {path}")

Estimate Processing Time

from pathlib import Path
import json

def estimate_time(audio_duration_minutes):
 """
 Estimate processing time based on audio duration.
 Typical performance: 1-2x real-time on CPU
 """
 separation_time = audio_duration_minutes * 1.5
 other_stages = 2 # minutes for other processing
 total = separation_time + other_stages
 return total

# Check recent job times
jobs_dir = Path("outputs")
recent_times = []

for job_dir in sorted(jobs_dir.iterdir())[-10:]:
 manifest_path = job_dir / "manifest.json"
 if manifest_path.exists():
 with open(manifest_path) as f:
 manifest = json.load(f)
 total_time = sum(
 s.get("duration_seconds", 0)
 for s in manifest["stages"]
 )
 recent_times.append(total_time)

if recent_times:
 avg_time = sum(recent_times) / len(recent_times)
 print(f"Average processing time: {avg_time:.1f}s")
 print(f"For 3-minute audio: {avg_time * 3 / 180:.1f} seconds")

SYSTEMD SERVICE SETUP (Linux)

Create /etc/systemd/system/audio-pipeline.service:

[Unit]
Description=Audio Pipeline Service
After=network.target

[Service]
Type=simple
User=audiouser
WorkingDirectory=/opt/audio-pipeline
ExecStart=/opt/audio-pipeline/venv/bin/python -m uvicorn api.app:app \
 --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

Enable and start:
sudo systemctl daemon-reload
sudo systemctl enable audio-pipeline
sudo systemctl start audio-pipeline

Check status:
sudo systemctl status audio-pipeline
sudo journalctl -u audio-pipeline -f