"""Unit tests for agentic_core.L0_routing.intake.receipts.

Wave 6.1 (P2 untested-module coverage) — typed Intake receipt contracts
(01.1..01.5). Every receipt is a frozen dataclass carrying a
``deterministic_receipt_hash`` computed over STABLE fields only (volatile ids /
timestamps excluded). Pure / deterministic: ``_stable_hash``, each
``with_hash`` round-trip, the volatile-field-exclusion invariant, frozen
immutability, and the ``DUPLICATE_CLASSES`` label set.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.intake.receipts import (
    DUPLICATE_CLASSES,
    DuplicateRequestFingerprint,
    DuplicateSuppressionReceipt,
    IntakeManifestHash,
    MalformedEnvelopeReport,
    QuotaReceipt,
    RequestCorrelationReceipt,
    RequestSchemaValidationReceipt,
    SessionBindingReceipt,
    TenantBoundaryReceipt,
    TransportEnvelopeReceipt,
    _stable_hash,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode


def _transport(**overrides: object) -> TransportEnvelopeReceipt:
    base = dict(
        receipt_id="r1",
        raw_envelope_id="env-1",
        transport="api",
        channel="rest_v2",
        accepted_transport=True,
        frame_parse_status="ok",
        method_allowed=True,
        content_type_allowed=True,
        encoding_allowed=True,
        body_size_status="ok",
        attachment_inventory_status="ok",
        raw_capture_status="ok",
        transport_policy_ref="policy-1",
    )
    base.update(overrides)
    return TransportEnvelopeReceipt(**base)  # type: ignore[arg-type]


class TestStableHash:
    def test_is_sha256_hex(self) -> None:
        h = _stable_hash(["a", 1, True])
        assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self) -> None:
        assert _stable_hash(["x", {"k": 1}]) == _stable_hash(["x", {"k": 1}])

    def test_dict_key_order_irrelevant(self) -> None:
        assert _stable_hash([{"a": 1, "b": 2}]) == _stable_hash([{"b": 2, "a": 1}])

    def test_content_change_changes_hash(self) -> None:
        assert _stable_hash(["a"]) != _stable_hash(["b"])

    def test_non_string_coerced_via_default_str(self) -> None:
        # default=str means arbitrary objects do not raise.
        assert len(_stable_hash([object()])) == 64


class TestTransportEnvelopeReceipt:
    def test_defaults(self) -> None:
        r = _transport()
        assert r.rejection_reason_codes == ()
        assert r.warnings == ()
        assert r.deterministic_receipt_hash == ""

    def test_frozen(self) -> None:
        r = _transport()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.transport = "chat"  # type: ignore[misc]

    def test_with_hash_fills_hash(self) -> None:
        r = _transport().with_hash()
        assert len(r.deterministic_receipt_hash) == 64

    def test_with_hash_deterministic(self) -> None:
        assert (
            _transport().with_hash().deterministic_receipt_hash
            == _transport().with_hash().deterministic_receipt_hash
        )

    def test_raw_envelope_id_excluded_from_hash(self) -> None:
        # receipt_id and raw_envelope_id are volatile per-run — must not perturb hash.
        a = _transport(raw_envelope_id="env-A", receipt_id="rA").with_hash()
        b = _transport(raw_envelope_id="env-B", receipt_id="rB").with_hash()
        assert a.deterministic_receipt_hash == b.deterministic_receipt_hash

    def test_stable_field_change_changes_hash(self) -> None:
        a = _transport(transport="api").with_hash()
        b = _transport(transport="chat").with_hash()
        assert a.deterministic_receipt_hash != b.deterministic_receipt_hash

    def test_reason_codes_serialized_by_value(self) -> None:
        r = _transport(
            rejection_reason_codes=(IngressReasonCode.EMPTY_PAYLOAD,)
        ).with_hash()
        assert len(r.deterministic_receipt_hash) == 64


class TestOtherReceiptsWithHash:
    def test_malformed_report_round_trip(self) -> None:
        rep = MalformedEnvelopeReport(
            report_id="rep1",
            raw_envelope_id="env-1",
            malformed_class="bad_frame",
            decisive_reason=IngressReasonCode.MALFORMED_ENVELOPE,
            parse_error_summary="boom",
            recoverable_by_user=False,
            safe_user_visible_summary="could not parse",
        ).with_hash()
        assert len(rep.deterministic_report_hash) == 64
        assert rep.report_id == "rep1"

    def test_tenant_boundary_round_trip(self) -> None:
        r = TenantBoundaryReceipt(
            receipt_id="t1",
            tenant_id="acme",
            tenant_resolved=True,
            tenant_source="claim",
            tenant_allowed=True,
            tenant_conflict_detected=False,
        ).with_hash()
        assert len(r.deterministic_receipt_hash) == 64

    def test_session_binding_round_trip(self) -> None:
        r = SessionBindingReceipt(
            receipt_id="s1",
            session_id="sess-1",
            session_created_or_resumed="created",
            session_scope="full",
            session_valid=True,
        ).with_hash()
        assert len(r.deterministic_receipt_hash) == 64

    def test_quota_receipt_round_trip(self) -> None:
        r = QuotaReceipt(
            receipt_id="q1",
            tenant_id="acme",
            principal_id_hash="ph",
            session_id="sess",
            quota_policy_ref="qp",
            request_size_status="ok",
            attachment_count_status="ok",
            rate_limit_status="ok",
            daily_limit_status="ok",
            concurrent_request_status="ok",
            allowed_to_continue_intake=True,
        ).with_hash()
        assert len(r.deterministic_receipt_hash) == 64

    def test_duplicate_fingerprint_excludes_volatile_id(self) -> None:
        kwargs = dict(
            raw_payload_hash="rph",
            normalized_payload_pre_hash="npph",
            principal_id_hash="ph",
            tenant_id="acme",
            session_id="sess",
            transport="api",
            idempotency_key="idem",
            dedupe_window=300,
        )
        a = DuplicateRequestFingerprint(fingerprint_id="fA", **kwargs).with_hash()  # type: ignore[arg-type]
        b = DuplicateRequestFingerprint(fingerprint_id="fB", **kwargs).with_hash()  # type: ignore[arg-type]
        assert a.fingerprint_hash == b.fingerprint_hash

    def test_duplicate_suppression_round_trip(self) -> None:
        r = DuplicateSuppressionReceipt(
            receipt_id="d1",
            duplicate_detected=True,
            duplicate_class="double_submit",
        ).with_hash()
        assert r.suppress_or_continue == "continue"
        assert len(r.deterministic_receipt_hash) == 64

    def test_schema_validation_round_trip(self) -> None:
        r = RequestSchemaValidationReceipt(
            receipt_id="sv1",
            request_schema_ref="schema",
            schema_version="1",
            schema_valid=True,
        ).with_hash()
        assert len(r.deterministic_receipt_hash) == 64

    def test_correlation_receipt_excludes_volatile_fields(self) -> None:
        common = dict(
            receipt_id="c1",
            session_id="sess",
            tenant_id="acme",
            principal_id_hash="ph",
            correlation_source="intake_assigned",
        )
        a = RequestCorrelationReceipt(
            request_id="req-A", trace_root="tr-A", raw_envelope_id="env-A",
            normalized_payload_id="np-A", **common,  # type: ignore[arg-type]
        ).with_hash()
        b = RequestCorrelationReceipt(
            request_id="req-B", trace_root="tr-B", raw_envelope_id="env-B",
            normalized_payload_id="np-B", **common,  # type: ignore[arg-type]
        ).with_hash()
        assert a.deterministic_receipt_hash == b.deterministic_receipt_hash

    def test_intake_manifest_hash_round_trip(self) -> None:
        r = IntakeManifestHash(
            manifest_hash_id="m1",
            transport_receipt_hash="a",
            caller_scope_baseline_hash="b",
            quota_receipt_hash="c",
            schema_validation_receipt_hash="d",
            origin_label_manifest_hash="e",
            normalized_request_hash="f",
            replay_seed_hash="g",
        ).with_hash()
        assert len(r.intake_manifest_hash) == 64


class TestDuplicateClasses:
    def test_expected_members(self) -> None:
        assert DUPLICATE_CLASSES == frozenset(
            {
                "exact_replay_same_idempotency_key",
                "exact_replay_same_payload",
                "near_duplicate_transport_retry",
                "double_submit",
                "suspicious_replay",
                "not_duplicate",
            }
        )
