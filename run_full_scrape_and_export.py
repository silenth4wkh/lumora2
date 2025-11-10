#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
import requests

BASE = os.environ.get("RENDER_BASE_URL", "https://lumora2.onrender.com").rstrip('/')
SEARCH_TIMEOUT = 900  # 15 minutes
EXPORT_TIMEOUT = 120  # 2 minutes


def main() -> int:
    print('='*70)
    print('FULL SCRAPING + EXCEL EXPORT')
    print('='*70)
    print(f"[TARGET] {BASE}")
    
    # 1. Service readiness
    print("\n[1] Checking service readiness...")
    try:
        r = requests.get(f"{BASE}/api/status", timeout=10)
        if r.status_code != 200:
            print("[ERROR] Service not ready")
            return 1
    except Exception as e:
        print(f"[ERROR] Cannot reach service: {e}")
        return 1
    print("[OK] Service ready")
    
    # 2. Full search
    print("\n[2] Running full search (may take 5-15 minutes)...")
    print('    POST /api/search {"categories":["IT"]}')
    start_search = time.time()
    
    try:
        r = requests.post(
            f"{BASE}/api/search",
            json={"categories": ["IT"]},
            timeout=SEARCH_TIMEOUT
        )
        
        search_duration = time.time() - start_search
        
        if r.status_code != 200:
            print(f"[ERROR] Search status: {r.status_code}")
            print(r.text[:1000])
            return 2
        
        data = r.json()
        jobs = data.get('jobs', [])
        total = data.get('total_jobs', len(jobs))
        profession = sum(1 for j in jobs if 'profession' in str(j.get('Forrás') or j.get('forras') or '').lower())
        nofluff = sum(1 for j in jobs if 'no fluff' in str(j.get('Forrás') or j.get('forras') or '').lower())
        
        print(f"[OK] Search completed in {search_duration:.1f}s ({search_duration/60:.1f} min)")
        print(f"     Total jobs: {total}")
        print(f"     - Profession.hu: {profession}")
        print(f"     - No Fluff Jobs: {nofluff}")
        
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Search timed out after {SEARCH_TIMEOUT}s")
        return 3
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return 4
    
    # 3. Excel export
    print("\n[3] Exporting to Excel...")
    print('    GET /api/export/excel')
    start_export = time.time()
    
    try:
        r = requests.get(f"{BASE}/api/export/excel", timeout=EXPORT_TIMEOUT, stream=True)
        
        if r.status_code != 200:
            print(f"[ERROR] Export status: {r.status_code}")
            print(r.text[:1000])
            return 5
        
        # Save Excel file
        filename = f"it_allasok_render_{int(time.time())}.xlsx"
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        export_duration = time.time() - start_export
        file_size = os.path.getsize(filename)
        
        print(f"[OK] Excel exported in {export_duration:.1f}s")
        print(f"     File: {filename}")
        print(f"     Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        print('\n' + '='*70)
        print('[SUCCESS] Full scraping + Excel export completed!')
        print('='*70)
        return 0
        
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Export timed out after {EXPORT_TIMEOUT}s")
        return 6
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        return 7


if __name__ == '__main__':
    sys.exit(main())

