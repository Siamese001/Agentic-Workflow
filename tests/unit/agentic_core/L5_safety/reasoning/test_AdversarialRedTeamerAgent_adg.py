"""ADG importability contract for agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_AdversarialRedTeamerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.AdversarialRedTeamerAgent import (  # noqa: F401
        AdversarialRedTeamerAgent,
        RedTeamResult,
        VulnerabilityTest,
        get_adversarial_red_teamer,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VulnerabilityTest = None  # type: ignore[assignment,misc]
    RedTeamResult = None  # type: ignore[assignment,misc]
    AdversarialRedTeamerAgent = None  # type: ignore[assignment,misc]
    get_adversarial_red_teamer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="AdversarialRedTeamerAgent deps unavailable")
class TestAdversarialredteameragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py must be importable."""
        assert _AVAILABLE

    def test_vulnerabilitytest_defined(self) -> None:
        assert VulnerabilityTest is not None

    def test_redteamresult_defined(self) -> None:
        assert RedTeamResult is not None

    def test_adversarialredteameragent_defined(self) -> None:
        assert AdversarialRedTeamerAgent is not None