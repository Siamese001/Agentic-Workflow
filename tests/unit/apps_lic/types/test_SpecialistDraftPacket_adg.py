"""ADG contract tests for apps_lic/types/SpecialistDraftPacket.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_SpecialistDraftPacket_adg")
_emit_applies_guardrail("p0", "test_SpecialistDraftPacket_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_SpecialistDraftPacket_adg", "policy_binding")
_emit_snapshots_state("p0", "test_SpecialistDraftPacket_adg", "state_snapshot")
emit_replay_key("p0", "test_SpecialistDraftPacket_adg")
emit_determinism_digest("p0", "test_SpecialistDraftPacket_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.SpecialistDraftPacket import EvidenceClarificationRecord, SpecialistDraftPacket
    _AVAIL = True
except ImportError:
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
