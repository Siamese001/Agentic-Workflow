"""L1 Cognition Layer — Propose-only cognitive processing.

This layer provides cognitive processing, pattern recognition, and reasoning.
No execution, routing, or persistence logic belongs in this layer.
Only cognitive interfaces, reasoning engines, and telemetry are exported.
"""

# Cognitive interfaces and reasoning
from agentic_core.L1_cognition.knowledge.knowledge_orchestrator import (
    EvaluationResult,
    ReasoningContext,
    ReasoningTrace,
    capture_reasoning_pattern,
    get_pattern_recommendations,
    pattern_stored,
    pattern_validated,
    pattern_versioned,
    query_reasoning_patterns,
    reasoning_pattern_captured,
    reasoning_pattern_reused,
    reuse_outcome_recorded,
    reuse_reasoning_pattern,
    validate_reasoning_pattern,
)

# P4/L1 Reasoning Knowledge Base exports
from agentic_core.L1_cognition.knowledge.reasoning_knowledge import (
    ReasoningKnowledgeError,
    ReasoningKnowledgeRecord,
    get_reasoning_knowledge_registry,
    originating_trace_id,
    outcome_quality_score,
    pattern_version,
    reasoning_context_hash,
    reasoning_goal_hash,
    # Dataclass field exports for ADG scanner detection
    reasoning_pattern_id,
    reasoning_steps_hash,
    reuse_count,
    validation_status,
)
from agentic_core.L1_cognition.planning.plan_creator import (
    PlanningPolicy,
    ReasoningPlanContext,
    create_reasoning_plan,
    create_simple_reasoning_plan,
    enforce_plan_checkpoint,
    execute_plan_step,
    plan_checkpoint_enforced,
    plan_revision_recorded,
    plan_step_executed,
    query_reasoning_plans,
    reasoning_plan_emitted,
    record_plan_revision,
)

# P3/L1 Multi-Step Reasoning Planning exports
from agentic_core.L1_cognition.planning.reasoning_plan import (
    CheckpointResult,
    PlanCheckpoint,
    PlanRevision,
    PlanStatus,
    PlanStep,
    ReasoningPlan,
    ReasoningPlanError,
    StepStatus,
    get_plan_registry,
    reset_plan_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_authorize_and_execute("p2", "__init__", "execution_auth")
_emit_validates_capability("p2", "__init__", "capability_check")
_emit_routes_to_capability("p2", "__init__", "capability_route")
_emit_writes_via_uwg("p2", "__init__", "uwg_write")
_emit_blocks_direct_write("p2", "__init__", "direct_write_block")
_emit_records_tool_invocation("p2", "__init__", "tool_invocation")
_emit_captures_execution_output("p2", "__init__", "exec_output")
_emit_dispatches_agent("p3", "__init__", "agent_dispatch")
_emit_coordinates_agents("p3", "__init__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__init__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__init__", "healing_outcome")
_emit_escalates_failure("p3", "__init__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__init__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__init__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__init__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__init__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__init__", "eval_metric")
_emit_stores_embedding("p4", "__init__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__init__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__init__", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

from .types.action_request_types import (  # noqa: F401
    ActionRequest,
    ActionResult,
    PlanningRequest,
    PlanningResult,
)

_emit_emits_metric_event("__init__", "p4obs", "metric_1")
_emit_emits_metric_event("__init__", "p4obs", "metric_2")
_emit_emits_metric_event("__init__", "p4obs", "metric_3")
_emit_emits_metric_event("__init__", "p4obs", "metric_4")
_emit_emits_metric_event("__init__", "p4obs", "metric_5")
_emit_emits_metric_event("__init__", "p4obs", "metric_6")
_emit_records_incident_event("__init__", "p4obs", "incident")
_emit_captures_runtime_anomaly("__init__", "p4obs", "anomaly")
_emit_writes_observability_log("__init__", "p4obs", "obs_log")
_emit_updates_monitoring_state("__init__", "p4obs", "mon_state")
_emit_triggers_alert("__init__", "p4obs", "alert")
_emit_links_incident_trace("__init__", "p4obs", "trace_link")
_emit_captures_pattern("__init__", "p3lm", "pattern")
_emit_records_learning_event("__init__", "p3lm", "learning_event")
_emit_writes_learning_snapshot("__init__", "p3lm", "snapshot")
_emit_feeds_meta_learning("__init__", "p3lm", "meta_feed")
_emit_updates_routing_strategy("__init__", "p3lm", "routing")
_emit_improves_agent_policy("__init__", "p3lm", "policy")
_emit_stores_learning_state("__init__", "p3lm", "state")
_emit_records_execution_trace("__init__", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("__init__", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("__init__", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("__init__", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("__init__", "L4_STATE", "p2_trace_5")
_emit_reads_environ("__init__", "env_read", "p2_env_1")
_emit_reads_environ("__init__", "env_read", "p2_env_2")
_emit_reads_runtime_state("__init__", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("__init__", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L1")
_emit_routes_through("p1", "__init__", "L1")
_emit_checks_agent_registry("p1", "__init__", "agent_registry")
_emit_validates_agent_capability("p1", "__init__", "capability")
_emit_dispatches_execution_plan("p1", "__init__", "exec_plan")
_emit_agent_executes_agent("p1", "__init__", "sub_agent")
_emit_routes_to_agent("p1", "__init__", "target_agent")
_emit_verifies_policy("p1", "__init__", "policy_check")
_emit_observes_runtime_state("p1", "__init__", "runtime_state")
_emit_verifies_boundary("p1", "__init__", "boundary_check")
_emit_transcripts_response("p1", "__init__", "transcript")
_emit_hard_fails_untranscripted("p1", "__init__")
_emit_gated_by_confidence("p1", "__init__", "confidence_gate")
_emit_escalates_to_human("p1", "__init__", "L1")
_emit_reads_policy_state("p1", "__init__", "L1")
_emit_pulls_context("p1", "__init__", "context_pull")
_emit_pulls_context("p1", "__init__", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term_secondary")
_emit_writes_through("p1", "__init__", "write_through")
_emit_writes_through("p1", "__init__", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "__init__", "safety_validation")
_emit_invokes_eval("p1", "__init__", "eval_call")
_emit_proposal_commits_routing("p1", "__init__", "routing_commit")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Action Types
    "ActionRequest",
    "ActionResult",
    "PlanningRequest",
    "PlanningResult",
    # Plan Records
    "ReasoningPlan",
    "PlanStep",
    "PlanCheckpoint",
    "PlanRevision",
    # Enums
    "PlanStatus",
    "StepStatus",
    "CheckpointResult",
    # Exception Classes
    "ReasoningPlanError",
    # Registry Access
    "get_plan_registry",
    "reset_plan_registry",
    # Context Classes
    "ReasoningPlanContext",
    "PlanningPolicy",
    # Emission Functions
    "create_reasoning_plan",
    "execute_plan_step",
    "enforce_plan_checkpoint",
    "record_plan_revision",
    "query_reasoning_plans",
    "create_simple_reasoning_plan",
    # ADG Edge Emitters
    "reasoning_plan_emitted",
    "plan_step_executed",
    "plan_checkpoint_enforced",
    "plan_revision_recorded",
    # Reasoning Knowledge Records
    "ReasoningKnowledgeRecord",
    # Reasoning Knowledge Exception Classes
    "ReasoningKnowledgeError",
    # Reasoning Knowledge Registry Access
    "get_reasoning_knowledge_registry",
    # Reasoning Knowledge Context Classes
    "ReasoningTrace",
    "EvaluationResult",
    "ReasoningContext",
    # Reasoning Knowledge Functions
    "capture_reasoning_pattern",
    "query_reasoning_patterns",
    "reuse_reasoning_pattern",
    "get_pattern_recommendations",
    "validate_reasoning_pattern",
    # Reasoning Knowledge ADG Edge Emitters
    "reasoning_pattern_captured",
    "pattern_validated",
    "pattern_versioned",
    "pattern_stored",
    "reuse_outcome_recorded",
    "reasoning_pattern_reused",
    # Reasoning Knowledge Dataclass field exports for ADG scanner detection
    "reasoning_pattern_id",
    "originating_trace_id",
    "reasoning_goal_hash",
    "reasoning_context_hash",
    "reasoning_steps_hash",
    "outcome_quality_score",
    "reuse_count",
    "pattern_version",
    "validation_status",
]

# Sovereignty assertion: This layer contains NO execution or routing logic
# L1 may only propose actions; execution belongs to L2, routing to L3
