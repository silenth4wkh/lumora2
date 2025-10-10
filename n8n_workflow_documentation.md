# n8n IT Jobs Scraper Workflow Dokumentáció

## Áttekintés
Ez az n8n workflow napi ütemezéssel gyűjti össze a magyar állásportálok IT hirdetéseit, normalizálja, deduplikálja és Excel fájlokba írja ki az adatokat.

## Workflow Struktúra

### 1. Trigger Node-ok
- **Daily Cron Trigger**: Minden nap 06:30-kor fut (Europe/Budapest időzóna)
- **Manual Trigger**: Teszteléshez használható

### 2. Adatgyűjtés
- **Job Sources**: Forrásportálok listája (profession.hu, nofluffjobs.com, cvonline.hu, jobline.hu, worki.hu, dreamjobs.hu)
- **HTTP Request**: Weboldalak lekérése User-Agent fejléccel
- **HTML Extract**: CSS selectorokkal történő adatkinyerés
- **Add Source Meta**: Forrás metaadatok hozzáadása

### 3. Adatfeldolgozás (Python Code Node-ok)
- **Raw to Structured**: Nyers HTML adatokból strukturált JSON objektumok
- **Normalize & Categorize**: 
  - Role kategorizálás (DevOps, Backend, Frontend, stb.)
  - Seniority meghatározás (junior, medior, senior, lead)
  - Work model (remote, hybrid, on-site)
  - Bérszámok parsing
  - Tech stack kinyerés
- **Generate Hash ID**: Deduplikációhoz hash kulcs generálás

### 4. Master Adatbázis Kezelés
- **Read Master Excel**: Meglévő master Excel fájl beolvasása
- **Diff against Master**: Új és módosult rekordok azonosítása
- **Upsert Master Excel**: Master fájl frissítése
- **Append Daily Excel**: Napi Excel fájl létrehozása

### 5. Jelentéskészítés
- **Send Email Report**: Email összefoglaló küldése
- **Error Slack Webhook**: Hibakezelés Slack webhook-kal

## Konfiguráció

### Szükséges Beállítások

#### 1. Excel Fájl Útvonalak
```json
{
  "master_file": "/data/it_jobs_master.xlsx",
  "daily_file": "/data/it_jobs_daily_{{ date }}.xlsx"
}
```

#### 2. Email Konfiguráció
```json
{
  "fromEmail": "noreply@yourcompany.com",
  "toEmail": "admin@yourcompany.com",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-email@gmail.com",
  "smtp_pass": "your-app-password"
}
```

#### 3. Slack Webhook
```json
{
  "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
}
```

### CSS Selectorok Testreszabása

A HTML Extract node-ban a következő selectorokat lehet módosítani forrásonként:

```javascript
{
  "job_title_raw": "h2.job-title, .job-title, h3 a, .position-title",
  "company_name": ".company-name, .employer, .company",
  "location_city": ".location, .city, .place",
  "description_raw": ".description, .job-description, .content",
  "salary_raw": ".salary, .wage, .compensation",
  "apply_url": "a[href*='apply'], a[href*='jelentkez'], .apply-link"
}
```

## Python Code Node-ok Részletei

### 1. Raw to Structured
```python
# Alapvető adatstruktúra létrehozása
structured_item = {
    'job_title_raw': job_title_raw,
    'job_title_norm': job_title_raw.strip(),
    'company_name': company_name,
    'location_city': location_city,
    'location_country': 'HU',
    'description_raw': description_raw,
    'salary_raw': salary_raw,
    'employment_type': 'full-time',
    'posted_at': dt.datetime.now().isoformat(),
    'valid_until': '',
    'apply_url': apply_url,
    'benefits_raw': '',
    'source': item.json.get('source', ''),
    'source_url': item.json.get('source_url', ''),
    'scraped_at': item.json.get('scraped_at', '')
}
```

### 2. Normalize & Categorize
```python
# Role kategorizálás
ROLE_MAP = {
    'DevOps': [r'\bdev[-\s]?ops\b', r'kubernetes', r'terraform', r'ci/?cd'],
    'Backend': [r'\bbackend\b', r'\b(java|kotlin|c#|\.net|python|go|php|node)\b'],
    'Frontend': [r'\bfront[-\s]?end\b', r'(react|angular|vue|typescript)'],
    # ... további kategóriák
}

# Seniority meghatározás
def seniority_of(text):
    t = text.lower()
    if re.search(r'\b(junior|kezd[őo]|pályakezd[őo])\b', t): return 'junior'
    if re.search(r'\b(medior|középhalad[óo]|3-5\s*év)\b', t): return 'medior'
    if re.search(r'\b(senior|tapasztalt|5\+?\s*év)\b', t): return 'senior'
    if re.search(r'\b(lead|principal|architect|vezet[őo])\b', t): return 'lead'
    return 'unspecified'
```

### 3. Generate Hash ID
```python
def hash_id(company, title_norm, city, role):
    key = f"{(company or '').lower()}|{(title_norm or '').lower()}|{(city or '').lower()}|{(role or '').lower()}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()
```

## Excel Kimenet Struktúra

### Master Sheet Oszlopok
1. source
2. source_url
3. scraped_at
4. job_title_raw
5. job_title_norm
6. role_category
7. seniority
8. employment_type
9. work_model
10. location_city
11. location_country
12. company_name
13. company_type
14. salary_raw
15. salary_min
16. salary_max
17. salary_currency
18. salary_gross_net
19. contract_type
20. benefits_raw
21. benefits_parsed
22. must_have_stack
23. nice_to_have_stack
24. languages
25. posted_at
26. valid_until
27. apply_url
28. description_excerpt
29. hash_id

### Daily Sheet
Ugyanazok az oszlopok, de csak az új/módosult rekordokkal.

## Hibakezelés

### Rate Limiting
- HTTP kérések között: 300-800ms késleltetés
- Lapozás között: 1-2 másodperc késleltetés

### Error Handling
- Minden node-ban be van állítva error handling
- Hibák esetén Slack webhook értesítés
- Failed execution esetén email értesítés

### Logging
- Minden lépés logolva van
- Scraped_at timestamp minden rekordnál
- Source és source_url minden rekordnál

## Telepítés és Futtatás

### 1. n8n Telepítés
```bash
npm install -g n8n
n8n start
```

### 2. Workflow Import
1. Nyisd meg az n8n webes felületét
2. Import workflow opció
3. Töltsd fel a `n8n_workflow_it_jobs.json` fájlt

### 3. Konfiguráció
1. Állítsd be az email SMTP beállításokat
2. Állítsd be a Slack webhook URL-t
3. Ellenőrizd az Excel fájl útvonalakat
4. Teszteld a Manual Trigger-rel

### 4. Ütemezés Aktiválása
1. Aktiváld a Cron Trigger-t
2. Ellenőrizd az időzóna beállításokat
3. Monitord a futásokat

## Monitoring és Karbantartás

### Napi Ellenőrzések
- Email összefoglalók ellenőrzése
- Excel fájlok létrehozásának ellenőrzése
- Hibák figyelése

### Heti Ellenőrzések
- Master Excel fájl méretének ellenőrzése
- CSS selectorok frissítése (ha változnak a portálok)
- Role kategorizálás finomhangolása

### Havonta
- Teljesítmény elemzés
- Duplikátumok ellenőrzése
- Adatminőség felmérése

## Hibaelhárítás

### Gyakori Problémák

#### 1. HTML Extract nem talál adatokat
- Ellenőrizd a CSS selectorokat
- Teszteld a forrás oldalt böngészőben
- Nézd meg, hogy változott-e a HTML struktúra

#### 2. Python Code node hibák
- Ellenőrizd a Python szintaxist
- Nézd meg a node logokat
- Teszteld a regex pattern-eket

#### 3. Excel írási hibák
- Ellenőrizd a fájl útvonalakat
- Győződj meg róla, hogy a könyvtár létezik
- Ellenőrizd a fájl jogosultságokat

#### 4. Email küldési hibák
- Ellenőrizd az SMTP beállításokat
- Győződj meg róla, hogy az app password helyes
- Teszteld a kapcsolatot

## Fejlesztési Lehetőségek

### Rövid távú
- További portálok hozzáadása
- Jobb CSS selectorok
- Hibakezelés javítása

### Közepes távú
- Google Sheets integráció
- Webhook értesítések
- Dashboard létrehozása

### Hosszú távú
- Machine learning alapú kategorizálás
- Realtime adatfrissítés
- API endpoint létrehozása
