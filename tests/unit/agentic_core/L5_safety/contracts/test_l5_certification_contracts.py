"""Unit tests for agentic_core.L5_safety.contracts.l5_certification_contracts.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L5 surface.
The three frozen evidence dataclasses (ChildCertifierReceipt,
EgressCertificationReceipt, L5CertificationPacket) enforce AG-4 NOT_APPLICABLE
justification, hex64 digest shape, closed packet-status vocab, and the
forbidden-runtime-disposition scan. Exhaustive coverage of construction,
__post_init__ ValueError paths, frozen immutability, and the closed vocabs.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L5_safety.contracts._vocab import FORBIDDEN_RUNTIME_DISPOSITIONS
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    _CHILD_APPLICABILITY_VALUES,
    _PACKET_ALLOWED_STATUSES,
    ChildCertifierReceipt,
    EgressCertificationReceipt,
    L5CertificationPacket,
)

_HEX64 = "a" * 64


class TestClosedVocabs:
    def test_packet_statuses(self) -> None:
        assert _PACKET_ALLOWED_STATUSES == frozenset({"L5_CERTIFIED", "L5_NOT_CERTIFIED"})

    def test_child_applicability_values(self) -> None:
        assert _CHILD_APPLICABILITY_VALUES == frozenset(
            {"REQUIRED", "OPTIONAL", "NOT_APPLICABLE"}
        )


class TestChildCertifierReceipt:
    def test_minimal_construction_defaults(self) -> None:
        r = ChildCertifierReceipt(domain="apps_x", applicability="REQUIRED", certified=True)
        assert r.evidence_digest == ""
        assert r.reason_codes == ()
        assert r.notes == ""

    def test_empty_domain_raises(self) -> None:
        with pytest.raises(ValueError, match="domain must be non-empty"):
            ChildCertifierReceipt(domain="", applicability="REQUIRED", certified=True)

    @pytest.mark.parametrize("applic", ["REQUIRED", "OPTIONAL"])
    def test_valid_non_na_applicability(self, applic: str) -> None:
        r = ChildCertifierReceipt(domain="d", applicability=applic, certified=False)
        assert r.applicability == applic

    def test_invalid_applicability_raises(self) -> None:
        with pytest.raises(ValueError, match="is not one of"):
            ChildCertifierReceipt(domain="d", applicability="MAYBE", certified=True)

    def test_not_applicable_without_justification_raises(self) -> None:
        with pytest.raises(ValueError, match="requires non-empty"):
            ChildCertifierReceipt(domain="d", applicability="NOT_APPLICABLE", certified=False)

    def test_not_applicable_with_full_justification_ok(self) -> None:
        r = ChildCertifierReceipt(
            domain="d",
            applicability="NOT_APPLICABLE",
            certified=False,
            not_applicable_reason="no egress",
            deciding_policy_ref="pol-1",
            deciding_stage="stage-1",
        )
        assert r.applicability == "NOT_APPLICABLE"

    def test_not_applicable_partial_justification_raises(self) -> None:
        with pytest.raises(ValueError, match="deciding_stage"):
            ChildCertifierReceipt(
                domain="d",
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="r",
                deciding_policy_ref="p",
                # deciding_stage omitted
            )

    def test_bad_evidence_digest_raises(self) -> None:
        with pytest.raises(ValueError, match="64 lowercase hex"):
            ChildCertifierReceipt(
                domain="d", applicability="REQUIRED", certified=True, evidence_digest="xyz",
            )

    def test_valid_hex64_evidence_digest_ok(self) -> None:
        r = ChildCertifierReceipt(
            domain="d", applicability="REQUIRED", certified=True, evidence_digest=_HEX64,
        )
        assert r.evidence_digest == _HEX64

    def test_frozen(self) -> None:
        r = ChildCertifierReceipt(domain="d", applicability="REQUIRED", certified=True)
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.certified = False  # type: ignore[misc]


class TestEgressCertificationReceipt:
    def _ok(self, **overrides: object) -> EgressCertificationReceipt:
        kwargs = {
            "provider_ref": "registry://prov-1",
            "response_digest": _HEX64,
            "redaction_policy_ref": "redact-1",
        }
        kwargs.update(overrides)
        return EgressCertificationReceipt(**kwargs)  # type: ignore[arg-type]

    def test_valid_construction(self) -> None:
        assert self._ok().certified is False  # default

    def test_empty_provider_ref_raises(self) -> None:
        with pytest.raises(ValueError, match="provider_ref must be non-empty"):
            self._ok(provider_ref="")

    def test_empty_redaction_policy_raises(self) -> None:
        with pytest.raises(ValueError, match="redaction_policy_ref must be non-empty"):
            self._ok(redaction_policy_ref="")

    def test_empty_response_digest_raises(self) -> None:
        with pytest.raises(ValueError, match="response_digest must be non-empty"):
            self._ok(response_digest="")

    def test_non_hex64_response_digest_raises(self) -> None:
        with pytest.raises(ValueError, match="64 lowercase"):
            self._ok(response_digest="deadbeef")

    def test_frozen(self) -> None:
        r = self._ok()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.certified = True  # type: ignore[misc]


class TestL5CertificationPacket:
    def test_evidence_only_and_output_kind(self) -> None:
        p = L5CertificationPacket(certification_status="L5_CERTIFIED")
        assert p.is_evidence_only() is True
        assert p.output_kind == "result"

    @pytest.mark.parametrize("status", ["L5_CERTIFIED", "L5_NOT_CERTIFIED"])
    def test_allowed_statuses(self, status: str) -> None:
        assert L5CertificationPacket(certification_status=status).certification_status == status

    @pytest.mark.parametrize("status", ["", "L5_PARTIAL", "L5_NOT_APPLICABLE", "CERTIFIED"])
    def test_forbidden_statuses_raise(self, status: str) -> None:
        with pytest.raises(ValueError, match="is not one of"):
            L5CertificationPacket(certification_status=status)

    def test_forbidden_disposition_token_in_producer_ref_raises(self) -> None:
        token = next(iter(FORBIDDEN_RUNTIME_DISPOSITIONS))
        with pytest.raises(ValueError, match="forbidden"):
            L5CertificationPacket(
                certification_status="L5_CERTIFIED", producer_ref=f"producer-{token}",
            )

    def test_clean_producer_ref_ok(self) -> None:
        p = L5CertificationPacket(
            certification_status="L5_CERTIFIED", producer_ref="l5-packet-producer",
        )
        assert p.producer_ref == "l5-packet-producer"

    def test_bad_digest_raises(self) -> None:
        with pytest.raises(ValueError, match="64 lowercase hex"):
            L5CertificationPacket(certification_status="L5_CERTIFIED", digest_sha256="nothex")

    def test_valid_digest_ok(self) -> None:
        p = L5CertificationPacket(certification_status="L5_CERTIFIED", digest_sha256=_HEX64)
        assert p.digest_sha256 == _HEX64

    def test_carries_child_and_egress_receipts(self) -> None:
        child = ChildCertifierReceipt(domain="d", applicability="REQUIRED", certified=True)
        egress = EgressCertificationReceipt(
            provider_ref="p", response_digest=_HEX64, redaction_policy_ref="r",
        )
        p = L5CertificationPacket(
            certification_status="L5_CERTIFIED",
            child_receipts=(child,),
            egress_receipts=(egress,),
        )
        assert p.child_receipts == (child,)
        assert p.egress_receipts == (egress,)

    def test_frozen(self) -> None:
        p = L5CertificationPacket(certification_status="L5_CERTIFIED")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.producer_ref = "x"  # type: ignore[misc]
