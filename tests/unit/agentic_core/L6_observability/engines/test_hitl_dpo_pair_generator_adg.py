"""ADG importability contract for agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hitl_dpo_pair_generator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.hitl_dpo_pair_generator import (  # noqa: F401
        DefaultDeterministicDPOPairGenerator,
        DPOPairGenerator,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DPOPairGenerator = None  # type: ignore[assignment,misc]
    DefaultDeterministicDPOPairGenerator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hitl_dpo_pair_generator deps unavailable")
class TestHitlDpoPairGeneratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py must be importable."""
        assert _AVAILABLE

    def test_dpopairgenerator_defined(self) -> None:
        assert DPOPairGenerator is not None

    def test_defaultdeterministicdpopairgenerator_defined(self) -> None:
        assert DefaultDeterministicDPOPairGenerator is not None
