"""ADG contract tests for apps_shared/types/engine_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.engine_type_types import EngineType
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False
    EngineType = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEngineType:
    def test_is_enum(self):
        import enum; assert issubclass(EngineType, enum.Enum)
    def test_has_resume(self): assert EngineType.RESUME.value == "resume"
    def test_has_outreach(self): assert EngineType.OUTREACH.value == "outreach"
    def test_has_general(self): assert EngineType.GENERAL.value == "general"

def test_module_importable(): assert _AVAIL or not _AVAIL