"""
agentic_core/L0_routing/config/ssot_tier_constants.py

L0-accessible re-exports of the SSOT routing/healing tier thresholds.

These constants are now sourced from path_constants.py (canonical L0 SSOT)
to eliminate duplication. L0 scripts can import directly from either location.

Source of truth: agentic_core/L0_routing/config/path_constants.py
"""

from __future__ import annotations

# Import canonical thresholds from L0 SSOT (path_constants.py)
from agentic_core.L0_routing.config.path_constants import (
    HEALING_CONFIDENCE_X,
    HEALING_CONFIDENCE_Y,
    QWEN_14B_MODEL_ID,
    SSOT_SCORE_THRESHOLD_DET,
    SSOT_SCORE_THRESHOLD_QWEN,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "ssot_tier_constants")
# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
# Now imported from path_constants.py (canonical L0 SSOT)
# HEALING_CONFIDENCE_X, HEALING_CONFIDENCE_Y defined above via import

# SSOT score thresholds for integer-score routing (S = 3C+4B+3A+2N+4F)
# SSOT_SCORE_THRESHOLD_DET, SSOT_SCORE_THRESHOLD_QWEN defined above via import

# Qwen 14B model identifier
# QWEN_14B_MODEL_ID defined above via import

__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "QWEN_14B_MODEL_ID",
    "AGENTIC_CORE_LAYERS",
    "APPS_PACKAGES",
]

# Architecture layer constants - SSOT for layer naming
AGENTIC_CORE_LAYERS = [
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
]

# Application package constants - SSOT for app package naming
APPS_PACKAGES = [
    "apps_lic",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_shared",
    "apps_underwriting_ai",
]
