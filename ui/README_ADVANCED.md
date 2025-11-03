# Audio Pipeline - Advanced UI

Professional audio separation tool with real-time visualization, spectral analysis, and comprehensive reporting.

## Features

### Core Features
- **Audio Separation** - Separate vocals, drums, bass, and instruments using Demucs
- **Real-time Visualization** - Waveforms and spectrograms for each separated track
- **Progress Tracking** - Live updates on processing stages
- **Batch Download** - Download individual or all tracks as ZIP
- **Report Generation** - Export analysis reports and metadata

### Advanced Features
- **Waveform Analysis** - Visual representation of audio amplitude
- **Spectrogram Display** - Frequency/time domain visualization
- **Audio Statistics** - Duration, sample rate, RMS, peak values
- **Auto-refresh** - Automatic status updates during processing
- **Professional UI** - Responsive design with customizable display options

## Quick Start

### Prerequisites
- Python 3.8+
- Running Audio API (`api/main.py`)
- Dependencies installed (see below)

### Installation

1. **Install dependencies:**
```bash
pip install streamlit librosa matplotlib soundfile requests numpy
```

2. **Start the API:**
```bash
python api/main.py
```

3. **Launch the Advanced UI:**
```bash
streamlit run ui/app_advanced.py
```

4. **Open in browser:**
 - Default: http://localhost:8501

## Usage Guide

### Step 1: Upload Audio File
1. Click **"Choose an audio file"** in the Upload & Process tab
2. Select a supported audio file (WAV, MP3, FLAC, OGG, M4A)
3. File details will display automatically

### Step 2: Process
1. Click **" Process Audio"** button
2. Wait for upload completion
3. You'll be redirected to Results & Visualization tab

### Step 3: Monitor Progress
- View real-time pipeline status
- Watch each stage (Audio Loading → Separation → Normalization → Post-processing)
- See duration for each stage

### Step 4: Visualize Results
Once processing completes:

#### Waveform Visualization
- Visual representation of audio amplitude over time
- Helps identify quiet/loud sections
- Available for each separated track

#### Spectrogram Analysis
- Frequency content over time
- Color intensity shows energy/power
- Useful for identifying instruments

#### Audio Statistics
- Duration, sample rate, total samples
- RMS (Root Mean Square) energy
- Peak amplitude values
- Channel information

#### Audio Playback
- Built-in player for each track
- Play directly in browser
- Volume control and seeking

### Step 5: Download & Export

#### Individual Tracks
- Click **" Download [Track Name]"**
- Select save location
- Format: `[track_name]_[job_id].wav`

#### All Tracks (ZIP)
- Click **" Download All Tracks (ZIP)"**
- Contains all separated tracks
- Format: `tracks_[job_id].zip`

#### Reports
- **Markdown Report** - Detailed analysis summary
- **JSON Metadata** - Complete job information and settings

## Display Options

Configure visualization from the sidebar:

- **Show Waveforms** - Toggle waveform plots
- **Show Spectrograms** - Toggle spectrogram analysis
- **Show Audio Stats** - Toggle statistics display
- **Auto-refresh** - Enable 5-second automatic status updates

### Performance Tips
- Disable spectrograms for faster rendering
- Use auto-refresh for long-running jobs
- Close unused browser tabs
- Process one file at a time

## Supported Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV |.wav | Recommended (lossless) |
| MP3 |.mp3 | Compressed, widely supported |
| FLAC |.flac | Lossless compression |
| OGG |.ogg | Open format |
| M4A |.m4a | Apple audio format |

## Output Tracks

The separation produces 4 tracks:

1. **Vocals** - Lead and background vocals
2. **Drums** - Drum sounds
3. **Bass** - Low-frequency bass lines
4. **Instruments** - All other instruments (strings, keys, etc.)

## Client Testing

### Automated Testing
Run the client testing suite:

```bash
python ui/test_client.py
```

This will:
- Test API connection
- Test Streamlit UI launch
- Upload test audio file
- Process full pipeline
- Monitor job status
- Test downloads
- Generate test report

### Test Reports
Reports are generated as:
- `test_report.json` - Detailed JSON data
- `test_report.md` - Formatted markdown report

## How Separation Works

1. **Audio Loading** - Load and validate input file
2. **Preprocessing** - Convert to appropriate format
3. **Demucs Separation** - AI model separates audio into 4 tracks
4. **Normalization** - Optimize levels for consistency
5. **Post-processing** - Final audio enhancement
6. **Export** - Save separated tracks

## Understanding Spectrograms

The spectrogram shows:
- **X-axis** - Time (seconds)
- **Y-axis** - Frequency (Hz, logarithmic scale)
- **Color Intensity** - Energy/power at that frequency

Interpreting:
- Bright areas = dominant frequencies
- Dark areas = minimal energy
- Vertical patterns = sustained notes/sounds
- Horizontal patterns = steady-state tones

## Audio Statistics Explained

- **Duration** - Total length in seconds
- **Sample Rate** - Samples per second (Hz)
- **Samples** - Total sample count
- **RMS** - Average energy level (0-1 scale)
- **Peak** - Maximum amplitude value
- **Channels** - Mono or stereo

## Troubleshooting

### API Connection Failed
1. Verify API is running: `python api/main.py`
2. Check API_URL in code: `http://localhost:8000`
3. Verify firewall allows port 8000

### Slow Processing
1. Check file size (should be < 500MB)
2. Verify API system resources
3. Close other applications
4. Disable spectrogram rendering

### Audio Quality Issues
1. Use WAV or FLAC (lossless)
2. Ensure sample rate 16-48kHz
3. Check original file quality
4. Verify mono/stereo compatibility

### Download Failures
1. Check available disk space
2. Verify browser download settings
3. Check API is still running
4. Try single track download first

## File Structure

```
ui/
 app_advanced.py # Advanced UI (with visualization)
 app.py # Original UI
 test_client.py # Client testing suite
 README_ADVANCED.md # This file
 requirements.txt # Dependencies
```

## Security Notes

- Files are processed server-side
- Temporary uploads are cleaned up
- Job IDs are unique identifiers
- No data is stored permanently
- Verify API endpoint is secure (use HTTPS in production)

## API Endpoints Used

- `GET /config` - Get API configuration
- `POST /process` - Upload and process audio
- `GET /job/{job_id}` - Get job status
- `GET /download/{job_id}/{track_name}` - Download single track
- `GET /download/{job_id}/all` - Download all tracks as ZIP

## Dependencies

```
streamlit>=1.28.0
librosa>=0.10.0
matplotlib>=3.7.0
soundfile>=0.12.0
requests>=2.31.0
numpy>=1.24.0
```

## Best Practices

### For Optimal Results
1. Use high-quality source audio
2. Upload WAV or FLAC when possible
3. Monitor processing stages
4. Review spectrograms for quality check
5. Download outputs while job is fresh

### For Client Demos
1. Pre-process audio for best results
2. Have backup test files ready
3. Run test_client.py before demo
4. Test on target system beforehand
5. Have fallback UI ready

## Support

### Common Issues
- See **Help & Info** tab in the UI
- Check **Troubleshooting** section above
- Review API logs
- Check browser console for errors

### Reporting Issues
- Screenshot of error
- Job ID for reference
- Input audio file format
- System specifications

## Version Info

- **UI Version:** 2.0 (Advanced)
- **Based on:** Streamlit 1.28+
- **Audio Engine:** Demucs
- **Analysis Library:** Librosa

## License

Same as main project - see root LICENSE file

---

**Last Updated:** 2024
**Maintained by:** Audio Pipeline Team