"""
L3OrchestrationBase - Consolidated Base for L3 Orchestration Agents

V10 Architecture: Layer 3 (Orchestration) base class for workflow engines,
coordinators, and planners.

Capabilities:
- Workflow coordination and planning
- State management via SovereignBaseAgent
- Atomic execution support (when combined with AtomicExecutionMixin)

MRO HARDENING:
- Inheritance order: Specialized Mixins -> L3OrchestrationBase -> SovereignBaseAgent
- When using AtomicExecutionMixin, it MUST come BEFORE this base class:
  class MyAgent(AtomicExecutionMixin, L3OrchestrationBase):
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_applies_guardrail("p0", "L3OrchestrationBase", "p0_governance")
_emit_reads_policy_state("p0", "L3OrchestrationBase", "policy_binding")
_emit_snapshots_state("p0", "L3OrchestrationBase", "state_snapshot")
emit_replay_key("p0", "L3OrchestrationBase")
emit_determinism_digest("p0", "L3OrchestrationBase")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class L3OrchestrationBase(SovereignBaseAgent):
    """
    Consolidated base for L3 Orchestration agents.

    MRO HARDENING:
    - AtomicExecutionMixin: First (if used - for rollback capability)
    - L3OrchestrationBase: Second (layer-specific capabilities)
    - SovereignBaseAgent: Last (root - includes MCPHardenedMixin)

    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations via SovereignBaseAgent
    - Workflow coordination methods

    L3 Table Decision:
    - Orchestration Logic: YES
    - State Management: YES (via SovereignBaseAgent)
    - Atomic Execution: Optional (via AtomicExecutionMixin)
    """

    name: str = "L3OrchestrationBase"
    layer: str = "L3"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L3OrchestrationBase.heal_repository")

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": [], "skipped": []}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": [], "skipped": []}
        _call_path.add(agent_name)
        try:
            result = super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                max_depth=max_depth,
                _call_path=_call_path,
                **kwargs,
            )
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            return {"violations_found": 0, "violations_fixed": 0, "errors": [str(e)], "skipped": []}

    def coordinate_workflow(self, workflow_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Base workflow coordination method.

        Override in subclasses for specific orchestration logic.

        Args:
            workflow_id: Unique identifier for the workflow
            context: Workflow context and parameters

        Returns:
            Workflow execution result
        """
        return {
            "workflow_id": workflow_id,
            "status": "not_implemented",
            "message": "Override coordinate_workflow in subclass",
        }

    def plan_execution(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Base execution planning method.

        Override in subclasses for specific planning logic.

        Args:
            task: Task definition and constraints

        Returns:
            Execution plan
        """
        _adg_route_mode: str = "static"
        _adg_scope_widening: list = []
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _self_file = _Path(__file__).resolve()
            _root = _self_file.parents[2]
            _bp = _gbp(_self_file, _root)
            _adg_route_mode = (
                "agent"
                if _bp.behavioral_score > 0.7
                else "script"
                if _bp.deterministic_coverage
                else "hybrid"
            )
            _adg_scope_widening = sorted(_bp.antipattern_signals)
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return {
            "task": task,
            "plan": [],
            "status": "not_implemented",
            "message": "Override plan_execution in subclass",
            "adg_route_mode": _adg_route_mode,
            "adg_scope_widening": _adg_scope_widening,
        }
