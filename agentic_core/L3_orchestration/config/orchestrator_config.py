from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

# Configuration constants

"""configuration types for the agentic framework.

Defines OrchestratorConfig and related configuration dataclasses.
"""
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.L0_routing.config.pipeline_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
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
