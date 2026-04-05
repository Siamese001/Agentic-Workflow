"""Profile the ADG scanner to identify the 50s bottleneck with 99.7% cache hits."""

from __future__ import annotations

import cProfile
import io
import pathlib
import pstats
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

cache_path = ROOT / "artifacts" / "adg" / "cache" / "scan_result_cache.json"
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)

pr = cProfile.Profile()
pr.enable()
result = scanner.scan(commit_sha=commit)
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(30)
print(s.getvalue())

print(f"Modules: {len(result.modules)}")
print(f"Edges: {len(result.edges)}")
print(f"Cache hits: {result.manifest.cache_hits}")
print(f"Cache misses: {result.manifest.cache_misses}")
print(f"Cache rate: {result.manifest.cache_hit_rate:.1%}")
