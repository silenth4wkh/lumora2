#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time

print("Waiting for Flask...")
time.sleep(3)

print("\n[INFO] Testing PARALLEL endpoint: /api/search/parallel")
try:
    start = time.time()
    r = requests.post('http://127.0.0.1:5000/api/search/parallel', 
                      json={}, 
                      timeout=600)  # 10 perc timeout
    duration = time.time() - start
    
    print(f"\nStatus: {r.status_code}")
    print(f"Duration: {duration:.1f}s")
    
    if r.status_code == 200:
        data = r.json()
        print(f"Total jobs: {data.get('total_jobs')}")
        print(f"Message: {data.get('message')}")
        
        jobs = data.get('jobs', [])
        profession = sum(1 for j in jobs if 'Profession' in j.get('forras', ''))
        nofluff = sum(1 for j in jobs if 'No Fluff' in j.get('forras', ''))
        
        print(f"\nProfession.hu: {profession}")
        print(f"No Fluff Jobs: {nofluff}")
        print("\n[SUCCESS] Parallel scraping OK!")
    else:
        print(f"Error: {r.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

