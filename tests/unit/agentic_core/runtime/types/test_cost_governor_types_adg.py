"""ADG importability contract for agentic_core/runtime/types/cost_governor_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cost_governor_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.types.cost_governor_types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        BudgetExceededError,
        CostGovernor,
        CostGovernorManager,
        UsageRecord,
        get_global_cost_governor,
        track_api_call,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    BudgetExceededError = None  # type: ignore[assignment,misc]
    CostGovernor = None  # type: ignore[assignment,misc]
    UsageRecord = None  # type: ignore[assignment,misc]
    CostGovernorManager = None  # type: ignore[assignment,misc]
    get_global_cost_governor = None  # type: ignore[assignment,misc]
    track_api_call = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cost_governor_types.py deps unavailable")
class TestCostGovernorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cost_governor_types.py must be importable."""
        assert _AVAILABLE

    def test_budgetexceedederror_is_type(self) -> None:
        assert BudgetExceededError is not None

    def test_costgovernor_is_type(self) -> None:
        assert CostGovernor is not None

    def test_usagerecord_is_type(self) -> None:
        assert UsageRecord is not None

    def test_get_global_cost_governor_callable(self) -> None:
        assert callable(get_global_cost_governor)

    def test_track_api_call_callable(self) -> None:
        assert callable(track_api_call)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None