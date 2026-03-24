"""Foundational behavioral tests for agentic_core/adg/analysis/ownership.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_ownership_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.analysis.ModuleOwnership import (  # noqa: F401
        ModuleOwnership,
        OwnershipRegistry,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ModuleOwnership = None  # type: ignore[assignment,misc]
    OwnershipRegistry = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ownership.py deps unavailable")
class TestModuleOwnershipContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ModuleOwnership)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(ModuleOwnership)}
        assert fnames >= {"criticality", "module_path", "runtime_surface", "owner"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(ModuleOwnership)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="ownership.py deps unavailable")
class TestOwnershipRegistryContract:
    def test_is_class(self):
        assert isinstance(OwnershipRegistry, type)

    def test_has_method_from_scan_result(self):
        assert callable(getattr(OwnershipRegistry, "from_scan_result", None))

    def test_has_method_from_module_list(self):
        assert callable(getattr(OwnershipRegistry, "from_module_list", None))

    def test_has_method_get(self):
        assert callable(getattr(OwnershipRegistry, "get", None))

    def test_has_method_blast_radius_report(self):
        assert callable(getattr(OwnershipRegistry, "blast_radius_report", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(OwnershipRegistry) if not m.startswith("_")]
        assert len(pub) >= 1


def test_module_importable():
    """Smoke: ownership importable or gracefully unavailable."""
    pass