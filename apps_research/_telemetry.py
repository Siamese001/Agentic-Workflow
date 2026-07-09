"""Optional telemetry bridge for standalone-safe imports.

This keeps apps_research importable even when agentic_core is absent.
All emitters degrade to no-op functions in standalone mode.
"""

from __future__ import annotations

from typing import Any

_EMITTER_NAMES = [
    "_emit_agent_executes_agent",
    "_emit_applies_guardrail",
    "_emit_authorize_and_execute",
    "_emit_blocks_direct_write",
    "_emit_captures_evaluation_metric",
    "_emit_captures_execution_output",
    "_emit_captures_pattern",
    "_emit_captures_runtime_anomaly",
    "_emit_checks_agent_registry",
    "_emit_coordinates_agents",
    "_emit_dispatches_agent",
    "_emit_dispatches_execution_plan",
    "_emit_dispatches_healing_run",
    "_emit_emits_metric_event",
    "_emit_escalates_failure",
    "_emit_escalates_to_human",
    "_emit_execution_terminates_at_uwg",
    "_emit_feeds_meta_learning",
    "_emit_gated_by_confidence",
    "_emit_hard_fails_untranscripted",
    "_emit_improves_agent_policy",
    "_emit_invokes_eval",
    "_emit_invokes_evaluation",
    "_emit_links_execution_to_snapshot",
    "_emit_links_incident_trace",
    "_emit_observes_runtime_state",
    "_emit_orchestrates_workflow",
    "_emit_proposal_commits_routing",
    "_emit_pulls_context",
    "_emit_reads_environ",
    "_emit_reads_policy_state",
    "_emit_reads_runtime_state",
    "_emit_records_execution_trace",
    "_emit_records_healing_outcome",
    "_emit_records_incident_event",
    "_emit_records_learning_event",
    "_emit_records_telemetry_event",
    "_emit_records_tool_invocation",
    "_emit_records_workflow_lineage",
    "_emit_routes_through",
    "_emit_routes_to_agent",
    "_emit_routes_to_capability",
    "_emit_signs_execution_trace",
    "_emit_snapshots_state",
    "_emit_stores_embedding",
    "_emit_stores_learning_state",
    "_emit_transcripts_response",
    "_emit_triggers_alert",
    "_emit_updates_meta_learning_state",
    "_emit_updates_monitoring_state",
    "_emit_updates_routing_strategy",
    "_emit_validated_by_safety_plane",
    "_emit_validates_agent_capability",
    "_emit_validates_capability",
    "_emit_verifies_boundary",
    "_emit_verifies_policy",
    "_emit_writes_learning_snapshot",
    "_emit_writes_observability_log",
    "_emit_writes_through",
    "_emit_writes_via_uwg",
    "emit_determinism_digest",
    "emit_replay_key",
]


def _noop(*_args: Any, **_kwargs: Any) -> None:
    return None


def _bind_trace_contract() -> None:
    try:
        from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
    except ImportError:
        trace_contract = None

    if trace_contract is None:
        class LayerSegment:
            L0_ROUTING = "L0_ROUTING"
            L1_REASONING = "L1_REASONING"
            L2_EXECUTION = "L2_EXECUTION"
            L3_ORCHESTRATION = "L3_ORCHESTRATION"
            L4_STATE = "L4_STATE"

        globals().update({name: _noop for name in _EMITTER_NAMES})
        globals()["LayerSegment"] = LayerSegment
        return

    globals().update({name: getattr(trace_contract, name) for name in _EMITTER_NAMES})
    globals()["LayerSegment"] = trace_contract.LayerSegment


_bind_trace_contract()

__all__ = ["LayerSegment", *_EMITTER_NAMES]
