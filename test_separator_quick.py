#!/usr/bin/env python3
"""Quick test of the fixed Demucs separator."""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.separator import DemucsModel

def test_separator():
    """Test the separator with synthetic audio."""
    
    print("\n" + "="*70)
    print("TESTING DEMUCS SEPARATOR FIX")
    print("="*70)
    
    audio_file = Path(__file__).parent / "uploads" / "synthetic_test_mix.wav"
    
    if not audio_file.exists():
        print(f"✗ Audio file not found: {audio_file}")
        return False
    
    print(f"\n📁 Input file: {audio_file}")
    print(f"   Size: {audio_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Create output directory
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n🔧 Initializing Demucs model...")
    try:
        separator = DemucsModel(model_name="htdemucs_ft", device="cpu")
        print("   ✓ Model loaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to load model: {e}")
        return False
    
    print(f"\n⚙️  Running audio separation...")
    print("   (This may take 2-5 minutes on CPU)")
    
    try:
        outputs = separator.separate(str(audio_file), str(output_dir))
        print(f"   ✓ Separation completed!")
        
        print(f"\n📊 Generated tracks:")
        for track_name, track_path in outputs.items():
            track_file = Path(track_path)
            if track_file.exists():
                size_mb = track_file.stat().st_size / (1024*1024)
                print(f"   ✓ {track_name:<12} {track_file.name} ({size_mb:.1f} MB)")
            else:
                print(f"   ✗ {track_name:<12} FILE NOT FOUND")
        
        print(f"\n✅ SEPARATOR TEST PASSED!")
        print(f"   Output directory: {output_dir}/demucs_output/")
        return True
        
    except Exception as e:
        print(f"\n   ✗ Separation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_separator()
    sys.exit(0 if success else 1)