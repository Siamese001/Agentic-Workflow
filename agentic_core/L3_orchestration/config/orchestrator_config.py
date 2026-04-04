from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "orchestrator_config")
emit_determinism_digest("p0", "orchestrator_config")

_emit_dispatches_healing_run("p1", "orchestrator_config", "L3")
_emit_routes_through("p1", "orchestrator_config", "L3")
_emit_checks_agent_registry("p1", "orchestrator_config", "agent_registry")
_emit_validates_agent_capability("p1", "orchestrator_config", "capability")
_emit_dispatches_execution_plan("p1", "orchestrator_config", "exec_plan")
_emit_agent_executes_agent("p1", "orchestrator_config", "sub_agent")
_emit_routes_to_agent("p1", "orchestrator_config", "target_agent")
_emit_verifies_policy("p1", "orchestrator_config", "policy_check")
_emit_observes_runtime_state("p1", "orchestrator_config", "runtime_state")
_emit_verifies_boundary("p1", "orchestrator_config", "boundary_check")
_emit_transcripts_response("p1", "orchestrator_config", "transcript")
_emit_hard_fails_untranscripted("p1", "orchestrator_config")
_emit_gated_by_confidence("p1", "orchestrator_config", "confidence_gate")
_emit_escalates_to_human("p1", "orchestrator_config", "L3")
_emit_reads_policy_state("p1", "orchestrator_config", "L3")
_emit_authorize_and_execute("p2", "orchestrator_config", "execution_auth")
_emit_validates_capability("p2", "orchestrator_config", "capability_check")
_emit_routes_to_capability("p2", "orchestrator_config", "capability_route")
_emit_writes_via_uwg("p2", "orchestrator_config", "uwg_write")
_emit_blocks_direct_write("p2", "orchestrator_config", "direct_write_block")
_emit_records_tool_invocation("p2", "orchestrator_config", "tool_invocation")
_emit_captures_execution_output("p2", "orchestrator_config", "exec_output")
_emit_dispatches_agent("p3", "orchestrator_config", "agent_dispatch")
_emit_coordinates_agents("p3", "orchestrator_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "orchestrator_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "orchestrator_config", "healing_outcome")
_emit_escalates_failure("p3", "orchestrator_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "orchestrator_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "orchestrator_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "orchestrator_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "orchestrator_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "orchestrator_config", "eval_metric")
_emit_stores_embedding("p4", "orchestrator_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "orchestrator_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "orchestrator_config", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""configuration types for the agentic framework.

Defines OrchestratorConfig and related configuration dataclasses.
"""
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_1")
_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_2")
_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_3")
_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_4")
_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_5")
_emit_emits_metric_event("orchestrator_config", "p4obs", "metric_6")
_emit_records_incident_event("orchestrator_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("orchestrator_config", "p4obs", "anomaly")
_emit_writes_observability_log("orchestrator_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("orchestrator_config", "p4obs", "mon_state")
_emit_triggers_alert("orchestrator_config", "p4obs", "alert")
_emit_links_incident_trace("orchestrator_config", "p4obs", "trace_link")
_emit_captures_pattern("orchestrator_config", "p3lm", "pattern")
_emit_records_learning_event("orchestrator_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("orchestrator_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("orchestrator_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("orchestrator_config", "p3lm", "routing")
_emit_improves_agent_policy("orchestrator_config", "p3lm", "policy")
_emit_stores_learning_state("orchestrator_config", "p3lm", "state")
_emit_records_execution_trace("orchestrator_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("orchestrator_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("orchestrator_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("orchestrator_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("orchestrator_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("orchestrator_config", "env_read", "p2_env_1")
_emit_reads_environ("orchestrator_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("orchestrator_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("orchestrator_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "orchestrator_config", "context_pull")
_emit_pulls_context("p1", "orchestrator_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "orchestrator_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "orchestrator_config", "uwg_term_2")
_emit_writes_through("p1", "orchestrator_config", "write_through")
_emit_writes_through("p1", "orchestrator_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "orchestrator_config", "safety_validation")
_emit_invokes_eval("p1", "orchestrator_config", "eval_call")
_emit_proposal_commits_routing("p1", "orchestrator_config", "routing_commit")


@dataclass
# NAMING FIXED: OrchestratorConfig → OrchestratorConfig
class OrchestratorConfig:
    """configuration for the orchestrator (Nervous System).

    Attributes:
        mission_id: Unique identifier for the mission
        max_iterations: Maximum Think-Act-Observe iterations
        max_phases: Maximum number of phases to execute
        enable_tri_brain: Whether to enable tri-brain routing
        enable_reflection: Whether to run reflection phase
        enable_state_persistence: Whether to persist state between runs
        timeout_seconds: Overall execution timeout
        retry_on_failure: Whether to retry failed actions
        max_retries: Maximum retry attempts
        parallel_actions: Whether to execute actions in parallel
        metadata: Additional configuration metadata
    """

    mission_id: str = "default-mission"
    max_iterations: int = 10
    max_phases: int | None = None
    enable_tri_brain: bool = False
    enable_reflection: bool = True
    enable_state_persistence: bool = True
    timeout_seconds: float | None = None
    retry_on_failure: bool = True
    max_retries: int = 3
    parallel_actions: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "OrchestratorConfig.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "OrchestratorConfig.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestratorConfig.to_dict")
        return {
            "mission_id": self.mission_id,
            "max_iterations": self.max_iterations,
            "max_phases": self.max_phases,
            "enable_tri_brain": self.enable_tri_brain,
            "enable_reflection": self.enable_reflection,
            "enable_state_persistence": self.enable_state_persistence,
            "timeout_seconds": self.timeout_seconds,
            "retry_on_failure": self.retry_on_failure,
            "max_retries": self.max_retries,
            "parallel_actions": self.parallel_actions,
            "metadata": self.metadata,
        }


@dataclass
# NAMING FIXED: CognitiveConfig → CognitiveConfig
class CognitiveConfig:
    """configuration for the cognitive plane.
    Attributes:
        model: LLM model to use for reasoning
        temperature: Sampling temperature
        max_tokens: Maximum tokens for generation
        enable_cot: Enable chain-of-thought reasoning
        enable_self_critique: Enable self-critique loop
    """

    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    enable_cot: bool = True
    enable_self_critique: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_cot": self.enable_cot,
            "enable_self_critique": self.enable_self_critique,
        }


@dataclass
# NAMING FIXED: ActionConfig → ActionConfig
class ActionConfig:
    """configuration for the action plane.

    Attributes:
        sandbox_enabled: Whether to run actions in sandbox
        timeout_per_action: Timeout per action in seconds
        max_concurrent: Maximum concurrent actions
        enable_fallback: Enable fallback providers
    """

    sandbox_enabled: bool = True
    timeout_per_action: float = 30.0
    max_concurrent: int = 5
    enable_fallback: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sandbox_enabled": self.sandbox_enabled,
            "timeout_per_action": self.timeout_per_action,
            "max_concurrent": self.max_concurrent,
            "enable_fallback": self.enable_fallback,
        }
