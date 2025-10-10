# MASTER PROMPT — n8n (HU IT állások → Excel)

## Követelmény
Az összes transzformáció, normalizálás, kategorizálás, deduplikáció **Python Code node-okban** készüljön (stdlib-re támaszkodva). **NE használj JS Function node-ot.**

## Cél
Napi ütemezéssel gyűjtsd össze a magyar állásportálok IT hirdetéseit, normalizáld, deduplikáld, és írd XLSX-be (+ opcionális Google Sheets). Csak új / módosult tételek kerüljenek a napi sheetre.

## Források (1. kör)
- **profession.hu** — IT kategória
- **nofluffjobs.com/hu** — HU régió  
- **cvonline.hu** — IT
- **jobline.hu** — IT
- **worki.hu / work.hu** — ha van IT
- **dreamjobs.hu** — IT állások
- (+ nagyvállalati karrieroldalak később)

**Elv**: ahol lehet, használj RSS/API/kereső URL-t; különben HTTP Request → HTML Extract (CSS selector).

## Ütemezés
- **Cron**: minden nap 06:30 Europe/Budapest
- **Manual Trigger** teszthez

## Folyamat (node-szintű terv)

### 1. Trigger
- **Cron Trigger** (0 30 6 * * * Europe/Budapest)
- **Manual Trigger** (teszteléshez)

### 2. Forrás-loop (forrásonként sub-workflow)
- **HTTP Request** (GET, User-Agent fejléccel, lapozás kezelése)
- **HTML Extract** vagy **RSS Read** (forrás típusától függően)
- **Set** (forrás meta: source, source_url, scraped_at)

### 3. Python: nyers → strukturált
**Code (Python) node**: HTML/RSS rekordokból dict-et állít elő:
```python
{
    'job_title_raw': str,
    'job_title_norm': str,
    'company_name': str,
    'location_city': str,
    'location_country': str,
    'description_raw': str,
    'salary_raw': str,
    'employment_type': str,
    'posted_at': str,
    'valid_until': str,
    'apply_url': str,
    'benefits_raw': str
}
```

### 4. Python: normalizálás + kategorizálás
**Code (Python) node**:
- **cím normalizálás** (job_title_norm)
- **role_category** (DevOps, Backend, Frontend, Full-stack, Data/ML, QA, Mobile, Security, Cloud, PM/PO, BA, UI/UX, SysAdmin/IT Ops, Embedded, Game, ERP/CRM, Support, Network, DBA) — kulcsszó-mátrix alapján
- **seniority** (junior/medior/senior/lead/principal) — regex
- **work_model** (remote/hybrid/on-site) — regex
- **salary_*** (min/max/currency/gross/net) — tartomány-felismerés
- **must_have_stack** / **nice_to_have_stack** (tech kulcsszók)
- **languages** (HU/EN/DE + szint ha van)
- **description_excerpt** (HTML-tlanított, max 300 char)

### 5. Python: deduplikáció kulcs
**Code (Python) node**: 
```python
hash_id = sha256(f"{company_name}|{job_title_norm}|{location_city}|{role_category}".lower())
```

### 6. Master beolvasása (ha Excel/Sheets)
- **Spreadsheet File (Read)** vagy **Google Sheets (Read)** → meglévő hash_id lista

### 7. Python: újak/updated szűrése
**Code (Python) node**: diff a master ellen; ha ugyanaz a hash, de bér/időpont változott → updated = True

### 8. Kiírás
- **Spreadsheet File (XLSX)**:
  - master sheet: Upsert hash_id alapján
  - daily_YYYY-MM-DD sheet: csak új/updated Append
- (opcionális) **Google Sheets Upsert**

### 9. Összefoglaló
**Email (SMTP)**: új/updated számok, források, csatolmányként napi XLSX

### 10. Hibakezelés
- **Error Trigger** → Slack/Discord webhook
- Rate-limit: HTTP kérések között 300–800 ms, page-loop 1–2 s
- Tartsd be a források TOS-át

## Táblastruktúra (Excel/Sheets oszlopok, fix sorrend)
1. source
2. source_url  
3. scraped_at (ISO)
4. job_title_raw
5. job_title_norm
6. role_category
7. seniority
8. employment_type (full-time/part-time/contract)
9. work_model (remote/hybrid/on-site)
10. location_city
11. location_country (HU)
12. company_name
13. company_type (vállalat/ügynökség/toborzó, ha kinyerhető)
14. salary_raw
15. salary_min
16. salary_max
17. salary_currency
18. salary_gross_net
19. contract_type (állandó/B2B/alvállalkozó)
20. benefits_raw
21. benefits_parsed (cafeteria, biztosítás, képzés, bónusz, ESOP…)
22. must_have_stack
23. nice_to_have_stack
24. languages
25. posted_at
26. valid_until
27. apply_url
28. description_excerpt
29. hash_id

## Python Code node – irányelvek (minták stdlibbel)

### Senioritás + munkamodell + bér regexek:
```python
import re, hashlib, html, datetime as dt

def seniority_of(text):
    t = text.lower()
    if re.search(r'\b(junior|kezd[őo]|pályakezd[őo])\b', t): return 'junior'
    if re.search(r'\b(medior|középhalad[óo]|3-5\s*év)\b', t): return 'medior'
    if re.search(r'\b(senior|tapasztalt|5\+?\s*év)\b', t): return 'senior'
    if re.search(r'\b(lead|principal|architect|vezet[őo])\b', t): return 'lead'
    return 'unspecified'

def work_model_of(text):
    t = text.lower()
    if re.search(r'\b(remote|táv|home\s*office)\b', t): return 'remote'
    if re.search(r'\b(hibrid|hybrid)\b', t): return 'hybrid'
    return 'on-site'

def salary_parse(text):
    t = text.replace('.', '').replace(' ', '')
    m = re.search(r'(\d{4,6})(?:-(\d{4,6}))?\s*(huf|ft|eur)', t, re.I)
    if not m: return (None, None, None, 'unknown')
    ccy = m.group(3).upper().replace('FT','HUF')
    mn = int(m.group(1)); mx = int(m.group(2) or m.group(1))
    grossnet = 'gross' if re.search(r'\b(brutt[óo]|gross)\b', text, re.I) else ('net' if re.search(r'\b(nett[óo]|net)\b', text, re.I) else 'unknown')
    return (mn, mx, ccy, grossnet)

def hash_id(company, title_norm, city, role):
    key = f"{(company or '').lower()}|{(title_norm or '').lower()}|{(city or '').lower()}|{(role or '').lower()}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()
```

### Role-kategorizálás (részlet – bővíthető dict):
```python
ROLE_MAP = {
    'DevOps': [r'\bdev[-\s]?ops\b', r'kubernetes', r'terraform', r'ci/?cd'],
    'Backend': [r'\bbackend\b', r'\b(java|kotlin|c#|\.net|python|go|php|node)\b'],
    'Frontend': [r'\bfront[-\s]?end\b', r'(react|angular|vue|typescript)'],
    'Full-stack': [r'\bfull[-\s]?stack\b'],
    'Data/ML': [r'\b(data\s(engineer|scientist)|machine\slearning|ml|spark|hadoop)\b'],
    'QA/Testing': [r'\bqa|test(er|ing)|cypress|selenium|playwright\b'],
    'Mobile': [r'\b(android|ios|flutter|react\s?native)\b'],
    'Security': [r'\b(security|secops|soc|siem)\b'],
    'Cloud': [r'\b(aws|azure|gcp)\b'],
    'UI/UX': [r'\b(ui|ux|product\sdesigner)\b'],
    # …
}

def role_of(text):
    t = text.lower()
    for role, pats in ROLE_MAP.items():
        if any(re.search(p, t) for p in pats): return role
    return 'Other'
```

### Stack-kulcsszavak (MUST/NICE) – rövid minta:
```python
MUST = ['java','python','go','c#','.net','php','node','react','angular','vue','typescript','kubernetes','docker','aws','azure','gcp','terraform','ansible','kafka','spark','sql','nosql','linux','git','ci/cd']

def extract_stack(text):
    t = text.lower()
    hits = [kw for kw in MUST if kw in t]
    return sorted(set(hits))
```

### Diff a master ellen:
```python
# inputs[0] = scraped items; inputs[1] = master rows
existing = {row['hash_id']: row for row in items_input_2}  # master
out_new, out_updated = [], []
for it in items_input_1:
    hid = it['hash_id']
    if hid not in existing:
        out_new.append(it)
    else:
        changed = any(it.get(k) != existing[hid].get(k) for k in ('salary_min','salary_max','posted_at'))
        if changed:
            it['updated'] = True
            out_updated.append(it)
```

**Megjegyzés**: ha olyan feladat jön, amihez 3rd-party py csomag kell (pl. fejlettebb NLP), akkor használj **Execute Command node-ot**, egy előkészített venv-ből (`python -m venv venv && venv/bin/pip install …`), és onnan olvasd vissza az eredményt JSON-ként.

## Kimenet (XLSX + Sheets)
- **Fájl**: `/data/it_jobs_master.xlsx`
  - master (Upsert hash_id alapján)
  - daily_YYYY-MM-DD (Append csak új/updated)
- **Opcionális**: Google Sheets Upsert ugyanilyen oszloprenddel

## Jelentés
**SMTP email**: 
- tárgy: „IT állások – napi összesítő {{date}}"
- törzs: új/updated darabszám, forráslisták, hibák
- csatolmány: napi sheet

## Hibakezelés, etikett
- Források TOS tisztelete, terhelés kímélése (rate limit, random delay)
- Csak publikus adatok, PII nélkül
- Minden rekordhoz source + source_url

## Elfogadási kritériumok
- Napi Cron fut, kézzel is indítható
- Python Code node-ok végzik a parse/normalize/dedupe lépéseket
- Deduplikáció stabil hash_id szerint; változásra upsert
- XLSX/Sheets kimenet fix oszloprenddel
- Email összefoglaló + hiba-értesítés
