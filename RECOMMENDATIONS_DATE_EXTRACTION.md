# Publikálási dátum kinyerése - Javaslatok

## Probléma
A No Fluff Jobs **nem jelenít meg publikálási dátumot** sem a lista oldalon, sem a detail oldalon a HTML-ben.

## Vizsgálat eredményei
- ✗ Lista oldal (anchor): nincs dátum
- ✗ Detail oldal: nincs `<time>` elem, nincs meta tag
- ✗ JSON-LD structured data: csak Organization schema, nincs JobPosting
- ✗ HTML szöveges keresés: nincs "X napja", "publikálva" stb.

## 💡 JAVASLATOK (Selenium nélkül, HTML parsing megtartásával)

### ✅ **1. API Reverse Engineering (LEGJOBB)**
**Mód:** Browser DevTools Network tab vizsgálata  
**Hol:** No Fluff Jobs oldal betöltése közben  
**Mit keresünk:** AJAX kérés ami JSON-t ad vissza az állásokkal

**Előnyök:**
- Strukturált JSON adat (datePosted mező várható)
- Gyors (1 kérés = sok állás)
- Stabil (API kevésbé változik mint HTML)

**Implementáció:**
```python
# Példa (ha találunk API endpoint-ot)
api_url = "https://nofluffjobs.com/api/v1/postings?category=ai&page=1"
r = requests.get(api_url, headers=HEADERS)
jobs_data = r.json()
for job in jobs_data['postings']:
    date = job.get('datePosted')  # vagy 'createdAt', 'publishedAt'
```

**Hogyan találjuk meg:**
1. Nyisd meg: https://nofluffjobs.com/hu/artificial-intelligence
2. F12 → Network tab → XHR/Fetch filter
3. Görgess/lapozz → keress JSON response-t ami job listát tartalmaz
4. Nézd meg a Request URL-t és a response struktúrát

---

### ✅ **2. Detail page scraping bővítése**
**Mód:** Minden job-hoz külön kérés a detail oldalra  
**Mit keresünk:** Hidden input, data-attribute, vagy dinamikus elem

**Előnyök:**
- Jelenleg is használjuk detail scraping-et (leíráshoz)
- Biztos, hogy a detail oldal tartalmaz minden infót

**Hátrányok:**
- Lassú (326 állás = 326 extra kérés)
- Nagyobb terhelés a szerveren

**Implementáció:**
```python
def fetch_job_details(job_url):
    r = requests.get(job_url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Keresés data-attribute-ban
    date_elem = soup.find(attrs={'data-posted-date': True})
    if date_elem:
        return date_elem['data-posted-date']
    
    # Keresés hidden input-ban
    hidden = soup.find('input', attrs={'name': 'posted_date', 'type': 'hidden'})
    if hidden:
        return hidden.get('value')
    
    # JavaScript változó keresése
    import re
    match = re.search(r'postedDate["\']?\s*:\s*["\']([^"\']+)', r.text)
    if match:
        return match.group(1)
    
    return None
```

---

### ⚠️ **3. Fallback: Lekérés dátuma használata**
**Mód:** Ha nincs publikálási dátum, használd a lekérés dátumát

**Előnyök:**
- Egyszerű
- Mindig működik

**Hátrányok:**
- Pontatlan (friss vs. régi állások)
- Szűrés lehetetlen

**Implementáció:**
```python
job['Publikálva'] = datetime.today().strftime('%Y-%m-%d')
job['Publikálva_megjegyzés'] = 'Becsült (lekérés dátuma)'
```

---

### ⚠️ **4. Heurisztika: "ÚJ" jelölés alapján**
**Mód:** Ha van "ÚJ" badge az anchor-ban, akkor 1-3 napja publikálva

**Előnyök:**
- Gyors (már meglévő adatból)
- Segít szűrni

**Hátrányok:**
- Pontatlan (mit jelent "új"? 1 nap? 7 nap?)

**Implementáció:**
```python
# nofluff_html_parser.py-ban
if 'ÚJ' in title_raw or 'NEW' in title_raw.upper():
    pub_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    pub_date_note = 'Becsült (ÚJ jelölés alapján)'
else:
    pub_date = ''
```

---

## 🎯 JAVASOLT MEGOLDÁS

**1. lépés:** Próbáld meg az **API reverse engineering**-et (10 perc)
- Ha találsz API endpoint-ot → használd azt (legjobb)

**2. lépés:** Ha nincs API, akkor **detail page scraping** (20 állás mintán)
- Nézd meg 20 random job detail oldalát
- Keress data-attribute-ot, hidden input-ot, JS változót

**3. lépés:** Ha a detail oldalon sincs, akkor **fallback megoldás**:
- Lekérés dátuma + "ÚJ" heurisztika
- Excel-ben jelöld: "Becsült dátum"

---

## Következő lépés
Szeretnéd, hogy:
1. **Segítsek megkeresni az API endpoint-ot?** (browser automation nélkül vizsgálom a hálózati forgalmat)
2. **Implementáljuk a detail page scraping bővítést?** (dátum keresés a detail oldalon)
3. **Fallback megoldást használjunk?** (lekérés dátuma + ÚJ heurisztika)

