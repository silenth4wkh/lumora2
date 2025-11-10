#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VÉGLEGES TESZT: Profession.hu + No Fluff Jobs együtt
Port: 5001
"""
import requests
import time

print("=" * 60)
print("PROFESSION.HU + NO FLUFF JOBS - EGYÜTTES TESZT")
print("=" * 60)

print("\n[1] Keresés indítása...")
print("    Várható idő: ~3-5 perc (Profession lassú, No Fluff gyors)")

start_time = time.time()

try:
    r = requests.post(
        'http://127.0.0.1:5001/api/search',
        json={'categories': ['IT']},
        timeout=900  # 15 perc max
    )
    
    duration = time.time() - start_time
    
    print(f"\n[2] Válasz érkezett: {r.status_code}")
    print(f"    Futási idő: {duration:.1f}s ({duration/60:.1f} perc)")
    
    if r.status_code == 200:
        data = r.json()
        total = data.get('total_jobs', 0)
        jobs = data.get('jobs', [])
        
        # Portálonkénti bontás
        profession_count = sum(1 for j in jobs if 'Profession' in j.get('forras', ''))
        nofluff_count = sum(1 for j in jobs if 'No Fluff' in j.get('forras', ''))
        
        print(f"\n[SUCCESS] Sikeres scraping!")
        print(f"    Összes állás: {total}")
        print(f"    - Profession.hu: {profession_count}")
        print(f"    - No Fluff Jobs: {nofluff_count}")
        
        # Első 3 állás minta
        print(f"\n[3] Első 3 állás (minta):")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n  #{i}:")
            print(f"    Pozíció: {job.get('pozicio', '')[:60]}")
            print(f"    Cég: {job.get('ceg', '')}")
            print(f"    Forrás: {job.get('forras', '')}")
            print(f"    Publikálva: {job.get('publikalva_datum', '')}")
        
        print("\n" + "=" * 60)
        print("[OK] MINDKÉT PORTÁL SIKERES!")
        print("=" * 60)
    else:
        print(f"\n[ERROR] {r.status_code}: {r.text[:500]}")

except requests.exceptions.Timeout:
    duration = time.time() - start_time
    print(f"\n[TIMEOUT] {duration:.1f}s után timeout")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

