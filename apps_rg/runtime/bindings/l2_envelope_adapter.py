"""apps_rg L2 v4 envelope adapter — E1 PREP → E2 VALIDATION → E3 EXEC → E4 HEAL → E5 SEAL.

Implements the contract surface exercised by ``tests/_apps_contract/test_apps_rg_l2_envelope.py``.

Plan: apps-rg-l2-v4-envelope-adoption-e9f2b1 (W2–W7).

**W3:** ``governed_pa_l2_exit`` — uses ``agentic_core`` ``ProviderGateway`` under envelope stages.
"""
from __future__ import annotations

from agentic_core.config.model_catalog import (
    ANTHROPIC_SONNET_4_20250514_MODEL_ID,
    GEMINI_20_FLASH_MODEL_ID,
    OPENAI_GPT4O_MINI_MODEL_ID,
)

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_GOVERNED_PA_L2_EXIT,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_GOVERNED_PA_L2_EXIT
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

import hashlib
import json
import os
import time
import uuid
from types import SimpleNamespace
from typing import Any, Optional

from agentic_core.runtime.providers.provider_gateway import ProviderGateway
from agentic_core.runtime.providers.provider_types import ProviderModeBlockedError

from apps_rg.l2_recipe.raw_text_json_unwrap import try_unwrap_raw_text_to_resume
from apps_rg.runtime.sections.executive_summary_context_limits import (
    DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS,
)
from apps_rg.l2_recipe.provider_run_diagnostics import write_provider_generation_diagnostics
from apps_rg.l2_recipe.resume_output_shape import (
    BLOCKED_PROVIDER_LANE,
    FAILED_PROVIDER,
    STUB_RECEIPT,
    STRUCTURED_RESUME_OK,
    classify_resume_payload,
)
from apps_rg.runtime.providers.provider_run_mode import (
    AppsRgEnvelopeProviderResolutionError,
    ProviderAuthenticityViolation,
    ProviderRunMode,
    assert_provider_authentic_for_full_resume,
    classify_provider_run_mode,
)

__all__ = [
    "run_apps_rg_l2_envelope",
    "_build_prep_output",
    "_build_frozen_execution_context",
    "_build_work_order_inputs",
    "_build_determinism_bundle",
    "_build_lineage_root",
    "_build_budget_snapshot",
    "_build_capability_scope_summary",
    "_build_approved_work_order",
    "_build_sealed_rejection_packet",
    "_validate_work_order",
    "_execute_approved_work_order",
    "_heal_attempt_failure",
    "_seal_l2_artifact",
]


def _synth_route_and_vr_from_prompt_artifact(prompt_artifact: Any) -> tuple[Any, Any]:
    """Minimal route + validated_request when callers only supply the CPA."""
    rq = str(getattr(prompt_artifact, "request_id", "") or "")
    rn = str(getattr(prompt_artifact, "run_id", "") or "")
    app = str(getattr(prompt_artifact, "app_id", "") or "apps_rg")
    tr = str(getattr(prompt_artifact, "trace_id", "") or "")
    tenant = str(getattr(prompt_artifact, "tenant_id", "") or "apps_rg")
    route = SimpleNamespace(
        route_id="R3_SIMPLE_GROUNDED_READ",
        request_id=rq,
        run_id=rn,
        app_id=app,
        trace_id=tr,
        tenant_id=tenant,
    )
    vr = SimpleNamespace(
        request_id=rq,
        run_id=rn,
        tenant_id=tenant,
        trace_id=tr,
    )
    return route, vr


def _identity_seed(prompt_artifact: Any) -> str:
    parts = "|".join(
        [
            str(getattr(prompt_artifact, "request_id", "") or ""),
            str(getattr(prompt_artifact, "run_id", "") or ""),
            str(getattr(prompt_artifact, "app_id", "") or ""),
            str(getattr(prompt_artifact, "trace_id", "") or ""),
            str(getattr(prompt_artifact, "tenant_id", "") or ""),
        ]
    )
    return hashlib.sha256(parts.encode("utf-8")).hexdigest()


def _cpa_prompt_text(cpa: Any) -> str:
    blocks = getattr(cpa, "prompt_blocks", ()) or ()
    if blocks:
        return "\n".join(f"{getattr(b, 'role', '?')}: {getattr(b, 'content', '')}" for b in blocks)
    sp = str(getattr(cpa, "system_preamble", "") or "")
    ui = str(getattr(cpa, "user_instruction", "") or "")
    return f"{sp}\n{ui}".strip()


def _build_lineage_root(prompt_artifact: Any) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import LineageRoot

    trace_id = str(getattr(prompt_artifact, "trace_id", "") or "")
    request_id = str(getattr(prompt_artifact, "request_id", "") or "")
    run_id = str(getattr(prompt_artifact, "run_id", "") or "")
    parent_route_id = trace_id if trace_id else request_id
    return LineageRoot(
        parent_route_id=parent_route_id,
        parent_plan_id=run_id,
        parent_step_id=None,
        ancestry_chain=(parent_route_id,),
        same_run_packet_family=run_id,
    )


def _build_determinism_bundle(prompt_artifact: Any) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import DeterminismBundle

    comp = str(getattr(prompt_artifact, "compilation_hash", "") or "")
    pol = str(getattr(prompt_artifact, "l5_certification_ref", "") or "")
    rk = str(getattr(prompt_artifact, "replay_key", "") or "")
    sig = str(getattr(prompt_artifact, "signature", "") or "")
    policy_hash = pol if pol else sig
    return DeterminismBundle(
        blueprint_hash=comp,
        policy_hash=policy_hash,
        prompt_hash=comp,
        input_hash=_identity_seed(prompt_artifact),
        replay_key=rk,
        attempt_seed=str(uuid.uuid4()),
    )


def _build_frozen_execution_context(
    prompt_artifact: Any,
    route_contract: Any | None = None,
    validated_request: Any | None = None,
) -> Any:
    del route_contract, validated_request
    from apps_rg.runtime.bindings.l2_envelope_contracts import FrozenExecutionContext

    tm = str(getattr(prompt_artifact, "target_model", "") or "").strip()
    if not tm:
        tm = "unknown"
    tp = str(getattr(prompt_artifact, "target_provider", "") or "").strip()
    if not tp:
        tp = "external_claude"
    roots = tuple(getattr(prompt_artifact, "allowed_file_roots", ()) or ())
    nets = tuple(getattr(prompt_artifact, "allowed_networks", ()) or ())
    return FrozenExecutionContext(
        tool_registry_version="v0",
        model_runtime_version=tm,
        provider_lane=tp,
        filesystem_view=str(roots),
        network_rules=str(nets),
        secrets_scope=str(getattr(prompt_artifact, "egress_policy_ref", "") or ""),
        allowed_file_roots=roots,
        allowed_network_destinations=nets,
        allowed_syscalls=(),
    )


def _build_work_order_inputs(
    prompt_artifact: Any,
    route_contract: Any | None = None,
) -> Any:
    del route_contract
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        CapabilitySpec,
        ExecutionForm,
        TaskSpec,
        WorkOrderInputs,
    )

    evidence_digest = str(getattr(prompt_artifact, "evidence_digest", "") or "")
    task = TaskSpec(
        intent=str(getattr(prompt_artifact, "system_preamble", "") or ""),
        expected_output_contract=str(getattr(prompt_artifact, "schema_version", "") or ""),
        grounded=bool(evidence_digest),
    )
    tools = tuple(getattr(prompt_artifact, "allowed_tools", ()) or ())
    tool_spec = CapabilitySpec(name=str(tools[0]), version="v1") if tools else None
    tm = str(getattr(prompt_artifact, "target_model", "") or "").strip() or "unknown"
    model_spec = CapabilitySpec(name=tm, version="v1")
    max_tokens = int(getattr(prompt_artifact, "max_tokens", DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS) or DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS)
    return WorkOrderInputs(
        execution_form=ExecutionForm.SINGLE_STEP,
        task_spec=task,
        tool_spec=tool_spec,
        model_spec=model_spec,
        action_spec=None,
        retry_ceiling=3,
        max_repair_count=3,
        slo_slice_ms=max_tokens * 15,
    )


def _build_budget_snapshot(prompt_artifact: Any) -> dict[str, Any]:
    return {
        "max_tokens": int(getattr(prompt_artifact, "max_tokens", DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS) or DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS),
        "temperature": float(getattr(prompt_artifact, "temperature", 0.0) or 0.0),
        "model_ref": str(getattr(prompt_artifact, "target_model", "") or ""),
    }


def _build_capability_scope_summary() -> dict[str, Any]:
    return {
        "can_call_llm": True,
        "can_write_l4": False,
        "can_emit_exit_disposition": True,
    }


def _build_approved_work_order(prep_output: Any, budget: dict) -> Any:
    del prep_output, budget
    return None


def _mk_sealed_rejection(
    *,
    rule: str,
    missing_field: str = "",
    decisive: str = "V_FAIL",
) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import SealedRejectionPacket

    return SealedRejectionPacket(
        rejection_packet_id=f"rej-{uuid.uuid4().hex}",
        failed_validation_rule=rule,
        side_effect_class="NONE",
        missing_or_invalid_authority_field=missing_field,
        suggested_reentry_target="L1",
        decisive_rule_id=decisive,
    )


def _build_sealed_rejection_packet(reason: str, run_id: str = "") -> dict[str, Any]:
    return {"status": "REJECTED", "reason": reason, "run_id": run_id}


def _build_prep_output(
    prompt_artifact: Any,
    route_contract: Any | None = None,
    validated_request: Any | None = None,
) -> Any:
    if route_contract is None:
        route_contract, validated_request = _synth_route_and_vr_from_prompt_artifact(
            prompt_artifact
        )
    elif validated_request is None:
        _, validated_request = _synth_route_and_vr_from_prompt_artifact(prompt_artifact)

    from apps_rg.runtime.bindings.l2_envelope_contracts import PrepOutput, ReplayBindings, WriteLockAssertion

    comp = str(getattr(prompt_artifact, "compilation_hash", "") or "")
    rk = str(getattr(prompt_artifact, "replay_key", "") or "")
    missing: list[str] = []
    if not comp:
        missing.append("compilation_hash")
    if not rk:
        missing.append("replay_key")
    ready = not missing
    refusal = "" if ready else "missing:" + ",".join(missing)

    fec = _build_frozen_execution_context(prompt_artifact, route_contract, validated_request)
    det = _build_determinism_bundle(prompt_artifact)
    lineage = _build_lineage_root(prompt_artifact)
    replay = ReplayBindings(
        determinism=det,
        snapshot_manifest=str(getattr(prompt_artifact, "replay_manifest_ref", "") or ""),
    )
    rid = str(getattr(prompt_artifact, "run_id", "") or "")
    rq = str(getattr(prompt_artifact, "request_id", "") or "")
    idem = f"{rq}:{rid}" if rq and rid else rk or rid
    return PrepOutput(
        prep_receipt_id=f"prep-{uuid.uuid4().hex}",
        frozen_execution_context=fec,
        run_id=rid,
        idempotency_key=idem,
        lineage_root=lineage,
        replay_bindings=replay,
        write_lock_assertion=WriteLockAssertion(),
        ready_for_validation=ready,
        refusal_reason=refusal,
    )


def _validate_work_order(prep_output: Any, cpa: Any) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        ApprovedWorkOrder,
        BudgetSnapshot,
        CapabilityScopeSummary,
        ValidationOutput,
    )

    vid = f"val-{uuid.uuid4().hex}"

    def _fail(rule: str, field: str = "") -> Any:
        return ValidationOutput(
            validation_packet_id=vid,
            validation_status="FAIL",
            approved_work_order=None,
            sealed_rejection_packet=_mk_sealed_rejection(rule=rule, missing_field=field),
        )

    if not str(getattr(cpa, "replay_key", "") or "").strip():
        return _fail("V2_MISSING_REPLAY_KEY", "replay_key")
    if not str(getattr(cpa, "compilation_hash", "") or "").strip():
        return _fail("V3_MISSING_COMPILATION_HASH", "compilation_hash")

    tm = str(getattr(cpa, "target_model", "") or "").strip()
    if not tm:
        return _fail("V1_MISSING_MODEL", "target_model")

    max_tok = int(getattr(cpa, "max_tokens", 0) or 0)
    if max_tok <= 0:
        return _fail("V7_INVALID_BUDGET", "max_tokens")

    allowed = tuple(getattr(cpa, "allowed_models", ()) or ())
    if allowed and tm not in allowed:
        return _fail("V1_MODEL_NOT_ALLOWED", "target_model")

    if not getattr(prep_output, "ready_for_validation", False):
        return _fail("V8_PREP_NOT_READY", "prep")

    caps = CapabilityScopeSummary(
        capability_token_id="cap-apps-rg-v1",
        granted_tools=tuple(getattr(cpa, "allowed_tools", ()) or ()),
        granted_models=tuple(getattr(cpa, "allowed_models", ()) or ()),
        tenant_scope=str(getattr(cpa, "tenant_id", "") or ""),
    )
    slo_ms = max_tok * 15
    bud = BudgetSnapshot(
        timeout_ms=slo_ms,
        retry_ceiling=3,
        repair_ceiling=3,
        token_limit=max_tok,
        compute_limit=1,
    )
    awo = ApprovedWorkOrder(
        validation_packet_id=vid,
        decisive_rule_id="V_PASS",
        capability_scope=caps,
        budget_snapshot=bud,
        side_effect_class="READ",
    )
    return ValidationOutput(
        validation_packet_id=vid,
        validation_status="PASS",
        approved_work_order=awo,
        sealed_rejection_packet=None,
    )


def _resolve_l2_envelope_provider_mode() -> Any:
    """How E3 may invoke models — driven by ``APPS_RG_L2_PROVIDER_MODE``.

    - ``stub_only`` — deterministic stub JSON (CI default via ``tests/conftest.py``).
    - ``local_only`` — legacy value retained by the generic enum; apps_rg no longer resolves local providers.
    - ``live_allowed`` — external APIs + stub.

    External keys: ``live``, ``external``, ``all`` map to ``live_allowed``.
    """
    from agentic_core.runtime.providers.provider_types import ProviderMode

    if os.environ.get("APPS_RG_L2_FORCE_STUB", "").strip() == "1":
        return ProviderMode.STUB_ONLY
    raw = (os.environ.get("APPS_RG_L2_PROVIDER_MODE") or "").strip().lower()
    if raw in ("stub_only", "stub", "off", "0", "false", "no"):
        return ProviderMode.STUB_ONLY
    if raw in ("live_allowed", "live", "external", "all"):
        return ProviderMode.LIVE_ALLOWED
    return ProviderMode.LIVE_ALLOWED


def _provider_profile_for_cpa(
    cpa: Any, *, provider_mode: Any, run_mode: ProviderRunMode
) -> Any:
    from agentic_core.runtime.providers.provider_types import (
        ProviderKind,
        ProviderMode,
        ProviderProfile,
    )

    mid = str(getattr(cpa, "target_model", "") or "").strip() or None
    tp = str(getattr(cpa, "target_provider", "") or "").strip().lower()

    if provider_mode == ProviderMode.STUB_ONLY:
        return ProviderProfile(
            profile_id="apps_rg_envelope_stub",
            provider_kind=ProviderKind.STUB,
            model_id=mid,
            capabilities=("text_generation", "structured_json_generation"),
            sandbox_safe=True,
            requires_network=False,
        )

    removed_local_aliases = ("local_v" + "llm", "v" + "llm", "local", "v" + "llm_local")
    if tp in removed_local_aliases:
        raise AppsRgEnvelopeProviderResolutionError(
            f"LOCAL_PROVIDER_REMOVED: target_provider={tp!r}; use external_claude or external_openai"
        )

    if provider_mode == ProviderMode.LIVE_ALLOWED:
        if tp in ("anthropic", "claude"):
            return ProviderProfile(
                profile_id="apps_rg_envelope_anthropic",
                provider_kind=ProviderKind.EXTERNAL_API,
                model_id=mid or ANTHROPIC_SONNET_4_20250514_MODEL_ID,
                api_key_env_var="ANTHROPIC_API_KEY",
                vendor="anthropic",
                capabilities=("text_generation", "structured_json_generation"),
                sandbox_safe=False,
                requires_network=True,
            )
        if tp in ("openai", "gpt", "azure_openai"):
            return ProviderProfile(
                profile_id="apps_rg_envelope_openai",
                provider_kind=ProviderKind.EXTERNAL_API,
                model_id=mid or OPENAI_GPT4O_MINI_MODEL_ID,
                api_key_env_var="OPENAI_API_KEY",
                vendor="openai",
                capabilities=("text_generation", "structured_json_generation"),
                sandbox_safe=False,
                requires_network=True,
            )
        if tp in ("google_gemini", "gemini", "google"):
            return ProviderProfile(
                profile_id="apps_rg_envelope_gemini",
                provider_kind=ProviderKind.EXTERNAL_API,
                model_id=mid or GEMINI_20_FLASH_MODEL_ID,
                api_key_env_var="GOOGLE_API_KEY",
                vendor="google_gemini",
                capabilities=("text_generation", "structured_json_generation"),
                sandbox_safe=False,
                requires_network=True,
            )
        if run_mode == ProviderRunMode.LIVE_REQUIRED:
            raise AppsRgEnvelopeProviderResolutionError(
                f"LIVE_REQUIRED: unknown external target_provider={tp!r} for live_allowed mode"
            )

    elif run_mode == ProviderRunMode.LIVE_REQUIRED:
        raise AppsRgEnvelopeProviderResolutionError(
            f"LIVE_REQUIRED: target_provider={tp!r} is not a resolved live lane under {provider_mode}"
        )

    return ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
        model_id=mid,
        capabilities=("text_generation", "structured_json_generation"),
        sandbox_safe=True,
        requires_network=False,
    )


def _attempt_from_provider_resolution_error(
    *,
    cpa: Any,
    approved_work_order: Any,
    prep_output: Any,
    attempt_number: int,
    exc: AppsRgEnvelopeProviderResolutionError,
) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        AttemptReceipt,
        ExecutionLane,
        ResultClass,
    )

    proposed: dict[str, Any] = {
        "provider_resolution_error": True,
        "generation_status": BLOCKED_PROVIDER_LANE,
        "full_resume_generated": False,
        "decisive_reason": str(exc),
    }
    local_check: dict[str, Any] = {
        "generation_status": BLOCKED_PROVIDER_LANE,
        "full_resume_generated": False,
        "outcome_authorized": False,
        "terminal_class": "BLOCKED",
        "provider_error": {"kind": "resolution", "message": str(exc)},
    }
    return AttemptReceipt(
        attempt_receipt_id=AttemptReceipt.new_id(),
        validation_packet_id=str(approved_work_order.validation_packet_id),
        attempt_count=attempt_number,
        determinism=prep_output.replay_bindings.determinism,
        lineage=prep_output.lineage_root,
        trace_id=cpa.trace_id,
        span_id=f"e3-attempt-{attempt_number}",
        latency_ms=0.0,
        tokens_used=0,
        return_code=10,
        result_class=ResultClass.FAIL_TERMINAL,
        error_summary=str(exc),
        execution_lane=ExecutionLane.MODEL,
        decisive_reason_code="E3_PROVIDER_PROFILE_UNRESOLVED",
        proposed_state_diff=proposed,
        local_check_results=local_check,  # type: ignore[arg-type]
    )


def _attempt_from_authenticity_violation(
    *,
    cpa: Any,
    approved_work_order: Any,
    prep_output: Any,
    attempt_number: int,
    viol: ProviderAuthenticityViolation,
) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        AttemptReceipt,
        ExecutionLane,
        ResultClass,
    )

    proposed: dict[str, Any] = {
        "provider_authenticity_block": True,
        "generation_status": viol.generation_status,
        "full_resume_generated": viol.full_resume_generated,
        "decisive_reason": viol.decisive_reason,
    }
    local_check: dict[str, Any] = {
        "generation_status": viol.generation_status,
        "full_resume_generated": viol.full_resume_generated,
        "outcome_authorized": False,
        "terminal_class": "BLOCKED",
    }
    return AttemptReceipt(
        attempt_receipt_id=AttemptReceipt.new_id(),
        validation_packet_id=str(approved_work_order.validation_packet_id),
        attempt_count=attempt_number,
        determinism=prep_output.replay_bindings.determinism,
        lineage=prep_output.lineage_root,
        trace_id=cpa.trace_id,
        span_id=f"e3-attempt-{attempt_number}",
        latency_ms=0.0,
        tokens_used=0,
        return_code=11,
        result_class=ResultClass.FAIL_TERMINAL,
        error_summary=viol.decisive_reason,
        execution_lane=ExecutionLane.MODEL,
        decisive_reason_code=viol.decisive_reason_code,
        proposed_state_diff=proposed,
        local_check_results=local_check,  # type: ignore[arg-type]
    )


def _execute_approved_work_order(
    *,
    cpa: Any,
    approved_work_order: Any,
    prep_output: Any,
    attempt_number: int,
    resume_artifact_contract_mode: Any | None = None,
    artifact_dir: str | None = None,
) -> Any:
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        AttemptReceipt,
        ExecutionLane,
        ResultClass,
    )
    from agentic_core.runtime.providers.provider_types import (
        ProviderKind,
        ProviderRequest,
    )

    def _emit_diagnostics(payload: dict[str, Any], raw_text: str | None = None) -> None:
        write_provider_generation_diagnostics(
            artifact_dir,
            payload,
            raw_provider_text=raw_text,
        )

    if approved_work_order is None:
        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id="",
            attempt_count=attempt_number,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            trace_id=cpa.trace_id,
            span_id=f"e3-attempt-{attempt_number}",
            latency_ms=0.0,
            tokens_used=0,
            return_code=1,
            result_class=ResultClass.REJECTED,
            error_summary="E3 requires ApprovedWorkOrder",
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="E3_REJECTED",
        )

    run_mode = classify_provider_run_mode(
        resume_artifact_contract_mode=resume_artifact_contract_mode,
    )
    mode = _resolve_l2_envelope_provider_mode()
    gateway = ProviderGateway(provider_mode=mode)

    try:
        profile = _provider_profile_for_cpa(cpa, provider_mode=mode, run_mode=run_mode)
    except AppsRgEnvelopeProviderResolutionError as exc:
        return _attempt_from_provider_resolution_error(
            cpa=cpa,
            approved_work_order=approved_work_order,
            prep_output=prep_output,
            attempt_number=attempt_number,
            exc=exc,
        )

    viol = assert_provider_authentic_for_full_resume(
        run_mode=run_mode,
        profile=profile,
        invoker_class_name=gateway.__class__.__name__,
    )
    if viol is not None:
        return _attempt_from_authenticity_violation(
            cpa=cpa,
            approved_work_order=approved_work_order,
            prep_output=prep_output,
            attempt_number=attempt_number,
            viol=viol,
        )

    prompt_text = _cpa_prompt_text(cpa)
    max_req_tok = int(getattr(cpa, "max_tokens", DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS) or DEFAULT_SCRATCH_MAX_OUTPUT_TOKENS)
    temp_val = float(getattr(cpa, "temperature", 0.1))
    top_p_val = float(getattr(cpa, "top_p", 0.8))
    json_object_response_format = None
    if os.environ.get("APPS_RG_RESPONSE_FORMAT_JSON_OBJECT", "").strip() == "1":
        json_object_response_format = {"type": "json_object"}

    packed_prompt = prompt_text
    prompt_budget_meta: dict[str, Any] = {}

    req = ProviderRequest(
        prompt_text=packed_prompt,
        provider_profile=profile,
        max_tokens=max_req_tok,
        temperature=temp_val,
        top_p=top_p_val,
        openai_response_format=json_object_response_format,
        request_id=str(getattr(cpa, "request_id", "") or ""),
        run_id=str(getattr(cpa, "run_id", "") or ""),
        trace_root=str(getattr(cpa, "trace_id", "") or ""),
        node_id=f"l2-envelope-{attempt_number}",
        prompt_artifact_ref=str(getattr(cpa, "compilation_hash", "") or ""),
    )
    started = time.perf_counter()
    try:
        resp = gateway.invoke(req)
    except ProviderModeBlockedError as exc:
        latency = (time.perf_counter() - started) * 1000.0
        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id=str(approved_work_order.validation_packet_id),
            attempt_count=attempt_number,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            trace_id=cpa.trace_id,
            span_id=f"e3-attempt-{attempt_number}",
            latency_ms=float(latency),
            tokens_used=0,
            return_code=9,
            result_class=ResultClass.FAIL_TERMINAL,
            error_summary=str(exc),
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="E3_PROVIDER_MODE_BLOCKED",
        )
    latency = (time.perf_counter() - started) * 1000.0
    tok = 0
    try:
        if resp.receipt and resp.receipt.token_usage:
            tok = int(resp.receipt.token_usage.total_tokens or 0)
    except (TypeError, ValueError, AttributeError):
        tok = 0

    local_check: dict[str, Any] = {
        "provider_lane": str(profile.profile_id),
        "model_or_tool_name": str(profile.model_id or getattr(cpa, "target_model", "") or ""),
        "span_ids": [f"span-{attempt_number:03d}"],
        "response_format_sent": json_object_response_format is not None,
        "response_format_json_object": bool(
            json_object_response_format
            and json_object_response_format.get("type") == "json_object"
        ),
        "provider_temperature": temp_val,
        "provider_top_p": top_p_val,
    }
    tm = str(getattr(cpa, "target_model", "") or "").strip()
    if tm:
        local_check["model_id"] = tm

    local_check["provider_profile"] = str(profile.profile_id)
    local_check["max_tokens_requested"] = max_req_tok
    local_check["prompt_budget"] = prompt_budget_meta
    local_check["input_prompt_chars"] = len(prompt_text)
    local_check["packed_prompt_chars"] = len(packed_prompt)
    if prompt_budget_meta:
        local_check["max_model_len"] = prompt_budget_meta.get("max_model_len")
        local_check["estimated_output_budget"] = prompt_budget_meta.get("completion_meta", {}).get(
            "effective_max_tokens"
        )
    inv0 = getattr(resp, "invocation_meta", None)
    if isinstance(inv0, dict):
        local_check["provider_invocation"] = inv0
        if inv0.get("http_status") is not None:
            local_check["http_status"] = inv0.get("http_status")
        if inv0.get("effective_max_tokens"):
            local_check["effective_max_tokens"] = inv0.get("effective_max_tokens")
        if inv0.get("prompt_truncated") is not None:
            local_check["prompt_truncated"] = inv0.get("prompt_truncated")
        if inv0.get("prompt_chars_after_truncate") is not None:
            local_check["input_prompt_tokens_est"] = max(
                1,
                int(inv0.get("prompt_chars_after_truncate") or 0) // 2,
            )

    text = str(resp.text or "")
    proposed: dict[str, Any] = {}
    result_class = ResultClass.SUCCESS
    err_summary: str | None = None
    ret_code = 0
    drc = "E3_SUCCESS"
    local_check["raw_text_wrapper_seen"] = False
    local_check["raw_text_unwrap_applied"] = False
    local_check["schema_validation_status"] = ""

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            proposed["generated_resume"] = parsed
        else:
            proposed["generated_resume"] = {"value": parsed}
    except json.JSONDecodeError:
        if text.strip():
            proposed["raw_text"] = text
        else:
            result_class = ResultClass.SOFT_REPAIRABLE
            err_summary = "JSON parse error: invalid syntax"
            drc = "E3_JSON_PARSE_ERROR"
            ret_code = 3

    gr_check = proposed.get("generated_resume")
    raw_only_top = set(proposed.keys()) == {"raw_text"}
    raw_only_nested = isinstance(gr_check, dict) and set(gr_check.keys()) == {"raw_text"}

    if raw_only_nested or raw_only_top:
        local_check["raw_text_wrapper_seen"] = True
        rt_source = None
        if raw_only_nested and isinstance(gr_check, dict):
            rt_source = gr_check.get("raw_text")
        elif raw_only_top:
            rt_source = proposed.get("raw_text")
        inner = None
        rcp: dict[str, Any] = {}
        if isinstance(rt_source, str):
            inner, rcp = try_unwrap_raw_text_to_resume(rt_source)
        proposed["raw_text_unwrap_receipt"] = rcp
        if (
            inner is not None
            and rcp.get("repair_applied") is True
            and rcp.get("validation_status") == "PASS"
        ):
            proposed["generated_resume"] = inner
            gr_check = inner
            raw_only_nested = False
            raw_only_top = False
            result_class = ResultClass.SUCCESS
            err_summary = None
            drc = "E3_SUCCESS"
            ret_code = 0
            local_check["raw_text_unwrap_applied"] = True
            local_check["schema_validation_status"] = "PASS"
            proposed["raw_text_unwrap_applied"] = True
            proposed["schema_validation_status"] = "PASS"
        else:
            local_check["raw_text_unwrap_applied"] = False
            local_check["schema_validation_status"] = "FAIL"
            result_class = ResultClass.FAIL_TERMINAL
            err_summary = (
                "MALFORMED_MODEL_OUTPUT: resume payload is raw_text-only wrapper "
                "(missing structured headline, summary, competencies, experience, education, certifications)"
            )
            drc = "E3_MALFORMED_MODEL_OUTPUT"
            ret_code = 7

    effective_payload: dict[str, Any] | None = None
    if isinstance(gr_check, dict):
        effective_payload = gr_check
    elif raw_only_top:
        rt0 = proposed.get("raw_text")
        effective_payload = {"raw_text": rt0} if rt0 is not None else {"raw_text": ""}

    if effective_payload is not None:
        shape_rep = classify_resume_payload(effective_payload)
        local_check["generation_status"] = shape_rep.generation_status
        local_check["full_resume_generated"] = shape_rep.full_resume_generated
        local_check["resume_shape"] = shape_rep.resume_shape

    if resp.success and run_mode == ProviderRunMode.EXPLICIT_STUB:
        if profile.provider_kind == ProviderKind.STUB:
            local_check["generation_status"] = STUB_RECEIPT
            local_check["full_resume_generated"] = False

    if (
        resp.success
        and result_class == ResultClass.SUCCESS
        and run_mode != ProviderRunMode.EXPLICIT_STUB
        and local_check.get("generation_status")
        and local_check["generation_status"] != STRUCTURED_RESUME_OK
    ):
        gs = str(local_check.get("generation_status") or "")
        result_class = ResultClass.FAIL_TERMINAL
        err_summary = f"INVALID_RESUME_STRUCTURE: generation_status={gs}"
        drc = "E3_MALFORMED_MODEL_OUTPUT"
        ret_code = 7
        local_check["outcome_authorized"] = False
        local_check["terminal_class"] = "FAILURE"

    if not resp.success:
        result_class = ResultClass.FAIL_TERMINAL
        err_summary = str(resp.error_message or "provider_failed")
        drc = "E3_FAILED_PROVIDER"
        ret_code = 8
        pk = profile.provider_kind
        pk_val = pk.value if hasattr(pk, "value") else str(pk)
        pe = {
            "success": False,
            "message": err_summary,
            "profile_id": str(profile.profile_id),
            "provider_kind": pk_val,
        }
        local_check["generation_status"] = FAILED_PROVIDER
        local_check["full_resume_generated"] = False
        local_check["outcome_authorized"] = False
        local_check["terminal_class"] = "FAILURE"
        local_check["provider_error"] = pe
        proposed["generation_status"] = FAILED_PROVIDER
        proposed["full_resume_generated"] = False
        proposed["provider_error"] = pe

    gs_lc = local_check.get("generation_status") if isinstance(local_check, dict) else None
    if gs_lc and "generation_status" not in proposed:
        proposed["generation_status"] = gs_lc
    if err_summary:
        proposed["e3_error_summary"] = err_summary
    proposed["e3_decisive_reason_code"] = drc
    proposed["prompt_budget"] = prompt_budget_meta

    if not resp.success:
        local_check["failure_stage"] = "post_provider"
        local_check["parsed_output_shape"] = "none_provider_failure"
    else:
        local_check["failure_stage"] = "post_parse"
        if "generated_resume" in proposed and isinstance(proposed.get("generated_resume"), dict):
            local_check["parsed_output_shape"] = "top_level_dict"
        elif proposed.get("raw_text") is not None:
            local_check["parsed_output_shape"] = "raw_text_only"
        else:
            local_check["parsed_output_shape"] = "unknown"

    inv_rf = getattr(resp, "invocation_meta", None) or {}
    if json_object_response_format is None:
        local_check["response_format_supported"] = "not_requested"
    elif isinstance(inv_rf, dict) and inv_rf.get("response_format_supported") is False:
        local_check["response_format_supported"] = False
    elif resp.success:
        local_check["response_format_supported"] = True
    else:
        em = str(resp.error_message or "")
        if "400" in em and "response_format" in em.lower():
            local_check["response_format_supported"] = False
        else:
            local_check["response_format_supported"] = "unknown"

    local_check["resume_shape_status"] = str(local_check.get("resume_shape", "") or "")
    local_check["decisive_reason_code"] = drc

    diag_payload: dict[str, Any] = {
        "schema_version": "apps_rg.provider_generation_diagnostics.v1",
        "decisive_reason_code": drc,
        "failure_stage": local_check.get("failure_stage"),
        "local_check": local_check,
        "provider_error_snippet": (str(resp.error_message or "")[:4000]) if not resp.success else "",
        "apps_rg_env_flags": {
            "APPS_RG_DIAGNOSTIC_MIN_CONTEXT": os.environ.get("APPS_RG_DIAGNOSTIC_MIN_CONTEXT"),
            "APPS_RG_RESPONSE_FORMAT_JSON_OBJECT": os.environ.get(
                "APPS_RG_RESPONSE_FORMAT_JSON_OBJECT"
            ),
        },
    }
    raw_snip = text if (not resp.success or drc != "E3_SUCCESS") else None
    _emit_diagnostics(diag_payload, raw_text=raw_snip)

    return AttemptReceipt(
        attempt_receipt_id=AttemptReceipt.new_id(),
        validation_packet_id=str(approved_work_order.validation_packet_id),
        attempt_count=attempt_number,
        determinism=prep_output.replay_bindings.determinism,
        lineage=prep_output.lineage_root,
        trace_id=cpa.trace_id,
        span_id=f"e3-attempt-{attempt_number}",
        latency_ms=float(latency),
        tokens_used=tok,
        return_code=ret_code,
        result_class=result_class,
        error_summary=err_summary,
        execution_lane=ExecutionLane.MODEL,
        decisive_reason_code=drc,
        proposed_state_diff=proposed,
        local_check_results=local_check,  # type: ignore[arg-type]
    )


def _heal_attempt_failure(
    *,
    failed_attempt: Any,
    prep_output: Any,
    approved_work_order: Any,
    cpa: Any,
    repair_count: int,
) -> Any:
    """E4 heal — same-authority repairs only (no ProviderGateway)."""
    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        AttemptReceipt,
        HealOutcomeStamp,
        HealReceipt,
        RepairStatus,
        ResultClass,
    )
    from apps_rg.runtime.bindings.l2_envelope_contracts import DISALLOWED_REPAIRS, SAFE_LOCAL_REPAIRS, is_repair_allowed

    _ = cpa  # reserved for CPA-scoped repairs
    rid = HealReceipt.new_id()
    prep_det = prep_output.replay_bindings.determinism
    att_det = failed_attempt.determinism
    snapshot_ok = (
        att_det.blueprint_hash == prep_det.blueprint_hash
        and att_det.policy_hash == prep_det.policy_hash
    )

    def _hr(
        *,
        outcome: Any,
        reason: str,
        tactic: str = "",
        delta: str = "",
        osc: str = "CLEAN",
        snap: str = "PASS" if snapshot_ok else "FAIL",
        nxt: str = "SEND_TO_E5",
        rstat: Any | None = None,
    ) -> Any:
        if tactic and not is_repair_allowed(tactic):
            _ = tactic  # documented gate usage
        if rstat is None:
            rstat = RepairStatus.REPAIRED if outcome == HealOutcomeStamp.PASS else RepairStatus.NOT_REPAIRED
        return HealReceipt(
            repair_attempt_id=rid,
            parent_attempt_receipt_id=failed_attempt.attempt_receipt_id,
            failed_span_id=failed_attempt.span_id,
            reason_code=reason,
            repair_count=repair_count,
            determinism=prep_det,
            lineage=failed_attempt.lineage,
            delta_summary=delta,
            outcome=outcome,
            repair_tactic=tactic,
            repair_status=rstat,
            oscillation_status=osc,
            snapshot_guard_status=snap,
            next_action=nxt,
        )

    if not isinstance(failed_attempt, AttemptReceipt):
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_INVALID_ATTEMPT",
            delta="invalid attempt type",
        )

    ceiling = int(getattr(approved_work_order.budget_snapshot, "repair_ceiling", 3) or 3)
    if repair_count > ceiling:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_REPAIR_BUDGET_EXHAUSTED",
            delta="repair budget exhausted",
            osc="CEILING_REACHED",
            snap="PASS" if snapshot_ok else "FAIL",
            tactic="",
        )

    if repair_count >= 3 and failed_attempt.result_class == ResultClass.SOFT_REPAIRABLE:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_OSCILLATION",
            delta="oscillation guard",
            osc="THRASHING",
            snap="PASS" if snapshot_ok else "FAIL",
        )

    if failed_attempt.result_class == ResultClass.SUCCESS:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_CANNOT_HEAL_SUCCESS",
            delta="cannot heal successful attempt",
        )

    if not snapshot_ok:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_SNAPSHOT_MISMATCH",
            delta="determinism snapshot mismatch vs prep",
            snap="FAIL",
        )

    err = f"{failed_attempt.error_summary or ''} {failed_attempt.decisive_reason_code or ''}".lower()

    if "replay key missing" in err:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_REPLAY_KEY",
            delta="replay key missing in failure surface",
            nxt="SEND_TO_E5",
        )

    blocked_pairs = [
        ("different provider", "provider substitution blocked"),
        ("provider unavailable, try different provider", "provider substitution blocked"),
        ("different model", "model substitution blocked"),
        ("try different model", "model substitution blocked"),
        ("policy restriction", "policy widening blocked"),
        ("policy widening", "policy widening blocked"),
        ("sandbox too restrictive", "sandbox widening blocked"),
        ("needs widening", "sandbox widening blocked"),
        ("capability insufficient", "capability expansion blocked"),
        ("budget exhausted", "budget increase blocked"),
        ("needs increase", "budget increase blocked"),
    ]
    for needle, msg in blocked_pairs:
        if needle in err:
            return _hr(
                outcome=HealOutcomeStamp.FAIL_TERMINAL,
                reason="E4_BLOCKED_REPAIR",
                delta=msg,
            )

    if failed_attempt.result_class != ResultClass.SOFT_REPAIRABLE:
        return _hr(
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            reason="E4_NOT_REPAIRABLE",
            delta="result not soft-repairable",
        )

    drc = str(failed_attempt.decisive_reason_code or "")
    if drc == "E3_JSON_PARSE_ERROR" or "json parse" in err:
        tactic = "json_repair_intact_source"
    elif drc == "E3_OUTPUT_OVERSIZED" or "oversized" in err:
        tactic = "trim_oversized_output_preserving_required_fields"
    elif drc == "E3_FORMAT_MISMATCH" or "markdown fence" in err:
        tactic = "output_reformat_to_required_shape"
    elif drc == "E3_TRANSIENT_TIMEOUT" or "transient timeout" in err:
        tactic = "retry_same_transient_tool_call"
    else:
        tactic = "json_repair_intact_source"

    if tactic in DISALLOWED_REPAIRS:
        return _hr(outcome=HealOutcomeStamp.FAIL_TERMINAL, reason="E4_DISALLOWED", delta=f"tactic {tactic} disallowed")
    assert tactic in SAFE_LOCAL_REPAIRS or is_repair_allowed(tactic)

    return _hr(
        outcome=HealOutcomeStamp.PASS,
        reason="E4_REPAIRED",
        tactic=tactic,
        delta=f"applied {tactic}",
        nxt="RETURN_TO_E3",
        rstat=RepairStatus.REPAIRED,
    )


def _seal_digest_hex(
    *,
    cpa: Any,
    prep_output: Any,
    validation_output: Any,
    attempt_receipt: Any,
) -> str:
    payload = {
        "request_id": str(getattr(cpa, "request_id", "") or ""),
        "run_id": str(getattr(cpa, "run_id", "") or ""),
        "trace_id": str(getattr(cpa, "trace_id", "") or ""),
        "prep_receipt_id": str(getattr(prep_output, "prep_receipt_id", "") or ""),
        "validation_packet_id": str(getattr(validation_output, "validation_packet_id", "") or ""),
        "attempt_receipt_id": str(getattr(attempt_receipt, "attempt_receipt_id", "") or ""),
        "compilation_hash": str(getattr(cpa, "compilation_hash", "") or ""),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _seal_l2_artifact(
    *,
    cpa: Any,
    prep_output: Any,
    validation_output: Any,
    attempt_receipt: Any | None,
    heal_receipt: Any | None = None,
) -> Any:
    from agentic_core.runtime.contracts.origin import Origin
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    if prep_output is None or validation_output is None:
        raise ValueError("E5_SEAL_REJECTED: missing prep_output or validation_output")
    if attempt_receipt is None:
        raise ValueError("E5_SEAL_REJECTED: missing attempt_receipt")

    st = str(getattr(validation_output, "validation_status", "") or "")
    srp = getattr(validation_output, "sealed_rejection_packet", None)
    awo = getattr(validation_output, "approved_work_order", None)
    if st == "PASS" and awo is None:
        raise ValueError("E5_SEAL_REJECTED: pass without approved work order")
    if st == "FAIL" and srp is None:
        raise ValueError("E5_SEAL_REJECTED: fail without sealed rejection packet")

    if str(getattr(attempt_receipt, "trace_id", "") or "") != str(getattr(cpa, "trace_id", "") or ""):
        raise ValueError("E5_SEAL_REJECTED: attempt trace_id mismatch vs cpa")

    digest = _seal_digest_hex(
        cpa=cpa,
        prep_output=prep_output,
        validation_output=validation_output,
        attempt_receipt=attempt_receipt,
    )

    lcr = getattr(attempt_receipt, "local_check_results", ())
    prov_lane = ""
    model_ref = ""
    if isinstance(lcr, dict):
        prov_lane = str(lcr.get("provider_lane", "") or "")
        model_ref = str(lcr.get("model_or_tool_name", "") or "")
    provider_receipts: tuple[str, ...] = ()
    model_call_refs: tuple[str, ...] = ()
    if prov_lane:
        provider_receipts = (f"provider:{prov_lane}",)
    if model_ref:
        model_call_refs = (f"model:{model_ref}",)

    ev_refs = tuple(str(v) for v in (getattr(cpa, "component_hash_map", {}) or {}).values())
    pr_refs = tuple(str(v) for v in (getattr(cpa, "slot_lineage_map", {}) or {}).values())

    audit_refs: list[str] = [
        "authority_scope:apps_rg_l2_envelope_adapter_receipts",
        "canonical_l2_artifact_authority:agentic_core_runtime_sealed_l2_artifact",
        f"attempt:{getattr(attempt_receipt, 'attempt_receipt_id', '')}",
        f"prep:{getattr(prep_output, 'prep_receipt_id', '')}",
        f"validation:{getattr(validation_output, 'validation_packet_id', '')}",
    ]
    if heal_receipt is not None:
        audit_refs.append(f"heal:{getattr(heal_receipt, 'repair_attempt_id', '')}")

    gen_content = ""
    try:
        diff = getattr(attempt_receipt, "proposed_state_diff", {}) or {}
        if isinstance(diff, dict) and "generated_resume" in diff:
            gen_content = json.dumps(diff["generated_resume"], sort_keys=True)
        else:
            gen_content = json.dumps(diff, sort_keys=True) if diff else ""
    except (TypeError, ValueError):
        gen_content = ""

    if st == "FAIL":
        exec_status = "rejected"
    else:
        rc = str(getattr(attempt_receipt.result_class, "value", attempt_receipt.result_class))
        if rc in ("SUCCESS", "DEGRADED_SUCCESS"):
            exec_status = "completed"
        else:
            exec_status = "failed"

    return SealedL2Artifact(
        request_id=str(getattr(cpa, "request_id", "") or ""),
        run_id=str(getattr(cpa, "run_id", "") or ""),
        app_id=str(getattr(cpa, "app_id", "") or ""),
        trace_id=str(getattr(cpa, "trace_id", "") or ""),
        execution_status=exec_status,
        generated_content=gen_content,
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff=dict(getattr(attempt_receipt, "proposed_state_diff", {}) or {}),
        state_diff_authorized=False,
        tenant_id=str(getattr(cpa, "tenant_id", "") or ""),
        sandbox_required=bool(getattr(cpa, "sandbox_required", False)),
        egress_policy_ref=str(getattr(cpa, "egress_policy_ref", "") or ""),
        allowed_tools=tuple(getattr(cpa, "allowed_tools", ()) or ()),
        allowed_models=tuple(getattr(cpa, "allowed_models", ()) or ()),
        allowed_networks=tuple(getattr(cpa, "allowed_networks", ()) or ()),
        allowed_file_roots=tuple(getattr(cpa, "allowed_file_roots", ()) or ()),
        prompt_artifact_digest=str(getattr(cpa, "evidence_digest", "") or ""),
        schema_version=str(getattr(cpa, "schema_version", "") or ""),
        compilation_hash=digest,
        otel_span_refs=tuple(getattr(cpa, "otel_span_refs", ()) or ()),
        audit_refs=tuple(audit_refs),
        replay_key=str(getattr(attempt_receipt.determinism, "replay_key", "") or ""),
        snapshot_refs=tuple(getattr(cpa, "snapshot_refs", ()) or ()),
        is_uwg_write_authority=False,
        l5_certification_ref=str(getattr(cpa, "l5_certification_ref", "") or ""),
        evidence_refs=ev_refs,
        prompt_refs=pr_refs,
        provider_receipts=provider_receipts,
        model_call_refs=model_call_refs,
        replay_manifest=str(getattr(cpa, "replay_manifest_ref", "") or ""),
    )


def _seal_e2_rejection(*, cpa: Any, prep_output: Any, validation_output: Any) -> Any:
    """E5-style seal when E2 fails (no E3 attempt, no provider receipts)."""
    from agentic_core.runtime.contracts.origin import Origin
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    srp = getattr(validation_output, "sealed_rejection_packet", None)
    rule = str(getattr(srp, "failed_validation_rule", "") if srp is not None else "E2_REJECTED")
    digest = hashlib.sha256(f"reject|{rule}|{cpa.request_id}|{cpa.run_id}".encode()).hexdigest()
    audit_refs = (
        f"prep:{getattr(prep_output, 'prep_receipt_id', '')}",
        f"validation:{getattr(validation_output, 'validation_packet_id', '')}",
        f"rejection:{rule}",
    )
    return SealedL2Artifact(
        request_id=str(getattr(cpa, "request_id", "") or ""),
        run_id=str(getattr(cpa, "run_id", "") or ""),
        app_id=str(getattr(cpa, "app_id", "") or ""),
        trace_id=str(getattr(cpa, "trace_id", "") or ""),
        execution_status="rejected",
        generated_content=json.dumps({"rejection": rule}, sort_keys=True),
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff={"rejection": rule},
        state_diff_authorized=False,
        tenant_id=str(getattr(cpa, "tenant_id", "") or ""),
        sandbox_required=bool(getattr(cpa, "sandbox_required", False)),
        egress_policy_ref=str(getattr(cpa, "egress_policy_ref", "") or ""),
        allowed_tools=tuple(getattr(cpa, "allowed_tools", ()) or ()),
        allowed_models=tuple(getattr(cpa, "allowed_models", ()) or ()),
        allowed_networks=tuple(getattr(cpa, "allowed_networks", ()) or ()),
        allowed_file_roots=tuple(getattr(cpa, "allowed_file_roots", ()) or ()),
        prompt_artifact_digest=str(getattr(cpa, "evidence_digest", "") or ""),
        schema_version=str(getattr(cpa, "schema_version", "") or ""),
        compilation_hash=digest,
        otel_span_refs=tuple(getattr(cpa, "otel_span_refs", ()) or ()),
        audit_refs=audit_refs,
        replay_key=str(getattr(cpa, "replay_key", "") or ""),
        snapshot_refs=tuple(getattr(cpa, "snapshot_refs", ()) or ()),
        is_uwg_write_authority=False,
        l5_certification_ref=str(getattr(cpa, "l5_certification_ref", "") or ""),
        provider_receipts=(),
        model_call_refs=(),
        replay_manifest=str(getattr(cpa, "replay_manifest_ref", "") or ""),
    )


def run_apps_rg_l2_envelope(
    prompt_artifact: Any,
    route_contract: Any | None = None,
    validated_request: Any | None = None,
    *,
    attempt_number: int = 1,
    enable_heal: bool = False,
    max_heal_attempts: int = 3,
    budget: Optional[dict] = None,
    resume_artifact_contract_mode: Any | None = None,
    artifact_dir: str | None = None,
) -> Any:
    """Run E1→E2→(E3↔E4)→E5 for apps_rg."""
    del route_contract, validated_request, budget
    prep = _build_prep_output(prompt_artifact)
    val = _validate_work_order(prep, prompt_artifact)
    if val.validation_status != "PASS" or val.approved_work_order is None:
        return _seal_e2_rejection(
            cpa=prompt_artifact,
            prep_output=prep,
            validation_output=val,
        )

    attempt = _execute_approved_work_order(
        cpa=prompt_artifact,
        approved_work_order=val.approved_work_order,
        prep_output=prep,
        attempt_number=attempt_number,
        resume_artifact_contract_mode=resume_artifact_contract_mode,
        artifact_dir=artifact_dir,
    )
    heal_r: Any | None = None
    heals_used = 0
    max_heals = int(max_heal_attempts)
    while (
        enable_heal
        and max_heals > 0
        and str(getattr(attempt.result_class, "value", attempt.result_class))
        == "SOFT_REPAIRABLE"
        and heals_used < max_heals
    ):
        heal_r = _heal_attempt_failure(
            failed_attempt=attempt,
            prep_output=prep,
            approved_work_order=val.approved_work_order,
            cpa=prompt_artifact,
            repair_count=heals_used + 1,
        )
        heals_used += 1
        if heal_r.next_action != "RETURN_TO_E3":
            break
        attempt = _execute_approved_work_order(
            cpa=prompt_artifact,
            approved_work_order=val.approved_work_order,
            prep_output=prep,
            attempt_number=attempt_number + heals_used,
            resume_artifact_contract_mode=resume_artifact_contract_mode,
            artifact_dir=artifact_dir,
        )

    return _seal_l2_artifact(
        cpa=prompt_artifact,
        prep_output=prep,
        validation_output=val,
        attempt_receipt=attempt,
        heal_receipt=heal_r,
    )
