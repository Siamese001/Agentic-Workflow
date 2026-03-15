"""
ArchitectureGovernorValidatorAgent - L5 Pure Validator.

Detects architectural governance violations (import compliance, layer gravity,
naming) via StructureValidatorAgent without mutating the codebase. Emits a
structured check dict consumed by heal_architecture_governance via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "ArchitectureGovernorValidatorAgent", "p0_governance")
_emit_snapshots_state("p0", "ArchitectureGovernorValidatorAgent", "state_snapshot")

CHECK_ID = "architecture_governance"


class ArchitectureGovernorValidatorAgent:
    """L5 Certify-only validator for architectural governance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run ArchitectureGovernorAgent.heal_repository in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw governance report dict from heal_repository(dry_run=True).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ArchitectureGovernorValidatorAgent.scan"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ArchitectureGovernorValidatorAgent.scan".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent(project_root=self.project_root)
        return agent.heal_repository(dry_run=True, execute=False, target_territory=target_territory)

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        scan_result = self.scan(target_territory=target_territory)
        violations_found = scan_result.get("violations_found", 0)
        return {
            "check_id": CHECK_ID,
            "evidence": scan_result,
            "violations_count": violations_found,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
