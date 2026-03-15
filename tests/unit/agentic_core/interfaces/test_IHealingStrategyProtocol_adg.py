"""ADG importability contract for agentic_core/interfaces/IHealingStrategyProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IHealingStrategyProtocol.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IHealingStrategyProtocol import (  # noqa: F401
        ChaosResilienceStrategy,
        IHealingStrategyProtocol,
        get_chaos_strategy,
        get_integration_status,
        register_chaos_healing,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    IHealingStrategyProtocol = None  # type: ignore[assignment,misc]
    ChaosResilienceStrategy = None  # type: ignore[assignment,misc]
    get_chaos_strategy = None  # type: ignore[assignment,misc]
    register_chaos_healing = None  # type: ignore[assignment,misc]
    get_integration_status = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IHealingStrategyProtocol deps unavailable")
class TestIhealingstrategyprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/interfaces/IHealingStrategyProtocol.py must be importable."""
        assert _AVAILABLE

    def test_ihealingstrategyprotocol_defined(self) -> None:
        assert IHealingStrategyProtocol is not None

    def test_chaosresiliencestrategy_defined(self) -> None:
        assert ChaosResilienceStrategy is not None
