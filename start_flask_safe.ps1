# Biztonságos Flask szerver indítás
# Automatikusan felszabadítja a portot ha foglalt
# Futtasd: .\start_flask_safe.ps1

# 1. Port felszabadítása
Write-Host "[1] Port 5001 felszabadítása..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue

if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "[OK] Port felszabadítva" -ForegroundColor Green
} else {
    Write-Host "[OK] Port már szabad" -ForegroundColor Green
}

Write-Host ""

# 2. Flask szerver indítása
Write-Host "[2] Flask szerver indítása..." -ForegroundColor Yellow

# Ellenőrizzük hogy az app.py létezik
if (-not (Test-Path "app.py")) {
    Write-Host "[HIBA] app.py nem található!" -ForegroundColor Red
    exit 1
}

# Flask indítása új ablakban
Start-Process python -ArgumentList "app.py" -WindowStyle Normal

Write-Host "[OK] Flask szerver elindítva" -ForegroundColor Green
Write-Host ""
Write-Host "Várj 5-10 másodpercet, majd próbáld meg:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:5001" -ForegroundColor Cyan
Write-Host ""

