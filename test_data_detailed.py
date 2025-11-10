#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Részletes adatellenőrzés - No Fluff Jobs és Profession.hu minták
"""

import requests
import re

BASE_URL = "http://127.0.0.1:5000"

def check_data_detailed():
    """Részletes adatellenőrzés"""
    print("=" * 60)
    print("RÉSZLETES ADATELLENŐRZÉS")
    print("=" * 60)
    print()
    
    try:
        # Lekérjük az állásokat
        jobs_response = requests.get(f"{BASE_URL}/api/jobs", timeout=10)
        if jobs_response.status_code != 200:
            print(f"[HIBA] Jobs: {jobs_response.status_code}")
            return
        
        jobs = jobs_response.json()
        print(f"[OK] Összesen {len(jobs)} állás")
        print()
        
        # No Fluff Jobs minták
        nofluff_jobs = [j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()]
        print(f"[NO FLUFF JOBS] {len(nofluff_jobs)} állás")
        
        date_ok_nf = 0
        date_wrong_nf = 0
        desc_ok_nf = 0
        desc_empty_nf = 0
        
        for i, job in enumerate(nofluff_jobs[:5], 1):
            pub_date = job.get('publikalva_datum') or job.get('Publikálva_dátum') or ""
            pub_date_str = str(pub_date)
            is_iso = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date_str))
            
            if is_iso:
                date_ok_nf += 1
            else:
                date_wrong_nf += 1
            
            leiras = job.get('leiras') or job.get('Leírás') or ""
            if leiras and len(leiras.strip()) > 10:
                desc_ok_nf += 1
            else:
                desc_empty_nf += 1
            
            print(f"  {i}. {job.get('pozicio') or job.get('Pozíció')}")
            print(f"     Dátum: {pub_date} {'[OK]' if is_iso else '[HIBA]'}")
            print(f"     Leírás: {(leiras[:100] if leiras else 'ÜRES')}...")
            print()
        
        print(f"[STATS NO FLUFF] Dátum: {date_ok_nf} OK, {date_wrong_nf} HIBA | Leírás: {desc_ok_nf} OK, {desc_empty_nf} ÜRES")
        print()
        
        # Profession.hu minták
        profession_jobs = [j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()]
        print(f"[PROFESSION.HU] {len(profession_jobs)} állás")
        
        date_ok_pr = 0
        date_wrong_pr = 0
        desc_ok_pr = 0
        desc_empty_pr = 0
        location_has_remote_pr = 0
        
        for i, job in enumerate(profession_jobs[:5], 1):
            pub_date = job.get('publikalva_datum') or job.get('Publikálva_dátum') or ""
            pub_date_str = str(pub_date)
            is_iso = bool(re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date_str))
            
            if is_iso:
                date_ok_pr += 1
            else:
                date_wrong_pr += 1
            
            leiras = job.get('leiras') or job.get('Leírás') or ""
            if leiras and len(leiras.strip()) > 10:
                desc_ok_pr += 1
            else:
                desc_empty_pr += 1
            
            lokacio = job.get('lokacio') or job.get('Lokáció') or ""
            if lokacio and ("táv" in lokacio.lower() or "remote" in lokacio.lower() or "hybrid" in lokacio.lower()):
                location_has_remote_pr += 1
            
            print(f"  {i}. {job.get('pozicio') or job.get('Pozíció')}")
            print(f"     Dátum: {pub_date} {'[OK]' if is_iso else '[HIBA]'}")
            print(f"     Lokáció: {lokacio}")
            print(f"     Leírás: {(leiras[:100] if leiras else 'ÜRES')}...")
            print()
        
        print(f"[STATS PROFESSION] Dátum: {date_ok_pr} OK, {date_wrong_pr} HIBA | Leírás: {desc_ok_pr} OK, {desc_empty_pr} ÜRES | Távmunka info: {location_has_remote_pr}")
        print()
        
        # Excel export ellenőrzése
        print("[3] Excel export ellenőrzése...")
        export_response = requests.get(f"{BASE_URL}/api/export/excel", timeout=30)
        if export_response.status_code == 200:
            print("[OK] Excel export sikeres")
            print(f"     Fájlméret: {len(export_response.content)} bytes")
        else:
            print(f"[HIBA] Excel export: {export_response.status_code}")
        
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_detailed()

