#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
import requests

BASE = os.environ.get("RENDER_BASE_URL", "https://lumora2.onrender.com").rstrip('/')
TIMEOUT = 900  # 15 minutes


def main() -> int:
    print(f"[TARGET] {BASE}")
    print("[WAIT] Checking service readiness...")
    try:
        r = requests.get(f"{BASE}/api/status", timeout=10)
        if r.status_code != 200:
            print("[ERROR] Service not ready")
            return 1
    except Exception as e:
        print(f"[ERROR] Cannot reach service: {e}")
        return 1

    print('[CALL] POST /api/search {"categories":["IT"]}')
    print("      This may take 5-15 minutes...")
    start = time.time()
    
    try:
        r = requests.post(
            f"{BASE}/api/search",
            json={"categories": ["IT"]},
            timeout=TIMEOUT
        )
        
        duration = time.time() - start
        
        if r.status_code != 200:
            print(f"[ERROR] Status: {r.status_code}")
            print(r.text[:1000])
            return 2
        
        data = r.json()
        jobs = data.get('jobs', [])
        total = data.get('total_jobs', len(jobs))
        profession = sum(1 for j in jobs if 'profession' in str(j.get('Forrás') or j.get('forras') or '').lower())
        nofluff = sum(1 for j in jobs if 'no fluff' in str(j.get('Forrás') or j.get('forras') or '').lower())
        
        print('='*70)
        print('[RESULTS - SYNC FULL SCRAPING]')
        print(f'Total jobs: {total}')
        print(f' - Profession.hu: {profession}')
        print(f' - No Fluff Jobs: {nofluff}')
        print(f'Duration: {duration:.1f}s ({duration/60:.1f} min)')
        print('='*70)
        return 0
        
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Request timed out after {TIMEOUT}s")
        return 3
    except Exception as e:
        print(f"[ERROR] {e}")
        return 4


if __name__ == '__main__':
    sys.exit(main())

