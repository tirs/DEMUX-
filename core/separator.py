import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SeparatorModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = logging.getLogger(f"separator.{model_name}")

    @abstractmethod
    def separate(self, input_path: str, output_dir: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def get_supported_tracks(self) -> List[str]:
        pass


class DemucsModel(SeparatorModel):
    def __init__(self, model_name: str = "htdemucs_ft", device: str = "cpu"):
        super().__init__(model_name)
        self.device = device
        self.demucs = None
        self._load_model()

    def _load_model(self):
        try:
            from demucs.pretrained import get_model
            self.demucs = get_model(self.model_name)
            self.demucs.to(self.device)
            self.logger.info(f"Demucs model {self.model_name} loaded on {self.device}")
        except ImportError:
            raise RuntimeError("Demucs not installed. Install with: pip install demucs")

    def validate(self) -> bool:
        return self.demucs is not None

    def get_supported_tracks(self) -> List[str]:
        return ["drums", "bass", "other", "vocals"]

    def separate(self, input_path: str, output_dir: str) -> Dict[str, str]:
        import torch
        import torchaudio
        import librosa
        from pathlib import Path
        from demucs.apply import apply_model

        try:
            output_path = Path(output_dir) / "demucs_output"
            output_path.mkdir(parents=True, exist_ok=True)

            # Try to load audio file with torchaudio, fallback to librosa
            try:
                wav, sr = torchaudio.load(input_path)
                self.logger.info(f"Loaded audio with torchaudio: {wav.shape}, sr={sr}")
            except Exception as e:
                self.logger.warning(f"torchaudio load failed ({str(e)}), trying librosa...")
                # Fallback: use librosa to load
                y, sr = librosa.load(input_path, sr=44100, mono=False)
                
                # Convert numpy to torch tensor
                wav = torch.from_numpy(y).float()
                
                # Ensure stereo format
                if wav.dim() == 1:
                    wav = wav.unsqueeze(0)
                
                self.logger.info(f"Loaded audio with librosa: {wav.shape}, sr={sr}")
            
            # Ensure audio is in correct format for Demucs
            # Demucs expects (channels, samples) format
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)  # Add channel dimension if mono
            
            # Ensure stereo (Demucs needs at least 2 channels)
            if wav.shape[0] == 1:
                wav = wav.repeat(2, 1)  # Duplicate mono to stereo
            
            # Resample to 44.1 kHz if needed (Demucs standard)
            if sr != 44100:
                self.logger.info(f"Resampling from {sr} to 44100 Hz...")
                resampler = torchaudio.transforms.Resample(sr, 44100)
                wav = resampler(wav)
                sr = 44100
            
            # Add batch dimension if missing (apply_model expects [batch, channels, samples])
            if wav.dim() == 2:
                wav = wav.unsqueeze(0)
            
            wav = wav.to(self.device)
            self.logger.info(f"Audio prepared for separation: shape={wav.shape}, device={self.device}")

            # Run separation using apply_model() from demucs.apply
            with torch.no_grad():
                result = apply_model(self.demucs, wav)
                self.logger.info(f"apply_model returned: {type(result)}, shape: {result.shape}")
                
                # apply_model returns tensor with shape [batch, sources, channels, length]
                # Remove batch dimension since we process one file at a time
                if result.shape[0] == 1:
                    result = result.squeeze(0)  # Now shape is [sources, channels, length]
                
                self.logger.info(f"sources shape after batch squeeze: {result.shape}")
                sources = result

            outputs = {}
            for track_idx, track_name in enumerate(self.get_supported_tracks()):
                track_path = output_path / f"{track_name}.wav"
                # Save on CPU to avoid memory issues
                source = sources[track_idx]  # Get the separated track
                torchaudio.save(str(track_path), source.cpu(), sr)
                outputs[track_name] = str(track_path)
                self.logger.info(f"Saved {track_name} to {track_path}")

            return outputs

        except Exception as e:
            self.logger.error(f"Separation failed: {str(e)}")
            raise


class SeparatorFactory:
    _separators = {
        "demucs": DemucsModel
    }

    @classmethod
    def register_separator(cls, name: str, separator_class: type):
        cls._separators[name] = separator_class
        logger.info(f"Registered separator: {name}")

    @classmethod
    def create_separator(cls, separator_type: str, **kwargs) -> SeparatorModel:
        if separator_type not in cls._separators:
            raise ValueError(
                f"Unknown separator type: {separator_type}. "
                f"Available: {list(cls._separators.keys())}"
            )

        separator_class = cls._separators[separator_type]
        return separator_class(**kwargs)

    @classmethod
    def get_available_separators(cls) -> List[str]:
        return list(cls._separators.keys())