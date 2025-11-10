# Test Fájlok Dokumentáció

## Aktív Test Fájlok

### Portál Tesztelés
- **`test_both_portals.py`** - Mindkét portál (No Fluff Jobs + Profession.hu) keresés tesztelése
- **`test_nofluff_direct.py`** - No Fluff Jobs scraper közvetlen tesztelése
- **`test_data_detailed.py`** - Részletes adatellenőrzés (dátum, leírás, lokáció)

### Gyors Ellenőrzések
- **`test_quick_check.py`** - Gyors állapot és adat ellenőrzés
- **`test_new_features_detailed.py`** - Új funkciók (dátum, leírás) részletes tesztelése

### Monitorozás
- **`monitor_search.py`** - Keresés folyamatának monitorozása valós időben
- **`check_search_progress.py`** - Keresés állapotának ellenőrzése

### Excel Ellenőrzések
- **`check_excel.py`** - Alap Excel fájl ellenőrzés (sorok, oszlopok, első sorok)
- **`check_excel_detailed.py`** - Részletes Excel ellenőrzés (portál statisztikák)
- **`check_excel_content.py`** - Excel tartalom részletes elemzése (parancssori argumentum)

## Használat

### Keresés tesztelése
```bash
python test_both_portals.py
```

### Gyors ellenőrzés
```bash
python test_quick_check.py
```

### Keresés monitorozása
```bash
python monitor_search.py
```

### Excel ellenőrzés
```bash
python check_excel.py
python check_excel_detailed.py
```

