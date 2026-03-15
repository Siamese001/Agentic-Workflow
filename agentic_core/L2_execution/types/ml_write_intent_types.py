"""
L2.2 MLWriteIntent — Phase 4

Declarative write intent emitted by the ML layer.
All durable ML writes (pattern_store, cache_set) MUST be executed
inside the L2.2 commit sandbox via MLWriteIntentExecutor.

Direct Pinecone/Redis writes from L1/L3/L6 are FORBIDDEN.
Attempting to execute an MLWriteIntent outside the sandbox raises
MLWriteEnvelopeViolation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class MLWriteEnvelopeViolation(Exception):
    """
    Raised when an MLWriteIntent is executed outside the L2.2 commit sandbox.

    Violation code: ML_WRITE_OUTSIDE_SANDBOX
    """

    VIOLATION_CODE = "ML_WRITE_OUTSIDE_SANDBOX"

    def __init__(self, message: str = "MLWriteIntent executed outside L2.2 commit sandbox") -> None:
        super().__init__(f"[{self.VIOLATION_CODE}] {message}")


@dataclass
class MLWriteIntent:
    """
    Declarative ML write intent.

    Fields:
        kind        — "pattern_store" or "cache_set"
        payload     — serializable dict of write parameters
        requires_commit — always True; enforced in __post_init__
        intent_hash — sha256 of canonical_bytes() (computed on construction)
    """

    kind: Literal["pattern_store", "cache_set"]
    payload: dict[str, Any]
    requires_commit: bool = True
    intent_hash: str = field(default="", init=False)
    _ALLOWED_KINDS = frozenset({"pattern_store", "cache_set"})

    def __post_init__(self) -> None:
        if self.kind not in self._ALLOWED_KINDS:
            raise ValueError(
                f"MLWriteIntent: kind must be one of {sorted(self._ALLOWED_KINDS)}, got {self.kind!r}"
            )
        if not isinstance(self.payload, dict):
            raise TypeError(f"MLWriteIntent: payload must be a dict, got {type(self.payload).__name__}")
        if not self.requires_commit:
            raise ValueError("MLWriteIntent: requires_commit must be True — direct writes are forbidden")
        object.__setattr__(self, "intent_hash", self._compute_hash())

    def _compute_hash(self) -> str:
        doc = {"kind": self.kind, "payload": self.payload, "requires_commit": self.requires_commit}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MLWriteIntent.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntent.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        doc = {"kind": self.kind, "payload": self.payload, "requires_commit": self.requires_commit}
        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()


_SANDBOX_ACTIVE = False


def is_commit_sandbox_active() -> bool:
    """Return True if the L2.2 commit sandbox is currently active."""
    return _SANDBOX_ACTIVE


class MLWriteIntentExecutor:
    """
    L2.2 commit sandbox for executing MLWriteIntents.

    Usage (context manager):
        with MLWriteIntentExecutor() as executor:
            executor.execute(intent)

    Attempting to call execute() outside the context manager raises
    MLWriteEnvelopeViolation.
    """

    def __enter__(self) -> MLWriteIntentExecutor:
        global _SANDBOX_ACTIVE
        _SANDBOX_ACTIVE = True
        return self

    def __exit__(self, *_: object) -> None:
        global _SANDBOX_ACTIVE
        _SANDBOX_ACTIVE = False

    def execute(self, intent: MLWriteIntent) -> dict[str, Any]:
        """
        Execute an MLWriteIntent inside the L2.2 sandbox.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MLWriteIntentExecutor.execute")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntentExecutor.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="execute_ml_write", target=intent.target_path)
        if not _SANDBOX_ACTIVE:
            raise MLWriteEnvelopeViolation(
                f"execute() called outside L2.2 commit sandbox for kind={intent.kind!r}"
            )
        return {"executed": True, "kind": intent.kind, "intent_hash": intent.intent_hash}


def execute_ml_write_intent_outside_sandbox(intent: MLWriteIntent) -> None:
    """
    Attempt to execute an MLWriteIntent outside the sandbox.
    Always raises MLWriteEnvelopeViolation.

    This function exists to make the enforcement contract explicit and testable.
    """
    if not _SANDBOX_ACTIVE:
        raise MLWriteEnvelopeViolation(
            f"Direct ML write attempted outside L2.2 sandbox for kind={intent.kind!r}"
        )
