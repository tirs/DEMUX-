#!/usr/bin/env python3
"""
Test what librosa.load() actually returns
"""
import librosa
from pathlib import Path

# Find a test audio file
audio_files = list(Path("./Audio").glob("*.wav"))[:1]

if audio_files:
    test_file = str(audio_files[0])
    print(f"Testing with: {test_file}\n")
    
    # Test 1: librosa.load with sr=None
    print("Test 1: librosa.load(file, sr=None)")
    result = librosa.load(test_file, sr=None)
    print(f"  Type: {type(result)}")
    print(f"  Is tuple: {isinstance(result, tuple)}")
    if isinstance(result, tuple):
        print(f"  Length: {len(result)}")
        for i, item in enumerate(result):
            print(f"    [{i}] type={type(item).__name__}, shape/value={getattr(item, 'shape', item)}")
    
    # Test 2: librosa.load with sr=44100
    print("\nTest 2: librosa.load(file, sr=44100)")
    result = librosa.load(test_file, sr=44100)
    print(f"  Type: {type(result)}")
    print(f"  Is tuple: {isinstance(result, tuple)}")
    if isinstance(result, tuple):
        print(f"  Length: {len(result)}")
        for i, item in enumerate(result):
            print(f"    [{i}] type={type(item).__name__}, shape/value={getattr(item, 'shape', item)}")
    
    # Test 3: librosa.load with sr=44100, mono=False
    print("\nTest 3: librosa.load(file, sr=44100, mono=False)")
    result = librosa.load(test_file, sr=44100, mono=False)
    print(f"  Type: {type(result)}")
    print(f"  Is tuple: {isinstance(result, tuple)}")
    if isinstance(result, tuple):
        print(f"  Length: {len(result)}")
        for i, item in enumerate(result):
            print(f"    [{i}] type={type(item).__name__}, shape/value={getattr(item, 'shape', item)}")
    
    # Test 4: librosa.load with sr=None, mono=False
    print("\nTest 4: librosa.load(file, sr=None, mono=False)")
    result = librosa.load(test_file, sr=None, mono=False)
    print(f"  Type: {type(result)}")
    print(f"  Is tuple: {isinstance(result, tuple)}")
    if isinstance(result, tuple):
        print(f"  Length: {len(result)}")
        for i, item in enumerate(result):
            print(f"    [{i}] type={type(item).__name__}, shape/value={getattr(item, 'shape', item)}")
    
else:
    print("No audio files found!")