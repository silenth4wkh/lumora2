#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask szerver indítása és azonnali teszt
"""
import subprocess
import time
import requests
import sys

print("=" * 70)
print("FLASK SZERVER INDÍTÁS ÉS TESZT")
print("=" * 70)
print()

# Flask szerver indítása külön folyamatban
print("[1] Flask szerver indítása...")
flask_process = subprocess.Popen(
    [sys.executable, "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print("[OK] Flask folyamat elindítva")
print()

# Várakozás hogy elinduljon
print("[2] Várakozás a szerver elindulására (10s)...")
time.sleep(10)
print()

# Status ellenőrzés
print("[3] Szerver állapot ellenőrzése...")
try:
    response = requests.get("http://127.0.0.1:5001/api/status", timeout=5)
    if response.status_code == 200:
        print("[OK] Szerver elérhető!")
        print()
        
        # Keresés indítása
        print("[4] Keresés indítása...")
        print("    Ez eltarthat 1-3 percig...")
        print()
        
        start_time = time.time()
        search_response = requests.post(
            "http://127.0.0.1:5001/api/search",
            json={"categories": ["IT"]},
            timeout=180  # 3 perc timeout
        )
        
        duration = time.time() - start_time
        
        if search_response.status_code == 200:
            data = search_response.json()
            jobs = data.get("jobs", [])
            total = data.get("total_jobs", len(jobs))
            
            profession_count = sum(1 for j in jobs if 'Profession' in str(j.get('Forrás', j.get('forras', ''))))
            nofluff_count = sum(1 for j in jobs if 'No Fluff' in str(j.get('Forrás', j.get('forras', ''))))
            
            print("=" * 70)
            print(f"[SUCCESS] Keresés befejezve!")
            print(f"         Összes állás: {total}")
            print(f"         - Profession.hu: {profession_count}")
            print(f"         - No Fluff Jobs: {nofluff_count}")
            print(f"         Futási idő: {duration:.1f} másodperc")
            print("=" * 70)
        else:
            print(f"[HIBA] Keresés status: {search_response.status_code}")
            print(f"Válasz: {search_response.text[:500]}")
    else:
        print(f"[HIBA] Status code: {response.status_code}")
except Exception as e:
    print(f"[HIBA] {e}")

finally:
    # Flask folyamat leállítása
    print()
    print("[5] Flask szerver leállítása...")
    flask_process.terminate()
    flask_process.wait(timeout=5)
    print("[OK] Leállítva")

