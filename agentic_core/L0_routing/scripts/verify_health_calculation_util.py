"""
Quick verification script to check health score calculation in dashboard.
"""

import json
import re
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verify_health_calculation_util")
emit_determinism_digest("p0", "verify_health_calculation_util")

_emit_dispatches_healing_run("p1", "verify_health_calculation_util", "L0")
_emit_routes_through("p1", "verify_health_calculation_util", "L0")
_emit_escalates_to_human("p1", "verify_health_calculation_util", "L0")
_emit_reads_policy_state("p1", "verify_health_calculation_util", "L0")


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    dashboard_path = Path("reports/autonomy_dashboard.html")
    if not dashboard_path.exists():
        print("Dashboard not found at reports/autonomy_dashboard.html")
        exit(1)
    html = dashboard_path.read_text(encoding="utf-8")
    match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
    if not match:
        print("dashboardData not found in HTML")
        exit(1)
    data = json.loads(match.group(1))
    total_row = next((r for r in data if r.get("Territory") == "TOTAL"), None)
    if not total_row:
        print("TOTAL row not found")
        exit(1)
    heal_cap = float(total_row.get("Heal Cap %", 0))
    invocation = float(total_row.get("Invocation %", 0))
    tests = float(total_row.get("Test %", 0))
    observable = float(total_row.get("Observable %", 0))
    cc_health = float(total_row.get("Complexity Health", 0))
    actual_health = float(total_row.get("Health", 0))
    expected_health = round((heal_cap + invocation + tests + observable + cc_health) / 5, 1)
    print("\n" + "=" * 80)
    print("DASHBOARD HEALTH SCORE VERIFICATION")
    print("=" * 80)
    print("\nTOTAL Row Components:")
    print(f"  Heal Capability:     {heal_cap:6.1f}%")
    print(f"  Heal Invocation:     {invocation:6.1f}%")
    print(f"  Test Coverage:       {tests:6.1f}%")
    print(f"  observability:       {observable:6.1f}%")
    print(f"  Complexity Health:   {cc_health:6.1f}%")
    print("\nHealth Score Calculation:")
    print("  Formula: (Heal Cap + Invocation + Tests + Observable + CC Health) / 5")
    print(f"  Expected: {expected_health:.1f}%")
    print(f"  Actual:   {actual_health:.1f}%")
    if abs(actual_health - expected_health) < 0.1:
        print("\nPASS: Health score correctly calculated!")
    else:
        print("\nFAIL: Health score mismatch!")
        print(f"  Difference: {abs(actual_health - expected_health):.1f}%")
        if actual_health == 100.0:
            print("\nWARNING: Health score is hardcoded to 100%!")
            print("  This is incorrect - it should be calculated from actual metrics.")
    print("=" * 80 + "\n")
    print("Sample Territory Health Scores:")
    print("-" * 80)
    for row in data[:5]:
        if row.get("Territory") == "TOTAL":
            continue
        territory = row.get("Territory", "Unknown")
        h_cap = float(row.get("Heal Cap %", 0))
        h_inv = float(row.get("Invocation %", 0))
        t = float(row.get("Test %", 0))
        o = float(row.get("Observable %", 0))
        cc = float(row.get("Complexity Health", 0))
        h = float(row.get("Health", 0))
        exp = round((h_cap + h_inv + t + o + cc) / 5, 1)
        status = "PASS" if abs(h - exp) < 0.1 else "FAIL"
        print(f"{status} {territory:30s} Health: {h:5.1f}% (Expected: {exp:5.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
