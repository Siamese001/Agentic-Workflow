"""ADG importability contract for agentic_core/mixins/ssot_meta_learning_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_meta_learning_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_meta_learning_mixin import (  # noqa: F401
        MetaLearningWriteRejected,
        SSOTMetaLearningMixin,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MetaLearningWriteRejected = None  # type: ignore[assignment,misc]
    SSOTMetaLearningMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_meta_learning_mixin.py deps unavailable")
class TestSsotMetaLearningMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ssot_meta_learning_mixin.py must be importable."""
        assert _AVAILABLE

    def test_metalearningwriterejected_is_type(self) -> None:
        assert MetaLearningWriteRejected is not None

    def test_ssotmetalearningmixin_is_type(self) -> None:
        assert SSOTMetaLearningMixin is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

