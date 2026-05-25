"""
agentic_core/interfaces/meta_control.py

Sovereign meta-control config interface for apps_* consumption.

Re-exports read-only config_store accessors and type definitions.
Mutation methods (meta_apply, apply_with_invariants) are re-exported
only when called from the operator entrypoint with a capability token.

AUTHORITY CONSTRAINTS:
- load_current / apply_change_package_readonly: read-only, always allowed
- apply_meta_learning_rollout / apply_with_invariants: write-path, operator-only
- SemanticClockSnapshot: type re-export, no execution authority
- CapabilityTokenArtifact: type re-export, no execution authority

USAGE (apps_*):
    from agentic_core.interfaces.meta_control import (
        load_current,
        apply_change_package_readonly,
        ConfigDeltaArtifact,
        canonical_json,
        validate_component_allowed,
        # Operator-only (requires capability token):
        apply_meta_learning_rollout,
        apply_with_invariants,
        SemanticClockSnapshot,
        CapabilityTokenArtifact,
    )

Defensive imports: matches the ``routing_types.py`` / ``state_agents.py``
pattern. ``system_learning`` is an optional plane in some build profiles;
if any of its sub-modules is unavailable, the affected symbol becomes a
fail-fast stub instead of crashing every importer of this shim.
"""

from __future__ import annotations

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import CapabilityTokenArtifact


class _MissingOptionalDependency:
    def __init__(self, symbol: str, reason: str) -> None:
        self._symbol = symbol
        self._reason = reason

    def __getattr__(self, attr: str):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")

    def __call__(self, *args, **kwargs):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")


try:
    from agentic_core.L6_system_learning.config_store import apply_change_package_readonly, load_current
except ImportError as exc:
    apply_change_package_readonly = _MissingOptionalDependency(
        "apply_change_package_readonly",
        str(exc),
    )
    load_current = _MissingOptionalDependency("load_current", str(exc))

try:
    from agentic_core.L6_system_learning.meta_apply import apply_meta_learning_rollout
except ImportError as exc:
    apply_meta_learning_rollout = _MissingOptionalDependency(
        "apply_meta_learning_rollout",
        str(exc),
    )

try:
    from agentic_core.L6_system_learning.meta_apply_ops import apply_with_invariants
except ImportError as exc:
    apply_with_invariants = _MissingOptionalDependency("apply_with_invariants", str(exc))

try:
    from agentic_core.L6_system_learning.config_store_types import (
        ConfigDeltaArtifact,
        canonical_json,
        validate_component_allowed,
    )
except ImportError as exc:
    ConfigDeltaArtifact = _MissingOptionalDependency("ConfigDeltaArtifact", str(exc))
    canonical_json = _MissingOptionalDependency("canonical_json", str(exc))
    validate_component_allowed = _MissingOptionalDependency(
        "validate_component_allowed",
        str(exc),
    )

__all__ = [
    "load_current",
    "apply_change_package_readonly",
    "ConfigDeltaArtifact",
    "canonical_json",
    "validate_component_allowed",
    "apply_meta_learning_rollout",
    "apply_with_invariants",
    "SemanticClockSnapshot",
    "CapabilityTokenArtifact",
]
