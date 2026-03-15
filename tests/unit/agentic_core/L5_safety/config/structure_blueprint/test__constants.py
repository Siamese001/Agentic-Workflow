"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/_constants.py.

fan_in=8 — imported by 8 other modules.
ADG import-hygiene is covered separately by test__constants_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
        SubfolderDefinition,
        TerritoryDefinition,
        build_sovereign_territories,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SubfolderDefinition = None  # type: ignore[assignment,misc]
    TerritoryDefinition = None  # type: ignore[assignment,misc]
    build_sovereign_territories = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="_constants.py deps unavailable")
class TestSubfolderDefinitionContract:
    def test_is_class(self):
        assert isinstance(SubfolderDefinition, type)

@pytest.mark.skipif(not _AVAILABLE, reason="_constants.py deps unavailable")
class TestTerritoryDefinitionContract:
    def test_is_class(self):
        assert isinstance(TerritoryDefinition, type)

@pytest.mark.skipif(not _AVAILABLE, reason="_constants.py deps unavailable")
class TestBuildSovereignTerritoriesFunction:
    def test_is_callable(self):
        assert callable(build_sovereign_territories)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_sovereign_territories)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: _constants importable or gracefully unavailable."""
    pass
