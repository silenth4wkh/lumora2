#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from nofluff_api_scraper import fetch_nofluff_jobs_api, check_api_health

def main():
    print("="*70)
    print("NO FLUFF JOBS API DIRECT TEST")
    print("="*70)
    
    # Health check
    print("\n[1] API Health Check...")
    health_ok = check_api_health()
    print(f"    Health check: {'OK' if health_ok else 'FAILED'}")
    
    # Full API fetch with all categories
    print("\n[2] Fetching all categories from API...")
    categories = [
        'artificial-intelligence', 'backend', 'frontend', 'fullstack',
        'mobile', 'devops', 'data', 'testing', 'security', 'embedded'
    ]
    
    all_jobs = fetch_nofluff_jobs_api(categories=categories)
    
    print("\n" + "="*70)
    print(f"TOTAL JOBS FROM API: {len(all_jobs)}")
    print("="*70)
    
    if all_jobs:
        print(f"\nFirst 5 jobs:")
        for i, job in enumerate(all_jobs[:5], 1):
            print(f"\n{i}. {job.get('Pozíció', 'N/A')}")
            print(f"   Cég: {job.get('Cég', 'N/A')}")
            print(f"   Lokáció: {job.get('Lokáció', 'N/A')}")
            print(f"   Publikálva: {job.get('Publikálva', 'N/A')}")
            print(f"   Link: {job.get('Link', 'N/A')[:60]}...")
    
    # Category breakdown
    print("\n" + "="*70)
    print("CATEGORY BREAKDOWN:")
    print("="*70)
    category_counts = {}
    for job in all_jobs:
        # Try to get category from technology or URL
        tech = job.get('_technology', '')
        link = job.get('Link', '')
        # This is approximate, but gives us some insight
        category_counts[tech] = category_counts.get(tech, 0) + 1
    
    for tech, count in sorted(category_counts.items(), key=lambda x: -x[1])[:10]:
        if tech:
            print(f"  {tech}: {count}")
    
    return len(all_jobs)

if __name__ == '__main__':
    total = main()
    if total < 50:
        print(f"\n[WARN] Only {total} jobs from API. The code requires >=50 for API usage.")
        print("       This explains why it falls back to HTML (20 jobs).")
    else:
        print(f"\n[OK] {total} jobs from API - should use API, not HTML fallback")

