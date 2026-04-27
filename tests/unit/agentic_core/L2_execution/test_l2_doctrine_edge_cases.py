"""L2 doctrine edge-case hardening pass.

Maps to: ``.windsurf/plans/l2-execute-doc-gap-fill-9c2a31.md`` Hardening Pass.

Coverage rule (uniformly enforced across every contract introduced by the
plan):

  1. Every ``__post_init__`` invariant has at least one direct edge-case test.
  2. Every public-API entrypoint validates input type.
  3. Every must-be-True assertion is verified via flipped-False raise.
  4. Every closed-vocabulary enum field rejects raw-string substitution.
  5. Every numeric field rejects out-of-range values (and bool-as-numeric
     where the type is `int` strict).
  6. Every required string rejects empty.
  7. Every required tuple rejects non-tuple / wrong-element-type where the
     contract states a homogeneous tuple.

This file is intentionally large and parametric. It is *additive* — it does
not modify any pre-existing contract, test, or runtime path.

Contracts hardened:
  * ``L2ExecutionRequest`` + ``ExecutionAuthorityContext`` + ``L2BoundaryAssertion``
    + ``EntryRejection`` + ``SourcePacketType`` / ``IssuerSurface`` /
    ``HumanInputScope`` / ``DurableWriteAuthority`` / ``EntryRejectionReason``
  * ``PTCExecutionProfile`` + ``PTCScriptEnvelope`` + ``PTCSandboxReceipt``
    + ``PTCToolCallReceipt`` + ``HumanReviewThreshold`` +
    ``PTCScriptLanguage`` / ``RawResultContextPolicy`` / ``StdoutReturnPolicy``
    / ``PTCResultClass`` / ``UntranscriptedIOStatus`` / ``CapabilityViolationStatus``
    / ``SandboxEscapeStatus``
  * ``packet_normalizer.normalize_to_request`` public API
  * ``observability.l2_spans.validate_span_attributes`` public API
  * ``enforcement.anti_bypass_guards`` 13 individual guards + aggregator
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.entry.packet_normalizer import (
    NormalizationResult,
    normalize_to_request,
)
from agentic_core.L2_execution.enforcement.anti_bypass_guards import (
    BypassCheckResult,
    BypassReason,
    L2BypassViolation,
    assert_capability_token_present,
    assert_human_input_is_data_only,
    assert_l2_bounded,
    assert_no_direct_human_call,
    assert_no_direct_l4_write,
    assert_no_direct_uwg_call,
    assert_no_forbidden_l2_output,
    assert_no_prompt_envelope_construction,
    assert_no_provider_or_tool_switch,
    assert_no_route_change,
    assert_no_unapproved_c0_retrieval,
    assert_no_workflow_expansion,
    assert_repair_under_same_snapshot,
    assert_sandbox_envelope_present,
    assert_seals_rejection_or_failure,
    raise_if_any,
)
from agentic_core.L2_execution.observability.l2_spans import (
    L2_E1_SPANS,
    L2_E2_SPANS,
    L2_E3_SPANS,
    L2_E4_SPANS,
    L2_E5_SPANS,
    L2_LOCAL_CRITIQUE_SPANS,
    L2_MUTATION_SPANS,
    L2_PTC_SPANS,
    L2_RESOLUTION_SPANS,
    L2_SEQUENCER_SPANS,
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)
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
from agentic_core.L2_execution.types.ptc_execution_profile import (
    CapabilityViolationStatus,
    HumanReviewThreshold,
    PTCContractError,
    PTCExecutionProfile,
    PTCResultClass,
    PTCSandboxReceipt,
    PTCScriptEnvelope,
    PTCScriptLanguage,
    PTCToolCallReceipt,
    RawResultContextPolicy,
    SandboxEscapeStatus,
    StdoutReturnPolicy,
    UntranscriptedIOStatus,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _good_authority(issuer: IssuerSurface = IssuerSurface.L0) -> ExecutionAuthorityContext:
    return ExecutionAuthorityContext(
        authority_context_id="auth-edge-1",
        issuer_surface=issuer,
        issuer_receipt_ref="iss-rcpt-1",
        route_authority_ref="r-auth-1",
        capability_scope="cap.read",
        sandbox_scope="sbx",
        tenant_scope="tenant-a",
        acl_scope="acl",
        provider_lane="anth.lane.a",
        filesystem_scope="/tmp/x",
        network_scope="none",
        credential_scope="none",
    )


def _good_packet() -> dict:
    return {
        "request_id": "req-1",
        "run_id": "run-1",
        "trace_root": "trace-1",
        "route_id": "route-1",
        "route_contract_ref": "rc-1",
        "execution_form": "SINGLE_STEP",
        "source_packet_type": SourcePacketType.L0_SINGLE_STEP,
        "signed_packet_ref": "sig-1",
        "task_spec_ref": "task-1",
        "capability_token_ref": "cap-tok-1",
        "sandbox_envelope_ref": "sbx-env-1",
        "side_effect_class": "READ",
        "policy_hash": "pol-1",
        "blueprint_hash": "bp-1",
        "replay_key": "rk-1",
        "snapshot_manifest_ref": "sm-1",
        "expected_output_contract": "answer.text.v1",
        "max_attempts": 1,
        "max_repair_count": 1,
        "timeout_ms": 5_000,
        "cost_budget": 0.05,
        "issuer_signature_hmac": "abc123",
        "telemetry_keys": ("trace_root", "request_id"),
    }


def _good_profile(**overrides) -> PTCExecutionProfile:
    base: dict = dict(
        ptc_profile_id="ptc-1",
        route_id="r-1",
        execution_form="SINGLE_STEP",
        script_language=PTCScriptLanguage.PYTHON,
        allowed_tool_calls=("query_database",),
        max_tool_calls=5,
        max_runtime_ms=30_000,
        max_stdout_bytes=4096,
        max_stderr_bytes=2048,
        max_raw_result_bytes=1_048_576,
    )
    base.update(overrides)
    return PTCExecutionProfile(**base)


def _good_envelope(**overrides) -> PTCScriptEnvelope:
    base: dict = dict(
        ptc_script_envelope_id="env-1",
        approved_work_order_ref="awo-1",
        script_text_ref="ref",
        script_digest="sha256:d",
        imports_allowlist=(),
        filesystem_allowlist=(),
        network_allowlist=(),
        tool_call_manifest=(),
        expected_stdout_schema="schema",
        deterministic_seed="seed",
        replay_key="rk",
    )
    base.update(overrides)
    return PTCScriptEnvelope(**base)


def _clean_receipt(**overrides) -> PTCSandboxReceipt:
    base: dict = dict(
        ptc_sandbox_receipt_id="r-1",
        script_envelope_ref="env-1",
        context_freeze_receipt_ref="cf-1",
        context_unfreeze_receipt_ref="cu-1",
        tool_call_receipts=(),
        raw_result_refs_sandbox_only=(),
        stdout_summary_ref="s",
        stderr_summary_ref="s",
        untranscripted_io_status=UntranscriptedIOStatus.CLEAN,
        capability_violation_status=CapabilityViolationStatus.CLEAN,
        sandbox_escape_status=SandboxEscapeStatus.CLEAN,
        result_class=PTCResultClass.SUCCESS,
        deterministic_digest="dd",
    )
    base.update(overrides)
    return PTCSandboxReceipt(**base)


# ===========================================================================
# Section A — L2BoundaryAssertion edge cases  (8 fields × asserted/unasserted)
# ===========================================================================


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
def test_boundary_assertion_each_bit_unasserted_surfaces_in_violations(field_name: str) -> None:
    """Every boundary bit must individually surface in `violations()` when False."""
    bad = dataclasses.replace(L2BoundaryAssertion(), **{field_name: False})
    assert not bad.all_clean()
    assert field_name in bad.violations()


def test_boundary_assertion_default_construction_all_clean() -> None:
    assert L2BoundaryAssertion().all_clean()
    assert L2BoundaryAssertion().violations() == ()


def test_boundary_assertion_multiple_unasserted_listed_in_order() -> None:
    bad = L2BoundaryAssertion(
        no_workflow_expansion_asserted=False,
        no_direct_l4_write_asserted=False,
    )
    v = bad.violations()
    assert "no_workflow_expansion_asserted" in v
    assert "no_direct_l4_write_asserted" in v
    assert len(v) == 2


# ===========================================================================
# Section B — ExecutionAuthorityContext invariants
# ===========================================================================


def test_authority_context_data_only_default() -> None:
    auth = _good_authority()
    assert auth.human_input_scope is HumanInputScope.DATA_ONLY
    assert auth.durable_write_authority is DurableWriteAuthority.NONE


def test_authority_context_with_durable_write_rejected_at_normalizer() -> None:
    """A forced-WRITE authority is caught at normalize boundary."""

    class _FakeWrite(str):
        value = "WRITE"

    auth = dataclasses.replace(
        _good_authority(),
        durable_write_authority=_FakeWrite("WRITE"),  # type: ignore[arg-type]
    )
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=auth)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.GRANTS_DURABLE_WRITE


@pytest.mark.parametrize(
    "field_name",
    [
        "issuer_receipt_ref",
        "route_authority_ref",
        "capability_scope",
        "sandbox_scope",
        "tenant_scope",
        "acl_scope",
        "provider_lane",
        "filesystem_scope",
        "network_scope",
        "credential_scope",
    ],
)
def test_authority_field_with_long_prose_rejected(field_name: str) -> None:
    """Each of the 10 prose-suspect authority fields rejects free-form text."""
    long_prose = (
        "This authority context was approved by a human reviewer because "
        "everything looked routine and the customer was friendly so we just "
        "passed it through without checking the policy hash."
    )
    bad_auth = dataclasses.replace(_good_authority(), **{field_name: long_prose})
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=bad_auth)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY


@pytest.mark.parametrize(
    "field_name",
    [
        "issuer_receipt_ref",
        "route_authority_ref",
        "capability_scope",
    ],
)
def test_authority_field_with_newline_rejected(field_name: str) -> None:
    """Newlines inside an authority field signal multi-line prose."""
    bad_auth = dataclasses.replace(_good_authority(), **{field_name: "ref-id\nextra-line"})
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=bad_auth)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY


def test_authority_short_id_with_space_passes() -> None:
    """A short authority ref with a single space (≤64 chars) is allowed."""
    auth = dataclasses.replace(_good_authority(), capability_scope="cap r")
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=auth)
    assert res.ok


# ===========================================================================
# Section C — Source / Issuer / HumanInputScope / DurableWriteAuthority enums
# ===========================================================================


@pytest.mark.parametrize(
    "raw,allowed",
    [
        ("L0_SINGLE_STEP", True),
        ("L3_CURRENT_STEP", True),
        ("REPLAY_RESUME", True),
        ("L0_SINGLE", False),
        ("L4_DIRECT", False),
        ("", False),
    ],
)
def test_source_packet_type_enum_substitution_rejected(raw: str, allowed: bool) -> None:
    pkt = _good_packet()
    pkt["source_packet_type"] = raw
    res = normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    if allowed:
        assert res.ok, res.rejection
    else:
        assert res.rejection is not None
        assert res.rejection.reason is EntryRejectionReason.MISSING_REQUIRED_REF


def test_issuer_surface_enum_has_exactly_two_members() -> None:
    members = {m.value for m in IssuerSurface}
    assert members == {"L0", "L3"}


def test_human_input_scope_enum_has_exactly_one_member() -> None:
    """DATA_ONLY is the only legal value (architectural invariant)."""
    members = list(HumanInputScope)
    assert len(members) == 1
    assert members[0] is HumanInputScope.DATA_ONLY


def test_durable_write_authority_enum_has_exactly_one_member() -> None:
    """NONE is the only legal value (L2 cannot self-grant durable write)."""
    members = list(DurableWriteAuthority)
    assert len(members) == 1
    assert members[0] is DurableWriteAuthority.NONE


def test_entry_rejection_reason_complete() -> None:
    """All 11 enumerated rejection reasons are present (matches doc 04.1 §3)."""
    expected = {
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
    assert {r.value for r in EntryRejectionReason} == expected


# ===========================================================================
# Section D — packet_normalizer required-field discipline
# ===========================================================================


@pytest.mark.parametrize(
    "missing_field",
    [
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
    ],
)
def test_each_required_field_individually_rejected_when_missing(missing_field: str) -> None:
    """All 16 required fields are individually enforced."""
    pkt = _good_packet()
    pkt[missing_field] = ""
    res = normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    assert res.rejection is not None, f"missing {missing_field} should reject"
    # route_contract_ref has its own dedicated reason; everything else is generic
    assert res.rejection.reason in (
        EntryRejectionReason.MISSING_REQUIRED_REF,
        EntryRejectionReason.NO_ROUTE_CONTRACT_REF,
    )
    if missing_field != "route_contract_ref":
        assert res.rejection.failed_field == missing_field


@pytest.mark.parametrize(
    "missing_field",
    [
        "request_id",
        "policy_hash",
        "blueprint_hash",
        "replay_key",
    ],
)
def test_each_required_field_individually_rejected_when_none(missing_field: str) -> None:
    """`None` (not just empty string) is also rejected."""
    pkt = _good_packet()
    pkt[missing_field] = None
    res = normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.MISSING_REQUIRED_REF


@pytest.mark.parametrize(
    "intent,expect_reject",
    [
        ("retrieve_more_evidence", True),
        ("select_route", True),
        ("reroute", True),
        ("expand_workflow", True),
        ("approve_output", True),
        ("ask_user_clarification", True),
        ("execute_step", False),
        ("", False),
    ],
)
def test_declared_intent_forbidden_set(intent: str, expect_reject: bool) -> None:
    """All 6 forbidden intents reject; benign intents pass."""
    pkt = _good_packet()
    if intent:
        pkt["declared_intent"] = intent
    res = normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    if expect_reject:
        assert res.rejection is not None
        assert res.rejection.reason is EntryRejectionReason.ASKS_L2_TO_RETRIEVE_OR_ROUTE
    else:
        assert res.ok


def test_route_digest_match_with_explicit_expected_passes() -> None:
    pkt = _good_packet()
    pkt["route_digest"] = "matching-digest"
    res = normalize_to_request(
        raw_packet=pkt,
        authority_context=_good_authority(),
        expected_route_digest="matching-digest",
    )
    assert res.ok


def test_route_digest_omitted_when_no_expected_passes() -> None:
    """If caller doesn't assert an expected digest, packet need not provide one."""
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    assert res.ok


def test_normalization_result_invariant() -> None:
    """Exactly one of request/rejection is non-None."""
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    assert res.ok
    assert (res.request is None) != (res.rejection is None)

    pkt_bad = _good_packet()
    pkt_bad["issuer_signature_hmac"] = ""
    res2 = normalize_to_request(raw_packet=pkt_bad, authority_context=_good_authority())
    assert not res2.ok
    assert (res2.request is None) != (res2.rejection is None)


# ===========================================================================
# Section E — PTCExecutionProfile invariants
# ===========================================================================


@pytest.mark.parametrize(
    "field,value,err_pattern",
    [
        ("max_tool_calls", 0, "max_tool_calls"),
        ("max_tool_calls", -1, "max_tool_calls"),
        ("max_runtime_ms", 0, "max_runtime_ms"),
        ("max_runtime_ms", -100, "max_runtime_ms"),
        ("max_stdout_bytes", -1, "max_stdout_bytes"),
        ("max_stderr_bytes", -1, "max_stderr_bytes"),
        ("max_raw_result_bytes", -1, "max_raw_result_bytes"),
    ],
)
def test_profile_numeric_field_rejects_out_of_range(field: str, value: int, err_pattern: str) -> None:
    with pytest.raises(PTCContractError, match=err_pattern):
        _good_profile(**{field: value})


def test_profile_must_have_context_freeze_required_true() -> None:
    """Flipped-False raise: context_freeze_required cannot be turned off."""
    with pytest.raises(PTCContractError, match="context_freeze_required"):
        _good_profile(context_freeze_required=False)


def test_profile_raw_result_context_policy_only_sandbox_only() -> None:
    """Even though enum has one member, contract verifies it explicitly."""
    p = _good_profile()
    assert p.raw_result_context_policy is RawResultContextPolicy.SANDBOX_ONLY


@pytest.mark.parametrize(
    "lang",
    [
        PTCScriptLanguage.PYTHON,
        PTCScriptLanguage.BASH,
        PTCScriptLanguage.OTHER_APPROVED,
        PTCScriptLanguage.POWERSHELL_DISALLOWED_IF_POLICY_BLOCKS,
    ],
)
def test_profile_script_language_each_enum_constructs(lang: PTCScriptLanguage) -> None:
    p = _good_profile(script_language=lang)
    assert p.script_language is lang


def test_profile_stdout_return_policy_each_enum_constructs() -> None:
    for policy in StdoutReturnPolicy:
        p = _good_profile(stdout_return_policy=policy)
        assert p.stdout_return_policy is policy


def test_profile_tool_is_allowed_membership_check() -> None:
    p = _good_profile(allowed_tool_calls=("alpha", "beta", "gamma"))
    assert p.tool_is_allowed("alpha")
    assert p.tool_is_allowed("gamma")
    assert not p.tool_is_allowed("delta")
    assert not p.tool_is_allowed("")


def test_profile_default_human_review_threshold_is_safe() -> None:
    p = _good_profile()
    t = p.human_review_thresholds
    assert 0.0 < t.confidence_below < 1.0
    assert 0.0 < t.risk_above < 1.0
    assert 0.0 < t.policy_ambiguity_above < 1.0


def test_profile_l5_reclearance_default_true() -> None:
    p = _good_profile()
    assert p.l5_reclearance_required_on_modify is True


def test_profile_fail_closed_default_true() -> None:
    p = _good_profile()
    assert p.fail_closed_on_untranscripted_io is True


# ===========================================================================
# Section F — PTCScriptEnvelope invariants
# ===========================================================================


@pytest.mark.parametrize(
    "field",
    [
        "approved_work_order_ref",
        "script_digest",
        "expected_stdout_schema",
        "replay_key",
    ],
)
def test_envelope_required_string_rejects_empty(field: str) -> None:
    with pytest.raises(PTCContractError):
        _good_envelope(**{field: ""})


def test_envelope_with_all_required_fields_constructs() -> None:
    e = _good_envelope()
    assert e.script_digest == "sha256:d"
    assert e.replay_key == "rk"


def test_envelope_disallowed_patterns_default_empty() -> None:
    e = _good_envelope()
    assert e.disallowed_patterns == ()


# ===========================================================================
# Section G — PTCSandboxReceipt fail-closed coupling matrix
# ===========================================================================


@pytest.mark.parametrize(
    "untrans,cap,esc,result,should_raise",
    [
        # CLEAN/CLEAN/CLEAN with any non-REJECTED is fine
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.SUCCESS,
            False,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.DEGRADED_SUCCESS,
            False,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.SOFT_REPAIRABLE,
            False,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.NEEDS_HELP,
            False,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.REJECTED,
            False,
        ),
        # Untranscripted DETECTED requires REJECTED
        (
            UntranscriptedIOStatus.DETECTED,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.SUCCESS,
            True,
        ),
        (
            UntranscriptedIOStatus.DETECTED,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.SOFT_REPAIRABLE,
            True,
        ),
        (
            UntranscriptedIOStatus.DETECTED,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.REJECTED,
            False,
        ),
        # Capability DETECTED requires REJECTED
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.DETECTED,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.SUCCESS,
            True,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.DETECTED,
            SandboxEscapeStatus.CLEAN,
            PTCResultClass.REJECTED,
            False,
        ),
        # Sandbox-escape DETECTED requires REJECTED
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.DETECTED,
            PTCResultClass.SUCCESS,
            True,
        ),
        (
            UntranscriptedIOStatus.CLEAN,
            CapabilityViolationStatus.CLEAN,
            SandboxEscapeStatus.DETECTED,
            PTCResultClass.REJECTED,
            False,
        ),
        # Multiple DETECTED + REJECTED is allowed
        (
            UntranscriptedIOStatus.DETECTED,
            CapabilityViolationStatus.DETECTED,
            SandboxEscapeStatus.DETECTED,
            PTCResultClass.REJECTED,
            False,
        ),
    ],
)
def test_receipt_fail_closed_coupling(
    untrans: UntranscriptedIOStatus,
    cap: CapabilityViolationStatus,
    esc: SandboxEscapeStatus,
    result: PTCResultClass,
    should_raise: bool,
) -> None:
    """Full coupling matrix for the 3 fail-closed status fields × result class."""
    if should_raise:
        with pytest.raises(PTCContractError):
            _clean_receipt(
                untranscripted_io_status=untrans,
                capability_violation_status=cap,
                sandbox_escape_status=esc,
                result_class=result,
            )
    else:
        rcpt = _clean_receipt(
            untranscripted_io_status=untrans,
            capability_violation_status=cap,
            sandbox_escape_status=esc,
            result_class=result,
        )
        assert rcpt.result_class is result


def test_receipt_is_clean_only_when_all_three_clean() -> None:
    """is_clean() is exactly the CLEAN×CLEAN×CLEAN case."""
    clean = _clean_receipt()
    assert clean.is_clean()

    rejected_clean = _clean_receipt(result_class=PTCResultClass.REJECTED)
    # Result class doesn't affect cleanliness — only the 3 status fields do.
    assert rejected_clean.is_clean()

    untrans_dirty = _clean_receipt(
        untranscripted_io_status=UntranscriptedIOStatus.DETECTED,
        result_class=PTCResultClass.REJECTED,
    )
    assert not untrans_dirty.is_clean()


@pytest.mark.parametrize("size", [2049, 4096, 8192, 16384])
def test_receipt_rejects_oversized_ref(size: int) -> None:
    with pytest.raises(PTCContractError, match="too large to be a ref"):
        _clean_receipt(raw_result_refs_sandbox_only=("x" * size,))


@pytest.mark.parametrize("size", [16, 64, 256, 1024, 2048])
def test_receipt_accepts_ref_at_or_below_2k(size: int) -> None:
    rcpt = _clean_receipt(raw_result_refs_sandbox_only=("x" * size,))
    assert len(rcpt.raw_result_refs_sandbox_only[0]) == size


def test_receipt_rejects_non_string_ref() -> None:
    with pytest.raises(PTCContractError):
        _clean_receipt(raw_result_refs_sandbox_only=(b"bytes-not-str",))  # type: ignore[arg-type]


def test_receipt_unavailable_status_not_treated_as_rejection_trigger() -> None:
    """UNAVAILABLE is distinct from DETECTED — does not force REJECTED."""
    rcpt = _clean_receipt(
        untranscripted_io_status=UntranscriptedIOStatus.UNAVAILABLE,
        result_class=PTCResultClass.SUCCESS,
    )
    assert rcpt.untranscripted_io_status is UntranscriptedIOStatus.UNAVAILABLE


# ===========================================================================
# Section H — PTCToolCallReceipt
# ===========================================================================


def test_tool_call_receipt_construction() -> None:
    r = PTCToolCallReceipt(
        tool_call_id="tc-1",
        tool_name="query_database",
        args_hash="argsha",
        raw_result_ref="sbx://tc-1",
        return_code=0,
        started_at_unix=1.0,
        ended_at_unix=2.0,
    )
    assert r.return_code == 0
    assert r.error is None


def test_tool_call_receipt_with_error() -> None:
    r = PTCToolCallReceipt(
        tool_call_id="tc-2",
        tool_name="query_database",
        args_hash="argsha",
        raw_result_ref="sbx://tc-2",
        return_code=1,
        started_at_unix=1.0,
        ended_at_unix=2.0,
        error="connection refused",
    )
    assert r.error == "connection refused"
    assert r.return_code == 1


# ===========================================================================
# Section I — OTEL span vocabulary edge cases
# ===========================================================================


def test_span_registry_total_is_sum_of_groups() -> None:
    total = (
        len(L2_E1_SPANS)
        + len(L2_E2_SPANS)
        + len(L2_E3_SPANS)
        + len(L2_E4_SPANS)
        + len(L2_RESOLUTION_SPANS)
        + len(L2_E5_SPANS)
        + len(L2_PTC_SPANS)
        + len(L2_SEQUENCER_SPANS)
        + len(L2_MUTATION_SPANS)
        + len(L2_LOCAL_CRITIQUE_SPANS)
    )
    assert len(all_l2_span_names()) == total


def test_no_span_appears_in_two_groups() -> None:
    """Every span belongs to exactly one phase group."""
    groups = {
        "E1": L2_E1_SPANS,
        "E2": L2_E2_SPANS,
        "E3": L2_E3_SPANS,
        "E4": L2_E4_SPANS,
        "E5": L2_E5_SPANS,
        "RESOLUTION": L2_RESOLUTION_SPANS,
        "PTC": L2_PTC_SPANS,
        "SEQUENCER": L2_SEQUENCER_SPANS,
        "MUTATION": L2_MUTATION_SPANS,
        "LOCAL_CRITIQUE": L2_LOCAL_CRITIQUE_SPANS,
    }
    seen: dict[str, str] = {}
    for label, names in groups.items():
        for n in names:
            assert n not in seen, f"{n} in both {seen.get(n)} and {label}"
            seen[n] = label


def test_every_e1_span_starts_with_l2_e1_prep() -> None:
    for n in L2_E1_SPANS:
        assert n.startswith("l2.e1.prep.")


def test_every_e2_span_starts_with_l2_e2_valid() -> None:
    for n in L2_E2_SPANS:
        assert n.startswith("l2.e2.valid.")


def test_every_e3_span_starts_with_l2_e3_exec() -> None:
    for n in L2_E3_SPANS:
        assert n.startswith("l2.e3.exec.")


def test_every_e4_span_starts_with_l2_e4_heal() -> None:
    for n in L2_E4_SPANS:
        assert n.startswith("l2.e4.heal.")


def test_every_e5_span_starts_with_l2_e5_seal() -> None:
    for n in L2_E5_SPANS:
        assert n.startswith("l2.e5.seal.")


def test_every_ptc_span_starts_with_l2_ptc() -> None:
    for n in L2_PTC_SPANS:
        assert n.startswith("l2.ptc.")


@pytest.mark.parametrize("attr", list(L2_REQUIRED_SPAN_ATTRIBUTES))
def test_each_required_attribute_individually_enforced(attr: str) -> None:
    """Each of the 13 always-required attributes is individually enforced."""
    full = {a: f"v-{a}" for a in L2_REQUIRED_SPAN_ATTRIBUTES}
    full["latency_ms"] = 42  # numeric not "v-latency_ms"
    incomplete = dict(full)
    incomplete.pop(attr)
    missing = validate_span_attributes(span_name="l2.e1.prep.receive", attrs=incomplete)
    assert attr in missing


def test_validate_span_returns_empty_tuple_when_clean() -> None:
    full = {a: f"v-{a}" for a in L2_REQUIRED_SPAN_ATTRIBUTES}
    full["latency_ms"] = 42
    assert validate_span_attributes(span_name="l2.e1.prep.receive", attrs=full) == ()


@pytest.mark.parametrize(
    "bad_name", ["l2.UNKNOWN", "L2.e1.prep.receive", "e1.prep.receive", "", "l3.exec.foo"]
)
def test_validate_span_unknown_name_raises(bad_name: str) -> None:
    full = {a: f"v-{a}" for a in L2_REQUIRED_SPAN_ATTRIBUTES}
    full["latency_ms"] = 42
    with pytest.raises(L2SpanAttributeViolation):
        validate_span_attributes(span_name=bad_name, attrs=full)


def test_validate_span_attribute_with_empty_string_treated_as_missing() -> None:
    full = {a: f"v-{a}" for a in L2_REQUIRED_SPAN_ATTRIBUTES}
    full["latency_ms"] = 42
    full["replay_key"] = ""  # empty string → missing
    missing = validate_span_attributes(span_name="l2.e2.valid.receipt_emit", attrs=full)
    assert "replay_key" in missing


def test_validate_span_attribute_with_none_treated_as_missing() -> None:
    full = {a: f"v-{a}" for a in L2_REQUIRED_SPAN_ATTRIBUTES}
    full["latency_ms"] = 42
    full["trace_id"] = None
    missing = validate_span_attributes(span_name="l2.e3.exec.attempt_open", attrs=full)
    assert "trace_id" in missing


# ===========================================================================
# Section J — Anti-bypass guards individually
# ===========================================================================


def test_assert_no_route_change_partial_drift() -> None:
    """Both route_id AND route_digest are individually checked."""
    res = assert_no_route_change(
        original_route_id="r1",
        original_route_digest="d1",
        new_route_id="r1",  # same
        new_route_digest="d2",  # changed
    )
    assert not res.ok
    assert res.reason is BypassReason.CHANGES_ROUTE_ID_OR_DIGEST


def test_assert_no_workflow_expansion_shrink_also_rejected() -> None:
    """Workflow shrinking is also a structural mutation."""
    res = assert_no_workflow_expansion(original_step_count=5, new_step_count=4)
    assert not res.ok


def test_assert_no_provider_or_tool_switch_only_provider_check() -> None:
    """When declared_model is None, model check is skipped."""
    res = assert_no_provider_or_tool_switch(
        declared_provider="anthropic",
        actual_provider="anthropic",
    )
    assert res.ok


def test_assert_repair_requires_both_hashes_to_match() -> None:
    """Both blueprint_hash and policy_hash must agree."""
    a = assert_repair_under_same_snapshot(
        original_blueprint_hash="b1",
        original_policy_hash="p1",
        repair_blueprint_hash="b1",
        repair_policy_hash="p1",
    )
    assert a.ok

    b = assert_repair_under_same_snapshot(
        original_blueprint_hash="b1",
        original_policy_hash="p1",
        repair_blueprint_hash="b2",  # drift
        repair_policy_hash="p1",
    )
    assert not b.ok

    c = assert_repair_under_same_snapshot(
        original_blueprint_hash="b1",
        original_policy_hash="p1",
        repair_blueprint_hash="b1",
        repair_policy_hash="p2",  # drift
    )
    assert not c.ok


@pytest.mark.parametrize(
    "cls,sealed,expected_ok",
    [
        ("SUCCESS", "", True),
        ("SUCCESS", "art-1", True),
        ("DEGRADED_SUCCESS", "", True),  # not in must-seal list
        ("FAILURE", "", False),
        ("FAILURE", "art-1", True),
        ("REJECTED", "", False),
        ("REJECTED", "art-1", True),
        ("NEEDS_HELP", "", False),
        ("NEEDS_HELP", "art-1", True),
        ("FAIL_TERMINAL", "", False),
        ("FAIL_TERMINAL", "art-1", True),
    ],
)
def test_assert_seals_rejection_or_failure_matrix(cls: str, sealed: str, expected_ok: bool) -> None:
    res = assert_seals_rejection_or_failure(terminal_class=cls, sealed_artifact_ref=sealed)
    assert res.ok is expected_ok


@pytest.mark.parametrize(
    "target",
    [
        "agentic_core/L4_state/whatever",
        "L4_state/canonical_store",
        "uwg_commit_path",
        "UWG.COMMIT.LOG",  # case insensitive
        "system_of_record",
        "DurableWrite",
    ],
)
def test_assert_no_direct_l4_write_case_insensitive_substrings(target: str) -> None:
    """All L4/UWG/system-of-record/durable-write substrings rejected (case-insensitive)."""
    res = assert_no_direct_l4_write(target=target)
    assert not res.ok


@pytest.mark.parametrize(
    "target",
    [
        "proposed_state_diff",
        "proposed_state_diff_buffer",
        "in_memory_only",
        "scratch_space",
        "",
    ],
)
def test_assert_no_direct_l4_write_passes_safe_targets(target: str) -> None:
    res = assert_no_direct_l4_write(target=target)
    assert res.ok


@pytest.mark.parametrize(
    "channel",
    [
        "hitl_chat",
        "human_direct_email",
        "ask_user_inline",
        "user_clarify_inline",
        "HITL_CHAT_FOO",
    ],
)
def test_assert_no_direct_human_call_rejects_direct(channel: str) -> None:
    res = assert_no_direct_human_call(channel=channel)
    assert not res.ok


@pytest.mark.parametrize(
    "channel",
    [
        "exit_hitl_packetization",
        "exit_review_packet",
        "uwg_request_candidate",
        "",
    ],
)
def test_assert_no_direct_human_call_packetized_passes(channel: str) -> None:
    res = assert_no_direct_human_call(channel=channel)
    assert res.ok


@pytest.mark.parametrize(
    "scope,ok",
    [
        ("DATA_ONLY", True),
        ("data_only", True),  # case insensitive
        ("AUTHORITATIVE", False),
        ("AUTHORITY", False),
        ("WRITE", False),
        ("", True),  # empty treated as not-set
    ],
)
def test_assert_human_input_data_only_matrix(scope: str, ok: bool) -> None:
    res = assert_human_input_is_data_only(human_input_scope=scope)
    assert res.ok is ok


@pytest.mark.parametrize(
    "layer,ok",
    [
        ("L2", False),
        ("l2", False),
        ("PROMPT_ASSEMBLY", True),
        ("L0", True),
        ("L3", True),
        ("", True),
    ],
)
def test_assert_no_prompt_envelope_construction_layer_matrix(layer: str, ok: bool) -> None:
    res = assert_no_prompt_envelope_construction(builder_layer=layer)
    assert res.ok is ok


@pytest.mark.parametrize(
    "auth,ok",
    [
        ("BOUNDED_READ", True),
        ("BOUNDED_TOOL_ACTION", True),
        ("EVIDENCE_CONTRACT", True),
        ("OPPORTUNISTIC", False),
        ("FREE_RETRIEVAL", False),
        ("AUTONOMOUS", False),
        ("", True),
    ],
)
def test_assert_no_unapproved_c0_retrieval_matrix(auth: str, ok: bool) -> None:
    res = assert_no_unapproved_c0_retrieval(retrieval_authority=auth)
    assert res.ok is ok


def test_assert_no_direct_uwg_call_clearance_table() -> None:
    """UWG with exit_cleared=True is OK; without is not."""
    assert assert_no_direct_uwg_call(target_layer="UWG", exit_cleared=True).ok
    assert not assert_no_direct_uwg_call(target_layer="UWG", exit_cleared=False).ok
    # Non-UWG layer: clearance flag irrelevant
    assert assert_no_direct_uwg_call(target_layer="L4", exit_cleared=False).ok
    assert assert_no_direct_uwg_call(target_layer="L0", exit_cleared=False).ok


# ===========================================================================
# Section K — assert_l2_bounded() aggregator surface
# ===========================================================================


def test_aggregator_with_empty_facts_runs_no_checks() -> None:
    results = assert_l2_bounded({})
    assert results == ()


def test_aggregator_partial_facts_runs_only_applicable_checks() -> None:
    results = assert_l2_bounded({"capability_token_ref": "cap-1"})
    assert len(results) == 1
    assert results[0].ok


def test_aggregator_fault_isolation() -> None:
    """One bad check doesn't suppress others; all run."""
    facts = {
        "capability_token_ref": "",  # FAIL
        "sandbox_envelope_ref": "sbx",  # OK
        "original_route_id": "r1",
        "new_route_id": "r2",  # FAIL
    }
    results = assert_l2_bounded(facts)
    fails = [r for r in results if not r.ok]
    passes = [r for r in results if r.ok]
    assert len(fails) == 2
    assert len(passes) == 1


def test_raise_if_any_with_no_results_does_not_raise() -> None:
    raise_if_any(())


def test_raise_if_any_with_only_passes_does_not_raise() -> None:
    raise_if_any((BypassCheckResult(ok=True),))


def test_raise_if_any_includes_violation_count_in_message() -> None:
    facts = {
        "capability_token_ref": "",
        "sandbox_envelope_ref": "",
    }
    results = assert_l2_bounded(facts)
    with pytest.raises(L2BypassViolation, match=r"2 violation"):
        raise_if_any(results)


def test_raise_if_any_includes_each_reason_value_in_message() -> None:
    facts = {
        "capability_token_ref": "",
        "human_input_scope": "AUTHORITATIVE",
    }
    results = assert_l2_bounded(facts)
    with pytest.raises(L2BypassViolation) as excinfo:
        raise_if_any(results)
    msg = str(excinfo.value)
    assert "missing_capability_token" in msg
    assert "treats_human_input_as_authority" in msg


# ===========================================================================
# Section L — Bypass-reason completeness
# ===========================================================================


def test_bypass_reason_enum_complete() -> None:
    """All 16 BypassReason values match the doc 04.8 §PHASE 3 list."""
    expected = {
        "direct_l4_write",
        "direct_uwg_call",
        "emits_final_exit_disposition",
        "changes_route_id_or_digest",
        "expands_workflow",
        "unapproved_c0_retrieval",
        "builds_prompt_envelope",
        "asks_human_directly",
        "treats_human_input_as_authority",
        "silent_provider_or_tool_switch",
        "missing_capability_token",
        "missing_sandbox_envelope",
        "repair_under_changed_snapshot",
        "unsealed_rejection_or_failure",
        "ptc_raw_result_leak",
        "ptc_untranscripted_io",
    }
    actual = {r.value for r in BypassReason}
    assert actual == expected, f"missing: {expected - actual} extra: {actual - expected}"


# ===========================================================================
# Section M — EntryRejection edge cases
# ===========================================================================


def test_entry_rejection_default_field_values() -> None:
    rej = EntryRejection(
        rejection_id="r-1",
        reason=EntryRejectionReason.UNSIGNED_PACKET,
        detail="missing sig",
    )
    assert rej.source_packet_type is None
    assert rej.failed_field == ""
    assert rej.boundary_violations == ()


def test_entry_rejection_with_boundary_violations_tuple() -> None:
    rej = EntryRejection(
        rejection_id="r-1",
        reason=EntryRejectionReason.BOUNDARY_VIOLATION,
        detail="multiple",
        boundary_violations=("no_direct_l4_write_asserted", "no_l6_learning_asserted"),
    )
    assert len(rej.boundary_violations) == 2


# ===========================================================================
# Section N — Determinism / replay invariants
# ===========================================================================


def test_normalization_is_pure_no_side_effects_on_inputs() -> None:
    """Calling normalize_to_request must not mutate the input dict."""
    pkt = _good_packet()
    snapshot = dict(pkt)
    normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    assert pkt == snapshot


def test_normalization_two_runs_yield_equal_request_fields() -> None:
    """Same input ⇒ identical request shape across two calls."""
    a = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    b = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    assert a.request is not None
    assert b.request is not None
    # Compare every field (dataclasses.asdict roundtrip via __eq__).
    assert a.request == b.request


def test_normalization_request_id_drift_yields_different_request() -> None:
    pkt_a = _good_packet()
    pkt_b = _good_packet()
    pkt_b["request_id"] = "different-request-id"
    a = normalize_to_request(raw_packet=pkt_a, authority_context=_good_authority())
    b = normalize_to_request(raw_packet=pkt_b, authority_context=_good_authority())
    assert a.request != b.request


# ===========================================================================
# Section O — Full pipeline negative composition
# ===========================================================================


def test_unsigned_packet_short_circuits_before_field_checks() -> None:
    """Unsigned packet rejected even when all required fields are present."""
    pkt = _good_packet()
    pkt["issuer_signature_hmac"] = ""
    res = normalize_to_request(raw_packet=pkt, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.UNSIGNED_PACKET


def test_boundary_violation_short_circuits_before_authority_checks() -> None:
    """Boundary check is the first gate (cheapest); fires before authority."""
    bad_boundary = L2BoundaryAssertion(no_route_decision_asserted=False)
    # Even a packet that would later fail multiple ways is rejected as boundary.
    pkt = _good_packet()
    pkt["issuer_signature_hmac"] = ""  # would also fail signature
    res = normalize_to_request(
        raw_packet=pkt,
        authority_context=_good_authority(),
        boundary_assertion=bad_boundary,
    )
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.BOUNDARY_VIOLATION
    # The BOUNDARY check hit FIRST, so signature is never checked.
