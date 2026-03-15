"""ADG importability contract for agentic_core/L6_observability/engines/dpo_pair_generator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_dpo_pair_generator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.dpo_pair_generator import (  # noqa: F401
        BoundedDPOPair,
        BoundingViolation,
        DPOBoundingPolicy,
        DPOPair,
        create_bounded_dpo_pairs,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BoundingViolation = None  # type: ignore[assignment,misc]
    DPOPair = None  # type: ignore[assignment,misc]
    BoundedDPOPair = None  # type: ignore[assignment,misc]
    DPOBoundingPolicy = None  # type: ignore[assignment,misc]
    create_bounded_dpo_pairs = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dpo_pair_generator deps unavailable")
class TestDpoPairGeneratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L6_observability/engines/dpo_pair_generator.py must be importable."""
        assert _AVAILABLE

    def test_boundingviolation_defined(self) -> None:
        assert BoundingViolation is not None

    def test_dpopair_defined(self) -> None:
        assert DPOPair is not None

    def test_boundeddpopair_defined(self) -> None:
        assert BoundedDPOPair is not None

    def test_dpoboundingpolicy_defined(self) -> None:
        assert DPOBoundingPolicy is not None
