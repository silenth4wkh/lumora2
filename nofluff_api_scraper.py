#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
No Fluff Jobs API-alapú scraper (pontos publikálási dátummal)
"""
import requests
from datetime import datetime
import time

def fetch_nofluff_jobs_api(categories=None):
    """
    No Fluff Jobs állások lekérése API-ból.
    
    Args:
        categories: lista vagy None. Ha None, akkor 'artificial-intelligence' default.
    
    Returns:
        list of dict: [{Pozíció, Cég, Lokáció, Publikálva, Leírás, Link, ...}]
    """
    if categories is None:
        categories = ['artificial-intelligence']
    
    api_url = "https://nofluffjobs.com/api/posting"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://nofluffjobs.com/hu/artificial-intelligence',
    }
    
    all_jobs = []
    today = datetime.today().strftime('%Y-%m-%d')
    
    for category in categories:
        print(f"[NOFLUFF][API] Fetching category: {category}")
        
        try:
            params = {'category': category}
            r = requests.get(api_url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            
            data = r.json()
            postings = data.get('postings', [])
            
            print(f"[NOFLUFF][API] Raw postings count: {len(postings)}")
            
            # Szűrés: csak magyar állások (regions: 'hu')
            hungarian_jobs = [p for p in postings if 'hu' in p.get('regions', [])]
            print(f"[NOFLUFF][API] Hungarian jobs: {len(hungarian_jobs)}")
            
            for posting in hungarian_jobs:
                job = parse_api_posting(posting, today)
                if job:
                    all_jobs.append(job)
            
            # Rate limiting (viselkedj emberileg)
            time.sleep(0.5)
        
        except Exception as e:
            print(f"[NOFLUFF][API][ERROR] {e}")
            raise  # Propagáljuk a hibát a fallback logikához
    
    print(f"[NOFLUFF][API] Total jobs parsed: {len(all_jobs)}")
    return all_jobs


def parse_api_posting(posting, today):
    """
    API posting objektum → strukturált job dict
    
    Args:
        posting: dict az API-ból
        today: str (YYYY-MM-DD)
    
    Returns:
        dict: {Pozíció, Cég, Lokáció, Publikálva, ...}
    """
    try:
        # Alapadatok
        title = posting.get('title', 'N/A')
        company = posting.get('name', 'N/A')
        url_slug = posting.get('url', '')
        link = f"https://nofluffjobs.com/hu/job/{url_slug}" if url_slug else ''
        
        # Lokáció - első magyar város vagy Remote
        location = 'N/A'
        location_data = posting.get('location', {})
        places = location_data.get('places', [])
        
        # Keressük az első magyar várost vagy Remote-ot
        for place in places:
            city = place.get('city', '')
            country = place.get('country', {})
            country_code = country.get('code', '')
            
            if city == 'Remote':
                location = 'Távmunka'
                break
            elif country_code == 'HUN':
                location = city
                break
        
        # Ha nincs magyar város, de van Remote
        if location == 'N/A' and location_data.get('fullyRemote'):
            location = 'Távmunka'
        
        # Publikálási dátum - Unix timestamp (milliszekundum) -> YYYY-MM-DD
        posted_timestamp = posting.get('posted')
        pub_date = ''
        if posted_timestamp:
            try:
                dt = datetime.fromtimestamp(posted_timestamp / 1000)
                pub_date = dt.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"[NOFLUFF][API][WARN] Date conversion failed: {e}")
                pub_date = today  # Fallback
        
        # Bérsáv - salary objektumból
        salary_info = ''
        salary_data = posting.get('salary')
        if salary_data:
            salary_from = salary_data.get('from')
            salary_to = salary_data.get('to')
            currency = salary_data.get('currency', '')
            salary_type = salary_data.get('type', '')
            
            if salary_from and salary_to:
                # Format: "28560 - 45360 PLN (b2b)"
                salary_info = f"{int(salary_from)} - {int(salary_to)} {currency}"
                if salary_type:
                    salary_info += f" ({salary_type})"
        
        # Leírás - nincs az API-ban, detail oldalról kellene
        description = ''
        
        # Tech stack (opcionális)
        technology = posting.get('technology', '')
        
        return {
            'Forrás': 'No Fluff Jobs',
            'Pozíció': title,
            'Cég': company,
            'Lokáció': location,
            'Publikálva': pub_date,
            'Fizetés': salary_info,
            'Leírás': description,
            'Link': link,
            'Lekérés_dátuma': today,
            # Extra mezők (debug)
            '_technology': technology,
            '_api_source': True,
        }
    
    except Exception as e:
        print(f"[NOFLUFF][API][WARN] Parsing error: {e}")
        return None


def check_api_health():
    """
    API health check - működik-e az endpoint?
    
    Returns:
        bool: True ha működik, False ha nem
    """
    api_url = "https://nofluffjobs.com/api/posting"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        # FONTOS: category paraméter kell az API-nak!
        params = {'category': 'artificial-intelligence'}
        r = requests.get(api_url, headers=headers, params=params, timeout=5)
        
        if r.status_code != 200:
            return False
        
        # Ellenőrizzük hogy JSON-t kapunk és van benne 'postings'
        try:
            data = r.json()
            return 'postings' in data and len(data.get('postings', [])) > 0
        except:
            return False
    except:
        return False


if __name__ == '__main__':
    # Teszt
    print("Testing No Fluff Jobs API scraper...")
    jobs = fetch_nofluff_jobs_api()
    print(f"\nTotal jobs: {len(jobs)}")
    if jobs:
        print("\nFirst 3 jobs:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['Pozíció']}")
            print(f"   Cég: {job['Cég']}")
            print(f"   Lokáció: {job['Lokáció']}")
            print(f"   Publikálva: {job['Publikálva']}")
            print(f"   Link: {job['Link'][:60]}...")

