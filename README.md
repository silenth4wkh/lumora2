# IT Álláskereső - Profession.hu Scraper

Egy modern webes felület a Profession.hu-ról való IT állások automatikus gyűjtéséhez és szűréséhez.

## Funkciók

### 🔍 **Intelligens Keresés**
- 9 kategória (Programozási nyelvek, Frontend, Backend, DevOps, stb.)
- 100+ kulcsszó automatikus kezelése
- Zaj-szűrők (nem-IT pozíciók kiszűrése)

### 📊 **Adat Enrichment**
- Cég neve és lokáció automatikus kinyerése
- JSON-LD és dataLayer támogatás
- Fallback mechanizmusok

### 🎨 **Modern Web Felület**
- Responsive design (Bootstrap 5)
- Valós idejű keresés
- Szűrés és rendezés
- CSV export
- Pagináció

### ⚡ **Teljesítmény**
- Párhuzamos RSS feed feldolgozás
- Progress tracking
- Duplikáció kezelés
- Rate limiting

## Telepítés

1. **Függőségek telepítése:**
```bash
pip install -r requirements.txt
```

2. **Alkalmazás indítása:**
```bash
python app.py
```

3. **Böngészőben megnyitás:**
```
http://localhost:5000
```

## Használat

1. **Kategóriák kiválasztása** - Válaszd ki a kívánt IT területeket
2. **Keresés indítása** - Kattints az "Állások keresése" gombra
3. **Eredmények böngészése** - Szűrj, rendezz, exportálj
4. **CSV export** - Töltsd le az eredményeket

## API Végpontok

- `GET /` - Főoldal
- `GET /api/categories` - Kategóriák listája
- `POST /api/search` - Állások keresése
- `GET /api/progress` - Keresés állapota
- `GET /api/jobs` - Megtalált állások

## Technológiai Stack

- **Backend:** Flask, Python
- **Frontend:** HTML5, Bootstrap 5, JavaScript
- **Scraping:** requests, BeautifulSoup4, XML parsing
- **Adatkezelés:** JSON, CSV export

## Kategóriák

1. **Programozási nyelvek** - Java, Python, C#, C++, Go, Rust, stb.
2. **Frontend fejlesztés** - React, Angular, Vue, TypeScript
3. **Backend fejlesztés** - Node.js, Spring, .NET Core, Django
4. **Mobil fejlesztés** - Android, iOS, Flutter, React Native
5. **Adatkezelés & AI** - Data Science, Machine Learning, Big Data
6. **DevOps & Cloud** - AWS, Azure, Kubernetes, Docker
7. **Tesztelés** - QA, Test Automation, SDET
8. **Embedded** - Firmware, FPGA, Microcontroller
9. **Biztonság** - Security Engineer, Penetration Testing
10. **Enterprise** - SAP, ERP, CRM rendszerek

## Fejlesztési lehetőségek

- [ ] Adatbázis integráció (SQLite/PostgreSQL)
- [ ] Felhasználói fiókok és kedvencek
- [ ] Email értesítések új állásokról
- [ ] WebSocket valós idejű frissítések
- [ ] Docker konténerizálás
- [ ] Unit tesztek
- [ ] Logging és monitoring

## Licenc

MIT License
