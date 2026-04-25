"""Quick diagnostic for the 5 gaps the user listed."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _hdr(n: int, title: str) -> None:
    print(f"\n{'=' * 78}\n[Gap {n}] {title}\n{'=' * 78}")


# --- Gap 1: archive_old_adg.py current_ts constraint ---
_hdr(1, "Archive cleanup script: does it require current_ts -> real sqlite?")
script = _REPO / "tools/archive/archive_old_adg.py"
src = script.read_text(encoding="utf-8")
has_sqlite_constraint = (
    ("require" in src.lower() and "sqlite" in src.lower())
    or "sqlite_exists" in src.lower()
    or "must have a sqlite" in src.lower()
)
print(f"  script path:                    {script.relative_to(_REPO)}")
print(f"  requires sqlite to define 'current' run: {'YES' if has_sqlite_constraint else 'NO'}")
print(f"  STATUS:                         {'DONE' if has_sqlite_constraint else 'OPEN'}")


# --- Gap 2: memory MCP auto-projected general entities ---
_hdr(2, "Memory MCP: ADGModule_* / ADGLayer_* protection from cleanup_stale")
db = _REPO / "artifacts/memory/knowledge_graph.sqlite"
if not db.exists():
    print(f"  DB missing: {db}")
else:
    with sqlite3.connect(str(db)) as c:
        rows = c.execute(
            "SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type ORDER BY 2 DESC"
        ).fetchall()
        print("  Entity-type distribution:")
        for t, n in rows:
            print(f"    {t or '(null)':<35} {n}")
        n_adg_prefix = c.execute(
            "SELECT COUNT(*) FROM entities WHERE "
            "name LIKE 'ADGModule_%' OR name LIKE 'ADGLayer_%' OR name LIKE 'ADG:%'"
        ).fetchone()[0]
        n_general = c.execute(
            "SELECT COUNT(*) FROM entities WHERE entity_type IN ('general', 'ADGNode')"
        ).fetchone()[0]
        print(f"  ADG-prefix / ADGNode entities:  {n_general}")
        print(f"    (name-prefix matches):        {n_adg_prefix}")

mem_server = _REPO / "tools/memory/adg_memory_server.py"
mem_src = mem_server.read_text(encoding="utf-8")
protected_block_match = (
    mem_src.split("_PROTECTED_TYPES = (")[1].split(")")[0] if "_PROTECTED_TYPES = (" in mem_src else ""
)
has_adg_protection = "ADGModule" in mem_src or "ADGLayer" in mem_src or "ADGNode" in protected_block_match
print(f"  _PROTECTED_TYPES in adg_memory_server includes ADG_*: {'YES' if has_adg_protection else 'NO'}")
print(f"  STATUS:                         {'DONE' if has_adg_protection else 'OPEN'}")


# --- Gap 3: Runtime ADG coverage — which agents emit spans? ---
_hdr(3, "Runtime ADG: span emission coverage diagnostic")
rta_dir = _REPO / "agentic_core/L4_state/memory/runtime_adg"
snaps = list(rta_dir.glob("*.json")) if rta_dir.exists() else []
print(f"  runtime_adg_dir:                {rta_dir.relative_to(_REPO)}")
print(f"  snapshot count:                 {len(snaps)}")
if snaps:
    sizes = [p.stat().st_size / 1024 for p in snaps]
    print(f"  avg size KB:                    {sum(sizes) / len(sizes):.1f}")
    print(f"  sample snapshot:                {snaps[0].name}")
    try:
        sample = json.loads(snaps[0].read_text(encoding="utf-8"))
        payload_hex = sample.get("payload_hex")
        if payload_hex:
            payload = json.loads(bytes.fromhex(payload_hex).decode("utf-8"))
        else:
            payload = sample
        nodes = payload.get("nodes", [])
        span_names = {n.get("span_name") or n.get("name") for n in nodes}
        span_names.discard(None)
        print(f"    nodes in sample:              {len(nodes)}")
        print(f"    unique span names:            {sorted(span_names)[:10]}")
    except (OSError, ValueError, KeyError) as exc:
        print(f"    sample decode failed:         {exc}")
diagnostic_exists = (_REPO / "tools/debug/_runtime_adg_coverage_audit.py").exists()
print(f"  coverage audit tool exists:     {'YES' if diagnostic_exists else 'NO'}")
print(f"  STATUS:                         {'DIAGNOSTIC AVAILABLE' if diagnostic_exists else 'OPEN'}")


# --- Gap 4: system_learning activation path ---
_hdr(4, "system_learning: where is the meta-learning consumer activated?")
sl_state = _REPO / "system_learning/state"
sl_store = _REPO / "system_learning/stores"
consumer_path = _REPO / "system_learning/runtime_hitl_consumer.py"
print(f"  runtime_hitl_consumer.py exists: {'YES' if consumer_path.exists() else 'NO'}")
if consumer_path.exists():
    body = consumer_path.read_text(encoding="utf-8")
    lines = body.count("\n")
    has_main = "__main__" in body
    writes_to = [
        line.strip().split("=")[0].strip() if "=" in line else line.strip()
        for line in body.splitlines()
        if "write" in line.lower() or "persist" in line.lower() or ".save(" in line
    ][:5]
    print(f"    lines of code:                 {lines}")
    print(f"    has __main__ entry point:      {has_main}")
    print(f"    write/persist references:")
    for ref in writes_to:
        print(f"      - {ref[:120]}")
# Check where it's imported
import subprocess

res = subprocess.run(
    ["git", "grep", "-l", "runtime_hitl_consumer"], cwd=_REPO, capture_output=True, text=True, timeout=10
)
importers = [
    line for line in res.stdout.splitlines() if line and line != "system_learning/runtime_hitl_consumer.py"
]
print(f"  importers of runtime_hitl_consumer: {len(importers)}")
for p in importers[:10]:
    print(f"    - {p}")
print(
    f"  STATUS:                         {'OPEN — activation path unclear' if len(importers) < 2 else 'INVESTIGATED'}"
)


# --- Gap 5: _subsystem_gap_analysis.py hardcoded OTEL path ---
_hdr(5, "_subsystem_gap_analysis.py: OTEL path correctness")
gap_script = _REPO / "tools/debug/_subsystem_gap_analysis.py"
gap_src = gap_script.read_text(encoding="utf-8")
uses_otel_config = "otel_config" in gap_src or "build_config" in gap_src
has_hardcoded = 'Path("artifacts/otel")' in gap_src or 'Path("system_learning/runtime_adg")' in gap_src
print(f"  reads from tools.otel.otel_config: {'YES' if uses_otel_config else 'NO'}")
print(f"  still has hardcoded wrong path:    {'YES' if has_hardcoded else 'NO'}")
print(f"  STATUS:                         {'DONE' if uses_otel_config and not has_hardcoded else 'OPEN'}")


print(f"\n{'=' * 78}\nDONE\n{'=' * 78}")
