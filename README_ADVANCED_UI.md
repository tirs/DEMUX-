# Audio Pipeline - Advanced UI Edition

**Professional audio separation with advanced visualization, real-time monitoring, and comprehensive analysis**

---

## Quick Start (Choose One)

### Option A: Automatic Launcher (Recommended)
```powershell
python START_ADVANCED_UI.py
```

### Option B: Manual Start
```powershell
# Terminal 1
python api/main.py

# Terminal 2 (wait for API to start)
streamlit run ui/app_advanced.py
```

### Option C: PowerShell Launcher
```powershell.\START_ADVANCED_UI.ps1
```

Then open: **http://localhost:8501**

---

## Documentation Index

### Getting Started (Pick Your Path)

#### I'm in a hurry
→ Read: **QUICK_START.md** (5 minutes)
- 60-second setup
- 3-step usage
- Quick reference

#### First time setup
→ Read: **ADVANCED_UI_SETUP.md** (15 minutes)
- Complete installation
- System requirements
- Step-by-step guide

#### Want full details
→ Read: **ADVANCED_UI_SUMMARY.md** (20 minutes)
- Complete overview
- All features explained
- Workflow documentation

#### Using the UI
→ Read: **ui/README_ADVANCED.md** (Inside app)
- Full user guide
- Feature documentation
- API information

#### Understanding visualizations
→ Read: **VISUALIZATION_GUIDE.md** (10 minutes)
- Waveform explained
- Spectrogram explained
- Statistics explained
- How to interpret

---

## What You Get

### Audio Separation
- **Input:** WAV, MP3, FLAC, OGG, M4A
- **Output:** 4 separated tracks (Vocals, Drums, Bass, Instruments)
- **Engine:** Demucs (AI-powered)
- **Time:** 5-15 minutes depending on file size

### Real-time Visualization
- **Waveforms** - See amplitude patterns
- **Spectrograms** - See frequency content
- **Statistics** - Duration, RMS, peak, sample rate
- **Audio Player** - Listen inline

### Download & Export
- Individual track download
- All tracks as ZIP
- Analysis reports (Markdown/JSON)
- Complete job metadata

### Quality Testing
- Automated test suite
- Validation reports
- JSON and Markdown output

---

## File Structure

```
Modular/
 START_ADVANCED_UI.py ← Start here (launcher)
 START_ADVANCED_UI.ps1 ← Or this (PowerShell)
 QUICK_START.md ← Quick reference (5 min)
 ADVANCED_UI_SETUP.md ← Setup guide (15 min)
 ADVANCED_UI_SUMMARY.md ← Complete overview (20 min)
 VISUALIZATION_GUIDE.md ← Learn visualizations (10 min)
 README_ADVANCED_UI.md ← This file (index)
 requirements.txt ← Dependencies

 ui/
 app_advanced.py ← Main UI application
 app.py ← Original UI
 test_client.py ← Testing suite
 README_ADVANCED.md ← UI documentation

 api/
 main.py ← API server

 core/
 pipeline.py ← Processing pipeline
 separator.py ← Audio separation
 processors.py ← Processors

 Audio/ ← Test audio files
 downloads/ ← Downloaded tracks go here
 outputs/ ← Processing results
```

---

## Which Document Should I Read?

### "I want to start in 5 minutes"
 **QUICK_START.md**

### "I want to understand the full setup"
 **ADVANCED_UI_SETUP.md**

### "I want complete information"
 **ADVANCED_UI_SUMMARY.md**

### "I want to understand the visualizations"
 **VISUALIZATION_GUIDE.md**

### "I want the full UI guide"
 **ui/README_ADVANCED.md**

---

## 3-Step Usage

### 1⃣ Upload
Upload an audio file (WAV, MP3, FLAC, OGG, M4A)

### 2⃣ Process
Click " Process Audio" and wait for completion

### 3⃣ Download
Download individual tracks or all as ZIP

---

## Testing

```powershell
python ui/test_client.py
```

Generates:
- `test_report.json` - Detailed results
- `test_report.md` - Formatted report

---

## Help

### Quick Troubleshooting
1. **API won't start** → Run in new terminal: `python api/main.py`
2. **UI won't load** → Refresh browser: F5
3. **Slow processing** → Disable spectrograms in sidebar
4. **Download fails** → Check disk space, restart API

### Full Help
See **Help & Info** tab in the UI ← Built-in help inside the application

---

## System Requirements

- **Python:** 3.8+ (you have 3.9.23 )
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 5GB free space
- **Browser:** Chrome, Edge, Firefox

---

## Documentation Guide

| Need | Read | Time |
|------|------|------|
| Quick start | QUICK_START.md | 5 min |
| Setup help | ADVANCED_UI_SETUP.md | 15 min |
| Learn UI | ui/README_ADVANCED.md | 20 min |
| Visualizations | VISUALIZATION_GUIDE.md | 10 min |
| Everything | ADVANCED_UI_SUMMARY.md | 20 min |

---

## Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ran launcher: `python START_ADVANCED_UI.py`
- [ ] Browser opens to http://localhost:8501
- [ ] Can see "Upload & Process" tab
- [ ] Ready to upload audio file!

---

## Let's Go!

### Start Now:
```powershell
python START_ADVANCED_UI.py
```

### Then:
1. Open `http://localhost:8501`
2. Upload an audio file (or use one from `Audio/` folder)
3. Click " Process Audio"
4. Watch the real-time progress
5. Explore the visualizations
6. Download your separated tracks!

---

## Key Features

 **AI-Powered Separation** - Separate vocals, drums, bass, instruments 
 **Advanced Visualization** - Waveforms, spectrograms, statistics 
 **Audio Player** - Listen in-browser 
 **Batch Download** - Get all tracks as ZIP 
 **Real-time Progress** - Watch each stage 
 **Export Reports** - Markdown and JSON 
 **Testing Suite** - Automated validation 
 **Professional UI** - Modern, responsive design 

---

## Output

**Get 4 separated tracks:**
- **Vocals** - Singing/vocal lines
- **Drums** - Percussion and drums
- **Bass** - Bass lines
- **Instruments** - All other instruments

---

## Important Notes

 **Local Processing** - All work done on your machine 
 **No Cloud Upload** - Your files never leave your computer 
 **Automatic Cleanup** - Temporary files deleted automatically 
 **Privacy First** - Complete control of your audio 

---

## Ready?

```powershell
python START_ADVANCED_UI.py
```

**That's it! The UI will launch automatically.**

---

**Version:** 2.0 Advanced Edition 
**Python:** 3.9.23 
**Status:** Ready to Use 

---

## Document Map

```
README_ADVANCED_UI.md (you are here)
 QUICK_START.md (60 seconds)
 ADVANCED_UI_SETUP.md (detailed setup)
 ADVANCED_UI_SUMMARY.md (everything)
 VISUALIZATION_GUIDE.md (learn visualizations)
 ui/README_ADVANCED.md (in-app help)
```

---

** Happy separating! **