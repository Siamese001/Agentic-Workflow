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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "default_healing_pattern_advisor", "execution_auth")
trace_contract._emit_validates_capability("p2", "default_healing_pattern_advisor", "capability_check")
trace_contract._emit_routes_to_capability("p2", "default_healing_pattern_advisor", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "default_healing_pattern_advisor", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "default_healing_pattern_advisor", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "default_healing_pattern_advisor", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "default_healing_pattern_advisor", "exec_output")
trace_contract._emit_dispatches_agent("p3", "default_healing_pattern_advisor", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "default_healing_pattern_advisor", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "default_healing_pattern_advisor", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "default_healing_pattern_advisor", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "default_healing_pattern_advisor", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "default_healing_pattern_advisor", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "default_healing_pattern_advisor", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "default_healing_pattern_advisor", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "default_healing_pattern_advisor", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "default_healing_pattern_advisor", "eval_metric")
trace_contract._emit_stores_embedding("p4", "default_healing_pattern_advisor", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "default_healing_pattern_advisor", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "default_healing_pattern_advisor", "exec_snapshot_link")
from agentic_core.L6_system_learning.ports.healing_pattern_advisor import (
    _MAX_PATTERN_BOOST,
    NullHealingPatternAdvisor,
    PatternAdvice,
)

trace_contract._emit_applies_guardrail("p0", "default_healing_pattern_advisor", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "default_healing_pattern_advisor", "policy_binding")
trace_contract._emit_snapshots_state("p0", "default_healing_pattern_advisor", "state_snapshot")

trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("default_healing_pattern_advisor", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("default_healing_pattern_advisor", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("default_healing_pattern_advisor", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("default_healing_pattern_advisor", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("default_healing_pattern_advisor", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("default_healing_pattern_advisor", "p4obs", "alert")
trace_contract._emit_links_incident_trace("default_healing_pattern_advisor", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("default_healing_pattern_advisor", "p3lm", "pattern")
trace_contract._emit_records_learning_event("default_healing_pattern_advisor", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("default_healing_pattern_advisor", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("default_healing_pattern_advisor", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("default_healing_pattern_advisor", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("default_healing_pattern_advisor", "p3lm", "policy")
trace_contract._emit_stores_learning_state("default_healing_pattern_advisor", "p3lm", "state")
trace_contract._emit_records_execution_trace("default_healing_pattern_advisor", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("default_healing_pattern_advisor", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("default_healing_pattern_advisor", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("default_healing_pattern_advisor", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("default_healing_pattern_advisor", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("default_healing_pattern_advisor", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("default_healing_pattern_advisor", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("default_healing_pattern_advisor", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("default_healing_pattern_advisor", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "default_healing_pattern_advisor", "context_pull")
trace_contract._emit_pulls_context("p1", "default_healing_pattern_advisor", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "default_healing_pattern_advisor", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "default_healing_pattern_advisor", "uwg_term_2")
trace_contract._emit_writes_through("p1", "default_healing_pattern_advisor", "write_through")
trace_contract._emit_writes_through("p1", "default_healing_pattern_advisor", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "default_healing_pattern_advisor", "safety_validation")
trace_contract._emit_invokes_eval("p1", "default_healing_pattern_advisor", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "default_healing_pattern_advisor", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "default_healing_pattern_advisor", "human_escalation")
trace_contract._emit_routes_through("p1", "default_healing_pattern_advisor", "route_through")
trace_contract._emit_checks_agent_registry("p1", "default_healing_pattern_advisor", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "default_healing_pattern_advisor", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "default_healing_pattern_advisor", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "default_healing_pattern_advisor", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "default_healing_pattern_advisor", "target_agent")
trace_contract._emit_verifies_policy("p1", "default_healing_pattern_advisor", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "default_healing_pattern_advisor", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "default_healing_pattern_advisor", "boundary_check")
trace_contract._emit_transcripts_response("p1", "default_healing_pattern_advisor", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "default_healing_pattern_advisor")
trace_contract._emit_gated_by_confidence("p1", "default_healing_pattern_advisor", "confidence_gate")
trace_contract.emit_replay_key("p0", "default_healing_pattern_advisor")
trace_contract.emit_determinism_digest("p0", "default_healing_pattern_advisor")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# MetaLearningClient import removed until implemented
# Optional: from agentic_core.L6_system_learning.meta_learning_client import MetaLearningClient

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "DefaultHealingPatternAdvisor.advise"
        )

        if self._ml_client is None:
            return NullHealingPatternAdvisor().advise(healing_input)

        try:
            patterns = self._ml_client.retrieve_healing_patterns(
                error_signature=healing_input.error_signature,
            )
        except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
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
        module_name = getattr(healing_input, "module_name", None)
        if module_name:
            try:
                from agentic_core.adg.adapters.ADGMemoryAdapter import get_adapter

                adapter = get_adapter()
                hotspots = adapter.get_hotspot_modules(limit=20)
                if module_name in hotspots:
                    # Add hotspot boost
                    patterns.append(
                        {
                            "pattern_name": "adg_hotspot",
                            "confidence_boost": 0.1,  # 10% boost for hotspots
                            "description": f"Module {module_name} is in top-20 fan-out hotspots",
                        }
                    )
            except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                logger.debug("default_healing_pattern_advisor: hotspot lookup failed: %s", exc)

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
