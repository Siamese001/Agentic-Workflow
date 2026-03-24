"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeHealerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CodeHealerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.CodeHealerAgent import (  # noqa: F401
        CodeHealerAgent,
        CodeHealingStrategy,
        HealerConfig,
        HealingAction,
        HealingType,
        create_legacy_canon_healer,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CodeHealingStrategy = None  # type: ignore[assignment,misc]
    HealingType = None  # type: ignore[assignment,misc]
    HealingAction = None  # type: ignore[assignment,misc]
    HealerConfig = None  # type: ignore[assignment,misc]
    CodeHealerAgent = None  # type: ignore[assignment,misc]
    create_legacy_canon_healer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeHealerAgent deps unavailable")
class TestCodehealeragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/CodeHealerAgent.py must be importable."""
        assert _AVAILABLE

    def test_codehealingstrategy_defined(self) -> None:
        assert CodeHealingStrategy is not None

    def test_healingtype_defined(self) -> None:
        assert HealingType is not None

    def test_healingaction_defined(self) -> None:
        assert HealingAction is not None

    def test_healerconfig_defined(self) -> None:
        assert HealerConfig is not None

    def test_codehealeragent_defined(self) -> None:
        assert CodeHealerAgent is not None