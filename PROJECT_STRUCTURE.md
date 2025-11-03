Audio Pipeline - Project Structure and Components

PROJECT DIRECTORY TREE

audio-pipeline/
 core/
 __init__.py # Core module exports
 pipeline.py # Pipeline orchestration (300 lines)
 separator.py # Model abstraction (150 lines)
 processors.py # Processing stages (350 lines)
 api/
 __init__.py
 app.py # FastAPI application (320 lines)
 ui/
 __init__.py
 app.py # Streamlit UI (360 lines)
 tests/
 test_pipeline.py # Unit tests (320 lines)
 logs/ # Runtime logs (created automatically)
 uploads/ # Temporary upload storage (created automatically)
 outputs/ # Processing results (created automatically)
 downloads/ # Downloaded files (created automatically)
 Dockerfile # Container definition
 docker-compose.yml # Multi-container setup
 requirements.txt # Python dependencies
 config.py # Configuration management.env.example # Environment variables template
 README.md # Quick start guide
 INSTALLATION.md # Setup instructions
 ARCHITECTURE.md # System design
 API_DOCS.md # API reference
 SCREENING_ANSWERS.md # Design rationale
 EXAMPLES.md # Usage examples
 PROJECT_STRUCTURE.md # This file

COMPONENT DESCRIPTIONS

CORE PIPELINE (core/)

pipeline.py
- AudioPipeline: Main orchestration class
- PipelineStage: Abstract base for processors
- ProcessingManifest: Job metadata container
- ProcessingStage: Stage execution record

Key classes:
- AudioPipeline: Manages stage execution, job lifecycle
- ProcessingManifest: Tracks processing history
- PipelineStage (ABC): Interface for all stages

Responsibilities:
- Sequential stage execution
- Error handling and recovery
- Manifest generation and persistence
- Job status tracking

separator.py
- SeparatorModel: Abstract base for audio separators
- DemucsModel: Demucs implementation
- SeparatorFactory: Model creation and registration

Key classes:
- SeparatorModel (ABC): Defines separator interface
- DemucsModel: Concrete Demucs implementation
- SeparatorFactory: Factory pattern for model creation

Responsibilities:
- Model abstraction and swapping
- Runtime model selection
- Validation and error handling

processors.py
- SeparationStage: Main audio separation
- HarmonicPercussiveStage: H/P decomposition
- CompositeTrackStage: Composite track generation
- NormalizationStage: Audio normalization

Key classes:
- SeparationStage: Uses separator models
- HarmonicPercussiveStage: librosa-based decomposition
- CompositeTrackStage: Generates main tracks
- NormalizationStage: Audio level adjustment

Responsibilities:
- Implement PipelineStage interface
- Execute specific processing tasks
- Validate inputs and handle errors
- Generate output files

API SERVER (api/)

app.py (FastAPI application)
- Health checks
- Configuration endpoint
- File upload/processing
- Status tracking
- Track downloads
- ZIP export

Endpoints:
- GET /health: System status
- GET /config: Configuration info
- POST /process: Upload and process
- GET /job/{id}: Get status
- GET /job/{id}/outputs: Get output list
- GET /download/{id}/{track}: Download track
- GET /download/{id}/all: Download ZIP

Features:
- CORS enabled
- Error handling with HTTP codes
- Streaming file downloads
- ZIP file generation
- Pipeline initialization

Middleware:
- CORS handling
- Request/response logging
- Error handling

USER INTERFACE (ui/)

app.py (Streamlit application)
- File upload interface
- Progress tracking
- Track management
- Download interface
- Job history

Pages:
- Upload & Process: File upload and monitoring
- View Results: Status and downloads
- Job History: Reload previous jobs

Features:
- Real-time status updates
- Individual track downloads
- Batch ZIP download
- Job ID persistence
- Responsive UI

CONFIGURATION (config.py)

Environment-based configuration:
- Directories: uploads, outputs, logs
- API settings: host, port
- Processing: device, model, target_db
- Limits: file size, retention period
- Logging: level, format
- Security: CORS origins

All settings can be overridden via environment variables.

TESTING (tests/)

test_pipeline.py
- Pipeline initialization tests
- Stage registration tests
- Manifest creation tests
- Error handling tests
- Separator factory tests

Test coverage:
- Core pipeline functionality
- Separator abstraction
- Manifest persistence
- Error recovery
- Mock implementations

Run tests:
python -m pytest tests/

DOCKER CONFIGURATION

Dockerfile
- Python 3.11 slim base image
- FFmpeg and audio dependencies
- Python package installation
- Application setup
- Directory creation
- Port exposure (8000, 8501)

docker-compose.yml
- Single service: audio-pipeline
- Port mapping: 8000 (API), 8501 (UI)
- Volume mounts: uploads, outputs, downloads
- Environment configuration
- Health checks
- Restart policy

RUNTIME DIRECTORIES

uploads/
- Temporary file storage
- Cleaned after processing
- Max 500MB per file

outputs/
- Processing results
- Structure: {job_id}/
 - manifest.json: Processing metadata
 - {processor_name}/: Processor-specific outputs
 - track_name.wav: Output audio files

downloads/
- Downloaded files from UI
- Temporary storage
- User managed

logs/
- Application logs
- Pipeline execution logs
- Error logs
- Structured logging format

DATA FLOW

1. INPUT
 uploads/ directory
 Receives file via:
 POST /process (API)
 Streamlit file uploader (UI)
 Temporary storage during processing

2. PROCESSING
 Pipeline stages execute sequentially:
 - SeparationStage: Split audio into tracks
 - HarmonicPercussiveStage: Decompose audio
 - CompositeTrackStage: Generate main tracks
 - NormalizationStage: Normalize levels

3. OUTPUT
 outputs/{job_id}/
 manifest.json: Complete metadata
 demucs_output/: Separated tracks
 harmonic_percussive/: H/P components
 composite/: Main track variants

4. DELIVERY
 Download options:
 - Single track: /download/{id}/{track}
 - All tracks: /download/{id}/all (ZIP)
 - Via UI or API

DEPENDENCIES

Python Packages:
- fastapi: Web framework (API)
- uvicorn: ASGI server
- streamlit: UI framework
- requests: HTTP client (UI communication)
- librosa: Audio processing
- soundfile: Audio I/O
- demucs: Audio separation model
- torch/torchaudio: Deep learning framework
- numpy/scipy: Scientific computing

System Packages:
- ffmpeg: Audio codec support
- libsndfile1: Audio library

EXTENSION POINTS

Adding New Separator:
1. Extend SeparatorModel
2. Implement interface methods
3. Register with factory
4. Select in configuration

Adding New Stage:
1. Extend PipelineStage
2. Implement execute() and validate_input()
3. Add to pipeline in api/app.py

Adding New Processor:
1. Create new class in processors.py
2. Use existing library (librosa, scipy, etc.)
3. Follow output format conventions

PERFORMANCE CHARACTERISTICS

Code Size:
- core/pipeline.py: ~300 lines
- core/separator.py: ~150 lines
- core/processors.py: ~350 lines
- api/app.py: ~320 lines
- ui/app.py: ~360 lines
Total core: ~1,480 lines

Memory Usage:
- Base: ~200MB (libraries)
- Processing: +1-3GB (audio buffers, models)
- Typical peak: ~3GB

Disk Usage:
- Models: ~2GB
- Per job: 0.5-5GB (depending on audio)
- Manifests: <10KB each

Processing Time (3-min audio):
- Separation: ~3 minutes (CPU)
- Other stages: ~1 minute
- Total: ~4-5 minutes (CPU)
- With GPU: 1-2 minutes

ERROR HANDLING PATHS

Input Validation → Stage Validation → Processing → Completion
 ↓ ↓ ↓ ↓
 Invalid Skip Stage Error Success
 Return 400 Record Error Record Return 200
 Log Fail
 Manifest

All paths lead to persistent manifest.

LOGGING STRUCTURE

Loggers:
- pipeline: Main orchestration
- stage.*: Per-stage logging
- separator.*: Separator operations
- API (uvicorn): Request logging

Log Format:
2024-01-15 10:30:45,123 - pipeline - INFO - Message

Environment:
LOGGING_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL

OUTPUT GENERATION

Each processing stage produces:
- Output files (WAV format)
- Metadata in manifest
- Logs to console/file
- Duration tracking

Example outputs:
- SeparationStage: vocals, drums, bass, other
- HPStage: harmonic, percussive
- CompositeStage: main, main_harmonic, main_percussive
- NormalizationStage: normalized tracks

SECURITY MODEL

Current:
- No authentication
- CORS allows all origins
- File size limits enforced
- Input validation

Production recommendations:
- API key authentication
- Restrict CORS origins
- Rate limiting
- HTTPS/TLS
- Access logging
- File scanning

DATABASE/PERSISTENCE

Manifest Storage:
- JSON files in outputs/{job_id}/
- Atomic writes
- No external database required
- Self-contained per job

Recovery:
- Query any job by ID
- Complete history persisted
- Reproducible state

Scaling:
- Directory-based for single instance
- Could migrate to database (PostgreSQL)
- Distributed file system for clustering

DEPLOYMENT SCENARIOS

Single Docker Container:
- API + UI in one container
- Volumes for persistence
- Simple deployment
- Resource efficient

Kubernetes:
- Multiple replicas for HA
- LoadBalancer for distribution
- PersistentVolumes for data
- Better resource utilization
- Auto-scaling capable

Distributed:
- API on separate instance
- UI connected remotely
- Processing queue possible
- Better separation of concerns

CONFIGURATION MANAGEMENT

Environment Variables:.env file or shell environment
- API_HOST, API_PORT
- DEVICE (cpu/cuda)
- SEPARATOR_MODEL
- File size limits
- Logging level

Runtime Config:
config.py handles loading and defaults

Overrides:
Environment variables > config.py > code defaults