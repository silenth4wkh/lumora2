# Tesztelési Útmutató

## 🚀 Gyors Tesztelés

### 1. Flask szerver indítása
```bash
python app.py
```
A szerver az `http://127.0.0.1:5001` címen indul el.

### 2. Keresés indítása

**Böngészőben:**
- Nyisd meg: `http://127.0.0.1:5001`
- Válaszd ki az "IT" kategóriát
- Kattints az "Állások keresése" gombra

**Vagy API-n keresztül (Postman/curl):**
```bash
curl -X POST http://127.0.0.1:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"categories": ["IT"]}'
```

**Vagy Python script-tel:**
```bash
python test_search_now.py
```

### 3. Várt eredmények

✅ **Profession.hu**: 300-900 állás  
✅ **No Fluff Jobs**: 50-820 állás (API-alapú, gyors)  
✅ **Összesen**: 350-1700 állás  
✅ **Futási idő**: 30-180 másodperc (API-val sokkal gyorsabb!)

### 4. Probléma esetén

**Ha a második keresés lefagy:**
1. Állítsd le a Flask szervert (Ctrl+C)
2. Várj 5 másodpercet
3. Indítsd újra: `python app.py`
4. Próbáld újra a keresést

**Ha az API nem működik:**
- A rendszer automatikusan HTML scraping-re vált
- Ez lassabb (1-2 perc), de működik

## 📊 Javítások

✅ **Hibrid API scraper integrálva** (2025-01-30)
- API elsődleges használata No Fluff Jobs-hoz
- Automatikus fallback HTML scraping-re
- Selenium csak utolsó esetben

## 🔍 Audit következő lépés

Miután a teszt sikeres, futtassuk az auditot a teljes kódminőség ellenőrzésére.

