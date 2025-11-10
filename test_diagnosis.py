#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DIAGNOSZTIKAI TESZT - No Fluff Jobs API és HTML scraper
"""
import time

print("=" * 60)
print("DIAGNOSZTIKAI TESZT")
print("=" * 60)

# 1. API Health Check
print("\n[1/5] API Health Check...")
from nofluff_api_scraper import check_api_health
api_healthy = check_api_health()
print(f"      Eredmény: {api_healthy}")

# 2. API Scraper teszt
print("\n[2/5] API Scraper teszt...")
from nofluff_api_scraper import fetch_nofluff_jobs_api
start = time.time()
api_jobs = fetch_nofluff_jobs_api(categories=['artificial-intelligence'])
api_duration = time.time() - start
print(f"      Eredmény: {len(api_jobs)} állás, {api_duration:.1f}s")

# 3. HTML Scraper teszt
print("\n[3/5] HTML Scraper teszt...")
from app import fetch_nofluffjobs_jobs
start = time.time()
html_jobs = fetch_nofluffjobs_jobs(
    "No Fluff Jobs Test",
    "https://nofluffjobs.com/hu/artificial-intelligence?criteria=category%3Dsys-administrator,business-analyst,architecture,backend,data,ux,devops,erp,embedded,frontend,fullstack,game-dev,mobile,project-manager,security,support,testing,other"
)
html_duration = time.time() - start
print(f"      Eredmény: {len(html_jobs)} állás, {html_duration:.1f}s")

# 4. Profession.hu scraper teszt
print("\n[4/5] Profession.hu Scraper teszt...")
from app import fetch_html_jobs
start = time.time()
profession_jobs = fetch_html_jobs(
    "Profession Test",
    "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"
)
profession_duration = time.time() - start
print(f"      Eredmény: {len(profession_jobs)} állás, {profession_duration:.1f}s")

# 5. EGYÜTT (SZEKVENCIÁLISAN)
print("\n[5/5] EGYÜTT - szekvenciális futtatás...")
start = time.time()

print("      [5a] No Fluff API...")
if api_healthy:
    jobs_nofluff = fetch_nofluff_jobs_api(categories=['artificial-intelligence'])
    print(f"           API: {len(jobs_nofluff)} állás")
else:
    print("           API nem elérhető, HTML fallback...")
    jobs_nofluff = fetch_nofluffjobs_jobs(
        "No Fluff Jobs",
        "https://nofluffjobs.com/hu/artificial-intelligence?criteria=category%3Dsys-administrator,business-analyst,architecture,backend,data,ux,devops,erp,embedded,frontend,fullstack,game-dev,mobile,project-manager,security,support,testing,other"
    )
    print(f"           HTML: {len(jobs_nofluff)} állás")

print("      [5b] Profession.hu...")
jobs_profession = fetch_html_jobs(
    "Profession – IT főkategória",
    "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"
)
print(f"           Profession: {len(jobs_profession)} állás")

total_duration = time.time() - start

# Összegzés
print("\n" + "=" * 60)
print("ÖSSZEGZÉS")
print("=" * 60)
print(f"API Health:        {api_healthy}")
print(f"API Jobs:          {len(api_jobs)}")
print(f"HTML Jobs:         {len(html_jobs)}")
print(f"Profession Jobs:   {len(profession_jobs)}")
print(f"Együtt - NoFluff:  {len(jobs_nofluff)}")
print(f"Együtt - Profess:  {len(jobs_profession)}")
print(f"Együtt futási idő: {total_duration:.1f}s ({total_duration/60:.1f} perc)")
print("=" * 60)

if api_healthy and len(api_jobs) > 50:
    print("\n✓ API MŰKÖDIK ÉS JÓL")
else:
    print("\n✗ API PROBLÉMA")

if len(html_jobs) >= 10:
    print("✓ HTML SCRAPER MŰKÖDIK (de limitált 10-re)")
else:
    print("✗ HTML SCRAPER PROBLÉMA")

if len(jobs_nofluff) > 500 and len(jobs_profession) > 500:
    print("✓ EGYÜTTES FUTTATÁS SIKERES!")
else:
    print("✗ EGYÜTTES FUTTATÁS PROBLÉMA")

