#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

api_url = 'https://nofluffjobs.com/api/posting'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}
params = {'category': 'artificial-intelligence'}

print("Testing API health check...")
try:
    r = requests.get(api_url, headers=headers, params=params, timeout=5)
    print(f"Status code: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    
    if r.status_code == 200:
        data = r.json()
        postings = data.get('postings', [])
        print(f"Postings count: {len(postings)}")
        print(f"Has postings: {'postings' in data}")
        print(f"Postings > 0: {len(postings) > 0}")
    else:
        print(f"[ERROR] Bad status code")
except Exception as e:
    print(f"[ERROR] {e}")

