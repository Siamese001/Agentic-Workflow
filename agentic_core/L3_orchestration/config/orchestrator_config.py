from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
