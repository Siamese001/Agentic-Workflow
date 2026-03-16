"""Debug which territories have mismatched targets."""

import json
import re
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "debug_target_mismatch_util")
emit_determinism_digest("p0", "debug_target_mismatch_util")

_emit_dispatches_healing_run("p1", "debug_target_mismatch_util", "L0")
_emit_routes_through("p1", "debug_target_mismatch_util", "L0")
_emit_escalates_to_human("p1", "debug_target_mismatch_util", "L0")
_emit_reads_policy_state("p1", "debug_target_mismatch_util", "L0")

_emit_records_execution_trace("p0", "evidence", "debug_target_mismatch_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_target_mismatch_util", "p0_governance")
_emit_snapshots_state("p0", "debug_target_mismatch_util", "state_snapshot")

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")
data_match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
rows = json.loads(data_match.group(1))
non_total = [r for r in rows if r.get("Territory") != "TOTAL"]
print("Checking all territories for target mismatches:\n")
mismatches = []
for row in non_total:
    target_inv = row.get("Target Invocation")
    territory = row.get("Territory", "")
    expected = None
    if "L0 Maintenance" in territory:
        if "Infrastructure" in territory or "Infrast" in territory:
            expected = 70
        else:
            expected = 20
    elif "Infrastructure" in territory or "Infrast" in territory:
        expected = 70
    elif "Base Cl" in territory:
        expected = "N/A"
    else:
        expected = 100
    if target_inv != expected:
        mismatches.append((territory, target_inv, expected))
        print(f"❌ {territory}")
        print(f"   Actual: {target_inv}, Expected: {expected}\n")
if not mismatches:
    print("✅ All territories have correct targets!")
else:
    print(f"\nTotal mismatches: {len(mismatches)}")
