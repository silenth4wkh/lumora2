#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keresés monitorozása - ellenőrzi az állapotot időnként
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def monitor_search():
    """Keresés monitorozása"""
    print("=" * 60)
    print("KERESÉS MONITOROZÁSA")
    print("=" * 60)
    print()
    
    last_count = 0
    same_count_iterations = 0
    
    while True:
        try:
            # Status ellenőrzése
            status = requests.get(f"{BASE_URL}/api/status", timeout=5)
            if status.status_code == 200:
                data = status.json()
                total_jobs = data.get('total_jobs', 0)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                
                if total_jobs > last_count:
                    print(f"[{current_time}] Új állások: {total_jobs} (előző: {last_count})")
                    last_count = total_jobs
                    same_count_iterations = 0
                else:
                    same_count_iterations += 1
                    if same_count_iterations == 1:
                        print(f"[{current_time}] Jelenlegi állások: {total_jobs}")
                    elif same_count_iterations % 3 == 0:
                        print(f"[{current_time}] Várakozás... ({total_jobs} állás)")
                
                # Portál szerinti bontás
                if total_jobs > 0:
                    jobs_response = requests.get(f"{BASE_URL}/api/jobs", timeout=10)
                    if jobs_response.status_code == 200:
                        jobs = jobs_response.json()
                        nofluff = len([j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()])
                        profession = len([j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()])
                        
                        if same_count_iterations == 1:
                            print(f"           No Fluff Jobs: {nofluff}")
                            print(f"           Profession.hu: {profession}")
                            print()
                            
                            # Ha már van No Fluff Jobs adat, akkor valószínűleg befejeződött
                            if nofluff > 0 and same_count_iterations >= 3:
                                print("=" * 60)
                                print("KERESÉS SIKERES!")
                                print("=" * 60)
                                print(f"No Fluff Jobs: {nofluff} állás")
                                print(f"Profession.hu: {profession} állás")
                                print(f"Összesen: {total_jobs} állás")
                                break
                
                # Ha 5 percig nem változik, akkor valószínűleg befejeződött
                if same_count_iterations >= 30:  # 5 perc = 30 * 10 másodperc
                    print()
                    print("=" * 60)
                    print("KERESÉS VALÓSZÍNŰLEG BEFEJEZŐDÖTT")
                    print("=" * 60)
                    print(f"Végső állások száma: {total_jobs}")
                    
                    if total_jobs > 0:
                        jobs_response = requests.get(f"{BASE_URL}/api/jobs", timeout=10)
                        if jobs_response.status_code == 200:
                            jobs = jobs_response.json()
                            nofluff = len([j for j in jobs if "no fluff" in (j.get("forras") or j.get("Forrás") or "").lower()])
                            profession = len([j for j in jobs if "profession" in (j.get("forras") or j.get("Forrás") or "").lower()])
                            
                            print(f"No Fluff Jobs: {nofluff} állás")
                            print(f"Profession.hu: {profession} állás")
                            print()
                            
                            if nofluff == 0:
                                print("[FIGYELEM] No Fluff Jobs adatok nincsenek - timeout lehet")
                            else:
                                print("[OK] Mindkét portál adatai elérhetők")
                    break
            else:
                print(f"[HIBA] Status: {status.status_code}")
                break
                
        except requests.exceptions.ConnectionError:
            print("[FIGYELEM] Flask app nem elérhető")
            print("          Várok 10 másodpercet és újra próbálom...")
            time.sleep(10)
            continue
        except KeyboardInterrupt:
            print("\n[Bevitel] Monitorozás megszakítva")
            break
        except Exception as e:
            print(f"[HIBA] {e}")
            time.sleep(10)
            continue
        
        time.sleep(10)  # 10 másodpercenként ellenőrzés

if __name__ == "__main__":
    monitor_search()

