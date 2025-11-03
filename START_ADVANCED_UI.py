#!/usr/bin/env python
"""
Quick Start Script for Advanced Audio Pipeline UI
Run this to validate setup and launch the UI
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    print("""
========================================================
         Audio Pipeline - Advanced UI Launcher
                                                              
  Professional audio separation with visualization
========================================================
    """)

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version
    print(f"    Python {version}")
    if sys.version_info < (3, 8):
        print("    Python 3.8+ required!")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")

    required = [
        'streamlit',
        'librosa',
        'matplotlib',
        'soundfile',
        'requests',
        'numpy',
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"    [OK] {package}")
        except ImportError:
            print(f"    [MISSING] {package}")
            missing.append(package)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False

    return True

def check_api():
    """Check if API is running"""
    print("\nChecking API connection...")
    try:
        import requests
        response = requests.get("http://localhost:8000/config", timeout=3)
        if response.status_code == 200:
            print("    [OK] API is running on http://localhost:8000")
            return True
    except:
        pass

    print("    [WARNING] API is not running")
    print("   Start API with: python api/main.py")
    return False

def check_ui_files():
    """Check if UI files exist"""
    print("\nChecking UI files...")
    files = [
        "ui/app_advanced.py",
        "ui/test_client.py",
        "ui/README_ADVANCED.md"
    ]

    for file in files:
        if Path(file).exists():
            print(f"    [OK] {file}")
        else:
            print(f"    [MISSING] {file}")
            return False

    return True

def launch_ui():
    """Launch Streamlit UI"""
    print("\n" + "="*60)
    print("Launching Advanced UI...")
    print("="*60)
    print("\nOpening http://localhost:8501 in your browser")
    print("  (If not opened automatically, go to that URL)")
    print("\nPress Ctrl+C to stop the UI\n")

    time.sleep(2)

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "ui/app_advanced.py", "--logger.level=error"],
            cwd=Path(__file__).parent
        )
    except KeyboardInterrupt:
        print("\n\nUI closed")
        sys.exit(0)

def show_help():
    """Show help information"""
    print("""
NEXT STEPS:
===================================================================

1. Upload an audio file (WAV, MP3, FLAC, OGG, M4A)

2. Click "Process Audio" to start separation

3. View real-time progress and visualization

4. Download individual tracks or all as ZIP

5. Export analysis reports

===================================================================

TIPS:

- If you see "API Connection Failed": Start the API first
  python api/main.py

- To run automated tests:
  python ui/test_client.py

- For more info, see: ui/README_ADVANCED.md

===================================================================
    """)

def main():
    print_banner()

    # Check requirements
    checks_passed = True

    if not check_python_version():
        checks_passed = False

    if not check_dependencies():
        checks_passed = False

    if not check_ui_files():
        checks_passed = False

    api_running = check_api()

    if not checks_passed:
        print("\nSetup incomplete. Please resolve issues above.")
        sys.exit(1)

    if not api_running:
        print("\nWARNING: API is not running!")
        print("   The UI will show 'API Connection Failed'")
        response = input("\n   Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("   Please start API first: python api/main.py")
            sys.exit(1)

    print("\nAll checks passed!")
    show_help()

    input("\nPress Enter to launch the UI...")
    launch_ui()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)