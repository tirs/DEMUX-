#!/usr/bin/env python3
"""
Quick test to identify the unpacking error
"""
import logging
logging.basicConfig(level=logging.DEBUG)

# Test soundfile.read
print("Testing soundfile.read...")
try:
    import soundfile as sf
    # Create a test audio file path (we won't actually read, just test the function signature)
    help(sf.read)
    print("soundfile.read signature checked")
except Exception as e:
    print(f"Error: {e}")

# Test librosa.load
print("\nTesting librosa.load...")
try:
    import librosa
    help(librosa.load)
    print("librosa.load signature checked")
except Exception as e:
    print(f"Error: {e}")

# Test librosa.effects.hpss
print("\nTesting librosa.effects.hpss...")
try:
    import librosa.effects
    help(librosa.effects.hpss)
    print("librosa.effects.hpss signature checked")
except Exception as e:
    print(f"Error: {e}")

# Test demucs.apply.apply_model
print("\nTesting demucs.apply.apply_model...")
try:
    from demucs.apply import apply_model
    help(apply_model)
    print("demucs.apply.apply_model signature checked")
except Exception as e:
    print(f"Error: {e}")

print("\nDone!")