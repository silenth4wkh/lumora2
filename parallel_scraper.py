#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Párhuzamos scraper modul - Profession.hu és No Fluff Jobs egyidejűleg
"""
import threading
from datetime import datetime
import time

def parallel_search_both_portals(fetch_html_jobs_func, fetch_nofluff_api, fetch_nofluff_html, check_api_health):
    """
    Párhuzamos scraping: Profession.hu és No Fluff Jobs egyidejűleg
    
    Returns:
        list: Összesített job lista (mindkét portál)
    """
    results = {'profession': [], 'nofluff': []}
    errors = {}
    
    def scrape_profession():
        """Profession.hu scraping thread"""
        try:
            print(f"[PARALLEL] Profession.hu - thread START")
            start = time.time()
            
            url = "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"
            items = fetch_html_jobs_func("Profession – IT főkategória", url)
            results['profession'] = items if items else []
            
            duration = time.time() - start
            print(f"[PARALLEL] Profession.hu - DONE: {len(results['profession'])} jobs in {duration:.1f}s")
        except Exception as e:
            print(f"[PARALLEL] Profession.hu - ERROR: {e}")
            import traceback
            traceback.print_exc()
            errors['profession'] = str(e)
            results['profession'] = []
    
    def scrape_nofluff():
        """No Fluff Jobs scraping thread (API first, HTML fallback)"""
        try:
            print(f"[PARALLEL] No Fluff Jobs - thread START")
            start = time.time()
            
            items = []
            # Try API first
            if check_api_health():
                print(f"[PARALLEL] No Fluff Jobs - using API")
                items = fetch_nofluff_api(categories=['artificial-intelligence'])
                if items and len(items) >= 50:
                    print(f"[PARALLEL] No Fluff Jobs - API SUCCESS: {len(items)} jobs")
                else:
                    print(f"[PARALLEL] No Fluff Jobs - API insufficient, fallback to HTML")
                    items = []
            
            # HTML fallback
            if not items:
                print(f"[PARALLEL] No Fluff Jobs - using HTML scraping")
                url = "https://nofluffjobs.com/hu/artificial-intelligence?criteria=category%3Dsys-administrator,business-analyst,architecture,backend,data,ux,devops,erp,embedded,frontend,fullstack,game-dev,mobile,project-manager,security,support,testing,other"
                items = fetch_nofluff_html("No Fluff Jobs – IT kategóriák", url)
            
            results['nofluff'] = items if items else []
            duration = time.time() - start
            print(f"[PARALLEL] No Fluff Jobs - DONE: {len(results['nofluff'])} jobs in {duration:.1f}s")
        except Exception as e:
            print(f"[PARALLEL] No Fluff Jobs - ERROR: {e}")
            import traceback
            traceback.print_exc()
            errors['nofluff'] = str(e)
            results['nofluff'] = []
    
    # Start threads
    t1 = threading.Thread(target=scrape_profession, daemon=False)
    t2 = threading.Thread(target=scrape_nofluff, daemon=False)
    
    print(f"[PARALLEL] Starting 2 threads...")
    t1.start()
    t2.start()
    
    # Wait for both
    print(f"[PARALLEL] Waiting for threads to complete...")
    t1.join(timeout=900)  # Max 15 min
    t2.join(timeout=900)
    
    print(f"[PARALLEL] All threads completed")
    
    # Combine results
    all_jobs = results['profession'] + results['nofluff']
    print(f"[PARALLEL] Total: {len(all_jobs)} jobs (Profession: {len(results['profession'])}, NoFluff: {len(results['nofluff'])})")
    
    if errors:
        print(f"[PARALLEL] Errors occurred: {errors}")
    
    return all_jobs

