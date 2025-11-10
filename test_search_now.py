#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gyors teszt: Keresés indítása Profession.hu és No Fluff Jobs portálokra
"""
import requests
import time
import sys

CANDIDATE_PORTS = list(range(5001, 5011)) + [8080]


def detect_base_url():
    for p in CANDIDATE_PORTS:
        try:
            r = requests.get(f"http://127.0.0.1:{p}/api/status", timeout=1.5)
            if r.status_code == 200:
                return f"http://127.0.0.1:{p}"
        except Exception:
            continue
    return None


def check_server(base_url: str):
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def start_search():
    print("=" * 70)
    print("KERESÉS INDÍTÁSA - PROFESSION.HU + NO FLUFF JOBS")
    print("=" * 70)
    print()

    print("[1] Flask szerver port detektálása...")
    base_url = detect_base_url()
    if not base_url:
        print("[HIBA] Nem találtam futó szervert a 5001-5010/8080 portokon!")
        print("       Indítsd el: python app.py")
        return False
    print(f"[OK] Szerver: {base_url}")
    print()

    # 1. Szerver ellenőrzés
    print("[1] Flask szerver ellenőrzése...")
    if not check_server(base_url):
        print("[HIBA] A szerver nem válaszol a /api/status végponton!")
        return False
    print("[OK] Szerver elérhető")
    print()

    # 2. Keresés indítása
    print("[2] Keresés indítása (IT kategória)...")
    print("    Ez eltarthat 1-5 percig...")
    print()

    start_time = time.time()

    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"categories": ["IT"]},
            timeout=600  # 10 perc timeout
        )

        duration = time.time() - start_time

        print(f"[3] Válasz érkezett ({duration:.1f}s)")
        print()

        if response.status_code != 200:
            print(f"[HIBA] Status code: {response.status_code}")
            print(f"Válasz: {response.text[:500]}")
            return False

        data = response.json()
        jobs = data.get("jobs", [])
        total = data.get("total_jobs", len(jobs))

        # Portálonkénti bontás
        profession_count = sum(1 for j in jobs if 'Profession' in str(j.get('Forrás', j.get('forras', ''))))
        nofluff_count = sum(1 for j in jobs if 'No Fluff' in str(j.get('Forrás', j.get('forras', ''))))

        print("=" * 70)
        print(f"[SUCCESS] Keresés befejezve!")
        print(f"         Összes állás: {total}")
        print(f"         - Profession.hu: {profession_count}")
        print(f"         - No Fluff Jobs: {nofluff_count}")
        print(f"         Futási idő: {duration:.1f} másodperc")
        print("=" * 70)
        print()

        # Első 5 állás minta
        if jobs:
            print("[4] Első 5 állás (minta):")
            print()
            for i, job in enumerate(jobs[:5], 1):
                pozicio = job.get('Pozíció', job.get('pozicio', 'N/A'))
                ceg = job.get('Cég', job.get('ceg', 'N/A'))
                forras = job.get('Forrás', job.get('forras', 'N/A'))
                pub_date = job.get('Publikálva', job.get('publikalva_datum', 'N/A'))

                print(f"  #{i}: {pozicio[:60]}")
                print(f"      Cég: {ceg}")
                print(f"      Forrás: {forras}")
                print(f"      Publikálva: {pub_date}")
                print()

        return True

    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] A keresés {time.time() - start_time:.1f}s után timeoutolt")
        return False
    except Exception as e:
        print(f"[HIBA] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = start_search()
    sys.exit(0 if success else 1)

