"""
Shim for backward compatibility. DEPRECATED.

SSOT Location: agentic_core/utils/core_extensions/healer_mixin.py

This file now re-exports from the SSOT location.
Migrate your imports to: from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
"""
import warnings

# Re-export from SSOT
from agentic_core.utils.core_extensions.healer_mixin import (
    HealerMixin as SSOTHealerMixin,
    HealResult as SSOTHealResult,
)

# Emit warning on import to encourage migration
warnings.warn(
    "Importing HealerMixin from common/healing is deprecated. "
    "Use agentic_core.utils.core_extensions.healer_mixin instead.",
    DeprecationWarning,
    stacklevel=2
)

# Maintain names for existing imports
HealerMixin = SSOTHealerMixin
HealResult = SSOTHealResult

__all__ = ["HealerMixin", "HealResult"]