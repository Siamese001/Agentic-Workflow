"""
HealerMixin - Backwards Compatibility Shim

[MIXIN REFACTOR] All healing governance logic has been consolidated into
HealingPolicyMixin (healing_policy_mixin.py). This file re-exports
the class under the old name to preserve 12+ existing import sites.

Canonical location: agentic_core.mixins.healing_policy_mixin.HealingPolicyMixin
"""

from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin


class HealerMixin(HealingPolicyMixin):
    """Backwards-compat alias. Use HealingPolicyMixin directly for new code."""

    pass
