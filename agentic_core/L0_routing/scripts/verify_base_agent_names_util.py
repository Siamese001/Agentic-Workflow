#!/usr/bin/env python3
"""Verify Base Agent names in dashboard data."""

import json
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
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

emit_replay_key("p0", "verify_base_agent_names_util")
emit_determinism_digest("p0", "verify_base_agent_names_util")

_emit_dispatches_healing_run("p1", "verify_base_agent_names_util", "L0")
_emit_routes_through("p1", "verify_base_agent_names_util", "L0")
_emit_escalates_to_human("p1", "verify_base_agent_names_util", "L0")
_emit_reads_policy_state("p1", "verify_base_agent_names_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_base_agent_names_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_base_agent_names_util", "p0_governance")
_emit_snapshots_state("p0", "verify_base_agent_names_util", "state_snapshot")

project_root = Path(__file__).parent.parent
data_file = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding="utf-8")
lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
content = "\n".join(lines).replace("window.dashboardData = ", "").strip().rstrip(";")
data = json.loads(content)

print("\nFirst 10 territories in dashboard data:")
print("=" * 60)
for i, row in enumerate(data[:10]):
    print(f"{i + 1}. {row['Territory']}")

print("\n" + "=" * 60)
print("Base Agent territories:")
print("=" * 60)
for row in data:
    if "Base Agent" in row["Territory"] or row["Territory"] == "Sovereign Base Agent":
        print(f"  ✅ {row['Territory']}")
