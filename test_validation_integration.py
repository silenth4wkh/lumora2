#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adatminőség validáció integráció tesztelése
"""

import requests
import json
from data_quality_validator import DataQualityValidator

def test_validation_integration():
    """Validációs integráció tesztelése"""
    
    # Mock adatok
    mock_jobs = [
        {
            "Forrás": "Profession – IT főkategória",
            "Pozíció": "Python fejlesztő (f/m/x)",
            "Cég": "Teszt Kft",
            "Lokáció": "Budapest",
            "Publikálva": "2025.01.28",
            "Link": "https://example.com/job1"
        },
        {
            "Forrás": "No Fluff Jobs",
            "Pozíció": "Own and maintain a clear delivery roadmap",
            "Cég": "Drive requirement specification",
            "Lokáció": "Define acceptance criteria",
            "Publikálva": "2025.01.25",
            "Link": "https://example.com/job2"
        },
        {
            "Forrás": "Profession – IT főkategória",
            "Pozíció": "Java Developer",
            "Cég": "Tech Solutions Zrt",
            "Lokáció": "Remote",
            "Publikálva": "2025.01.15",
            "Link": "https://example.com/job3"
        }
    ]
    
    print("=== Adatminőség validáció integráció tesztelése ===")
    
    # Validátor inicializálása
    validator = DataQualityValidator()
    
    # Validálás
    validated_jobs = []
    for job in mock_jobs:
        validated_job = validator.validate_job(job)
        validated_jobs.append(validated_job)
    
    # Statisztikák
    stats = validator.get_validation_stats(validated_jobs)
    
    print(f"\nValidációs eredmények:")
    print(f"  - Összes állás: {stats['összes_állás']}")
    print(f"  - Pozíció valid: {stats['pozíció_valid']} ({stats['pozíció_valid_százalék']:.1f}%)")
    print(f"  - Cég valid: {stats['cég_valid']} ({stats['cég_valid_százalék']:.1f}%)")
    print(f"  - Lokáció valid: {stats['lokáció_valid']} ({stats['lokáció_valid_százalék']:.1f}%)")
    print(f"  - Átlagos pontszám: {stats['átlagos_pontszám']:.2f}")
    
    print(f"\nMinőség osztályok:")
    for quality_class, count in stats['minőség_osztályok'].items():
        print(f"  - {quality_class}: {count}")
    
    print(f"\nRészletes validációs eredmények:")
    for i, job in enumerate(validated_jobs, 1):
        validation = job['Validáció']
        print(f"\n{i}. {job['Pozíció']}")
        print(f"   Pozíció: {validation['pozíció_valid']} ({validation['pozíció_konfidencia']:.2f})")
        print(f"   Cég: {validation['cég_valid']} ({validation['cég_konfidencia']:.2f})")
        print(f"   Lokáció: {validation['lokáció_valid']} ({validation['lokáció_konfidencia']:.2f})")
        print(f"   Minőség: {validation['minőség_osztály']} ({validation['összesített_pontszám']:.2f})")
    
    # Frontend integráció tesztelése
    print(f"\n=== Frontend integráció tesztelése ===")
    
    # Validációs információk formázása
    quality_info = {
        'pozíció_valid_százalék': stats['pozíció_valid_százalék'],
        'cég_valid_százalék': stats['cég_valid_százalék'],
        'lokáció_valid_százalék': stats['lokáció_valid_százalék'],
        'átlagos_pontszám': stats['átlagos_pontszám']
    }
    
    print(f"Frontend minőség információk:")
    print(f"  - Pozíció: {quality_info['pozíció_valid_százalék']:.1f}%")
    print(f"  - Cég: {quality_info['cég_valid_százalék']:.1f}%")
    print(f"  - Lokáció: {quality_info['lokáció_valid_százalék']:.1f}%")
    print(f"  - Átlagos pontszám: {quality_info['átlagos_pontszám']:.2f}")
    
    # Színek beállítása minőség szerint
    def get_quality_color(percentage):
        if percentage >= 80:
            return "bg-success"
        elif percentage >= 60:
            return "bg-warning"
        elif percentage >= 40:
            return "bg-info"
        else:
            return "bg-danger"
    
    print(f"\nFrontend badge színek:")
    print(f"  - Pozíció: {get_quality_color(quality_info['pozíció_valid_százalék'])}")
    print(f"  - Cég: {get_quality_color(quality_info['cég_valid_százalék'])}")
    print(f"  - Lokáció: {get_quality_color(quality_info['lokáció_valid_százalék'])}")
    print(f"  - Átlagos: {get_quality_color(quality_info['átlagos_pontszám'] * 100)}")
    
    print(f"\n=== Teszt befejezve ===")
    
    return validated_jobs, stats

if __name__ == "__main__":
    test_validation_integration()
