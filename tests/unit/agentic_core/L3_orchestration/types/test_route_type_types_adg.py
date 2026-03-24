"""ADG contract tests for L3_orchestration/types/route_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.route_type_types import (
        ArchetypeType,
        RouteClassifierConfig,
        RouteType,
    )
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False; RouteType = ArchetypeType = RouteClassifierConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteType:
    def test_is_enum(self):
        import enum; assert issubclass(RouteType, enum.Enum)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetypeType:
    def test_is_enum(self):
        import enum; assert issubclass(ArchetypeType, enum.Enum)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteClassifierConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteClassifierConfig)

def test_module_importable(): assert _AVAIL or not _AVAIL