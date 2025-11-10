# Flask szerver indítása - AUTOMATIKUS PORT KERESÉSSEL
# Ez MINDIG működik, mert automatikusan talál szabad portot!
# Futtasd: .\start_flask_anyway.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FLASK SZERVER INDÍTÁS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ellenőrizzük hogy az app.py létezik
if (-not (Test-Path "app.py")) {
    Write-Host "[HIBA] app.py nem található!" -ForegroundColor Red
    Write-Host "       Győződj meg róla hogy a helyes könyvtárban vagy." -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Flask szerver indítása..." -ForegroundColor Yellow
Write-Host "       (Automatikusan talál szabad portot ha az 5001 foglalt)" -ForegroundColor Gray
Write-Host ""

# Flask indítása új ablakban
Start-Process python -ArgumentList "app.py" -WindowStyle Normal

Write-Host "[OK] Flask szerver elindítva új ablakban" -ForegroundColor Green
Write-Host ""
Write-Host "Várj 5-10 másodpercet, majd:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Nézd meg az ablakot ahol a Flask fut" -ForegroundColor Cyan
Write-Host "   Ott látod: 'Running on http://127.0.0.1:XXXX'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Vagy próbáld meg ezeket a portokat sorban:" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:5001" -ForegroundColor White
Write-Host "   http://127.0.0.1:5002" -ForegroundColor White
Write-Host "   http://127.0.0.1:5003" -ForegroundColor White
Write-Host ""
Write-Host "3. Vagy automatikus port ellenőrzés:" -ForegroundColor Cyan
Write-Host "   .\check_flask_port.ps1" -ForegroundColor White
Write-Host ""

