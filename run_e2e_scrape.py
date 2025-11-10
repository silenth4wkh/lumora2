#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated end-to-end scraper runner:
 - Starts Flask app (app.py) in a child process
 - Detects active port from logs or by probing
 - Runs combined search (/api/search) for IT
 - Prints summary and recent logs
 - Shuts down the Flask process
"""
import os
import sys
import time
import re
import subprocess
import threading
import queue
from typing import Optional, List

try:
    import requests
except Exception as e:
    print(f"[ERROR] requests import failed: {e}")
    sys.exit(1)

CANDIDATE_PORTS: List[int] = list(range(5001, 5011)) + [8080]
LOG_LINES_TO_SHOW: int = 200
SEARCH_TIMEOUT_SEC: int = 600
SERVER_BOOT_TIMEOUT_SEC: int = 40


def start_flask() -> subprocess.Popen:
    env = os.environ.copy()
    # Ensure local runs don't force a specific port
    env["PORT"] = ""
    print("[RUN] Starting Flask server (app.py)...")
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    return proc


def log_reader(proc: subprocess.Popen, out_queue: queue.Queue):
    assert proc.stdout is not None
    for line in proc.stdout:
        out_queue.put(line)
    out_queue.put(None)


def detect_port(out_queue: queue.Queue) -> Optional[int]:
    """Try to detect the port from logs and probing /api/status."""
    pattern_port_info = re.compile(r"Flask szerver indítása porton:\s*(\d+)")
    pattern_running = re.compile(r"Running on .*:(\d+)")

    start = time.time()
    found_port: Optional[int] = None

    print("[WAIT] Waiting for server to come up (<= 40s)...")
    while time.time() - start < SERVER_BOOT_TIMEOUT_SEC and found_port is None:
        # Consume logs for port hints
        try:
            while True:
                line = out_queue.get_nowait()
                if line is None:
                    break
                sys.stdout.write(line)
                m = pattern_port_info.search(line) or pattern_running.search(line)
                if m:
                    found_port = int(m.group(1))
        except Exception:
            pass

        # Probe common ports
        if found_port is None:
            for p in CANDIDATE_PORTS:
                try:
                    r = requests.get(f"http://127.0.0.1:{p}/api/status", timeout=1.2)
                    if r.status_code == 200:
                        print(f"[DETECT] /api/status OK on port {p}")
                        found_port = p
                        break
                except Exception:
                    continue
        if found_port is None:
            time.sleep(0.4)
    return found_port


def run_search(port: int) -> dict:
    base_url = f"http://127.0.0.1:{port}"
    print(f"[CALL] POST {base_url}/api/search ...")
    start = time.time()
    r = requests.post(
        f"{base_url}/api/search",
        json={"categories": ["IT"]},
        timeout=SEARCH_TIMEOUT_SEC,
    )
    duration = time.time() - start
    print(f"[INFO] Search completed in {duration:.1f}s, status={r.status_code}")
    if r.status_code != 200:
        print("[RESP]", r.text[:1000])
        raise SystemExit(2)
    return {"duration": duration, "data": r.json()}


def main() -> int:
    flask_proc = start_flask()
    out_q: queue.Queue = queue.Queue()
    t = threading.Thread(target=log_reader, args=(flask_proc, out_q), daemon=True)
    t.start()

    port = detect_port(out_q)
    if not port:
        print("[ERROR] Could not detect active server port.")
        try:
            flask_proc.terminate()
        except Exception:
            pass
        return 1

    print(f"[OK] Server detected on port {port}")

    # Run the combined scrape
    try:
        result = run_search(port)
        data = result["data"]
        jobs = data.get("jobs", [])
        total = data.get("total_jobs", len(jobs))
        profession = sum(1 for j in jobs if 'profession' in str(j.get('Forrás') or j.get('forras') or '').lower())
        nofluff = sum(1 for j in jobs if 'no fluff' in str(j.get('Forrás') or j.get('forras') or '').lower())
        print("=" * 70)
        print("[RESULTS]")
        print(f"Total jobs: {total}")
        print(f" - Profession.hu: {profession}")
        print(f" - No Fluff Jobs: {nofluff}")
        print(f" - Duration: {result['duration']:.1f}s")
        print("=" * 70)
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Search request timed out")
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")

    # Drain recent logs
    print("\n[TAIL] Recent server logs:")
    tail: List[str] = []
    while True:
        try:
            line = out_q.get(timeout=0.25)
            if line is None:
                break
            tail.append(line)
        except Exception:
            break
    for line in tail[-LOG_LINES_TO_SHOW:]:
        sys.stdout.write(line)

    # Shutdown
    print("\n[STOP] Stopping Flask server...")
    try:
        flask_proc.terminate()
    except Exception:
        pass
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
