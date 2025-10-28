#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adatminőség validáció modul
"""

import re
from typing import Dict, List, Tuple, Optional

class DataQualityValidator:
    """Adatminőség validátor osztály"""
    
    def __init__(self):
        # Magyar városok listája
        self.hungarian_cities = {
            'budapest', 'debrecen', 'szeged', 'miskolc', 'pécs', 'győr',
            'nyíregyháza', 'kecskemét', 'székesfehérvár', 'szombathely',
            'szolnok', 'tatabánya', 'kaposvár', 'békéscsaba', 'erőd',
            'veszprém', 'zalaegerszeg', 'sopron', 'egerszeg', 'nagykanizsa',
            'dunakeszi', 'hódmezővásárhely', 'salgótarján', 'cigánd',
            'baja', 'kiskunhalas', 'kiskunfélegyháza', 'pápa', 'gyöngyös',
            'gyula', 'hajdúböszörmény', 'kiskunhalas', 'kiskunfélegyháza',
            'pápa', 'gyöngyös', 'gyula', 'hajdúböszörmény', 'kiskunhalas',
            'kiskunfélegyháza', 'pápa', 'gyöngyös', 'gyula', 'hajdúböszörmény',
            'remote', 'távmunka', 'hibrid', 'home office'
        }
        
        # Magyar cégformák
        self.company_suffixes = {
            'kft', 'zrt', 'bt', 'kkt', 'rt', 'nyrt', 'közkereseti társaság',
            'ltd', 'llc', 'inc', 'corp', 'gmbh', 'ag', 'sa', 'sarl',
            's.r.o.', 's.r.l.', 'bv', 'nv', 'ab', 'oy', 'as', 'a/s'
        }
        
        # Pozíció típusok
        self.position_keywords = {
            'fejlesztő', 'developer', 'programozó', 'programmer', 'mérnök', 'engineer',
            'elemző', 'analyst', 'tervező', 'designer', 'architect', 'architect',
            'manager', 'menedzser', 'vezető', 'lead', 'senior', 'junior',
            'devops', 'sysadmin', 'rendszergazda', 'tester', 'tesztelő',
            'data', 'adat', 'ai', 'ml', 'machine learning', 'mesterséges intelligencia',
            'frontend', 'backend', 'fullstack', 'mobile', 'mobil', 'web',
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'c#', 'c++', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift'
        }
        
        # Invalid pozíció szavak
        self.invalid_position_words = {
            'maintain', 'delivery', 'roadmap', 'requirement', 'specification',
            'criteria', 'mvp', 'collaboration', 'business', 'it', 'osztály',
            'vezető', 'kontrolling', 'együttműködve', 'közeli', 'kapcsolat',
            'meghatározás', 'definíció', 'elfogadás', 'követelmény', 'specifikáció'
        }
    
    def validate_position(self, position: str) -> Tuple[bool, str, float]:
        """
        Pozíció validálása
        
        Returns:
            Tuple[is_valid, cleaned_position, confidence_score]
        """
        if not position or len(position.strip()) < 3:
            return False, "", 0.0
        
        cleaned = self._clean_text(position)
        
        # Ellenőrizzük, hogy tartalmaz-e pozíció kulcsszavakat
        position_lower = cleaned.lower()
        position_score = 0.0
        
        # Pozitív pontok
        for keyword in self.position_keywords:
            if keyword in position_lower:
                position_score += 0.1
        
        # Negatív pontok
        for invalid_word in self.invalid_position_words:
            if invalid_word in position_lower:
                position_score -= 0.2
        
        # Minimum hossz ellenőrzés
        if len(cleaned) < 5:
            position_score -= 0.3
        
        # Maximum hossz ellenőrzés (túl hosszú leírás)
        if len(cleaned) > 100:
            position_score -= 0.2
        
        # (f/m/x) eltávolítása
        cleaned = re.sub(r'\s*\([fmx]\)\s*$', '', cleaned, flags=re.IGNORECASE)
        
        # Konfidencia számítás
        confidence = max(0.0, min(1.0, position_score + 0.5))
        is_valid = confidence >= 0.3
        
        return is_valid, cleaned, confidence
    
    def validate_company(self, company: str) -> Tuple[bool, str, float]:
        """
        Cég validálása
        
        Returns:
            Tuple[is_valid, cleaned_company, confidence_score]
        """
        if not company or len(company.strip()) < 2:
            return False, "", 0.0
        
        cleaned = self._clean_text(company)
        
        # Ellenőrizzük, hogy tartalmaz-e cégformát
        company_lower = cleaned.lower()
        company_score = 0.0
        
        # Pozitív pontok
        for suffix in self.company_suffixes:
            if suffix in company_lower:
                company_score += 0.3
                break
        
        # Ellenőrizzük, hogy nem pozíció leírás
        for invalid_word in self.invalid_position_words:
            if invalid_word in company_lower:
                company_score -= 0.4
        
        # Ellenőrizzük, hogy nem túl hosszú (leírás lehet)
        if len(cleaned) > 50:
            company_score -= 0.2
        
        # Ellenőrizzük, hogy tartalmaz-e nagybetűket (cégnevek általában)
        if any(c.isupper() for c in cleaned):
            company_score += 0.1
        
        # Konfidencia számítás
        confidence = max(0.0, min(1.0, company_score + 0.4))
        is_valid = confidence >= 0.3
        
        return is_valid, cleaned, confidence
    
    def validate_location(self, location: str) -> Tuple[bool, str, float]:
        """
        Lokáció validálása
        
        Returns:
            Tuple[is_valid, cleaned_location, confidence_score]
        """
        if not location or len(location.strip()) < 2:
            return False, "", 0.0
        
        cleaned = self._clean_text(location)
        
        # Ellenőrizzük, hogy magyar város-e
        location_lower = cleaned.lower()
        location_score = 0.0
        
        # Pozitív pontok
        for city in self.hungarian_cities:
            if city in location_lower:
                location_score += 0.5
                break
        
        # Ellenőrizzük, hogy nem pozíció vagy cég
        for keyword in self.position_keywords:
            if keyword in location_lower:
                location_score -= 0.3
        
        for suffix in self.company_suffixes:
            if suffix in location_lower:
                location_score -= 0.3
        
        # Konfidencia számítás
        confidence = max(0.0, min(1.0, location_score + 0.3))
        is_valid = confidence >= 0.4
        
        return is_valid, cleaned, confidence
    
    def validate_job(self, job: Dict) -> Dict:
        """
        Teljes állás validálása
        
        Returns:
            Dict with validation results
        """
        position = job.get('Pozíció', '')
        company = job.get('Cég', '')
        location = job.get('Lokáció', '')
        
        # Validálás
        pos_valid, pos_cleaned, pos_conf = self.validate_position(position)
        comp_valid, comp_cleaned, comp_conf = self.validate_company(company)
        loc_valid, loc_cleaned, loc_conf = self.validate_location(location)
        
        # Összesített minőség pontszám
        overall_score = (pos_conf + comp_conf + loc_conf) / 3
        
        # Validált állás létrehozása
        validated_job = job.copy()
        validated_job.update({
            'Pozíció': pos_cleaned,
            'Cég': comp_cleaned,
            'Lokáció': loc_cleaned,
            'Validáció': {
                'pozíció_valid': pos_valid,
                'pozíció_konfidencia': pos_conf,
                'cég_valid': comp_valid,
                'cég_konfidencia': comp_conf,
                'lokáció_valid': loc_valid,
                'lokáció_konfidencia': loc_conf,
                'összesített_pontszám': overall_score,
                'minőség_osztály': self._get_quality_class(overall_score)
            }
        })
        
        return validated_job
    
    def _clean_text(self, text: str) -> str:
        """Szöveg tisztítása"""
        if not text:
            return ""
        
        # Extra whitespace eltávolítása
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Speciális karakterek eltávolítása
        cleaned = re.sub(r'[^\w\s\-\.\(\)]', '', cleaned)
        
        return cleaned
    
    def _get_quality_class(self, score: float) -> str:
        """Minőség osztály meghatározása"""
        if score >= 0.8:
            return "Kiváló"
        elif score >= 0.6:
            return "Jó"
        elif score >= 0.4:
            return "Közepes"
        elif score >= 0.2:
            return "Gyenge"
        else:
            return "Rossz"
    
    def get_validation_stats(self, jobs: List[Dict]) -> Dict:
        """Validációs statisztikák"""
        total_jobs = len(jobs)
        if total_jobs == 0:
            return {}
        
        stats = {
            'összes_állás': total_jobs,
            'pozíció_valid': 0,
            'cég_valid': 0,
            'lokáció_valid': 0,
            'minőség_osztályok': {
                'Kiváló': 0,
                'Jó': 0,
                'Közepes': 0,
                'Gyenge': 0,
                'Rossz': 0
            },
            'átlagos_pontszám': 0.0
        }
        
        total_score = 0.0
        
        for job in jobs:
            validation = job.get('Validáció', {})
            
            if validation.get('pozíció_valid', False):
                stats['pozíció_valid'] += 1
            
            if validation.get('cég_valid', False):
                stats['cég_valid'] += 1
            
            if validation.get('lokáció_valid', False):
                stats['lokáció_valid'] += 1
            
            score = validation.get('összesített_pontszám', 0.0)
            total_score += score
            
            quality_class = validation.get('minőség_osztály', 'Rossz')
            stats['minőség_osztályok'][quality_class] += 1
        
        stats['átlagos_pontszám'] = total_score / total_jobs if total_jobs > 0 else 0.0
        
        # Százalékok számítása
        stats['pozíció_valid_százalék'] = (stats['pozíció_valid'] / total_jobs) * 100
        stats['cég_valid_százalék'] = (stats['cég_valid'] / total_jobs) * 100
        stats['lokáció_valid_százalék'] = (stats['lokáció_valid'] / total_jobs) * 100
        
        return stats

# Tesztelés
if __name__ == "__main__":
    validator = DataQualityValidator()
    
    # Teszt adatok
    test_jobs = [
        {
            "Pozíció": "Python fejlesztő (f/m/x)",
            "Cég": "Teszt Kft",
            "Lokáció": "Budapest"
        },
        {
            "Pozíció": "Own and maintain a clear delivery roadmap",
            "Cég": "Drive requirement specification",
            "Lokáció": "Define acceptance criteria"
        },
        {
            "Pozíció": "Java Developer",
            "Cég": "Tech Solutions Zrt",
            "Lokáció": "Remote"
        }
    ]
    
    print("=== Adatminőség validáció tesztelése ===")
    
    validated_jobs = []
    for job in test_jobs:
        validated_job = validator.validate_job(job)
        validated_jobs.append(validated_job)
        
        print(f"\nPozíció: {job['Pozíció']}")
        print(f"  Validált: {validated_job['Pozíció']}")
        print(f"  Konfidencia: {validated_job['Validáció']['pozíció_konfidencia']:.2f}")
        
        print(f"Cég: {job['Cég']}")
        print(f"  Validált: {validated_job['Cég']}")
        print(f"  Konfidencia: {validated_job['Validáció']['cég_konfidencia']:.2f}")
        
        print(f"Lokáció: {job['Lokáció']}")
        print(f"  Validált: {validated_job['Lokáció']}")
        print(f"  Konfidencia: {validated_job['Validáció']['lokáció_konfidencia']:.2f}")
        
        print(f"Minőség: {validated_job['Validáció']['minőség_osztály']}")
    
    # Statisztikák
    stats = validator.get_validation_stats(validated_jobs)
    print(f"\n=== Validációs statisztikák ===")
    print(f"Összes állás: {stats['összes_állás']}")
    print(f"Pozíció valid: {stats['pozíció_valid']} ({stats['pozíció_valid_százalék']:.1f}%)")
    print(f"Cég valid: {stats['cég_valid']} ({stats['cég_valid_százalék']:.1f}%)")
    print(f"Lokáció valid: {stats['lokáció_valid']} ({stats['lokáció_valid_százalék']:.1f}%)")
    print(f"Átlagos pontszám: {stats['átlagos_pontszám']:.2f}")
    
    print("\n=== Teszt befejezve ===")
