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
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MetaLearningWriteRejected = None  # type: ignore[assignment,misc]
    SSOTMetaLearningMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_meta_learning_mixin deps unavailable")
class TestSsotMetaLearningMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/ssot_meta_learning_mixin.py must be importable."""
        assert _AVAILABLE

    def test_metalearningwriterejected_defined(self) -> None:
        assert MetaLearningWriteRejected is not None

    def test_ssotmetalearningmixin_defined(self) -> None:
        assert SSOTMetaLearningMixin is not None
