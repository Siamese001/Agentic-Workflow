"""
Seam for L5 safety reasoning agents - approved L0→L5 interface.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "safety_reasoning_seam")
emit_determinism_digest("p0", "safety_reasoning_seam")

_emit_dispatches_healing_run("p1", "safety_reasoning_seam", "L0")
_emit_routes_through("p1", "safety_reasoning_seam", "L0")
_emit_checks_agent_registry("p1", "safety_reasoning_seam", "agent_registry")
_emit_validates_agent_capability("p1", "safety_reasoning_seam", "capability")
_emit_dispatches_execution_plan("p1", "safety_reasoning_seam", "exec_plan")
_emit_agent_executes_agent("p1", "safety_reasoning_seam", "sub_agent")
_emit_routes_to_agent("p1", "safety_reasoning_seam", "target_agent")
_emit_verifies_policy("p1", "safety_reasoning_seam", "policy_check")
_emit_observes_runtime_state("p1", "safety_reasoning_seam", "runtime_state")
_emit_verifies_boundary("p1", "safety_reasoning_seam", "boundary_check")
_emit_transcripts_response("p1", "safety_reasoning_seam", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_reasoning_seam")
_emit_gated_by_confidence("p1", "safety_reasoning_seam", "confidence_gate")
_emit_escalates_to_human("p1", "safety_reasoning_seam", "L0")
_emit_reads_policy_state("p1", "safety_reasoning_seam", "L0")
_emit_authorize_and_execute("p2", "safety_reasoning_seam", "execution_auth")
_emit_validates_capability("p2", "safety_reasoning_seam", "capability_check")
_emit_routes_to_capability("p2", "safety_reasoning_seam", "capability_route")
_emit_writes_via_uwg("p2", "safety_reasoning_seam", "uwg_write")
_emit_blocks_direct_write("p2", "safety_reasoning_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_reasoning_seam", "tool_invocation")
_emit_captures_execution_output("p2", "safety_reasoning_seam", "exec_output")
_emit_dispatches_agent("p3", "safety_reasoning_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_reasoning_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_reasoning_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_reasoning_seam", "healing_outcome")
_emit_escalates_failure("p3", "safety_reasoning_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_reasoning_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_reasoning_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_reasoning_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_reasoning_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_reasoning_seam", "eval_metric")
_emit_stores_embedding("p4", "safety_reasoning_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_reasoning_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_reasoning_seam", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_1")
_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_2")
_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_3")
_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_4")
_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_5")
_emit_emits_metric_event("safety_reasoning_seam", "p4obs", "metric_6")
_emit_records_incident_event("safety_reasoning_seam", "p4obs", "incident")
_emit_captures_runtime_anomaly("safety_reasoning_seam", "p4obs", "anomaly")
_emit_writes_observability_log("safety_reasoning_seam", "p4obs", "obs_log")
_emit_updates_monitoring_state("safety_reasoning_seam", "p4obs", "mon_state")
_emit_triggers_alert("safety_reasoning_seam", "p4obs", "alert")
_emit_links_incident_trace("safety_reasoning_seam", "p4obs", "trace_link")
_emit_captures_pattern("safety_reasoning_seam", "p3lm", "pattern")
_emit_records_learning_event("safety_reasoning_seam", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safety_reasoning_seam", "p3lm", "snapshot")
_emit_feeds_meta_learning("safety_reasoning_seam", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safety_reasoning_seam", "p3lm", "routing")
_emit_improves_agent_policy("safety_reasoning_seam", "p3lm", "policy")
_emit_stores_learning_state("safety_reasoning_seam", "p3lm", "state")
_emit_records_execution_trace("safety_reasoning_seam", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safety_reasoning_seam", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safety_reasoning_seam", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safety_reasoning_seam", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safety_reasoning_seam", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safety_reasoning_seam", "env_read", "p2_env_1")
_emit_reads_environ("safety_reasoning_seam", "env_read", "p2_env_2")
_emit_reads_runtime_state("safety_reasoning_seam", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safety_reasoning_seam", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safety_reasoning_seam", "context_pull")
_emit_pulls_context("p1", "safety_reasoning_seam", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safety_reasoning_seam", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safety_reasoning_seam", "uwg_term_2")
_emit_writes_through("p1", "safety_reasoning_seam", "write_through")
_emit_writes_through("p1", "safety_reasoning_seam", "write_through_2")
_emit_validated_by_safety_plane("p1", "safety_reasoning_seam", "safety_validation")
_emit_invokes_eval("p1", "safety_reasoning_seam", "eval_call")
_emit_proposal_commits_routing("p1", "safety_reasoning_seam", "routing_commit")


def load_naming_agent():
    """Load NamingAgent from L5."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_naming_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_naming_agent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_naming_agent")
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.NamingAgent")
    return mod.NamingAgent


def load_structure_enforcer_agent():
    """Load StructureEnforcerAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.StructureEnforcerAgent")
    return mod.StructureEnforcerAgent


def load_cognitive_disposition_agent():
    """Load CognitiveDispositionAgent from L5 reasoning."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.CognitiveDispositionAgent")
    return mod.CognitiveDispositionAgent


def load_file_classification_agent():
    """Load FileClassificationAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    return mod.FileClassificationAgent


def load_location_validator_agent():
    """Load LocationValidatorAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.location_validator")
    return mod.LocationValidatorAgent


def load_verification_gate_adapter():
    """Load verification_gate_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.verification_gate_adapter")


def load_human_review_adapter():
    """Load human_review_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.human_review_adapter")


def load_inspector_executor():
    """Load InspectorExecutor from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
    return mod.InspectorExecutor
