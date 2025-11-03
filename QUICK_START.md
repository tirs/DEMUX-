# Quick Start - Advanced Audio Pipeline UI

**Total setup time: 5 minutes**

---

## 60-Second Setup

### Step 1: Install Dependencies (2 min)
```powershell
pip install -r requirements.txt
```

### Step 2: Start API (Terminal 1)
```powershell
python api/main.py
```
 Look for: `Application startup complete`

### Step 3: Start Advanced UI (Terminal 2)
```powershell
python START_ADVANCED_UI.py
```
or
```powershell
streamlit run ui/app_advanced.py
```

### Step 4: Open Browser
Click → `http://localhost:8501` or Ctrl+Click the URL shown

---

## Using the UI (3 Steps)

### 1⃣ Upload Audio
- Tab: **" Upload & Process"**
- Click: **"Choose an audio file"**
- Select: WAV, MP3, FLAC, OGG, or M4A
- File size: < 500MB recommended

### 2⃣ Process
- Click: **" Process Audio"**
- Wait for: Processing to complete
- Time: Usually 5-10 minutes depending on file size

### 3⃣ Download & View
- Tab: **" Results & Visualization"**
- View: Waveforms, spectrograms, stats
- Download: Individual tracks or ZIP
- Export: Report (Markdown/JSON)

---

## Output Files

You'll get **4 separated tracks:**

| Track | Contains | Use Case |
|-------|----------|----------|
| **vocals.wav** | Singing/vocal lines | Karaoke, acapella |
| **drums.wav** | Drums & percussion | Rhythm, drum loops |
| **bass.wav** | Bass lines | Bass remixes, grooves |
| **instruments.wav** | Keys, strings, guitars | Instrumental, backing |

---

## Configuration (Sidebar)

### Display Options
- **Show Waveforms** - See amplitude over time
- **Show Spectrograms** - See frequency analysis
- **Show Audio Stats** - See audio properties
- **Auto-refresh** - Auto-update every 5s

### Tips
- Disable spectrograms for **faster rendering**
- Use auto-refresh for **large files**
- Close other apps for **better performance**

---

## Quick Tips

| Problem | Solution |
|---------|----------|
| API Connection Failed | Run `python api/main.py` in separate terminal |
| Slow processing | Use file < 300MB, disable spectrograms |
| Audio won't play | Try Chrome/Edge browser, refresh page |
| Poor visualization | Check file size, verify audio format |
| Can't download | Check disk space, verify API still running |

---

## Understanding Visualizations

### Waveform
- **What:** Audio amplitude over time
- **Read:** Vertical = loud/quiet, Horizontal = time
- **Use:** Find clicks, artifacts, quiet sections

### Spectrogram 
- **What:** Frequency content over time
- **Read:** Vertical = frequency, Color = energy
- **Use:** Identify instruments, check separation

### Statistics
- **What:** Audio properties (duration, sample rate, levels)
- **Read:** Numbers showing audio characteristics
- **Use:** Verify no clipping, check loudness

---

## File Locations

```
C:\Users\simba\Desktop\Modular\
 ui/
 app_advanced.py ← Advanced UI (use this!)
 test_client.py ← Testing
 README_ADVANCED.md ← Full docs
 api/
 main.py ← API server
 core/
 *.py ← Processing
 Audio/ ← Test files
 downloads/ ← Downloaded tracks
 START_ADVANCED_UI.py ← Launcher
```

---

## Troubleshooting

### "API Connection Failed"
1. Open new terminal
2. Run: `python api/main.py`
3. Wait for "Application startup complete"
4. Refresh UI (F5)

### "Module Not Found"
1. Run: `pip install -r requirements.txt`
2. Restart both terminals
3. Try again

### "Processing hangs"
1. Check Task Manager (Ctrl+Shift+Esc)
2. Verify RAM usage < 80%
3. Restart API server

### "Download fails"
1. Check disk space
2. Try downloading single track first
3. Verify API still running

---

## Full Documentation

For complete guides see:
- `ui/README_ADVANCED.md` - Full UI documentation
- `ADVANCED_UI_SETUP.md` - Detailed setup
- `VISUALIZATION_GUIDE.md` - Visualization explained
- `API_DOCS.md` - API endpoints

---

## Testing

Run automated tests:
```powershell
python ui/test_client.py
```

Generates:
- `test_report.json` - Detailed results
- `test_report.md` - Formatted report

---

## Ready?

1. Python 3.8+ installed? (You have 3.9.23 )
2. Dependencies installed? (`pip install -r requirements.txt`)
3. Two terminals ready?

**Then run:**
```powershell
python START_ADVANCED_UI.py
```

**Or manually:**
```powershell
# Terminal 1
python api/main.py

# Terminal 2
streamlit run ui/app_advanced.py
```

---

## That's it!

Go to `http://localhost:8501` and upload an audio file!

**Questions?** See the **Help & Info** tab in the UI.

---

**Version:** 2.0 Advanced Edition 
**Python:** 3.9.23 
**Setup Time:** ~5 minutes 
**Processing Time:** ~5-15 minutes per file