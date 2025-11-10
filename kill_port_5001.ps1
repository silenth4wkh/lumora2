# Gyors script az 5001-es port foglaló folyamatok leállításához
# Futtasd: .\kill_port_5001.ps1

Write-Host "5001-es port foglaló folyamatok leállítása..." -ForegroundColor Yellow

# PowerShell módszer
$connections = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue

if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($pid in $pids) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Leállítom PID $pid ($($process.ProcessName))..." -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    
    Start-Sleep -Seconds 2
    
    # Újraellenőrzés
    $stillRunning = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue
    if ($stillRunning) {
        Write-Host "[WARN] Még mindig van folyamat a porton" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Port felszabadítva!" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] Port már szabad" -ForegroundColor Green
}

Write-Host ""
Write-Host "Nyomj Enter-t a kilépéshez..." -ForegroundColor Gray
Read-Host

