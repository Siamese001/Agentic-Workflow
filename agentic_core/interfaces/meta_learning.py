"""
agentic_core/interfaces/meta_learning.py

Sovereign meta-learning interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- All meta-learning APIs return ChangePackage only (proposal-only)
- commit(), activate(), execute() are BLOCKED with PermissionError
- Inner client is sealed via __slots__ and __getattr__ override
- JSON-only payload validation on ChangePackage
- proposal_only=False requires explicit approval_gate + version_store injection

USAGE (apps_*):
    from agentic_core.interfaces.meta_learning import (
        get_sovereign_meta_client,
        ChangePackage,
        HealingPattern,
        MetaLearningGuardrails,
        get_guardrails,
    )
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

# JSONPrimitive: restrict payloads to serializable types only
JSONPrimitive = str | int | float | bool | None


@dataclass(frozen=True)
class ChangePackage:
    """
    Immutable JSON-only proposal package.

    No executable closures, callables, function pointers, or object references
    are permitted in parameters.  Runtime validation enforces this.
    """

    proposal_id: str
    change_type: str
    parameters: dict[str, Any]
    requires_approval: bool = True

    def __post_init__(self) -> None:
        try:
            json.dumps(self.parameters)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"ChangePackage.parameters must be JSON-serializable: {exc}") from exc


class SovereignMetaLearningClient:
    """
    Reflection-hardened sealed implementation of MetaLearningInterface.

    Authority guards:
    - __slots__ prevents __dict__ attribute traversal
    - __getattr__ blocks access to any undeclared attribute
    - __setattr__ / __delattr__ prevent modification
    - commit / activate / execute raise PermissionError unconditionally
    - proposal_only=False requires approval_gate + version_store injection
    """

    __slots__ = ("_sealed_client", "_proposal_only")

    def __init__(
        self,
        inner_client: Any,
        proposal_only: bool = True,
        approval_gate: Any = None,
        version_store: Any = None,
    ) -> None:
        if not proposal_only and (approval_gate is None or version_store is None):
            raise PermissionError(
                "proposal_only=False requires explicit approval_gate and "
                "version_store injection.  No silent activation path allowed."
            )
        object.__setattr__(self, "_sealed_client", inner_client)
        object.__setattr__(self, "_proposal_only", proposal_only)

    # ------------------------------------------------------------------
    # Allowed proposal-only methods
    # ------------------------------------------------------------------

    def propose_healing_pattern(self, pattern: dict[str, Any]) -> ChangePackage:
        """Propose a healing pattern change — JSON-only payload, requires approval."""
        if not object.__getattribute__(self, "_proposal_only"):
            raise PermissionError("Direct execution forbidden — proposal only")
        return ChangePackage(
            proposal_id=str(uuid.uuid4()),
            change_type="healing_pattern",
            parameters=pattern,
            requires_approval=True,
        )

    def suggest_threshold_adjustment(self, threshold: float) -> ChangePackage:
        """Suggest a routing threshold change — requires approval."""
        if not object.__getattribute__(self, "_proposal_only"):
            raise PermissionError("Direct execution forbidden — proposal only")
        return ChangePackage(
            proposal_id=str(uuid.uuid4()),
            change_type="threshold_adjustment",
            parameters={"threshold": threshold},
            requires_approval=True,
        )

    def retrieve_healing_pattern(self, violation_type: str, error_signature: str) -> dict[str, Any] | None:
        """Read-only pattern retrieval — delegates to inner client."""
        inner = object.__getattribute__(self, "_sealed_client")
        if hasattr(inner, "retrieve_pattern"):
            return inner.retrieve_pattern(violation_type, error_signature)
        return None

    # ------------------------------------------------------------------
    # Authority blocks — must raise PermissionError
    # ------------------------------------------------------------------

    def commit(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("commit() authority reserved for L5 — blocked by interface seal")

    def activate(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("activate() authority reserved for L0 — blocked by interface seal")

    def execute(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("execute() authority reserved for L2 — blocked by interface seal")

    def store_pattern(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("store_pattern() write authority reserved for L4 — blocked")

    # ------------------------------------------------------------------
    # Reflection protection
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(
            f"'{self.__class__.__name__}' has no attribute '{name}' — inner client access is sealed"
        )

    def __getattribute__(self, name: str) -> Any:
        allowed = frozenset(
            {
                "propose_healing_pattern",
                "suggest_threshold_adjustment",
                "retrieve_healing_pattern",
                "commit",
                "activate",
                "execute",
                "store_pattern",
                "__class__",
                "__slots__",
                "__doc__",
                "__module__",
                "__getattribute__",
                "__getattr__",
                "__setattr__",
                "__delattr__",
            }
        )
        if name not in allowed:
            raise AttributeError(f"'{self.__class__.__name__}' attribute '{name}' is sealed")
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"Cannot set attribute '{name}' on sealed SovereignMetaLearningClient")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"Cannot delete attribute '{name}' on sealed SovereignMetaLearningClient")


# ------------------------------------------------------------------
# Re-exports for apps_* consumption
# ------------------------------------------------------------------


def get_sovereign_meta_client(
    proposal_only: bool = True,
    approval_gate: Any = None,
    version_store: Any = None,
) -> SovereignMetaLearningClient:
    """
    Factory: returns a sealed sovereign meta-learning client.

    Default: proposal_only=True — no activation path without injection.
    """
    from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client

    inner = get_meta_learning_client()
    return SovereignMetaLearningClient(
        inner,
        proposal_only=proposal_only,
        approval_gate=approval_gate,
        version_store=version_store,
    )


def get_guardrails() -> Any:
    """Re-export guardrails — read-only safety checks, no mutation authority."""
    from agentic_core.L1_cognition.utils.guardrails import get_guardrails as _get

    return _get()


# Type re-exports so apps_* can annotate without importing from L* layers
def _import_healing_pattern() -> type:
    from agentic_core.L1_cognition.types.client_types import HealingPattern

    return HealingPattern


def _import_guardrails_class() -> type:
    from agentic_core.L1_cognition.utils.guardrails import MetaLearningGuardrails

    return MetaLearningGuardrails


# Lazy type aliases (populated on first import by callers)
try:
    from agentic_core.L1_cognition.types.client_types import HealingPattern
    from agentic_core.L1_cognition.utils.guardrails import MetaLearningGuardrails
except ImportError:
    HealingPattern = None  # type: ignore[assignment,misc]
    MetaLearningGuardrails = None  # type: ignore[assignment,misc]


__all__ = [
    "ChangePackage",
    "SovereignMetaLearningClient",
    "get_sovereign_meta_client",
    "get_guardrails",
    "HealingPattern",
    "MetaLearningGuardrails",
    "JSONPrimitive",
]
