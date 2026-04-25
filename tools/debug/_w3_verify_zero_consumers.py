"""For each of the 21 W3 agents, count LIVE import references via regex grep.

An import match is:
  from <module.path> import <ClassName>
  import <module.path>
  from <module.path> import (...<ClassName>...)

Self-references (inside the agent's own file) are excluded.
archives/ and tools/archive/ paths are excluded.
"""

from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
MAP = REPO / "artifacts" / "agent_deprecation" / "w3_replacement_map.json"
OUT = REPO / "artifacts" / "agent_deprecation" / "w3_live_consumers.json"

EXCLUDE_DIRS = {"archives", ".git", ".venv", "__pycache__"}
EXCLUDE_PATH_PARTS = ("tools/archive", "tools\\archive", "_archived_adg_audits")

data = json.loads(MAP.read_text(encoding="utf-8"))

results = []
for entry in data["entries"]:
    rel = entry["agent_path"]
    # derive module path + class name from file path
    mod_path = rel.replace("/", ".").removesuffix(".py")
    class_name = pathlib.Path(rel).stem  # same as file stem for these
    # Build conservative regex: anything referencing the full module path,
    # OR importing the class name with a hint of the module
    mod_re = re.compile(
        rf"(?:from\s+{re.escape(mod_path)}\s+import|"
        rf"import\s+{re.escape(mod_path)}\b)"
    )

    consumers = []
    for py in REPO.rglob("*.py"):
        try:
            rel_parts = py.relative_to(REPO).parts
        except ValueError:
            continue
        if rel_parts[0] in EXCLUDE_DIRS:
            continue
        rp = py.relative_to(REPO).as_posix()
        if any(p in rp for p in EXCLUDE_PATH_PARTS):
            continue
        if rp == rel:  # self
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if mod_re.search(text):
            consumers.append(rp)

    results.append(
        {
            "agent_path": rel,
            "class_name": class_name,
            "module_path": mod_path,
            "replacement_util": entry["inferred_replacement"],
            "live_consumer_count": len(consumers),
            "live_consumer_files": consumers,
        }
    )

OUT.write_text(json.dumps({"total": len(results), "entries": results}, indent=2), encoding="utf-8")
print(f"[ok] wrote {OUT}")
zero = [r for r in results if r["live_consumer_count"] == 0]
nonzero = [r for r in results if r["live_consumer_count"] > 0]
print(f"[ok] zero live consumers: {len(zero)}/{len(results)}")
print(f"[ok] with live consumers: {len(nonzero)}")
for r in sorted(results, key=lambda x: x["live_consumer_count"]):
    name = r["agent_path"].split("/")[-1]
    print(f"  {r['live_consumer_count']:3d} {name:50s}")
