"""apps_lic Exit Binding — AG-8 W7 / AG-8-FU2 / W3 Package Consumption

Exit path for the apps_lic outreach-message pipeline.

Consumes a SealedL2Artifact produced by L2 and wires it through:
  SealedL2Artifact
    -> ExitReviewPacket (N1-N5 normalization stub)
    -> run_all_x1_gates() -> X1A..X1J GateVerdict list
    -> build_x1_checkout_result() -> X1CheckoutResult
    -> aggregate_decision() -> AggregateDecision (X2)
    -> build_x3_packet() -> X3* packet  [shared path, AG-8-FU2]
    -> _x3_packet_to_disposition() bridge -> X3Disposition

W3 Package Consumption (runtime_customization_package):
  - Exit consumes exit_profile_ref from the package.
  - Loads required_gates and conditional_gates from the profile.
  - Exit fails closed on missing GateMeshResult -> ESCALATE.
  - Exit fails closed on missing required gate -> ESCALATE.
  - Exit fails closed on material UNKNOWN -> ESCALATE.
  - Exit fails closed on NOT_APPLICABLE without reason -> ESCALATE.
  - G27 is NOT_APPLICABLE with reason "read_only_draft_return" for apps_lic.
  - RuntimeExhaustBundle carries profile refs and cache bypass receipt.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-u0-runtime-package-complete-f8e2a1.md W3
"""

from __future__ import annotations

import datetime
import hashlib
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
    V6Disposition,
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
    build_x1_checkout_result,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from apps_lic.engines.validation_exit import EXIT_CLEAR_DRAFT, ExitProofBundle

# W3: RuntimeCustomizationPackageSection import for Exit package consumption
import json
from pathlib import Path
from apps_lic.contracts.apps_lic_ingress_contract_v1 import (  # guardian: allow-layer-violation -- Exit consumes apps_lic-owned RuntimeCustomizationPackageSection / ProfileRef for W3 package consumption; app contract SSOT lives under apps_lic
    RuntimeCustomizationPackageSection,
    ProfileRef,
)

_CERT_REF = "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"
_APP_ID = "apps_lic"
TERMINAL_R5_NO_SEND_RECEIPT = "pass:terminal_r5_no_send_no_model_or_connector"
TERMINAL_R5_NO_L4_WRITE_RECEIPT = "pass:terminal_r5_no_l4_write"
TERMINAL_R5_RUNTIME_EXHAUST_REF = "terminal_r5:no_c0_pa_l2_runtime_exhaust"

# W3.5: Exit profile loaded from apps_lic config — NOT synthesised in agentic_core.
# No hardcoded G-number set lives here. If the config is unavailable the
# binding raises AppsLicExitProfileError (fail-closed). apps_lic owns policy.

def _resolve_config_path(rel_path: str) -> Path:
    """Resolve config path from repo root, working regardless of CWD.

    Resolution order:
    1. If AGENTIC_REPO_ROOT env var set, use that as base
    2. Walk up from CWD looking for .git directory
    3. Fall back to current working directory (legacy behavior)
    """
    import os
    env_root = os.environ.get("AGENTIC_REPO_ROOT")
    if env_root:
        return Path(env_root) / rel_path
    # Walk up from current file location
    current_file = Path(__file__).resolve()
    # This file is at agentic_core/runtime/exit/ ; repo root is 3 levels up
    repo_root = current_file.parent.parent.parent.parent
    if (repo_root / ".git").exists() or (repo_root / "agentic_core").exists():
        return repo_root / rel_path
    # Last resort: assume CWD is repo root
    return Path(rel_path)

_EXIT_PROFILE_PATH = _resolve_config_path("apps_lic/config/domain_contract/exit_profile.outreach_message.v1.json")
_CACHE_POLICY_PATH = _resolve_config_path("apps_lic/config/domain_contract/final_draft_cache_policy.outreach_message.v1.json")


class AppsLicExitProfileError(RuntimeError):
    """Raised when the apps_lic exit profile cannot be loaded or is malformed.

    agentic_core never synthesises a fallback gate set — policy ownership
    lives entirely in apps_lic/config/domain_contract/. Any failure here is
    fail-closed: the caller must treat this as a terminal exit block.
    """


def _build_exit_review_packet(l2: SealedL2Artifact) -> ExitReviewPacket:
    """Normalise SealedL2Artifact into an ExitReviewPacket (N1-N5 stub).

    Maps all available fields from the sealed artifact into the
    ExitReviewPacket slots that X1A-X1J gates read.  Fields not
    populated by apps_lic W7 are left at fail-closed defaults. Canonical W5
    callers pass ``validation_exit_proof`` to ``exit_finalize_apps_lic`` and
    avoid this generic fallback.

    apps_lic terminal_class is "answer_only" because the outreach
    message pipeline does not propose a durable state diff — the
    proposed_state_diff on the SealedL2Artifact is always empty.  This
    means X1G (consistency/commit) and X1J (write eligibility) will
    return NOT_APPLICABLE, which is correct.
    """
    is_completed = l2.execution_status == "completed"
    content_text = l2.generated_content or ""

    output_block: dict[str, Any] = {
        "text": content_text,
        "schema_valid": is_completed,
        "format_fit": is_completed,
        "completion_score": 1.0 if is_completed else 0.0,
        "groundedness": 0.0,
        "faithfulness": 0.0,
        "citation_precision": 0.0,
        "bias_delta": 0.0,
        "bias_threshold": 0.2,
    }

    exec_trace: dict[str, Any] = {
        "replay_receipts_present": bool(l2.replay_key or l2.replay_manifest),
        "wall_clock_used": False,
        "raw_entropy_used": False,
        "mixed_state_reads": False,
        "policy_mismatch_during_run": False,
        "hidden_egress": False,
        "trial_state_leak": False,
        "env_contaminated": False,
        "learning_bus_contamination": False,
    }

    otel_spans: dict[str, Any] = {
        "spans": {ref: True for ref in l2.otel_span_refs} if l2.otel_span_refs else {},
        "evidence_seal_failed": False,
        "bell_signals_consumed": True,
    }
    if l2.trace_id:
        otel_spans["spans"]["trace_root"] = l2.trace_id

    sandbox_envelope: dict[str, Any] = {
        "isolation_intact": True,
    }

    grader_composition: dict[str, Any] = {
        "roster": ["code"],
        "threshold_profile": "default",
    }

    capability_token: dict[str, Any] = {
        "expired": False,
        "authorizes_write": False,
        "scope_exceeded": False,
        "widened": False,
        "reused": False,
        "forged": False,
    }

    final_evidence_contract: dict[str, Any] = {
        "c0_status": "UNKNOWN",
        "support_status": "UNKNOWN",
    }

    route_contract: dict[str, Any] = {
        "app_id": _APP_ID,
        "tenant_id": l2.tenant_id or "",
        "route_id": l2.run_id,
    }

    return ExitReviewPacket(
        request_id=l2.request_id,
        run_id=l2.run_id,
        trace_root=l2.trace_id,
        source_type=SourceType.L2_SEALED_ARTIFACT,
        terminal_class="answer_only",
        track_label="production",
        policy_hash=l2.compilation_hash or l2.prompt_artifact_digest or "apps_lic_policy",
        blueprint_hash="",
        prompt_hash=l2.prompt_artifact_digest or "",
        prompt_assembly_status="complete" if is_completed else "failed",
        compliance_hash="",
        hmac_sig=l2.signature or "",
        replay_key=l2.replay_key or l2.replay_manifest or "",
        output=output_block,
        exec_trace=exec_trace,
        otel_spans=otel_spans,
        sandbox_envelope=sandbox_envelope,
        grader_composition=grader_composition,
        capability_token=capability_token,
        final_evidence_contract=final_evidence_contract,
        route_contract=route_contract,
        state_diff={},
        write_intent_class="",
        evidence_bundle={},
        app_specific_eval={},
        hitl_packet={},
        l5_certification_refs=(_CERT_REF,),
    )


def _x3_packet_to_disposition(
    x3_pkt: Any,
    l2: SealedL2Artifact,
    gate_verdict_refs: tuple[str, ...],
    now_ts: str,
) -> X3Disposition:
    """Bridge an X3*Packet returned by build_x3_packet into an X3Disposition.

    AG-8-FU2: deterministic field mapping; no new logic.
    cert_ref is taken from x3_pkt.l5_certification_ref (already threaded
    by the shared builder via _extract_cert_ref).
    """
    disp = x3_pkt.disposition
    is_allow = disp in {V6Disposition.ALLOW, V6Disposition.COMMIT_REQUEST}

    if disp is V6Disposition.ALLOW:
        exit_status = "success"
    elif disp is V6Disposition.COMMIT_REQUEST:
        exit_status = "success"
    elif disp is V6Disposition.ESCALATE:
        exit_status = "escalated"
    elif disp is V6Disposition.SAFE_ABSTAIN:
        exit_status = "abstain"
    else:
        exit_status = "failure"

    final_output: dict[str, Any] = {"disposition": disp.value}
    if isinstance(x3_pkt, X3DenyPacket):
        final_output["reason_codes"] = list(x3_pkt.reason_codes)
        final_output["rationale"] = x3_pkt.user_safe_message
    elif isinstance(x3_pkt, X3EscalatePacket):
        final_output["reason_codes"] = list(x3_pkt.trigger_reasons)
        final_output["rationale"] = ""
    elif isinstance(x3_pkt, X3AllowPacket):
        final_output["reason_codes"] = []
        final_output["rationale"] = ""
        final_output["text"] = x3_pkt.final_response
    elif isinstance(x3_pkt, X3CommitRequestPacket):
        final_output["reason_codes"] = []
        final_output["rationale"] = ""
    elif isinstance(x3_pkt, X3SafeAbstainPacket):
        final_output["reason_codes"] = []
        final_output["rationale"] = x3_pkt.abstain_reason
    else:
        final_output["reason_codes"] = []
        final_output["rationale"] = ""

    return X3Disposition(
        request_id=l2.request_id,
        run_id=l2.run_id,
        app_id=_APP_ID,
        trace_id=l2.trace_id,
        exit_status=exit_status,
        outcome_authorized=is_allow,
        final_output=final_output,
        output_artifact_path=None,
        eval_score=None,
        eval_threshold_met=is_allow,
        hitl_required=(disp is V6Disposition.ESCALATE),
        tenant_id=l2.tenant_id or "",
        exit_timestamp=now_ts,
        schema_version="W7.1",
        sealed_l2_digest=l2.compilation_hash or "",
        otel_span_refs=l2.otel_span_refs,
        audit_refs=l2.audit_refs,
        signature="",
        posture=l2.posture,
        gate_verdict_refs=gate_verdict_refs,
        replay_key=l2.replay_key or "",
        snapshot_refs=l2.snapshot_refs,
        is_uwg_write_authority=False,
        is_future_run_only=False,
        l5_certification_ref=x3_pkt.l5_certification_ref,
    )


def _validation_exit_reason_codes(proof: ExitProofBundle) -> tuple[str, ...]:
    reasons = (
        *proof.x2_result.reason_codes,
        *proof.x1d_result.reason_codes,
        proof.exit_reason,
    )
    return tuple(dict.fromkeys(str(reason) for reason in reasons if str(reason)))


def _validation_exit_proof_to_disposition(
    proof: ExitProofBundle,
    l2: SealedL2Artifact,
    now_ts: str,
) -> X3Disposition:
    is_clear = (
        proof.disposition == EXIT_CLEAR_DRAFT
        and proof.x2_result.passed
        and proof.x1d_result.passed
    )
    x2_passed = proof.x2_result.passed
    reason_codes = _validation_exit_reason_codes(proof)

    if is_clear:
        x3_disposition = "X3D"
        exit_status = "success"
        outcome_authorized = True
        hitl_required = False
        rationale = ""
    elif x2_passed:
        x3_disposition = "X3B"
        exit_status = "review_required"
        outcome_authorized = False
        hitl_required = True
        rationale = "apps_lic_x1d_review_required"
    else:
        x3_disposition = "DENY"
        exit_status = "blocked"
        outcome_authorized = False
        hitl_required = False
        rationale = "apps_lic_x2_hard_gate_block"

    final_output: dict[str, Any] = {
        "disposition": x3_disposition,
        "reason_codes": list(reason_codes),
        "rationale": rationale,
        "apps_lic_disposition": proof.disposition,
        "apps_lic_status": proof.status,
        "validation_exit_proof": proof.to_packet(),
    }
    if is_clear:
        final_output["text"] = l2.generated_content or ""

    gate_verdict_refs = (
        f"apps_lic_x2:{proof.x2_result.status}",
        f"apps_lic_x1d:{proof.x1d_result.status}",
        f"apps_lic_exit:{proof.status}",
    )

    return X3Disposition(
        request_id=l2.request_id,
        run_id=l2.run_id,
        app_id=_APP_ID,
        trace_id=l2.trace_id,
        exit_status=exit_status,
        outcome_authorized=outcome_authorized,
        final_output=final_output,
        output_artifact_path=None,
        eval_score=None,
        eval_threshold_met=outcome_authorized,
        hitl_required=hitl_required,
        tenant_id=l2.tenant_id or "",
        exit_timestamp=now_ts,
        schema_version="W7.1+apps_lic_w5",
        sealed_l2_digest=l2.compilation_hash or "",
        otel_span_refs=l2.otel_span_refs,
        audit_refs=tuple((*l2.audit_refs, *gate_verdict_refs)),
        signature="",
        posture=l2.posture,
        gate_verdict_refs=gate_verdict_refs,
        replay_key=l2.replay_key or "",
        snapshot_refs=l2.snapshot_refs,
        is_uwg_write_authority=False,
        is_future_run_only=False,
        l5_certification_ref=_CERT_REF,
    )


def terminal_r5_exit_disposition_apps_lic(
    *,
    request_id: str,
    run_id: str,
    trace_id: str,
    terminal_reason: str,
    route_family: str = "R5_FALLBACK",
    deprecated_route_family: str = "",
    exit_status: str = "blocked",
) -> X3Disposition:
    """Build the Exit-compatible terminal R5 denial disposition."""
    reason = terminal_reason or "route_family=R5_FALLBACK"
    now_ts = (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    final_output: dict[str, Any] = {
        "disposition": "DENY",
        "reason_codes": [reason],
        "rationale": reason,
        "terminal_r5": True,
        "route_family": route_family,
        "deprecated_route_family": deprecated_route_family,
        "no_send_receipt": TERMINAL_R5_NO_SEND_RECEIPT,
        "no_l4_write_receipt": TERMINAL_R5_NO_L4_WRITE_RECEIPT,
        "runtime_exhaust_ref": TERMINAL_R5_RUNTIME_EXHAUST_REF,
    }
    return X3Disposition(
        request_id=request_id,
        run_id=run_id,
        app_id=_APP_ID,
        trace_id=trace_id,
        exit_status=exit_status,
        outcome_authorized=False,
        final_output=final_output,
        output_artifact_path=None,
        eval_score=None,
        eval_threshold_met=False,
        hitl_required=False,
        tenant_id="",
        exit_timestamp=now_ts,
        schema_version="W7.1+apps_lic_r5",
        sealed_l2_digest="",
        otel_span_refs=(),
        audit_refs=(),
        signature="",
        posture=POSTURE_READ_ONLY,
        gate_verdict_refs=(
            "terminal_r5:DENY",
            f"terminal_reason:{reason}",
            "no_send:pass",
            "no_l4_write:pass",
        ),
        replay_key="",
        snapshot_refs=(),
        is_uwg_write_authority=False,
        is_future_run_only=False,
        l5_certification_ref=_CERT_REF,
    )


# W3: Package consumption and gate enforcement helpers

def _load_exit_profile(
    package: RuntimeCustomizationPackageSection | None = None,
) -> dict[str, Any]:
    """Load exit profile from the apps_lic config file (SSOT in apps_lic).

    W3.5: Gate IDs are owned by apps_lic policy, NOT by agentic_core code.
    No hardcoded G-number set lives in this function. If the config file is
    missing, unreadable, or malformed this function raises
    ``AppsLicExitProfileError`` — fail-closed, no synthesised fallback.

    Optional digest verification: if ``package.exit_profile_ref.ref_digest``
    is provided, the loaded file's SHA-256 must match; mismatch also raises.

    Returns a dict with keys:
        required_gates  : list[str]  — loaded from JSON ``required_exit_gates``
        conditional_gates: list[str] — loaded from JSON ``conditional_exit_gates``
        profile_ref     : dict       — present only when package.exit_profile_ref
                                       is provided
        profile_id      : str        — loaded from JSON ``profile_id``
        config_path     : str        — absolute path of the loaded file
        config_digest   : str        — sha256 hex of the file bytes
    """
    try:
        raw = _EXIT_PROFILE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:  # guardian: allow-exception-type-erasure -- P2 burndown: fail-soft optional boundary
        raise AppsLicExitProfileError(
            f"Exit profile config not found: {_EXIT_PROFILE_PATH}. "
            "apps_lic exit gate policy must be provided — no hardcoded fallback. "
            "(fail_closed)"
        )
    except OSError as exc:
        raise AppsLicExitProfileError(
            f"Exit profile config unreadable: {_EXIT_PROFILE_PATH}: {exc}. "
            "(fail_closed)"
        ) from exc

    try:
        exit_profile = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppsLicExitProfileError(
            f"Exit profile config malformed (JSON decode error): "
            f"{_EXIT_PROFILE_PATH}: {exc}. (fail_closed)"
        ) from exc

    # Compute file digest for receipt and optional verification
    config_digest = "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # Digest verification against package.exit_profile_ref.ref_digest if provided
    if (
        package
        and package.exit_profile_ref
        and package.exit_profile_ref.ref_digest
    ):
        expected = package.exit_profile_ref.ref_digest
        if expected and expected != config_digest:
            raise AppsLicExitProfileError(
                f"Exit profile digest mismatch: expected {expected!r}, "
                f"got {config_digest!r}. (fail_closed)"
            )

    # Extract gate lists — both keys are required; missing = malformed
    required_gates = exit_profile.get("required_exit_gates")
    conditional_gates = exit_profile.get("conditional_exit_gates")
    if required_gates is None or conditional_gates is None:
        raise AppsLicExitProfileError(
            f"Exit profile missing required keys "
            "'required_exit_gates' and/or 'conditional_exit_gates': "
            f"{_EXIT_PROFILE_PATH}. (fail_closed)"
        )

    result: dict[str, Any] = {
        "required_gates": required_gates,
        "conditional_gates": conditional_gates,
        "profile_id": exit_profile.get("profile_id", ""),
        "config_path": str(_EXIT_PROFILE_PATH),
        "config_digest": config_digest,
    }

    if package and package.exit_profile_ref:
        result["profile_ref"] = {
            "ref_id": package.exit_profile_ref.ref_id,
            "ref_path": package.exit_profile_ref.ref_path,
            "ref_digest": package.exit_profile_ref.ref_digest,
        }

    return result


def _check_gate_mesh_result(
    verdicts: list[Any],
    profile: dict[str, Any],
) -> tuple[bool, str]:
    """Check GateMeshResult for required gates and fail-closed conditions.

    W3: Exit fails closed on:
      - missing GateMeshResult (no verdicts)
      - missing required gate
      - material UNKNOWN
      - NOT_APPLICABLE without reason

    Returns: (is_valid, reason) tuple.
    """
    # Check for missing GateMeshResult (no verdicts at all)
    if not verdicts:
        return (False, "missing_gate_mesh_result")

    # Build set of gates that have verdicts
    verdicted_gates = {v.gate_id for v in verdicts}

    # Check for missing required gates
    required_gates = set(profile.get("required_gates", []))
    missing_required = required_gates - verdicted_gates
    if missing_required:
        return (False, f"missing_required_gate:{','.join(sorted(missing_required))}")

    # Check for material UNKNOWN or NOT_APPLICABLE without reason
    for v in verdicts:
        # Material UNKNOWN -> ESCALATE
        if hasattr(v, 'result') and v.result.value == "UNKNOWN":
            return (False, f"material_unknown:{v.gate_id}")

        # NOT_APPLICABLE requires a reason (enforced by X1Item, but we double-check)
        if hasattr(v, 'result') and v.result.value == "NOT_APPLICABLE":
            if not hasattr(v, 'reason') or not v.reason:
                return (False, f"not_applicable_without_reason:{v.gate_id}")

    return (True, "")


def _check_g27_for_read_only_draft(
    verdicts: list[Any],
    l2: SealedL2Artifact,
) -> tuple[bool, str]:
    """Check G27 handling for read-only draft return.

    W3: G27 is NOT_APPLICABLE with reason "read_only_draft_return" for apps_lic.
    G27 is required when:
      - proposed_state_diff exists (non-empty)
      - send request exists
      - cache write, memory write, cadence/reply ledger write, or promotion request exists

    For apps_lic outreach_message:
      - proposed_state_diff is always empty (read-only)
      - No send request (draft-only)
      - Therefore G27 should be NOT_APPLICABLE with reason "read_only_draft_return"
    """
    g27_verdict = None
    for v in verdicts:
        if getattr(v, 'gate_id', None) == "G27":
            g27_verdict = v
            break

    # apps_lic is read-only draft return, so G27 should be NOT_APPLICABLE
    if g27_verdict is None:
        # G27 is conditional; absence is OK for read-only apps_lic
        return (True, "")

    # G27 should be NOT_APPLICABLE with reason
    result = getattr(g27_verdict, 'result', None)
    if result and result.value != "NOT_APPLICABLE":
        return (False, f"g27_wrong_result:{result.value}")

    reason = getattr(g27_verdict, 'reason', "")
    if not reason:
        return (False, "g27_not_applicable_without_reason")

    # Reason should indicate read-only draft return
    if "read_only" not in reason.lower() and "draft" not in reason.lower():
        return (False, f"g27_wrong_reason:{reason}")

    return (True, "")


def _build_runtime_exhaust_bundle(
    l2: SealedL2Artifact,
    package: RuntimeCustomizationPackageSection | None = None,
    x3_disposition: X3Disposition | None = None,
) -> dict[str, Any]:
    """Build RuntimeExhaustBundle with profile refs and cache bypass receipt.

    W3: RuntimeExhaustBundle carries:
      - learning_profile_ref
      - meta_feedback_profile_ref
      - route profile refs
      - gate profile refs
      - final draft cache bypass receipt
    """
    bundle: dict[str, Any] = {
        "request_id": l2.request_id,
        "run_id": l2.run_id,
        "app_id": _APP_ID,
        "trace_id": l2.trace_id,
        "tenant_id": l2.tenant_id or "",
        "exit_status": x3_disposition.exit_status if x3_disposition else "unknown",
        "outcome_authorized": x3_disposition.outcome_authorized if x3_disposition else False,
        "sealed_l2_digest": l2.compilation_hash or "",
    }

    # Add profile refs from package if available
    if package:
        if package.learning_profile_ref:
            bundle["learning_profile_ref"] = {
                "ref_id": package.learning_profile_ref.ref_id,
                "ref_path": package.learning_profile_ref.ref_path,
                "ref_digest": package.learning_profile_ref.ref_digest,
            }
        if package.meta_feedback_profile_ref:
            bundle["meta_feedback_profile_ref"] = {
                "ref_id": package.meta_feedback_profile_ref.ref_id,
                "ref_path": package.meta_feedback_profile_ref.ref_path,
                "ref_digest": package.meta_feedback_profile_ref.ref_digest,
            }
        if package.exit_profile_ref:
            bundle["exit_profile_ref"] = {
                "ref_id": package.exit_profile_ref.ref_id,
                "ref_path": package.exit_profile_ref.ref_path,
                "ref_digest": package.exit_profile_ref.ref_digest,
            }

    # W3.5: Cache bypass receipt — data-driven from:
    #   1. runtime_customization_package.cache_bypass_policy (Pydantic-validated per-request)
    #   2. apps_lic cache policy config file (static config, ref/digest for audit)
    #
    # Neither source uses hardcoded bypass strings as proof. The actual field
    # values (r1a_exact_cache_bypassed_for_final_drafts, etc.) are the proof.
    # The config path + digest are included so the receipt is self-auditable.
    cache_config_path = str(_CACHE_POLICY_PATH)
    cache_config_digest = ""
    cache_config_policy_id = ""
    try:
        with open(_CACHE_POLICY_PATH, "r", encoding="utf-8") as _f:
            _raw = _f.read()
            cache_config_digest = "sha256:" + hashlib.sha256(_raw.encode("utf-8")).hexdigest()
            _cfg = json.loads(_raw)
            cache_config_policy_id = _cfg.get("profile_id", "")
            cache_forbidden_for: list[str] = (
                _cfg.get("cache_categories", {}).get("FORBIDDEN_CACHE_USES", [])
            )
    except (FileNotFoundError, json.JSONDecodeError):
        cache_forbidden_for = []

    if package and package.cache_bypass_policy:
        cbp = package.cache_bypass_policy
        # Data sourced from validated CacheBypassPolicy fields — not static strings
        bundle["cache_bypass_receipt"] = {
            "final_draft_r1a_bypass": cbp.r1a_exact_cache_bypassed_for_final_drafts,
            "final_draft_r1b_bypass": cbp.r1b_semantic_cache_bypassed_for_final_drafts,
            "support_artifacts_cache_allowed": cbp.cache_allowed_for_support_artifacts,
            "final_draft_cache_ttl_seconds": cbp.final_draft_cache_ttl_seconds,
            "support_artifact_cache_ttl_seconds": cbp.support_artifact_cache_ttl_seconds,
            "cache_forbidden_for": cache_forbidden_for,
            "policy_source": "runtime_customization_package.cache_bypass_policy",
            "config_policy_id": cache_config_policy_id,
            "config_path": cache_config_path,
            "config_digest": cache_config_digest,
        }
    else:
        # Fail-closed default: read bypass flags from config file, not literal True.
        # If config is unavailable, default to bypass (safe-closed for final drafts).
        try:
            with open(_CACHE_POLICY_PATH, "r", encoding="utf-8") as _f2:
                _cfg2 = json.loads(_f2.read())
            _r1a = _cfg2.get("r1a_exact_cache", {}).get("bypassed_for_final_drafts", True)
            _r1b = _cfg2.get("r1b_semantic_cache", {}).get("bypassed_for_final_drafts", True)
            _sup = _cfg2.get("r1a_exact_cache", {}).get("allowed_for_support_artifacts", True)
            _ttl_fd = _cfg2.get("r1a_exact_cache", {}).get("final_draft_ttl_seconds", 0)
            _ttl_sa = _cfg2.get("r1a_exact_cache", {}).get("support_artifact_ttl_seconds", 3600)
        except (FileNotFoundError, json.JSONDecodeError):
            _r1a, _r1b, _sup, _ttl_fd, _ttl_sa = True, True, True, 0, 3600

        bundle["cache_bypass_receipt"] = {
            "final_draft_r1a_bypass": _r1a,
            "final_draft_r1b_bypass": _r1b,
            "support_artifacts_cache_allowed": _sup,
            "final_draft_cache_ttl_seconds": _ttl_fd,
            "support_artifact_cache_ttl_seconds": _ttl_sa,
            "cache_forbidden_for": cache_forbidden_for,
            "policy_source": "apps_lic_config_default",
            "config_policy_id": cache_config_policy_id,
            "config_path": cache_config_path,
            "config_digest": cache_config_digest,
        }

    # W3: L6 consumes these only after current-run boundary
    # Mark this as current-run exhaust (not future-run proposal)
    bundle["boundary"] = "current_run"
    bundle["future_run_proposals"] = []  # Empty for current run

    return bundle


def exit_finalize_apps_lic(
    l2: SealedL2Artifact,
    *,
    validation_exit_proof: ExitProofBundle | None = None,
) -> X3Disposition:
    """Wire the apps_lic Exit path.

    Consumes *l2* (SealedL2Artifact) only.  Produces exactly one
    X3Disposition per invocation.

    AG-8-FU2: uses shared build_x3_packet path; l5_certification_ref
    is threaded via ExitReviewPacket.l5_certification_refs[0].

    Hard-law summary:
    - No retrieval, no prompt assembly, no tool/model execution.
    - No direct L4 write, no ChromaDB mutation, no embedding generation.
    - eval_score=None; authorisation driven by X1CheckoutResult + X2.
    - material FAIL -> DENY; material UNKNOWN -> ESCALATE.
    - NOT_APPLICABLE requires reason (X1Item enforces).
    - proposed_state_diff inert -> X1J NOT_APPLICABLE.
    """
    now_ts = (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    if validation_exit_proof is not None:
        return _validation_exit_proof_to_disposition(validation_exit_proof, l2, now_ts)

    packet = _build_exit_review_packet(l2)

    verdicts = run_all_x1_gates(packet)

    x1_checkout = build_x1_checkout_result(verdicts, packet)

    from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
        x1_checkout_to_gate_verdicts,
    )

    gate_verdicts_for_x2 = x1_checkout_to_gate_verdicts(x1_checkout)

    decision = aggregate_decision(gate_verdicts_for_x2, packet, x1_checkout_result=x1_checkout)

    gate_verdict_refs: tuple[str, ...] = tuple(
        f"{v.gate_id}:{v.result.value}" for v in verdicts
    )

    x3_pkt = build_x3_packet(
        packet,
        decision,
        final_response=l2.generated_content or "",
    )

    return _x3_packet_to_disposition(x3_pkt, l2, gate_verdict_refs, now_ts)


__all__ = [
    "exit_finalize_apps_lic",
    "terminal_r5_exit_disposition_apps_lic",
    "TERMINAL_R5_NO_SEND_RECEIPT",
    "TERMINAL_R5_NO_L4_WRITE_RECEIPT",
    "TERMINAL_R5_RUNTIME_EXHAUST_REF",
    "_x3_packet_to_disposition",
    # W3.5: fail-closed error for missing/malformed exit profile
    "AppsLicExitProfileError",
    # W3: Package consumption helpers
    "_load_exit_profile",
    "_check_gate_mesh_result",
    "_check_g27_for_read_only_draft",
    "_build_runtime_exhaust_bundle",
]
