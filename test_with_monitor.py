#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
import threading

def monitor_progress():
    """Monitor progress endpoint"""
    time.sleep(10)  # Várj 10 másodpercet hogy elinduljon
    
    for i in range(60):  # 10 perc monitorozás
        try:
            r = requests.get('http://127.0.0.1:5000/api/search/progress', timeout=5)
            if r.status_code == 200:
                data = r.json()
                print(f"[MONITOR] Progress: {data.get('progress', 0)}% | Status: {data.get('status', 'N/A')}")
        except:
            pass
        time.sleep(10)

print("Starting search with monitoring...")
time.sleep(3)

# Indíts monitor thread-et
monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
monitor_thread.start()

try:
    print("[MAIN] Sending search request...")
    r = requests.post('http://127.0.0.1:5000/api/search', 
                      json={'categories': ['IT']}, 
                      timeout=1200)  # 20 perc
    print(f"\n[MAIN] Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"[MAIN] Total jobs: {data.get('total_jobs')}")
        
        jobs = data.get('jobs', [])
        profession = sum(1 for j in jobs if 'Profession' in j.get('Forrás', ''))
        nofluff = sum(1 for j in jobs if 'No Fluff' in j.get('Forrás', ''))
        
        print(f"[MAIN] Profession.hu: {profession}")
        print(f"[MAIN] No Fluff Jobs: {nofluff}")
    else:
        print(f"[MAIN] Error: {r.text[:200]}")
except Exception as e:
    print(f"[MAIN] Exception: {e}")

