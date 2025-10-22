from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from datetime import datetime
import time
import re
import json
from collections import defaultdict
import threading
import queue
import os
import io

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

app = Flask(__name__)
CORS(app)

# Error handler for debugging
@app.errorhandler(Exception)
def handle_exception(e):
    error_message = f"Error: {str(e)}"
    print(f"ERROR: {error_message}")
    return jsonify({"error": error_message, "type": type(e).__name__}), 500

# Scraper kód (a te kódból)
KW_LANG = [
    "java","python","c#",".net","dotnet","c++","cpp","golang","go","rust","php","ruby","scala","haskell",
    "kotlin","swift","objective-c"
]
KW_FE = [
    "frontend","front-end","react","angular","vue","svelte","next.js","nuxt","typescript","javascript","web developer"
]
KW_BE = [
    "backend","back-end","node","spring","spring boot","quarkus",".net core","asp.net","laravel","symfony","django","flask","fastapi"
]
KW_MOBILE = [
    "android","ios","mobile","kotlin","swift","flutter","react native","xamarin","ionic"
]
KW_DATA = [
    "data engineer","data scientist","ml engineer","machine learning","ai engineer","big data",
    "etl","elt","dwh","data warehouse","power bi","tableau","qlik","sql","spark","hadoop","db developer","snowflake","databricks"
]
KW_DEVOPS = [
    "devops","sre","site reliability","platform engineer","cloud engineer","kubernetes","docker","terraform","ansible",
    "aws","azure","gcp","cloud architect","finops","observability"
]
KW_TEST = [
    "qa","test automation","tesztautomatizálás","tesztmérnök","sdet","cypress","selenium","playwright","jmeter","postman"
]
KW_EMBED = [
    "embedded","firmware","fpga","rtos","bare metal","microcontroller","stm32","esp32","embedded linux","yocto","driver developer","c developer"
]
KW_SECURITY = [
    "security engineer","application security","appsec","devsecops","penetration tester","pentest","iam","siem","soc"
]
KW_ENTERPRISE = [
    "sap","abap","erp","crm","salesforce","servicenow","mendix","outsystems","navision","business central","oracle developer","ms dynamics"
]
KW_GENERAL_HU = [
    "fejlesztő","programozó","szoftver","szoftvermérnök","rendszermérnök","alkalmazásfejlesztő","alkalmazás üzemeltető","full stack","full-stack"
]

KEYWORDS = (
    KW_LANG + KW_FE + KW_BE + KW_MOBILE + KW_DATA + KW_DEVOPS +
    KW_TEST + KW_EMBED + KW_SECURITY + KW_ENTERPRISE + KW_GENERAL_HU
)

EXCLUDE_PHRASES = [
    "fejlesztő pedagógus","pedagógus","gyógypedagógus","konstruktőr","technológus","gyártás",
    "pénztáros","eladó","értékesítő","ügyfél","adminisztrátor","raktár","logisztika","gépkezelő","karbantartó"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE = "https://www.profession.hu/allasok/1,0,0,{}"

# Portálok definiálása
PORTALS = {
    "profession": {
        "name": "Profession.hu",
        "description": "Magyarország legnagyobb álláskereső portálja",
        "status": "Aktív",
        "enabled": True
    },
    "jobline": {
        "name": "Jobline.hu",
        "description": "IT specializált álláskereső portál",
        "status": "Tervezés alatt",
        "enabled": False
    },
    "cvonline": {
        "name": "CV-Online.hu",
        "description": "Népszerű álláskereső portál",
        "status": "Tervezés alatt",
        "enabled": False
    },
    "indeed": {
        "name": "Indeed.hu",
        "description": "Nemzetközi álláskereső portál",
        "status": "Tervezés alatt",
        "enabled": False
    }
}

# ——————————————————————————
# Kulcsszó-katalógus (maximalista, bővíthető)
# ——————————————————————————
KW_LANG = [
    "java","python","c#",".net","dotnet","c++","cpp","golang","go","rust","php","ruby","scala","haskell",
    "kotlin","swift","objective-c"
]
KW_FE = [
    "frontend","front-end","react","angular","vue","svelte","next.js","nuxt","typescript","javascript","web developer"
]
KW_BE = [
    "backend","back-end","node","spring","spring boot","quarkus",".net core","asp.net","laravel","symfony","django","flask","fastapi"
]
KW_MOBILE = [
    "android","ios","mobile","kotlin","swift","flutter","react native","xamarin","ionic"
]
KW_DATA = [
    "data engineer","data scientist","ml engineer","machine learning","ai engineer","big data",
    "etl","elt","dwh","data warehouse","power bi","tableau","qlik","sql","spark","hadoop","db developer","snowflake","databricks"
]
KW_DEVOPS = [
    "devops","sre","site reliability","platform engineer","cloud engineer","kubernetes","docker","terraform","ansible",
    "aws","azure","gcp","cloud architect","finops","observability"
]
KW_TEST = [
    "qa","test automation","tesztautomatizálás","tesztmérnök","sdet","cypress","selenium","playwright","jmeter","postman"
]
KW_EMBED = [
    "embedded","firmware","fpga","rtos","bare metal","microcontroller","stm32","esp32","embedded linux","yocto","driver developer","c developer"
]
KW_SECURITY = [
    "security engineer","application security","appsec","devsecops","penetration tester","pentest","iam","siem","soc"
]
KW_ENTERPRISE = [
    "sap","abap","erp","crm","salesforce","servicenow","mendix","outsystems","navision","business central","oracle developer","ms dynamics"
]
KW_GENERAL_HU = [
    "fejlesztő","programozó","szoftver","szoftvermérnök","rendszermérnök","alkalmazásfejlesztő","alkalmazás üzemeltető","full stack","full-stack"
]

# Összes kulcsszó egy listában
ALL_KEYWORDS = (
    KW_LANG + KW_FE + KW_BE + KW_MOBILE + KW_DATA + KW_DEVOPS +
    KW_TEST + KW_EMBED + KW_SECURITY + KW_ENTERPRISE + KW_GENERAL_HU
)

# Kategóriák definiálása a frontend-hez
CATEGORIES = {
    "languages": {"name": "Programozási nyelvek", "keywords": KW_LANG},
    "frontend": {"name": "Frontend fejlesztés", "keywords": KW_FE},
    "backend": {"name": "Backend fejlesztés", "keywords": KW_BE},
    "mobile": {"name": "Mobil fejlesztés", "keywords": KW_MOBILE},
    "data": {"name": "Data & AI", "keywords": KW_DATA},
    "devops": {"name": "DevOps & Cloud", "keywords": KW_DEVOPS},
    "testing": {"name": "Tesztelés", "keywords": KW_TEST},
    "embedded": {"name": "Embedded", "keywords": KW_EMBED},
    "security": {"name": "Biztonság", "keywords": KW_SECURITY},
    "enterprise": {"name": "Enterprise", "keywords": KW_ENTERPRISE},
    "general": {"name": "Általános IT", "keywords": KW_GENERAL_HU}
}

def clean_text(s: str) -> str:
    if not s:
        return ""
    # Karakterkódolás javítása
    if isinstance(s, str):
        s = s.encode('utf-8', errors='ignore').decode('utf-8')
    s = re.sub(r"<.*?>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Speciális karakterek tisztítása
    s = s.replace('\u00a0', ' ')  # Non-breaking space
    s = s.replace('\u2013', '-')  # En dash
    s = s.replace('\u2014', '--') # Em dash
    s = s.replace('\u2018', "'")  # Left single quotation mark
    s = s.replace('\u2019', "'")  # Right single quotation mark
    s = s.replace('\u201c', '"')  # Left double quotation mark
    s = s.replace('\u201d', '"')  # Right double quotation mark
    return s

def build_feed_url(keyword: str) -> str:
    return BASE.format(quote(keyword, safe=""))

def is_probably_dev(title: str, desc: str) -> bool:
    t = (title or "").lower()
    d = (desc or "").lower()
    if any(bad in t for bad in EXCLUDE_PHRASES) or any(bad in d for bad in EXCLUDE_PHRASES):
        return False
    return True

def parse_publication_date(date_str: str):
    """Publikálási dátum feldolgozása ISO formátumra"""
    if not date_str:
        return None, False
    
    date_str = date_str.strip().lower()
    
    # "Friss" esetén
    if "friss" in date_str:
        return datetime.today().strftime("%Y-%m-%d"), True
    
    # Magyar dátum formátumok
    import re
    from datetime import datetime, timedelta
    
    # 2025. október 20. formátum
    match = re.search(r'(\d{4})\.\s*(\w+)\s*(\d{1,2})\.', date_str)
    if match:
        year, month_name, day = match.groups()
        month_map = {
            'január': 1, 'február': 2, 'március': 3, 'április': 4,
            'május': 5, 'június': 6, 'július': 7, 'augusztus': 8,
            'szeptember': 9, 'október': 10, 'november': 11, 'december': 12
        }
        if month_name in month_map:
            try:
                date_obj = datetime(int(year), month_map[month_name], int(day))
                return date_obj.strftime("%Y-%m-%d"), False
            except ValueError:
                pass
    
    # 2025-10-20 formátum
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d"), False
        except ValueError:
            pass
    
    # 20. október 2025 formátum
    match = re.search(r'(\d{1,2})\.\s*(\w+)\s*(\d{4})', date_str)
    if match:
        day, month_name, year = match.groups()
        month_map = {
            'január': 1, 'február': 2, 'március': 3, 'április': 4,
            'május': 5, 'június': 6, 'július': 7, 'augusztus': 8,
            'szeptember': 9, 'október': 10, 'november': 11, 'december': 12
        }
        if month_name in month_map:
            try:
                date_obj = datetime(int(year), month_map[month_name], int(day))
                return date_obj.strftime("%Y-%m-%d"), False
            except ValueError:
                pass
    
    # Ha nem sikerült feldolgozni, ma dátumot adunk vissza
    return datetime.today().strftime("%Y-%m-%d"), False

def create_excel_export(jobs_data):
    """Excel fájl létrehozása a munkák adataiból"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        
        wb = Workbook()
        ws = wb.active
        ws.title = "IT Állások"
        
        # Oszlopok definiálása
        headers = [
            "ID", "Forrás", "Pozíció", "Cég", "Lokáció", "Fizetés", 
            "Munkavégzés típusa", "Cég mérete", "Publikálva", 
            "Lekérés dátuma", "Leírás", "Link"
        ]
        
        # Stílusok definiálása
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Border stílus
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Fejléc sor hozzáadása
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Adatok hozzáadása
        for row_num, job in enumerate(jobs_data, 2):
            ws.cell(row=row_num, column=1, value=job.get("id", ""))
            ws.cell(row=row_num, column=2, value=job.get("forras", ""))
            ws.cell(row=row_num, column=3, value=job.get("pozicio", ""))
            ws.cell(row=row_num, column=4, value=job.get("ceg", ""))
            ws.cell(row=row_num, column=5, value=job.get("lokacio", ""))
            ws.cell(row=row_num, column=6, value=job.get("fizetes", ""))
            ws.cell(row=row_num, column=7, value=job.get("munkavégzés_típusa", ""))
            ws.cell(row=row_num, column=8, value=job.get("ceg_merete", ""))
            ws.cell(row=row_num, column=9, value=job.get("publikalva", ""))
            ws.cell(row=row_num, column=10, value=job.get("lekeres_datuma", ""))
            ws.cell(row=row_num, column=11, value=job.get("leiras", ""))
            ws.cell(row=row_num, column=12, value=job.get("link", ""))
            
            # Border hozzáadása minden cellához
            for col_num in range(1, len(headers) + 1):
                ws.cell(row=row_num, column=col_num).border = thin_border
        
        # Oszlopok szélességének beállítása
        column_widths = [8, 20, 40, 25, 20, 20, 20, 15, 15, 15, 50, 60]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        
        # Szűrés hozzáadása
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(jobs_data) + 1}"
        
        return wb
        
    except ImportError:
        print("openpyxl nincs telepítve, egyszerű Excel export használata")
        # Fallback: egyszerű CSV formátum
        return None

def get_total_pages(source_name: str, url: str):
    """Get total number of pages for a search - dinamikus meghatározás"""
    print(f"[DEBUG] get_total_pages hivasa: {source_name} - {url}")
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        
        # Első oldal lekérése
        r = session.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # 1. Keresés pagination elemekben
        pagination_selectors = [
            'div.pager', 'nav.pager', '.pager',  # Profession.hu specifikus
            'div.pagination', 'nav.pagination', '.pagination', 
            'ul.pagination', 'ol.pagination'
        ]
        
        for selector in pagination_selectors:
            pagination = soup.select_one(selector)
            if pagination:
                print(f"[DEBUG] Pagination elem találva: {selector}")
                
                # Keresés utolsó oldal linkjében
                page_links = pagination.find_all('a', href=True)
                if page_links:
                    # Utolsó link href-jéből oldalszám kinyerése
                    last_href = page_links[-1].get('href', '')
                    print(f"[DEBUG] Utolsó pagination link: {last_href}")
                    
                    # Profession.hu formátum: /OLDALSZÁM,10
                    if '/,' in last_href:
                        try:
                            page_num = int(last_href.split('/')[-1].split(',')[0])
                            print(f"[SUCCESS] {source_name} - Dinamikus oldalszám: {page_num} oldal")
                            return page_num
                        except (ValueError, IndexError):
                            pass
                    
                    # Standard formátum: ?page=N vagy &page=N
                    if 'page=' in last_href:
                        try:
                            page_num = int(last_href.split('page=')[1].split('&')[0].split('#')[0])
                            print(f"[SUCCESS] {source_name} - Dinamikus oldalszám: {page_num} oldal")
                            return page_num
                        except (ValueError, IndexError):
                            pass
                
                # Fallback: span elemekben keresés (ha nincs link)
                page_spans = pagination.find_all('span')
                if page_spans:
                    max_page = 0
                    for span in page_spans:
                        span_text = span.get_text(strip=True)
                        if span_text.isdigit():
                            max_page = max(max_page, int(span_text))
                    if max_page > 0:
                        print(f"[SUCCESS] {source_name} - Dinamikus oldalszám (span): {max_page} oldal")
                        return max_page
        
        # 2. Fallback: job card szám alapján becslés
        job_selectors = [
            'li.card.job-card', 'ul.job-cards li', '.job-card', 
            '.job-item', '.listing-item', '.search-result-item'
        ]
        
        total_jobs = 0
        for selector in job_selectors:
            job_cards = soup.select(selector)
            if job_cards:
                total_jobs = len(job_cards)
                break
        
        if total_jobs > 0:
            # Becslés: ~13-15 állás/oldal (Profession.hu átlag)
            estimated_pages = max(1, (total_jobs + 12) // 13)  # Felfelé kerekítés
            print(f"[ESTIMATE] {source_name} - Becsült oldalszám: {estimated_pages} (alapján: {total_jobs} job card)")
            return estimated_pages
        
        # 3. Fallback: 1 oldal
        print(f"[FALLBACK] {source_name} - Nem található pagination, 1 oldal használata")
        return 1
        
    except Exception as e:
        print(f"[WARNING] {source_name} - Oldalszám meghatározási hiba: {e}, 1 oldal használata")
        return 1

def fetch_html_jobs(source_name: str, url: str, max_pages: int = None):
    """HTML scraping a Profession.hu álláslistákról - dinamikus oldalszám"""
    if not BeautifulSoup:
        print("BeautifulSoup nincs telepítve, RSS fallback használata")
        return fetch_rss_fallback(source_name, url)
    
    # Get total pages dynamically if not specified
    if max_pages is None:
        max_pages = get_total_pages(source_name, url)
    
    # Dinamikus limit - mindig annyi oldal amennyi van
    # Csak biztonsági limit: maximum 200 oldal (védés a végtelen ciklus ellen)
    max_pages = min(max_pages, 200)  # Biztonsági limit
    
    print(f"[INFO] {source_name} - {max_pages} oldal feldolgozása")
    
    all_items = []
    
    for page in range(1, max_pages + 1):
        try:
            # Oldalszámozás hozzáadása - Profession.hu formátum: /OLDALSZÁM,10
            if '/1,10' in url:
                page_url = url.replace('/1,10', f'/{page},10')
            elif '&page=' in url or '?page=' in url:
                page_url = f"{url}&page={page}" if "?" in url else f"{url}?page={page}"
            else:
                page_url = f"{url}&page={page}" if "?" in url else f"{url}?page={page}"
            
            # Debug: URL ellenőrzés
            if page <= 3:  # Csak az első 3 oldalról debug
                print(f"   [DEBUG] Oldal {page} URL: {page_url}")
            
            # Retry logika timeout esetén
            max_retries = 5
            for retry in range(max_retries):
                try:
                    r = requests.get(page_url, headers=HEADERS, timeout=30)
                    r.raise_for_status()
                    break
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
                    if retry < max_retries - 1:
                        wait_time = (retry + 1) * 10
                        print(f"   [WARNING] Error, retry {retry + 1}/{max_retries} in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        print(f"   [ERROR] Max retries reached, skipping page {page}")
                        raise e
            r.encoding = "utf-8"
            
            # Karakterkódolás javítása
            content = r.text
            if r.encoding.lower() != 'utf-8':
                content = content.encode('utf-8', errors='ignore').decode('utf-8')
            
            soup = BeautifulSoup(content, "html.parser")
            
            # Keresés ul.job-cards > li elemekben
            job_cards = soup.select("ul.job-cards li")
            if not job_cards:
                # Fallback: más lehetséges szelektorok
                job_cards = soup.select(".job-card, .job-item, .listing-item, .search-result-item")
            
            print(f"DEBUG: {source_name} - Oldal {page}: {len(job_cards)} job card")
            
            if not job_cards:
                # Ha nincs több állás, szakítsuk meg
                print(f"   [STOP] Nincs több állás az oldalon, leállítás")
                break
            
            for card in job_cards:
                try:
                    # Pozíció címe
                    title_elem = card.select_one("h3, .job-title, .position-title, .title, a[href*='/allas/']")
                    title = clean_text(title_elem.get_text()) if title_elem else ""
                    
                    # Link
                    link_elem = card.select_one("a[href*='/allas/']")
                    link = link_elem.get("href") if link_elem else ""
                    if link and not link.startswith("http"):
                        link = "https://www.profession.hu" + link
                    
                    # Cég neve - profession.hu specifikus szelektorok
                    company_elem = card.select_one(".company-name, .employer-name, .job-company, .company, [data-company], .job-card-company")
                    if not company_elem:
                        # Fallback: keresés a szövegben - egyszerűsített megközelítés
                        card_text = card.get_text()
                        import re
                        
                        # Keresés cégnevek után (Kft, Zrt, stb.) - csak a végén lévő cégneveket
                        # A cég neve általában a job card végén van
                        lines = card_text.split('\n')
                        company = ""
                        
                        # Végigjárjuk a sorokat hátulról
                        for line in reversed(lines):
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Keresés cégnevek után
                            company_match = re.search(r'([A-ZÁÉÍÓÖŐÚÜŰ][a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\s&.,-]+(?:Kft|Zrt|Nyrt|Bt|Kkt|Ltd|Corp|Inc|Hungary|Services|Solutions|Technologies|Systems|Group|Consulting|Software|Digital|IT|Tech))\b', line)
                            if company_match:
                                potential_company = company_match.group(1).strip()
                                # Ellenőrizzük, hogy nem pozíció cím
                                if not any(word in potential_company.lower() for word in [
                                    'developer', 'engineer', 'manager', 'analyst', 'specialist', 'consultant', 'architect',
                                    'programozó', 'fejlesztő', 'menedzser', 'elemző', 'szakember', 'tanácsadó', 'építész',
                                    'rendszer', 'alkalmazás', 'webes', 'mobil', 'backend', 'frontend', 'full-stack',
                                    'tervezése', 'fejlesztése', 'optimalizálása', 'integrálva', 'meglévő', 'új', 'munkatárs'
                                ]):
                                    company = potential_company
                                    break
                        
                        # Ha nem találtunk cégnevet, próbáljuk meg a teljes szövegből
                        if not company:
                            company_match = re.search(r'([A-ZÁÉÍÓÖŐÚÜŰ][a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\s&.,-]+(?:Kft|Zrt|Nyrt|Bt|Kkt|Ltd|Corp|Inc|Hungary|Services|Solutions|Technologies|Systems|Group|Consulting|Software|Digital|IT|Tech))\b', card_text)
                            if company_match:
                                potential_company = company_match.group(1).strip()
                                if not any(word in potential_company.lower() for word in [
                                    'developer', 'engineer', 'manager', 'analyst', 'specialist', 'consultant', 'architect',
                                    'programozó', 'fejlesztő', 'menedzser', 'elemző', 'szakember', 'tanácsadó', 'építész',
                                    'rendszer', 'alkalmazás', 'webes', 'mobil', 'backend', 'frontend', 'full-stack',
                                    'tervezése', 'fejlesztése', 'optimalizálása', 'integrálva', 'meglévő', 'új', 'munkatárs'
                                ]):
                                    company = potential_company
                    else:
                        company = clean_text(company_elem.get_text())
                    
                    # Lokáció - profession.hu specifikus szelektorok
                    location_elem = card.select_one(".job-location, .location, .city, .place, [data-location], .job-card-location")
                    if not location_elem:
                        # Fallback: keresés a szövegben
                        card_text = card.get_text()
                        # Magyar városok keresése
                        hungarian_cities = ["Budapest", "Debrecen", "Szeged", "Miskolc", "Pécs", "Győr", "Nyíregyháza", "Kecskemét", "Székesfehérvár", "Szombathely", "Szolnok", "Tatabánya", "Kaposvár", "Békéscsaba", "Zalaegerszeg", "Érd", "Sopron", "Veszprém", "Dunaújváros", "Hódmezővásárhely"]
                        for city in hungarian_cities:
                            if city in card_text:
                                location = city
                                break
                        else:
                            location = ""
                    else:
                        location = clean_text(location_elem.get_text())
                    
                    # Leírás
                    desc_elem = card.select_one(".description, .job-description, .summary, .excerpt")
                    desc = clean_text(desc_elem.get_text()) if desc_elem else ""
                    
                    # Dátum
                    date_elem = card.select_one(".date, .published, .job-date, .time")
                    pub_date = clean_text(date_elem.get_text()) if date_elem else ""
                    
                    # Dátum feldolgozás - ISO formátumra konvertálás
                    pub_date_iso, is_fresh = parse_publication_date(pub_date)
                    
                    if title and link:
                        all_items.append({
                            "Forrás": source_name, 
                            "Pozíció": title, 
                            "Link": link, 
                            "Leírás": desc,
                            "Publikálva": pub_date,
                            "Publikálva_dátum": pub_date_iso,
                            "Friss_állás": is_fresh,
                            "Cég": company,
                            "Lokáció": location
                        })
                        
                except Exception as e:
                    print(f"ERROR parsing job card: {e}")
                    continue
            
            # Kímélet a szerver felé (csökkentett delay - stabilitásért)
            time.sleep(1.0)
            
        except Exception as e:
            print(f"ERROR fetching page {page}: {e}")
            break
    
    print(f"DEBUG: {source_name} - Összesen {len(all_items)} állás {page-1} oldalról (max {max_pages})")
    return all_items

def fetch_rss_items(source_name: str, url: str):
    """RSS feed feldolgozása"""
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    r.encoding = "utf-8"
    root = ET.fromstring(r.text)
    items = []
    for it in root.findall(".//item"):
        title = clean_text(it.findtext("title",""))
        link  = (it.findtext("link","") or "").strip()
        desc  = clean_text(it.findtext("description",""))
        pub   = (it.findtext("pubDate","") or "").strip()
        items.append({"Forrás": source_name, "Pozíció": title, "Link": link, "Leírás": desc, "Publikálva": pub, "Cég": "", "Lokáció": ""})
    return items

def fetch_rss_fallback(source_name: str, url: str):
    """RSS fallback ha HTML scraping nem működik"""
    rss_url = url + "?rss"
    r = requests.get(rss_url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    r.encoding = "utf-8"
    root = ET.fromstring(r.text)
    items = []
    for it in root.findall(".//item"):
        title = clean_text(it.findtext("title",""))
        link  = (it.findtext("link","") or "").strip()
        desc  = clean_text(it.findtext("description",""))
        pub   = (it.findtext("pubDate","") or "").strip()
        items.append({"Forrás": source_name, "Pozíció": title, "Link": link, "Leírás": desc, "Publikálva": pub, "Cég": "", "Lokáció": ""})
    return items

def _json_loads_safe(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None

def extract_company_location_from_html(html: str):
    company = None
    location = None

    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.select("script[type='application/ld+json']"):
            j = _json_loads_safe(tag.string or "")
            if not j:
                continue
            objs = j if isinstance(j, list) else [j]
            for obj in objs:
                if not isinstance(obj, dict):
                    continue
                if obj.get("@type") == "JobPosting":
                    org = obj.get("hiringOrganization") or {}
                    if isinstance(org, dict) and (org.get("name")):
                        company = company or org.get("name")
                    jl = obj.get("jobLocation")
                    jl_list = jl if isinstance(jl, list) else [jl] if isinstance(jl, dict) else []
                    for loc in jl_list:
                        addr = (loc or {}).get("address") or {}
                        parts = [addr.get("addressLocality"), addr.get("addressRegion")]
                        loc_str = ", ".join([p for p in parts if p])
                        if loc_str:
                            location = location or loc_str

    if not (company and location):
        m_items = re.search(r'"items"\s*:\s*(\[[^\]]+\])', html, re.IGNORECASE | re.DOTALL)
        if m_items:
            raw = m_items.group(1)
            raw_json = raw.replace("'", '"')
            arr = _json_loads_safe(raw_json)
            if isinstance(arr, list):
                for it in arr:
                    if not isinstance(it, dict):
                        continue
                    company = company or it.get("affiliation") or it.get("brand") or it.get("seller") or it.get("company")
                    location = location or it.get("location") or it.get("city") or it.get("region")

    if not company:
        m = re.search(r"Hirdető\s*cég\s*:\s*([^,<>\n]+)", html, flags=re.IGNORECASE)
        if m:
            company = m.group(1).strip()

    if not location:
        mloc = re.search(r"(Budapest(?:\s*[IVXLC]+\.?\s*kerület)?|Debrecen|Szeged|Győr|Pécs|Miskolc|Kecskemét|Székesfehérvár|Nyíregyháza|Eger|Veszprém|Szombathely|Sopron|Tatabánya|Pápa|Érd|Budaörs|Pest megye|Bács-Kiskun megye|Fejér megye|Győr-Moson-Sopron megye)", html, flags=re.IGNORECASE)
        if mloc:
            location = mloc.group(1).strip()

    if isinstance(location, str):
        location = location.replace("_", " ").replace("megye", "megye").strip(", ")

    return company, location

def fetch_job_meta(url: str, session: requests.Session = None, retries: int = 2, pause: float = 0.25):
    sess = session or requests.Session()
    last_err = None
    for _ in range(retries + 1):
        try:
            r = sess.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            r.encoding = "utf-8"
            company, location = extract_company_location_from_html(r.text)
            return (company, location)
        except Exception as e:
            last_err = e
            time.sleep(pause)
    return (None, None)

def _json_loads_safe(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None

def extract_company_location_from_html(html: str):
    """
    Próbálkozási sorrend:
      1) JSON-LD (JobPosting)
      2) dataLayer (items[].affiliation / items[].location)
      3) DOM szöveg-fallback („Hirdető cég: …", tipikus location elemek)
    """
    company = None
    location = None

    # 1) JSON-LD
    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.select("script[type='application/ld+json']"):
            j = _json_loads_safe(tag.string or "")
            if not j:
                continue
            objs = j if isinstance(j, list) else [j]
            for obj in objs:
                if not isinstance(obj, dict):
                    continue
                if obj.get("@type") == "JobPosting":
                    org = obj.get("hiringOrganization") or {}
                    if isinstance(org, dict) and (org.get("name")):
                        company = company or org.get("name")
                    jl = obj.get("jobLocation")
                    jl_list = jl if isinstance(jl, list) else [jl] if isinstance(jl, dict) else []
                    for loc in jl_list:
                        addr = (loc or {}).get("address") or {}
                        parts = [addr.get("addressLocality"), addr.get("addressRegion")]
                        loc_str = ", ".join([p for p in parts if p])
                        if loc_str:
                            location = location or loc_str

    # 2) dataLayer (gyors/egyszerű regexekkel)
    if not (company and location):
        # próbáljuk kifogni az items[]-et
        # pl.: "items":[{"affiliation":"4iG Nyrt.","location":"Pest_megye,_Budapest"}]
        m_items = re.search(r'"items"\s*:\s*(\[[^\]]+\])', html, re.IGNORECASE | re.DOTALL)
        if m_items:
            raw = m_items.group(1)
            # próbáljuk JSON kompatibilissé tenni (előfordulhat aposztróf): durva fallback
            raw_json = raw.replace("'", '"')
            arr = _json_loads_safe(raw_json)
            if isinstance(arr, list):
                for it in arr:
                    if not isinstance(it, dict):
                        continue
                    company = company or it.get("affiliation") or it.get("brand") or it.get("seller") or it.get("company")
                    location = location or it.get("location") or it.get("city") or it.get("region")

    # 3) DOM szöveg-fallbackok (regex)
    if not company:
        m = re.search(r"Hirdető\s*cég\s*:\s*([^,<>\n]+)", html, flags=re.IGNORECASE)
        if m:
            company = m.group(1).strip()

    if not location:
        # keressünk tipikus magyar város/megye mintákat az oldal fő tartalmában
        mloc = re.search(r"(Budapest(?:\s*[IVXLC]+\.?\s*kerület)?|Debrecen|Szeged|Győr|Pécs|Miskolc|Kecskemét|Székesfehérvár|Nyíregyháza|Eger|Veszprém|Szombathely|Sopron|Tatabánya|Pápa|Érd|Budaörs|Pest megye|Bács-Kiskun megye|Fejér megye|Győr-Moson-Sopron megye)", html, flags=re.IGNORECASE)
        if mloc:
            location = mloc.group(1).strip()

    # utóformázás
    if isinstance(location, str):
        location = location.replace("_", " ").replace("megye", "megye").strip(", ")

    return company, location

def fetch_job_meta(url: str, session: requests.Session = None, retries: int = 2, pause: float = 0.25):
    sess = session or requests.Session()
    last_err = None
    for _ in range(retries + 1):
        try:
            r = sess.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            r.encoding = "utf-8"
            company, location = extract_company_location_from_html(r.text)
            return (company, location)
        except Exception as e:
            last_err = e
            time.sleep(pause)
    # ha nem sikerült, térjünk vissza None-okkal
    return (None, None)

def parse_company_from_summary(summary: str):
    if not isinstance(summary, str):
        return None
    m = re.search(r"Hirdető\s*cég\s*:\s*([^,|;]+)", summary, flags=re.IGNORECASE)
    return m.group(1).strip() if m else None

# Scraper futtatása háttérben
def run_scraper_async(selected_categories, progress_queue):
    all_rows = []
    seen_links = set()
    
    # Feed lista generálása a kiválasztott kategóriák alapján
    feed_list = [
        ("Profession – IT főfeed", "https://www.profession.hu/partner/files/rss-it.rss"),
        ("Profession – Fejlesztő", "https://www.profession.hu/allasok/1,0,0,fejlesztő?rss"),
        ("Profession – Programozó", "https://www.profession.hu/allasok/1,0,0,programozó?rss"),
        ("Profession – Szoftver", "https://www.profession.hu/allasok/1,0,0,szoftver?rss")
    ]
    
    # Csak a legfontosabb kulcsszavakhoz generálunk feedet (max 3 per kategória)
    for cat_id in selected_categories:
        if cat_id in CATEGORIES:
            keywords = CATEGORIES[cat_id]["keywords"][:3]  # Csak az első 3 kulcsszó
            for keyword in keywords:
                feed_list.append((f"Profession – {keyword}", build_feed_url(keyword)))
    
    sess = requests.Session()
    total_feeds = len(feed_list)
    
    for i, (name, url) in enumerate(feed_list):
        progress_queue.put({"progress": (i / total_feeds) * 100, "status": f"Feldolgozás: {name}"})
        
        try:
            items = fetch_rss_items(name, url)
            progress_queue.put({"debug": f"{name}: {len(items)} állás találva"})
            print(f"DEBUG: {name} - {len(items)} állás")
        except Exception as e:
            progress_queue.put({"error": f"Kihagyva ({name}): {str(e)}"})
            print(f"ERROR: {name} - {str(e)}")
            continue

        for it in items:
            link = it["Link"]
            if not link or link in seen_links:
                continue

            title = it["Pozíció"]
            desc = it["Leírás"]
            if not is_probably_dev(title, desc):
                continue

            company, location = fetch_job_meta(link, session=sess, retries=1, pause=0.2)
            if not company:
                company = parse_company_from_summary(desc)

            seen_links.add(link)
            all_rows.append({
                "id": len(all_rows) + 1,
                "forras": it["Forrás"],
                "pozicio": title,
                "ceg": company or "N/A",
                "lokacio": location or "N/A",
                "link": link,
                "publikalva": it["Publikálva"],
                "lekeres_datuma": datetime.today().strftime("%Y-%m-%d"),
                "leiras": (desc[:200] if isinstance(desc, str) else "")
            })

            time.sleep(0.1)

        time.sleep(0.1)
    
    # Globális változó frissítése
    global scraped_jobs
    scraped_jobs = all_rows
    
    progress_queue.put({
        "progress": 100, 
        "status": "Kész!", 
        "data": all_rows,
        "stats": {
            "total_feeds": total_feeds,
            "total_jobs": len(all_rows),
            "unique_links": len(seen_links)
        }
    })

# API végpontok
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/portals')
def get_portals():
    return jsonify(PORTALS)

@app.route('/api/categories')
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/search', methods=['POST'])
def search_jobs():
    try:
        data = request.json
        selected_categories = data.get('categories', [])
        
        if not selected_categories:
            return jsonify({"error": "Válassz legalább egy kategóriát!"}), 400
        # Scraper futtatása szinkron módon (egyszerűsített verzió)
        all_rows = []
        seen_links = set()
        
        # Csak IT főkategória - duplikáció nélkül, maximalizált lefedettség
        search_queries = []
        
        # IT főkategória - 900+ állás elérése (70+ oldal)
        search_queries.append(("Profession – IT főkategória", "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"))
        
        print(f"[INFO] Csak IT főkategória használata - {len(search_queries)} keresés")
        print(f"[INFO] Cél: 900+ állás elérése duplikáció nélkül")
        print(f"[INFO] Dinamikus oldalszám - automatikusan meghatározza a teljes oldalszámot")
        
        sess = requests.Session()
        
        per_source_kept = defaultdict(int)
        per_source_skipped = defaultdict(int)
        
        total_queries = len(search_queries)
        for i, (name, keyword_or_url) in enumerate(search_queries):
            try:
                # Progress tracking
                progress = (i / total_queries) * 100
                print(f"[STATS] Progress: {progress:.1f}% - {name}")
                
                # URL meghatározása
                if keyword_or_url.startswith("http"):
                    if keyword_or_url.endswith(".rss"):
                        # IT főfeed - RSS
                        url = keyword_or_url
                        items = fetch_rss_items(name, url)
                    else:
                        # HTML scraping - speciális logika IT főoldalhoz
                        url = keyword_or_url
                        # Dinamikus oldalszám - automatikusan meghatározza a teljes oldalszámot
                        items = fetch_html_jobs(name, url)
                else:
                    # Kulcsszavas keresés - HTML scraping (dinamikus oldalszám)
                    url = f"https://www.profession.hu/allasok/1,0,0,{quote(keyword_or_url, safe='')}"
                    # Dinamikus oldalszám - automatikusan meghatározza a teljes oldalszámot
                    items = fetch_html_jobs(name, url)
                print(f"[SEARCH] {name} - {len(items)} állás")
                
                # Debug: első néhány link ellenőrzése
                if items:
                    sample_links = [item["Link"] for item in items[:3]]
                    print(f"   Sample links: {sample_links}")
                    print(f"   [STATS] Eredeti állások száma: {len(items)}")
                    if "it-programozas-fejlesztes" in url:
                        print(f"   [TARGET] IT főkategória - dinamikus oldalszám meghatározás")
                    elif "python" in url.lower():
                        print(f"   [PYTHON] Python keresés - várható ~180 állás (15 oldal)")
                else:
                    print(f"   [WARNING] Nincs állás ebben a feed-ben: {url}")
                
                kept = 0
                skipped = 0
                
                for it in items:
                    link = it["Link"]
                    if not link:
                        skipped += 1
                        continue

                    # Duplikáció ellenőrzés - clean link alapján (session paramétereket eltávolítjuk)
                    clean_link = link.split('?')[0]  # Eltávolítjuk a query paramétereket
                    if clean_link in seen_links:
                        skipped += 1
                        continue

                    title = it["Pozíció"]
                    desc = it["Leírás"]
                    if not is_probably_dev(title, desc):
                        skipped += 1
                        continue

                    # HTML scraping-ből már van cég és lokáció
                    company = it.get("Cég", "") or parse_company_from_summary(desc) or "N/A"
                    location = it.get("Lokáció", "") or "N/A"
                    
                    # Dátum információk
                    pub_date_iso = it.get("Publikálva_dátum", "")
                    is_fresh = it.get("Friss_állás", False)

                    seen_links.add(clean_link)
                    all_rows.append({
                        "id": len(all_rows) + 1,
                        "forras": it["Forrás"],
                        "pozicio": title,
                        "ceg": company or "N/A",
                        "lokacio": location or "N/A",
                        "link": link,  # Eredeti linket tároljuk
                        "publikalva": it["Publikálva"],
                        "publikalva_datum": pub_date_iso or datetime.today().strftime("%Y-%m-%d"),
                        "friss_allas": is_fresh,
                        "lekeres_datuma": datetime.today().strftime("%Y-%m-%d"),
                        "leiras": (desc[:200] if isinstance(desc, str) else "")
                    })
                    kept += 1

                    # Gyors mód: nincs delay (teszteléshez)
                    # time.sleep(0.15)

                per_source_kept[name] = kept
                per_source_skipped[name] = skipped
                
                print(f"   [SUCCESS] Megtartva: {kept}, Kihagyva: {skipped}")
                
                # Debug: részletes szűrési statisztikák
                if items:
                    print(f"   [STATS] Feldolgozott: {len(items)} állás")
                    print(f"   [LINKS] Egyedi linkek: {len(seen_links)}")
                    print(f"   [SUCCESS] Megtartva: {kept}")
                    print(f"   [ERROR] Kihagyva: {skipped}")
                    if skipped > 0:
                        print(f"   [INFO] Kihagyás okai: duplikáció vagy nem fejlesztői")
                elif skipped > kept:
                    print(f"   [WARNING] Sok duplikáció - valószínűleg ugyanazok az állások különböző kulcsszavakkal")
                
                # Progress mentés (ha megszakad, legalább ezek megmaradnak)
                if len(all_rows) > 0:
                    global scraped_jobs
                    scraped_jobs = all_rows
                    print(f"[SAVED] Mentett állások: {len(all_rows)} (folyamatban)")
                    print(f"[STATS] Progress: {((i+1) / total_queries) * 100:.1f}% - {len(all_rows)} állás eddig")
                
                # Kímélet a szerver felé (feedek között - csökkentett delay)
                time.sleep(2.0)

            except Exception as e:
                print(f"[WARNING] Kihagyva ({name}): {str(e)}")
                print(f"   Error type: {type(e).__name__}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                continue
        
        # Globális változó frissítése
        scraped_jobs = all_rows
        
        # Progress mentés (ha megszakad, legalább ezek megmaradnak)
        print(f"[SAVED] Mentett állások: {len(all_rows)}")
        
        print(f"\n[SUCCESS] {len(all_rows)} fejlesztői állás találva, {len(search_queries)} kulcsszóval")
        print(f"[TOTAL] Összesen {len(seen_links)} egyedi állás link")
        print(f"[TARGET] VISSZAADOTT ÁLLÁSOK: {len(all_rows)} (összes)")
        
        # Top források statisztikája
        print("\n[STATS] Forrásösszegzés (megtartott / kihagyott):")
        sorted_sources = sorted(per_source_kept.items(), key=lambda x: x[1], reverse=True)[:15]
        for name, kept in sorted_sources:
            print(f"  • {name}: {kept} / {per_source_skipped[name]}")
        
        # Duplikáció statisztikák
        total_processed = sum(per_source_kept.values()) + sum(per_source_skipped.values())
        total_duplicates = sum(per_source_skipped.values())
        duplicate_rate = (total_duplicates / total_processed * 100) if total_processed > 0 else 0
        print(f"\n[DUP] Duplikáció arány: {duplicate_rate:.1f}% ({total_duplicates}/{total_processed})")
        
        return jsonify({
            "message": "Turbó keresés befejezve", 
            "total_jobs": len(all_rows),
            "total_searches": len(search_queries),
            "unique_links": len(seen_links),
            "top_sources": dict(sorted_sources),
            "jobs": all_rows  # Összes állás
        })
        
    except Exception as e:
        error_message = f"Keresési hiba: {str(e)}"
        print(f"SEARCH ERROR: {error_message}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_message, "type": type(e).__name__}), 500

@app.route('/api/progress')
def get_progress():
    # Egyszerűsített progress - valós implementációban session/task ID kellene
    return jsonify({"progress": 0, "status": "Keresés..."})

@app.route('/api/search/new', methods=['POST'])
def search_new_jobs():
    """Csak az új állások keresése (ma publikáltak)"""
    try:
        data = request.json
        selected_categories = data.get('categories', [])
        
        if not selected_categories:
            return jsonify({"error": "Válassz legalább egy kategóriát!"}), 400
        
        # Ugyanaz a keresési logika, mint a normál keresésben
        all_rows = []
        seen_links = set()
        
        # Csak IT főkategória - duplikáció nélkül, maximalizált lefedettség
        search_queries = []
        search_queries.append(("Profession – IT főkategória", "https://www.profession.hu/allasok/it-programozas-fejlesztes/1,10"))
        
        print(f"[INFO] Új állások keresése - {len(search_queries)} keresés")
        
        sess = requests.Session()
        per_source_kept = defaultdict(int)
        per_source_skipped = defaultdict(int)
        
        total_queries = len(search_queries)
        for i, (name, keyword_or_url) in enumerate(search_queries):
            try:
                # Progress tracking
                progress = (i / total_queries) * 100
                print(f"[STATS] Progress: {progress:.1f}% - {name}")
                
                # URL meghatározása
                if keyword_or_url.startswith("http"):
                    url = keyword_or_url
                    items = fetch_html_jobs(name, url)
                else:
                    url = f"https://www.profession.hu/allasok/1,0,0,{quote(keyword_or_url, safe='')}"
                    items = fetch_html_jobs(name, url)
                
                print(f"[SEARCH] {name} - {len(items)} állás")
                
                kept = 0
                skipped = 0
                today = datetime.today().strftime("%Y-%m-%d")
                
                for it in items:
                    link = it["Link"]
                    if not link:
                        skipped += 1
                        continue

                    # Duplikáció ellenőrzés
                    clean_link = link.split('?')[0]
                    if clean_link in seen_links:
                        skipped += 1
                        continue

                    title = it["Pozíció"]
                    desc = it["Leírás"]
                    if not is_probably_dev(title, desc):
                        skipped += 1
                        continue

                    # ÚJ SZŰRÉS: Csak a mai állások
                    pub_date_iso = it.get("Publikálva_dátum", "")
                    is_fresh = it.get("Friss_állás", False)
                    
                    if not (pub_date_iso == today or is_fresh):
                        skipped += 1
                        continue

                    # HTML scraping-ből már van cég és lokáció
                    company = it.get("Cég", "") or parse_company_from_summary(desc) or "N/A"
                    location = it.get("Lokáció", "") or "N/A"

                    seen_links.add(clean_link)
                    all_rows.append({
                        "id": len(all_rows) + 1,
                        "forras": it["Forrás"],
                        "pozicio": title,
                        "ceg": company or "N/A",
                        "lokacio": location or "N/A",
                        "link": link,
                        "publikalva": it["Publikálva"],
                        "publikalva_datum": pub_date_iso or today,
                        "friss_allas": is_fresh,
                        "lekeres_datuma": today,
                        "leiras": (desc[:200] if isinstance(desc, str) else "")
                    })
                    kept += 1

                per_source_kept[name] = kept
                per_source_skipped[name] = skipped
                
                print(f"   [SUCCESS] Új állások: {kept}, Kihagyva: {skipped}")
                
                # Progress mentés
                if len(all_rows) > 0:
                    global scraped_jobs
                    scraped_jobs = all_rows
                    print(f"[SAVED] Mentett új állások: {len(all_rows)} (folyamatban)")
                
                time.sleep(2.0)

            except Exception as e:
                print(f"[WARNING] Kihagyva ({name}): {str(e)}")
                continue
        
        # Globális változó frissítése
        scraped_jobs = all_rows
        
        print(f"\n[SUCCESS] {len(all_rows)} új állás találva")
        print(f"[TOTAL] Összesen {len(seen_links)} egyedi új állás link")
        
        return jsonify({
            "message": "Új állások keresése befejezve", 
            "total_jobs": len(all_rows),
            "total_searches": len(search_queries),
            "unique_links": len(seen_links),
            "jobs": all_rows
        })
        
    except Exception as e:
        error_message = f"Új állások keresési hiba: {str(e)}"
        print(f"NEW JOBS SEARCH ERROR: {error_message}")
        return jsonify({"error": error_message}), 500

# Globális változó a scraped adatok tárolásához
scraped_jobs = []

@app.route('/api/jobs')
def get_jobs():
    # Visszaadjuk a scraped állásokat
    return jsonify(scraped_jobs)

@app.route('/api/export/excel')
def export_excel():
    """Excel export endpoint"""
    try:
        if not scraped_jobs:
            return jsonify({"error": "Nincsenek adatok az exportáláshoz"}), 400
        
        # Excel fájl létrehozása
        wb = create_excel_export(scraped_jobs)
        
        # Excel fájl memóriába írása
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Response küldése
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'it_allasok_{datetime.today().strftime("%Y-%m-%d")}.xlsx'
        )
        
    except Exception as e:
        print(f"Excel export hiba: {e}")
        return jsonify({"error": f"Excel export hiba: {str(e)}"}), 500

@app.route('/api/export/excel/filtered')
def export_excel_filtered():
    """Szűrt Excel export endpoint"""
    try:
        if not scraped_jobs:
            return jsonify({"error": "Nincsenek adatok az exportáláshoz"}), 400
        
        # Szűrési paraméterek
        search = request.args.get('search', '')
        location = request.args.get('location', '')
        company = request.args.get('company', '')
        salary = request.args.get('salary', '')
        work_type = request.args.get('work_type', '')
        
        # Szűrt adatok
        filtered_jobs = []
        for job in scraped_jobs:
            # Szűrési logika
            matches = True
            
            if search:
                search_lower = search.lower()
                if not (search_lower in (job.get('pozicio', '') or '').lower() or 
                       search_lower in (job.get('ceg', '') or '').lower()):
                    matches = False
            
            if location and matches:
                if location not in (job.get('lokacio', '') or ''):
                    matches = False
            
            if company and matches:
                if company not in (job.get('ceg', '') or ''):
                    matches = False
            
            if matches:
                filtered_jobs.append(job)
        
        if not filtered_jobs:
            return jsonify({"error": "Nincsenek szűrt adatok az exportáláshoz"}), 400
        
        # Excel fájl létrehozása
        wb = create_excel_export(filtered_jobs)
        
        # Excel fájl memóriába írása
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Response küldése
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'it_allasok_szurt_{datetime.today().strftime("%Y-%m-%d")}.xlsx'
        )
        
    except Exception as e:
        print(f"Szűrt Excel export hiba: {e}")
        return jsonify({"error": f"Szűrt Excel export hiba: {str(e)}"}), 500

@app.route('/api/status')
def get_status():
    """Visszaadja a jelenlegi állapotot"""
    global scraped_jobs
    return jsonify({
        "total_jobs": len(scraped_jobs),
        "status": "ready" if scraped_jobs else "no_data"
    })

@app.route('/api/test')
def test_endpoint():
    """Egyszerű test endpoint"""
    return jsonify({"message": "API működik!", "timestamp": datetime.now().isoformat()})

@app.route('/api/debug')
def debug_endpoint():
    """Debug endpoint - jelenlegi állapot"""
    global scraped_jobs
    return jsonify({
        "scraped_jobs_count": len(scraped_jobs),
        "last_update": datetime.now().isoformat(),
        "sample_jobs": scraped_jobs[:5] if scraped_jobs else []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
