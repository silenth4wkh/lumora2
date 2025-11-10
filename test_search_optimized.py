#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teszt az optimalizált /api/search endpoint-ra
"""
import requests
import time

print("=" * 60)
print("OPTIMALIZÁLT SCRAPING TESZT")
print("=" * 60)

print("\n[1] Várakozás Flask indulására...")
time.sleep(5)

print("\n[2] Keresés indítása (Profession + No Fluff API)...")
print("    Várható idő: ~2-3 perc")

start_time = time.time()

try:
    r = requests.post(
        'http://127.0.0.1:5000/api/search',
        json={'categories': ['IT']},
        timeout=600  # 10 perc max
    )
    
    duration = time.time() - start_time
    
    print(f"\n[3] Válasz érkezett: {r.status_code}")
    print(f"    Futási idő: {duration:.1f}s ({duration/60:.1f} perc)")
    
    if r.status_code == 200:
        data = r.json()
        total = data.get('total_jobs', 0)
        jobs = data.get('jobs', [])
        
        # Portálonkénti bontás
        profession_count = sum(1 for j in jobs if 'Profession' in j.get('forras', ''))
        nofluff_count = sum(1 for j in jobs if 'No Fluff' in j.get('forras', ''))
        
        print(f"\n[OK] Sikeres scraping!")
        print(f"    Összes állás: {total}")
        print(f"    - Profession.hu: {profession_count}")
        print(f"    - No Fluff Jobs: {nofluff_count}")
        
        # Első 3 állás minta
        print(f"\n[4] Első 3 állás (minta):")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n  #{i}:")
            print(f"    Pozíció: {job.get('pozicio', '')[:60]}")
            print(f"    Cég: {job.get('ceg', '')}")
            print(f"    Forrás: {job.get('forras', '')}")
            print(f"    Lokáció: {job.get('lokacio', '')}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Scraping befejezve!")
        print("=" * 60)
    else:
        print(f"\n[ERROR] {r.status_code}: {r.text[:500]}")

except requests.exceptions.Timeout:
    duration = time.time() - start_time
    print(f"\n[TIMEOUT] {duration:.1f}s után timeout")
    print("  A scraping túl sokáig tart vagy a Flask app nem válaszol")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

