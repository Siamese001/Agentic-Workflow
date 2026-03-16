"""
Reflection Engine - Post-execution learning and scoring
Refactored from RgReflectionAgent.py
"""

from __future__ import annotations

import logging
from typing import Any

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
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "reflection_engine", "p0_governance")
_emit_reads_policy_state("p0", "reflection_engine", "policy_binding")
_emit_snapshots_state("p0", "reflection_engine", "state_snapshot")
emit_replay_key("p0", "reflection_engine")
emit_determinism_digest("p0", "reflection_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ReflectionEngine(BaseRGEngine):
    """
    Reflection - Post-cycle learning and scoring.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.REFLECTION")

    async def execute(self, workflow_results: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze workflow results and extract learnings.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflectionEngine.execute")

        self._mcp_audit("reflection_start")
        reflection = {
            "overall_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "learnings": [],
            "recommendations": [],
        }
        passed_engines = [k for k, v in workflow_results.items() if v.get("passed", False)]
        failed_engines = [k for k, v in workflow_results.items() if not v.get("passed", True)]
        reflection["overall_score"] = len(passed_engines) / max(len(workflow_results), 1)
        if reflection["overall_score"] >= 0.9:
            reflection["strengths"].append("High success rate across engines")
        if failed_engines:
            reflection["weaknesses"].append(f"Failures in: {', '.join(failed_engines)}")
            reflection["recommendations"].append("Review failed engine configurations")
        for engine_name, result in workflow_results.items():
            if result.get("signal"):
                reflection["learnings"].append(f"{engine_name} signaled: {result['signal']}")
        self.record_pass("Reflection complete", data=reflection)
        return reflection
