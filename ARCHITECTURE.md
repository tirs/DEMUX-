Audio Pipeline - Architecture and Design

SYSTEM OVERVIEW

The system follows a stage-based pipeline architecture where each processing stage:
- Has a well-defined interface (PipelineStage ABC)
- Validates input before processing
- Returns structured output
- Tracks execution metadata

Pipeline Flow:
Input Audio -> Separation Stage -> HP Separation -> Composite Track -> Normalization -> Output Tracks

CORE COMPONENTS

1. Pipeline Orchestration (core/pipeline.py)

AudioPipeline class manages:
- Stage registration and execution
- Job lifecycle management
- Error handling and recovery
- Result manifest creation

Key Features:
- Sequential stage execution
- Atomic job operations
- Complete tracking of all stages
- Manifest versioning

2. Separator Abstraction (core/separator.py)

SeparatorModel (ABC)
- define interface: separate(), validate(), get_supported_tracks()
- Demucs implementation handles actual separation
- Factory pattern for model creation

Enables:
- Model swapping without code changes
- Multiple separator implementations
- Runtime model selection

3. Processing Stages (core/processors.py)

SeparationStage: Main audio separation (vocals, drums, bass, other)
HarmonicPercussiveStage: Decompose audio into harmonic/percussive components
CompositeTrackStage: Generate main, main_harmonic, main_percussive tracks
NormalizationStage: Audio level normalization

Each stage:
- Validates input independently
- Produces specific output tracks
- Logs execution details
- Handles errors gracefully

4. API (api/app.py)

FastAPI application exposing:
- /process: Upload and process audio
- /job/{id}: Get job status
- /download: Download tracks
- /config: System configuration

Features:
- CORS enabled for external integration
- Streaming downloads for large files
- ZIP export for all tracks
- Health checks and metrics

5. User Interface (ui/app.py)

Streamlit application providing:
- File upload interface
- Real-time progress tracking
- Individual track download
- Batch download as ZIP
- Job history and reload capability

DESIGN ANSWERS

Question 1: Module Encapsulation for Swappable Separators

ANSWER: Factory Pattern + Abstract Base Class

Implementation:
```python
class SeparatorModel(ABC):
 @abstractmethod
 def separate(input_path, output_dir) -> Dict[str, str]
 @abstractmethod
 def validate() -> bool

class SeparatorFactory:
 @classmethod
 def create_separator(separator_type, **kwargs) -> SeparatorModel
 @classmethod
 def register_separator(name, separator_class)
```

To add new separator (e.g., Spleeter):
1. Create class extending SeparatorModel
2. Implement required methods
3. Register: SeparatorFactory.register_separator("spleeter", SpleeterModel)
4. Use: SeparatorFactory.create_separator("spleeter")

Benefits:
- No changes to pipeline code
- Runtime model selection
- Easy testing with mock separators
- Clear interface contracts

Question 2: Error Handling and Crash Resilience

ANSWER: Multi-Layer Error Strategy

Implementation:
1. Input Validation Layer
 - Format verification
 - File size checks
 - Audio codec validation
 - Early failure detection

2. Execution Error Handling
 - Try-catch around all processing
 - Error capture in stage records
 - Detailed error messages
 - Graceful degradation

3. Manifest Recording
 - All stages tracked
 - Success/failure states
 - Error messages stored
 - Processing metadata persisted

4. Job Recovery
 - Manifests stored independently
 - Can replay from checkpoint
 - No data loss
 - Clear audit trail

Example:
```python
try:
 outputs = stage.execute(input_file, job_dir)
except Exception as e:
 stage_record.status = "failed"
 stage_record.error = str(e)
 manifest.status = "failed"
 logger.error(...)
 raise
```

Benefits:
- Clear failure points
- No silent failures
- Full recovery information
- Operator visibility

Question 3: Robustness Against Difficult Input Formats

ANSWER: Progressive Validation + Format Normalization

Implementation:
1. Format Detection
```python
def validate_input(input_path: str) -> bool:
 path = Path(input_path)
 # Check existence
 if not path.exists()
 # Check extension
 if path.suffix.lower() not in [".wav", ".mp3", ".flac", ".ogg"]
 # Check file size
 if file_size_mb > 500
```

2. Audio Codec Handling
 - Uses librosa/torchaudio (auto-detect codecs)
 - Handles sample rate conversion
 - Manages bit depth variations
 - Resamples to common rate if needed

3. Error Recovery
 - Detailed logging of codec issues
 - Fallback to alternative decoders
 - User feedback with specific errors
 - Manifest documents exact issue

4. Input Constraints
 - Maximum 500 MB files
 - Supported formats: WAV, MP3, FLAC, OGG
 - Sample rates: 16kHz to 48kHz
 - Mono and stereo support

Question 4: Artifact Versioning and Result Manifest

ANSWER: JSON-Based Manifest System

Implementation:
```python
@dataclass
class ProcessingManifest:
 job_id: str # Unique identifier
 input_file: str # Original file
 created_at: str # ISO timestamp
 version: str # Schema version
 stages: List[...] # All stage records
 outputs: Dict # Output file paths
 metadata: Dict # System metadata
 status: str # Overall status
```

Versioning Strategy:
- Version 1.0: Current schema
- Backward compatible design for future versions
- Schema stored in manifest for validation
- Migration path defined for upgrades

Manifest Features:
1. Atomic Job Record
 - Self-contained
 - Reproducible
 - Auditable

2. Stage Tracking
 ```python
 @dataclass
 class ProcessingStage:
 name: str
 processor_type: str
 status: str
 started_at: str
 completed_at: str
 error: Optional[str]
 duration_seconds: Optional[float]
 ```

3. Artifact Organization
 - outputs/{job_id}/manifest.json (metadata)
 - outputs/{job_id}/*/track.wav (actual files)
 - Logical grouping by processor

4. Recovery and Audit
 - Complete processing history
 - Reproducible results
 - Version tracking
 - Failure diagnostics

File Structure:
```
outputs/
 {job_id}/
 manifest.json # Main manifest
 demucs_output/
 vocals.wav
 drums.wav
 bass.wav
 other.wav
 harmonic_percussive/
 harmonic.wav
 percussive.wav
 composite/
 main.wav
 main_harmonic.wav
 main_percussive.wav
```

MODULARITY AND EXTENSIBILITY

Stage Extension Points:
1. Create new stage class extending PipelineStage
2. Implement execute() and validate_input()
3. Add to pipeline: pipeline.add_stage(NewStage())

Separator Extension Points:
1. Create class extending SeparatorModel
2. Implement required methods
3. Register with factory
4. Use via factory creation

Example: Adding NVIDIA Denoiser Stage
```python
class DenoiseStage(PipelineStage):
 def __init__(self):
 super().__init__("denoising", "audio_processing")

 def execute(self, input_path, output_dir):
 # Implementation here
 return {"denoised": output_path}

# Register
pipeline.add_stage(DenoiseStage())
```

DEPLOYMENT ARCHITECTURE

Docker Structure:
- Single container with API + UI
- Volumes for persistence
- Health checks for monitoring
- Resource limits configurable

Scaling Considerations:
- API can run independently
- UI can connect to remote API
- Processing can be queued
- Multiple pipelines can run in parallel

API Integration:
- Stateless design
- RESTful endpoints
- Standard HTTP methods
- JSON responses
- Error handling with HTTP codes

PERFORMANCE CHARACTERISTICS

Pipeline Stages:
1. Separation: ~70% of total time
2. HP Decomposition: ~15% of total time
3. Composite Creation: ~5% of total time
4. Normalization: ~10% of total time

Bottlenecks:
- Model inference (separation stage)
- Audio I/O operations
- Memory constraints
- Disk I/O for large files

Optimization Opportunities:
- Batch processing
- GPU acceleration
- Caching model weights
- Async API calls
- Parallel stage execution

TESTING STRATEGY

Unit Testing:
- Mock separators
- Pipeline orchestration
- Manifest generation
- API endpoints

Integration Testing:
- Full pipeline with test audio
- Error condition handling
- Result verification
- Performance benchmarks

End-to-End Testing:
- Docker deployment
- UI functionality
- API load testing
- File I/O validation

SECURITY CONSIDERATIONS

Input Validation:
- File type verification
- Size limits
- Path traversal prevention

API Security:
- CORS configuration
- Rate limiting (future)
- Input sanitization

Data Isolation:
- Job-based directory structure
- No cross-job access
- Secure file permissions

FUTURE EXTENSIONS

Potential Enhancements:
1. Real-time progress streaming (WebSocket)
2. Batch job processing
3. Model fine-tuning capability
4. Custom mixing/mastering stages
5. Effects processing stages
6. Audio quality analysis
7. Distributed processing
8. Multi-format output
9. Metadata extraction
10. Automatic backups

These can be added without core architecture changes.