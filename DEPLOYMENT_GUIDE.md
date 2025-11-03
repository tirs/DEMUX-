Audio Pipeline - Production Deployment Guide

PRODUCTION CHECKLIST

Pre-Deployment Verification:
 All tests passing: python -m pytest tests/
 Docker builds successfully: docker build.
 Environment variables configured:.env file created
 Resource requirements met: CPU, RAM, storage
 Network configuration reviewed: Firewall, ports
 Backup strategy in place: Outputs directory
 Monitoring configured: Logging, health checks
 Documentation reviewed: README, ARCHITECTURE

DOCKER PRODUCTION DEPLOYMENT

Production Dockerfile Optimization

FROM python:3.11-slim as base

RUN apt-get update && apt-get install -y --no-install-recommends \
 ffmpeg \
 libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

FROM base as builder

WORKDIR /app
COPY requirements.txt.
RUN pip install --user --no-cache-dir -r requirements.txt

FROM base

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY..

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

RUN mkdir -p uploads outputs downloads logs

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
 CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000 8501

CMD ["sh", "-c", "python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 & \
 streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0"]

Production docker-compose.yml

version: "3.8"

services:
 audio-pipeline:
 build:
 context:.
 dockerfile: Dockerfile
 container_name: audio-pipeline-api
 restart: unless-stopped
 ports:
 - "8000:8000"
 - "8501:8501"
 volumes:
 - pipeline-uploads:/app/uploads
 - pipeline-outputs:/app/outputs
 - pipeline-downloads:/app/downloads
 - pipeline-logs:/app/logs
 environment:
 - PYTHONUNBUFFERED=1
 - DEVICE=cpu
 - API_HOST=0.0.0.0
 - API_PORT=8000
 - LOGGING_LEVEL=INFO
 - MAX_FILE_SIZE_MB=500
 - JOB_RETENTION_DAYS=30
 healthcheck:
 test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
 interval: 30s
 timeout: 10s
 retries: 3
 start_period: 40s
 networks:
 - pipeline-network
 deploy:
 resources:
 limits:
 cpus: "4"
 memory: 8G
 reservations:
 cpus: "2"
 memory: 4G
 logging:
 driver: "json-file"
 options:
 max-size: "10m"
 max-file: "3"

volumes:
 pipeline-uploads:
 pipeline-outputs:
 pipeline-downloads:
 pipeline-logs:

networks:
 pipeline-network:
 driver: bridge

Launch:
docker-compose -f docker-compose.prod.yml up -d

Monitor:
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml ps

NGINX REVERSE PROXY CONFIGURATION

/etc/nginx/sites-available/audio-pipeline

upstream audio_api {
 server localhost:8000;
}

upstream audio_ui {
 server localhost:8501;
}

server {
 listen 80;
 server_name audio-pipeline.yourdomain.com;

 client_max_body_size 500M;

 location /api/ {
 proxy_pass http://audio_api/;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 proxy_read_timeout 300s;
 proxy_connect_timeout 300s;
 }

 location / {
 proxy_pass http://audio_ui/;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection "upgrade";
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
 proxy_set_header X-Forwarded-Proto $scheme;
 }

 # SSL configuration (use certbot)
 # listen 443 ssl;
 # ssl_certificate /etc/letsencrypt/live/audio-pipeline.yourdomain.com/fullchain.pem;
 # ssl_certificate_key /etc/letsencrypt/live/audio-pipeline.yourdomain.com/privkey.pem;
}

Enable:
sudo ln -s /etc/nginx/sites-available/audio-pipeline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

KUBERNETES DEPLOYMENT

namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
 name: audio-pipeline

configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
 name: pipeline-config
 namespace: audio-pipeline
data:
 DEVICE: "cpu"
 API_HOST: "0.0.0.0"
 LOGGING_LEVEL: "INFO"
 MAX_FILE_SIZE_MB: "500"

pvc.yaml

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
 name: pipeline-data
 namespace: audio-pipeline
spec:
 accessModes:
 - ReadWriteMany
 storageClassName: nfs
 resources:
 requests:
 storage: 500Gi

deployment.yaml

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
 - name: pipeline
 image: audio-pipeline:1.0.0
 ports:
 - containerPort: 8000
 name: api
 - containerPort: 8501
 name: ui
 envFrom:
 - configMapRef:
 name: pipeline-config
 volumeMounts:
 - name: data
 mountPath: /app/outputs
 subPath: outputs
 - name: data
 mountPath: /app/uploads
 subPath: uploads
 - name: data
 mountPath: /app/downloads
 subPath: downloads
 - name: data
 mountPath: /app/logs
 subPath: logs
 resources:
 requests:
 cpu: 2000m
 memory: 4Gi
 limits:
 cpu: 4000m
 memory: 8Gi
 livenessProbe:
 httpGet:
 path: /health
 port: 8000
 initialDelaySeconds: 30
 periodSeconds: 10
 timeoutSeconds: 5
 failureThreshold: 3
 readinessProbe:
 httpGet:
 path: /health
 port: 8000
 initialDelaySeconds: 10
 periodSeconds: 5
 volumes:
 - name: data
 persistentVolumeClaim:
 claimName: pipeline-data

service.yaml

apiVersion: v1
kind: Service
metadata:
 name: audio-pipeline
 namespace: audio-pipeline
spec:
 selector:
 app: audio-pipeline
 ports:
 - port: 8000
 targetPort: 8000
 name: api
 - port: 8501
 targetPort: 8501
 name: ui
 type: LoadBalancer

Deploy:
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

Check:
kubectl get pods -n audio-pipeline
kubectl get svc -n audio-pipeline
kubectl logs -n audio-pipeline <pod-name>

MONITORING AND LOGGING

Prometheus Metrics (Optional)

Add to api/app.py:

from prometheus_client import Counter, Histogram, generate_latest

processing_counter = Counter(
 'audio_processing_total',
 'Total processing jobs',
 ['status']
)

processing_time = Histogram(
 'audio_processing_seconds',
 'Processing time in seconds',
 buckets=[60, 120, 180, 300, 600]
)

@app.get("/metrics")
async def metrics():
 return generate_latest()

Grafana Dashboard:
- Query: audio_processing_total
- Query: rate(audio_processing_seconds_bucket[5m])
- Alert: processing_time > 600s

Log Aggregation

Stack options:
1. ELK Stack (Elasticsearch, Logstash, Kibana)
2. Loki + Grafana
3. Cloudwatch (AWS)
4. Stackdriver (GCP)

Example with Loki:

Configure filebeat:
filebeat.inputs:
- type: log
 paths:
 - /app/logs/*.log

output.elasticsearch:
 hosts: ["elasticsearch:9200"]

BACKUP STRATEGY

Automated Backups

#!/bin/bash
BACKUP_DIR="/backups/audio-pipeline"
OUTPUTS_DIR="/app/outputs"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup manifests only (fast)
find "$OUTPUTS_DIR" -name "manifest.json" | \
 tar -czf "$BACKUP_DIR/manifests_$DATE.tar.gz" -T -

# Backup outputs (full)
tar -czf "$BACKUP_DIR/outputs_$DATE.tar.gz" "$OUTPUTS_DIR"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

Schedule with cron:
0 2 * * * /scripts/backup.sh

Cloud Backup (AWS S3):

aws s3 sync /app/outputs s3://audio-pipeline-backups/outputs/ \
 --delete \
 --storage-class GLACIER

SECURITY HARDENING

API Authentication

Add to api/app.py:

from fastapi.security import APIKeyHeader

api_key = APIKeyHeader(name="X-API-Key")

@app.post("/process")
async def process_audio(file: UploadFile, api_key: str = Depends(api_key)):
 if api_key!= os.getenv("API_KEY"):
 raise HTTPException(status_code=403, detail="Invalid API key")
 # Process...

Rate Limiting

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/process")
@limiter.limit("10/hour")
async def process_audio(request: Request, file: UploadFile):
 # Process...

HTTPS/TLS

With Let's Encrypt:

sudo certbot certonly --standalone -d audio-pipeline.yourdomain.com

Update Nginx:
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/audio-pipeline.yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/audio-pipeline.yourdomain.com/privkey.pem;

Auto-renewal:
sudo certbot renew --dry-run

Firewall Rules

UFW (Ubuntu):
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw default deny incoming
sudo ufw enable

AWS Security Group:
- Inbound: Port 80 (HTTP), 443 (HTTPS)
- Outbound: All
- Source: Your IP range

PERFORMANCE TUNING

Resource Allocation

CPU:
- 1 core per 2 jobs (separation bottleneck)
- 4+ cores recommended
- More cores = parallel processing

Memory:
- Minimum: 4GB
- Recommended: 8-16GB
- Peak: ~3GB per job

Storage:
- Models: ~2GB
- Temp files: 5-10x audio file size
- Outputs: Audio files stored permanently
- Logs: 100-500MB per month

Database Optimization

If migrating to database:
- Index on job_id, created_at
- Partition by date
- Archive old manifests
- Query optimization

Connection pooling:
max_connections=20
pool_size=5
max_overflow=10

JOB SCHEDULING

Task Queue (Celery example)

from celery import Celery

celery_app = Celery(
 'audio_pipeline',
 broker='redis://localhost:6379'
)

@celery_app.task
def process_audio_task(file_path):
 manifest = pipeline.process(file_path)
 return manifest.to_dict()

Usage:
task = process_audio_task.delay(file_path)
status = task.status

ALERTING AND NOTIFICATIONS

Alert Conditions

Processing timeout:
- If job > 10 minutes: Alert
- If stage > 5 minutes: Log warning

Error rate:
- If > 10% failures: Alert
- If specific stage failing: Log

Resource exhaustion:
- Disk space < 10%
- Memory usage > 90%
- CPU sustained > 95%

Notification Channels

Email:
- Send alerts to ops@yourdomain.com
- Daily summary report

Slack:
- Webhook integration
- Real-time alerts
- Failure notifications

PagerDuty:
- Critical alerts
- On-call rotation
- Escalation

DISASTER RECOVERY

RTO/RPO Targets

Recovery Time Objective: 1 hour
Recovery Point Objective: 1 day

Failure Scenarios

Scenario: Disk full
- Cleanup old outputs
- Restore from backup
- Alert ops team

Scenario: Model corruption
- Re-download models
- Clear cache
- Restart service

Scenario: Complete system failure
- Restore from last backup
- Reconfigure services
- Resume processing

Recovery Plan

1. Identify failure type
2. Check backups available
3. Stop services
4. Restore data
5. Verify integrity
6. Start services
7. Resume processing

MAINTENANCE SCHEDULE

Daily:
- Check system health
- Review error logs
- Monitor disk space

Weekly:
- Run full backup
- Review performance metrics
- Update dependencies (test)

Monthly:
- Security updates
- Database maintenance
- Capacity planning

Quarterly:
- Major version updates
- Architecture review
- Performance audit

COST OPTIMIZATION

Resource Sizing

Underutilization check:
- Monitor CPU/Memory usage
- Right-size containers
- Use spot instances (cloud)

Unused resources:
- Archive old outputs
- Delete temporary files
- Consolidate services

Cloud-specific:
- Reserved instances (1-3 year discount)
- Auto-scaling groups
- Cost monitoring/alerts

COMPLIANCE AND AUDIT

Data Retention

Manifests: Keep indefinitely (immutable audit trail)
Audio files: Keep per policy (30/60/90 days)
Logs: Keep 6 months
Backups: Keep 1 year

Compliance requirements:
- GDPR: Implement right to be forgotten
- HIPAA: Encrypt data at rest and in transit
- SOC2: Maintain audit logs

Audit Trail

Every action logged:
- User, timestamp, action
- Input parameters
- Output results
- Errors/failures

Example log entry:
2024-01-15 10:30:45 - USER:api - ACTION:process - \
 INPUT:song.wav - OUTPUT:job_id:abc123 - STATUS:completed