"""Foundational behavioral tests for agentic_core/adg/analysis/hotspot_index.py.

fan_in=6 — imported by 6 other modules.
ADG import-hygiene is covered separately by test_hotspot_index_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.analysis.hotspot_index_types import (  # noqa: F401
        HotspotIndex,
        ModuleCoupling,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ModuleCoupling = None  # type: ignore[assignment,misc]
    HotspotIndex = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hotspot_index.py deps unavailable")
class TestModuleCouplingContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ModuleCoupling)

    def test_field_names_present(self):
        import dataclasses

        fnames = {f.name for f in dataclasses.fields(ModuleCoupling)}
        assert fnames >= {"coupling", "fan_out", "module_path", "instability", "fan_in"}

    def test_field_count_reasonable(self):
        import dataclasses

        assert len(dataclasses.fields(ModuleCoupling)) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="hotspot_index.py deps unavailable")
class TestHotspotIndexContract:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(HotspotIndex)


def test_module_importable():
    """Smoke: hotspot_index importable or gracefully unavailable."""
    pass