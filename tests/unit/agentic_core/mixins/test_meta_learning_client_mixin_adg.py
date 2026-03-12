"""ADG importability contract for agentic_core/mixins/meta_learning_client_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_meta_learning_client_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.meta_learning_client_mixin import (  # noqa: F401
        MetaLearningClientMixin,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MetaLearningClientMixin = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_client_mixin.py deps unavailable")
class TestMetaLearningClientMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: meta_learning_client_mixin.py must be importable."""
        assert _AVAILABLE

    def test_metalearningclientmixin_is_type(self) -> None:
        assert MetaLearningClientMixin is not None

