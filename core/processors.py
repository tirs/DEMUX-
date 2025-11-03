import logging
from pathlib import Path
from typing import Dict

from core.pipeline import PipelineStage
from core.separator import SeparatorFactory

logger = logging.getLogger(__name__)


class SeparationStage(PipelineStage):
    def __init__(
        self,
        separator_type: str = "demucs",
        separator_model: str = "htdemucs_ft",
        device: str = "cpu"
    ):
        super().__init__(
            name="audio_separation",
            processor_type="separator"
        )
        self.separator_type = separator_type
        self.separator_model = separator_model
        self.device = device
        self.separator = None

    def _get_separator(self):
        if self.separator is None:
            self.separator = SeparatorFactory.create_separator(
                self.separator_type,
                model_name=self.separator_model,
                device=self.device
            )
        return self.separator

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
            self.logger.error(f"File too large: {file_size_mb}MB (max 500MB)")
            return False

        return True

    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        separator = self._get_separator()

        if not separator.validate():
            raise RuntimeError("Separator model not properly initialized")

        self.logger.info(f"Starting separation of {input_path}")
        outputs = separator.separate(input_path, output_dir)

        self.logger.info(f"Separation completed with {len(outputs)} tracks")
        return outputs


class HarmonicPercussiveStage(PipelineStage):
    def __init__(self):
        super().__init__(
            name="harmonic_percussive_separation",
            processor_type="decomposition"
        )

    def validate_input(self, input_path: str) -> bool:
        return Path(input_path).exists()

    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        import librosa
        import soundfile as sf

        try:
            output_path = Path(output_dir) / "harmonic_percussive"
            output_path.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Loading audio from {input_path}")
            result = librosa.load(input_path, sr=None)
            self.logger.info(f"librosa.load returned: {type(result)}, len={len(result) if isinstance(result, tuple) else 'N/A'}")
            y, sr = result
            self.logger.info(f"Audio loaded: shape={getattr(y, 'shape', 'N/A')}, sr={sr}")
            
            harmonic, percussive = librosa.effects.hpss(y)

            harmonic_path = output_path / "harmonic.wav"
            percussive_path = output_path / "percussive.wav"

            sf.write(str(harmonic_path), harmonic, sr)
            sf.write(str(percussive_path), percussive, sr)

            self.logger.info("Harmonic/percussive separation completed")
            return {
                "harmonic": str(harmonic_path),
                "percussive": str(percussive_path)
            }

        except Exception as e:
            self.logger.error(f"Harmonic/percussive separation failed: {str(e)}")
            raise


class CompositeTrackStage(PipelineStage):
    def __init__(self):
        super().__init__(
            name="composite_track_creation",
            processor_type="composition"
        )

    def validate_input(self, input_path: str) -> bool:
        return Path(input_path).exists()

    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        import librosa
        import soundfile as sf

        try:
            output_path = Path(output_dir) / "composite"
            output_path.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Loading audio from {input_path}")
            result = librosa.load(input_path, sr=None)
            self.logger.info(f"librosa.load returned: {type(result)}, len={len(result) if isinstance(result, tuple) else 'N/A'}")
            y, sr = result
            self.logger.info(f"Audio loaded: shape={getattr(y, 'shape', 'N/A')}, sr={sr}")

            main_path = output_path / "main.wav"
            sf.write(str(main_path), y, sr)

            harmonic, percussive = librosa.effects.hpss(y)

            main_harmonic_path = output_path / "main_harmonic.wav"
            main_percussive_path = output_path / "main_percussive.wav"

            sf.write(str(main_harmonic_path), harmonic, sr)
            sf.write(str(main_percussive_path), percussive, sr)

            self.logger.info("Composite track creation completed")
            return {
                "main": str(main_path),
                "main_harmonic": str(main_harmonic_path),
                "main_percussive": str(main_percussive_path)
            }

        except Exception as e:
            self.logger.error(f"Composite track creation failed: {str(e)}")
            raise


class SeparatedTrackHarmonicPercussiveStage(PipelineStage):
    """Apply harmonic/percussive separation to each separated track"""
    def __init__(self):
        super().__init__(
            name="separated_track_harmonic_percussive",
            processor_type="decomposition"
        )

    def validate_input(self, input_path: str) -> bool:
        # This stage works on the demucs_output directory from previous stage
        return Path(input_path).exists()

    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        import librosa
        import soundfile as sf

        try:
            # Look for demucs_output directory
            demucs_output_dir = Path(output_dir) / "demucs_output"
            if not demucs_output_dir.exists():
                self.logger.warning(f"Demucs output directory not found at {demucs_output_dir}")
                return {}

            output_path = Path(output_dir) / "separated_harmonic_percussive"
            output_path.mkdir(parents=True, exist_ok=True)

            outputs = {}
            track_names = ["vocals", "drums", "bass", "other"]
            
            for track_name in track_names:
                track_file = demucs_output_dir / f"{track_name}.wav"
                
                if not track_file.exists():
                    self.logger.warning(f"Track file not found: {track_file}")
                    continue

                try:
                    self.logger.info(f"Processing {track_name} track...")
                    y, sr = librosa.load(str(track_file), sr=None)
                    
                    # Apply harmonic/percussive source separation
                    harmonic, percussive = librosa.effects.hpss(y)
                    
                    # Save harmonic component
                    harmonic_path = output_path / f"{track_name}_harmonic.wav"
                    sf.write(str(harmonic_path), harmonic, sr)
                    outputs[f"{track_name}_harmonic"] = str(harmonic_path)
                    
                    # Save percussive component
                    percussive_path = output_path / f"{track_name}_percussive.wav"
                    sf.write(str(percussive_path), percussive, sr)
                    outputs[f"{track_name}_percussive"] = str(percussive_path)
                    
                    self.logger.info(f"Completed H/P analysis for {track_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {track_name}: {str(e)}")
                    continue

            self.logger.info(f"Separated track H/P analysis completed with {len(outputs)} outputs")
            return outputs

        except Exception as e:
            self.logger.error(f"Separated track harmonic/percussive separation failed: {str(e)}")
            raise


class NormalizationStage(PipelineStage):
    def __init__(self, target_db: float = -20.0):
        super().__init__(
            name="normalization",
            processor_type="audio_processing"
        )
        self.target_db = target_db

    def validate_input(self, input_path: str) -> bool:
        return Path(input_path).exists()

    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        from pathlib import Path
        import soundfile as sf
        import librosa
        import numpy as np

        try:
            output_path = Path(output_dir) / "normalized"
            output_path.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Reading audio from {input_path}")
            # Try soundfile first, fallback to librosa for compatibility
            try:
                result = sf.read(input_path)
                self.logger.info(f"sf.read returned: {type(result)}, len={len(result) if isinstance(result, tuple) else 'N/A'}")
                y, sr = result
            except Exception as e:
                self.logger.warning(f"soundfile.read failed ({str(e)}), trying librosa...")
                y, sr = librosa.load(input_path, sr=None, mono=True)
            
            self.logger.info(f"Audio loaded: shape={getattr(y, 'shape', 'N/A')}, sr={sr}")

            rms = np.sqrt(np.mean(y ** 2))
            if rms > 0:
                target_amplitude = 10 ** (self.target_db / 20.0)
                y_normalized = y * (target_amplitude / rms)
            else:
                y_normalized = y

            normalized_path = output_path / f"normalized_{Path(input_path).name}"
            sf.write(str(normalized_path), y_normalized, sr)

            self.logger.info(f"Normalization completed (target: {self.target_db}dB)")
            return {"normalized": str(normalized_path)}

        except Exception as e:
            self.logger.error(f"Normalization failed: {str(e)}")
            raise