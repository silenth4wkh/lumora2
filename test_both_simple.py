#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time

print("Waiting for Flask...")
time.sleep(3)

print("\nStarting search...")
try:
    r = requests.post('http://127.0.0.1:5000/api/search', 
                      json={'categories': ['IT']}, 
                      timeout=300)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"Total jobs: {data.get('total_jobs')}")
        print(f"Message: {data.get('message')}")
        
        jobs = data.get('jobs', [])
        profession = sum(1 for j in jobs if 'Profession' in j.get('Forrás', ''))
        nofluff = sum(1 for j in jobs if 'No Fluff' in j.get('Forrás', ''))
        
        print(f"\nProfession.hu: {profession}")
        print(f"No Fluff Jobs: {nofluff}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

