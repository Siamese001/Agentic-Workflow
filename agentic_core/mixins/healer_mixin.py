"""
HealerMixin - Backwards Compatibility Shim

[MIXIN REFACTOR] All healing governance logic has been consolidated into
HealingPolicyMixin (healing_policy_mixin.py). This file re-exports
the class under the old name to preserve 12+ existing import sites.

Canonical location: agentic_core.mixins.healing_policy_mixin.HealingPolicyMixin
"""
from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class HealerMixin(HealingPolicyMixin):
    """Backwards-compat alias. Use HealingPolicyMixin directly for new code."""
    pass
