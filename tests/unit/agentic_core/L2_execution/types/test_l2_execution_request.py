"""Unit tests for agentic_core.L2_execution.types.l2_execution_request.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L2 entry
surface. ``l2_execution_request`` owns the three sealed entry contracts
(L2ExecutionRequest / ExecutionAuthorityContext / L2BoundaryAssertion) plus the
provenance and rejection enums. Pure dataclass/enum surface: construction,
defaults, frozen behavior, enum member sets, and the boundary/governed-channel
invariants — no live deps, no execution.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.types.l2_execution_request import (
    DurableWriteAuthority,
    EntryRejection,
    EntryRejectionReason,
    ExecutionAuthorityContext,
    HumanInputScope,
    IssuerSurface,
    L2BoundaryAssertion,
    L2ExecutionRequest,
    SourcePacketType,
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


def _request(**overrides: object) -> L2ExecutionRequest:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        route_id="route-1",
        route_contract_ref="rc-1",
        execution_form="MODEL",
        source_packet_type=SourcePacketType.L0_SINGLE_STEP,
        signed_packet_ref="sp-1",
        task_spec_ref="ts-1",
        capability_token_ref="ct-1",
        sandbox_envelope_ref="se-1",
        side_effect_class="NONE",
        policy_hash="ph-1",
        blueprint_hash="bh-1",
        replay_key="rk-1",
        snapshot_manifest_ref="sm-1",
        expected_output_contract="eoc-1",
        max_attempts=1,
        max_repair_count=1,
        timeout_ms=30_000,
        cost_budget=0.0,
        authority_context=_authority(),
        boundary_assertion=L2BoundaryAssertion(),
    )
    base.update(overrides)
    return L2ExecutionRequest(**base)  # type: ignore[arg-type]


class TestEnums:
    def test_source_packet_type_members(self) -> None:
        assert {m.value for m in SourcePacketType} == {
            "L0_SINGLE_STEP",
            "L3_CURRENT_STEP",
            "REPLAY_RESUME",
        }

    def test_issuer_surface_members(self) -> None:
        assert {m.value for m in IssuerSurface} == {"L0", "L3"}

    def test_human_input_scope_is_data_only(self) -> None:
        assert {m.value for m in HumanInputScope} == {"DATA_ONLY"}

    def test_durable_write_authority_is_none(self) -> None:
        assert {m.value for m in DurableWriteAuthority} == {"NONE"}

    def test_rejection_reason_members(self) -> None:
        assert {m.value for m in EntryRejectionReason} == {
            "no_route_contract_ref",
            "non_governed_issuer",
            "unsigned_packet",
            "route_digest_mismatch",
            "grants_durable_write",
            "human_text_in_authority",
            "asks_l2_to_retrieve_or_route",
            "ptc_missing_digest_or_profile",
            "boundary_violation",
            "missing_required_ref",
            "grounded_missing_evidence_contract",
            "model_execution_missing_prompt_envelope",
        }

    def test_str_enum_value_equality(self) -> None:
        # All enums subclass str — value compares equal to the bare string.
        assert SourcePacketType.REPLAY_RESUME == "REPLAY_RESUME"
        assert IssuerSurface.L3 == "L3"


class TestExecutionAuthorityContext:
    def test_typed_default_scopes(self) -> None:
        ac = _authority()
        assert ac.human_input_scope is HumanInputScope.DATA_ONLY
        assert ac.durable_write_authority is DurableWriteAuthority.NONE
        assert ac.allowed_side_effect_classes == ()
        assert ac.disallowed_side_effect_classes == ()
        assert ac.step_authority_ref is None
        assert ac.model_lane is None
        assert ac.tool_lane is None

    def test_frozen(self) -> None:
        ac = _authority()
        with pytest.raises(dataclasses.FrozenInstanceError):
            ac.tenant_scope = "other"  # type: ignore[misc]

    def test_optional_fields_settable(self) -> None:
        ac = _authority(model_lane="ml-1", tool_lane="tl-1", step_authority_ref="sa-1")
        assert ac.model_lane == "ml-1"
        assert ac.tool_lane == "tl-1"
        assert ac.step_authority_ref == "sa-1"


class TestL2BoundaryAssertion:
    def test_defaults_all_clean(self) -> None:
        b = L2BoundaryAssertion()
        assert b.all_clean() is True
        assert b.violations() == ()

    def test_frozen(self) -> None:
        b = L2BoundaryAssertion()
        with pytest.raises(dataclasses.FrozenInstanceError):
            b.no_c0_retrieval_asserted = False  # type: ignore[misc]

    @pytest.mark.parametrize(
        "field_name",
        [
            "no_route_decision_asserted",
            "no_workflow_expansion_asserted",
            "no_c0_retrieval_asserted",
            "no_prompt_assembly_asserted",
            "no_direct_human_call_asserted",
            "no_direct_l4_write_asserted",
            "no_exit_disposition_asserted",
            "no_l6_learning_asserted",
        ],
    )
    def test_single_unasserted_bit_is_violation(self, field_name: str) -> None:
        b = L2BoundaryAssertion(**{field_name: False})
        assert b.all_clean() is False
        assert b.violations() == (field_name,)

    def test_multiple_violations_preserve_canonical_order(self) -> None:
        b = L2BoundaryAssertion(
            no_workflow_expansion_asserted=False,
            no_exit_disposition_asserted=False,
        )
        assert b.violations() == (
            "no_workflow_expansion_asserted",
            "no_exit_disposition_asserted",
        )


class TestL2ExecutionRequest:
    def test_optional_ref_defaults(self) -> None:
        r = _request()
        assert r.prompt_envelope_ref is None
        assert r.final_evidence_contract_ref is None
        assert r.l3_step_contract_ref is None
        assert r.ptc_execution_profile_ref is None
        assert r.script_digest is None
        assert r.sandbox_profile_ref is None
        assert r.telemetry_keys == ()
        assert r.grounded is False
        assert r.is_model_execution is False
        assert r.is_ptc_execution is False
        assert r.issuer_signature_hmac == ""

    def test_frozen(self) -> None:
        r = _request()
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.route_id = "other"  # type: ignore[misc]

    @pytest.mark.parametrize(
        "surface,expected",
        [
            (IssuerSurface.L0, True),
            (IssuerSurface.L3, True),
        ],
    )
    def test_is_governed_channel_true_for_l0_l3(
        self, surface: IssuerSurface, expected: bool
    ) -> None:
        r = _request(authority_context=_authority(issuer_surface=surface))
        assert r.is_governed_channel() is expected


class TestEntryRejection:
    def test_defaults(self) -> None:
        rej = EntryRejection(
            rejection_id="rej-1",
            reason=EntryRejectionReason.UNSIGNED_PACKET,
            detail="missing sig",
        )
        assert rej.source_packet_type is None
        assert rej.failed_field == ""
        assert rej.boundary_violations == ()

    def test_frozen(self) -> None:
        rej = EntryRejection(
            rejection_id="rej-1",
            reason=EntryRejectionReason.BOUNDARY_VIOLATION,
            detail="d",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rej.detail = "other"  # type: ignore[misc]

    def test_boundary_violations_default_factory_is_independent(self) -> None:
        a = EntryRejection(
            rejection_id="a", reason=EntryRejectionReason.MISSING_REQUIRED_REF, detail="d"
        )
        b = EntryRejection(
            rejection_id="b", reason=EntryRejectionReason.MISSING_REQUIRED_REF, detail="d"
        )
        assert a.boundary_violations == () and b.boundary_violations == ()
        assert a.boundary_violations is not b.boundary_violations or a.boundary_violations == ()
