# Flask szerver port automatikus megkeresése
# Futtasd: .\check_flask_port.ps1

Write-Host "Flask szerver port keresése..." -ForegroundColor Yellow
Write-Host ""

$found = $false

# Próbáljuk meg a portokat 5001-től 5010-ig
for ($port = 5001; $port -le 5010; $port++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/api/status" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "[FOUND] Flask szerver fut!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Port: $port" -ForegroundColor Cyan
            Write-Host "URL: http://127.0.0.1:$port" -ForegroundColor White
            Write-Host "     http://localhost:$port" -ForegroundColor White
            Write-Host ""
            Write-Host "Megnyitás böngészőben..." -ForegroundColor Yellow
            Start-Process "http://127.0.0.1:$port"
            $found = $true
            break
        }
    } catch {
        # Port nem válaszol, folytatjuk
    }
}

if (-not $found) {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "[HIBA] Flask szerver nem található!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Lehetőségek:" -ForegroundColor Yellow
    Write-Host "1. Indítsd el: python app.py" -ForegroundColor Cyan
    Write-Host "2. Várj 5-10 másodpercet és futtasd újra ezt a scriptet" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "Nyomj Enter-t a kilépéshez..." -ForegroundColor Gray
Read-Host

