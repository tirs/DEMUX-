# Advanced UI Visualization Guide

Complete guide to understanding and using all visualization features in the Advanced Audio Pipeline UI.

## Overview

The Advanced UI provides four main visualization types:

1. ** Audio Player** - In-browser playback
2. ** Statistics** - Audio properties
3. ** Waveform** - Amplitude over time
4. ** Spectrogram** - Frequency analysis

---

## Audio Player

### What It Is
Built-in browser audio player for each separated track.

### What You Can Do
- Play/pause audio
- Adjust volume
- ⏱ Seek forward/backward
- See current playback time
- Download directly from player

### Why It's Useful
- **Preview before downloading** - Make sure separation is good
- **Quality check** - Listen for artifacts or issues
- **Quick comparison** - Switch between tracks easily
- **No external player needed** - Everything in browser

### Tips
- Use headphones for better quality assessment
- Listen to quiet sections to catch artifacts
- Compare dry/wet sections for separation quality

---

## Audio Statistics

### What It Shows

#### Duration (seconds)
- **What:** Total song length
- **Example:** "120.50"
- **Why:** Know how long the track is
- **Use case:** Verify file loaded correctly

#### Sample Rate (Hz)
- **What:** Audio quality / sampling frequency
- **Examples:**
 - 16000 Hz = Standard CD quality
 - 44100 Hz = CD quality
 - 48000 Hz = Professional audio
- **Why:** Indicates audio fidelity
- **Interpretation:**
 - Higher = Better quality but larger file
 - Lower = Smaller file but lower quality

#### Total Samples
- **What:** Complete number of audio points
- **Formula:** Duration × Sample Rate
- **Example:** 120.50s × 44100 Hz = 5,316,405 samples
- **Why:** Technical detail for verification

#### RMS (Root Mean Square)
- **What:** Average energy / loudness level
- **Range:** 0.0 to 1.0
- **Examples:**
 - 0.01-0.05 = Very quiet
 - 0.05-0.20 = Moderate level
 - 0.20-0.50 = Loud
 - 0.50+ = Very loud (possible clipping)
- **Why:** Helps identify normalization issues
- **Use case:** Check if separation caused level problems

#### Peak (Amplitude)
- **What:** Loudest point in the audio
- **Range:** 0.0 to 1.0
- **Examples:**
 - 0.1 = Quiet audio
 - 0.5 = Moderate
 - 0.9+ = Very loud (risk of distortion)
 - 1.0 = Clipping/distortion
- **Why:** Prevent audio clipping
- **Use case:** Monitor for distortion after separation

#### Channels
- **What:** Mono (1) or Stereo (2)
- **Examples:**
 - "Mono" = Single channel (combined L+R)
 - "Stereo" = Two channels (left + right)
- **Why:** Know if audio is in mono or stereo
- **Use case:** Understand spatial characteristics

---

## Waveform Visualization

### What It Shows
Visual representation of audio amplitude over time.

```
Amplitude
 
 1 
 
 0 Time
 
 -1 
 
 
```

### Reading the Waveform

#### Vertical Axis (Amplitude)
- **Top (+1)** = Maximum positive peak
- **Middle (0)** = Zero level (silence)
- **Bottom (-1)** = Maximum negative peak

#### Horizontal Axis (Time)
- **Left** = Beginning of track
- **Right** = End of track
- **Each unit** = Time in seconds

#### Visual Patterns

**Drums/Percussion** 
```
 
 Sharp, tall spikes
 Quick attacks
```
- Sharp, vertical spikes
- Sudden peaks and valleys
- Indicate percussive elements

**Vocals** 
```
 
 Smoother waves
 Longer sustains
```
- Smoother, more continuous waves
- Longer sustain periods
- Natural vibrato oscillations

**Bass** 
```
 
 Lower frequency
 Longer wavelengths
```
- Large wavelengths
- Smooth, rolling motion
- Lower frequency content

**Quiet Sections** 
```
 Flat line (or very small)
 Indicates silence or very
 quiet audio
```
- Nearly flat line
- Indicates silence
- Should be near zero

### Using Waveform Analysis

**Quality Check:**
- Consistent amplitude = Good levels
- Smooth curves = Natural audio
- Flat line = Possible error
- Red-lining (hitting ±1.0) = Clipping/distortion

**Separation Quality:**
- Compare waveforms between tracks
- Vocals should be distinct from drums
- Bass should be separate from instruments

**Find Specific Sections:**
- Large spikes = Loud moments
- Quiet sections = Soft passages
- Silence = Gaps or breaks

---

## Spectrogram Visualization

### What It Shows
Frequency content over time (Time-Frequency representation).

```
Frequency (Hz)
 
20k 
 
10k 
 = Quiet (dark blue)
 5k = Medium (green/yellow)
 = Loud (red/bright)
 1k 
 
 100 Time (seconds)
 0s 10s 20s 30s
```

### Understanding the Spectrogram

#### Axes

**Vertical Axis (Frequency)**
- **Top** = High frequencies (treble, sibilance)
- **Middle** = Mid frequencies (vocals, instruments)
- **Bottom** = Low frequencies (bass, drums)

**Horizontal Axis (Time)**
- **Left** = Beginning
- **Right** = End
- **Duration** = Song length

#### Color Intensity

**Blue (Dark):**
- No or very little energy
- Frequency not present at that time
- "Empty" space

**Green/Yellow (Medium):**
- Moderate energy
- Some frequency content
- Background elements

**Red/Orange (Bright):**
- High energy / Loud
- Dominant frequencies
- Main components

### Interpreting Common Patterns

#### Vocal Spectrogram 
```
 High 
 
 
 
 
 
 Low 
```
- Energy concentrated in middle frequencies (200-8000 Hz)
- Presence of formants (vocal resonances)
- Dynamic pattern following lyrics

#### Drums Spectrogram 
```
 High 
 
 
 
 (kick pattern)
 
 Low 
```
- Sharp, distinct bursts
- Kick drums in low frequencies
- Hi-hats in high frequencies
- Clear rhythmic pattern

#### Bass Spectrogram 
```
 High 
 
 
 
 
 (bass notes)
 Low 
```
- Concentrated in low frequencies (20-250 Hz)
- Smooth curves = sustained notes
- Multiple horizontal lines = harmonic series

#### Instrument Spectrogram 
```
 High 
 
 
 
 
 
 Low 
```
- Energy spread across frequencies
- Harmonics visible
- Varying patterns depending on instrument

### Using Spectrogram Analysis

**Frequency Identification:**
- Identify which frequencies are present
- Spot problematic frequencies (hum, noise)
- See harmonic content

**Time Localization:**
- When sounds occur in time
- Duration of individual sounds
- Timing of instrument changes

**Quality Assessment:**
- Clean, defined patterns = Good separation
- Blurry patterns = Poor separation
- Unexpected frequencies = Artifacts

**Separation Quality:**
- Vocals should show distinct patterns
- Drums should have clear transients
- Bass should be low-frequency only
- Instruments should have varied frequencies

---

## Comparing Multiple Visualizations

### Track Comparison Example

For a song with vocals, drums, bass, and instruments:

#### Vocals Track
- Waveform: Smooth, continuous curves
- Stats: RMS ~0.15, Peak ~0.45
- Spectrogram: Energy 200-8000 Hz, dynamic pattern

#### Drums Track
- Waveform: Sharp spikes, rhythmic pulses
- Stats: RMS ~0.20, Peak ~0.70 (loud)
- Spectrogram: Clear kicks + hi-hats, distinct bursts

#### Bass Track
- Waveform: Large, smooth waves
- Stats: RMS ~0.12, Peak ~0.40
- Spectrogram: Low frequencies only, 20-250 Hz

#### Instruments Track
- Waveform: Complex, varied patterns
- Stats: RMS ~0.18, Peak ~0.60
- Spectrogram: Spread across mid/high frequencies

### What Good Separation Looks Like

 **Distinct Patterns**
- Each track has unique visual characteristics
- Minimal overlap in spectrograms
- Clear separation in frequency domains

 **Appropriate Levels**
- RMS values ~0.10-0.20 each
- Peak values below 0.80 (room for headroom)
- No track dominates others

 **Clean Audio**
- No artifacts or noise
- Smooth waveforms (not jagged)
- Logical frequency distribution

 **Poor Separation Signs**
- Similar patterns in all tracks
- Overlapping frequencies
- Very different loudness levels
- Unexpected frequencies in tracks

---

## Tips for Best Results

### Interpretation
1. **Look at multiple visualizations** - Waveform + Spectrogram = Complete picture
2. **Compare across tracks** - Understand relationship between outputs
3. **Check statistics** - Verify levels and properties
4. **Listen carefully** - Audio player is final check

### Quality Assessment
1. **Listen first** - Your ears are the best judge
2. **Check spectrogram** - Confirm visual separation
3. **Review waveforms** - Look for artifacts
4. **Check statistics** - Ensure no clipping

### Common Issues

**Poor Separation:**
- Original audio quality too low
- MP3 compression damaged audio
- Vocals heavily mixed with instruments
- Try different source file

**Clipping/Distortion:**
- Peak amplitude near 1.0
- Use audio with more headroom
- Consider normalizing input

**Unexpected Artifacts:**
- Strange frequencies in spectrogram
- Clicks or pops in waveform
- Usually from input file quality
- Pre-process audio if possible

---

## Quick Reference Guide

| Visualization | Shows | Read | Use For |
|---|---|---|---|
| **Waveform** | Amplitude over time | Vertical = loudness, Horizontal = time | Identify clips, artifacts |
| **Spectrogram** | Frequency over time | Vertical = frequency, Color = energy | Identify frequency content |
| **Statistics** | Audio properties | Numbers | Verify levels, sample rate |
| **Player** | Actual sound | Ears | Final quality check |

---

## Further Reading

- **Audio Basics:** Understanding Waveforms and Spectrograms
- **Signal Processing:** FFT and Time-Frequency Analysis
- **Music Separation:** How Demucs Works
- **Audio Quality:** Digital Audio Standards

---

**Version:** 1.0 
**Last Updated:** 2024 
**For:** Advanced Audio Pipeline UI v2.0