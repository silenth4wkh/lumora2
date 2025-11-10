#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gyors ellenőrzés az adatokra - megnézi a scraped_jobs változót
"""

import requests
import re

BASE_URL = "http://127.0.0.1:5000"

def quick_check():
    """Gyors ellenőrzés"""
    print("=" * 60)
    print("GYORS ELLENŐRZÉS")
    print("=" * 60)
    print()
    
    try:
        # Ellenőrizzük az app állapotát
        print("[1] App állapot ellenőrzése...")
        status_response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"[OK] App fut: {status_data.get('total_jobs', 0)} állás van az adatbázisban")
        else:
            print(f"[HIBA] Status: {status_response.status_code}")
            return
        
        print()
        
        # Megnézzük az első néhány állást
        print("[2] Első 5 állás ellenőrzése...")
        jobs_response = requests.get(f"{BASE_URL}/api/jobs", timeout=5)
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            print(f"[OK] {len(jobs)} állás elérhető")
            print()
            
            # Ellenőrizzük a dátum formátumokat
            date_ok = 0
            date_wrong = 0
            
            for i, job in enumerate(jobs[:5], 1):
                pub_date = job.get('publikalva_datum') or job.get('Publikálva_dátum') or ""
                pub_date_str = str(pub_date)
                is_iso = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date_str))
                
                if is_iso:
                    date_ok += 1
                else:
                    date_wrong += 1
                
                print(f"  {i}. Pozíció: {job.get('pozicio') or job.get('Pozíció')}")
                print(f"     Forrás: {job.get('forras') or job.get('Forrás')}")
                print(f"     Publikálva_dátum: {pub_date} {'[OK]' if is_iso else '[HIBA]'}")
                print(f"     Leírás: {(job.get('leiras') or job.get('Leírás') or '')[:80]}")
                print()
            
            print(f"[STATS] Dátum formátum: {date_ok} OK, {date_wrong} HIBA")
        else:
            print(f"[HIBA] Jobs: {jobs_response.status_code}")
        
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_check()

