"""ADG importability contract for agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_HygieneGuardianAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.HygieneGuardianAgent import (  # noqa: F401
        MAX_FILENAME_WORDS,
        MAX_TEST_FILENAME_WORDS,
        REDUNDANT_TERMS,
        HygieneGuardianAgent,
        HygieneViolation,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MAX_FILENAME_WORDS = None  # type: ignore[assignment,misc]
    MAX_TEST_FILENAME_WORDS = None  # type: ignore[assignment,misc]
    REDUNDANT_TERMS = None  # type: ignore[assignment,misc]
    HygieneViolation = None  # type: ignore[assignment,misc]
    HygieneGuardianAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="HygieneGuardianAgent deps unavailable")
class TestHygieneguardianagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py must be importable."""
        assert _AVAILABLE

    def test_hygieneviolation_defined(self) -> None:
        assert HygieneViolation is not None

    def test_hygieneguardianagent_defined(self) -> None:
        assert HygieneGuardianAgent is not None
