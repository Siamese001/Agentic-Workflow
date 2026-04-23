"""
agentic_core/interfaces/meta_control_shim.py

Sovereign meta-control config interface shim for apps_* consumption.
"""

from __future__ import annotations

from agentic_core.interfaces.determinism_types_shim import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import CapabilityTokenArtifact
from system_learning.config.config_store import apply_change_package_readonly, load_current
from system_learning.types.config_store_types import (
    ConfigDeltaArtifact,
    canonical_json,
    validate_component_allowed,
)


def apply_meta_learning_rollout(*args, **kwargs):
    from system_learning.meta_learning.meta_apply import apply_meta_learning_rollout as _impl

    return _impl(*args, **kwargs)


def apply_with_invariants(*args, **kwargs):
    from system_learning.meta_learning.meta_apply_ops import apply_with_invariants as _impl

    return _impl(*args, **kwargs)


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
