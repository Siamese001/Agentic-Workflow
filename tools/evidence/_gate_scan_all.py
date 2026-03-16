"""Scan all blocking files for gate violations."""

import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_gate_scan_all")
_emit_applies_guardrail("p0", "_gate_scan_all", "p0_governance")
_emit_reads_policy_state("p0", "_gate_scan_all", "policy_binding")
_emit_snapshots_state("p0", "_gate_scan_all", "state_snapshot")
emit_replay_key("p0", "_gate_scan_all")
emit_determinism_digest("p0", "_gate_scan_all")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
