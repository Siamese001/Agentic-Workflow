"""Unit tests for agentic_core.L2_execution.entry.packet_normalizer.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L2 entry
chokepoint. ``packet_normalizer`` is the single validate-and-normalize seam at
the L2 boundary: it performs NO execution and NO retrieval, only shape checks.
Pure-function coverage of ``normalize_to_request`` (every fail-closed rejection
branch + the happy path) and the ``NormalizationResult.ok`` property, driven by
dict inputs.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.entry.packet_normalizer import (
    NormalizationResult,
    normalize_to_request,
)
from agentic_core.L2_execution.types.l2_execution_request import (
    EntryRejection,
    EntryRejectionReason,
    ExecutionAuthorityContext,
    IssuerSurface,
    L2BoundaryAssertion,
    L2ExecutionRequest,
    SourcePacketType,
)

_REQUIRED_FIELDS = (
    "request_id",
    "run_id",
    "trace_root",
    "route_id",
    "route_contract_ref",
    "execution_form",
    "signed_packet_ref",
    "task_spec_ref",
    "capability_token_ref",
    "sandbox_envelope_ref",
    "side_effect_class",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "snapshot_manifest_ref",
    "expected_output_contract",
)


def _authority(**overrides: object) -> ExecutionAuthorityContext:
    base: dict[str, object] = dict(
        authority_context_id="ac-1",
        issuer_surface=IssuerSurface.L0,
        issuer_receipt_ref="rcpt-1",
        route_authority_ref="route-auth-1",
        capability_scope="cap-1",
        sandbox_scope="sbx-1",
        tenant_scope="tenant-1",
        acl_scope="acl-1",
        provider_lane="lane-1",
        filesystem_scope="fs-1",
        network_scope="net-1",
        credential_scope="cred-1",
    )
    base.update(overrides)
    return ExecutionAuthorityContext(**base)  # type: ignore[arg-type]


def _valid_packet(**overrides: object) -> dict[str, object]:
    pkt: dict[str, object] = {f: f"{f}-val" for f in _REQUIRED_FIELDS}
    pkt["source_packet_type"] = SourcePacketType.L0_SINGLE_STEP
    pkt["issuer_signature_hmac"] = "sig-abc"
    pkt.update(overrides)
    return pkt


class TestNormalizationResult:
    def test_ok_true_when_request_only(self) -> None:
        res = NormalizationResult(request=object(), rejection=None)  # type: ignore[arg-type]
        assert res.ok is True

    def test_ok_false_when_rejection_present(self) -> None:
        rej = EntryRejection(
            rejection_id="r", reason=EntryRejectionReason.UNSIGNED_PACKET, detail="d"
        )
        assert NormalizationResult(request=None, rejection=rej).ok is False

    def test_ok_false_when_both_none(self) -> None:
        assert NormalizationResult(request=None, rejection=None).ok is False


class TestHappyPath:
    def test_minimal_valid_packet_normalizes(self) -> None:
        res = normalize_to_request(raw_packet=_valid_packet(), authority_context=_authority())
        assert res.ok is True
        assert isinstance(res.request, L2ExecutionRequest)
        assert res.rejection is None
        assert res.request.request_id == "request_id-val"
        assert res.request.issuer_signature_hmac == "sig-abc"
        assert res.request.source_packet_type is SourcePacketType.L0_SINGLE_STEP

    def test_string_source_packet_type_coerced(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(source_packet_type="L3_CURRENT_STEP"),
            authority_context=_authority(issuer_surface=IssuerSurface.L3),
        )
        assert res.ok is True
        assert res.request.source_packet_type is SourcePacketType.L3_CURRENT_STEP

    def test_numeric_and_telemetry_defaults_and_coercion(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(
                max_attempts="3",
                timeout_ms="500",
                cost_budget="1.5",
                telemetry_keys=["a", "b"],
            ),
            authority_context=_authority(),
        )
        assert res.ok is True
        assert res.request.max_attempts == 3
        assert res.request.timeout_ms == 500
        assert res.request.cost_budget == 1.5
        assert res.request.telemetry_keys == ("a", "b")

    def test_telemetry_keys_non_sequence_falls_back_to_empty(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(telemetry_keys="not-a-list"),
            authority_context=_authority(),
        )
        assert res.ok is True
        assert res.request.telemetry_keys == ()


class TestBoundaryAndIssuerRejections:
    def test_unasserted_boundary_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(),
            authority_context=_authority(),
            boundary_assertion=L2BoundaryAssertion(no_c0_retrieval_asserted=False),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.BOUNDARY_VIOLATION
        assert "no_c0_retrieval_asserted" in res.rejection.boundary_violations

    def test_non_governed_issuer_rejected(self) -> None:
        # Bypass the IssuerSurface enum constraint with a stand-in that is not L0/L3.
        class _FakeSurface:
            value = "L5"

        res = normalize_to_request(
            raw_packet=_valid_packet(),
            authority_context=_authority(issuer_surface=_FakeSurface()),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.NON_GOVERNED_ISSUER


class TestAuthorityContextRejections:
    def test_prose_in_authority_field_rejected(self) -> None:
        long_prose = "this is a long human sentence that should never appear in a scope " * 2
        res = normalize_to_request(
            raw_packet=_valid_packet(),
            authority_context=_authority(capability_scope=long_prose),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY

    def test_newline_in_authority_field_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(),
            authority_context=_authority(network_scope="line1\nline2"),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY


class TestFieldAndSignatureRejections:
    @pytest.mark.parametrize("field_name", _REQUIRED_FIELDS)
    def test_missing_required_field_rejected(self, field_name: str) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(**{field_name: ""}),
            authority_context=_authority(),
        )
        assert res.ok is False
        # route_contract_ref empty trips the generic required-field guard first.
        assert res.rejection.reason is EntryRejectionReason.MISSING_REQUIRED_REF
        assert res.rejection.failed_field == field_name

    def test_unknown_source_packet_type_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(source_packet_type="NOT_A_REAL_TYPE"),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.MISSING_REQUIRED_REF
        assert res.rejection.failed_field == "source_packet_type"

    def test_empty_signature_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(issuer_signature_hmac=""),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.UNSIGNED_PACKET


class TestRouteDigestAndIntentRejections:
    def test_route_digest_mismatch_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(route_digest="abc"),
            authority_context=_authority(),
            expected_route_digest="xyz",
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.ROUTE_DIGEST_MISMATCH

    def test_route_digest_match_passes(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(route_digest="abc"),
            authority_context=_authority(),
            expected_route_digest="abc",
        )
        assert res.ok is True

    @pytest.mark.parametrize(
        "intent",
        [
            "retrieve_more_evidence",
            "select_route",
            "reroute",
            "expand_workflow",
            "approve_output",
            "ask_user_clarification",
        ],
    )
    def test_forbidden_declared_intent_rejected(self, intent: str) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(declared_intent=intent),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.ASKS_L2_TO_RETRIEVE_OR_ROUTE


class TestModeSpecificRejections:
    def test_grounded_missing_evidence_refs_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(grounded=True),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.GROUNDED_MISSING_EVIDENCE_CONTRACT

    def test_grounded_with_refs_passes(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(
                grounded=True,
                final_evidence_contract_ref="fec-1",
                prompt_envelope_ref="pe-1",
            ),
            authority_context=_authority(),
        )
        assert res.ok is True
        assert res.request.grounded is True

    def test_model_execution_missing_prompt_envelope_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(is_model_execution=True),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert (
            res.rejection.reason
            is EntryRejectionReason.MODEL_EXECUTION_MISSING_PROMPT_ENVELOPE
        )

    def test_ptc_missing_digest_rejected(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(is_ptc_execution=True),
            authority_context=_authority(),
        )
        assert res.ok is False
        assert res.rejection.reason is EntryRejectionReason.PTC_MISSING_DIGEST_OR_PROFILE

    def test_ptc_with_all_refs_passes(self) -> None:
        res = normalize_to_request(
            raw_packet=_valid_packet(
                is_ptc_execution=True,
                ptc_execution_profile_ref="ptc-1",
                script_digest="digest-1",
                sandbox_profile_ref="sbx-prof-1",
            ),
            authority_context=_authority(),
        )
        assert res.ok is True
        assert res.request.is_ptc_execution is True
        assert res.request.script_digest == "digest-1"
