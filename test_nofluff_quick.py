#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time

time.sleep(3)
print("Testing No Fluff only...")
r = requests.post('http://127.0.0.1:5000/api/search/nofluff-only', json={}, timeout=120)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Jobs: {data.get('total_jobs')}")
    print(f"Method: {data.get('method_used')}")
else:
    print(f"Error: {r.text[:200]}")

