"""Compare live extraction fingerprint vs stored cache fingerprint."""

import sys

sys.path.insert(0, ".")
import json
from pathlib import Path
from agentic_core.adg.extraction.scan_cache import compute_extraction_fingerprint
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

repo_root = Path(".")
live_fp = compute_extraction_fingerprint(repo_root)
print("Live fingerprint  :", live_fp)
f"{ADG_ARTIFACTS_DIR}/cache/scan_result_cache.json"
cache_path = Path(f"{ADG_ARTIFACTS_DIR}/cache/scan_result_cache.json")
if cache_path.exists():
    stored = json.loads(cache_path.read_bytes()).get("extraction_fingerprint", "<MISSING>")
    print("Stored fingerprint:", stored)
    print("Match             :", live_fp == stored)
    if live_fp != stored:
        print("\n=> Cache WILL be invalidated on next ADG run")
    else:
        print("\n=> Cache is VALID (no extraction-layer changes detected)")
