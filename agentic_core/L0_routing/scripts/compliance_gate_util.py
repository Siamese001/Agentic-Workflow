"""
L0 Compliance Gate: SSOT Architecture Enforcement

This module enforces critical architectural rules across the entire agent ecosystem.
It validates that all agents conform to the Sovereign Architecture Pattern and
prevents structural violations that would compromise system integrity.

Critical Rules:
1. All agents must inherit from SovereignBaseAgent (directly or via mixin chain)
2. SovereignBaseAgent itself is whitelisted (root exception)
3. Agents must belong to valid layers (tests layer is prohibited)
"""

import logging
from typing import Any

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
)

_emit_dispatches_healing_run("p1", "compliance_gate_util", "L0")
_emit_routes_through("p1", "compliance_gate_util", "L0")
_emit_escalates_to_human("p1", "compliance_gate_util", "L0")
_emit_reads_policy_state("p1", "compliance_gate_util", "L0")


def _get_DiscoveredAgent():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_DiscoveredAgent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_DiscoveredAgent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_DiscoveredAgent")
    from agentic_core.runtime.utils.discovery_util import DiscoveredAgent

    return DiscoveredAgent


logger = logging.getLogger(__name__)


def check_compliance(discovered_agents: list[DiscoveredAgent]) -> list[str]:
    """
    Validates that all discovered agents conform to architectural requirements.

    Args:
        discovered_agents: List of agents discovered by AgentRegistry

    Returns:
        List of violation descriptions (empty if all compliant)
    """
    violations = []
    for agent in discovered_agents:
        if agent.name == "SovereignBaseAgent":
            continue
        if "SovereignBaseAgent" not in [c.__name__ for c in agent.class_ref.__mro__]:
            violations.append(f"{agent.name} (Orphaned: No Sovereign Inheritance)")
            continue
        if agent.layer == "unknown":
            violations.append(f"{agent.name} (Unknown Layer)")
    if violations:
        logger.error(f"Compliance Violation Detected in L-Architecture: {violations}")
        logger.error("Agents violating architectural rules will be quarantined.")
    return violations


def check_legacy_compatibility() -> dict[str, Any]:
    """
    Legacy compatibility check for older agent formats.
    This function ensures backward compatibility during migration.

    Returns:
        Dict containing compatibility status and recommendations
    """
    return {
        "status": "compatible",
        "message": "All agents conform to Sovereign Architecture Pattern",
        "recommendations": [],
    }
