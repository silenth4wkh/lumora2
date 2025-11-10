#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keresés állapotának ellenőrzése
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def check_progress():
    """Progress ellenőrzése"""
    print("=" * 60)
    print("KERESÉS ÁLLAPOT ELLENŐRZÉSE")
    print("=" * 60)
    print()
    
    try:
        # Status ellenőrzése
        print("[1] Jelenlegi állapot...")
        status = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if status.status_code == 200:
            data = status.json()
            total_jobs = data.get('total_jobs', 0)
            print(f"[OK] Jelenlegi állások száma: {total_jobs}")
            
            if total_jobs > 0:
                print()
                print("[2] Adatok lekérése...")
                jobs_response = requests.get(f"{BASE_URL}/api/jobs", timeout=10)
                if jobs_response.status_code == 200:
                    jobs = jobs_response.json()
                    print(f"[OK] {len(jobs)} állás elérhető")
                    
                    # Portál bontás
                    nofluff = [j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()]
                    profession = [j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()]
                    
                    print()
                    print(f"No Fluff Jobs: {len(nofluff)} állás")
                    print(f"Profession.hu: {len(profession)} állás")
                    
                    if len(nofluff) > 0 or len(profession) > 0:
                        print()
                        print("[OK] Keresés sikeres volt!")
                    else:
                        print()
                        print("[INFO] Keresés még futhat a háttérben...")
                else:
                    print(f"[HIBA] Jobs lekérés: {jobs_response.status_code}")
            else:
                print("[INFO] Még nincsenek adatok - a keresés valószínűleg még fut")
        
    except Exception as e:
        print(f"[HIBA] {e}")

if __name__ == "__main__":
    check_progress()

