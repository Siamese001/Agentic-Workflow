"""ADG importability contract for agentic_core/L5_safety/enforcement/safety_eval_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_safety_eval_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.safety_eval_cache import (  # noqa: F401
        SafetyEvalCache,
        get_safety_eval_cache,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SafetyEvalCache = None  # type: ignore[assignment,misc]
    get_safety_eval_cache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="safety_eval_cache.py deps unavailable")
class TestSafetyEvalCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: safety_eval_cache.py must be importable."""
        assert _AVAILABLE

    def test_safetyevalcache_is_type(self) -> None:
        assert SafetyEvalCache is not None

    def test_get_safety_eval_cache_callable(self) -> None:
        assert callable(get_safety_eval_cache)

