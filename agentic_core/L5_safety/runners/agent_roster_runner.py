"""
L5 Runner for Agent Roster Validation.

This module provides subprocess-callable entry points for L0 scripts
to validate agent roster integrity without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.agent_roster_runner --action=validate
"""

from __future__ import annotations

import argparse
import json
import sys
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

emit_replay_key("p0", "agent_roster_runner")
emit_determinism_digest("p0", "agent_roster_runner")

_emit_dispatches_healing_run("p1", "agent_roster_runner", "L5")
_emit_routes_through("p1", "agent_roster_runner", "L5")
_emit_escalates_to_human("p1", "agent_roster_runner", "L5")
_emit_reads_policy_state("p1", "agent_roster_runner", "L5")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _get_ObservabilityProbeExecutorAgent():
    """Lazy loader for ObservabilityProbeExecutorAgent (upward L5->L6 seam)."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_ObservabilityProbeExecutorAgent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_ObservabilityProbeExecutorAgent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "_get_ObservabilityProbeExecutorAgent")
    from agentic_core.L6_observability.reasoning.observability_probe_executor import (
        ObservabilityProbeExecutorAgent,
    )

    return ObservabilityProbeExecutorAgent


def validate_agent_roster() -> dict:
    """Validate mandatory agent roster integrity."""
    try:
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import CognitiveDispositionAgent
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
        from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import FilesystemSSOTReconcilerAgent
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent
        from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent
        from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent

        DebateSynthesisAgent = _get_ObservabilityProbeExecutorAgent()
        agents = {
            "reconciler": FilesystemSSOTReconcilerAgent,
            "location": LocationHealerAgent,
            "hierarchy": HierarchyAgent,
            "arch_governor": ArchitectureGovernorAgent,
            "gravity_repair": GravityLeakRepairAgent,
            "system_architect": SystemArchitectAgent,
            "file_classification": FileClassificationAgent,
            "conversational_repair": DebateSynthesisAgent,
            "cognitive_disposition": CognitiveDispositionAgent,
            "root_hygiene": RootHygieneAgent,
        }
        integrity_errors = []
        for name, agent_cls in agents.items():
            if not hasattr(agent_cls, "__init__"):
                integrity_errors.append(f"{name}: Missing __init__")
            if not callable(agent_cls):
                integrity_errors.append(f"{name}: Not callable")
        return {
            "success": len(integrity_errors) == 0,
            "agents_validated": list(agents.keys()),
            "integrity_errors": integrity_errors,
        }
    except ImportError as e:
        return {
            "success": False,
            "error": f"Import error: {e}",
            "agents_validated": [],
            "integrity_errors": [str(e)],
        }
    # guardian: allow-silent-swallow
    except Exception as e:
        return {"success": False, "error": str(e), "agents_validated": [], "integrity_errors": [str(e)]}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="Agent Roster Runner")
    parser.add_argument("--action", choices=["validate"], required=True, help="Action to perform")
    args = parser.parse_args()
    try:
        if args.action == "validate":
            result = validate_agent_roster()
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}
        print(json.dumps(result, default=str))
        return 0 if result.get("success") else 1
    # guardian: allow-silent-swallow
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
