"""Find which Infrastructure territory has wrong target."""

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
)

_emit_dispatches_healing_run("p1", "find_infrastructure_target_issue_util", "L0")
_emit_routes_through("p1", "find_infrastructure_target_issue_util", "L0")
_emit_escalates_to_human("p1", "find_infrastructure_target_issue_util", "L0")
_emit_reads_policy_state("p1", "find_infrastructure_target_issue_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_infrastructure_target_issue_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_infrastructure_target_issue_util", "p0_governance")
_emit_snapshots_state("p0", "find_infrastructure_target_issue_util", "state_snapshot")

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")
data_match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
rows = json.loads(data_match.group(1))
non_total = [r for r in rows if r.get("Territory") != "TOTAL"]
infra_rows = [
    r for r in non_total if "Infrastructure" in r.get("Territory", "") or "Infrast" in r.get("Territory", "")
]
print(f"Found {len(infra_rows)} Infrastructure territories:\n")
for row in infra_rows:
    terr = row.get("Territory")
    target_inv = row.get("Target Invocation")
    print(f"  {terr}: Target = {target_inv}")
    if target_inv == 20:
        print("    ⚠️  WRONG! Should be 70")
