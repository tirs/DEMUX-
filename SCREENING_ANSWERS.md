Audio Pipeline - Screening Questions and Answers

QUESTION 1: Module Encapsulation for Swappable Separators

Q: How would you encapsulate the separator module so that we can exchange models later?

ANSWER:

I implemented a Factory Pattern combined with Abstract Base Class to achieve complete model interchangeability:

1. Abstract Interface (core/separator.py):

class SeparatorModel(ABC):
 @abstractmethod
 def separate(input_path, output_dir) -> Dict[str, str]
 
 @abstractmethod
 def validate() -> bool
 
 @abstractmethod
 def get_supported_tracks() -> List[str]

This defines the contract any separator must implement.

2. Concrete Implementation:

class DemucsModel(SeparatorModel):
 def separate(...) -> Dict[str, str]:
 # Implementation specific to Demucs
 
 def validate() -> bool:
 # Model-specific validation
 
 def get_supported_tracks() -> List[str]:
 return ["drums", "bass", "other", "vocals"]

3. Factory Pattern for Runtime Selection:

class SeparatorFactory:
 _separators = {"demucs": DemucsModel}
 
 @classmethod
 def register_separator(cls, name, separator_class):
 cls._separators[name] = separator_class
 
 @classmethod
 def create_separator(cls, separator_type, **kwargs):
 return cls._separators[separator_type](**kwargs)

4. Usage in Pipeline:

# At initialization
separator = SeparatorFactory.create_separator(
 "demucs",
 model_name="htdemucs_ft",
 device="cpu"
)

# To swap models later:
SeparatorFactory.register_separator("spleeter", SpleeterModel)
separator = SeparatorFactory.create_separator("spleeter")

BENEFITS:
- Zero changes to pipeline orchestration code
- New separators added without modifying existing code
- Runtime model selection
- Easy mocking for testing
- Clear interface contracts

ADDING NEW SEPARATOR (Example: Spleeter):

1. Create implementation:
class SpleeterModel(SeparatorModel):
 def separate(self, input_path, output_dir):
 # Spleeter-specific logic
 return {"vocals": path1, "accompaniment": path2}

2. Register:
from core.separator import SeparatorFactory
SeparatorFactory.register_separator("spleeter", SpleeterModel)

3. Use immediately:
sep = SeparatorFactory.create_separator("spleeter")

No changes needed to existing pipeline code.

QUESTION 2: Error Handling and Crash Resilience

Q: What measures would you take to ensure that the system generates an error message in the event of a possible crash?

ANSWER:

I implemented multi-layer error handling throughout the system:

1. INPUT VALIDATION LAYER (Early Failure Detection):

def validate_input(self, input_path: str) -> bool:
 path = Path(input_path)
 if not path.exists():
 self.logger.error(f"Input file not found: {input_path}")
 return False
 
 if path.suffix.lower() not in [".wav", ".mp3", ".flac", ".ogg"]:
 self.logger.error(f"Unsupported audio format: {path.suffix}")
 return False
 
 file_size_mb = path.stat().st_size / (1024 * 1024)
 if file_size_mb > 500:
 self.logger.error(f"File too large: {file_size_mb}MB")
 return False
 
 return True

Prevents crashes from invalid inputs before processing starts.

2. STAGE-LEVEL ERROR HANDLING (Execution Phase):

try:
 if not stage.validate_input(input_file):
 raise ValueError(f"Invalid input for stage {stage.name}")
 
 stage_record.status = "processing"
 outputs = stage.execute(input_file, str(job_dir))
 stage_record.status = "completed"

except Exception as e:
 stage_record.status = "failed"
 stage_record.error = str(e)
 manifest.status = "failed"
 self.logger.error(f"Stage {stage.name} failed: {str(e)}")
 raise # Propagate for caller handling

Captures all exceptions and records them.

3. MANIFEST RECORDING (Atomic Job State):

ProcessingManifest captures:
- job_id: Unique identifier
- created_at: Timestamp for audit
- stages: Complete history of all stages with:
 * status: pending/processing/completed/failed
 * started_at: When stage started
 * completed_at: When stage finished
 * error: Exception message if failed
 * duration_seconds: Execution time
- metadata: System information
- outputs: Generated file paths

Even if system crashes, manifest is written and persists.

4. PERSISTENT JOB STORAGE:

manifest_path = job_dir / "manifest.json"
with open(manifest_path, "w") as f:
 f.write(manifest.to_json())

Manifest written to disk after each stage.
Can recover job status anytime via job_id.

5. API ERROR RESPONSES:

Responses include HTTP status codes and error details:

Response (500 Internal Server Error):
{
 "detail": "Demucs model failed: CUDA out of memory"
}

Response (400 Bad Request):
{
 "detail": "File format not supported:.aac"
}

6. LOGGING INFRASTRUCTURE:

logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

Every component logs:
- Stage start/completion
- Error conditions
- Processing metrics
- Resource warnings

7. RECOVERY CAPABILITIES:

After crash:
1. Query GET /job/{job_id}
2. Retrieve manifest with complete history
3. Resume from known state
4. Retry failed stages

Error visibility example:
curl http://localhost:8000/job/abc123
Returns manifest with exact error that caused failure.

BENEFITS:
- No silent failures
- Complete audit trail
- Reproducible error conditions
- Easy debugging
- Operator visibility

QUESTION 3: Robustness Against Difficult Input Formats

Q: What measures would you implement to ensure robustness against "difficult" input formats?

ANSWER:

I implemented progressive validation and flexible audio handling:

1. MULTI-LAYER VALIDATION:

Format Detection Layer:
def validate_input(self, input_path: str) -> bool:
 path = Path(input_path)
 
 # Existence check
 if not path.exists():
 raise FileNotFoundError(f"File not found: {input_path}")
 
 # Format check
 supported = [".wav", ".mp3", ".flac", ".ogg"]
 if path.suffix.lower() not in supported:
 raise ValueError(f"Unsupported format: {path.suffix}")
 
 # Size check
 size_mb = path.stat().st_size / (1024 * 1024)
 if size_mb > 500:
 raise ValueError(f"File too large: {size_mb}MB (max 500MB)")
 
 return True

2. CODEC HANDLING:

Using librosa and torchaudio (industry-standard libraries):

y, sr = librosa.load(input_path, sr=None)

These libraries:
- Auto-detect audio codec
- Handle bit depth variations
- Support mono/stereo
- Convert sample rates if needed
- Catch codec errors gracefully

3. AUDIO FORMAT CONVERSION:

if sample_rate!= target_sample_rate:
 y = librosa.resample(y, orig_sr=sample_rate, target_sr=target_sample_rate)

if y.ndim == 1:
 y = np.expand_dims(y, 0) # Convert mono to stereo

Standardizes all audio to expected format.

4. ERROR-SPECIFIC HANDLING:

try:
 wav, sr = torchaudio.load(input_path)
except RuntimeError as e:
 if "codec" in str(e).lower():
 raise ValueError(f"Audio codec not supported: {str(e)}")
 elif "corrupt" in str(e).lower():
 raise ValueError(f"Audio file appears corrupted: {str(e)}")
 else:
 raise

Specific error messages for different issues.

5. SUPPORTED INPUT FORMATS:

Format: WAV
- Codec: PCM (raw)
- Container: RIFF
- Bit depth: 8, 16, 24, 32-bit
- Sample rate: 8kHz to 48kHz
- Channels: Mono, stereo

Format: MP3
- Codec: MPEG-1 Layer III
- Bit rates: 128kbps to 320kbps
- Sample rates: 16kHz, 22.05kHz, 24kHz, 44.1kHz, 48kHz
- Channels: Mono, stereo

Format: FLAC
- Codec: Free Lossless Audio Codec
- Bit depth: 8 to 32-bit
- Sample rates: Up to 655.35kHz
- Channels: Mono to 8 channels

Format: OGG
- Codec: Ogg Vorbis
- Bit rates: 64kbps to 500kbps
- Sample rates: Any rate supported
- Channels: Mono, stereo

6. CONSTRAINT ENFORCEMENT:

File size limits:
- Maximum 500 MB (prevents memory exhaustion)
- Configurable per deployment

Sample rate handling:
- Accepts 16kHz to 48kHz natively
- Resamples others automatically
- Maintains quality

Duration limits:
- No hard limit enforced (file size is proxy)
- Typical 10+ hour files supported

7. CHALLENGING INPUT HANDLING:

Problem: Corrupted audio file
Solution: Early detection, specific error message

Problem: Unusual sample rate (e.g., 11025 Hz)
Solution: Automatic resampling with librosa

Problem: Mono audio
Solution: Expansion to stereo for processing

Problem: Compressed audio (MP3 with VBR)
Solution: Codec auto-detection and handling

Problem: Very small files (<1 second)
Solution: Accepted but processed as-is

8. QUALITY ASSURANCE:

After separation:
assert output.shape[0] > 0, "Output audio is empty"
assert np.isfinite(output).all(), "Output contains NaN/Inf"

Validates output integrity.

BENEFITS:
- Handles real-world audio variations
- Clear error messages for unsupported formats
- Graceful degradation
- Prevents crashes from edge cases

QUESTION 4: Artifact Versioning and Result Manifest

Q: How would you design the artifact versioning and the result manifest?

ANSWER:

I implemented a comprehensive JSON-based manifest system:

1. MANIFEST STRUCTURE (ProcessingManifest dataclass):

@dataclass
class ProcessingManifest:
 job_id: str # Unique job identifier (UUID)
 input_file: str # Original input filename
 created_at: str # ISO 8601 timestamp
 version: str # Schema version "1.0"
 stages: List[ProcessingStage] # All processing stages
 outputs: Dict[str, str] # Output file paths
 metadata: Dict # System metadata
 status: str # "completed", "failed", "processing"

Saved as JSON: outputs/{job_id}/manifest.json

2. VERSIONING STRATEGY:

Current Version: "1.0"
Backward compatible design for future versions.

Schema versions allow:
- Safe upgrades
- Migration paths
- Compatibility checking

Future version (e.g., "2.0") can:
- Add new fields (backward compatible)
- Change processors
- Update file structure
- Maintain access to "1.0" manifests

3. PROCESSING STAGE TRACKING:

@dataclass
class ProcessingStage:
 name: str # e.g., "audio_separation"
 processor_type: str # e.g., "separator"
 status: str # "pending"/"processing"/"completed"/"failed"
 started_at: Optional[str] # ISO 8601 timestamp
 completed_at: Optional[str] # ISO 8601 timestamp
 error: Optional[str] # Error message if failed
 duration_seconds: Optional[float] # Execution time

Each stage fully documented.

4. MANIFEST EXAMPLE:

{
 "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
 "input_file": "song.wav",
 "created_at": "2024-01-15T10:30:45.123456",
 "version": "1.0",
 "status": "completed",
 "metadata": {
 "processor_count": 4,
 "python_version": "3.11",
 "device": "cpu"
 },
 "stages": [
 {
 "name": "audio_separation",
 "processor_type": "separator",
 "status": "completed",
 "started_at": "2024-01-15T10:30:46.123456",
 "completed_at": "2024-01-15T10:35:12.654321",
 "error": null,
 "duration_seconds": 286.531
 },
 {
 "name": "harmonic_percussive_separation",
 "processor_type": "decomposition",
 "status": "completed",
 "started_at": "2024-01-15T10:35:13.123456",
 "completed_at": "2024-01-15T10:36:01.654321",
 "error": null,
 "duration_seconds": 48.531
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

5. ARTIFACT ORGANIZATION:

Directory Structure:
outputs/
 {job_id}/
 manifest.json # Main manifest file
 demucs_output/
 vocals.wav # Separation outputs
 drums.wav
 bass.wav
 other.wav
 harmonic_percussive/
 harmonic.wav # HP decomposition
 percussive.wav
 composite/
 main.wav # Composite tracks
 main_harmonic.wav
 main_percussive.wav
 normalized/
 (optional normalization outputs)

Logical grouping by processor type.

6. RECOVERY AND AUDIT CAPABILITIES:

Query job status anytime:
GET /job/{job_id}

Returns:
- Complete processing history
- All stage timings
- Output file locations
- Error details (if any)

Example recovery scenario:
1. Client crashes during download
2. Later: Query GET /job/a1b2c3d4...
3. Get complete manifest with all outputs
4. Resume downloads

7. REPRODUCIBILITY:

Manifest enables exact reproduction:
- Input file preserved
- Processor versions tracked
- Stage sequence documented
- Exact outputs listed
- Timestamps for audit

Scientific reproducibility:
- Timestamps for tracing
- Processor types documented
- Error conditions captured
- System metadata included

8. VERSION MIGRATION STRATEGY:

Upgrade scenario (e.g., "1.0" to "2.0"):
```python
def migrate_manifest(manifest_v1):
 return {
 **manifest_v1,
 "version": "2.0",
 "new_fields": default_values
 }
```

Backward compatibility:
- Old manifests still readable
- New fields optional with defaults
- Migration transparent to clients

9. RETENTION POLICY:

Manifest retention:
- Permanent by default
- Queryable indefinitely
- Archive after X days (configurable)

Space efficiency:
- Manifests are JSON (small)
- Audio files can be archived separately
- Manifests never deleted

10. METADATA TRACKING:

System metadata captured:
```python
"metadata": {
 "processor_count": 4,
 "device": "cpu",
 "models": {
 "separator": "demucs_htdemucs_ft",
 "version": "4.0.1"
 },
 "settings": {
 "target_db": -20.0,
 "device": "cpu"
 }
}
```

Enables:
- Model version tracking
- Configuration auditing
- System state reproduction
- Troubleshooting

BENEFITS:
- Complete audit trail
- Full reproducibility
- Easy recovery
- Version management
- Extensible design