"""
agentic_core/interfaces/meta_learning.py

Sovereign meta-learning interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- Meta-learning is mandatory by default (proposal_only=False)
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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
JSONPrimitive = str | int | float | bool | None

@dataclass(frozen=True)
class ChangePackage:
    """
    Immutable JSON-only proposal package.

    No executable closures, callables, function pointers, or object references
    are permitted in parameters.  Runtime validation enforces this.

    ``proposal_only`` defaults to True.  Setting it to False requires an
    explicit ``approval_token`` to be supplied; without one the constructor
    raises ValueError, preventing silent runtime activation.
    """
    proposal_id: str
    change_type: str
    parameters: dict[str, Any]
    requires_approval: bool = True
    proposal_only: bool = True
    approval_token: str | None = None

    def __post_init__(self) -> None:
        try:
            json.dumps(self.parameters)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'ChangePackage.parameters must be JSON-serializable: {exc}') from exc
        if not self.proposal_only and (not self.approval_token):
            raise ValueError('ChangePackage.proposal_only=False requires an explicit approval_token. Runtime mutation without an approval token is prohibited.')

class SovereignMetaLearningClient:
    """
    Reflection-hardened sealed implementation of MetaLearningInterface.

    Authority guards:
    - __slots__ prevents __dict__ attribute traversal
    - __getattr__ blocks access to any undeclared attribute
    - __setattr__ / __delattr__ prevent modification
    - commit / activate / execute raise PermissionError unconditionally
    - Mandatory application by default (proposal_only=False)
    """
    __slots__ = ('_sealed_client', '_proposal_only')

    def __init__(self, inner_client: Any, proposal_only: bool=False, approval_gate: Any=None, version_store: Any=None) -> None:
        if not proposal_only and (approval_gate is None or version_store is None):
            raise PermissionError('proposal_only=False requires explicit approval_gate and version_store injection.  No silent activation path allowed.')
        object.__setattr__(self, '_sealed_client', inner_client)
        object.__setattr__(self, '_proposal_only', proposal_only)

    def propose_healing_pattern(self, pattern: dict[str, Any]) -> ChangePackage:
        """Propose or apply a healing pattern change — JSON-only payload."""
        return ChangePackage(proposal_id=str(uuid.uuid4()), change_type='healing_pattern', parameters=pattern, requires_approval=True)

    def suggest_threshold_adjustment(self, threshold: float) -> ChangePackage:
        """Apply or suggest a routing threshold change."""
        return ChangePackage(proposal_id=str(uuid.uuid4()), change_type='threshold_adjustment', parameters={'threshold': threshold}, requires_approval=True)

    def retrieve_healing_pattern(self, violation_type: str, error_signature: str) -> dict[str, Any] | None:
        """Read-only pattern retrieval — delegates to inner client."""
        inner = object.__getattribute__(self, '_sealed_client')
        if hasattr(inner, 'retrieve_pattern'):
            return inner.retrieve_pattern(violation_type, error_signature)
        return None

    def commit(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError('commit() authority reserved for L5 — blocked by interface seal')

    def activate(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError('activate() authority reserved for L0 — blocked by interface seal')

    def execute(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError('execute() authority reserved for L2 — blocked by interface seal')

    def store_pattern(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError('store_pattern() write authority reserved for L4 — blocked')

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}' — inner client access is sealed")

    def __getattribute__(self, name: str) -> Any:
        allowed = frozenset({'propose_healing_pattern', 'suggest_threshold_adjustment', 'retrieve_healing_pattern', 'commit', 'activate', 'execute', 'store_pattern', '__class__', '__slots__', '__doc__', '__module__', '__getattribute__', '__getattr__', '__setattr__', '__delattr__'})
        if name not in allowed:
            raise AttributeError(f"'{self.__class__.__name__}' attribute '{name}' is sealed")
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"Cannot set attribute '{name}' on sealed SovereignMetaLearningClient")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"Cannot delete attribute '{name}' on sealed SovereignMetaLearningClient")

def get_sovereign_meta_client(proposal_only: bool=False, approval_gate: Any=None, version_store: Any=None) -> SovereignMetaLearningClient:
    """
    Factory: returns a sealed sovereign meta-learning client.

    Default: proposal_only=False — mandatory application mode.
    """
    from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client
    inner = get_meta_learning_client()
    return SovereignMetaLearningClient(inner, proposal_only=proposal_only, approval_gate=approval_gate, version_store=version_store)

def get_guardrails() -> Any:
    """Re-export guardrails — read-only safety checks, no mutation authority."""
    from agentic_core.L1_cognition.utils.guardrails_util import get_guardrails as _get
    return _get()

def _import_healing_pattern() -> type:
    from agentic_core.L1_cognition.types.client_types import HealingPattern
    return HealingPattern

def _import_guardrails_class() -> type:
    from agentic_core.L1_cognition.utils.guardrails_util import MetaLearningGuardrails
    return MetaLearningGuardrails
try:
    from agentic_core.L1_cognition.types.client_types import HealingPattern
    from agentic_core.L1_cognition.utils.guardrails_util import MetaLearningGuardrails
except ImportError:
    HealingPattern = None
    MetaLearningGuardrails = None
__all__ = ['ChangePackage', 'SovereignMetaLearningClient', 'get_sovereign_meta_client', 'get_guardrails', 'HealingPattern', 'MetaLearningGuardrails', 'JSONPrimitive']
