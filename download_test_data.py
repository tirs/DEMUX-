#!/usr/bin/env python3
"""
Download and prepare test audio datasets for the audio pipeline.
Supports multiple data sources for flexibility.
"""

import os
import sys
import json
import urllib.request
import zipfile
from pathlib import Path

# Test data sources
TEST_SOURCES = {
    "musdb18_samples": {
        "description": "MUSDB18 sample tracks (4 tracks, ~30 min total)",
        "url": "https://zenodo.org/record/3338373/files/musdb18_wav_drums.zip",
        "requires_auth": False,
        "size_mb": 500
    },
    "freesound_cc": {
        "description": "Creative Commons music from Freesound (manual download)",
        "requires_auth": True,
        "url": "https://freesound.org/search/?q=music&filter_license=Creative%20Commons"
    },
    "youtube_dl": {
        "description": "Download from YouTube (requires youtube-dl)",
        "requires_auth": False,
        "example": "youtube-dl -x --audio-format wav 'https://www.youtube.com/watch?v=...' -o '%(title)s.%(ext)s'"
    },
    "synthetic_test": {
        "description": "Generate synthetic test audio (built-in)",
        "requires_auth": False,
        "size_mb": 50
    }
}

def create_uploads_directory():
    """Ensure uploads directory exists."""
    uploads_dir = Path(__file__).parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print(f"✓ Uploads directory: {uploads_dir}")
    return uploads_dir

def generate_synthetic_test_audio():
    """Generate synthetic test audio using numpy and soundfile."""
    try:
        import numpy as np
        import soundfile as sf
    except ImportError:
        print("⚠ soundfile not installed. Install with: pip install soundfile")
        return False
    
    uploads_dir = create_uploads_directory()
    
    # Generate a 180-second (3 min) test track with multiple frequencies
    sample_rate = 44100
    duration = 180  # 3 minutes
    t = np.linspace(0, duration, sample_rate * duration)
    
    # Create a mix of frequencies (vocals-like, drums-like, bass-like)
    vocals = 0.1 * np.sin(2 * np.pi * 440 * t)  # A4 note
    drums = 0.15 * np.sin(2 * np.pi * 60 * t)   # Bass kick ~60 Hz
    bass = 0.12 * np.sin(2 * np.pi * 100 * t)   # Bass ~100 Hz
    
    # Mix with some variation
    audio = vocals + drums + bass
    audio = audio / np.max(np.abs(audio))  # Normalize
    
    output_file = uploads_dir / "synthetic_test_mix.wav"
    sf.write(output_file, audio, sample_rate)
    print(f"✓ Generated synthetic test audio: {output_file}")
    print(f"  Duration: 3 minutes, Sample rate: {sample_rate} Hz")
    return True

def print_manual_download_options():
    """Print manual download options."""
    print("\n" + "="*70)
    print("MANUAL DOWNLOAD OPTIONS")
    print("="*70)
    
    options = {
        "Option 1: YouTube Music": {
            "steps": [
                "1. Visit: https://www.youtube.com/",
                "2. Search for royalty-free music or your favorite song",
                "3. Install youtube-dl: pip install youtube-dl",
                "4. Download: youtube-dl -x --audio-format wav '<URL>' -o '%(title)s.%(ext)s'",
                "5. Move file to: uploads/ folder"
            ]
        },
        "Option 2: Freesound (Creative Commons)": {
            "steps": [
                "1. Visit: https://freesound.org/search/?q=music",
                "2. Filter by: Creative Commons license",
                "3. Download high-quality WAV/MP3",
                "4. Move file to: uploads/ folder"
            ]
        },
        "Option 3: Internet Archive": {
            "steps": [
                "1. Visit: https://archive.org/details/audio",
                "2. Search for music collections",
                "3. Download audio files",
                "4. Move file to: uploads/ folder"
            ]
        },
        "Option 4: MUSDB18 (Official)": {
            "steps": [
                "1. Visit: https://sigsep.github.io/musdb/",
                "2. Register (free) for access",
                "3. Download MUSDB18 dataset",
                "4. Extract WAV files to: uploads/ folder"
            ]
        }
    }
    
    for option, details in options.items():
        print(f"\n{option}:")
        for step in details["steps"]:
            print(f"  {step}")

def list_uploaded_files():
    """List files in uploads directory."""
    uploads_dir = Path(__file__).parent / "uploads"
    if not uploads_dir.exists():
        print("✗ Uploads directory not found")
        return
    
    files = list(uploads_dir.glob("*.*"))
    if not files:
        print("✗ No audio files in uploads/ directory yet")
        return
    
    print("\n" + "="*70)
    print("AVAILABLE TEST FILES")
    print("="*70)
    
    total_size = 0
    for file in sorted(files):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"  ✓ {file.name:<50} ({size_mb:>6.1f} MB)")
    
    print(f"\n  Total: {total_size:.1f} MB in {len(files)} file(s)")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("AUDIO PIPELINE - TEST DATA SETUP")
    print("="*70)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "synthetic":
            print("\nGenerating synthetic test audio...")
            if generate_synthetic_test_audio():
                print("\n✓ Ready to test! Run:")
                print("  1. Docker: docker-compose up --build")
                print("  2. Or: streamlit run ui/app.py")
                print("  Then upload uploads/synthetic_test_mix.wav")
            return
        
        elif command == "list":
            list_uploaded_files()
            return
    
    # Show available options
    print("\nAvailable test data sources:\n")
    for key, info in TEST_SOURCES.items():
        auth = "🔒 Requires registration" if info.get("requires_auth") else "✓ Free"
        print(f"  • {key}")
        print(f"    {info['description']}")
        print(f"    {auth}\n")
    
    print("="*70)
    print("QUICK START - GENERATE SYNTHETIC TEST AUDIO")
    print("="*70)
    print("\nRun this command to generate a 3-minute test track:")
    print("  python download_test_data.py synthetic\n")
    
    print("="*70)
    print("MANUAL DOWNLOAD OPTIONS")
    print("="*70)
    print_manual_download_options()
    
    print("\n" + "="*70)
    print("CHECK UPLOADED FILES")
    print("="*70)
    print("\nRun this to see available test files:")
    print("  python download_test_data.py list\n")
    
    list_uploaded_files()

if __name__ == "__main__":
    main()