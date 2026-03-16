"""Scan execute_ssot.py for silent_swallower antipatterns using the gate's scanner."""

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

_emit_records_execution_trace("p0", "evidence", "_scan_silent_swallower")
_emit_applies_guardrail("p0", "_scan_silent_swallower", "p0_governance")
_emit_reads_policy_state("p0", "_scan_silent_swallower", "policy_binding")
_emit_snapshots_state("p0", "_scan_silent_swallower", "state_snapshot")
emit_replay_key("p0", "_scan_silent_swallower")
emit_determinism_digest("p0", "_scan_silent_swallower")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

project_root = Path(".")
scanner = AntiPatternScanner(project_root)
results = scanner.scan_file(Path("agentic_core/L0_routing/scripts/execute_ssot.py"))
print(f"result type: {type(results)}")
if isinstance(results, list):
    ss = [
        r
        for r in results
        if getattr(r, "category", None) == "silent_swallower" or "silent" in str(getattr(r, "category", ""))
    ]
    print(f"silent_swallower count={len(ss)}")
    for item in ss:
        print(f"  line={getattr(item, 'line_no', '?')}  {str(item)[:120]}")
    # Show all categories
    from collections import Counter

    cats = Counter(getattr(r, "category", str(r)) for r in results)
    print("All categories:", dict(cats))
elif isinstance(results, dict):
    for cat, items in results.items():
        if cat == "silent_swallower":
            print(f"silent_swallower count={len(items)}")
            for item in items:
                print(f"  line={item.line_no}  snippet={item.snippet[:100]}")
        elif items:
            print(f"{cat} count={len(items)}")
