#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
No Fluff Jobs teljes scraper teszt - pagination és adatellenőrzéssel
"""

import requests
import json
import time
import re
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_nofluff_complete():
    """No Fluff Jobs teljes scraper teszt"""
    print("=" * 60)
    print("NO FLUFF JOBS TELJES SCRAPER TESZT")
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
        
        # No Fluff Jobs scraper indítása
        print("[2] No Fluff Jobs scraper indítása...")
        print("    (Ez eltarthat 5-10 percig a pagination miatt...)")
        print("    Timeout: 15 perc")
        print()
        
        url = "https://nofluffjobs.com/hu/artificial-intelligence?criteria=category%3Dsys-administrator,business-analyst,architecture,backend,data,ux,devops,erp,embedded,frontend,fullstack,game-dev,mobile,project-manager,security,support,testing,other"
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/test/nofluffjobs-pagination",
                json={"url": url},
                timeout=900  # 15 perc timeout
            )
            
            elapsed_time = time.time() - start_time
            
            print(f"[OK] Scraper befejeződött!")
            print(f"    Futási idő: {elapsed_time:.1f} másodperc ({elapsed_time/60:.1f} perc)")
            print()
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                count = data.get("count", 0)
                
                print(f"[3] Eredmények:")
                print(f"    Összes állás: {count}")
                print()
                
                if jobs:
                    # Adatminőség ellenőrzés
                    print("[4] Adatminőség ellenőrzés:")
                    
                    has_date = 0
                    has_date_iso = 0
                    has_description = 0
                    has_location = 0
                    has_company = 0
                    
                    unique_links = set()
                    
                    for job in jobs:
                        link = job.get('Link') or job.get('link') or ""
                        if link:
                            unique_links.add(link.split('?')[0])
                        
                        pub_date = job.get('Publikálva_dátum') or job.get('publikalva_datum') or ""
                        if pub_date:
                            has_date += 1
                            # ISO formátum ellenőrzése (YYYY-MM-DD)
                            if re.match(r'^\d{4}-\d{2}-\d{2}$', str(pub_date)):
                                has_date_iso += 1
                        
                        desc = job.get('Leírás') or job.get('leiras') or ""
                        if desc and len(desc.strip()) > 10:
                            has_description += 1
                        
                        location = job.get('Lokáció') or job.get('lokacio') or ""
                        if location and location != "N/A":
                            has_location += 1
                        
                        company = job.get('Cég') or job.get('ceg') or ""
                        if company and company != "N/A":
                            has_company += 1
                    
                    print(f"    Dátum: {has_date}/{count} ({has_date/count*100:.1f}%)\n      ISO formátum: {has_date_iso}/{count} ({has_date_iso/count*100:.1f}%)")
                    print(f"    Leírás: {has_description}/{count} ({has_description/count*100:.1f}%)")
                    print(f"    Lokáció: {has_location}/{count} ({has_location/count*100:.1f}%)")
                    print(f"    Cég: {has_company}/{count} ({has_company/count*100:.1f}%)")
                    print(f"    Egyedi linkek: {len(unique_links)}/{count}")
                    print()
                    
                    # Minták
                    print("[5] Példa állások (első 10):")
                    for i, job in enumerate(jobs[:10], 1):
                        title = job.get('Pozíció') or job.get('pozicio') or 'N/A'
                        pub_date = job.get('Publikálva_dátum') or job.get('publikalva_datum') or 'N/A'
                        company = job.get('Cég') or job.get('ceg') or 'N/A'
                        location = job.get('Lokáció') or job.get('lokacio') or 'N/A'
                        
                        # Dátum formátum jelölés
                        date_ok = '[OK]' if re.match(r'^\d{4}-\d{2}-\d{2}$', str(pub_date)) else '[HIBA]'
                        
                        print(f"  {i}. {title[:50]}")
                        print(f"     Cég: {company[:40]}")
                        print(f"     Lokáció: {location[:40]}")
                        print(f"     Dátum: {pub_date} {date_ok}")
                        print()
                else:
                    print("[FIGYELEM] Nem talált állásokat")
                    print("          Ellenőrizd a Flask app console outputját hibákért")
            else:
                print(f"[HIBA] Scraper hiba: {response.status_code}")
                print(f"Válasz: {response.text[:500]}")
        
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"[HIBA] Timeout - a scraper túl sokáig tart ({elapsed_time/60:.1f} perc)")
            print("       Valószínűleg a Selenium lassan tölti be az oldalt")
            print("       Vagy túl sok oldal van feldolgozni")
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[HIBA] {e}")
            print(f"       Futási idő: {elapsed_time/60:.1f} perc")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nofluff_complete()

