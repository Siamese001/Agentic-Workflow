"""
Phase 7 — ToolIntent: declarative tool emission from L1 + L1 mutation blocker.

L1 cognition MUST NOT directly invoke mutating tools.
Instead it emits a ToolIntent which is executed in the L2.2 commit sandbox.

Enforcement seam:
  assert_l1_tool_allowed(capability) — raises ToolViolation if MUTATING_* in L1 context.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ToolCapability(str, Enum):
    """
    Capability class of a tool.

    NON_MUTATING      — read-only; safe to call from L1 directly.
    MUTATING_EXTERNAL — writes to external services (Redis, Pinecone, APIs).
    MUTATING_FS       — writes to the filesystem.
    MUTATING_STATEBUS — writes to the internal state bus / event bus.
    """

    NON_MUTATING = "non_mutating"
    MUTATING_EXTERNAL = "mutating_external"
    MUTATING_FS = "mutating_fs"
    MUTATING_STATEBUS = "mutating_statebus"


_MUTATING_CAPABILITIES: frozenset[ToolCapability] = frozenset(
    {ToolCapability.MUTATING_EXTERNAL, ToolCapability.MUTATING_FS, ToolCapability.MUTATING_STATEBUS}
)


def is_mutating(capability: ToolCapability) -> bool:
    """Return True if the capability class requires sandbox execution."""
    return capability in _MUTATING_CAPABILITIES


class ToolViolation(Exception):
    """
    Raised when L1 attempts a direct mutating tool call, or when a ToolIntent
    is executed outside the L2.2 commit sandbox.

    Attributes
    ----------
    code   : str  — violation code string
    detail : str  — human-readable description
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"[{code}]" + (f" {detail}" if detail else ""))


_L1_COGNITION_ACTIVE: bool = False


def is_l1_cognition_active() -> bool:
    """Return True when L1 cognition context is active."""
    return _L1_COGNITION_ACTIVE


def assert_l1_tool_allowed(capability: ToolCapability, tool_name: str = "") -> None:
    """
    Raise ToolViolation(code="L1_TOOL_CALL_BLOCKED") if L1 cognition is active
    and the tool has a MUTATING_* capability.

    Call this at the top of any tool invocation seam.
    """
    if _L1_COGNITION_ACTIVE and is_mutating(capability):
        detail = f"tool '{tool_name}' has capability {capability.value}; emit ToolIntent instead"
        raise ToolViolation(code="L1_TOOL_CALL_BLOCKED", detail=detail)


from contextlib import contextmanager
from typing import Generator


@contextmanager
def l1_cognition_scope() -> Generator[None, None, None]:
    """
    Context manager that activates the L1 cognition enforcement flag.

    Inside this scope, any direct call to a MUTATING_* tool raises ToolViolation.
    """
    global _L1_COGNITION_ACTIVE
    already_active = _L1_COGNITION_ACTIVE
    _L1_COGNITION_ACTIVE = True
    try:
        yield
    finally:
        if not already_active:
            _L1_COGNITION_ACTIVE = False


@dataclass
class ToolIntent:
    """
    Declarative tool intent emitted by L1 cognition.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — non-empty tool identifier
    capability     : ToolCapability
    args           : dict  — JSON-serializable tool arguments
    args_hash      : str   — sha256(canonical args); auto-computed if empty
    requires_commit: bool  — True for any MUTATING_* capability (enforced)
    policy_hash    : str   — active PolicyConfig hash
    model_hash     : str   — active ModelConfig hash
    budget_hash    : str   — active BudgetConfig hash
    routing_hash   : str   — active RoutingConfig hash
    intent_hash    : str   — sha256(canonical_bytes excluding intent_hash); auto-computed
    """

    schema_version: int
    tool_name: str
    capability: ToolCapability
    args: dict[str, Any]
    requires_commit: bool
    policy_hash: str = ""
    model_hash: str = ""
    budget_hash: str = ""
    routing_hash: str = ""
    args_hash: str = field(default="", init=True)
    intent_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ToolIntent: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.tool_name:
            raise ValueError("ToolIntent: tool_name must be non-empty")
        if not isinstance(self.capability, ToolCapability):
            raise TypeError(
                f"ToolIntent: capability must be ToolCapability, got {type(self.capability).__name__}"
            )
        if not isinstance(self.args, dict):
            raise TypeError("ToolIntent: args must be a dict")
        if is_mutating(self.capability) and (not self.requires_commit):
            raise ValueError(
                f"ToolIntent: requires_commit must be True for capability {self.capability.value}"
            )
        if not self.args_hash:
            self.args_hash = _sha256(json.dumps(self.args, sort_keys=True, separators=(",", ":")).encode())
        object.__setattr__(self, "intent_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation excluding intent_hash (self-referential)."""
        doc: dict[str, Any] = {
            "args_hash": self.args_hash,
            "budget_hash": self.budget_hash,
            "capability": self.capability.value,
            "model_hash": self.model_hash,
            "policy_hash": self.policy_hash,
            "requires_commit": self.requires_commit,
            "routing_hash": self.routing_hash,
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "capability": self.capability.value,
            "args": self.args,
            "args_hash": self.args_hash,
            "requires_commit": self.requires_commit,
            "policy_hash": self.policy_hash,
            "model_hash": self.model_hash,
            "budget_hash": self.budget_hash,
            "routing_hash": self.routing_hash,
            "intent_hash": self.intent_hash,
        }


def build_tool_intent(
    tool_name: str,
    capability: ToolCapability,
    args: dict[str, Any],
    *,
    policy_hash: str = "",
    model_hash: str = "",
    budget_hash: str = "",
    routing_hash: str = "",
) -> ToolIntent:
    """
    Factory: build a ToolIntent from tool parameters.

    requires_commit is automatically set to True for MUTATING_* capabilities.
    """
    return ToolIntent(
        schema_version=_SCHEMA_VERSION,
        tool_name=tool_name,
        capability=capability,
        args=args,
        requires_commit=is_mutating(capability),
        policy_hash=policy_hash,
        model_hash=model_hash,
        budget_hash=budget_hash,
        routing_hash=routing_hash,
    )
