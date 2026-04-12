#!/usr/bin/env python3
"""Timed checkpoint profiler for generate_full_adg.py hang diagnosis"""

import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Timer:
    def __init__(self):
        self.start = time.time()
        self.last = self.start

    def checkpoint(self, label):
        now = time.time()
        elapsed = now - self.last
        total = now - self.start
        print(f"[PROFILE] +{elapsed:.2f}s (total {total:.2f}s) -- {label}", flush=True)
        self.last = now


T = Timer()


def timeout_handler(signum, frame):
    print(f"\n[PROFILE] *** TIMEOUT at {time.time() - T.start:.1f}s ***", flush=True)
    import traceback

    traceback.print_stack(frame)
    sys.exit(1)


# Set 120s timeout
try:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)
except AttributeError as e:
    # TODO: Fix programming error - AttributeError should not occur
    pass  # Windows doesn't have SIGALRM

T.checkpoint("START")

# Step 1: imports
T.checkpoint("imports done")

# Step 2: sys.path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
T.checkpoint("sys.path set")

# Step 3: import lifecycle_trace_contract (this fires hard_fails_untranscripted)
T.checkpoint("about to import lifecycle_trace_contract")
T.checkpoint("lifecycle_trace_contract imported")

# Step 4: import ADGStaticScanner
T.checkpoint("about to import ADGStaticScanner")
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

T.checkpoint("ADGStaticScanner imported")

# Step 5: instantiate scanner
T.checkpoint("about to instantiate scanner")
cache_path = ROOT / "artifacts" / "adg" / "scan_result_cache.json"
scanner = ADGStaticScanner(repo_root=ROOT, cache_path=cache_path)
T.checkpoint("scanner instantiated")

# Step 6: call scanner.scan() — this is likely the hang
T.checkpoint("about to call scanner.scan()")

# Patch _scan_file to track per-file timing
import agentic_core.adg.extraction.static_scanner as sm

original_scan_file = sm._scan_file
file_count = [0]
slow_files = []


def timed_scan_file(filepath, repo_root, include_tests=True):
    t0 = time.time()
    result = original_scan_file(filepath, repo_root, include_tests)
    elapsed = time.time() - t0
    file_count[0] += 1
    n = file_count[0]
    if n <= 5 or n % 500 == 0:
        print(f"[PROFILE]   file #{n}: {elapsed:.3f}s -- {filepath.name}", flush=True)
    if elapsed > 2.0:
        slow_files.append((elapsed, str(filepath)))
        print(f"[PROFILE]   *** SLOW FILE {elapsed:.2f}s: {filepath}", flush=True)
    return result


sm._scan_file = timed_scan_file

result = scanner.scan()
sm._scan_file = original_scan_file

T.checkpoint(f"scanner.scan() complete: {len(result.modules)} modules, {len(result.edges)} edges")
T.checkpoint(
    f"cache hits={result.manifest.cache_hits} misses={result.manifest.cache_misses} rate={result.manifest.cache_hit_rate:.1%}"
)

if slow_files:
    print("\n[PROFILE] TOP SLOW FILES:")
    for elapsed, path in sorted(slow_files, reverse=True)[:10]:
        print(f"  {elapsed:.2f}s  {path}")

print(f"\n[PROFILE] DONE. Total time: {time.time() - T.start:.1f}s")
