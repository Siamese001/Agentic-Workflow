"""
Fact Check Engine - Hallucination prevention
Refactored from FactCheckAgent.py
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from apps_rg.engines.base_rg_engine import BaseRGEngine

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("fact_check_engine")


Logger = logging.getLogger(__name__)


class FactCheckEngine(BaseRGEngine):
    """
    Validates factual accuracy and prevents hallucinations.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.FACT_CHECK")

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self, claims: list[str], source_data: dict[str, Any]) -> dict[str, Any]:
        """
        Verify claims against source data.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FactCheckEngine.execute")

        self._mcp_audit("fact_check_start", {"claim_count": len(claims)})
        verified_claims = []
        unverified_claims = []
        for claim in claims:
            if self._verify_claim(claim, source_data):
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
        result = {
            "verified_count": len(verified_claims),
            "unverified_count": len(unverified_claims),
            "unverified_claims": unverified_claims,
            "verification_rate": len(verified_claims) / len(claims) if claims else 1.0,
        }
        if result["verification_rate"] < 0.8:
            self.record_fail(
                f"Low verification rate: {result['verification_rate']:.1%}",
                data=result,
                signal="FACT_CHECK_FAILURE",
            )
        else:
            self.record_pass(f"Fact check passed: {result['verification_rate']:.1%} verified")
        return result

    def _verify_claim(self, claim: str, source: dict[str, Any]) -> bool:
        """Verify single claim against source."""
        source_text = str(source).lower()
        claim_lower = claim.lower()
        claim_words = set(claim_lower.split())
        source_words = set(source_text.split())
        overlap = len(claim_words & source_words)
        return overlap >= len(claim_words) * 0.5
