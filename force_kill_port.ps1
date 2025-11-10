# ERŐS Port felszabadítás - minden foglaló folyamat leállítása
# Futtasd: .\force_kill_port.ps1

Write-Host "========================================" -ForegroundColor Red
Write-Host "ERŐS PORT FELSZABADÍTÁS" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

$port = 5001
Write-Host "[1] $port-es port foglaló folyamatok keresése..." -ForegroundColor Yellow

$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if (-not $connections) {
    Write-Host "[OK] Port már szabad!" -ForegroundColor Green
    exit 0
}

$pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
Write-Host "[INFO] $($pids.Count) egyedi folyamat találva" -ForegroundColor Yellow
Write-Host ""

# Folyamatok részletes listája
Write-Host "[2] Folyamatok részletei:" -ForegroundColor Yellow
foreach ($procId in $pids) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  PID $procId : $($proc.ProcessName)" -ForegroundColor Cyan
        if ($proc.Path) {
            Write-Host "         Path: $($proc.Path)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  PID $procId : (Nem található)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[3] Folyamatok leállítása..." -ForegroundColor Yellow

$killed = 0
$failed = 0

foreach ($procId in $pids) {
    try {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Leállítom PID $procId ($($proc.ProcessName))..." -ForegroundColor Gray
            Stop-Process -Id $procId -Force -ErrorAction Stop
            $killed++
        }
    } catch {
        Write-Host "  [HIBA] PID $procId leállítása sikertelen: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Start-Sleep -Seconds 3

# Újraellenőrzés
Write-Host "[4] Újraellenőrzés..." -ForegroundColor Yellow
$stillRunning = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($stillRunning) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "[HIBA] A port még mindig foglalt!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Lehetséges megoldások:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. RESTART a géped (leggyorsabb megoldás)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Használj másik portot (5002, 5003, stb.)" -ForegroundColor Cyan
    Write-Host "   A Flask automatikusan talál szabad portot!" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Manuális folyamat leállítás:" -ForegroundColor Cyan
    Write-Host "   - Nyisd meg a Task Manager-t (Ctrl+Shift+Esc)" -ForegroundColor Gray
    Write-Host "   - Keresd meg a foglaló folyamatot (pl. python.exe)" -ForegroundColor Gray
    Write-Host "   - Jobb klikk → End Task" -ForegroundColor Gray
    Write-Host ""
    
    # Mutatjuk a még futó folyamatokat
    $stillPids = $stillRunning | Select-Object -ExpandProperty OwningProcess -Unique
    Write-Host "Még futó folyamatok:" -ForegroundColor Yellow
    foreach ($procId in $stillPids) {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  PID $procId : $($proc.ProcessName)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "4. Vagy egyszerűen indítsd el a Flask-et," -ForegroundColor Cyan
    Write-Host "   és ő automatikusan talál szabad portot!" -ForegroundColor Gray
    
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Port felszabadítva!" -ForegroundColor Green
    Write-Host "         $killed folyamat leállítva" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Most már elindíthatod a Flask szervert:" -ForegroundColor Yellow
    Write-Host "  python app.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Nyomj Enter-t a kilépéshez..." -ForegroundColor Gray
Read-Host

