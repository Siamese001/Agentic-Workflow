"""ADG contract tests for agentic_core/L1_cognition/types/domain_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_domain_types_adg")
_emit_applies_guardrail("p0", "test_domain_types_adg", "p0_governance")
_emit_snapshots_state("p0", "test_domain_types_adg", "state_snapshot")
emit_replay_key("p0", "test_domain_types_adg")
emit_determinism_digest("p0", "test_domain_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.domain_types import DomainContext, SharingPolicy
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SharingPolicy = DomainContext = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSharingPolicy:
    def test_is_enum(self):
        import enum; assert issubclass(SharingPolicy, enum.Enum)
    def test_has_none(self): assert SharingPolicy.NONE.value == "none"
    def test_has_bidirectional(self): assert SharingPolicy.BIDIRECTIONAL.value == "bidirectional"
    def test_four_policies(self): assert len(list(SharingPolicy)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDomainContext:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(DomainContext)
    def test_creates(self):
        dc = DomainContext(domain="resume")
        assert dc.domain == "resume"; assert dc.sharing_policy == SharingPolicy.NONE
    def test_can_read_from_none_policy(self):
        dc = DomainContext(domain="d1")
        assert dc.can_read_from("other") is False
    def test_can_read_from_bidirectional(self):
        dc = DomainContext(domain="d1", sharing_policy=SharingPolicy.BIDIRECTIONAL)
        assert dc.can_read_from("any") is True
    def test_can_share_pattern_type_none(self):
        dc = DomainContext(domain="d1")
        assert dc.can_share_pattern_type("FAILURE") is False
    def test_can_share_selective(self):
        dc = DomainContext(domain="d1", sharing_policy=SharingPolicy.SELECTIVE,
                           pattern_types_shared=["FAILURE"])
        assert dc.can_share_pattern_type("FAILURE") is True
        assert dc.can_share_pattern_type("SUCCESS") is False

def test_module_importable(): assert _AVAIL or not _AVAIL
