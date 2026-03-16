"""
Run unified HierarchyAgent in dry-run mode (healing_enabled=False)
This consolidates both HierarchyEnforcerAgent and HierarchyHealerAgent functionality.

Location: Uses the NEW unified agent at agentic_core/L5_safety/enforcement/HierarchyAgent.py
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "run_hierarchy_agent_dry_run_util")
emit_determinism_digest("p0", "run_hierarchy_agent_dry_run_util")

_emit_dispatches_healing_run("p1", "run_hierarchy_agent_dry_run_util", "L0")
_emit_routes_through("p1", "run_hierarchy_agent_dry_run_util", "L0")
_emit_escalates_to_human("p1", "run_hierarchy_agent_dry_run_util", "L0")
_emit_reads_policy_state("p1", "run_hierarchy_agent_dry_run_util", "L0")

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


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
    print("=" * 80)
    print("UNIFIED HIERARCHY AGENT - DRY RUN MODE")
    print("=" * 80)
    print("Using: agentic_core/L5_safety/enforcement/HierarchyAgent.py")
    print("Validating hierarchy (no changes will be made)...\n")
    project_root = Path.cwd()
    result = invoke_hierarchy_agent(action="dry_run", project_root=project_root)
    if result.get("success"):
        print(f"\n{result.get('message', 'Dry run complete')}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)
    print("\nTo apply these changes, run with healing_enabled=True")
    print(
        "Note: There is an older HierarchyAgent in validators/ - this uses the new unified version in guardrails/"
    )


if __name__ == "__main__":
    main()
