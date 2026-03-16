"""
L2.3 Tiering Allowlist — Compile-Time Frozen Governance.

ONLY agents in TIERING_ALLOWLIST may invoke the centralized healing tier router.
All other agents MUST emit FailureSignal and let L2.3 handle tier selection.

This allowlist is compile-time frozen - no CSV loading, no runtime mutation.
"""

from __future__ import annotations

import logging

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

emit_replay_key("p0", "tiering_allowlist")
emit_determinism_digest("p0", "tiering_allowlist")

_emit_dispatches_healing_run("p1", "tiering_allowlist", "L2")
_emit_routes_through("p1", "tiering_allowlist", "L2")
_emit_escalates_to_human("p1", "tiering_allowlist", "L2")
_emit_reads_policy_state("p1", "tiering_allowlist", "L2")

logger = logging.getLogger(__name__)
TIERING_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("CodeHealerAgent", "agentic_core/L5_safety/reasoning/CodeHealerAgent.py"),
        ("GravityLeakRepairAgent", "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py"),
        ("IntegrityGateExecutorAgent", "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py"),
        ("LocationHealerAgent", "agentic_core/L5_safety/reasoning/LocationHealerAgent.py"),
        ("SafetyExecutorAgent", "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py"),
        ("StructureHealerAgent", "agentic_core/L5_safety/reasoning/StructureHealerAgent.py"),
        ("TypeHintFixerAgent", "agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py"),
        ("DispatchOutreachToolsAgent", "apps_lic/reasoning/DispatchOutreachToolsAgent.py"),
        ("OutreachValidationExecutorAgent", "apps_lic/reasoning/OutreachValidationExecutorAgent.py"),
        ("DispatchResumeToolsAgent", "apps_rg/reasoning/DispatchResumeToolsAgent.py"),
        ("remediation_dispatcher", "agentic_core/L2_execution/scripts/remediation_dispatcher.py"),
    }
)
TIERING_ALLOWLIST_AGENT_NAMES: frozenset[str] = frozenset((name for name, _ in TIERING_ALLOWLIST))
TIERING_ALLOWLIST_FILE_PATHS: frozenset[str] = frozenset((path for _, path in TIERING_ALLOWLIST))


def _validate_allowlist_sovereignty() -> None:
    """Validate allowlist invariants at module import time."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_validate_allowlist_sovereignty", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_validate_allowlist_sovereignty", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_validate_allowlist_sovereignty")
    logger.info("Validating compile-time frozen TIERING_ALLOWLIST...")
    if not isinstance(TIERING_ALLOWLIST, frozenset):
        raise RuntimeError("TIERING_ALLOWLIST must be frozenset for compile-time freezing")
    if not isinstance(TIERING_ALLOWLIST_AGENT_NAMES, frozenset):
        raise RuntimeError("TIERING_ALLOWLIST_AGENT_NAMES must be frozenset for compile-time freezing")
    agent_names = list(TIERING_ALLOWLIST_AGENT_NAMES)
    if len(agent_names) != len(set(agent_names)):
        raise RuntimeError("Duplicate agent names detected in TIERING_ALLOWLIST")
    expected_agents = {"CodeHealerAgent", "DispatchOutreachToolsAgent", "DispatchResumeToolsAgent"}
    missing_agents = expected_agents - TIERING_ALLOWLIST_AGENT_NAMES
    if missing_agents:
        raise RuntimeError(f"Expected agents missing from TIERING_ALLOWLIST: {missing_agents}")
    logger.info(
        f"TIERING_ALLOWLIST validated: {len(TIERING_ALLOWLIST)} agents, {len(TIERING_ALLOWLIST_AGENT_NAMES)} unique names"
    )


def is_tiering_allowed(agent_name: str) -> bool:
    """Check if agent is in compile-time frozen allowlist.

    Args:
        agent_name: Agent name to check

    Returns:
        True if agent is in TIERING_ALLOWLIST, False otherwise
    """
    return agent_name in TIERING_ALLOWLIST_AGENT_NAMES


def is_tiering_allowed_by_path(file_path: str) -> bool:
    """Check if a file path is in the compile-time frozen allowlist.

    Args:
        file_path: File path to check

    Returns:
        True if file path is in TIERING_ALLOWLIST, False otherwise
    """
    normalized = file_path.replace("\\", "/")
    return normalized in TIERING_ALLOWLIST_FILE_PATHS


_validate_allowlist_sovereignty()
__all__ = [
    "TIERING_ALLOWLIST",
    "TIERING_ALLOWLIST_AGENT_NAMES",
    "TIERING_ALLOWLIST_FILE_PATHS",
    "is_tiering_allowed",
    "is_tiering_allowed_by_path",
]
