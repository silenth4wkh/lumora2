#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test No Fluff Jobs API only endpoint on Render"""
import os, sys
import requests

BASE = os.environ.get("RENDER_BASE_URL", "https://lumora2.onrender.com").rstrip('/')


def main():
    print("="*70)
    print("TESTING NO FLUFF JOBS ONLY ENDPOINT ON RENDER")
    print("="*70)
    print(f"[TARGET] {BASE}")
    
    # Test health check endpoint if it exists
    print("\n[1] Testing /api/search/nofluff-only...")
    try:
        r = requests.post(f"{BASE}/api/search/nofluff-only", json={}, timeout=300)
        if r.status_code == 200:
            data = r.json()
            jobs = data.get('jobs', [])
            total = data.get('total_jobs', len(jobs))
            print(f"[OK] NoFluff-only search completed")
            print(f"     Total jobs: {total}")
            
            # Check source
            sources = {}
            for job in jobs:
                source = job.get('Forrás', job.get('forras', 'Unknown'))
                sources[source] = sources.get(source, 0) + 1
            print(f"     Sources: {sources}")
            
            if total < 100:
                print(f"\n[WARN] Only {total} jobs - API might not be working")
                print("       Check Render logs for API errors")
            else:
                print(f"\n[SUCCESS] {total} jobs - API is likely working")
        else:
            print(f"[ERROR] Status: {r.status_code}")
            print(r.text[:1000])
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == '__main__':
    main()

