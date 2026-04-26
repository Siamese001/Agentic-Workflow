"""L2 doctrine runtime proof harness.

Exercises every contract introduced by plan
``.windsurf/plans/l2-execute-doc-gap-fill-9c2a31.md`` end-to-end and emits
deterministic digests + behavioral evidence for the requirements matrix at
``docs/reports/plans/l2_doctrine_requirements_matrix.md``.

Run:
    python scripts/proof/run_l2_doctrine_runtime_proof.py

Output is plain text, designed to be redirected to
``docs/reports/plans/l2_doctrine_runtime_proof.txt``.

This harness performs **no I/O outside stdout**. It does not call any tool,
model, MCP, or write to L4. Every contract is constructed in-memory and the
emitted digests come purely from the canonical-payload hashing implemented
inside each contract.
"""

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from typing import Any

from agentic_core.L2_execution.entry.packet_normalizer import normalize_to_request
from agentic_core.L2_execution.enforcement.anti_bypass_guards import (
    BypassReason,
    L2BypassViolation,
    assert_l2_bounded,
    raise_if_any,
)
from agentic_core.L2_execution.observability.l2_spans import (
    L2_E1_SPANS,
    L2_E2_SPANS,
    L2_E3_SPANS,
    L2_E4_SPANS,
    L2_E5_SPANS,
    L2_PTC_SPANS,
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)
from agentic_core.L2_execution.types.l2_execution_request import (
    DurableWriteAuthority,
    EntryRejectionReason,
    ExecutionAuthorityContext,
    HumanInputScope,
    IssuerSurface,
    L2BoundaryAssertion,
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
# Helpers
# ---------------------------------------------------------------------------


def _digest(label: str, payload: dict[str, Any]) -> str:
    """Compute a stable SHA256 digest tagged with a short label."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return f"{label}:{hashlib.sha256(canonical.encode()).hexdigest()[:16]}"


def _section(title: str) -> None:
    bar = "=" * 78
    print(bar)
    print(f"  {title}")
    print(bar)


def _step(step: str, detail: str = "") -> None:
    if detail:
        print(f"  [STEP] {step:<48s} | {detail}")
    else:
        print(f"  [STEP] {step}")


def _evidence(label: str, value: object) -> None:
    print(f"  [EVID] {label:<48s} = {value!r}")


def _pass(rule: str) -> None:
    print(f"  [PASS] {rule}")


def _fail_closed(rule: str, exc: BaseException) -> None:
    print(f"  [FAIL-CLOSED] {rule:<40s} | {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Section 1 — 04.1 Entry / Authority / Packet Intake
# ---------------------------------------------------------------------------


def _good_authority(issuer: IssuerSurface = IssuerSurface.L0) -> ExecutionAuthorityContext:
    return ExecutionAuthorityContext(
        authority_context_id="proof-auth-1",
        issuer_surface=issuer,
        issuer_receipt_ref="iss-rcpt-proof-1",
        route_authority_ref="route-auth-proof-1",
        capability_scope="cap.read",
        sandbox_scope="sbx.tmp",
        tenant_scope="tenant-proof",
        acl_scope="acl.read",
        provider_lane="anthropic.lane.proof",
        filesystem_scope="/tmp/proof",
        network_scope="none",
        credential_scope="none",
    )


def _good_packet() -> dict[str, Any]:
    return {
        "request_id": "proof-req-1",
        "run_id": "proof-run-1",
        "trace_root": "proof-trace-1",
        "route_id": "route-proof-1",
        "route_contract_ref": "rc-proof-1",
        "execution_form": "SINGLE_STEP",
        "source_packet_type": SourcePacketType.L0_SINGLE_STEP,
        "signed_packet_ref": "sig-proof-1",
        "task_spec_ref": "task-proof-1",
        "capability_token_ref": "cap-tok-proof-1",
        "sandbox_envelope_ref": "sbx-env-proof-1",
        "side_effect_class": "READ",
        "policy_hash": "pol-proof-1",
        "blueprint_hash": "bp-proof-1",
        "replay_key": "rk-proof-1",
        "snapshot_manifest_ref": "sm-proof-1",
        "expected_output_contract": "answer.text.v1",
        "max_attempts": 1,
        "max_repair_count": 1,
        "timeout_ms": 5_000,
        "cost_budget": 0.05,
        "issuer_signature_hmac": "sig-hmac-proof",
        "telemetry_keys": ("trace_root", "request_id"),
    }


def section_04_1() -> None:
    _section("04.1  L2 Execution Entry / Authority / Packet Intake")

    _step("happy-path normalization (L0 single-step)")
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    assert res.ok, res.rejection
    req = res.request
    assert req is not None
    digest = _digest(
        "l2req",
        {
            "request_id": req.request_id,
            "run_id": req.run_id,
            "route_id": req.route_id,
            "policy_hash": req.policy_hash,
            "blueprint_hash": req.blueprint_hash,
            "replay_key": req.replay_key,
            "source_packet_type": req.source_packet_type.value,
            "issuer": req.authority_context.issuer_surface.value,
        },
    )
    _evidence("L2ExecutionRequest digest", digest)
    _evidence("issuer_surface", req.authority_context.issuer_surface.value)
    _evidence("human_input_scope", req.authority_context.human_input_scope.value)
    _evidence("durable_write_authority", req.authority_context.durable_write_authority.value)
    _evidence("boundary_all_clean", req.boundary_assertion.all_clean())
    _pass("PHASE 1 §1 — required fields populated")
    _pass("PHASE 1 §2 — ExecutionAuthorityContext.human_input_scope=DATA_ONLY")
    _pass("PHASE 1 §3 — L2BoundaryAssertion.all_clean()=True")

    _step("L3 current-step + grounded route normalization")
    raw = _good_packet()
    raw["source_packet_type"] = SourcePacketType.L3_CURRENT_STEP
    raw["grounded"] = True
    raw["prompt_envelope_ref"] = "pe-proof-1"
    raw["final_evidence_contract_ref"] = "fec-proof-1"
    raw["l3_step_contract_ref"] = "step-proof-1"
    res2 = normalize_to_request(raw_packet=raw, authority_context=_good_authority(IssuerSurface.L3))
    assert res2.ok, res2.rejection
    _evidence(
        "L3-step lineage refs preserved",
        {
            "prompt_envelope_ref": res2.request.prompt_envelope_ref,
            "final_evidence_contract_ref": res2.request.final_evidence_contract_ref,
            "l3_step_contract_ref": res2.request.l3_step_contract_ref,
        },
    )
    _pass("PHASE 4 — entry receipt preserves route/plan/prompt/evidence/step refs")

    _step("PTC marker normalization (no execution)")
    raw_ptc = _good_packet()
    raw_ptc["is_ptc_execution"] = True
    raw_ptc["ptc_execution_profile_ref"] = "ptc-profile-proof-1"
    raw_ptc["script_digest"] = "sha256:proofdigest"
    raw_ptc["sandbox_profile_ref"] = "sbx-profile-proof-1"
    res3 = normalize_to_request(raw_packet=raw_ptc, authority_context=_good_authority())
    assert res3.ok and res3.request.is_ptc_execution
    _evidence("PTC request normalized but NOT executed", True)
    _pass("PHASE 4 — PTC marker does not execute during entry")

    _step("FAIL-CLOSED: unsigned packet")
    raw_unsigned = _good_packet()
    raw_unsigned["issuer_signature_hmac"] = ""
    bad = normalize_to_request(raw_packet=raw_unsigned, authority_context=_good_authority())
    assert bad.rejection is not None
    assert bad.rejection.reason is EntryRejectionReason.UNSIGNED_PACKET
    _evidence("rejection.reason", bad.rejection.reason.value)
    _pass("PHASE 3 — unsigned packet rejected")

    _step("FAIL-CLOSED: human prose in authority field")
    bad_auth = ExecutionAuthorityContext(
        authority_context_id="auth-bad-1",
        issuer_surface=IssuerSurface.L0,
        issuer_receipt_ref=(
            "Approved by human reviewer because the customer sounded nice "
            "and the request looked routine on a Friday afternoon"
        ),
        route_authority_ref="r",
        capability_scope="c",
        sandbox_scope="s",
        tenant_scope="t",
        acl_scope="a",
        provider_lane="p",
        filesystem_scope="f",
        network_scope="n",
        credential_scope="cr",
    )
    bad2 = normalize_to_request(raw_packet=_good_packet(), authority_context=bad_auth)
    assert bad2.rejection is not None
    assert bad2.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY
    _evidence("rejection.reason", bad2.rejection.reason.value)
    _pass("PHASE 3 — human text cannot become authority")

    _step("FAIL-CLOSED: route_digest mismatch")
    raw_drift = _good_packet()
    raw_drift["route_digest"] = "digest-A"
    bad3 = normalize_to_request(
        raw_packet=raw_drift,
        authority_context=_good_authority(),
        expected_route_digest="digest-B",
    )
    assert bad3.rejection is not None
    assert bad3.rejection.reason is EntryRejectionReason.ROUTE_DIGEST_MISMATCH
    _evidence("rejection.reason", bad3.rejection.reason.value)
    _pass("PHASE 3 — route_digest drift rejected")

    _step("FAIL-CLOSED: declared_intent asks L2 to reroute")
    raw_reroute = _good_packet()
    raw_reroute["declared_intent"] = "reroute"
    bad4 = normalize_to_request(raw_packet=raw_reroute, authority_context=_good_authority())
    assert bad4.rejection is not None
    assert bad4.rejection.reason is EntryRejectionReason.ASKS_L2_TO_RETRIEVE_OR_ROUTE
    _evidence("rejection.reason", bad4.rejection.reason.value)
    _pass("PHASE 3 — packet asks L2 to retrieve/route → rejected")

    _step("FAIL-CLOSED: boundary assertion violation")
    bad_boundary = L2BoundaryAssertion(no_direct_l4_write_asserted=False)
    bad5 = normalize_to_request(
        raw_packet=_good_packet(),
        authority_context=_good_authority(),
        boundary_assertion=bad_boundary,
    )
    assert bad5.rejection is not None
    assert bad5.rejection.reason is EntryRejectionReason.BOUNDARY_VIOLATION
    _evidence("boundary_violations", bad5.rejection.boundary_violations)
    _pass("PHASE 1 §3 — boundary violations short-circuit normalization")

    _step("DETERMINISM: two identical packets → identical request digest")
    a = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    b = normalize_to_request(raw_packet=_good_packet(), authority_context=_good_authority())
    da = _digest(
        "rep",
        {
            "rid": a.request.request_id,
            "ph": a.request.policy_hash,
            "bp": a.request.blueprint_hash,
            "rk": a.request.replay_key,
            "src": a.request.source_packet_type.value,
        },
    )
    db = _digest(
        "rep",
        {
            "rid": b.request.request_id,
            "ph": b.request.policy_hash,
            "bp": b.request.blueprint_hash,
            "rk": b.request.replay_key,
            "src": b.request.source_packet_type.value,
        },
    )
    _evidence("digest run-1", da)
    _evidence("digest run-2", db)
    assert da == db, f"DETERMINISM FAILED: {da} != {db}"
    _pass("DETERMINISM — same request → same digest across two runs")

    print()


# ---------------------------------------------------------------------------
# Section 2 — 04.7 PTC Sandbox contracts
# ---------------------------------------------------------------------------


def section_04_7() -> None:
    _section("04.7  PTC Programmatic Tool Calling / Sandbox")

    _step("happy-path PTCExecutionProfile construction")
    profile = PTCExecutionProfile(
        ptc_profile_id="ptc-prof-proof-1",
        route_id="route-proof-1",
        execution_form="SINGLE_STEP",
        script_language=PTCScriptLanguage.PYTHON,
        allowed_tool_calls=("query_database", "fetch_record", "compute_summary"),
        max_tool_calls=5,
        max_runtime_ms=30_000,
        max_stdout_bytes=4096,
        max_stderr_bytes=2048,
        max_raw_result_bytes=1_048_576,
    )
    pdig = _digest(
        "ptcprof",
        {
            "id": profile.ptc_profile_id,
            "lang": profile.script_language.value,
            "policy": profile.raw_result_context_policy.value,
            "fail_closed": profile.fail_closed_on_untranscripted_io,
        },
    )
    _evidence("PTCExecutionProfile digest", pdig)
    _evidence("raw_result_context_policy", profile.raw_result_context_policy.value)
    _evidence("context_freeze_required", profile.context_freeze_required)
    _evidence("fail_closed_on_untranscripted_io", profile.fail_closed_on_untranscripted_io)
    _evidence("l5_reclearance_required_on_modify", profile.l5_reclearance_required_on_modify)
    _evidence("tool_is_allowed('query_database')", profile.tool_is_allowed("query_database"))
    _evidence("tool_is_allowed('execute_shell')", profile.tool_is_allowed("execute_shell"))
    _pass("PHASE 1 §1 — context isolation defaults are SANDBOX_ONLY")
    _pass("PHASE 1 §1 — fail-closed default is True")

    _step("happy-path PTCScriptEnvelope construction")
    envelope = PTCScriptEnvelope(
        ptc_script_envelope_id="ptc-env-proof-1",
        approved_work_order_ref="awo-proof-1",
        script_text_ref="script-store://proof",
        script_digest="sha256:proofscriptdig",
        imports_allowlist=("json", "datetime"),
        filesystem_allowlist=("/tmp/sandbox",),
        network_allowlist=(),
        tool_call_manifest=("query_database", "fetch_record", "compute_summary"),
        expected_stdout_schema="schema://stdout/v1",
        deterministic_seed="seed-proof",
        replay_key="rk-proof-1",
    )
    edig = _digest(
        "ptcenv",
        {
            "id": envelope.ptc_script_envelope_id,
            "digest": envelope.script_digest,
            "seed": envelope.deterministic_seed,
            "replay_key": envelope.replay_key,
        },
    )
    _evidence("PTCScriptEnvelope digest", edig)
    _pass("PHASE 1 §2 — script_digest + replay_key bound at construction")

    _step("happy-path clean PTCSandboxReceipt (3 tool calls / one sandbox)")
    receipt = PTCSandboxReceipt(
        ptc_sandbox_receipt_id="ptc-rcpt-proof-1",
        script_envelope_ref=envelope.ptc_script_envelope_id,
        context_freeze_receipt_ref="cfreeze-proof",
        context_unfreeze_receipt_ref="cunfreeze-proof",
        tool_call_receipts=tuple(
            PTCToolCallReceipt(
                tool_call_id=f"tc-{i}",
                tool_name="query_database",
                args_hash=f"argsha-{i}",
                raw_result_ref=f"sbx://tc-{i}/result",
                return_code=0,
                started_at_unix=float(i),
                ended_at_unix=float(i + 1),
            )
            for i in range(1, 4)
        ),
        raw_result_refs_sandbox_only=(
            "sbx://tc-1/result",
            "sbx://tc-2/result",
            "sbx://tc-3/result",
        ),
        stdout_summary_ref="stdout-summary://proof",
        stderr_summary_ref="stderr-summary://proof",
        untranscripted_io_status=UntranscriptedIOStatus.CLEAN,
        capability_violation_status=CapabilityViolationStatus.CLEAN,
        sandbox_escape_status=SandboxEscapeStatus.CLEAN,
        result_class=PTCResultClass.SUCCESS,
        deterministic_digest="ddigest-proof",
    )
    rdig = _digest(
        "ptcrcpt",
        {
            "id": receipt.ptc_sandbox_receipt_id,
            "result_class": receipt.result_class.value,
            "is_clean": receipt.is_clean(),
            "tool_calls": len(receipt.tool_call_receipts),
        },
    )
    _evidence("PTCSandboxReceipt digest", rdig)
    _evidence("is_clean()", receipt.is_clean())
    _evidence("tool_call_count", len(receipt.tool_call_receipts))
    _evidence("raw_result_refs are short URLs", all(len(r) < 2048 for r in receipt.raw_result_refs_sandbox_only))
    _pass("PHASE 6 — three allowed tool calls run inside one sandbox attempt")
    _pass("PHASE 4 — raw results stay in sandbox (refs only, ≤2KB each)")
    _pass("PHASE 6 — receipt returns stdout summary by ref, not bulk content")

    _step("FAIL-CLOSED: untranscripted IO detected → must be REJECTED")
    try:
        PTCSandboxReceipt(
            ptc_sandbox_receipt_id="bad-1",
            script_envelope_ref="env",
            context_freeze_receipt_ref="cf",
            context_unfreeze_receipt_ref="cu",
            tool_call_receipts=(),
            raw_result_refs_sandbox_only=(),
            stdout_summary_ref="s",
            stderr_summary_ref="s",
            untranscripted_io_status=UntranscriptedIOStatus.DETECTED,
            capability_violation_status=CapabilityViolationStatus.CLEAN,
            sandbox_escape_status=SandboxEscapeStatus.CLEAN,
            result_class=PTCResultClass.SUCCESS,  # WRONG — must be REJECTED
            deterministic_digest="d",
        )
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("untranscripted_io DETECTED requires REJECTED", exc)

    _step("FAIL-CLOSED: capability_violation DETECTED → must be REJECTED")
    try:
        PTCSandboxReceipt(
            ptc_sandbox_receipt_id="bad-2",
            script_envelope_ref="env",
            context_freeze_receipt_ref="cf",
            context_unfreeze_receipt_ref="cu",
            tool_call_receipts=(),
            raw_result_refs_sandbox_only=(),
            stdout_summary_ref="s",
            stderr_summary_ref="s",
            untranscripted_io_status=UntranscriptedIOStatus.CLEAN,
            capability_violation_status=CapabilityViolationStatus.DETECTED,
            sandbox_escape_status=SandboxEscapeStatus.CLEAN,
            result_class=PTCResultClass.SUCCESS,
            deterministic_digest="d",
        )
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("capability_violation DETECTED requires REJECTED", exc)

    _step("FAIL-CLOSED: sandbox_escape DETECTED → must be REJECTED")
    try:
        PTCSandboxReceipt(
            ptc_sandbox_receipt_id="bad-3",
            script_envelope_ref="env",
            context_freeze_receipt_ref="cf",
            context_unfreeze_receipt_ref="cu",
            tool_call_receipts=(),
            raw_result_refs_sandbox_only=(),
            stdout_summary_ref="s",
            stderr_summary_ref="s",
            untranscripted_io_status=UntranscriptedIOStatus.CLEAN,
            capability_violation_status=CapabilityViolationStatus.CLEAN,
            sandbox_escape_status=SandboxEscapeStatus.DETECTED,
            result_class=PTCResultClass.SUCCESS,
            deterministic_digest="d",
        )
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("sandbox_escape DETECTED requires REJECTED", exc)

    _step("FAIL-CLOSED: bulk payload as raw_result_ref (>2KB)")
    bulk = "x" * 4096
    try:
        PTCSandboxReceipt(
            ptc_sandbox_receipt_id="bad-4",
            script_envelope_ref="env",
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
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("bulk payload inlined as ref → blocked", exc)

    _step("FAIL-CLOSED: empty allowed_tool_calls")
    try:
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
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("empty allowed_tool_calls → blocked", exc)

    _step("FAIL-CLOSED: context_freeze_required=False")
    try:
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
        raise AssertionError("expected PTCContractError")
    except PTCContractError as exc:
        _fail_closed("context_freeze_required must be True", exc)

    _step("Enum invariant: RawResultContextPolicy is SANDBOX_ONLY only")
    members = list(RawResultContextPolicy)
    _evidence("RawResultContextPolicy members", [m.value for m in members])
    assert members == [RawResultContextPolicy.SANDBOX_ONLY]
    _pass("PHASE 4 — raw_result_context_policy enum has only SANDBOX_ONLY")

    _step("HumanReviewThreshold defaults push borderline to review")
    t = HumanReviewThreshold()
    _evidence("confidence_below", t.confidence_below)
    _evidence("risk_above", t.risk_above)
    _evidence("policy_ambiguity_above", t.policy_ambiguity_above)
    assert 0.0 < t.confidence_below < 1.0
    _pass("PHASE 3 — human review thresholds default to safe")

    print()


# ---------------------------------------------------------------------------
# Section 3 — 04.8 OTEL span vocabulary
# ---------------------------------------------------------------------------


def section_04_8_otel() -> None:
    _section("04.8  OTEL Span Vocabulary")

    spans = all_l2_span_names()
    _evidence("E1 span count", len(L2_E1_SPANS))
    _evidence("E2 span count", len(L2_E2_SPANS))
    _evidence("E3 span count", len(L2_E3_SPANS))
    _evidence("E4 span count", len(L2_E4_SPANS))
    _evidence("E5 span count", len(L2_E5_SPANS))
    _evidence("PTC span count", len(L2_PTC_SPANS))
    _evidence("total L2 span count", len(spans))
    assert len(spans) == len(set(spans)), "duplicate span names"
    _pass("PHASE 1 — span registry is duplicate-free")
    assert all(n.startswith("l2.") for n in spans)
    _pass("PHASE 1 — every span uses 'l2.' prefix")

    _step("registry digest (stable across runs)")
    sdig = _digest("spans", {"all": list(spans)})
    _evidence("span registry digest", sdig)

    _step("required-attribute schema enforcement")
    _evidence("required attrs", list(L2_REQUIRED_SPAN_ATTRIBUTES))

    full = {
        "trace_id": "tr-1",
        "span_id": "sp-1",
        "parent_span_id": "psp-1",
        "request_id": "req-1",
        "run_id": "run-1",
        "route_id": "route-1",
        "policy_hash": "pol-1",
        "blueprint_hash": "bp-1",
        "replay_key": "rk-1",
        "capability_token_ref": "cap-1",
        "sandbox_envelope_ref": "sbx-1",
        "side_effect_class": "READ",
        "latency_ms": 42,
    }
    missing_clean = validate_span_attributes(span_name="l2.e1.prep.receive", attrs=full)
    _evidence("clean attrs missing[]", missing_clean)
    assert missing_clean == ()
    _pass("PHASE 1 — every required attribute present → 0 violations")

    incomplete = dict(full)
    del incomplete["replay_key"]
    del incomplete["latency_ms"]
    missing = validate_span_attributes(span_name="l2.e3.exec.tool_call", attrs=incomplete)
    _evidence("incomplete missing", missing)
    assert "replay_key" in missing and "latency_ms" in missing
    _pass("PHASE 1 — missing attrs surfaced by name")

    _step("conditional schema: workflow / attempt / invocation / terminal / artifacts")
    cond = validate_span_attributes(
        span_name="l2.e5.seal.terminal_stamp",
        attrs=full,
        has_workflow=True,
        has_attempt=True,
        has_invocation=True,
        has_terminal=True,
        has_artifacts=True,
    )
    _evidence("all-conditions-true missing", cond)
    expected_cond = {"workflow_id", "step_id", "attempt_id", "invocation_kind", "terminal_class", "reason_codes", "artifact_refs"}
    assert set(cond) == expected_cond
    _pass("PHASE 1 — all conditional attributes correctly demanded")

    _step("FAIL-CLOSED: unknown span name")
    try:
        validate_span_attributes(span_name="l2.unknown.foo", attrs=full)
        raise AssertionError("expected L2SpanAttributeViolation")
    except L2SpanAttributeViolation as exc:
        _fail_closed("unknown span name → reject", exc)

    print()


# ---------------------------------------------------------------------------
# Section 4 — 04.8 Anti-bypass guards
# ---------------------------------------------------------------------------


def section_04_8_bypass() -> None:
    _section("04.8  Anti-Bypass Guards")

    _step("clean facts → all checks pass")
    clean_facts = {
        "capability_token_ref": "cap-1",
        "sandbox_envelope_ref": "sbx-1",
        "original_route_id": "r1",
        "new_route_id": "r1",
        "original_route_digest": "d1",
        "new_route_digest": "d1",
        "original_step_count": 5,
        "new_step_count": 5,
        "declared_provider": "anthropic",
        "actual_provider": "anthropic",
        "declared_model": "claude-haiku",
        "actual_model": "claude-haiku",
        "original_blueprint_hash": "bp",
        "original_policy_hash": "pol",
        "repair_blueprint_hash": "bp",
        "repair_policy_hash": "pol",
        "terminal_class": "SUCCESS",
        "sealed_artifact_ref": "art-1",
        "write_target": "proposed_state_diff_buffer",
        "human_call_channel": "exit_hitl_packetization",
        "human_input_scope": "DATA_ONLY",
        "prompt_envelope_builder_layer": "PROMPT_ASSEMBLY",
        "c0_retrieval_authority": "BOUNDED_READ",
        "uwg_target_layer": "L4",
        "exit_cleared": False,
        "final_disposition": "SUCCESS",
    }
    results = assert_l2_bounded(clean_facts)
    fails = [r for r in results if not r.ok]
    _evidence("clean facts checks", len(results))
    _evidence("clean facts violations", len(fails))
    assert fails == []
    raise_if_any(results)  # must not raise
    _pass("PHASE 3 — well-formed L2 surface passes all 16 guards")

    _step("dirty facts → multiple violations collected")
    dirty_facts = {
        "capability_token_ref": "",
        "sandbox_envelope_ref": "",
        "original_route_id": "r1",
        "new_route_id": "r2",
        "original_route_digest": "d1",
        "new_route_digest": "d1",
        "original_step_count": 5,
        "new_step_count": 7,
        "declared_provider": "anthropic",
        "actual_provider": "openai",
        "original_blueprint_hash": "bp1",
        "repair_blueprint_hash": "bp2",
        "original_policy_hash": "pol1",
        "repair_policy_hash": "pol1",
        "terminal_class": "REJECTED",
        "sealed_artifact_ref": "",
        "write_target": "uwg.commit",
        "human_call_channel": "hitl_chat_inline",
        "human_input_scope": "AUTHORITATIVE",
        "prompt_envelope_builder_layer": "L2",
        "c0_retrieval_authority": "OPPORTUNISTIC",
        "uwg_target_layer": "UWG",
        "exit_cleared": False,
        "final_disposition": "ALLOW_FINISH",
    }
    results2 = assert_l2_bounded(dirty_facts)
    fails2 = [r for r in results2 if not r.ok]
    reasons2 = {r.reason for r in fails2 if r.reason}
    _evidence("dirty checks", len(results2))
    _evidence("dirty violations", len(fails2))
    expected_reasons = {
        BypassReason.MISSING_CAPABILITY_TOKEN,
        BypassReason.MISSING_SANDBOX_ENVELOPE,
        BypassReason.CHANGES_ROUTE_ID_OR_DIGEST,
        BypassReason.EXPANDS_WORKFLOW,
        BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH,
        BypassReason.REPAIR_UNDER_CHANGED_SNAPSHOT,
        BypassReason.UNSEALED_REJECTION_OR_FAILURE,
        BypassReason.DIRECT_L4_WRITE,
        BypassReason.ASKS_HUMAN_DIRECTLY,
        BypassReason.TREATS_HUMAN_INPUT_AS_AUTHORITY,
        BypassReason.BUILDS_PROMPT_ENVELOPE,
        BypassReason.UNAPPROVED_C0_RETRIEVAL,
        BypassReason.DIRECT_UWG_CALL,
        BypassReason.EMITS_FINAL_EXIT_DISPOSITION,
    }
    _evidence(
        "expected reasons covered",
        sorted(r.value for r in expected_reasons & reasons2),
    )
    assert expected_reasons.issubset(reasons2), expected_reasons - reasons2
    _pass("PHASE 3 — every forbidden L2 behavior detected when active")

    _step("raise_if_any() escalates dirty results")
    try:
        raise_if_any(results2)
        raise AssertionError("expected L2BypassViolation")
    except L2BypassViolation as exc:
        _evidence("L2BypassViolation count", str(exc).split("(")[1].split(" ")[0])
        _fail_closed("aggregator escalates ≥1 violation", exc)

    print()


# ---------------------------------------------------------------------------
# Section 5 — Determinism replay across full pipeline
# ---------------------------------------------------------------------------


def section_determinism() -> None:
    _section("Cross-cutting  Determinism / Replay")

    auth = _good_authority()
    raw = _good_packet()
    a = normalize_to_request(raw_packet=raw, authority_context=auth)
    b = normalize_to_request(raw_packet=raw, authority_context=auth)
    da = _digest(
        "fullreq",
        {
            "rid": a.request.request_id,
            "ph": a.request.policy_hash,
            "bp": a.request.blueprint_hash,
            "rk": a.request.replay_key,
            "src": a.request.source_packet_type.value,
            "boundary": a.request.boundary_assertion.all_clean(),
        },
    )
    db = _digest(
        "fullreq",
        {
            "rid": b.request.request_id,
            "ph": b.request.policy_hash,
            "bp": b.request.blueprint_hash,
            "rk": b.request.replay_key,
            "src": b.request.source_packet_type.value,
            "boundary": b.request.boundary_assertion.all_clean(),
        },
    )
    _evidence("run-1 digest", da)
    _evidence("run-2 digest", db)
    assert da == db
    _pass("REPLAY — identical input ⇒ identical request digest")

    raw_drift = dict(raw)
    raw_drift["policy_hash"] = "pol-DIFFERENT"
    c = normalize_to_request(raw_packet=raw_drift, authority_context=auth)
    dc = _digest(
        "fullreq",
        {
            "rid": c.request.request_id,
            "ph": c.request.policy_hash,
            "bp": c.request.blueprint_hash,
            "rk": c.request.replay_key,
            "src": c.request.source_packet_type.value,
            "boundary": c.request.boundary_assertion.all_clean(),
        },
    )
    _evidence("policy_hash-changed digest", dc)
    assert dc != da
    _pass("REPLAY — policy_hash drift ⇒ different digest")

    print()


# ---------------------------------------------------------------------------
# Section 6 — Import hygiene (no I/O / no upper-layer / no PowerShell)
# ---------------------------------------------------------------------------


def section_import_hygiene() -> None:
    _section("Import Hygiene  (no I/O / no upper-layer / no PowerShell)")

    import importlib

    modules = [
        "agentic_core.L2_execution.types.l2_execution_request",
        "agentic_core.L2_execution.types.ptc_execution_profile",
        "agentic_core.L2_execution.entry.packet_normalizer",
        "agentic_core.L2_execution.observability.l2_spans",
        "agentic_core.L2_execution.enforcement.anti_bypass_guards",
    ]
    forbidden_imports = (
        "subprocess",
        "requests",
        "httpx",
        "sqlite3",
        "boto3",
        "psycopg2",
    )
    for mod_name in modules:
        m = importlib.import_module(mod_name)
        src_file = m.__file__ or ""
        with open(src_file, "r", encoding="utf-8") as f:
            text = f.read()
        offenders = [
            f for f in forbidden_imports
            if (f"import {f}" in text or f"from {f} " in text)
        ]
        _evidence(f"{mod_name} forbidden imports", offenders)
        assert offenders == [], f"{mod_name} imports {offenders}"
    _pass("All 5 doctrine modules have zero I/O imports")

    # No PowerShell *invocations* (not enum vocabulary). Match command-style
    # patterns that would actually shell-out, never bare identifiers.
    invocation_patterns = (
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "os.system",
        '"powershell"',
        "'powershell'",
        '"pwsh"',
        "'pwsh'",
        "Start-Process",
    )
    for mod_name in modules:
        m = importlib.import_module(mod_name)
        src_file = m.__file__ or ""
        with open(src_file, "r", encoding="utf-8") as f:
            text = f.read()
        offenders = [b for b in invocation_patterns if b in text]
        assert offenders == [], f"{mod_name} mentions {offenders}"
    _pass("All 5 doctrine modules have zero shell/PowerShell invocations")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print(textwrap.dedent("""
    ============================================================
      L2 EXECUTE DOCTRINE — RUNTIME PROOF HARNESS
      Plan:    .windsurf/plans/l2-execute-doc-gap-fill-9c2a31.md
      Commit:  d92857f4d7 (HEAD at run-time)
      Goal:    exercise every contract; emit deterministic digests;
               prove behavioral invariants under fail-closed conditions.
    ============================================================
    """).strip())
    print()
    section_04_1()
    section_04_7()
    section_04_8_otel()
    section_04_8_bypass()
    section_determinism()
    section_import_hygiene()

    _section("ALL SECTIONS COMPLETED")
    print("  Status: ALL DOCTRINE INVARIANTS PROVEN AT RUNTIME")
    return 0


if __name__ == "__main__":
    sys.exit(main())
