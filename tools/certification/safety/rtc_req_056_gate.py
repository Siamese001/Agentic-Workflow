"""RTC-REQ-056 consensus-jury panel-attestation gate.

Central decision function consumed by:
  - ``scripts/compose_semantic_cache_subclaims.py``
  - ``scripts/verify_semantic_cache_certification.py``
  - ``scripts/verify_runtime_certification_acceptance.py``
  - ``tools/certification/evidence/probe_integrated_runtime_safe_reuse.py``
  - Tests.

Invariant: these consumers MUST delegate to ``validate_panel_attestation``
for the RTC-REQ-056 decision. They MUST NOT re-implement the gate logic
locally. Divergent copies of these rules are a §23 source-of-truth
violation.

Per operator directive 2026-05-01 13:39 UTC-04:00.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.certification.safety.rtc_req_056_panel import (
    ATTESTATION_SCHEMA_VERSION,
    CERTIFICATION_SCOPE,
    CONTROL_SURFACE,
    JUDGE_MODE,
    PURPOSE,
    QUORUM_RULE,
    REJECTED_MODELS_FOR_CERT,
    REJECTED_PROVIDERS_FOR_CERT,
    REQUIRED_JURORS,
    REQUIRED_JUROR_COUNT,
    RejectReason,
    classify_healing_tier_for_reject,
    classify_rejected_model,
    classify_rejected_provider,
    get_juror_by_family,
    is_registered_model,
    panel_artifact_path,
)


@dataclass(frozen=True)
class PanelGateResult:
    """Outcome of panel-attestation validation.

    Attributes:
        accepted: True iff the panel attestation certifies RTC-REQ-056.
            A False value plus an empty ``reason_codes`` indicates an
            internal validation error (defensive).
        reason_codes: Ordered list of ``RejectReason.*`` or
            ``INFRASTRUCTURE_GAP_*`` codes that blocked acceptance.
            Stable ordering: structural codes first, then per-juror.
        messages: Human-readable audit messages paired 1:1 with
            ``reason_codes``.
        row_status: Suggested RTC-REQ-056 row status
            ("ACCEPTED" | "PENDING" | "PARTIAL" | "BLOCKED" |
            "INFRASTRUCTURE_GAP").
    """

    accepted: bool
    reason_codes: tuple[str, ...]
    messages: tuple[str, ...]
    row_status: str


_REQUIRED_TOP_LEVEL_FIELDS = (
    "attestation_schema_version",
    "certification_scope",
    "control_surface",
    "purpose",
    "judge_mode",
    "quorum_rule",
    "required_juror_count",
    "invoked_juror_count",
    "final_consensus_verdict",
    "final_safe_reuse_allow",
    "final_x3_disposition",
    "rubric_hash_sha256",
    "request_hash_sha256",
    "cache_candidate_hash_sha256",
    "panel_response_hash_sha256",
    "provider_panel_match_status",
    "model_panel_match_status",
    "mock_safe_used_any",
    "deterministic_proof_stage_used_any",
    "created_at_utc",
    "jurors",
)

_REQUIRED_JUROR_FIELDS = (
    "juror_id",
    "control_surface",
    "provider_family",
    "provider",
    "model_id",
    "target_provider_family",
    "target_provider",
    "target_model_id",
    "provider_match_status",
    "model_match_status",
    "approved_provider",
    "verdict",
    "confidence",
    "latency_ms",
    "response_hash_sha256",
    "parse_status",
    "timeout_count",
    "error_count",
    "unknown_count",
    "unsafe_count",
    "parse_fail_count",
    "mock_safe_used",
    "deterministic_proof_stage_used",
    "raw_output_retention_mode",
)


def _append_violation(
    codes: list[str], msgs: list[str], code: str, message: str
) -> None:
    codes.append(code)
    msgs.append(f"{code}: {message}")


def validate_panel_attestation(
    attestation: dict[str, Any] | None,
) -> PanelGateResult:
    """Validate a consensus-jury panel attestation payload.

    Returns PanelGateResult.accepted=True ONLY when every hard gate passes.
    Missing attestation -> REJECT_MISSING_PANEL_ATTESTATION.
    """
    codes: list[str] = []
    msgs: list[str] = []

    if attestation is None:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_PANEL_ATTESTATION,
            "panel attestation payload is None (file missing or unreadable)",
        )
        return PanelGateResult(
            accepted=False,
            reason_codes=tuple(codes),
            messages=tuple(msgs),
            row_status="BLOCKED",
        )

    # ---- Control-surface gate (FIRST, before any other schema check) ----
    # Per operator directive 2026-05-01 14:15 UTC-04:00. Rejects any
    # healing-origin document before any structural/quorum logic runs,
    # so the specific reason code (e.g. REJECT_QWEN_HEALING_...) surfaces
    # even when other gates would also fire.
    top_surface = attestation.get("control_surface")
    top_purpose = attestation.get("purpose")
    top_healing_tier = attestation.get("healing_tier")  # healing docs set this

    surface_reject = classify_healing_tier_for_reject(
        control_surface=top_surface,
        healing_tier=top_healing_tier,
        model_id=None,
    )
    if surface_reject is not None:
        _append_violation(
            codes, msgs, surface_reject,
            f"top-level control_surface={top_surface!r} "
            f"(healing_tier={top_healing_tier!r})",
        )
        # Short-circuit: a healing or missing-surface document cannot be
        # salvaged by any later check. Emit ONLY the surface reject.
        return PanelGateResult(
            accepted=False,
            reason_codes=tuple(codes),
            messages=tuple(msgs),
            row_status="BLOCKED",
        )

    # purpose must accompany surface for schema v3
    if top_purpose != PURPOSE:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_CONTROL_SURFACE_MISMATCH,
            f"top-level purpose={top_purpose!r} expected {PURPOSE!r}",
        )

    # ---- Structural fields ----
    for f in _REQUIRED_TOP_LEVEL_FIELDS:
        if f not in attestation:
            _append_violation(
                codes, msgs,
                RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
                f"missing top-level field {f!r}",
            )

    # Scope + mode + quorum must match
    if attestation.get("certification_scope") != CERTIFICATION_SCOPE:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_PANEL_ATTESTATION,
            f"certification_scope={attestation.get('certification_scope')!r} "
            f"expected {CERTIFICATION_SCOPE!r}",
        )
    if attestation.get("judge_mode") != JUDGE_MODE:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056,
            f"judge_mode={attestation.get('judge_mode')!r} expected {JUDGE_MODE!r}",
        )
    if attestation.get("quorum_rule") != QUORUM_RULE:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_QUORUM_RULE,
            f"quorum_rule={attestation.get('quorum_rule')!r} "
            f"expected {QUORUM_RULE!r}",
        )

    if attestation.get("required_juror_count") != REQUIRED_JUROR_COUNT:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_JUROR,
            f"required_juror_count={attestation.get('required_juror_count')} "
            f"expected {REQUIRED_JUROR_COUNT}",
        )
    if attestation.get("invoked_juror_count") != REQUIRED_JUROR_COUNT:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_JUROR,
            f"invoked_juror_count={attestation.get('invoked_juror_count')} "
            f"expected {REQUIRED_JUROR_COUNT}",
        )

    # Mock-safe / deterministic absolutes
    if attestation.get("mock_safe_used_any") is True:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MOCK_SAFE_IN_CERTIFICATION,
            "mock_safe_used_any=true",
        )
    if attestation.get("deterministic_proof_stage_used_any") is True:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION,
            "deterministic_proof_stage_used_any=true",
        )

    # Panel match statuses
    if attestation.get("provider_panel_match_status") != "PASS":
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_PROVIDER_MODEL_MISMATCH,
            f"provider_panel_match_status="
            f"{attestation.get('provider_panel_match_status')!r}",
        )
    if attestation.get("model_panel_match_status") != "PASS":
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_PROVIDER_MODEL_MISMATCH,
            f"model_panel_match_status="
            f"{attestation.get('model_panel_match_status')!r}",
        )

    # Hash integrity (non-empty required)
    if not attestation.get("rubric_hash_sha256"):
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
            "rubric_hash_sha256 missing/empty",
        )
    if not attestation.get("panel_response_hash_sha256"):
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
            "panel_response_hash_sha256 missing/empty",
        )

    # Final consensus + allow disposition
    if attestation.get("final_consensus_verdict") != "SAFE":
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_PANEL_NOT_FULLY_SAFE,
            f"final_consensus_verdict="
            f"{attestation.get('final_consensus_verdict')!r}",
        )
    if attestation.get("final_safe_reuse_allow") is not True:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_PANEL_NOT_FULLY_SAFE,
            f"final_safe_reuse_allow="
            f"{attestation.get('final_safe_reuse_allow')!r}",
        )
    x3 = attestation.get("final_x3_disposition")
    if x3 not in ("X3D", "X3_APPROVED_ALLOW"):
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_PANEL_NOT_FULLY_SAFE,
            f"final_x3_disposition={x3!r} (not an approved allow label)",
        )

    # ---- Per-juror gates ----
    jurors = attestation.get("jurors") or []
    if not isinstance(jurors, list) or len(jurors) != REQUIRED_JUROR_COUNT:
        _append_violation(
            codes, msgs,
            RejectReason.REJECT_MISSING_JUROR,
            f"jurors[] length={len(jurors) if isinstance(jurors, list) else 'N/A'} "
            f"expected {REQUIRED_JUROR_COUNT}",
        )

    # All three registered jurors must appear
    observed_ids = set()
    if isinstance(jurors, list):
        for j in jurors:
            if isinstance(j, dict):
                observed_ids.add(j.get("juror_id"))
    for required in REQUIRED_JURORS:
        if required.juror_id not in observed_ids:
            _append_violation(
                codes, msgs,
                RejectReason.REJECT_MISSING_JUROR,
                f"required juror {required.juror_id!r} absent from panel",
            )

    # Per-juror field / value checks
    if isinstance(jurors, list):
        for idx, j in enumerate(jurors):
            if not isinstance(j, dict):
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
                    f"juror[{idx}] is not a dict",
                )
                continue
            for f in _REQUIRED_JUROR_FIELDS:
                if f not in j:
                    _append_violation(
                        codes, msgs,
                        RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
                        f"juror[{idx}] missing field {f!r}",
                    )

            provider = j.get("provider")
            family = j.get("provider_family")
            model = j.get("model_id")
            juror_surface = j.get("control_surface")
            juror_healing_tier = j.get("healing_tier")

            # Per-juror control-surface classifier (mirrors top-level gate)
            per_juror_surface_reject = classify_healing_tier_for_reject(
                control_surface=juror_surface,
                healing_tier=juror_healing_tier,
                model_id=model,
            )
            if per_juror_surface_reject is not None:
                _append_violation(
                    codes, msgs, per_juror_surface_reject,
                    f"juror[{idx}] control_surface={juror_surface!r}"
                    + (
                        f" healing_tier={juror_healing_tier!r}"
                        if juror_healing_tier
                        else ""
                    ),
                )

            # Explicit rejection mapping: reject BEFORE registry lookup
            rej_p = classify_rejected_provider(provider) or classify_rejected_provider(family)
            if rej_p is not None:
                _append_violation(
                    codes, msgs, rej_p,
                    f"juror[{idx}] uses rejected provider={provider!r} "
                    f"family={family!r}",
                )
            rej_m = classify_rejected_model(model)
            if rej_m is not None:
                _append_violation(
                    codes, msgs, rej_m,
                    f"juror[{idx}] uses rejected model_id={model!r}",
                )

            # Registry lookup (after explicit rejection)
            target = get_juror_by_family(family or "")
            if target is None:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_UNREGISTERED_PROVIDER,
                    f"juror[{idx}] provider_family={family!r} not in registry",
                )
            elif not is_registered_model(target.provider, model or ""):
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_UNREGISTERED_MODEL,
                    f"juror[{idx}] model_id={model!r} not registered for "
                    f"provider={target.provider!r}",
                )

            # Match statuses must be PASS
            if j.get("provider_match_status") != "PASS":
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_PROVIDER_MODEL_MISMATCH,
                    f"juror[{idx}] provider_match_status="
                    f"{j.get('provider_match_status')!r}",
                )
            if j.get("model_match_status") != "PASS":
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_PROVIDER_MODEL_MISMATCH,
                    f"juror[{idx}] model_match_status="
                    f"{j.get('model_match_status')!r}",
                )
            if j.get("approved_provider") is not True:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_UNREGISTERED_PROVIDER,
                    f"juror[{idx}] approved_provider="
                    f"{j.get('approved_provider')!r}",
                )

            # Per-juror verdict + fault counters
            verdict = j.get("verdict")
            if verdict != "SAFE":
                if verdict == "UNCERTAIN":
                    _append_violation(
                        codes, msgs,
                        RejectReason.REJECT_JUROR_UNKNOWN,
                        f"juror[{idx}] verdict=UNCERTAIN",
                    )
                elif verdict in ("UNSAFE_DIFFERENT_INTENT",
                                 "UNSAFE_POLICY_DRIFT"):
                    _append_violation(
                        codes, msgs,
                        RejectReason.REJECT_JUROR_UNSAFE,
                        f"juror[{idx}] verdict={verdict}",
                    )
                elif verdict == "ERROR":
                    # Differentiate error sub-types from parse_status
                    ps = j.get("parse_status")
                    if ps == "PARSE_FAIL":
                        _append_violation(
                            codes, msgs,
                            RejectReason.REJECT_JUROR_PARSE_FAIL,
                            f"juror[{idx}] parse_status=PARSE_FAIL",
                        )
                    elif ps == "TIMEOUT":
                        _append_violation(
                            codes, msgs,
                            RejectReason.REJECT_JUROR_TIMEOUT,
                            f"juror[{idx}] parse_status=TIMEOUT",
                        )
                    else:
                        _append_violation(
                            codes, msgs,
                            RejectReason.REJECT_JUROR_ERROR,
                            f"juror[{idx}] verdict=ERROR parse_status={ps!r}",
                        )
                else:
                    _append_violation(
                        codes, msgs,
                        RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
                        f"juror[{idx}] verdict={verdict!r} not recognized",
                    )

            if (j.get("timeout_count") or 0) > 0:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_JUROR_TIMEOUT,
                    f"juror[{idx}] timeout_count={j.get('timeout_count')}",
                )
            if (j.get("error_count") or 0) > 0:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_JUROR_ERROR,
                    f"juror[{idx}] error_count={j.get('error_count')}",
                )
            if (j.get("unknown_count") or 0) > 0:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_JUROR_UNKNOWN,
                    f"juror[{idx}] unknown_count={j.get('unknown_count')}",
                )
            if (j.get("unsafe_count") or 0) > 0:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_JUROR_UNSAFE,
                    f"juror[{idx}] unsafe_count={j.get('unsafe_count')}",
                )
            if (j.get("parse_fail_count") or 0) > 0:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_JUROR_PARSE_FAIL,
                    f"juror[{idx}] parse_fail_count={j.get('parse_fail_count')}",
                )
            if not j.get("response_hash_sha256"):
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_MALFORMED_JUROR_OUTPUT,
                    f"juror[{idx}] response_hash_sha256 missing/empty",
                )
            if j.get("mock_safe_used") is True:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_MOCK_SAFE_IN_CERTIFICATION,
                    f"juror[{idx}] mock_safe_used=true",
                )
            if j.get("deterministic_proof_stage_used") is True:
                _append_violation(
                    codes, msgs,
                    RejectReason.REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION,
                    f"juror[{idx}] deterministic_proof_stage_used=true",
                )

    accepted = len(codes) == 0
    if accepted:
        row_status = "ACCEPTED"
    elif any(c == RejectReason.REJECT_MISSING_PANEL_ATTESTATION for c in codes):
        row_status = "PENDING"
    elif any(
        "MISSING_KEY" in c or "INFRASTRUCTURE" in c for c in codes
    ):
        row_status = "INFRASTRUCTURE_GAP"
    else:
        row_status = "BLOCKED"

    return PanelGateResult(
        accepted=accepted,
        reason_codes=tuple(codes),
        messages=tuple(msgs),
        row_status=row_status,
    )


def load_panel_attestation(repo_root: Path) -> dict[str, Any] | None:
    """Read the panel attestation JSON from the canonical path. Returns
    None if the file is missing or unreadable."""
    path = panel_artifact_path(repo_root)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, FileNotFoundError, json.JSONDecodeError):
        return None


__all__ = [
    "PanelGateResult",
    "load_panel_attestation",
    "validate_panel_attestation",
]
