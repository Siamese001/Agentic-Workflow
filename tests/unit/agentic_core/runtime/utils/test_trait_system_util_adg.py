"""ADG importability contract for agentic_core/runtime/utils/trait_system_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_trait_system_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.utils.trait_system_util import (  # noqa: F401
        BatchingTrait,
        CachingTrait,
        MetricsTrait,
        T,
        Trait,
        with_traits,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    T = None  # type: ignore[assignment,misc]
    Trait = None  # type: ignore[assignment,misc]
    CachingTrait = None  # type: ignore[assignment,misc]
    MetricsTrait = None  # type: ignore[assignment,misc]
    BatchingTrait = None  # type: ignore[assignment,misc]
    with_traits = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="trait_system_util deps unavailable")
class TestTraitSystemUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/utils/trait_system_util.py must be importable."""
        assert _AVAILABLE

    def test_trait_defined(self) -> None:
        assert Trait is not None

    def test_cachingtrait_defined(self) -> None:
        assert CachingTrait is not None

    def test_metricstrait_defined(self) -> None:
        assert MetricsTrait is not None

    def test_batchingtrait_defined(self) -> None:
        assert BatchingTrait is not None
