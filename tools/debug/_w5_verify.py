"""W5 live-consumer verification for the top 3 high-fan-in DEPRECATED agents."""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "agent_deprecation" / "w5_live_consumers.json"

W5_TARGETS = [
    "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
    "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
    "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
]

EXCLUDE_DIRS = {"archives", ".git", ".venv", "__pycache__"}
EXCLUDE_PATH_PARTS = ("tools/archive", "tools\\archive", "_archived_adg_audits")

entries = []
for rel in W5_TARGETS:
    abs_path = REPO / rel
    mod_path = rel.replace("/", ".").removesuffix(".py")
    class_name = pathlib.Path(rel).stem
    doc = ""
    if abs_path.exists():
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'"""(.*?)"""', text, re.DOTALL)
        doc = (m.group(1).strip() if m else "")[:400]
    mod_re = re.compile(
        rf"(?:from\s+{re.escape(mod_path)}\s+import|"
        rf"import\s+{re.escape(mod_path)}\b)"
    )
    consumers = []
    for py in REPO.rglob("*.py"):
        try:
            rp_parts = py.relative_to(REPO).parts
        except ValueError:
            continue
        if rp_parts[0] in EXCLUDE_DIRS:
            continue
        rp = py.relative_to(REPO).as_posix()
        if any(p in rp for p in EXCLUDE_PATH_PARTS):
            continue
        if rp == rel:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if mod_re.search(text):
            consumers.append(rp)
    entries.append(
        {
            "agent_path": rel,
            "class_name": class_name,
            "module_path": mod_path,
            "docstring_head": doc,
            "live_consumer_count": len(consumers),
            "live_consumer_files": consumers,
        }
    )

OUT.write_text(json.dumps({"total": len(entries), "entries": entries}, indent=2), encoding="utf-8")
print(f"[ok] wrote {OUT}")
for e in sorted(entries, key=lambda x: x["live_consumer_count"]):
    print(f'=== {e["class_name"]} ({e["live_consumer_count"]} consumers) ===')
    print(f'  doc: {(e["docstring_head"] or "").replace(chr(10)," | ")[:180]}')
    for c in e["live_consumer_files"][:15]:
        print(f'  consumer: {c}')
    if e["live_consumer_count"] > 15:
        print(f'  ... and {e["live_consumer_count"]-15} more')
    print()
