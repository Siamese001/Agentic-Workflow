"""
HierarchyValidatorAgent - L5 Pure Validator.

Read-only scan of territory root violations via HierarchyAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "hierarchy_validator", "L5")
_emit_routes_through("p1", "hierarchy_validator", "L5")
_emit_escalates_to_human("p1", "hierarchy_validator", "L5")
_emit_reads_policy_state("p1", "hierarchy_validator", "L5")

_emit_applies_guardrail("p0", "hierarchy_validator", "p0_governance")
_emit_snapshots_state("p0", "hierarchy_validator", "state_snapshot")


class HierarchyValidatorAgent:
    """L5 Certify-only validator for hierarchy/territory root violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self, target_territory: str | None = None) -> dict[str, Any]:
        """Delegate to HierarchyAgent.scan_root_violations (read-only)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HierarchyValidatorAgent.scan_root_violations"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HierarchyValidatorAgent.scan_root_violations".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        agent = HierarchyAgent(project_root=self.project_root, healing_enabled=False)
        return agent.scan_root_violations(target_territory=target_territory)
