#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Közvetlen No Fluff Jobs scraper teszt
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_nofluff_direct():
    """Közvetlen No Fluff Jobs teszt"""
    print("=" * 60)
    print("NO FLUFF JOBS DIRECT TESZT")
    print("=" * 60)
    print()
    
    try:
        # No Fluff Jobs teszt endpoint hívása
        print("[1] No Fluff Jobs scraper tesztelése...")
        print("    (Ez eltarthat 1-2 percig...)")
        print()
        
        url = "https://nofluffjobs.com/hu/artificial-intelligence?criteria=category%3Dsys-administrator,business-analyst,architecture,backend,data,ux,devops,erp,embedded,frontend,fullstack,game-dev,mobile,project-manager,security,support,testing,other"
        
        response = requests.post(
            f"{BASE_URL}/api/test/nofluffjobs-pagination",
            json={"url": url},
            timeout=900  # 15 perc timeout (növelve)
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            count = data.get("count", 0)
            
            print(f"[OK] Scraper futott!")
            print(f"    Talált állások: {count}")
            print()
            
            if jobs:
                print(f"[2] Első 5 állás:")
                for i, job in enumerate(jobs[:5], 1):
                    print(f"  {i}. {job.get('Pozíció') or job.get('pozicio') or 'N/A'}")
                    print(f"     Link: {job.get('Link') or job.get('link') or 'N/A'}")
                    print(f"     Publikálva_dátum: {job.get('Publikálva_dátum') or job.get('publikalva_datum') or 'N/A'}")
                    print()
            else:
                print("[FIGYELEM] Nem talált állásokat")
        else:
            print(f"[HIBA] Scraper hiba: {response.status_code}")
            print(f"Válasz: {response.text[:500]}")
        
    except requests.exceptions.Timeout:
        print("[HIBA] Timeout - a scraper túl sokáig tart")
        print("       Valószínűleg a Selenium lassan tölti be az oldalt")
    except Exception as e:
        print(f"[HIBA] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nofluff_direct()

