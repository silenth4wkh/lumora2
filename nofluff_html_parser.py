#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
No Fluff Jobs HTML-alapú parsing (anchor + környezet strukturált elemzése)
"""
from bs4 import BeautifulSoup
from datetime import datetime
import re

def parse_nofluff_html_anchors(html):
    """
    Parse No Fluff Jobs HTML anchor elemekből.
    Visszaad: list of {Pozíció, Cég, Lokáció, Publikálva, Leírás, Link}
    """
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Keressünk job card/posting elemeket
    # No Fluff Jobs általában <a> linkeket használ job card-okhoz
    job_links = soup.select("a[href*='/hu/job/']")
    
    for a in job_links:
        href = a.get('href')
        if not href:
            continue
        if href.startswith('/'):
            href = f"https://nofluffjobs.com{href}"
        link = href.split('?')[0]
        
        # Pozíció: h3.posting-title__position elem tartalmazza a pontos pozíció nevet
        title = 'N/A'
        title_elem = a.find('h3', class_=re.compile(r'posting-title__position', re.I))
        if title_elem:
            # Csak a h3 közvetlen text node-ját, ne a span (ÚJ) gyermekét
            title_raw = ''.join(title_elem.find_all(string=True, recursive=False))
            title = title_raw.strip()
        
        # Ha nem találtuk, fallback az anchor első 60 karaktere
        if not title or title == 'N/A':
            title_raw = a.get_text(strip=True) or ''
            title = title_raw[:60].strip()
        
        # Cég és lokáció: próbáljuk meg a parent vagy testvér elemekből kinyerni
        company = 'N/A'
        location = 'N/A'
        
        # Cégnév: keresés anchor-ban és parent-ben is
        company_elem = a.find(class_=re.compile(r'company|employer|brand', re.I))
        if company_elem:
            company = company_elem.get_text(strip=True)
        
        # Lokáció: keresés anchor-ban
        location_elem = a.find(class_=re.compile(r'location|city|place', re.I))
        if location_elem:
            location = location_elem.get_text(strip=True)
        elif location == 'N/A':
            # Fallback: keres lokáció kulcsszavakat az anchor teljes szövegében
            anchor_text = a.get_text(' ', strip=True)
            loc_match = re.search(r'\b(Remote|Hybrid|Távmunka|Budapest|Debrecen|Győr|Szeged|Pécs)\b', anchor_text, re.I)
            if loc_match:
                location = loc_match.group(0)
        
        # Leírás: általában nincs az anchor-ban, ezért üres marad
        # (csak a detail oldalon érhető el)
        description = ''
        
        # Publikálva: keressünk dátum szöveget az anchor-ban vagy környezetében
        pub_date = ''
        from datetime import timedelta
        date_patterns = [
            (r'(\d+)\s*napja', lambda m: (datetime.today() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')),
            (r'(\d+)\s*hete', lambda m: (datetime.today() - timedelta(weeks=int(m.group(1)))).strftime('%Y-%m-%d')),
            (r'\bma\b', lambda m: today),
            (r'\btegnap\b', lambda m: (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')),
        ]
        anchor_text = a.get_text(' ', strip=True)
        for pattern, converter in date_patterns:
            match = re.search(pattern, anchor_text, re.I)
            if match:
                try:
                    pub_date = converter(match)
                    break
                except:
                    pass
        
        jobs.append({
            'Pozíció': title or 'N/A',
            'Cég': company,
            'Lokáció': location,
            'Publikálva': pub_date,
            'Leírás': description,
            'Link': link
        })
    
    return jobs

