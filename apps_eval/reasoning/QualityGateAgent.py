"""
Quality Gate Agent — apps_eval/reasoning

Agent for enforcing evaluation quality gates.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_agent,
    _emit_gated_by_confidence,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class QualityGateAgent:
    """Agent for enforcing quality gates on evaluation results."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the quality gate agent."""
        self.config = config or {}
        self._default_threshold = self.config.get("quality_threshold", 0.70)

        emit_replay_key("quality_gate", "agent_init")
        emit_determinism_digest("quality_gate", "agent_init")
        _emit_applies_guardrail("p0", "quality_gate_agent", "agent_init")
        _emit_snapshots_state("p0", "quality_gate_agent", "agent_state")

    async def evaluate_quality_gate(
        self,
        evaluation_results: dict[str, Any],
        quality_threshold: float | None = None,
    ) -> dict[str, Any]:
        """Evaluate if results pass quality gates.

        Args:
            evaluation_results: Results to evaluate
            quality_threshold: Optional override threshold

        Returns:
            Gate evaluation result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "QualityGateAgent.evaluate_quality_gate",
        )
        _emit_orchestrates_workflow("p3", "quality_gate_agent", "gate_workflow")
        _emit_dispatches_agent("p3", "quality_gate_agent", "gate_dispatch")
        _emit_records_telemetry_event("p4", "quality_gate_agent", "gate_start")

        threshold = quality_threshold or self._default_threshold
        overall_score = evaluation_results.get("overall_score", 0.0)
        passed = overall_score >= threshold

        _emit_gated_by_confidence("p1", "quality_gate_agent", f"score:{overall_score}")

        if not passed:
            _emit_applies_guardrail("p0", "quality_gate_agent", "quality_violation")

        _log.info(
            "Quality gate %s: score=%.2f, threshold=%.2f",
            "PASSED" if passed else "FAILED",
            overall_score,
            threshold,
        )
        _emit_records_telemetry_event(
            "p4", "quality_gate_agent", f"gate_complete:{'passed' if passed else 'failed'}",
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "passed": passed,
            "overall_score": overall_score,
            "threshold": threshold,
            "violations": [] if passed else ["Overall score below threshold"],
        }

    @staticmethod
    def _make_trace_id(results: dict[str, Any]) -> str:
        """Generate a deterministic trace ID."""
        score = results.get("overall_score", 0.0)
        raw = f"gate:{score:.3f}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
