#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time, re, subprocess, threading, queue
from typing import Optional, List

import requests

CANDIDATE_PORTS: List[int] = list(range(5001, 5011)) + [8080]
BOOT_TIMEOUT = 40
TAIL_LINES = 200


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


def call(endpoint_base: str, path: str, timeout_sec: int = 600):
    url = f"{endpoint_base}{path}"
    print(f"[CALL] POST {url}")
    r = requests.post(url, json={}, timeout=timeout_sec)
    print(f"[RESP] {r.status_code}")
    if r.status_code != 200:
        print(r.text[:1000])
        raise SystemExit(2)
    return r.json()


def main():
    print("[RUN] Starting server...")
    proc = start_server()
    q = queue.Queue()
    t = threading.Thread(target=reader, args=(proc, q), daemon=True)
    t.start()

    port = detect_port(q)
    if not port:
        print("[ERROR] Server port not detected")
        try:
            proc.terminate()
        except Exception:
            pass
        return 1

    base = f"http://127.0.0.1:{port}"
    print(f"[OK] Server on {base}")

    # Profession only
    prof = call(base, '/api/search/profession-only', timeout_sec=480)
    print(f"[PROFESSION] count={prof.get('count')} source={prof.get('source')}")

    # NoFluff only
    nfj = call(base, '/api/search/nofluff-only', timeout_sec=480)
    print(f"[NOFLUFF] count={nfj.get('count')} source={nfj.get('source')} method={nfj.get('method')}")

    # Tail logs
    print("\n[TAIL]")
    tail = []
    while True:
        try:
            line = q.get(timeout=0.25)
            if line is None:
                break
            tail.append(line)
        except Exception:
            break
    for line in tail[-TAIL_LINES:]:
        sys.stdout.write(line)

    print("\n[STOP] Stopping server...")
    try:
        proc.terminate()
    except Exception:
        pass
    print("[DONE]")
    return 0


if __name__ == '__main__':
    sys.exit(main())
