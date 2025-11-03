# Quick Start Script for Advanced Audio Pipeline UI (PowerShell)
# Run this to validate setup and launch the UI

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║        🎵 Audio Pipeline - Advanced UI Launcher 🎵          ║
║                                                              ║
║  Professional audio separation with visualization           ║
╚══════════════════════════════════════════════════════════════╝
"@

Write-Host "`n📍 Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
Write-Host "   ✓ $pythonVersion"

Write-Host "`n📍 Checking dependencies..." -ForegroundColor Cyan
$packages = @('streamlit', 'librosa', 'matplotlib', 'soundfile', 'requests', 'numpy')
$missing = @()

foreach ($package in $packages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "   ✓ $package" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ $package - MISSING" -ForegroundColor Red
        $missing += $package
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n⚠️ Missing packages: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "   Install with: pip install $($missing -join ' ')"
    exit 1
}

Write-Host "`n📍 Checking API connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/config" -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API is running on http://localhost:8000" -ForegroundColor Green
        $apiRunning = $true
    }
}
catch {
    Write-Host "   ⚠️ API is not running" -ForegroundColor Yellow
    Write-Host "   Start API with: python api/main.py" -ForegroundColor Yellow
    $apiRunning = $false
}

Write-Host "`n📍 Checking UI files..." -ForegroundColor Cyan
$files = @("ui/app_advanced.py", "ui/test_client.py", "ui/README_ADVANCED.md")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ $file - NOT FOUND" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n✅ All checks passed!" -ForegroundColor Green

Write-Host @"
📖 NEXT STEPS:
═══════════════════════════════════════════════════════════════

1. ✅ Upload an audio file (WAV, MP3, FLAC, OGG, M4A)

2. 🚀 Click "Process Audio" to start separation

3. 📊 View real-time progress and visualization

4. 💾 Download individual tracks or all as ZIP

5. 📄 Export analysis reports

═══════════════════════════════════════════════════════════════

💡 TIPS:

• To run automated tests:
  python ui/test_client.py

• For more info, see: ui/README_ADVANCED.md

• Default URL: http://localhost:8501

═══════════════════════════════════════════════════════════════
"@

if (-not $apiRunning) {
    Write-Host "`n⚠️ WARNING: API is not running!" -ForegroundColor Yellow
    $continue = Read-Host "`nContinue anyway? (y/n)"
    if ($continue -ne 'y') {
        Write-Host "Please start API first: python api/main.py"
        exit 1
    }
}

Write-Host "`n🚀 Launching Advanced UI..." -ForegroundColor Green
Write-Host "Opening http://localhost:8501 in your browser..."
Write-Host "Press Ctrl+C to stop the UI`n"

Start-Sleep -Seconds 2

python -m streamlit run ui/app_advanced.py --logger.level=error