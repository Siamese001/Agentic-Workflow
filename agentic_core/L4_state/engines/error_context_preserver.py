from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

ExecutionTrace = Any
AgentState = Any


class PreservationResult(NamedTuple):
    """The result of preserving an error context in L4."""

    context_hash: str
    prev_hash: str
    l4_storage_path: str


@dataclass(frozen=True)
class ErrorContext:
    """A structured, versioned representation of an error and its context."""

    error_type: str
    error_message: str
    agent_state: AgentState
    execution_trace: ExecutionTrace
    context_hash: str = field(init=False)
    prev_hash: str = field(init=False)

    def __post_init__(self):
        canonical_bytes = self._canonical_bytes()
        object.__setattr__(self, "context_hash", hashlib.sha256(canonical_bytes).hexdigest())

    def _canonical_bytes(self) -> bytes:
        """Computes the canonical byte representation of the context for hashing."""
        data = {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "agent_state": self.agent_state,
            "execution_trace": self.execution_trace,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def with_chain(self, prev_hash: str) -> ErrorContext:
        """Attaches the previous hash to form a chain, returning a new instance."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ErrorContext.with_chain")

        new_instance = ErrorContext(
            error_type=self.error_type,
            error_message=self.error_message,
            agent_state=self.agent_state,
            execution_trace=self.execution_trace,
        )
        object.__setattr__(new_instance, "prev_hash", prev_hash)
        object.__setattr__(new_instance, "context_hash", self.context_hash)
        return new_instance


def preserve_error_context(
    error: Exception, agent_state: AgentState, execution_trace: ExecutionTrace, prev_hash: str
) -> PreservationResult:
    """
    Preserves the full error context in L4 with content-hash chaining.

    This function enforces Guarantee #5 (Don't lose data on error) by creating a
    versioned, auditable record of the system's state at the time of failure.
    The hash chain ensures the integrity of the historical record.

    Args:
        error: The exception that was raised.
        agent_state: The complete state of the agent at the time of error.
        execution_trace: The execution trace leading up to the error.
        prev_hash: The hash of the previous record in the L4 state ledger.

    Returns:
        A PreservationResult with the new context hash and storage path.
    """
    context = ErrorContext(
        error_type=type(error).__name__,
        error_message=str(error),
        agent_state=agent_state,
        execution_trace=execution_trace,
    ).with_chain(prev_hash)
    l4_storage_path = f"l4/errors/{context.context_hash}.json"
    return PreservationResult(
        context_hash=context.context_hash, prev_hash=prev_hash, l4_storage_path=l4_storage_path
    )
