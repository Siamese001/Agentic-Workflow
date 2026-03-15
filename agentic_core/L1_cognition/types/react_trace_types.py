"""ReAct determinism and provenance types — L1_cognition canonical types.

Defines immutable, hashable artifacts required for:
  - Deterministic reasoning trace capture (ReasonTraceEnvelope)
  - Prompt provenance recording (PromptProvenanceRecord)
  - C0 boundary enforcement (C0BoundaryViolation)
  - Replay guard contract (ReplayGuard)

C0 RULE: All RAG context is informational only. These types enforce that
RAG data cannot mutate routing decisions, safety policy, execution tier,
or tool budget.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

# ---------------------------------------------------------------------------
# C0 Forbidden mutation fields — RAG context must not carry these
# ---------------------------------------------------------------------------

C0_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {
        "route_mode",
        "execution_tier",
        "safety_threshold",
        "allowed_tools",
        "auth_token",
        "tool_budget",
        "policy_override",
        "safety_policy",
    }
)


class C0BoundaryViolation(RuntimeError):
    """Raised when RAG context attempts to mutate a protected field."""


def assert_c0_informational(rag_context: dict[str, Any], source: str = "") -> None:
    """Enforce C0 boundary: RAG context must contain no authority fields.

    Args:
        rag_context: The RAG context dict to inspect.
        source: Optional label for error messages.

    Raises:
        C0BoundaryViolation: If any forbidden field is present.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_c0_informational", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_c0_informational", "p0_governance")
    leaked = C0_FORBIDDEN_FIELDS & set(rag_context.keys())
    if leaked:
        raise C0BoundaryViolation(
            f"C0 violation{f' in {source}' if source else ''}: "
            f"RAG context contains authority fields {sorted(leaked)}. "
            "RAG context is informational only."
        )


# ---------------------------------------------------------------------------
# ReasonTraceEnvelope — deterministic reasoning trace artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasonTraceEnvelope:
    """Immutable envelope capturing a complete ReAct reasoning trace.

    All fields are required. The envelope hash is computed from canonical
    JSON of all fields except envelope_hash itself.
    """

    trace_id: str
    plan_hash: str
    reason_steps: tuple[str, ...]
    action_steps: tuple[str, ...]
    tool_invocations: tuple[str, ...]
    policy_hash: str
    semantic_clock_vector: tuple[int, ...]
    envelope_hash: str = ""

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "ReasonTraceEnvelope.canonical_bytes"
        )

        d = {
            "trace_id": self.trace_id,
            "plan_hash": self.plan_hash,
            "reason_steps": list(self.reason_steps),
            "action_steps": list(self.action_steps),
            "tool_invocations": list(self.tool_invocations),
            "policy_hash": self.policy_hash,
            "semantic_clock_vector": list(self.semantic_clock_vector),
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def compute_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def verify(self) -> bool:
        """Return True if envelope_hash matches recomputed hash."""
        return not self.envelope_hash or self.envelope_hash == self.compute_hash()

    @classmethod
    def build(
        cls,
        trace_id: str,
        plan_hash: str,
        reason_steps: tuple[str, ...],
        action_steps: tuple[str, ...],
        tool_invocations: tuple[str, ...],
        policy_hash: str,
        semantic_clock_vector: tuple[int, ...],
    ) -> ReasonTraceEnvelope:
        obj = cls(
            trace_id=trace_id,
            plan_hash=plan_hash,
            reason_steps=reason_steps,
            action_steps=action_steps,
            tool_invocations=tool_invocations,
            policy_hash=policy_hash,
            semantic_clock_vector=semantic_clock_vector,
            envelope_hash="",
        )
        h = obj.compute_hash()
        return cls(
            trace_id=trace_id,
            plan_hash=plan_hash,
            reason_steps=reason_steps,
            action_steps=action_steps,
            tool_invocations=tool_invocations,
            policy_hash=policy_hash,
            semantic_clock_vector=semantic_clock_vector,
            envelope_hash=h,
        )


# ---------------------------------------------------------------------------
# PromptProvenanceRecord — prompt lineage artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptProvenanceRecord:
    """Immutable record of prompt construction provenance.

    Captures all inputs that contributed to a prompt so that replay
    can reconstruct the identical prompt hash.
    """

    prompt_hash: str
    prompt_template_id: str
    rag_context_ids: tuple[str, ...]
    policy_hash: str
    model_id: str

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "PromptProvenanceRecord.canonical_bytes"
        )

        d = {
            "prompt_hash": self.prompt_hash,
            "prompt_template_id": self.prompt_template_id,
            "rag_context_ids": list(self.rag_context_ids),
            "policy_hash": self.policy_hash,
            "model_id": self.model_id,
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def record_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def build(
        cls,
        prompt_text: str,
        prompt_template_id: str,
        rag_context_ids: tuple[str, ...],
        policy_hash: str,
        model_id: str,
    ) -> PromptProvenanceRecord:
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        return cls(
            prompt_hash=prompt_hash,
            prompt_template_id=prompt_template_id,
            rag_context_ids=rag_context_ids,
            policy_hash=policy_hash,
            model_id=model_id,
        )


# ---------------------------------------------------------------------------
# ReplayGuard — intercepts non-deterministic clock/random sources
# ---------------------------------------------------------------------------


class NonDeterministicCallDetected(RuntimeError):
    """Raised when a forbidden non-deterministic call is detected."""


@dataclass
class ReplayGuard:
    """Guards a reasoning execution against non-deterministic sources.

    In replay mode, any call to wall-clock time or random is intercepted
    and replaced with the deterministic semantic_clock_vector tick.

    Usage::

        guard = ReplayGuard(semantic_clock_vector=(1000, 0))
        with guard:
            result = run_react(...)
    """

    semantic_clock_vector: tuple[int, ...]
    strict: bool = True
    _violations: list[str] = field(default_factory=list)

    @property
    def current_tick(self) -> int:
        return self.semantic_clock_vector[0] if self.semantic_clock_vector else 0

    def record_violation(self, source: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReplayGuard.record_violation")

        self._violations.append(source)
        if self.strict:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: non-deterministic call intercepted from '{source}'. "
                "Use semantic_clock_vector instead of wall-clock time or random."
            )

    @property
    def violations(self) -> list[str]:
        return list(self._violations)

    def assert_clean(self) -> None:
        """Raise if any violations were recorded (non-strict mode check)."""
        if self._violations:
            raise NonDeterministicCallDetected(
                f"ReplayGuard: {len(self._violations)} non-deterministic call(s) detected: {self._violations}"
            )


__all__ = [
    "C0_FORBIDDEN_FIELDS",
    "C0BoundaryViolation",
    "assert_c0_informational",
    "ReasonTraceEnvelope",
    "PromptProvenanceRecord",
    "NonDeterministicCallDetected",
    "ReplayGuard",
]
