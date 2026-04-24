"""W4 discovery + live-consumer verification for 7 medium-fan-in DEPRECATED agents.

Targets from W0 assessment (fan-in 15-46 via ADG resolves_callsite).
"""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "agent_deprecation" / "w4_live_consumers.json"

W4_TARGETS = [
    "agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py",
    "agentic_core/L5_safety/reasoning/RedSentinelAgent.py",
    "agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py",
    "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
    "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
    "agentic_core/L5_safety/reasoning/StructureHealerAgent.py",
    "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
]

REPLACEMENT_PATTERNS = [
    re.compile(r"[Uu]se\s+([a-zA-Z_][\w\.]+)\s+instead"),
    re.compile(r"[Rr]eplaced?\s+by\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Mm]igrat\w+\s+to\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Cc]onsolidated\s+into\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Mm]oved\s+to\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Ss]ee\s+([a-zA-Z_][\w\.]+)\s+for"),
]

EXCLUDE_DIRS = {"archives", ".git", ".venv", "__pycache__"}
EXCLUDE_PATH_PARTS = ("tools/archive", "tools\\archive", "_archived_adg_audits")


def extract_docstring(path: pathlib.Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = re.search(r'"""(.*?)"""', text, re.DOTALL)
    return m.group(1).strip() if m else ""


def infer_replacement(doc: str) -> str | None:
    for pat in REPLACEMENT_PATTERNS:
        m = pat.search(doc)
        if m:
            return m.group(1).rstrip(".,:;")
    return None


entries = []
for rel in W4_TARGETS:
    abs_path = REPO / rel
    if not abs_path.exists():
        entries.append({"agent_path": rel, "missing": True})
        continue
    doc = extract_docstring(abs_path)
    repl = infer_replacement(doc)
    mod_path = rel.replace("/", ".").removesuffix(".py")
    class_name = pathlib.Path(rel).stem
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
            "replacement_util": repl,
            "docstring_head": doc[:300],
            "live_consumer_count": len(consumers),
            "live_consumer_files": consumers,
        }
    )

OUT.write_text(json.dumps({"total": len(entries), "entries": entries}, indent=2), encoding="utf-8")
print(f"[ok] wrote {OUT}")
zero = sum(1 for e in entries if e.get("live_consumer_count") == 0)
print(f"[ok] zero live consumers: {zero}/{len(entries)}")
for e in sorted(entries, key=lambda x: x.get("live_consumer_count", 999)):
    name = e["agent_path"].split("/")[-1]
    cnt = e.get("live_consumer_count", "?")
    repl = e.get("replacement_util")
    print(f'  {cnt:>3} {name:40s} -> {repl}')
