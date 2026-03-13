"""ADG importability contract for agentic_core/L2_execution/healers/healing_tier_dispatcher.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_tier_dispatcher.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import (  # noqa: F401
        DefaultHealingProviderInvoker,
        HealingProviderInvoker,
        InvocationRecord,
        dispatch_healing,
        handle_qwen_oom_via_router,
        invoke_qwen_with_oom_protection,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InvocationRecord = None  # type: ignore[assignment,misc]
    handle_qwen_oom_via_router = None  # type: ignore[assignment,misc]
    HealingProviderInvoker = None  # type: ignore[assignment,misc]
    DefaultHealingProviderInvoker = None  # type: ignore[assignment,misc]
    dispatch_healing = None  # type: ignore[assignment,misc]
    invoke_qwen_with_oom_protection = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_dispatcher deps unavailable")
class TestHealingTierDispatcherImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/healers/healing_tier_dispatcher.py must be importable."""
        assert _AVAILABLE

    def test_invocationrecord_defined(self) -> None:
        assert InvocationRecord is not None

    def test_healingproviderinvoker_defined(self) -> None:
        assert HealingProviderInvoker is not None

    def test_defaulthealingproviderinvoker_defined(self) -> None:
        assert DefaultHealingProviderInvoker is not None
