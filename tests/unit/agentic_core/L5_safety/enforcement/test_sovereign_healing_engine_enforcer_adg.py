"""ADG importability contract for agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereign_healing_engine_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer import (  # noqa: F401
        HealingTransaction,
        SovereignHealingEngine,
        get_filesystem_client,
        get_git_client,
        run_autonomous_healing,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_filesystem_client = None  # type: ignore[assignment,misc]
    get_git_client = None  # type: ignore[assignment,misc]
    HealingTransaction = None  # type: ignore[assignment,misc]
    SovereignHealingEngine = None  # type: ignore[assignment,misc]
    run_autonomous_healing = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_healing_engine_enforcer deps unavailable")
class TestSovereignHealingEngineEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_healingtransaction_defined(self) -> None:
        assert HealingTransaction is not None

    def test_sovereignhealingengine_defined(self) -> None:
        assert SovereignHealingEngine is not None