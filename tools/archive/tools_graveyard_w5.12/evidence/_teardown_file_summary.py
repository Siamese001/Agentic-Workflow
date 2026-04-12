"""Summarize teardown guardian-exempt candidates by file."""

from __future__ import annotations

import json
from pathlib import Path

data = json.loads(Path("artifacts/adg_analysis/hitl_guardian_candidates.json").read_text())
teardowns = [d for d in data if d["sub_category"] == "teardown"]
print(f"Teardown entries: {len(teardowns)}")

by_file: dict[str, list[dict]] = {}
for t in teardowns:
    by_file.setdefault(t["source_file"], []).append(t)
print(f"Unique files: {len(by_file)}")
print()
for fpath, entries in sorted(by_file.items()):
    lines = [str(e["line_no"]) for e in entries]
    kind = entries[0]["kind"]
    func = entries[0]["func"]
    print(f"  {fpath}")
    print(f"    lines={','.join(lines)}  kind={kind}  func={func}")
