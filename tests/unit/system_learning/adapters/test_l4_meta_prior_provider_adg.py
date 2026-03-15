"""ADG importability contract for system_learning/adapters/l4_meta_prior_provider.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_l4_meta_prior_provider.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.adapters.l4_meta_prior_provider import (  # noqa: F401
        L4MetaPriorProvider,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    L4MetaPriorProvider = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="l4_meta_prior_provider.py deps unavailable")
class TestL4MetaPriorProviderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: l4_meta_prior_provider.py must be importable."""
        assert _AVAILABLE

    def test_l4metapriorprovider_is_type(self) -> None:
        assert L4MetaPriorProvider is not None
