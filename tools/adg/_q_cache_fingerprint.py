"""Report extraction_fingerprint stored in scan cache and basic stats."""

import json
from pathlib import Path

cache_path = Path("artifacts/adg/cache/scan_result_cache.json")
if not cache_path.exists():
    print("Cache file not found:", cache_path)
else:
    raw = json.loads(cache_path.read_bytes())
    print("version            :", raw.get("version"))
    print("extraction_fingerprint:", raw.get("extraction_fingerprint", "<MISSING>"))
    print("entry count        :", len(raw.get("entries", {})))
