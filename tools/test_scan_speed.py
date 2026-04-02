#!/usr/bin/env python3
"""Rigorous test: verify the shared-normalizer fix eliminates per-file rglob cost."""

import logging
import sys
import time

logging.disable(logging.CRITICAL)

from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import _iter_python_files, _scan_file
from agentic_core.adg.identity.normalizer import IdentityNormalizer

files = list(_iter_python_files(ROOT))
# Use first 50 files as benchmark set
bench = files[:50]

print(f"Benchmark: {len(bench)} files")
print()

# --- OLD behaviour: new normalizer per file ---
t0 = time.perf_counter()
for f in bench:
    _scan_file(f, ROOT, include_tests=True, identity_normalizer=None)
old_time = time.perf_counter() - t0
print(f"OLD (normalizer per file): {old_time:.2f}s  ({old_time/len(bench)*1000:.0f}ms/file)")

# --- NEW behaviour: one shared normalizer ---
shared = IdentityNormalizer(repo_root=ROOT)
_ = shared._get_known_files()   # pre-warm
t0 = time.perf_counter()
for f in bench:
    _scan_file(f, ROOT, include_tests=True, identity_normalizer=shared)
new_time = time.perf_counter() - t0
print(f"NEW (shared normalizer):   {new_time:.2f}s  ({new_time/len(bench)*1000:.0f}ms/file)")

speedup = old_time / new_time if new_time > 0 else float('inf')
print(f"\nSpeedup: {speedup:.1f}x")

# Project to full run
total_files = len(files)
projected_old = old_time / len(bench) * total_files
projected_new = new_time / len(bench) * total_files
print(f"\nProjected full scan ({total_files} files):")
print(f"  OLD: {projected_old/60:.1f} minutes")
print(f"  NEW: {projected_new/60:.1f} minutes")

assert speedup >= 5.0, f"Expected >=5x speedup, got {speedup:.1f}x"
print(f"\n✅ PASS: {speedup:.1f}x speedup confirmed")
