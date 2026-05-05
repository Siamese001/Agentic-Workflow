"""W2.4 Evidence integration tests — prove evidence contracts flow correctly.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W2.4
"""

from __future__ import annotations

import pytest

from apps_qna.c0_adapter import C0UnavailableError, call_c0
from apps_qna.briefing_validator import validate_briefing
from apps_qna.types.evidence_contracts import (
    BriefingValidationState,
    EvidenceSufficiency,
    FinalEvidenceContract,
    UploadedBriefingEvidenceContract,
)


class TestFinalEvidenceContract:
    """C0-produced FinalEvidenceContract shape and invariants."""

    def test_fec_has_required_fields(self) -> None:
        fec = FinalEvidenceContract(route_id="r1", interview_slug="test")
        d = fec.to_dict()
        for key in ("schema_version", "producer", "grounded", "route_id",
                     "evidence_sufficiency", "interview_slug"):
            assert key in d

    def test_fec_producer_is_c0(self) -> None:
        fec = FinalEvidenceContract()
        assert fec.producer == "agentic_core.C0"

    def test_fec_grounded_by_default(self) -> None:
        fec = FinalEvidenceContract()
        assert fec.grounded is True
        assert fec.evidence_sufficiency == "grounded"

    def test_call_c0_returns_fec_dict(self) -> None:
        result = call_c0(interview_slug="test", route_id="r1")
        assert result["producer"] == "agentic_core.C0"
        assert result["grounded"] is True

    def test_call_c0_includes_claim_confidence(self) -> None:
        result = call_c0(interview_slug="test", route_id="r1")
        assert "claim_confidence" in result
        assert result["claim_confidence"] > 0


class TestUploadedBriefingEvidenceContract:
    """Briefing-produced evidence contract shape and invariants."""

    def test_ubec_has_required_fields(self) -> None:
        ubec = UploadedBriefingEvidenceContract()
        d = ubec.to_dict()
        for key in ("schema_version", "producer", "grounded", "briefing_hash",
                     "validation_state", "evidence_sufficiency"):
            assert key in d

    def test_ubec_producer_is_briefing_validator(self) -> None:
        ubec = UploadedBriefingEvidenceContract()
        assert ubec.producer == "apps_qna.briefing_validator"

    def test_ubec_not_grounded_by_default(self) -> None:
        ubec = UploadedBriefingEvidenceContract()
        assert ubec.grounded is False

    def test_valid_briefing_returns_sufficient(self, tmp_path) -> None:
        p = tmp_path / "briefing.yaml"
        p.write_text("company: TestCo\nrole: DS Director\n")
        result = validate_briefing(briefing_path=str(p))
        assert result.validation_state == BriefingValidationState.SUFFICIENT
        assert result.company_name == "TestCo"
        assert result.role_title == "DS Director"

    def test_valid_briefing_has_size(self, tmp_path) -> None:
        p = tmp_path / "briefing.yaml"
        content = "company: TestCo\nrole: DS Director\n"
        p.write_text(content)
        result = validate_briefing(briefing_path=str(p))
        assert result.briefing_size_bytes > 0


class TestContractDistinction:
    """FEC and UBEC must be clearly distinct."""

    def test_producers_are_different(self) -> None:
        fec = FinalEvidenceContract()
        ubec = UploadedBriefingEvidenceContract()
        assert fec.producer != ubec.producer

    def test_grounded_flags_differ(self) -> None:
        fec = FinalEvidenceContract()
        ubec = UploadedBriefingEvidenceContract()
        assert fec.grounded != ubec.grounded

    def test_dict_shapes_are_different(self) -> None:
        fec = FinalEvidenceContract().to_dict()
        ubec = UploadedBriefingEvidenceContract().to_dict()
        assert fec["producer"] != ubec["producer"]

    def test_call_c0_vs_validate_briefing_different(self) -> None:
        fec = call_c0(interview_slug="test", route_id="r1")
        ubec = validate_briefing(briefing_path=None).to_dict()
        assert fec["producer"] != ubec["producer"]


class TestC0FailClosed:
    """C0 adapter must fail closed when unavailable."""

    def test_c0_unavailable_error_is_raised_on_failure(self, monkeypatch) -> None:
        def _failing_call(*args, **kwargs):
            raise ConnectionError("C0 down")
        monkeypatch.setattr(
            "apps_qna.c0_adapter._call_canonical_c0", _failing_call
        )
        with pytest.raises(C0UnavailableError, match="Fail-closed"):
            call_c0(interview_slug="test", route_id="r1")
