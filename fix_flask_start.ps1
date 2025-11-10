# Flask szerver indítás javítva - port foglaltság kezelés
# Futtasd: .\fix_flask_start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FLASK SZERVER INDÍTÁS JAVÍTÁS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Port foglaltság ellenőrzése
Write-Host "[1] 5001-es port ellenőrzése..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr :5001

if ($portCheck) {
    Write-Host "[WARN] A 5001-es port foglalt!" -ForegroundColor Yellow
    Write-Host "       Leállítom a foglaló folyamatokat..." -ForegroundColor Yellow
    
    # PID-ek kinyerése
    $pids = $portCheck | ForEach-Object {
        if ($_ -match 'LISTENING\s+(\d+)') {
            $matches[1]
        }
    } | Sort-Object -Unique
    
    foreach ($pid in $pids) {
        Write-Host "       Leállítom PID: $pid" -ForegroundColor Gray
        taskkill /PID $pid /F 2>$null | Out-Null
    }
    
    Start-Sleep -Seconds 2
    Write-Host "[OK] Port felszabadítva" -ForegroundColor Green
} else {
    Write-Host "[OK] Port szabad" -ForegroundColor Green
}

Write-Host ""

# 2. Python folyamatok leállítása (biztonság kedvéért)
Write-Host "[2] Régi Python folyamatok ellenőrzése..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcs) {
    Write-Host "[WARN] $($pythonProcs.Count) Python folyamat fut" -ForegroundColor Yellow
    $answer = Read-Host "       Leállítsam őket? (I/N)"
    if ($answer -eq "I" -or $answer -eq "i") {
        $pythonProcs | Stop-Process -Force
        Write-Host "[OK] Python folyamatok leállítva" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
} else {
    Write-Host "[OK] Nincs futó Python folyamat" -ForegroundColor Green
}

Write-Host ""

# 3. Flask szerver indítása
Write-Host "[3] Flask szerver indítása..." -ForegroundColor Yellow

# Ellenőrizzük hogy az app.py létezik
if (-not (Test-Path "app.py")) {
    Write-Host "[HIBA] app.py nem található!" -ForegroundColor Red
    Write-Host "       Győződj meg róla hogy a helyes könyvtárban vagy." -ForegroundColor Yellow
    exit 1
}

# Flask indítása új ablakban
Write-Host "       Flask szerver indítása új ablakban..." -ForegroundColor Gray
Start-Process python -ArgumentList "app.py" -WindowStyle Normal

Write-Host "[OK] Flask szerver elindítva" -ForegroundColor Green
Write-Host ""

# 4. Várakozás és ellenőrzés
Write-Host "[4] Várakozás a szerver elindulására (8 másodperc)..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "[5] Szerver állapot ellenőrzése..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5001/api/status" -TimeoutSec 5 -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host "[SUCCESS] Flask szerver fut és válaszol!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Szerver elérhető:" -ForegroundColor White
        Write-Host "  http://127.0.0.1:5001" -ForegroundColor Cyan
        Write-Host "  http://localhost:5001" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Szerver válaszol, de status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Szerver még nem válaszol" -ForegroundColor Yellow
    Write-Host "       Lehet hogy még indul..." -ForegroundColor Yellow
    Write-Host "       Próbáld meg 10 másodperc múlva:" -ForegroundColor Yellow
    Write-Host "       http://127.0.0.1:5001/api/status" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Nyomj Enter-t a kilépéshez..." -ForegroundColor Gray
Read-Host

