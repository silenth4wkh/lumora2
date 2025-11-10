#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from nofluff_api_scraper import fetch_nofluff_jobs_api

def main():
    print("="*70)
    print("NO FLUFF JOBS API + DUPLICATION REMOVAL TEST")
    print("="*70)
    
    # Fetch all jobs
    categories = [
        'artificial-intelligence', 'backend', 'frontend', 'fullstack',
        'mobile', 'devops', 'data', 'testing', 'security', 'embedded'
    ]
    
    all_jobs = fetch_nofluff_jobs_api(categories=categories)
    print(f"\n[1] Total jobs from API: {len(all_jobs)}")
    
    # Simulate deduplication (same as in app.py)
    seen_links = set()
    deduplicated = []
    
    for job in all_jobs:
        link = job.get('Link', '')
        if link and link not in seen_links:
            seen_links.add(link)
            deduplicated.append(job)
    
    print(f"[2] After deduplication: {len(deduplicated)}")
    print(f"    Removed duplicates: {len(all_jobs) - len(deduplicated)}")
    
    # Check how many unique links we have
    unique_links = set(job.get('Link', '') for job in all_jobs if job.get('Link'))
    print(f"[3] Unique links: {len(unique_links)}")
    
    return len(deduplicated)

if __name__ == '__main__':
    result = main()
    print("\n" + "="*70)
    if result < 50:
        print(f"[WARN] After dedup: {result} jobs - below 50 threshold")
    else:
        print(f"[OK] After dedup: {result} jobs - should use API")
    print("="*70)

