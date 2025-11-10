#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time, re, subprocess, threading, queue
from typing import Optional, List
import requests

CANDIDATE_PORTS: List[int] = list(range(5001, 5011)) + [8080]
BOOT_TIMEOUT = 40
POLL_INTERVAL = 2.0
MAX_WAIT = 600  # 10 minutes


def start_server():
    env = os.environ.copy()
    env['PORT'] = ''
    proc = subprocess.Popen([sys.executable, 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
    return proc


def reader(proc, q):
    for line in proc.stdout:
        q.put(line)
    q.put(None)


def detect_port(q) -> Optional[int]:
    pat1 = re.compile(r"Flask szerver indítása porton:\s*(\d+)")
    pat2 = re.compile(r"Running on .*:(\d+)")
    start = time.time()
    found = None
    while time.time() - start < BOOT_TIMEOUT and found is None:
        try:
            while True:
                line = q.get_nowait()
                if line is None:
                    break
                sys.stdout.write(line)
                m = pat1.search(line) or pat2.search(line)
                if m:
                    found = int(m.group(1))
        except Exception:
            pass
        if found is None:
            for p in CANDIDATE_PORTS:
                try:
                    r = requests.get(f"http://127.0.0.1:{p}/api/status", timeout=1.2)
                    if r.status_code == 200:
                        print(f"[DETECT] status OK on {p}")
                        return p
                except Exception:
                    continue
        time.sleep(0.4)
    return found


def main():
    print('[RUN] Starting server...')
    proc = start_server()
    q = queue.Queue()
    t = threading.Thread(target=reader, args=(proc, q), daemon=True)
    t.start()

    port = detect_port(q)
    if not port:
        print('[ERROR] Server port not detected')
        try:
            proc.terminate()
        except Exception:
            pass
        return 1

    base = f"http://127.0.0.1:{port}"
    print(f"[OK] Server on {base}")

    # Reset state first
    try:
        requests.post(f"{base}/api/reset", timeout=5)
    except Exception:
        pass

    # Start async quick search
    print('[CALL] POST /api/search/async {"mode":"quick"}')
    r = requests.post(f"{base}/api/search/async", json={"mode": "quick"}, timeout=30)
    if r.status_code not in (200, 202):
        print('[ERROR] Could not start async search:', r.status_code, r.text[:500])
        proc.terminate()
        return 2
    tid = r.json().get('task_id')
    print(f"[TASK] id={tid}")

    # Poll progress
    start_wait = time.time()
    while time.time() - start_wait < MAX_WAIT:
        try:
            pr = requests.get(f"{base}/api/progress/{tid}", timeout=10)
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

    # Fetch result
    rr = requests.get(f"{base}/api/result/{tid}", timeout=30)
    if rr.status_code == 200:
        data = rr.json()
        jobs = data.get('jobs', [])
        total = data.get('total_jobs', len(jobs))
        profession = sum(1 for j in jobs if 'profession' in str(j.get('Forrás') or j.get('forras') or '').lower())
        nofluff = sum(1 for j in jobs if 'no fluff' in str(j.get('Forrás') or j.get('forras') or '').lower())
        print('='*70)
        print('[RESULTS - ASYNC QUICK]')
        print(f'Total jobs: {total}')
        print(f' - Profession.hu: {profession}')
        print(f' - No Fluff Jobs: {nofluff}')
        print('='*70)
    else:
        print('[INFO] result status:', rr.status_code, rr.text[:500])

    print('\n[STOP] Stopping server...')
    try:
        proc.terminate()
    except Exception:
        pass
    print('[DONE]')
    return 0


if __name__ == '__main__':
    sys.exit(main())
