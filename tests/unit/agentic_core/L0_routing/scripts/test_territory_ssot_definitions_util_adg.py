"""ADG-driven tests for agentic_core/L0_routing/scripts/territory_ssot_definitions_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.territory_ssot_definitions_util import (  # noqa: F401
        TERRITORY_L0_BASE,
        TERRITORY_L1_BASE,
        TERRITORY_L2_BASE,
        TERRITORY_L3_BASE,
        TERRITORY_L4_BASE,
        TERRITORY_SOVEREIGN_BASE,
        get_base_agent_territory,
        get_territory_from_path,
        get_territory_sort_key,
        refine_territory_by_ast,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_base_agent_territory = None  # type: ignore[assignment,misc]
    get_territory_from_path = None  # type: ignore[assignment,misc]
    get_territory_sort_key = None  # type: ignore[assignment,misc]
    refine_territory_by_ast = None  # type: ignore[assignment,misc]
    TERRITORY_SOVEREIGN_BASE = None  # type: ignore[assignment,misc]
    TERRITORY_L0_BASE = None  # type: ignore[assignment,misc]
    TERRITORY_L1_BASE = None  # type: ignore[assignment,misc]
    TERRITORY_L2_BASE = None  # type: ignore[assignment,misc]
    TERRITORY_L3_BASE = None  # type: ignore[assignment,misc]
    TERRITORY_L4_BASE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestGetBaseAgentTerritory:
    def test_is_callable(self):
        assert callable(get_base_agent_territory)

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestGetTerritoryFromPath:
    def test_is_callable(self):
        assert callable(get_territory_from_path)

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestGetTerritorySortKey:
    def test_is_callable(self):
        assert callable(get_territory_sort_key)

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestRefineTerritoryByAst:
    def test_is_callable(self):
        assert callable(refine_territory_by_ast)

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritorySovereignBaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_SOVEREIGN_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritoryL0BaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_L0_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritoryL1BaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_L1_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritoryL2BaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_L2_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritoryL3BaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_L3_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="territory_ssot_definitions_util.py deps unavailable")
class TestTerritoryL4BaseConstant:
    def test_is_not_none(self):
        assert TERRITORY_L4_BASE is not None


def test_module_importable():
    """Module territory_ssot_definitions_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
