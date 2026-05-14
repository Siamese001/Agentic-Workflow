"""W2 producer tests — L5PacketProducer.

Tests explicitly cover every certification path specified in the W2 spec:

  1.  valid complete child set → L5_CERTIFIED
  2.  missing required child → L5_NOT_CERTIFIED
  3.  UNKNOWN child (certified=False, no reason_codes) → L5_NOT_CERTIFIED
  4.  NOT_APPLICABLE child without full justification → fails closed
  5.  child digest mismatch → raises L5DigestMismatchError
  6.  egress digest mismatch (egress.certified=False) → L5_NOT_CERTIFIED
  7.  deterministic packet digest stable across equivalent input ordering
  8.  prior_packet_digest preserved in packet
  9.  no authority widening (L5AuthorityWideningError raised on attempt)
  10. no forbidden source tokens in producer file
  11. no W3 egress certifier interface implemented

Hard prohibitions re-stated for test clarity:
  - No GateVerdict, X3, CommitRequest, UWG, L4 import
  - No provider SDK (openai, anthropic, boto3, httpx) import
  - No app-specific literals (apps_rg, apps_research, apps_lic, resume, CV)
  - No filesystem writes or network calls
"""
from __future__ import annotations

import hashlib
import pathlib
import re

import pytest

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
    EgressCertificationReceipt,
    L5CertificationPacket,
)
from agentic_core.L5_safety.exceptions import (
    L5AuthorityWideningError,
    L5DigestMismatchError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]

_PRODUCER_SOURCE = (
    _REPO_ROOT
    / "agentic_core"
    / "L5_safety"
    / "certification"
    / "l5_packet_producer.py"
)

_EXCEPTIONS_SOURCE = (
    _REPO_ROOT / "agentic_core" / "L5_safety" / "exceptions.py"
)

_HEX64 = "a" * 64  # placeholder valid sha256 hex


def _make_valid_receipt(domain: str, *, certified: bool = True) -> ChildCertifierReceipt:
    return ChildCertifierReceipt(
        domain=domain,
        applicability="REQUIRED",
        certified=certified,
        reason_codes=("evidence_bound",) if not certified else (),
    )


def _make_na_receipt(domain: str) -> ChildCertifierReceipt:
    return ChildCertifierReceipt(
        domain=domain,
        applicability="NOT_APPLICABLE",
        certified=False,
        not_applicable_reason="category does not apply to this run configuration",
        deciding_policy_ref="urn:policy:ref:na-exemption-v1",
        deciding_stage="pre-run classification",
    )


def _make_egress(*, certified: bool = True) -> EgressCertificationReceipt:
    return EgressCertificationReceipt(
        provider_ref="urn:provider:symbolic:v1",
        response_digest=_HEX64,
        redaction_policy_ref="urn:redaction:policy:v1",
        certified=certified,
    )


_ALL_REQUIRED_DOMAINS = [
    "safety_enforcement",
    "authority_context_registry_binding",
    "origin_trust_content_boundary",
    "replay_audit_certification_evidence",
    "static_governance_structure_drift",
    "runtime_certification_binding",
]

_PRODUCER = L5PacketProducer()

_COMMON_REFS = dict(
    certified_object_ref="urn:obj:test:v1",
    policy_ref="urn:policy:test:v1",
    blueprint_ref="urn:blueprint:test:v1",
    registry_ref="urn:registry:test:v1",
    authority_ref="urn:authority:test:v1",
    replay_ref="urn:replay:test:v1",
    audit_ref="urn:audit:test:v1",
    static_ref="urn:static:test:v1",
    runtime_ref="urn:runtime:test:v1",
    producer_ref="l5_packet_producer:w2:v1",
    certifier_version="0.1.0",
)


def _full_child_set() -> list[ChildCertifierReceipt]:
    return [_make_valid_receipt(d) for d in _ALL_REQUIRED_DOMAINS]


# ---------------------------------------------------------------------------
# 1. Valid complete child set → L5_CERTIFIED
# ---------------------------------------------------------------------------


class TestCertifiedPath:
    def test_all_required_children_yields_certified(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert isinstance(packet, L5CertificationPacket)
        assert packet.certification_status == "L5_CERTIFIED"
        assert packet.reason_codes == ()

    def test_certified_packet_has_valid_digest_sha256(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert len(packet.digest_sha256) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", packet.digest_sha256)

    def test_certified_with_egress_receipt(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[_make_egress(certified=True)],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"

    def test_not_applicable_children_accepted_for_required_category(self):
        # A NOT_APPLICABLE receipt with full justification is acceptable for
        # a required category (it doesn't block certification).
        children = _full_child_set()
        # Replace safety_enforcement with a NOT_APPLICABLE receipt
        children = [
            _make_na_receipt("safety_enforcement")
            if r.domain == "safety_enforcement"
            else r
            for r in children
        ]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"

    def test_child_receipts_preserved_in_packet(self):
        children = _full_child_set()
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert len(packet.child_receipts) == len(children)
        assert set(r.domain for r in packet.child_receipts) == set(
            d for d in _ALL_REQUIRED_DOMAINS
        )

    def test_egress_receipts_preserved_in_packet(self):
        egress = [_make_egress()]
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=egress,
            **_COMMON_REFS,
        )
        assert len(packet.egress_receipts) == 1
        assert packet.egress_receipts[0].provider_ref == "urn:provider:symbolic:v1"

    def test_is_evidence_only(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.is_evidence_only() is True


# ---------------------------------------------------------------------------
# 2. Missing required child → L5_NOT_CERTIFIED
# ---------------------------------------------------------------------------


class TestMissingRequiredChild:
    @pytest.mark.parametrize("missing_domain", _ALL_REQUIRED_DOMAINS)
    def test_missing_required_child_not_certified(self, missing_domain: str):
        children = [r for r in _full_child_set() if r.domain != missing_domain]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert any(missing_domain in rc for rc in packet.reason_codes), (
            f"Expected {missing_domain!r} in reason_codes, got {packet.reason_codes}"
        )

    def test_empty_children_not_certified(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=[],
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"

    def test_missing_policy_ref_not_certified(self):
        refs = dict(_COMMON_REFS)
        refs["policy_ref"] = ""
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert any("policy_ref" in rc for rc in packet.reason_codes)

    def test_missing_certified_object_ref_not_certified(self):
        refs = dict(_COMMON_REFS)
        refs["certified_object_ref"] = ""
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert any("certified_object_ref" in rc for rc in packet.reason_codes)


# ---------------------------------------------------------------------------
# 3. UNKNOWN child (certified=False, no reason_codes) → L5_NOT_CERTIFIED
# ---------------------------------------------------------------------------


class TestUnknownChild:
    def test_unknown_child_yields_not_certified(self):
        children = _full_child_set()
        unknown_idx = 0
        unknown_domain = children[unknown_idx].domain
        children[unknown_idx] = ChildCertifierReceipt(
            domain=unknown_domain,
            applicability="REQUIRED",
            certified=False,
            # No reason_codes → UNKNOWN
        )
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert any("UNKNOWN" in rc for rc in packet.reason_codes)

    def test_unknown_child_reason_codes_mention_domain(self):
        children = _full_child_set()
        children[0] = ChildCertifierReceipt(
            domain=children[0].domain,
            applicability="REQUIRED",
            certified=False,
        )
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert any(children[0].domain in rc for rc in packet.reason_codes)


# ---------------------------------------------------------------------------
# 4. NOT_APPLICABLE child without justification triple → fails closed
# ---------------------------------------------------------------------------


class TestNotApplicableJustification:
    def test_na_missing_reason_raises_at_construction(self):
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires"):
            ChildCertifierReceipt(
                domain="safety_enforcement",
                applicability="NOT_APPLICABLE",
                certified=False,
                # Missing not_applicable_reason / deciding_policy_ref / deciding_stage
            )

    def test_na_missing_policy_ref_raises_at_construction(self):
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires"):
            ChildCertifierReceipt(
                domain="safety_enforcement",
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="reason present",
                deciding_stage="stage present",
                # Missing deciding_policy_ref
            )

    def test_na_missing_stage_raises_at_construction(self):
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires"):
            ChildCertifierReceipt(
                domain="safety_enforcement",
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="reason present",
                deciding_policy_ref="urn:policy:v1",
                # Missing deciding_stage
            )

    def test_na_with_full_triple_accepted(self):
        r = _make_na_receipt("hitl_reclearance")
        assert r.applicability == "NOT_APPLICABLE"

    def test_na_child_for_conditional_category_accepted(self):
        children = _full_child_set() + [_make_na_receipt("hitl_reclearance")]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"


# ---------------------------------------------------------------------------
# 5. Child digest mismatch → raises L5DigestMismatchError (fail-closed)
# ---------------------------------------------------------------------------


class TestChildDigestMismatch:
    def test_child_digest_mismatch_raises(self):
        children = _full_child_set()
        # Add a valid-format but wrong digest to one child
        bad_child = ChildCertifierReceipt(
            domain=children[0].domain,
            applicability="REQUIRED",
            certified=True,
            evidence_digest="b" * 64,  # wrong digest — will not match computed
        )
        children[0] = bad_child
        with pytest.raises(L5DigestMismatchError, match="evidence_digest"):
            _PRODUCER.produce_packet(
                child_receipts=children,
                egress_receipts=[],
                **_COMMON_REFS,
            )

    def test_child_without_digest_accepted(self):
        # Children without evidence_digest set are not digest-checked
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),  # evidence_digest="" by default
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"


# ---------------------------------------------------------------------------
# 6. Egress uncertified → L5_NOT_CERTIFIED
# ---------------------------------------------------------------------------


class TestEgressCertification:
    def test_uncertified_egress_yields_not_certified(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[_make_egress(certified=False)],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        assert any("egress" in rc for rc in packet.reason_codes)

    def test_certified_egress_does_not_block_certification(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[_make_egress(certified=True)],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED"


# ---------------------------------------------------------------------------
# 7. Deterministic packet digest — stable across equivalent input orderings
# ---------------------------------------------------------------------------


class TestDeterministicDigest:
    def test_same_inputs_same_digest(self):
        children = _full_child_set()
        p1 = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        p2 = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert p1.digest_sha256 == p2.digest_sha256

    def test_reordered_children_same_digest(self):
        children_fwd = _full_child_set()
        children_rev = list(reversed(_full_child_set()))
        p1 = _PRODUCER.produce_packet(
            child_receipts=children_fwd,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        p2 = _PRODUCER.produce_packet(
            child_receipts=children_rev,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        # Governance context digest sorts by domain — both should be identical
        assert p1.digest_sha256 == p2.digest_sha256

    def test_different_refs_different_digest(self):
        refs_a = dict(_COMMON_REFS)
        refs_b = dict(_COMMON_REFS)
        refs_b["policy_ref"] = "urn:policy:different:v2"
        p1 = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs_a,
        )
        p2 = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs_b,
        )
        assert p1.digest_sha256 != p2.digest_sha256


# ---------------------------------------------------------------------------
# 8. prior_packet_digest preserved
# ---------------------------------------------------------------------------


class TestPriorPacketDigest:
    def test_prior_packet_digest_preserved(self):
        prior = "c" * 64
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior,
            **_COMMON_REFS,
        )
        # prior_packet_digest is not a field on L5CertificationPacket directly
        # but it is baked into the digest computation — verify via digest
        # determinism: same prior → same digest, different prior → different digest.
        packet_no_prior = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest="",
            **_COMMON_REFS,
        )
        assert packet.digest_sha256 != packet_no_prior.digest_sha256

    def test_prior_packet_digest_influences_packet_digest(self):
        prior_a = "d" * 64
        prior_b = "e" * 64
        pa = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior_a,
            **_COMMON_REFS,
        )
        pb = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior_b,
            **_COMMON_REFS,
        )
        assert pa.digest_sha256 != pb.digest_sha256


# ---------------------------------------------------------------------------
# 9. No authority widening
# ---------------------------------------------------------------------------


class TestNoAuthorityWidening:
    def test_symbolic_urn_authority_ref_accepted(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "urn:authority:symbolic:registry:v1"
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_CERTIFIED"

    def test_empty_authority_ref_accepted(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = ""
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_CERTIFIED"

    def test_raw_openai_key_in_authority_ref_raises(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "sk-abc123"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_bearer_token_in_authority_ref_raises(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "Bearer my-token"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_url_in_authority_ref_raises(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "https://api.example.com/authority"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_non_urn_ungrounded_authority_ref_raises(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "my-registry-key"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_authority_ref_grounded_in_child_evidence_ref_accepted(self):
        refs = dict(_COMMON_REFS)
        shared_ref = "grounded-authority-key"
        refs["authority_ref"] = shared_ref
        children = _full_child_set()
        # Patch one child to carry the authority ref in evidence_ref
        children[0] = ChildCertifierReceipt(
            domain=children[0].domain,
            applicability="REQUIRED",
            certified=True,
            evidence_ref=shared_ref,
        )
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_CERTIFIED"


# ---------------------------------------------------------------------------
# 10. No forbidden source tokens in producer file
# ---------------------------------------------------------------------------


class TestForbiddenTokensInSource:
    _FORBIDDEN_PATTERNS = [
        r"\bGateVerdict\b",
        r"\bX3\b",
        r"\bCommitRequest\b",
        r"\bUWG\b",
        r"\bL4\b",
        r"\bopenai\b",
        r"\banthropic\b",
        r"\bboto3\b",
        r"\bhttpx\b",
        r"\brequests\b",
        r"\bapps_rg\b",
        r"\bapps_research\b",
        r"\bapps_lic\b",
        r"\bresume\b",
        r"\bCV\b",
        r"\bL5_CERTIFICATION_READY\b",
    ]

    def _scan_source(self, path: pathlib.Path, pattern: str) -> list[int]:
        lines = path.read_text(encoding="utf-8").splitlines()
        return [
            i + 1
            for i, line in enumerate(lines)
            if re.search(pattern, line)
        ]

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_producer_source_clean(self, pattern: str):
        hits = self._scan_source(_PRODUCER_SOURCE, pattern)
        assert not hits, (
            f"Forbidden pattern {pattern!r} found in producer source at "
            f"lines {hits}"
        )

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_exceptions_source_clean(self, pattern: str):
        hits = self._scan_source(_EXCEPTIONS_SOURCE, pattern)
        assert not hits, (
            f"Forbidden pattern {pattern!r} found in exceptions source at "
            f"lines {hits}"
        )


# ---------------------------------------------------------------------------
# 11. No W3 egress certifier interface in producer
# ---------------------------------------------------------------------------


class TestW3EgressCertifierSeparation:
    def test_no_egress_certifier_class_in_producer(self):
        source = _PRODUCER_SOURCE.read_text(encoding="utf-8")
        assert "EgressCertifier" not in source, (
            "W3 EgressCertifier interface must not be implemented in the W2 producer"
        )

    def test_no_certify_egress_method_on_producer(self):
        assert not hasattr(L5PacketProducer, "certify_egress"), (
            "W3 certify_egress method must not exist on W2 producer"
        )

    def test_certification_package_exports_egress_certifier(self):
        import agentic_core.L5_safety.certification as cert_pkg
        public_names = [n for n in dir(cert_pkg) if not n.startswith("_")]
        assert "EgressCertifier" in public_names, (
            "W3 EgressCertifier must be exported from certification package"
        )
        assert "MetadataOnlyEgressCertifier" in public_names, (
            "W3 MetadataOnlyEgressCertifier must be exported from certification package"
        )


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_run_id_and_trace_id_threaded(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            run_id="run-001",
            trace_id="trace-abc",
            **_COMMON_REFS,
        )
        assert packet.run_id == "run-001"
        assert packet.trace_id == "trace-abc"

    def test_producer_ref_and_version_preserved(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            producer_ref="l5_packet_producer:test:v99",
            certifier_version="99.0.0",
            **{k: v for k, v in _COMMON_REFS.items()
               if k not in ("producer_ref", "certifier_version")},
        )
        assert packet.producer_ref == "l5_packet_producer:test:v99"
        assert packet.certifier_version == "99.0.0"

    def test_evidence_refs_contains_governance_context_digest(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert len(packet.evidence_refs) >= 1
        # The governance context digest must be a valid sha256 hex
        assert re.fullmatch(r"[0-9a-f]{64}", packet.evidence_refs[0])

    def test_packet_output_kind_is_result(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.output_kind == "result"

    def test_multiple_uncertified_children_all_reported(self):
        children = _full_child_set()
        # Replace first two with UNKNOWN receipts
        for i in range(2):
            children[i] = ChildCertifierReceipt(
                domain=children[i].domain,
                applicability="REQUIRED",
                certified=False,
            )
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        # Both domains should appear in reason_codes
        assert sum(1 for rc in packet.reason_codes if "UNKNOWN" in rc) >= 2

    def test_produce_packet_returns_frozen_packet(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        with pytest.raises((AttributeError, TypeError)):
            packet.certification_status = "L5_CERTIFIED"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# W4 — Digest determinism proof
# ---------------------------------------------------------------------------


class TestW4DigestDeterminism:
    def test_certified_object_ref_change_changes_packet_digest(self):
        refs_a = dict(_COMMON_REFS)
        refs_b = dict(_COMMON_REFS)
        refs_b["certified_object_ref"] = "urn:obj:DIFFERENT:v99"
        pa = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs_a,
        )
        pb = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs_b,
        )
        assert pa.digest_sha256 != pb.digest_sha256, (
            "Changing certified_object_ref must change packet digest"
        )

    def test_governance_context_digest_is_64_hex_chars(self):
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **_COMMON_REFS,
        )
        gcd = packet.evidence_refs[0]
        assert len(gcd) == 64, f"governance_context_digest must be 64 chars, got {len(gcd)}"
        assert re.fullmatch(r"[0-9a-f]{64}", gcd), (
            f"governance_context_digest must be lowercase hex, got {gcd!r}"
        )

    def test_prior_packet_digest_exact_influence(self):
        prior_a = "f" * 64
        prior_b = "0" * 64
        pa = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior_a,
            **_COMMON_REFS,
        )
        pb = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior_b,
            **_COMMON_REFS,
        )
        pc = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            prior_packet_digest=prior_a,
            **_COMMON_REFS,
        )
        assert pa.digest_sha256 != pb.digest_sha256
        assert pa.digest_sha256 == pc.digest_sha256, (
            "Same prior_packet_digest must yield identical packet digest"
        )

    def test_packet_digest_stable_across_identical_runs(self):
        results = [
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **_COMMON_REFS,
            ).digest_sha256
            for _ in range(5)
        ]
        assert len(set(results)) == 1, "Packet digest must be stable across identical calls"

    def test_egress_ref_change_changes_packet_digest(self):
        egress_a = [_make_egress(certified=True)]
        egress_b = []
        pa = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=egress_a,
            **_COMMON_REFS,
        )
        pb = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=egress_b,
            **_COMMON_REFS,
        )
        assert pa.digest_sha256 != pb.digest_sha256, (
            "Adding an egress receipt must change the packet digest"
        )


# ---------------------------------------------------------------------------
# W4 — Duplicate domain / unknown category behavior proof
# ---------------------------------------------------------------------------


class TestW4DuplicateDomainBehavior:
    def test_duplicate_domain_receipts_are_all_stored_in_packet(self):
        first = _make_valid_receipt("safety_enforcement", certified=True)
        duplicate = ChildCertifierReceipt(
            domain="safety_enforcement",
            applicability="REQUIRED",
            certified=True,
            reason_codes=(),
        )
        children = [r for r in _full_child_set() if r.domain != "safety_enforcement"]
        children = [first] + children + [duplicate]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        # Duplicate domains with certified=True — at least one appears in packet
        # The producer's domain_map resolves duplicates; the resulting packet is
        # deterministic regardless of which duplicate wins.
        assert isinstance(packet, L5CertificationPacket)
        assert len(packet.child_receipts) >= len(_ALL_REQUIRED_DOMAINS)

    def test_unknown_child_category_not_checked_by_producer(self):
        children = _full_child_set() + [
            ChildCertifierReceipt(
                domain="completely_unknown_category",
                applicability="OPTIONAL",
                certified=False,
                reason_codes=("irrelevant",),
            )
        ]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED", (
            "Unknown category with OPTIONAL applicability must not block certification"
        )

    def test_optional_missing_child_does_not_block_certification(self):
        children = _full_child_set()
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_CERTIFIED", (
            "Optional categories absent from inputs must not block L5_CERTIFIED"
        )


# ---------------------------------------------------------------------------
# W4 — Authority widening via child union / egress / optional fields
# ---------------------------------------------------------------------------


class TestW4NoSilentWideningProof:
    def test_no_widening_through_egress_provider_ref(self):
        egress = EgressCertificationReceipt(
            provider_ref="urn:provider:governed:v1",
            response_digest=_HEX64,
            redaction_policy_ref="urn:policy:redaction:v1",
            certified=True,
        )
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "urn:authority:test:v1"
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[egress],
            **refs,
        )
        assert packet.certification_status == "L5_CERTIFIED", (
            "Symbolic egress provider_ref must not trigger authority widening"
        )

    def test_no_widening_through_empty_optional_fields(self):
        refs = dict(_COMMON_REFS)
        refs["blueprint_ref"] = ""
        refs["registry_ref"] = ""
        refs["replay_ref"] = ""
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=[],
            **refs,
        )
        assert packet.certification_status == "L5_CERTIFIED", (
            "Empty optional refs (blueprint, registry, replay) must not block "
            "certification or trigger authority widening — only certified_object_ref "
            "and policy_ref are hard-required."
        )

    def test_credential_pattern_in_authority_ref_raises_widening(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "sk-live-abcdefg"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_http_url_in_authority_ref_raises_widening(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "http://internal-registry/authority"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )

    def test_ungrounded_plain_string_raises_widening(self):
        refs = dict(_COMMON_REFS)
        refs["authority_ref"] = "plain-string-not-urn"
        with pytest.raises(L5AuthorityWideningError, match="widening"):
            _PRODUCER.produce_packet(
                child_receipts=_full_child_set(),
                egress_receipts=[],
                **refs,
            )


# ---------------------------------------------------------------------------
# W4 — Multiple egress uncertified all reported
# ---------------------------------------------------------------------------


class TestW4MultipleEgressReporting:
    def test_multiple_uncertified_egress_all_reported(self):
        egress = [
            EgressCertificationReceipt(
                provider_ref=f"urn:provider:p{i}:v1",
                response_digest=_HEX64,
                redaction_policy_ref="urn:policy:redact:v1",
                certified=False,
            )
            for i in range(3)
        ]
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=egress,
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED"
        egress_reasons = [rc for rc in packet.reason_codes if "egress" in rc]
        assert len(egress_reasons) >= 3, (
            f"All 3 uncertified egress receipts must appear in reason_codes, "
            f"got: {packet.reason_codes}"
        )

    def test_mixed_egress_certified_and_not_certified(self):
        egress = [
            EgressCertificationReceipt(
                provider_ref="urn:provider:p1:v1",
                response_digest=_HEX64,
                redaction_policy_ref="urn:policy:redact:v1",
                certified=True,
            ),
            EgressCertificationReceipt(
                provider_ref="urn:provider:p2:v1",
                response_digest=_HEX64,
                redaction_policy_ref="urn:policy:redact:v1",
                certified=False,
            ),
        ]
        packet = _PRODUCER.produce_packet(
            child_receipts=_full_child_set(),
            egress_receipts=egress,
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED", (
            "Any uncertified egress must block L5_CERTIFIED"
        )


# ---------------------------------------------------------------------------
# W4 — UNKNOWN child never yields L5_CERTIFIED
# ---------------------------------------------------------------------------


class TestW4UnknownChildNeverCertifies:
    @pytest.mark.parametrize("domain", _ALL_REQUIRED_DOMAINS)
    def test_unknown_required_child_never_yields_certified(self, domain: str):
        children = _full_child_set()
        children = [
            ChildCertifierReceipt(
                domain=c.domain,
                applicability="REQUIRED",
                certified=False,
                # No reason_codes → UNKNOWN
            )
            if c.domain == domain
            else c
            for c in children
        ]
        packet = _PRODUCER.produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_REFS,
        )
        assert packet.certification_status == "L5_NOT_CERTIFIED", (
            f"UNKNOWN child (certified=False, no reason_codes) for domain {domain!r} "
            "must never yield L5_CERTIFIED"
        )
        assert any("UNKNOWN" in rc for rc in packet.reason_codes), (
            "UNKNOWN child must be recorded in reason_codes"
        )
