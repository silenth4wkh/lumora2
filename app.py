from flask import Flask, request, jsonify, render_template
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

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

app = Flask(__name__)
CORS(app)

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
    s = re.sub(r"<.*?>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def build_feed_url(keyword: str) -> str:
    return BASE.format(quote(keyword, safe=""))

def is_probably_dev(title: str, desc: str) -> bool:
    t = (title or "").lower()
    d = (desc or "").lower()
    if any(bad in t for bad in EXCLUDE_PHRASES) or any(bad in d for bad in EXCLUDE_PHRASES):
        return False
    return True

def fetch_html_jobs(source_name: str, url: str, max_pages: int = 5):
    """HTML scraping a Profession.hu álláslistákról - több oldal feldolgozása"""
    if not BeautifulSoup:
        print("BeautifulSoup nincs telepítve, RSS fallback használata")
        return fetch_rss_fallback(source_name, url)
    
    all_items = []
    
    for page in range(1, max_pages + 1):
        try:
            # Oldalszámozás hozzáadása
            page_url = f"{url}&page={page}" if "?" in url else f"{url}?page={page}"
            
            r = requests.get(page_url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            r.encoding = "utf-8"
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Keresés ul.job-cards > li elemekben
            job_cards = soup.select("ul.job-cards li")
            if not job_cards:
                # Fallback: más lehetséges szelektorok
                job_cards = soup.select(".job-card, .job-item, .listing-item, .search-result-item")
            
            print(f"DEBUG: {source_name} - Oldal {page}: {len(job_cards)} job card")
            
            if not job_cards:
                # Ha nincs több állás, szakítsuk meg
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
                    
                    # Cég neve
                    company_elem = card.select_one(".company, .employer, .company-name, .job-company")
                    company = clean_text(company_elem.get_text()) if company_elem else ""
                    
                    # Lokáció
                    location_elem = card.select_one(".location, .job-location, .city, .place")
                    location = clean_text(location_elem.get_text()) if location_elem else ""
                    
                    # Leírás
                    desc_elem = card.select_one(".description, .job-description, .summary, .excerpt")
                    desc = clean_text(desc_elem.get_text()) if desc_elem else ""
                    
                    # Dátum
                    date_elem = card.select_one(".date, .published, .job-date, .time")
                    pub_date = clean_text(date_elem.get_text()) if date_elem else ""
                    
                    if title and link:
                        all_items.append({
                            "Forrás": source_name, 
                            "Pozíció": title, 
                            "Link": link, 
                            "Leírás": desc,
                            "Publikálva": pub_date,
                            "Cég": company,
                            "Lokáció": location
                        })
                        
                except Exception as e:
                    print(f"ERROR parsing job card: {e}")
                    continue
            
            # Kímélet a szerver felé
            time.sleep(0.5)
            
        except Exception as e:
            print(f"ERROR fetching page {page}: {e}")
            break
    
    print(f"DEBUG: {source_name} - Összesen {len(all_items)} állás {max_pages} oldalról")
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
    data = request.json
    selected_categories = data.get('categories', [])
    
    if not selected_categories:
        return jsonify({"error": "Válassz legalább egy kategóriát!"}), 400
    
    try:
        # Scraper futtatása szinkron módon (egyszerűsített verzió)
        all_rows = []
        seen_links = set()
        
        # Turbó kulcsszavas keresés - minden kulcsszóhoz külön keresés
        search_queries = []
        
        # Alap IT főfeed
        search_queries.append(("Profession – IT főfeed", "https://www.profession.hu/partner/files/rss-it.rss"))
        
        # HTML scraping - csak a legfontosabb kulcsszavak
        priority_keywords = [
            # Legfontosabb területek (kevesebb duplikáció)
            "fejlesztő", "programozó", "szoftver", "szoftvermérnök", "rendszermérnök",
            "frontend", "backend", "full stack", "devops", "data scientist", "mobile"
        ]
        
        for keyword in priority_keywords:
            if keyword in ALL_KEYWORDS:
                # HTML scraping URL (nem RSS)
                search_queries.append((f"Profession – {keyword}", f"https://www.profession.hu/allasok/1,0,0,{quote(keyword, safe='')}"))
        
        # Alternatív megközelítés: teljesen különböző keresések
        alternative_searches = [
            # Különböző pozíciók
            ("Profession – IT Manager", "https://www.profession.hu/allasok/1,0,0,it%20manager"),
            ("Profession – System Admin", "https://www.profession.hu/allasok/1,0,0,rendszergazda"),
            ("Profession – Database", "https://www.profession.hu/allasok/1,0,0,adatbázis"),
            ("Profession – Network", "https://www.profession.hu/allasok/1,0,0,hálózat"),
            ("Profession – Security", "https://www.profession.hu/allasok/1,0,0,biztonság"),
            # Különböző technológiák
            ("Profession – Docker", "https://www.profession.hu/allasok/1,0,0,docker"),
            ("Profession – Kubernetes", "https://www.profession.hu/allasok/1,0,0,kubernetes"),
            ("Profession – AWS", "https://www.profession.hu/allasok/1,0,0,aws"),
            ("Profession – Azure", "https://www.profession.hu/allasok/1,0,0,azure"),
            ("Profession – SQL", "https://www.profession.hu/allasok/1,0,0,sql")
        ]
        
        for name, url in alternative_searches:
            search_queries.append((name, url))
        
        print(f"🔍 Összesen {len(search_queries)} kulcsszavas keresés + IT főfeed")
        print(f"📝 Kulcsszavak: {len(ALL_KEYWORDS)} egyedi kulcsszó")
        
        sess = requests.Session()
        
        per_source_kept = defaultdict(int)
        per_source_skipped = defaultdict(int)
        
        total_queries = len(search_queries)
        for i, (name, keyword_or_url) in enumerate(search_queries):
            try:
                # Progress tracking
                progress = (i / total_queries) * 100
                print(f"📊 Progress: {progress:.1f}% - {name}")
                
                # URL meghatározása
                if keyword_or_url.startswith("http"):
                    if keyword_or_url.endswith(".rss"):
                        # IT főfeed - RSS
                        url = keyword_or_url
                        items = fetch_rss_items(name, url)
                    else:
                        # HTML scraping
                        url = keyword_or_url
                        items = fetch_html_jobs(name, url)
                else:
                    # Kulcsszavas keresés - HTML scraping
                    url = f"https://www.profession.hu/allasok/1,0,0,{quote(keyword_or_url, safe='')}"
                    items = fetch_html_jobs(name, url)
                print(f"🔎 {name} - {len(items)} állás")
                
                # Debug: első néhány link ellenőrzése
                if items:
                    sample_links = [item["Link"] for item in items[:3]]
                    print(f"   Sample links: {sample_links}")
                else:
                    print(f"   ⚠️ Nincs állás ebben a feed-ben: {url}")
                
                kept = 0
                skipped = 0
                
                for it in items:
                    link = it["Link"]
                    if not link:
                        skipped += 1
                        continue

                    # Csak a teljes link alapján duplikáció ellenőrzés (nem a session paraméterek miatt)
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

                    seen_links.add(clean_link)
                    all_rows.append({
                        "id": len(all_rows) + 1,
                        "forras": it["Forrás"],
                        "pozicio": title,
                        "ceg": company or "N/A",
                        "lokacio": location or "N/A",
                        "link": link,  # Eredeti linket tároljuk
                        "publikalva": it["Publikálva"],
                        "lekeres_datuma": datetime.today().strftime("%Y-%m-%d"),
                        "leiras": (desc[:200] if isinstance(desc, str) else "")
                    })
                    kept += 1

                    # Gyors mód: nincs delay (teszteléshez)
                    # time.sleep(0.15)

                per_source_kept[name] = kept
                per_source_skipped[name] = skipped
                
                print(f"   ✅ Megtartva: {kept}, Kihagyva: {skipped}")
                
                # Debug: duplikáció statisztikák
                if kept > 0:
                    print(f"   📊 Duplikációk: {skipped} (összesen {len(seen_links)} egyedi link)")
                    if skipped > kept:
                        print(f"   ⚠️ Sok duplikáció - valószínűleg ugyanazok az állások különböző kulcsszavakkal")
                
                # Kímélet a szerver felé (feedek között)
                time.sleep(0.15)

            except Exception as e:
                print(f"⚠️ Kihagyva ({name}): {str(e)}")
                continue
        
        # Globális változó frissítése
        global scraped_jobs
        scraped_jobs = all_rows
        
        print(f"\n✅ {len(all_rows)} fejlesztői állás találva, {len(search_queries)} kulcsszóval")
        
        # Top források statisztikája
        print("\n📊 Forrásösszegzés (megtartott / kihagyott):")
        sorted_sources = sorted(per_source_kept.items(), key=lambda x: x[1], reverse=True)[:10]
        for name, kept in sorted_sources:
            print(f"  • {name}: {kept} / {per_source_skipped[name]}")
        
        return jsonify({
            "message": "Turbó keresés befejezve", 
            "total_jobs": len(all_rows),
            "total_searches": len(search_queries),
            "unique_links": len(seen_links),
            "top_sources": dict(sorted_sources),
            "jobs": all_rows[:20]  # Első 20 állás
        })
        
    except Exception as e:
        return jsonify({"error": f"Hiba a keresés során: {str(e)}"}), 500

@app.route('/api/progress')
def get_progress():
    # Egyszerűsített progress - valós implementációban session/task ID kellene
    return jsonify({"progress": 0, "status": "Keresés..."})

# Globális változó a scraped adatok tárolásához
scraped_jobs = []

@app.route('/api/jobs')
def get_jobs():
    # Visszaadjuk a scraped állásokat
    return jsonify(scraped_jobs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
