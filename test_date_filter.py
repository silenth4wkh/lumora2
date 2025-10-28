#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dátum szűrés tesztelése
"""

from datetime import datetime, timedelta
import json

# Mock adatok teszteléshez
mock_jobs = [
    {
        "Forrás": "Profession – IT főkategória",
        "Pozíció": "Python fejlesztő",
        "Cég": "Teszt Kft",
        "Lokáció": "Budapest",
        "Publikálva": "2025.01.28",
        "Publikálva_dátum": datetime.now(),
        "Friss_állás": True,
        "Link": "https://example.com/job1"
    },
    {
        "Forrás": "No Fluff Jobs",
        "Pozíció": "Java fejlesztő", 
        "Cég": "Teszt Zrt",
        "Lokáció": "Debrecen",
        "Publikálva": "2025.01.25",
        "Publikálva_dátum": datetime.now() - timedelta(days=3),
        "Friss_állás": True,
        "Link": "https://example.com/job2"
    },
    {
        "Forrás": "Profession – IT főkategória",
        "Pozíció": "DevOps mérnök",
        "Cég": "Régi Kft",
        "Lokáció": "Szeged",
        "Publikálva": "2025.01.15",
        "Publikálva_dátum": datetime.now() - timedelta(days=13),
        "Friss_állás": False,
        "Link": "https://example.com/job3"
    }
]

def filter_jobs_by_date(jobs, days_filter):
    """Állások szűrése dátum szerint"""
    filtered_jobs = []
    cutoff_date = datetime.now() - timedelta(days=days_filter)
    
    for job in jobs:
        pub_date = job.get("Publikálva_dátum")
        if pub_date:
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.strptime(pub_date, "%Y.%m.%d")
                except:
                    try:
                        pub_date = datetime.strptime(pub_date, "%Y-%m-%d")
                    except:
                        continue
            
            if pub_date >= cutoff_date:
                filtered_jobs.append(job)
    
    return filtered_jobs

def get_job_stats(jobs):
    """Állások statisztikái dátum szerint"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        "total": len(jobs),
        "today": 0,
        "yesterday": 0,
        "last_7_days": 0,
        "last_30_days": 0,
        "older": 0
    }
    
    for job in jobs:
        pub_date = job.get("Publikálva_dátum")
        if pub_date:
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.strptime(pub_date, "%Y.%m.%d").date()
                except:
                    try:
                        pub_date = datetime.strptime(pub_date, "%Y-%m-%d").date()
                    except:
                        continue
            elif isinstance(pub_date, datetime):
                pub_date = pub_date.date()
            else:
                continue
            
            if pub_date == today:
                stats["today"] += 1
            elif pub_date == yesterday:
                stats["yesterday"] += 1
            elif pub_date >= week_ago:
                stats["last_7_days"] += 1
            elif pub_date >= month_ago:
                stats["last_30_days"] += 1
            else:
                stats["older"] += 1
    
    return stats

if __name__ == "__main__":
    print("=== Dátum szűrés tesztelése ===")
    
    # Statisztikák
    stats = get_job_stats(mock_jobs)
    print(f"\nStatisztikák:")
    print(f"  - Összes állás: {stats['total']}")
    print(f"  - Ma: {stats['today']}")
    print(f"  - Tegnap: {stats['yesterday']}")
    print(f"  - Elmúlt 7 nap: {stats['last_7_days']}")
    print(f"  - Elmúlt 30 nap: {stats['last_30_days']}")
    print(f"  - Régebbi: {stats['older']}")
    
    # 7 napos szűrés
    filtered_7_days = filter_jobs_by_date(mock_jobs, 7)
    print(f"\n7 napos szűrés:")
    print(f"  - Szűrt állások: {len(filtered_7_days)}")
    print(f"  - Százalék: {(len(filtered_7_days) / len(mock_jobs) * 100):.1f}%")
    
    # 1 napos szűrés
    filtered_1_day = filter_jobs_by_date(mock_jobs, 1)
    print(f"\n1 napos szűrés:")
    print(f"  - Szűrt állások: {len(filtered_1_day)}")
    print(f"  - Százalék: {(len(filtered_1_day) / len(mock_jobs) * 100):.1f}%")
    
    print("\n=== Teszt befejezve ===")
