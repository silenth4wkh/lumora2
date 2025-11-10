#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MŰKÖDŐ STANDALONE SCRAPER - Profession.hu + No Fluff Jobs
Tesztelt és bizonyítottan működik!
"""
from datetime import datetime
import openpyxl

print("=" * 60)
print("PROFESSION.HU + NO FLUFF JOBS - STANDALONE SCRAPER")
print("=" * 60)

# Import a scraper függvényeket
from app import fetch_html_jobs
from nofluff_api_scraper import fetch_nofluff_jobs_api, check_api_health

# 1. No Fluff Jobs - API (gyors!)
print("\n[1/3] No Fluff Jobs scraping (API)...")
nofluff_jobs = []
if check_api_health():
    print("      API elerheto, hasznalata...")
    nofluff_jobs = fetch_nofluff_jobs_api(categories=['artificial-intelligence'])
    print(f"      [OK] API: {len(nofluff_jobs)} allas")
else:
    print("      [WARN] API nem elerheto")

# 2. Profession.hu scraping
print("\n[2/3] Profession.hu scraping...")
profession_jobs = fetch_html_jobs(
    "Profession - IT fokategoria",
    "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"
)
print(f"      [OK] Profession.hu: {len(profession_jobs)} allas")

# 3. Egyesítés és duplikáció szűrés
print("\n[3/3] Excel export...")
all_jobs = nofluff_jobs + profession_jobs

seen_links = set()
unique_jobs = []
for job in all_jobs:
    link = job.get('Link', '').split('?')[0]
    if link and link not in seen_links:
        seen_links.add(link)
        unique_jobs.append(job)

print(f"      Osszesen: {len(all_jobs)} allas")
print(f"      Duplikacio utan: {len(unique_jobs)} allas")

# Excel létrehozása
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "IT Allasok"

# Fejlécek
headers = ['ID', 'Forras', 'Pozicio', 'Ceg', 'Lokacio', 'Link', 'Fizetes', 'Leiras', 'Publikalva']
ws.append(headers)

# Adatok
today = datetime.today().strftime('%Y-%m-%d')
for i, job in enumerate(unique_jobs, 1):
    ws.append([
        i,
        job.get('Forrás', 'Forrás') or 'N/A',  # Key compatibility
        job.get('Pozíció', 'Pozicio') or 'N/A',
        job.get('Cég', 'Ceg') or 'N/A',
        job.get('Lokáció', 'Lokacio') or 'N/A',
        job.get('Link', '') or 'N/A',
        job.get('Fizetés', 'Fizetes') or '',
        (job.get('Leírás', 'Leiras') or '')[:200],
        job.get('Publikálva', 'Publikalva') or job.get('Publikálva_dátum', '') or today
    ])

# Mentés
filename = f"it_allasok_working_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
wb.save(filename)

print(f"\n[OK] Excel fajl mentve: {filename}")
print("=" * 60)
print("[SUCCESS] SCRAPING KESZ!")
print(f"  - Profession.hu: {len(profession_jobs)} allas")
print(f"  - No Fluff Jobs: {len(nofluff_jobs)} allas")
print(f"  - Egyedi allasok: {len(unique_jobs)}")
print("=" * 60)

