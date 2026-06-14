"""Unit tests for agentic_core.runtime.contracts.final_evidence_contract.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``final_evidence_contract`` (fan_in=74, second-highest) is C0's evidence-collection
output. AG-4 invariant: only support_status PASS is passing; NOT_APPLICABLE needs a
reason; L5 cert-ref fail-closed. Frozen/slots dataclasses — exhaustive coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    STATUS_NOT_APPLICABLE,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PASSING_VALUES,
    SUPPORT_STATUS_WEAK,
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY, RuntimePosture


class TestStatusSentinels:
    def test_sentinel_values(self) -> None:
        assert STATUS_UNKNOWN == "UNKNOWN"
        assert STATUS_NOT_APPLICABLE == "NOT_APPLICABLE"
        assert SUPPORT_STATUS_PASS == "PASS"
        assert ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY == "C0_EVIDENCE_DATA_ONLY"

    def test_only_pass_is_passing(self) -> None:
        assert SUPPORT_STATUS_PASSING_VALUES == frozenset({SUPPORT_STATUS_PASS})

    @pytest.mark.parametrize(
        "status",
        [STATUS_UNKNOWN, SUPPORT_STATUS_EMPTY, SUPPORT_STATUS_BLOCKED,
         SUPPORT_STATUS_CONFLICTED, SUPPORT_STATUS_WEAK],
    )
    def test_non_pass_sentinels_excluded(self, status: str) -> None:
        assert status not in SUPPORT_STATUS_PASSING_VALUES


class TestEvidenceItem:
    def test_required_fields(self) -> None:
        e = EvidenceItem(source="chroma", content="some text")
        assert e.source == "chroma"
        assert e.content == "some text"

    def test_defaults(self) -> None:
        e = EvidenceItem(source="s", content="c")
        assert e.content_type == "text"
        assert e.confidence_score == 0.0
        assert e.origin == Origin.RETRIEVED_DATA
        assert e.evidence_id == ""
        assert e.citation_anchor == ""

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            EvidenceItem(source="s", content="c").content = "x"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(EvidenceItem(source="s", content="c"), "__dict__")


def _fec(**overrides: object) -> FinalEvidenceContract:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        l5_certification_ref="cert-ref-1",
    )
    base.update(overrides)
    return FinalEvidenceContract(**base)  # type: ignore[arg-type]


class TestFinalEvidenceContract:
    def test_valid_construction(self) -> None:
        c = _fec()
        assert c.app_id == "apps_rg"

    def test_defaults(self) -> None:
        c = _fec()
        assert c.evidence_items == ()
        assert c.retrieval_sources == ()
        assert c.support_target_met is False
        assert c.evidence_sufficiency_score == 0.0
        assert c.support_status == STATUS_UNKNOWN
        assert c.schema_version == "W6.0"
        assert c.blocked_source_refs == ()
        assert c.contradiction_report == ""

    def test_posture_default_read_only(self) -> None:
        c = _fec()
        assert isinstance(c.posture, RuntimePosture)
        assert c.posture == POSTURE_READ_ONLY

    def test_carries_evidence_items(self) -> None:
        items = (EvidenceItem(source="s1", content="a"), EvidenceItem(source="s2", content="b"))
        c = _fec(evidence_items=items)
        assert c.evidence_items == items

    def test_missing_cert_ref_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _fec(l5_certification_ref="")

    def test_not_applicable_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires a reason"):
            _fec(support_status=STATUS_NOT_APPLICABLE)

    def test_not_applicable_with_reason_ok(self) -> None:
        c = _fec(support_status=STATUS_NOT_APPLICABLE, not_applicable_reason="cache-hit route")
        assert c.support_status == STATUS_NOT_APPLICABLE

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _fec().support_status = SUPPORT_STATUS_PASS  # type: ignore[misc]


class TestFinalEvidenceContractHelpers:
    def test_support_status_is_passing_only_for_pass(self) -> None:
        assert _fec(support_status=SUPPORT_STATUS_PASS).support_status_is_passing() is True

    @pytest.mark.parametrize(
        "status",
        [STATUS_UNKNOWN, SUPPORT_STATUS_EMPTY, SUPPORT_STATUS_BLOCKED,
         SUPPORT_STATUS_CONFLICTED, SUPPORT_STATUS_WEAK],
    )
    def test_non_pass_status_not_passing(self, status: str) -> None:
        assert _fec(support_status=status).support_status_is_passing() is False

    def test_has_blocked_sources(self) -> None:
        assert _fec().has_blocked_sources() is False
        assert _fec(blocked_source_refs=("src-1",)).has_blocked_sources() is True

    def test_has_contradictions(self) -> None:
        assert _fec().has_contradictions() is False
        assert _fec(contradiction_report="report-ref").has_contradictions() is True
