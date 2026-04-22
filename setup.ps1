# Healthcare Chatbot - Windows Setup Script
Write-Host "=== Healthcare Chatbot Setup ===" -ForegroundColor Cyan

# --- Backend ---
Write-Host "`n[1/4] Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Python not found. Install from https://python.org" -ForegroundColor Red; exit 1 }

Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\pip install -r backend\requirements.txt

# Copy .env if it doesn't exist
if (-Not (Test-Path "backend\.env")) {
    Write-Host "[INFO] Creating backend\.env from example..." -ForegroundColor Gray
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "[INFO] Edit backend\.env to add your NVIDIA_API_KEY if needed." -ForegroundColor Gray
}

# --- Frontend ---
Write-Host "[3/4] Installing frontend Node.js dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host "`n[4/4] Setup complete! " -ForegroundColor Green
Write-Host "-----------------------------------------------" -ForegroundColor Cyan
Write-Host "To run the app, open TWO terminals in VS Code:" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "    .\.venv\Scripts\activate" -ForegroundColor Gray
Write-Host "    cd backend" -ForegroundColor Gray
Write-Host "    uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "    cd frontend" -ForegroundColor Gray
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Then open: http://localhost:5173" -ForegroundColor Cyan
Write-Host "-----------------------------------------------" -ForegroundColor Cyan
