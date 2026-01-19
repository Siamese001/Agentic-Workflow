"""
Phase 3 Default-On Healing Infrastructure - Canonical Import Path

This module provides the authoritative import path for HealerMixin:
    from agentic_core.common.healing.healer_mixin import HealerMixin

Re-exports from the implementation at agentic_core.utils.core_extensions.healer_mixin
"""
from agentic_core.L5_safety.validators.healer_mixin import HealerMixin

__all__ = ["HealerMixin"]
