#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Részletes teszt az új funkciókhoz - megnézi az adatokat részletesen
"""

import requests
import json
import time
import re
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_detailed():
    """Részletes teszt"""
    print("=" * 60)
    print("RÉSZLETES TESZT - ÚJ FUNKCIÓK")
    print("=" * 60)
    print()
    
    # Keresés indítása
    print("[1] Keresés indítása...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"categories": ["IT"]},
            timeout=600
        )
        
        if response.status_code != 200:
            print(f"[HIBA] {response.status_code}: {response.text}")
            return
        
        data = response.json()
        jobs = data.get("jobs", [])
        print(f"[OK] {len(jobs)} állás találva")
        print()
        
        # Részletes analízis
        print("[2] Részletes analízis...")
        print()
        
        # Dátum formátum ellenőrzés
        date_format_ok = 0
        date_format_wrong = 0
        
        # No Fluff Jobs példák
        nofluff_samples = [j for j in jobs if "no fluff" in (j.get("Forrás") or j.get("forras") or "").lower()][:5]
        print(f"No Fluff Jobs példák ({len(nofluff_samples)}):")
        for i, job in enumerate(nofluff_samples, 1):
            pub_date_iso = job.get('Publikálva_dátum') or job.get('publikalva_datum') or ""
            pub_date_str = str(pub_date_iso)
            
            # Dátum formátum ellenőrzése (YYYY-MM-DD formátum)
            is_iso = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date_str))
            if is_iso:
                date_format_ok += 1
            else:
                date_format_wrong += 1
            
            print(f"  {i}. Pozíció: {job.get('Pozíció') or job.get('pozicio')}")
            print(f"     Link: {job.get('Link') or job.get('link')}")
            print(f"     Publikálva (eredeti): {job.get('Publikálva') or job.get('publikalva')}")
            print(f"     Publikálva_dátum: {pub_date_iso} {'[OK] ISO' if is_iso else '[HIBA] NEM ISO'}")
            print(f"     Leírás: {(job.get('Leírás') or job.get('leiras') or '')[:100]}")
            print()
        
        # Profession.hu példák
        profession_samples = [j for j in jobs if "profession" in (j.get("Forrás") or j.get("forras") or "").lower()][:5]
        print(f"Profession.hu példák ({len(profession_samples)}):")
        for i, job in enumerate(profession_samples, 1):
            pub_date_iso = job.get('Publikálva_dátum') or job.get('publikalva_datum') or ""
            pub_date_str = str(pub_date_iso)
            is_iso = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date_str))
            if is_iso:
                date_format_ok += 1
            else:
                date_format_wrong += 1
            
            print(f"  {i}. Pozíció: {job.get('Pozíció') or job.get('pozicio')}")
            print(f"     Link: {job.get('Link') or job.get('link')}")
            print(f"     Lokáció: {job.get('Lokáció') or job.get('lokacio')}")
            print(f"     Publikálva_dátum: {pub_date_iso} {'[OK] ISO' if is_iso else '[HIBA] NEM ISO'}")
            print(f"     Leírás: {(job.get('Leírás') or job.get('leiras') or '')[:100]}")
            print()
        
        print(f"[STATS] Dátum formátum: {date_format_ok} OK, {date_format_wrong} HIBA")
        print()
        
        # Export ellenőrzése
        print("[3] Excel export ellenőrzése...")
        export_response = requests.get(f"{BASE_URL}/api/export/excel", timeout=30)
        if export_response.status_code == 200:
            print("[OK] Excel export elérhető")
        else:
            print(f"[HIBA] Excel export: {export_response.status_code}")
        
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed()

