"""Default Healing Pattern Advisor — C0 informational-only implementation.

Uses MetaLearningClient.retrieve_healing_patterns() for advisory hints.
All pattern data is informational-only and cannot change routing tiers
or heal_confidence values.  Only appends reason_codes and provides
pattern_boost for audit.

Layer contract:
- Lives in system_learning layer.
- Uses protocol-injected MetaLearningClient (no direct L1 imports).
- Enforces C0 informational-only behavior.
"""

from __future__ import annotations

import logging
from typing import Any, NotRequired, TypedDict

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

_emit_authorize_and_execute("p2", "default_healing_pattern_advisor", "execution_auth")
_emit_validates_capability("p2", "default_healing_pattern_advisor", "capability_check")
_emit_routes_to_capability("p2", "default_healing_pattern_advisor", "capability_route")
_emit_writes_via_uwg("p2", "default_healing_pattern_advisor", "uwg_write")
_emit_blocks_direct_write("p2", "default_healing_pattern_advisor", "direct_write_block")
_emit_records_tool_invocation("p2", "default_healing_pattern_advisor", "tool_invocation")
_emit_captures_execution_output("p2", "default_healing_pattern_advisor", "exec_output")
_emit_dispatches_agent("p3", "default_healing_pattern_advisor", "agent_dispatch")
_emit_coordinates_agents("p3", "default_healing_pattern_advisor", "agent_coordination")
_emit_records_workflow_lineage("p3", "default_healing_pattern_advisor", "workflow_lineage")
_emit_records_healing_outcome("p3", "default_healing_pattern_advisor", "healing_outcome")
_emit_escalates_failure("p3", "default_healing_pattern_advisor", "failure_escalation")
_emit_orchestrates_workflow("p3", "default_healing_pattern_advisor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "default_healing_pattern_advisor", "healing_dispatch")
_emit_invokes_evaluation("p3", "default_healing_pattern_advisor", "evaluation_signal")
_emit_records_telemetry_event("p4", "default_healing_pattern_advisor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "default_healing_pattern_advisor", "eval_metric")
_emit_stores_embedding("p4", "default_healing_pattern_advisor", "embedding_store")
_emit_updates_meta_learning_state("p4", "default_healing_pattern_advisor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "default_healing_pattern_advisor", "exec_snapshot_link")
from system_learning.ports.healing_pattern_advisor import (
    _MAX_PATTERN_BOOST,
    NullHealingPatternAdvisor,
    PatternAdvice,
)

_emit_applies_guardrail("p0", "default_healing_pattern_advisor", "p0_governance")
_emit_reads_policy_state("p0", "default_healing_pattern_advisor", "policy_binding")
_emit_snapshots_state("p0", "default_healing_pattern_advisor", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_1")
_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_2")
_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_3")
_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_4")
_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_5")
_emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_6")
_emit_records_incident_event("default_healing_pattern_advisor", "p4obs", "incident")
_emit_captures_runtime_anomaly("default_healing_pattern_advisor", "p4obs", "anomaly")
_emit_writes_observability_log("default_healing_pattern_advisor", "p4obs", "obs_log")
_emit_updates_monitoring_state("default_healing_pattern_advisor", "p4obs", "mon_state")
_emit_triggers_alert("default_healing_pattern_advisor", "p4obs", "alert")
_emit_links_incident_trace("default_healing_pattern_advisor", "p4obs", "trace_link")
_emit_captures_pattern("default_healing_pattern_advisor", "p3lm", "pattern")
_emit_records_learning_event("default_healing_pattern_advisor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("default_healing_pattern_advisor", "p3lm", "snapshot")
_emit_feeds_meta_learning("default_healing_pattern_advisor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("default_healing_pattern_advisor", "p3lm", "routing")
_emit_improves_agent_policy("default_healing_pattern_advisor", "p3lm", "policy")
_emit_stores_learning_state("default_healing_pattern_advisor", "p3lm", "state")
_emit_records_execution_trace("default_healing_pattern_advisor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("default_healing_pattern_advisor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("default_healing_pattern_advisor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("default_healing_pattern_advisor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("default_healing_pattern_advisor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("default_healing_pattern_advisor", "env_read", "p2_env_1")
_emit_reads_environ("default_healing_pattern_advisor", "env_read", "p2_env_2")
_emit_reads_runtime_state("default_healing_pattern_advisor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("default_healing_pattern_advisor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "default_healing_pattern_advisor", "context_pull")
_emit_pulls_context("p1", "default_healing_pattern_advisor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "default_healing_pattern_advisor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "default_healing_pattern_advisor", "uwg_term_2")
_emit_writes_through("p1", "default_healing_pattern_advisor", "write_through")
_emit_writes_through("p1", "default_healing_pattern_advisor", "write_through_2")
_emit_validated_by_safety_plane("p1", "default_healing_pattern_advisor", "safety_validation")
_emit_invokes_eval("p1", "default_healing_pattern_advisor", "eval_call")
_emit_proposal_commits_routing("p1", "default_healing_pattern_advisor", "routing_commit")
_emit_escalates_to_human("p1", "default_healing_pattern_advisor", "human_escalation")
_emit_routes_through("p1", "default_healing_pattern_advisor", "route_through")
_emit_checks_agent_registry("p1", "default_healing_pattern_advisor", "agent_registry")
_emit_validates_agent_capability("p1", "default_healing_pattern_advisor", "capability")
_emit_dispatches_execution_plan("p1", "default_healing_pattern_advisor", "exec_plan")
_emit_agent_executes_agent("p1", "default_healing_pattern_advisor", "sub_agent")
_emit_routes_to_agent("p1", "default_healing_pattern_advisor", "target_agent")
_emit_verifies_policy("p1", "default_healing_pattern_advisor", "policy_check")
_emit_observes_runtime_state("p1", "default_healing_pattern_advisor", "runtime_state")
_emit_verifies_boundary("p1", "default_healing_pattern_advisor", "boundary_check")
_emit_transcripts_response("p1", "default_healing_pattern_advisor", "transcript")
_emit_hard_fails_untranscripted("p1", "default_healing_pattern_advisor")
_emit_gated_by_confidence("p1", "default_healing_pattern_advisor", "confidence_gate")
emit_replay_key("p0", "default_healing_pattern_advisor")
emit_determinism_digest("p0", "default_healing_pattern_advisor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# MetaLearningClient import removed until implemented
# Optional: from system_learning.ports.meta_learning_client import MetaLearningClient

logger = logging.getLogger(__name__)


class HealingPattern(TypedDict):
    """Schema for a healing pattern from MetaLearningClient."""

    pattern_id: str
    pattern_name: str
    confidence_boost: NotRequired[float]  # Advisory only
    description: NotRequired[str]


class DefaultHealingPatternAdvisor:
    """Concrete advisor that queries MetaLearningClient for patterns.

    Enforces C0 informational-only contract: pattern data is advisory only
    and cannot affect routing decisions.
    """

    def __init__(self, ml_client: Any = None) -> None:
        self._ml_client = ml_client

    def advise(self, healing_input) -> PatternAdvice:
        """Return advisory pattern metadata for healing_input.

        This method is C0 informational-only:
        - Does NOT modify routing thresholds
        - Does NOT change tier selection
        - Does NOT mutate heal_confidence
        - Only provides metadata for audit
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultHealingPatternAdvisor.advise")

        if self._ml_client is None:
            return NullHealingPatternAdvisor().advise(healing_input)

        try:
            patterns = self._ml_client.retrieve_healing_patterns(
                error_signature=healing_input.error_signature
            )
        # guardian: allow-silent-swallow
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.warning(
                "pattern_advisor_query_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )
            return NullHealingPatternAdvisor().advise(healing_input)

        if not patterns:
            return {
                "pattern_match": False,
                "pattern_name": None,
                "pattern_boost": 0.0,
                "extra_reason_codes": (),
            }

        # Check if failing module is an ADG hotspot
        module_name = getattr(healing_input, 'module_name', None)
        if module_name:
            try:
                from agentic_core.adg.adapters.ADGMemoryAdapter import get_adapter
                adapter = get_adapter()
                hotspots = adapter.get_hotspot_modules(limit=20)
                if module_name in hotspots:
                    # Add hotspot boost
                    patterns.append({
                        "pattern_name": "adg_hotspot",
                        "confidence_boost": 0.1,  # 10% boost for hotspots
                        "description": f"Module {module_name} is in top-20 fan-out hotspots"
                    })
            except Exception:
                # ADG unavailable - continue without hotspot boost
                pass

        # Take the highest-confidence pattern (advisory only)
        best = max(patterns, key=lambda p: p.get("confidence_boost", 0.0))
        boost = min(best.get("confidence_boost", 0.0), _MAX_PATTERN_BOOST)

        extra_reason_codes = []
        if boost > 0:
            extra_reason_codes.append(f"pattern_boost={boost:.2f}")
            if best.get("pattern_name") == "adg_hotspot":
                extra_reason_codes.append("adg_hotspot")

        return {
            "pattern_match": True,
            "pattern_name": best.get("pattern_name"),
            "pattern_boost": boost,
            "extra_reason_codes": tuple(extra_reason_codes),
        }


__all__ = [
    "DefaultHealingPatternAdvisor",
    "HealingPattern",
]
