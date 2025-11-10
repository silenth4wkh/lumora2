#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script Flask app indításához"""
import sys
print("[DEBUG] Starting Flask app...")
sys.stdout.flush()

try:
    print("[DEBUG] Importing app module...")
    sys.stdout.flush()
    import app
    print("[DEBUG] Import OK")
    sys.stdout.flush()
    
    print("[DEBUG] Running Flask...")
    sys.stdout.flush()
    app.app.run(host='0.0.0.0', port=5000)
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.stdout.flush()

