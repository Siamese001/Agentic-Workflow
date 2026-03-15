"""
L2.3 Healing Tier Types — Mathematically Deterministic Contracts.

Defines:
- HealingTier enum (LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO)
- HealingInput (structured failure context with replay_mode)
- HealingDecision (tier + heal_confidence + reason_codes)
- InvocationRecord (replay-deterministic audit trail)
- FailureSignal (emitted by NO_TIERING agents for L2.3 consumption)

All dataclasses are frozen/immutable. Timestamp excluded from replay surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class HealingTier(str, Enum):
    """Healing model tier selected by the centralized router."""

    LOCAL_AGENT = "LOCAL_AGENT"
    QWEN_VLLM = "QWEN_VLLM"
    GEMINI_2_5_PRO = "GEMINI_2_5_PRO"


@dataclass(frozen=True, slots=True)
class HealingInput:
    """Structured failure context consumed by the L2.3 healing router.

    Attributes:
        failure_type: Category of the failure (e.g. 'syntax_error', 'import_cycle').
        error_signature: Deterministic hash or short string identifying the error class.
        trace_id: Correlation ID linking to the execution cycle.
        retry_count: Number of prior heal attempts for this failure.
        blast_radius_estimate: Bounded [0.0, 1.0] estimate of change scope.
        required_tools: Tools the healer needs (e.g. ['ast_rewrite', 'file_move']).
        violation_metadata_refs: Paths to violation artifacts for context.
        replay_mode: Enable deterministic replay mode (timestamp excluded).
        agent_id: Optional identifier of the agent requesting healing (execution profile enforcement).
        failure_entropy_class: Entropy classification of the failure (LOW/MEDIUM/HIGH).
    """

    failure_type: str
    error_signature: str
    trace_id: str
    retry_count: int
    blast_radius_estimate: float
    required_tools: tuple[str, ...] = ()
    violation_metadata_refs: tuple[str, ...] = ()
    replay_mode: bool = False
    agent_id: str = ""
    failure_entropy_class: str = "MEDIUM"

    def __post_init__(self) -> None:
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if not self.error_signature:
            raise ValueError("error_signature must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.retry_count < 0:
            raise ValueError(f"retry_count must be >= 0, got {self.retry_count}")
        if not 0.0 <= self.blast_radius_estimate <= 1.0:
            raise ValueError(f"blast_radius_estimate must be in [0.0, 1.0], got {self.blast_radius_estimate}")


@dataclass(frozen=True, slots=True)
class HealingDecision:
    """Immutable routing decision produced by the L2.3 healing router.

    Attributes:
        heal_confidence: Deterministic score in [0.0, 1.0] driving tier selection.
        tier: Selected healing tier.
        reason_codes: Deterministic list of reasons contributing to the decision.
    """

    heal_confidence: float
    tier: HealingTier
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.heal_confidence <= 1.0:
            raise ValueError(f"heal_confidence must be in [0.0, 1.0], got {self.heal_confidence}")
        if not isinstance(self.tier, HealingTier):
            raise ValueError(f"tier must be a HealingTier enum, got {type(self.tier).__name__}")


@dataclass(frozen=True, slots=True)
class InvocationRecord:
    """Immutable record with replay-deterministic fields only.

    Timestamp excluded from replay surface for mathematical determinism.
    Provider configuration and historical data versioning included.

    Attributes:
        tier: Selected healing tier
        model_id: Model identifier used
        agent_name: Agent that made the request
        trace_id: Correlation ID for the request
        heal_confidence: Confidence score for the decision
        method_called: Method name that was invoked
        provider_config_hash: Hash of provider configuration for replay
        historical_data_hash: Hash of historical data version for replay
        replay_key: Mathematical replay key (timestamp excluded)
    """

    tier: HealingTier
    model_id: str
    agent_name: str
    trace_id: str
    heal_confidence: float
    method_called: str
    provider_config_hash: str
    historical_data_hash: str
    replay_key: str
    response_text: str | None = None


@dataclass(frozen=True, slots=True)
class FailureSignal:
    """Structured signal emitted by NO_TIERING agents on failure.

    L2.3 consumes this to perform healing tier routing on behalf of the agent.
    The agent itself MUST NOT select a healing model.

    Attributes:
        source_agent: Name of the agent emitting the signal.
        failure_type: Category of the failure.
        error_signature: Deterministic identifier for the error class.
        trace_id: Correlation ID.
        context: Arbitrary structured context for the healer.
        retry_count: Number of prior attempts.
        blast_radius_estimate: Bounded [0.0, 1.0].
    """

    source_agent: str
    failure_type: str
    error_signature: str
    trace_id: str
    context: dict
    retry_count: int = 0
    blast_radius_estimate: float = 0.0

    def __post_init__(self) -> None:
        if not self.source_agent:
            raise ValueError("source_agent must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")

    def to_healing_input(
        self, required_tools: tuple[str, ...] = (), violation_metadata_refs: tuple[str, ...] = ()
    ) -> HealingInput:
        """Convert FailureSignal to HealingInput for L2.3 router consumption."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FailureSignal.to_healing_input", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FailureSignal.to_healing_input", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FailureSignal.to_healing_input")
        return HealingInput(
            agent_id=self.source_agent,
            failure_type=self.failure_type,
            error_signature=self.error_signature,
            trace_id=self.trace_id,
            retry_count=self.retry_count,
            blast_radius_estimate=self.blast_radius_estimate,
            required_tools=required_tools,
            violation_metadata_refs=violation_metadata_refs,
        )


__all__ = ["FailureSignal", "HealingDecision", "HealingInput", "HealingTier", "InvocationRecord"]
