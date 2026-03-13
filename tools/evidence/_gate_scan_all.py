"""Scan all blocking files for gate violations."""

import sys

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from collections import Counter
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

project_root = Path(".")
scanner = AntiPatternScanner(project_root)

FILES = [
    "agentic_core/L5_safety/enforcement/hitl_gate.py",
    "tools/_scan_temp_folders.py",
    "tools/adg/adg_redis_ingest.py",
    "tools/evidence/_adg_confidence_audit.py",
    "tools/evidence/_adg_confidence_audit2.py",
    "tools/evidence/_scan_silent_swallower.py",
]

for f in FILES:
    p = Path(f)
    if not p.exists():
        print(f"MISSING: {f}")
        continue
    results = scanner.scan_file(p)
    if isinstance(results, list):
        cats = Counter(str(getattr(r, "category", r)).split(".")[-1].strip("'>") for r in results)
        if cats:
            print(f"\n{f}:")
            for cat, cnt in cats.items():
                print(f"  {cat}: {cnt}")
            for r in results:
                cat = str(getattr(r, "category", r)).split(".")[-1].strip("'>")
                ln = getattr(r, "line_number", "?")
                print(f"    line={ln}  cat={cat}")
