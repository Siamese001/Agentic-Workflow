"""
HealerMixin - Backwards Compatibility Shim

[MIXIN REFACTOR] All healing governance logic has been consolidated into
HealingPolicyMixin (healing_policy_mixin.py). This file re-exports
the class under the old name to preserve 12+ existing import sites.

Canonical location: agentic_core.mixins.healing_policy_mixin.HealingPolicyMixin
"""

from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class HealerMixin(HealingPolicyMixin):
    """Backwards-compat alias. Use HealingPolicyMixin directly for new code."""

    pass
