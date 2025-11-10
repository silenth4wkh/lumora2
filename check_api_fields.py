#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check what fields are available in API response
"""
import requests
import json

api_url = "https://nofluffjobs.com/api/posting"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

r = requests.get(api_url, headers=headers, params={'category': 'artificial-intelligence'}, timeout=15)
data = r.json()
postings = data.get('postings', [])

if postings:
    first = postings[0]
    
    print("=" * 80)
    print("AVAILABLE FIELDS IN API")
    print("=" * 80)
    print(f"All keys: {list(first.keys())}\n")
    
    # Salary
    print("SALARY field:")
    print(json.dumps(first.get('salary'), indent=2))
    
    # Description/Requirements
    print("\n\nDESCRIPTION-like fields:")
    for key in first.keys():
        if 'desc' in key.lower() or 'req' in key.lower() or 'text' in key.lower():
            print(f"  {key}: {str(first[key])[:200]}")
    
    print("\n\nFull first posting (truncated):")
    print(json.dumps(first, indent=2, ensure_ascii=False)[:2000])

