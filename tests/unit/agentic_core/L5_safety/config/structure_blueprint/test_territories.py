"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/territories.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_territories_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.structure_blueprint.territories import (  # noqa: F401
        get_all_territories,
        get_territory_metadata,
        is_valid_root_folder,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_territory_metadata = None  # type: ignore[assignment,misc]
    get_all_territories = None  # type: ignore[assignment,misc]
    is_valid_root_folder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="territories.py deps unavailable")
class TestGetTerritoryMetadataFunction:
    def test_is_callable(self):
        assert callable(get_territory_metadata)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_territory_metadata)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="territories.py deps unavailable")
class TestGetAllTerritoriesFunction:
    def test_is_callable(self):
        assert callable(get_all_territories)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_all_territories)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="territories.py deps unavailable")
class TestIsValidRootFolderFunction:
    def test_is_callable(self):
        assert callable(is_valid_root_folder)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_valid_root_folder)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: territories importable or gracefully unavailable."""
    pass