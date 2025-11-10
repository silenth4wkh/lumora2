#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import requests

BASE = os.environ.get("RENDER_BASE_URL", "https://lumora2.onrender.com").rstrip('/')


def main() -> int:
    print(f"[TARGET] {BASE}")
    print("[CALL] GET /api/export/excel")
    
    try:
        r = requests.get(f"{BASE}/api/export/excel", timeout=120, stream=True)
        
        if r.status_code != 200:
            print(f"[ERROR] Status: {r.status_code}")
            print(r.text[:1000])
            return 1
        
        # Save Excel file
        filename = "it_allasok_render_export.xlsx"
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filename)
        print(f"[SUCCESS] Excel file saved: {filename}")
        print(f"         Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        return 0
        
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Export request timed out")
        return 2
    except Exception as e:
        print(f"[ERROR] {e}")
        return 3


if __name__ == '__main__':
    sys.exit(main())

