"""Teszt script Flask console output ellenőrzéséhez"""
import requests
import time
import sys

print("="*60)
print("Excel export debug üzenetek ellenőrzése")
print("="*60)
print("\nFIGYELEM: Ellenőrizd a Flask app console output-ját!")
print("A Flask app terminál ablakban látnod kellene a debug üzeneteket!")
print("\nVárt üzenetek:")
print("  - [EXCEL DEBUG START]")
print("  - [EXCEL] 1 portál")
print("  - [EXCEL DEBUG] scraped_jobs első job mezői")
print("  - [CREATE_EXCEL_EXPORT] jobs_data count")
print("  - [SHEET DEBUG] Adatok hozzáadása")
print("  - [SHEET WRITE] Sor 2:")
print("\n" + "="*60)

# Scraper futtatása
print("\n1. No Fluff Jobs scraper futtatása...")
try:
    response = requests.post('http://localhost:5000/api/test/nofluffjobs-no-dedup', json={}, timeout=120)
    data = response.json()
    print(f"   [OK] Status: {response.status_code}")
    print(f"   [OK] Talalt allasok: {data.get('count', 0)}")
    print(f"   [OK] Cache updated: {data.get('cache_updated', False)}")
except Exception as e:
    print(f"   [ERROR] Hiba: {e}")
    sys.exit(1)

time.sleep(2)

# Excel export
print("\n2. Excel export futtatása...")
print("   FIGYELEM: Most nézd meg a Flask app console output-ját!")
print("   Várj 3 másodpercet...")
time.sleep(3)

try:
    response = requests.get('http://localhost:5000/api/export/excel', timeout=30)
    print(f"   [OK] Status: {response.status_code}")
    print(f"   [OK] Excel meret: {len(response.content)} bytes")
    
    # Fájl mentése
    with open('test_excel_logs.xlsx', 'wb') as f:
        f.write(response.content)
    print(f"   [OK] Fajl mentve: test_excel_logs.xlsx")
    
except Exception as e:
    print(f"   [ERROR] Hiba: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("KÉSZ!")
print("\nELLENŐRIZD:")
print("1. A Flask app terminál ablakban láttad-e a debug üzeneteket?")
print("2. Ha NEM láttad, akkor a függvények nem futnak le vagy exception történik")
print("3. Ha LÁTTAD, akkor más a probléma")
print("="*60)

