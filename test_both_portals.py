#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keresés indítása mindkét portálon (No Fluff Jobs és Profession.hu)
"""

import requests
import time
import re

BASE_URL = "http://127.0.0.1:5000"

def test_both_portals():
    """Keresés mindkét portálon"""
    print("=" * 60)
    print("KERESÉS - NO FLUFF JOBS ÉS PROFESSION.HU")
    print("=" * 60)
    print()
    
    try:
        # Ellenőrizzük, hogy az app fut-e
        print("[1] App kapcsolat ellenőrzése...")
        try:
            status = requests.get(f"{BASE_URL}/api/status", timeout=5)
            if status.status_code == 200:
                print("[OK] App elérhető")
            else:
                print(f"[HIBA] App nem elérhető: {status.status_code}")
                return
        except:
            print("[HIBA] App nem fut! Indítsd el: python app.py")
            return
        
        print()
        
        # Keresés indítása
        print("[2] Keresés indítása (IT kategória)...")
        print("    Ez eltarthat pár percig...")
        
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={"categories": ["IT"]},
            timeout=1800  # 30 perc timeout (No Fluff Jobs scraper lassabb)
        )
        
        if response.status_code != 200:
            print(f"[HIBA] Keresési hiba: {response.status_code}")
            print(f"Válasz: {response.text[:500]}")
            return
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        print()
        print(f"[OK] Keresés befejezve!")
        print(f"    Összes állás: {len(jobs)}")
        print()
        
        # Portál szerinti bontás
        print("[3] Eredmények portálonként...")
        print()
        
        nofluff_jobs = [j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()]
        profession_jobs = [j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()]
        
        print(f"No Fluff Jobs: {len(nofluff_jobs)} állás")
        print(f"Profession.hu: {len(profession_jobs)} állás")
        print()
        
        # No Fluff Jobs minták
        if nofluff_jobs:
            print("[4] No Fluff Jobs minták (5):")
            date_ok_nf = 0
            date_wrong_nf = 0
            desc_ok_nf = 0
            
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
                
                print(f"  {i}. {job.get('pozicio') or job.get('Pozíció')}")
                print(f"     Dátum: {pub_date} {'[OK]' if is_iso else '[HIBA]'}")
                print(f"     Leírás: {(leiras[:80] if leiras else 'ÜRES')}...")
                print()
            
            print(f"    Dátum formátum: {date_ok_nf} OK, {date_wrong_nf} HIBA")
            print(f"    Leírás: {desc_ok_nf}/5 kitöltött")
            print()
        
        # Profession.hu minták
        if profession_jobs:
            print("[5] Profession.hu minták (5):")
            date_ok_pr = 0
            date_wrong_pr = 0
            desc_ok_pr = 0
            location_remote_pr = 0
            
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
                
                lokacio = job.get('lokacio') or job.get('Lokáció') or ""
                if lokacio and ("táv" in lokacio.lower() or "remote" in lokacio.lower() or "hybrid" in lokacio.lower()):
                    location_remote_pr += 1
                
                print(f"  {i}. {job.get('pozicio') or job.get('Pozíció')}")
                print(f"     Dátum: {pub_date} {'[OK]' if is_iso else '[HIBA]'}")
                print(f"     Lokáció: {lokacio[:60]}")
                print(f"     Leírás: {(leiras[:80] if leiras else 'ÜRES')}...")
                print()
            
            print(f"    Dátum formátum: {date_ok_pr} OK, {date_wrong_pr} HIBA")
            print(f"    Leírás: {desc_ok_pr}/5 kitöltött")
            print(f"    Távmunka/Hybrid info: {location_remote_pr}/5")
            print()
        
        # Excel export ellenőrzése
        print("[6] Excel export ellenőrzése...")
        export_response = requests.get(f"{BASE_URL}/api/export/excel", timeout=30)
        if export_response.status_code == 200:
            print("[OK] Excel export sikeres")
            print(f"    Fájlméret: {len(export_response.content) / 1024:.2f} KB")
            
            # Excel fájl mentése
            import os
            from datetime import datetime
            filename = f"it_allasok_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, 'wb') as f:
                f.write(export_response.content)
            print(f"    Mentve: {filename}")
        else:
            print(f"[HIBA] Excel export: {export_response.status_code}")
        
        print()
        print("=" * 60)
        print("TESZTELÉS BEFEJEZVE")
        print("=" * 60)
        
    except requests.exceptions.Timeout:
        print("[HIBA] Timeout - a keresés túl sokáig tart")
        print("       Ellenőrizd a Flask app console outputját")
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_both_portals()

