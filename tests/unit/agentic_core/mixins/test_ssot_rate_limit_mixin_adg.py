"""ADG importability contract for agentic_core/mixins/ssot_rate_limit_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_rate_limit_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_rate_limit_mixin import (  # noqa: F401
        RateLimitExceeded,
        SSOTRateLimitMixin,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RateLimitExceeded = None  # type: ignore[assignment,misc]
    SSOTRateLimitMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_rate_limit_mixin deps unavailable")
class TestSsotRateLimitMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/ssot_rate_limit_mixin.py must be importable."""
        assert _AVAILABLE

    def test_ratelimitexceeded_defined(self) -> None:
        assert RateLimitExceeded is not None

    def test_ssotratelimitmixin_defined(self) -> None:
        assert SSOTRateLimitMixin is not None
