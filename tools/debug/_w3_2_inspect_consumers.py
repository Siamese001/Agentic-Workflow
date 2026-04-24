"""For each W3.2 consumer, extract the exact usage of the deprecated agent
(import line + any class name mentions in the file body). Classify as:
- dead_import: import exists but class name never referenced in body
- class_only: referenced in type hints / isinstance / annotations only
- active_usage: instantiated or methods called
"""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
LIVE = REPO / "artifacts" / "agent_deprecation" / "w3_live_consumers.json"
OUT = REPO / "artifacts" / "agent_deprecation" / "w3_2_consumer_usage.json"

data = json.loads(LIVE.read_text(encoding="utf-8"))

report = []
for entry in data["entries"]:
    if entry["live_consumer_count"] == 0:
        continue
    cls = entry["class_name"]
    mod = entry["module_path"]
    for consumer_path in entry["live_consumer_files"]:
        abs_consumer = REPO / consumer_path
        if not abs_consumer.exists():
            continue
        text = abs_consumer.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        # Find import lines that reference the module
        import_lines = [
            (i + 1, ln.rstrip())
            for i, ln in enumerate(lines)
            if re.search(rf"(?:from\s+{re.escape(mod)}\s+import|import\s+{re.escape(mod)}\b)", ln)
        ]
        # Count non-import references to class name
        body_lines = []
        for i, ln in enumerate(lines):
            if any(i + 1 == j for j, _ in import_lines):
                continue
            if re.search(rf"\b{re.escape(cls)}\b", ln):
                body_lines.append((i + 1, ln.rstrip()))
        # Detect instantiation
        has_instantiation = any(re.search(rf"\b{re.escape(cls)}\s*\(", ln) for _, ln in body_lines)
        has_isinstance = any("isinstance" in ln and cls in ln for _, ln in body_lines)
        has_typehint_only = (
            len(body_lines) > 0
            and not has_instantiation
            and all(":" in ln or "->" in ln or "[" in ln for _, ln in body_lines)
        )
        if not body_lines:
            category = "dead_import"
        elif has_instantiation:
            category = "active_usage"
        elif has_typehint_only:
            category = "typehint_only"
        elif has_isinstance:
            category = "isinstance_check"
        else:
            category = "class_reference_only"
        report.append(
            {
                "agent": cls,
                "replacement_util": entry["replacement_util"],
                "consumer": consumer_path,
                "import_lines": import_lines,
                "body_refs": body_lines[:10],
                "body_ref_count": len(body_lines),
                "category": category,
            }
        )

OUT.write_text(json.dumps({"items": report}, indent=2), encoding="utf-8")
print(f"[ok] wrote {OUT}")
cats: dict[str, int] = {}
for r in report:
    cats[r["category"]] = cats.get(r["category"], 0) + 1
print(f"[summary] {len(report)} consumer touches")
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {n:3d} {c}")
print("\n[detail]")
for r in sorted(report, key=lambda x: (x["category"], x["agent"])):
    print(f"  [{r['category']:20s}] {r['agent']:28s} <- {r['consumer']}")
