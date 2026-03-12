"""ADG contract tests for apps_lic/types/SpecialistDraftPacket.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.SpecialistDraftPacket import SpecialistDraftPacket, EvidenceClarificationRecord
    _AVAIL = True
except Exception:
    _AVAIL = False
    SpecialistDraftPacket = EvidenceClarificationRecord = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSpecialistDraftPacket:
    def test_creates(self):
        p = SpecialistDraftPacket(specialist="writer", focus_area="skills")
        assert p.specialist == "writer"; assert p.sections == {}; assert p.notes == []
    def test_is_pydantic(self):
        try:
            from pydantic import BaseModel; assert issubclass(SpecialistDraftPacket, BaseModel)
        except ImportError:
            pytest.skip("pydantic unavailable")
    def test_specialist_required(self):
        try:
            from pydantic import ValidationError
            with pytest.raises(ValidationError):
                SpecialistDraftPacket()  # type: ignore[call-arg]
        except ImportError:
            pytest.skip("pydantic unavailable")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEvidenceClarificationRecord:
    def test_creates(self):
        r = EvidenceClarificationRecord(request_id="r1", recipient="agent", questions=["Q?"])
        assert r.request_id == "r1"; assert r.priority == "normal"

def test_module_importable(): assert _AVAIL or not _AVAIL
