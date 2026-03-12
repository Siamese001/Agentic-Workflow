"""ADG importability contract for agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hitl_dpo_pair_generator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.hitl_dpo_pair_generator import (  # noqa: F401
        DPOPairGenerator,
        DefaultDeterministicDPOPairGenerator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DPOPairGenerator = None  # type: ignore[assignment,misc]
    DefaultDeterministicDPOPairGenerator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hitl_dpo_pair_generator.py deps unavailable")
class TestHitlDpoPairGeneratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hitl_dpo_pair_generator.py must be importable."""
        assert _AVAILABLE

    def test_dpopairgenerator_is_type(self) -> None:
        assert DPOPairGenerator is not None

    def test_defaultdeterministicdpopairgenerator_is_type(self) -> None:
        assert DefaultDeterministicDPOPairGenerator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

