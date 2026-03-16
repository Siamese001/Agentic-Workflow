"""
Fix duplicate const realAgentData declarations in autonomy_dashboard.html

This script removes all but the first occurrence of realAgentData.
"""

import re

from agentic_core.L5_safety.config.structure_blueprint_config import DASHBOARD_DIR, get_validated_project_root
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "fix_duplicate_realagentdata")
_emit_applies_guardrail("p0", "fix_duplicate_realagentdata", "p0_governance")
_emit_reads_policy_state("p0", "fix_duplicate_realagentdata", "policy_binding")
_emit_snapshots_state("p0", "fix_duplicate_realagentdata", "state_snapshot")
emit_replay_key("p0", "fix_duplicate_realagentdata")
emit_determinism_digest("p0", "fix_duplicate_realagentdata")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def fix_duplicates():
    """Remove duplicate realAgentData declarations."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    print("Reading dashboard HTML...")
    html = dashboard_path.read_text(encoding="utf-8")
    pattern = (
        "// Real per-agent data \\(replaces generateMockAgentData\\)\\s*const realAgentData = \\{[^}]*\\};"
    )
    matches = list(re.finditer(pattern, html, re.DOTALL))
    print(f"Found {len(matches)} realAgentData declarations")
    if len(matches) <= 1:
        print("✅ No duplicates found")
        return
    print(f"Removing {len(matches) - 1} duplicate declarations...")
    for match in reversed(matches[1:]):
        html = html[: match.start()] + html[match.end() :]
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"✅ Fixed! Removed {len(matches) - 1} duplicates")
    print(f"   Kept first declaration at position {matches[0].start()}")


if __name__ == "__main__":
    fix_duplicates()
