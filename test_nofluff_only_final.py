#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time

print("Testing No Fluff Jobs ONLY...")
start = time.time()

r = requests.post('http://127.0.0.1:5001/api/search/nofluff-only', json={}, timeout=120)
duration = time.time() - start

print(f"\nStatus: {r.status_code} | Duration: {duration:.1f}s")

if r.status_code == 200:
    data = r.json()
    print(f"Jobs: {data.get('total_jobs')}")
    print(f"Method: {data.get('method_used')}")
    print("\n[SUCCESS] No Fluff Jobs működik!")
else:
    print(f"Error: {r.text[:200]}")

