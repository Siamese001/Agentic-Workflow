"""Extract hard import file locations for the 15 optional packages from the audit JSON."""

import json
from pathlib import Path

TARGETS = [
    "numpy",
    "chromadb",
    "duckdb",
    "rank-bm25",
    "scikit-learn",
    "pydantic-settings",
    "beautifulsoup4",
    "dash",
    "fastapi",
    "livereload",
    "pandas",
    "playwright",
    "plotly",
    "waitress",
    "rich",
]

data = json.loads(Path("docs/reports/plans/dependency_audit_scan_runtime.json").read_text())
for pkg in TARGETS:
    info = data["dist_summary"].get(pkg, {})
    hard = info.get("hard_files", [])
    if hard:
        print(f"\n{pkg} ({len(hard)} hard):")
        for f in hard:
            print(f"  {f}")
    else:
        print(f"\n{pkg}: 0 hard (already guarded)")
