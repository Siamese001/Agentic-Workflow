"""Tests for PTC execution contracts (doc 04.7).

Covers:
  * PTCExecutionProfile invariants (04.7 §PHASE 1.1)
  * PTCScriptEnvelope invariants (04.7 §PHASE 1.2)
  * PTCSandboxReceipt fail-closed invariants (04.7 §PHASE 1.3 + §PHASE 4)
  * Acceptance tests from 04.7 §PHASE 6
"""

from __future__ import annotations

import pytest

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
# Fixtures
# ---------------------------------------------------------------------------


def _good_profile() -> PTCExecutionProfile:
    return PTCExecutionProfile(
        ptc_profile_id="ptc-prof-1",
        route_id="route-1",
        execution_form="SINGLE_STEP",
        script_language=PTCScriptLanguage.PYTHON,
        allowed_tool_calls=("query_database", "fetch_record", "compute_summary"),
        max_tool_calls=5,
        max_runtime_ms=30_000,
        max_stdout_bytes=4096,
        max_stderr_bytes=2048,
        max_raw_result_bytes=1_048_576,
    )


def _good_envelope() -> PTCScriptEnvelope:
    return PTCScriptEnvelope(
        ptc_script_envelope_id="ptc-env-1",
        approved_work_order_ref="awo-1",
        script_text_ref="script-store://abc",
        script_digest="sha256:deadbeef",
        imports_allowlist=("json", "datetime"),
        filesystem_allowlist=("/tmp/sandbox",),
        network_allowlist=(),
        tool_call_manifest=("query_database", "fetch_record", "compute_summary"),
        expected_stdout_schema="schema://stdout/v1",
        deterministic_seed="seed-1",
        replay_key="rk-1",
    )


def _good_tool_receipt(tool_call_id: str = "tc-1") -> PTCToolCallReceipt:
    return PTCToolCallReceipt(
        tool_call_id=tool_call_id,
        tool_name="query_database",
        args_hash="argsha-1",
        raw_result_ref=f"sbx://{tool_call_id}/result",
        return_code=0,
        started_at_unix=1.0,
        ended_at_unix=2.0,
    )


def _good_receipt(
    *,
    result_class: PTCResultClass = PTCResultClass.SUCCESS,
    untranscripted: UntranscriptedIOStatus = UntranscriptedIOStatus.CLEAN,
    capability: CapabilityViolationStatus = CapabilityViolationStatus.CLEAN,
    escape: SandboxEscapeStatus = SandboxEscapeStatus.CLEAN,
) -> PTCSandboxReceipt:
    return PTCSandboxReceipt(
        ptc_sandbox_receipt_id="ptc-rcpt-1",
        script_envelope_ref="ptc-env-1",
        context_freeze_receipt_ref="cfreeze-1",
        context_unfreeze_receipt_ref="cunfreeze-1",
        tool_call_receipts=(
            _good_tool_receipt("tc-1"),
            _good_tool_receipt("tc-2"),
            _good_tool_receipt("tc-3"),
        ),
        raw_result_refs_sandbox_only=(
            "sbx://tc-1/result",
            "sbx://tc-2/result",
            "sbx://tc-3/result",
        ),
        stdout_summary_ref="stdout-summary://abc",
        stderr_summary_ref="stderr-summary://abc",
        untranscripted_io_status=untranscripted,
        capability_violation_status=capability,
        sandbox_escape_status=escape,
        result_class=result_class,
        deterministic_digest="ddigest-1",
    )


# ---------------------------------------------------------------------------
# 04.7 §PHASE 1.1 — PTCExecutionProfile invariants
# ---------------------------------------------------------------------------


def test_profile_default_policies_are_safe() -> None:
    p = _good_profile()
    assert p.context_freeze_required is True
    assert p.raw_result_context_policy is RawResultContextPolicy.SANDBOX_ONLY
    assert p.fail_closed_on_untranscripted_io is True
    assert p.l5_reclearance_required_on_modify is True
    assert p.stdout_return_policy in (
        StdoutReturnPolicy.SUMMARY_ONLY,
        StdoutReturnPolicy.STRUCTURED_CARD_ONLY,
    )


def test_profile_rejects_empty_allowed_tool_calls() -> None:
    with pytest.raises(PTCContractError, match="allowed_tool_calls"):
        PTCExecutionProfile(
            ptc_profile_id="x",
            route_id="r",
            execution_form="f",
            script_language=PTCScriptLanguage.PYTHON,
            allowed_tool_calls=(),
            max_tool_calls=1,
            max_runtime_ms=1,
            max_stdout_bytes=1,
            max_stderr_bytes=1,
            max_raw_result_bytes=1,
        )


def test_profile_rejects_invalid_max_tool_calls() -> None:
    with pytest.raises(PTCContractError, match="max_tool_calls"):
        PTCExecutionProfile(
            ptc_profile_id="x",
            route_id="r",
            execution_form="f",
            script_language=PTCScriptLanguage.PYTHON,
            allowed_tool_calls=("a",),
            max_tool_calls=0,
            max_runtime_ms=1,
            max_stdout_bytes=1,
            max_stderr_bytes=1,
            max_raw_result_bytes=1,
        )


def test_profile_rejects_disabled_context_freeze() -> None:
    with pytest.raises(PTCContractError, match="context_freeze_required"):
        PTCExecutionProfile(
            ptc_profile_id="x",
            route_id="r",
            execution_form="f",
            script_language=PTCScriptLanguage.PYTHON,
            allowed_tool_calls=("a",),
            max_tool_calls=1,
            max_runtime_ms=1,
            max_stdout_bytes=1,
            max_stderr_bytes=1,
            max_raw_result_bytes=1,
            context_freeze_required=False,
        )


def test_profile_tool_is_allowed() -> None:
    p = _good_profile()
    assert p.tool_is_allowed("query_database")
    assert not p.tool_is_allowed("execute_shell")


# ---------------------------------------------------------------------------
# 04.7 §PHASE 1.2 — PTCScriptEnvelope invariants
# ---------------------------------------------------------------------------


def test_envelope_requires_script_digest() -> None:
    with pytest.raises(PTCContractError, match="script_digest"):
        PTCScriptEnvelope(
            ptc_script_envelope_id="x",
            approved_work_order_ref="awo-1",
            script_text_ref="ref",
            script_digest="",
            imports_allowlist=(),
            filesystem_allowlist=(),
            network_allowlist=(),
            tool_call_manifest=(),
            expected_stdout_schema="s",
            deterministic_seed="seed",
            replay_key="rk",
        )


def test_envelope_requires_approved_work_order_ref() -> None:
    with pytest.raises(PTCContractError, match="approved_work_order_ref"):
        PTCScriptEnvelope(
            ptc_script_envelope_id="x",
            approved_work_order_ref="",
            script_text_ref="ref",
            script_digest="d",
            imports_allowlist=(),
            filesystem_allowlist=(),
            network_allowlist=(),
            tool_call_manifest=(),
            expected_stdout_schema="s",
            deterministic_seed="seed",
            replay_key="rk",
        )


# ---------------------------------------------------------------------------
# 04.7 §PHASE 1.3 + §PHASE 4 — fail-closed invariants on receipt
# ---------------------------------------------------------------------------


def test_three_allowed_tool_calls_run_inside_one_ptc_attempt() -> None:
    """04.7 §PHASE 6 — Three allowed tool calls in one PTC sandbox attempt."""
    receipt = _good_receipt()
    assert len(receipt.tool_call_receipts) == 3
    assert receipt.is_clean()
    assert receipt.result_class is PTCResultClass.SUCCESS


def test_raw_tool_result_never_appears_in_model_visible_context() -> None:
    """04.7 §PHASE 6 — raw results stay in sandbox.

    Receipt may only carry refs (short opaque strings), never inlined bytes.
    """
    receipt = _good_receipt()
    for ref in receipt.raw_result_refs_sandbox_only:
        assert isinstance(ref, str)
        # Each ref is a short URL-shaped string, not bulk content.
        assert len(ref) < 2048
        assert ref.startswith("sbx://")


def test_receipt_rejects_inlined_bulk_payload_as_ref() -> None:
    """A "ref" longer than 2 KB is bulk leakage — must be rejected."""
    bulk = "x" * 4096
    with pytest.raises(PTCContractError, match="too large to be a ref"):
        PTCSandboxReceipt(
            ptc_sandbox_receipt_id="r",
            script_envelope_ref="se",
            context_freeze_receipt_ref="cf",
            context_unfreeze_receipt_ref="cu",
            tool_call_receipts=(),
            raw_result_refs_sandbox_only=(bulk,),
            stdout_summary_ref="s",
            stderr_summary_ref="s",
            untranscripted_io_status=UntranscriptedIOStatus.CLEAN,
            capability_violation_status=CapabilityViolationStatus.CLEAN,
            sandbox_escape_status=SandboxEscapeStatus.CLEAN,
            result_class=PTCResultClass.SUCCESS,
            deterministic_digest="d",
        )


def test_untranscripted_io_fails_closed() -> None:
    """04.7 §PHASE 6 — untranscripted file read fails closed."""
    # untranscripted DETECTED but result_class != REJECTED must raise.
    with pytest.raises(PTCContractError, match="untranscripted_io_status=DETECTED"):
        _good_receipt(
            result_class=PTCResultClass.SUCCESS,
            untranscripted=UntranscriptedIOStatus.DETECTED,
        )

    # Compliant: when DETECTED, result_class MUST be REJECTED.
    rcpt = _good_receipt(
        result_class=PTCResultClass.REJECTED,
        untranscripted=UntranscriptedIOStatus.DETECTED,
    )
    assert rcpt.result_class is PTCResultClass.REJECTED


def test_unknown_network_egress_fails_closed_via_capability_violation() -> None:
    """04.7 §PHASE 6 — unknown network egress = capability violation = REJECTED."""
    with pytest.raises(PTCContractError, match="capability_violation_status=DETECTED"):
        _good_receipt(
            result_class=PTCResultClass.SUCCESS,
            capability=CapabilityViolationStatus.DETECTED,
        )
    rcpt = _good_receipt(
        result_class=PTCResultClass.REJECTED,
        capability=CapabilityViolationStatus.DETECTED,
    )
    assert rcpt.result_class is PTCResultClass.REJECTED


def test_sandbox_escape_fails_closed() -> None:
    with pytest.raises(PTCContractError, match="sandbox_escape_status=DETECTED"):
        _good_receipt(
            result_class=PTCResultClass.SUCCESS,
            escape=SandboxEscapeStatus.DETECTED,
        )
    rcpt = _good_receipt(
        result_class=PTCResultClass.REJECTED,
        escape=SandboxEscapeStatus.DETECTED,
    )
    assert rcpt.result_class is PTCResultClass.REJECTED


def test_clean_receipt_returns_stdout_summary_and_receipts_only() -> None:
    """04.7 §PHASE 6 — PTC returns stdout summary + receipts only."""
    receipt = _good_receipt()
    # Stdout summary is by REFERENCE — the bulk text itself is not on the receipt.
    assert receipt.stdout_summary_ref == "stdout-summary://abc"
    assert receipt.stderr_summary_ref == "stderr-summary://abc"
    # Each tool call has a receipt entry.
    assert all(isinstance(t, PTCToolCallReceipt) for t in receipt.tool_call_receipts)


def test_human_review_threshold_defaults_are_safe() -> None:
    """04.7 §PHASE 3 — low-confidence/policy-ambiguous → human review."""
    t = HumanReviewThreshold()
    # Defaults push borderline cases to human review by default.
    assert t.confidence_below > 0.0
    assert t.risk_above < 1.0
    assert t.policy_ambiguity_above < 1.0


def test_envelope_carries_all_replay_metadata() -> None:
    """04.7 §PHASE 1.2 — script envelope must carry replay-relevant fields."""
    env = _good_envelope()
    assert env.script_digest == "sha256:deadbeef"
    assert env.deterministic_seed == "seed-1"
    assert env.replay_key == "rk-1"
    assert "json" in env.imports_allowlist


def test_profile_acceptance_is_data_only_no_authority_flip() -> None:
    """A valid profile may not silently change context isolation defaults."""
    p = _good_profile()
    assert p.raw_result_context_policy is RawResultContextPolicy.SANDBOX_ONLY
    # Cannot construct one with raw_result_context_policy != SANDBOX_ONLY because
    # the enum class only has SANDBOX_ONLY. Sanity check:
    assert list(RawResultContextPolicy) == [RawResultContextPolicy.SANDBOX_ONLY]
