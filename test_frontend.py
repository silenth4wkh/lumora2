#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frontend tesztelés - böngészőben ellenőrzés
"""

import requests
import json
import time

def test_frontend_endpoints():
    """Frontend endpoint-ok tesztelése"""
    
    base_url = "http://localhost:5000"
    
    print("=== Frontend tesztelés - API endpoint-ok ===")
    
    # 1. Főoldal elérhetőség
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("OK - Főoldal elérhető")
        else:
            print(f"HIBÁS - Főoldal hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Főoldal kapcsolódási hiba: {e}")
        return False
    
    # 2. Statisztikák endpoint
    try:
        response = requests.get(f"{base_url}/api/jobs/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK - Statisztikák endpoint működik")
            print(f"   - Összes állás: {data.get('stats', {}).get('total', 0)}")
        else:
            print(f"HIBÁS - Statisztikák endpoint hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Statisztikák endpoint hiba: {e}")
    
    # 3. Minőség statisztikák endpoint
    try:
        response = requests.get(f"{base_url}/api/jobs/quality-stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK - Minőség statisztikák endpoint működik")
            stats = data.get('stats', {})
            print(f"   - Pozíció valid: {stats.get('pozíció_valid_százalék', 0):.1f}%")
            print(f"   - Cég valid: {stats.get('cég_valid_százalék', 0):.1f}%")
            print(f"   - Lokáció valid: {stats.get('lokáció_valid_százalék', 0):.1f}%")
        else:
            print(f"HIBÁS - Minőség statisztikák endpoint hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Minőség statisztikák endpoint hiba: {e}")
    
    # 4. Dátum szűrés endpoint
    try:
        payload = {"days": 7}
        response = requests.post(f"{base_url}/api/jobs/filtered", 
                               json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK - Dátum szűrés endpoint működik")
            print(f"   - Szűrt állások: {data.get('filtered_count', 0)}")
            print(f"   - Százalék: {data.get('percentage', 0):.1f}%")
        else:
            print(f"HIBÁS - Dátum szűrés endpoint hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Dátum szűrés endpoint hiba: {e}")
    
    # 5. Validáció endpoint
    try:
        response = requests.post(f"{base_url}/api/jobs/validate", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("OK - Validáció endpoint működik")
            stats = data.get('stats', {})
            print(f"   - Validált állások: {data.get('count', 0)}")
            print(f"   - Pozíció valid: {stats.get('pozíció_valid_százalék', 0):.1f}%")
            print(f"   - Cég valid: {stats.get('cég_valid_százalék', 0):.1f}%")
            print(f"   - Lokáció valid: {stats.get('lokáció_valid_százalék', 0):.1f}%")
        else:
            print(f"HIBÁS - Validáció endpoint hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Validáció endpoint hiba: {e}")
    
    # 6. Excel export endpoint
    try:
        response = requests.get(f"{base_url}/api/export/excel", timeout=30)
        if response.status_code == 200:
            print("OK - Excel export endpoint működik")
            print(f"   - Fájl méret: {len(response.content)} bytes")
        else:
            print(f"HIBÁS - Excel export endpoint hiba: {response.status_code}")
    except Exception as e:
        print(f"HIBÁS - Excel export endpoint hiba: {e}")
    
    print("\n=== Frontend tesztelés befejezve ===")
    return True

def test_frontend_features():
    """Frontend funkciók tesztelése"""
    
    print("\n=== Frontend funkciók tesztelése ===")
    
    print("Ellenőrizd a következő funkciókat a böngészőben:")
    print("   URL: http://localhost:5000")
    
    print("\n1. Adatminőség ellenőrzés gomb:")
    print("   - Keressd meg a 'Adatminőség ellenőrzés' gombot")
    print("   - Kattints rá és várj a validáció befejezésére")
    print("   - Ellenőrizd, hogy megjelennek-e a minőség információk")
    
    print("\n2. Dátum szűrő dropdown:")
    print("   - Keressd meg a 'Minden dátum' dropdown-ot")
    print("   - Válaszd ki a 'Ma', 'Elmúlt 7 nap' opciókat")
    print("   - Ellenőrizd, hogy változnak-e a megjelenített állások")
    
    print("\n3. Minőség információk panel:")
    print("   - Keressd meg a kék színű minőség információkat")
    print("   - Ellenőrizd a Pozíció, Cég, Lokáció, Átlagos minőség értékeket")
    print("   - Ellenőrizd a színkódolt badge-eket (zöld/sárga/kék/piros)")
    
    print("\n4. Job kártyák validációs adatok:")
    print("   - Keressd meg a job kártyákat")
    print("   - Ellenőrizd a minőség badge-eket (Kiváló/Jó/Közepes/Gyenge/Rossz)")
    print("   - Ellenőrizd a 'Adatminőség' részben a konfidencia pontszámokat")
    
    print("\n5. Excel export funkciók:")
    print("   - Keressd meg a 'Excel export' gombot")
    print("   - Keressd meg a 'Szűrt Excel' gombot")
    print("   - Kattints rá és ellenőrizd a letöltést")
    
    print("\n6. Szűrők működése:")
    print("   - Teszteld a keresési szűrőt")
    print("   - Teszteld a lokáció szűrőt")
    print("   - Teszteld a munkavégzés típusa szűrőt")
    print("   - Teszteld a fizetés szűrőt")
    print("   - Teszteld a rendezési opciókat")
    
    print("\n7. Pagináció:")
    print("   - Ellenőrizd az oldalszámozást")
    print("   - Teszteld az 'Előző'/'Következő' gombokat")
    print("   - Ellenőrizd az állások számának megjelenítését")
    
    print("\n=== Frontend funkciók tesztelése befejezve ===")

def test_frontend_ui_elements():
    """Frontend UI elemek tesztelése"""
    
    print("\n=== Frontend UI elemek tesztelése ===")
    
    print("Ellenőrizd a következő UI elemeket:")
    
    print("\n1. Főcím és navigáció:")
    print("   - 'IT Álláskereső' főcím")
    print("   - 'Keresés indítása' gomb")
    print("   - 'Szűrők törlése' gomb")
    
    print("\n2. Szűrő panel:")
    print("   - Keresési mező")
    print("   - Dátum szűrő dropdown")
    print("   - Lokáció szűrő dropdown")
    print("   - Munkavégzés típusa szűrő dropdown")
    print("   - Fizetés szűrő dropdown")
    print("   - Rendezés szűrő dropdown")
    
    print("\n3. Eredmények panel:")
    print("   - Állások száma badge")
    print("   - Export gombok (CSV, Excel, Szűrt Excel)")
    print("   - Adatminőség ellenőrzés gomb")
    print("   - Minőség információk panel")
    
    print("\n4. Job kártyák:")
    print("   - Pozíció címe (linkkel)")
    print("   - Cég neve")
    print("   - Lokáció")
    print("   - Fizetés (ha van)")
    print("   - Munkavégzés típusa (ha van)")
    print("   - Leírás")
    print("   - Publikálás dátuma")
    print("   - Validációs információk")
    print("   - Minőség badge")
    print("   - 'Megtekintés' gomb")
    
    print("\n5. Pagináció:")
    print("   - Oldalszámok")
    print("   - 'Előző'/'Következő' gombok")
    print("   - Állások száma megjelenítés")
    
    print("\n=== Frontend UI elemek tesztelése befejezve ===")

if __name__ == "__main__":
    print("Frontend tesztelés indítása...")
    
    # API endpoint-ok tesztelése
    if test_frontend_endpoints():
        # Frontend funkciók tesztelése
        test_frontend_features()
        
        # Frontend UI elemek tesztelése
        test_frontend_ui_elements()
        
        print("\nOK - Frontend tesztelés befejezve!")
        print("Nyisd meg a böngészőt: http://localhost:5000")
        print("Kövesd a fenti ellenőrzési listát")
    else:
        print("\nHIBÁS - Frontend tesztelés sikertelen!")
        print("Ellenőrizd, hogy a Flask alkalmazás fut-e")
