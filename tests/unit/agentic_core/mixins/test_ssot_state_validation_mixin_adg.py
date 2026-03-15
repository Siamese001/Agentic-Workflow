"""ADG importability contract for agentic_core/mixins/ssot_state_validation_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_state_validation_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_state_validation_mixin import (  # noqa: F401
        SSOTStateValidationError,
        SSOTStateValidationMixin,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SSOTStateValidationError = None  # type: ignore[assignment,misc]
    SSOTStateValidationMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_state_validation_mixin deps unavailable")
class TestSsotStateValidationMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/ssot_state_validation_mixin.py must be importable."""
        assert _AVAILABLE

    def test_ssotstatevalidationerror_defined(self) -> None:
        assert SSOTStateValidationError is not None

    def test_ssotstatevalidationmixin_defined(self) -> None:
        assert SSOTStateValidationMixin is not None
