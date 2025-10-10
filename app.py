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
BASE = "https://www.profession.hu/allasok/1,0,0,{}?rss"

# Kategóriák definiálása - legnépszerűbb fejlesztői területek
CATEGORIES = {
    "java": {"name": "Java", "keywords": ["java", "spring", "spring boot", "maven", "gradle", "hibernate", "jpa", "microservices", "jakarta", "junit", "mockito"]},
    "javascript": {"name": "JavaScript", "keywords": ["javascript", "js", "node.js", "nodejs", "express", "npm", "yarn", "webpack", "babel", "es6", "typescript", "ts"]},
    "python": {"name": "Python", "keywords": ["python", "django", "flask", "fastapi", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "celery", "redis"]},
    "php": {"name": "PHP", "keywords": ["php", "laravel", "symfony", "composer", "wordpress", "drupal", "magento", "codeigniter", "yii", "phalcon"]},
    "react": {"name": "React", "keywords": ["react", "reactjs", "redux", "next.js", "nextjs", "gatsby", "jsx", "hooks", "context", "router"]},
    "angular": {"name": "Angular", "keywords": ["angular", "angularjs", "rxjs", "ngrx", "typescript", "material", "cli", "universal", "ivy"]},
    "vue": {"name": "Vue.js", "keywords": ["vue", "vuejs", "nuxt", "nuxtjs", "vuex", "pinia", "composition api", "vite", "quasar"]},
    "devops": {"name": "DevOps", "keywords": ["devops", "docker", "kubernetes", "jenkins", "gitlab", "github actions", "terraform", "ansible", "aws", "azure", "gcp"]},
    "dotnet": {"name": ".NET", "keywords": [".net", "dotnet", "c#", "csharp", "asp.net", "entity framework", "blazor", "xamarin", "maui", "core"]},
    "mobile": {"name": "Mobile", "keywords": ["android", "ios", "flutter", "react native", "swift", "kotlin", "xamarin", "ionic", "cordova", "pwa"]},
    "data": {"name": "Data & AI", "keywords": ["data scientist", "machine learning", "ai", "big data", "sql", "postgresql", "mysql", "mongodb", "elasticsearch", "kafka"]},
    "testing": {"name": "Testing", "keywords": ["qa", "test automation", "selenium", "cypress", "jest", "junit", "pytest", "sdet", "performance testing", "api testing"]}
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

def fetch_rss_items(source_name: str, url: str):
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
        items.append({"Forrás": source_name, "Pozíció": title, "Link": link, "Leírás": desc, "Publikálva": pub})
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
    feed_list = [("Profession – IT főfeed", "https://www.profession.hu/partner/files/rss-it.rss")]
    
    for cat_id in selected_categories:
        if cat_id in CATEGORIES:
            for keyword in CATEGORIES[cat_id]["keywords"]:
                feed_list.append((f"Profession – {keyword}", build_feed_url(keyword)))
    
    sess = requests.Session()
    total_feeds = len(feed_list)
    
    for i, (name, url) in enumerate(feed_list):
        progress_queue.put({"progress": (i / total_feeds) * 100, "status": f"Feldolgozás: {name}"})
        
        try:
            items = fetch_rss_items(name, url)
        except Exception as e:
            progress_queue.put({"error": f"Kihagyva ({name}): {str(e)}"})
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
    
    progress_queue.put({"progress": 100, "status": "Kész!", "data": all_rows})

# API végpontok
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories')
def get_categories():
    return jsonify(CATEGORIES)

@app.route('/api/search', methods=['POST'])
def search_jobs():
    data = request.json
    selected_categories = data.get('categories', [])
    
    if not selected_categories:
        return jsonify({"error": "Válassz legalább egy kategóriát!"}), 400
    
    # Progress queue a valós idejű frissítésekhez
    progress_queue = queue.Queue()
    
    # Scraper indítása háttérben
    thread = threading.Thread(target=run_scraper_async, args=(selected_categories, progress_queue))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Keresés elindítva", "task_id": "search_1"})

@app.route('/api/progress')
def get_progress():
    # Egyszerűsített progress - valós implementációban session/task ID kellene
    return jsonify({"progress": 0, "status": "Keresés..."})

@app.route('/api/jobs')
def get_jobs():
    # Itt visszaadnánk a megtalált állásokat
    # Valós implementációban adatbázisból vagy cache-ből
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
