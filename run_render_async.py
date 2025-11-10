#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
from typing import Optional
import requests

DEFAULT_HOST_GUESSES = [
    "https://it-allaskereso.onrender.com",
    "http://it-allaskereso.onrender.com",
]

START_TIMEOUT = 30
PROGRESS_TIMEOUT = 10
RESULT_TIMEOUT = 30
TOTAL_WAIT = 900  # 15 minutes
POLL_INTERVAL = 2.0


def pick_base_url() -> Optional[str]:
    env = os.environ.get("RENDER_BASE_URL", "").strip()
    if env:
        return env.rstrip('/')
    for guess in DEFAULT_HOST_GUESSES:
        try:
            r = requests.get(f"{guess}/api/status", timeout=10)
            if r.status_code == 200:
                return guess
        except Exception:
            continue
    return None


def wait_ready(base: str, max_wait: int = 120) -> bool:
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get(f"{base}/api/status", timeout=10)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def main() -> int:
    base = pick_base_url()
    if not base:
        print("[ERROR] Could not determine Render base URL. Set RENDER_BASE_URL env var.")
        print("        Example: https://it-allaskereso.onrender.com")
        return 1
    print(f"[TARGET] {base}")

    print("[WAIT] Checking service readiness...")
    if not wait_ready(base):
        print("[ERROR] Service not ready at /api/status")
        return 2

    try:
        # Reset (best effort)
        try:
            requests.post(f"{base}/api/reset", timeout=10)
        except Exception:
            pass

        print('[CALL] POST /api/search/async {"mode":"full"}')
        r = requests.post(f"{base}/api/search/async", json={"mode": "full"}, timeout=START_TIMEOUT)
        if r.status_code not in (200, 202):
            print('[ERROR] start status:', r.status_code, r.text[:500])
            return 3
        tid = r.json().get('task_id')
        if not tid:
            print('[ERROR] No task_id returned')
            return 3
        print(f"[TASK] id={tid}")

        # Poll progress
        start_wait = time.time()
        while time.time() - start_wait < TOTAL_WAIT:
            try:
                pr = requests.get(f"{base}/api/progress/{tid}", timeout=PROGRESS_TIMEOUT)
                if pr.status_code == 200:
                    p = pr.json()
                    print(f"[PROGRESS] status={p.get('status')} progress={p.get('progress')}")
                    if p.get('status') in ('completed', 'failed'):
                        break
                else:
                    print('[WARN] progress status:', pr.status_code)
            except Exception as e:
                print('[WARN] progress error:', e)
            time.sleep(POLL_INTERVAL)

        rr = requests.get(f"{base}/api/result/{tid}", timeout=RESULT_TIMEOUT)
        if rr.status_code == 200:
            data = rr.json()
            jobs = data.get('jobs', [])
            total = data.get('total_jobs', len(jobs))
            profession = sum(1 for j in jobs if 'profession' in str(j.get('Forrás') or j.get('forras') or '').lower())
            nofluff = sum(1 for j in jobs if 'no fluff' in str(j.get('Forrás') or j.get('forras') or '').lower())
            print('='*70)
            print('[RESULTS - RENDER ASYNC QUICK]')
            print(f'Total jobs: {total}')
            print(f' - Profession.hu: {profession}')
            print(f' - No Fluff Jobs: {nofluff}')
            print('='*70)
            return 0
        else:
            print('[INFO] result status:', rr.status_code, rr.text[:500])
            return 4

    except requests.exceptions.Timeout:
        print('[ERROR] Request timed out')
        return 5
    except Exception as e:
        print('[ERROR]', e)
        return 6


if __name__ == '__main__':
    sys.exit(main())
