# Advanced UI Setup Guide

Complete setup instructions for the Professional Audio Pipeline UI with Visualization

## What's New in Advanced UI

- **Waveform Visualization** - See audio amplitude over time
- **Spectrogram Analysis** - Frequency domain visualization 
- **Audio Statistics** - Duration, RMS, Peak, Sample Rate
- **In-browser Audio Player** - Preview tracks without downloading
- **Real-time Progress** - Watch each pipeline stage
- **Report Export** - Markdown and JSON outputs
- **Automated Testing** - Client validation suite

## Quick Start (60 seconds)

### Option 1: Python (Recommended)
```powershell
# Navigate to project
cd C:\Users\simba\Desktop\Modular

# Run the launcher
python START_ADVANCED_UI.py
```

### Option 2: PowerShell
```powershell
# Navigate to project
cd C:\Users\simba\Desktop\Modular

# Run with PowerShell.\START_ADVANCED_UI.ps1
```

### Option 3: Manual
```powershell
# 1. Update dependencies
pip install -r requirements.txt

# 2. Start API (in one terminal)
python api/main.py

# 3. Start Advanced UI (in another terminal)
streamlit run ui/app_advanced.py
```

## System Requirements

- **Python:** 3.8 or newer (you have 3.9.23 )
- **OS:** Windows 10/11
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 5GB free space
- **Internet:** Not required for processing

## Installation Steps

### Step 1: Install/Update Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Key packages:**
- `streamlit>=1.28.0` - Web UI framework
- `librosa>=0.10.0` - Audio analysis
- `matplotlib>=3.7.0` - Plotting and visualization
- `soundfile>=0.12.0` - Audio file I/O
- `requests` - HTTP client
- `numpy` - Numerical computing

### Step 2: Verify Installation

```powershell
python -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"
python -c "import librosa; print(f'Librosa {librosa.__version__}')"
python -c "import matplotlib; print(f'Matplotlib {matplotlib.__version__}')"
```

### Step 3: Start the API

In **Terminal 1**:
```powershell
cd C:\Users\simba\Desktop\Modular
python api/main.py
```

Expected output:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete
```

### Step 4: Start Advanced UI

In **Terminal 2**:
```powershell
cd C:\Users\simba\Desktop\Modular
streamlit run ui/app_advanced.py
```

Expected output:
```
 You can now view your Streamlit app in your browser.

 Local URL: http://localhost:8501
 Network URL: http://[your-ip]:8501
```

### Step 5: Open in Browser

Click the **Local URL** or go to: `http://localhost:8501`

## Using the Advanced UI

### Tab 1: Upload & Process
1. Click **"Choose an audio file"**
2. Select WAV, MP3, FLAC, OGG, or M4A
3. Click **" Process Audio"**
4. Wait for processing to complete

### Tab 2: Results & Visualization
1. **View Progress** - Real-time pipeline stages
2. **Listen to Tracks** - Built-in audio player
3. **View Waveforms** - Visual amplitude representation
4. **View Spectrograms** - Frequency analysis
5. **See Statistics** - Audio properties
6. **Download** - Individual or all tracks

### Tab 3: Help & Info
- Getting started guide
- Troubleshooting tips
- Format compatibility
- About the tools

### Sidebar Options
- Show Waveforms
- Show Spectrograms 
- Show Audio Stats
- Auto-refresh (5s)

## File Structure

```
Modular/
 ui/
 app_advanced.py ← Advanced UI (use this!)
 app.py ← Original UI
 test_client.py ← Testing suite
 README_ADVANCED.md ← UI documentation
 requirements.txt ← UI dependencies
 api/
 main.py ← Audio processing API
 core/
 pipeline.py ← Processing pipeline
 separator.py ← Audio separation
 processors.py ← Audio processors
 START_ADVANCED_UI.py ← Launcher script
 START_ADVANCED_UI.ps1 ← PowerShell launcher
 ADVANCED_UI_SETUP.md ← This file
```

## Testing the Setup

### Automated Test Suite
```powershell
python ui/test_client.py
```

This will:
- Test API connection
- Test UI launch
- Test audio upload
- Test full processing
- Test downloads
- Generate reports

### Manual Test
1. Upload `Audio/1.wav` (included)
2. Process it
3. View visualizations
4. Download track
5. Play in media player

## Troubleshooting

### "API Connection Failed"
**Problem:** UI shows connection error 
**Solution:**
```powershell
# Check if API is running
Invoke-WebRequest http://localhost:8000/config

# If not, start API
python api/main.py
```

### "Module not found" (librosa, streamlit, etc.)
**Problem:** Import error 
**Solution:**
```powershell
pip install librosa streamlit matplotlib soundfile
```

### "Failed to visualize"
**Problem:** Plots don't show 
**Solution:**
- Update matplotlib: `pip install --upgrade matplotlib`
- Disable spectrograms in sidebar
- Reduce file size and try again

### UI not responsive
**Problem:** Streamlit freezes 
**Solution:**
- Disable auto-refresh while processing
- Use smaller audio files
- Restart Streamlit: `streamlit run ui/app_advanced.py --logger.level=error`

### Audio won't play
**Problem:** Player doesn't show 
**Solution:**
- Try different browser (Chrome recommended)
- Download and play locally
- Check audio file format

## Supported Audio Formats

| Format | Extension | Quality | Speed |
|--------|-----------|---------|-------|
| WAV |.wav | | |
| FLAC |.flac | | |
| MP3 |.mp3 | | |
| OGG |.ogg | | |
| M4A |.m4a | | |

**Recommendation:** Use WAV for best results

## What Each Visualization Shows

### Waveform
- Shows amplitude over time
- Identifies loud/quiet sections
- Vertical spikes = transients (drums, percussion)
- Smooth waves = sustained sounds (vocals, strings)

### Spectrogram
- X-axis = Time (seconds)
- Y-axis = Frequency (Hz)
- Color = Energy/Power intensity
- Bright = strong frequency at that time
- Dark = no energy at that frequency

### Statistics
- **Duration** - Total song length
- **Sample Rate** - Audio quality measure
- **Samples** - Total audio points
- **RMS** - Average loudness
- **Peak** - Loudest point
- **Channels** - Mono or stereo

## Output Files

When you download tracks, you get:

1. **Individual Tracks:**
 - `vocals_[job_id].wav`
 - `drums_[job_id].wav`
 - `bass_[job_id].wav`
 - `instruments_[job_id].wav`

2. **All Tracks (ZIP):**
 - `tracks_[job_id].zip` (contains all 4 tracks)

3. **Reports (when exported):**
 - `report_[job_id].md` (Markdown format)
 - `metadata_[job_id].json` (Raw JSON data)

## Performance Tips

### For Faster Processing
1. Use smaller files (< 500MB)
2. Use WAV format
3. Disable spectrograms while processing
4. Close other applications
5. Ensure 4GB+ RAM available

### For Better Visualization
1. Enable both waveforms and spectrograms
2. Use dark theme (set in browser)
3. Maximize browser window
4. Use Chrome or Edge browser
5. Disable browser extensions

## Privacy & Security

- Local processing only
- No data sent to external servers
- Temporary files automatically deleted
- Job IDs are random/unique
- Compatible with enterprise networks

## Additional Resources

### Documentation
- `ui/README_ADVANCED.md` - Full UI documentation
- `API_DOCS.md` - API endpoint documentation
- `ARCHITECTURE.md` - System architecture

### Test Files
- `Audio/1.wav` - Sample mono audio
- `Audio/` - Folder with 100+ test files

### Scripts
- `START_ADVANCED_UI.py` - Python launcher
- `START_ADVANCED_UI.ps1` - PowerShell launcher
- `ui/test_client.py` - Automated testing

## Next Steps

1. **Run the launcher:**
 ```powershell
 python START_ADVANCED_UI.py
 ```

2. **Upload a test file:**
 - Use `Audio/1.wav` or any audio file
 - File will be visible in sidebar

3. **Process:**
 - Click " Process Audio"
 - Watch progress in real-time

4. **Explore visualizations:**
 - View waveforms
 - Analyze spectrograms
 - Check statistics

5. **Download results:**
 - Individual tracks
 - All as ZIP
 - Export reports

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API running (`python api/main.py`)
- [ ] UI running (`streamlit run ui/app_advanced.py`)
- [ ] Browser opens to `http://localhost:8501`
- [ ] Can upload audio file
- [ ] Can start processing
- [ ] Can see progress
- [ ] Can download results
- [ ] Can view visualizations

## Getting Help

If something doesn't work:

1. **Check API logs:**
 ```powershell
 # Look at the terminal running the API
 ```

2. **Check browser console:**
 ```
 F12 → Console tab → Look for errors
 ```

3. **Run test suite:**
 ```powershell
 python ui/test_client.py
 ```

4. **Check requirements:**
 ```powershell
 pip list | grep -E "streamlit|librosa|matplotlib"
 ```

## Contact & Support

For issues or suggestions:
1. Check README_ADVANCED.md in ui/ folder
2. Review test_report.md from test_client.py
3. Check browser console for JavaScript errors

---

**Version:** 2.0 (Advanced Edition) 
**Python:** 3.9.23 
**Last Updated:** 2024

** Ready to start? Run: `python START_ADVANCED_UI.py`**