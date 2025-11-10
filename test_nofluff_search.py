#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
No Fluff Jobs keresés tesztelése a teljes rendszerrel
"""

import requests
import json
import time
import re

BASE_URL = "http://127.0.0.1:5000"

def test_nofluff_search():
    """No Fluff Jobs keresés a teljes rendszerrel"""
    print("=" * 60)
    print("NO FLUFF JOBS KERESÉS - TELJES RENDSZER")
    print("=" * 60)
    print()
    
    try:
        # App ellenőrzése
        print("[1] Flask app ellenőrzése...")
        status = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if status.status_code == 200:
            print("[OK] App elérhető")
        else:
            print(f"[HIBA] App nem elérhető: {status.status_code}")
            return
        print()
        
        # Keresés indítása
        print("[2] Keresés indítása (IT kategória)...")
        print("    Ez No Fluff Jobs és Profession.hu adatokat is tartalmaz")
        print("    Timeout: 30 perc")
        print()
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/search",
                json={"categories": ["IT"]},
                timeout=1800  # 30 perc timeout
            )
            
            elapsed_time = time.time() - start_time
            
            print(f"[OK] Keresés befejeződött!")
            print(f"    Futási idő: {elapsed_time:.1f} másodperc ({elapsed_time/60:.1f} perc)")
            print()
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                total = data.get("total_jobs", 0)
                
                print(f"[3] Eredmények:")
                print(f"    Összes állás: {total}")
                print()
                
                # Portál bontás
                nofluff_jobs = [j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()]
                profession_jobs = [j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()]
                
                print(f"    No Fluff Jobs: {len(nofluff_jobs)} állás")
                print(f"    Profession.hu: {len(profession_jobs)} állás")
                print()
                
                if nofluff_jobs:
                    print("[4] No Fluff Jobs adatminőség:")
                    
                    has_date_iso = 0
                    has_description = 0
                    has_location = 0
                    has_company = 0
                    
                    for job in nofluff_jobs:
                        pub_date = job.get('publikalva_datum') or job.get('Publikálva_dátum') or ""
                        if pub_date and re.match(r'^\d{4}-\d{2}-\d{2}$', str(pub_date)):
                            has_date_iso += 1
                        
                        desc = job.get('leiras') or job.get('Leírás') or ""
                        if desc and len(desc.strip()) > 10:
                            has_description += 1
                        
                        location = job.get('lokacio') or job.get('Lokáció') or ""
                        if location and location != "N/A":
                            has_location += 1
                        
                        company = job.get('ceg') or job.get('Cég') or ""
                        if company and company != "N/A":
                            has_company += 1
                    
                    nf_count = len(nofluff_jobs)
                    print(f"    Dátum (ISO): {has_date_iso}/{nf_count} ({has_date_iso/nf_count*100:.1f}%)")
                    print(f"    Leírás: {has_description}/{nf_count} ({has_description/nf_count*100:.1f}%)")
                    print(f"    Lokáció: {has_location}/{nf_count} ({has_location/nf_count*100:.1f}%)")
                    print(f"    Cég: {has_company}/{nf_count} ({has_company/nf_count*100:.1f}%)")
                    print()
                    
                    # No Fluff Jobs minták
                    print("[5] No Fluff Jobs példák (első 5):")
                    for i, job in enumerate(nofluff_jobs[:5], 1):
                        title = job.get('pozicio') or job.get('Pozíció') or 'N/A'
                        pub_date = job.get('publikalva_datum') or job.get('Publikálva_dátum') or 'N/A'
                        company = job.get('ceg') or job.get('Cég') or 'N/A'
                        location = job.get('lokacio') or job.get('Lokáció') or 'N/A'
                        
                        date_ok = '[OK]' if re.match(r'^\d{4}-\d{2}-\d{2}$', str(pub_date)) else '[HIBA]'
                        
                        print(f"  {i}. {title[:50]}")
                        print(f"     Cég: {company[:40]}")
                        print(f"     Lokáció: {location[:40]}")
                        print(f"     Dátum: {pub_date} {date_ok}")
                        print()
                else:
                    print("[FIGYELEM] No Fluff Jobs adatok nincsenek!")
                    print("          Lehet, hogy timeout történt vagy hiba lépett fel")
                    print("          Nézd meg a Flask app console outputját")
                
                # Excel export ellenőrzés
                print("[6] Excel export ellenőrzése...")
                export_response = requests.get(f"{BASE_URL}/api/export/excel", timeout=30)
                if export_response.status_code == 200:
                    print("[OK] Excel export sikeres")
                    print(f"    Fájlméret: {len(export_response.content) / 1024:.2f} KB")
                else:
                    print(f"[HIBA] Excel export: {export_response.status_code}")
                    
            else:
                print(f"[HIBA] Keresési hiba: {response.status_code}")
                print(f"Válasz: {response.text[:500]}")
        
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"[HIBA] Timeout - a keresés túl sokáig tart ({elapsed_time/60:.1f} perc)")
            print("       Valószínűleg a No Fluff Jobs scraper lassan fut")
        
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nofluff_search()

