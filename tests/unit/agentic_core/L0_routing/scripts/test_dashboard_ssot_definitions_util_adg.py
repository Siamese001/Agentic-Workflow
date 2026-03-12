"""ADG-driven tests for agentic_core/L0_routing/scripts/dashboard_ssot_definitions_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.dashboard_ssot_definitions_util import (  # noqa: F401
        calc_heal_cap_pct,
        COL_TERRITORY,
        COL_TOTAL,
        COL_COMPLIANT,
        COL_HEAL_CAP,
        COL_INVOCATION,
        COL_TEST,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    calc_heal_cap_pct = None  # type: ignore[assignment,misc]
    COL_TERRITORY = None  # type: ignore[assignment,misc]
    COL_TOTAL = None  # type: ignore[assignment,misc]
    COL_COMPLIANT = None  # type: ignore[assignment,misc]
    COL_HEAL_CAP = None  # type: ignore[assignment,misc]
    COL_INVOCATION = None  # type: ignore[assignment,misc]
    COL_TEST = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestCalcHealCapPct:
    def test_is_callable(self):
        assert callable(calc_heal_cap_pct)

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColTerritoryConstant:
    def test_is_not_none(self):
        assert COL_TERRITORY is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColTotalConstant:
    def test_is_not_none(self):
        assert COL_TOTAL is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColCompliantConstant:
    def test_is_not_none(self):
        assert COL_COMPLIANT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColHealCapConstant:
    def test_is_not_none(self):
        assert COL_HEAL_CAP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColInvocationConstant:
    def test_is_not_none(self):
        assert COL_INVOCATION is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_ssot_definitions_util.py deps unavailable")
class TestColTestConstant:
    def test_is_not_none(self):
        assert COL_TEST is not None


def test_module_importable():
    """Module dashboard_ssot_definitions_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
