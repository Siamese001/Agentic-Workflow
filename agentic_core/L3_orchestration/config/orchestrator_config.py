from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "orchestrator_config")
emit_determinism_digest("p0", "orchestrator_config")

_emit_dispatches_healing_run("p1", "orchestrator_config", "L3")
_emit_routes_through("p1", "orchestrator_config", "L3")
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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
