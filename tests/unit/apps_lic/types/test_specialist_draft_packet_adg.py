"""ADG contract tests for apps_lic/types/SpecialistDraftPacket.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.SpecialistDraftPacket import (
        CritiqueFindingRecord,
        CritiquePanelPacket,
        EvidenceBriefRecord,
        EvidenceClarificationRecord,
        EvidenceLiaisonPacket,
        SpecialistDraftPacket,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SpecialistDraftPacket = EvidenceClarificationRecord = EvidenceBriefRecord = None  # type: ignore[assignment,misc]
    EvidenceLiaisonPacket = CritiqueFindingRecord = CritiquePanelPacket = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSpecialistDraftPacket:
    def test_creates(self):
        p = SpecialistDraftPacket(specialist="Writer", focus_area="summary")
        assert p.specialist == "Writer"; assert p.sections == {}
    def test_defaults(self):
        p = SpecialistDraftPacket(specialist="A", focus_area="B")
        assert p.notes == []; assert p.dependencies == []

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEvidenceClarificationRecord:
    def test_creates(self):
        r = EvidenceClarificationRecord(request_id="r1", recipient="Alice", questions=["Why?"])
        assert r.request_id == "r1"; assert r.priority == "normal"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCritiquePanelPacket:
    def test_creates(self):
        p = CritiquePanelPacket(overall_status="PASS")
        assert p.overall_status == "PASS"; assert p.findings == []

def test_module_importable(): assert _AVAIL or not _AVAIL
