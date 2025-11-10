#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Direct health check test"""

# Másold be a check_api_health kódját ide és teszteld
import requests

def check_api_health_local():
    api_url = "https://nofluffjobs.com/api/posting"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        params = {'category': 'artificial-intelligence'}
        print(f"[1] Sending request to {api_url}...")
        r = requests.get(api_url, headers=headers, params=params, timeout=5)
        
        print(f"[2] Status code: {r.status_code}")
        if r.status_code != 200:
            print("[3] Status not 200 -> FALSE")
            return False
        
        print("[3] Parsing JSON...")
        try:
            data = r.json()
            has_postings = 'postings' in data
            count = len(data.get('postings', []))
            print(f"[4] Has 'postings': {has_postings}")
            print(f"[5] Postings count: {count}")
            result = has_postings and count > 0
            print(f"[6] Result: {result}")
            return result
        except Exception as json_error:
            print(f"[ERROR] JSON parse: {json_error}")
            return False
    except Exception as e:
        print(f"[ERROR] Request: {e}")
        return False

print("=" * 60)
print("LOCAL HEALTH CHECK TEST")
print("=" * 60)
result = check_api_health_local()
print(f"\nFinal result: {result}")
print("=" * 60)

# Most teszteljük az import-ot
print("\nImporting from module...")
from nofluff_api_scraper import check_api_health
module_result = check_api_health()
print(f"Module result: {module_result}")

