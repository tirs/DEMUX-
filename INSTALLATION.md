Audio Pipeline - Installation and Setup Guide

SYSTEM REQUIREMENTS

Operating System:
- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS (10.14+)
- Windows (10/11 with WSL2)

Hardware Minimum:
- CPU: 4 cores (Intel i5/AMD Ryzen 5 or equivalent)
- RAM: 8 GB (16 GB recommended)
- Storage: 50 GB (for models and processing)
- GPU: Optional (NVIDIA CUDA for GPU acceleration)

Software Requirements:
- Python 3.11+
- Docker 20.10+ (for containerized deployment)
- FFmpeg 4.0+

OPTION 1: DOCKER INSTALLATION (Recommended)

Fastest and most reliable setup.

Prerequisites:
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- On Windows: Enable WSL2 backend in Docker settings

Steps:

1. Clone or download project:
cd c:\Users\simba\Desktop\Modular

2. Build Docker image:
docker-compose build

3. Start services:
docker-compose up

4. Access services:
- Web UI: http://localhost:8501
- API: http://localhost:8000
- Health check: curl http://localhost:8000/health

5. Stop services:
docker-compose down

First run notes:
- Demucs model downloads ~2GB on first use
- Takes 5-10 minutes for initial setup
- Internet connection required for model download
- Subsequent runs are much faster

GPU Support (Optional):

Install NVIDIA Container Runtime:
# Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
 sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-runtime

Update docker-compose.yml:
services:
 audio-pipeline:
 runtime: nvidia
 environment:
 - NVIDIA_VISIBLE_DEVICES=all
 - DEVICE=cuda

Rebuild and restart:
docker-compose build
docker-compose up

OPTION 2: LOCAL INSTALLATION (Advanced)

For development or custom configurations.

Prerequisites Installation:

Windows:
1. Install Python 3.11: https://www.python.org/downloads/
2. Install FFmpeg:
 - Download from: https://ffmpeg.org/download.html
 - Add to PATH environment variable
3. Install libsndfile:
 - Download from: http://www.mega-nerd.com/libsndfile/

Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip ffmpeg libsndfile1

macOS:
brew install python@3.11 ffmpeg libsndfile

Python Installation:

1. Create virtual environment:
python -m venv venv

2. Activate virtual environment:
Windows:
venv\Scripts\activate

Linux/macOS:
source venv/bin/activate

3. Upgrade pip:
pip install --upgrade pip setuptools wheel

4. Install dependencies:
pip install -r requirements.txt

Note: First pip install downloads ~3GB (PyTorch + models)

5. Create required directories:
mkdir -p uploads outputs downloads logs

6. Start API (Terminal 1):
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

Output should show:
Uvicorn running on http://0.0.0.0:8000

7. Start UI (Terminal 2):
streamlit run ui/app.py

Output should show:
Local URL: http://localhost:8501

First-Time Setup:

When first accessing the API, Demucs downloads models:
- Watch logs for download progress
- Takes 5-10 minutes first time
- ~2GB download size
- Cached after first download

Verify installation:
curl http://localhost:8000/health

Expected response:
{"status":"healthy","version":"1.0.0","pipeline_stages":4}

OPTION 3: KUBERNETES DEPLOYMENT (Production)

Deploy multiple replicas for high availability.

Create namespace:
kubectl create namespace audio-pipeline

Create ConfigMap for outputs:
kubectl create configmap pipeline-config \
 --from-literal=output-dir=/data/outputs \
 -n audio-pipeline

Create PersistentVolumeClaim:
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
 name: pipeline-data
 namespace: audio-pipeline
spec:
 accessModes:
 - ReadWriteMany
 resources:
 requests:
 storage: 100Gi

Create Deployment:
apiVersion: apps/v1
kind: Deployment
metadata:
 name: audio-pipeline
 namespace: audio-pipeline
spec:
 replicas: 3
 selector:
 matchLabels:
 app: audio-pipeline
 template:
 metadata:
 labels:
 app: audio-pipeline
 spec:
 containers:
 - name: api
 image: audio-pipeline:latest
 ports:
 - containerPort: 8000
 volumeMounts:
 - name: data
 mountPath: /data
 resources:
 requests:
 memory: "4Gi"
 cpu: "2"
 limits:
 memory: "8Gi"
 cpu: "4"
 volumes:
 - name: data
 persistentVolumeClaim:
 claimName: pipeline-data

Apply:
kubectl apply -f deployment.yaml

Expose service:
kubectl expose deployment audio-pipeline \
 --type=LoadBalancer \
 --port=8000 \
 --target-port=8000 \
 -n audio-pipeline

TROUBLESHOOTING

Model Download Issues

Problem: "Model download failed"
Solution:
- Check internet connection
- Verify disk space (need 5GB free)
- Check firewall/proxy settings
- Manually download: python -m demucs.pretrained

Problem: "CUDA out of memory"
Solution:
- Use CPU device instead: DEVICE=cpu
- Reduce batch size in code
- Process smaller files first

API Connection Failed

Problem: "Connection refused on port 8000"
Solutions:
- Port 8000 already in use: lsof -i:8000
- Kill process: kill -9 <PID>
- Or use different port: --port 8001

Problem: "API running but returning errors"
Solutions:
- Check logs: cat logs/pipeline.log
- Verify models downloaded: ls ~/.cache/deezer/demucs/
- Try health check: curl http://localhost:8000/health

Dependency Issues

Problem: "ModuleNotFoundError: librosa"
Solution:
pip install -r requirements.txt
pip install librosa --upgrade

Problem: "No module named demucs"
Solution:
pip install demucs --upgrade
python -m demucs.pretrained # Pre-download models

File Permission Issues

Linux/macOS - Grant permissions:
chmod +x ui/app.py
chmod +x api/app.py
chmod -R 755 uploads outputs downloads

Memory Issues

Problem: "MemoryError: Unable to allocate X GB"
Solutions:
- Increase system swap
- Process smaller files
- Close other applications
- Use GPU acceleration

Ubuntu swap increase:
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

FFmpeg Missing

Ubuntu/Debian:
sudo apt-get install ffmpeg

macOS:
brew install ffmpeg

Windows:
- Download: https://ffmpeg.org/download.html
- Extract to C:\ffmpeg
- Add C:\ffmpeg\bin to PATH
- Restart terminal/IDE

PERFORMANCE TUNING

CPU Processing:
- Default device
- Suitable for general use
- Takes 3-5 minutes for typical songs

GPU Processing (if available):
export DEVICE=cuda
Requires NVIDIA GPU with CUDA support
3-5x faster than CPU

Memory Optimization:
- Reduce batch size in processors
- Process files sequentially
- Archive old outputs regularly

Network Optimization (Kubernetes):
- Use LoadBalancer for traffic distribution
- Add caching layer (Redis)
- Enable gzip compression

MONITORING

Check system health:
curl http://localhost:8000/health

View recent jobs:
ls -lt outputs/ | head -20

Monitor logs:
tail -f logs/pipeline.log

Docker monitoring:
docker stats audio-pipeline

BACKUP AND RECOVERY

Backup outputs:
tar -czf outputs-backup-$(date +%Y%m%d).tar.gz outputs/

Backup manifests only:
find outputs -name manifest.json | tar -czf manifests-backup.tar.gz -T -

Restore from backup:
tar -xzf outputs-backup-*.tar.gz

SECURITY HARDENING

For production deployment:

1. Enable authentication:
- API key headers
- JWT token validation
- User authentication

2. Network security:
- Use HTTPS/TLS
- Firewall rules
- VPN access only

3. Data security:
- Encrypt stored files
- Secure deletion after retention period
- Access logs and auditing

4. System security:
- Regular security updates
- System hardening
- Antivirus/malware scanning

Configuration example:
SECURE_API_KEY=your-secret-key
ENABLE_HTTPS=true
RETENTION_DAYS=30

VERSION MANAGEMENT

Check installed version:
python -c "import pkg_resources; print(pkg_resources.get_distribution('demucs').version)"

Update components:
pip install --upgrade demucs librosa streamlit fastapi

Check for compatibility:
pip check

UNINSTALLATION

Docker cleanup:
docker-compose down
docker rmi audio-pipeline:latest
docker volume prune

Local installation cleanup:
deactivate # Exit virtual environment
rm -rf venv # Remove virtual environment
rm -rf outputs uploads downloads logs # Remove data

GETTING HELP

Documentation:
- README.md: Quick start
- ARCHITECTURE.md: System design
- API_DOCS.md: API reference
- SCREENING_ANSWERS.md: Design rationale

Community:
- Check issues in GitHub
- Review troubleshooting section
- Post in discussions forum

Support:
- Review logs in outputs/{job_id}/manifest.json
- Enable debug logging
- Capture error messages
- Include system specs in reports