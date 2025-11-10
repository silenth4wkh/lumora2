#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the No Fluff Jobs API fix locally"""
import sys
sys.path.insert(0, '.')

# Simulate the deduplication logic from app.py
from nofluff_api_scraper import fetch_nofluff_jobs_api

def test_dedup_logic():
    print("="*70)
    print("TESTING NO FLUFF JOBS API DEDUPLICATION FIX")
    print("="*70)
    
    categories = ['artificial-intelligence', 'backend', 'frontend', 'fullstack', 
                 'mobile', 'devops', 'data', 'testing', 'security', 'embedded']
    
    print(f"\n[1] Fetching from API with {len(categories)} categories...")
    api_items = fetch_nofluff_jobs_api(categories=categories)
    raw_count = len(api_items) if api_items else 0
    print(f"    Raw items: {raw_count}")
    
    # Deduplication (same as in app.py)
    if api_items:
        seen_api_links = set()
        deduped_api_items = []
        for item in api_items:
            link = item.get("Link") or item.get("link") or ""
            if link and link not in seen_api_links:
                seen_api_links.add(link)
                deduped_api_items.append(item)
        api_items = deduped_api_items
    
    dedup_count = len(api_items) if api_items else 0
    print(f"    After dedup: {dedup_count} unique jobs")
    print(f"    Removed duplicates: {raw_count - dedup_count}")
    
    # Check threshold
    threshold_ok = dedup_count >= 20
    print(f"\n[2] Threshold check (>= 20): {'PASS' if threshold_ok else 'FAIL'}")
    print(f"    Would use API: {threshold_ok}")
    
    print("\n" + "="*70)
    if threshold_ok:
        print(f"[SUCCESS] API would be used with {dedup_count} jobs")
    else:
        print(f"[FAIL] API would NOT be used (only {dedup_count} jobs)")
    print("="*70)
    
    return dedup_count

if __name__ == '__main__':
    count = test_dedup_logic()
    print(f"\nExpected result: ~795 jobs (was 20 before fix)")

