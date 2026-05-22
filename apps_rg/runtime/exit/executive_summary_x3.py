"""X3 disposition aggregator for executive summary runtime slice."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Any

from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS


# Blocked provider evaluator modes
BLOCKED_MODES = {
    "BLOCKED_PROVIDER_UNAVAILABLE",
    "BLOCKED_MODEL_NOT_FOUND",
    "BLOCKED_RESPONSE_PARSE_ERROR",
    "BLOCKED_SCHEMA_VALIDATION_ERROR",
}


@dataclass
class X3Disposition:
    x3_code: str
    decisive_reason: str
    review_reason: str
    authorization_scope: str
    proceed_to_runtime: bool
    pass_: bool
    runtime_generation_status: str
    x1d_evaluator_mode: str
    product_quality_status: str
    x2_failed_gates: list[str]
    blocked_judges: list[str]
    mocked_judges: list[str]
    soft_failed_judges: list[str]
    decisive_judge_failures: list[str]
    final_summary_hash: str
    claim_ledger_hash: str
    required_remediation: list[str]
    # Forensics: populated by aggregate_x3 — does not relax gates or imply quorum.
    blocked_judge_detail_rows: list[dict[str, Any]] = field(default_factory=list)
    model_backed_pass_provider_keys: list[str] = field(default_factory=list)
    proof_eligible_allow_requires: str = "every_configured_x1d_judge_model_backed_pass"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        from apps_rg.runtime.disposition_authority import apply_lane_x3_authority_fields

        return apply_lane_x3_authority_fields(data)


def _is_blocked_judge(judge: dict[str, Any]) -> bool:
    return bool(judge.get("provider_blocked")) or judge.get("evaluator_mode") in BLOCKED_MODES


def _is_mocked_judge(judge: dict[str, Any]) -> bool:
    return judge.get("evaluator_mode") == "MOCKED"


def _is_model_backed_soft_fail(judge: dict[str, Any]) -> bool:
    if judge.get("evaluator_mode") != "MODEL_BACKED":
        return False
    if judge.get("decisive_failure"):
        return False
    if judge.get("provider_status") == "MODEL_BACKED_FAIL":
        return True
    if judge.get("pass") is False:
        return True
    normalized_score = judge.get("normalized_score")
    normalized_threshold = judge.get("normalized_threshold")
    if normalized_score is not None and normalized_threshold is not None:
        return float(normalized_score) < float(normalized_threshold)
    return False


def _model_backed_pass_provider_keys(judges: list[dict[str, Any]]) -> list[str]:
    """Providers that satisfied the same MODEL_BACKED_PASS slice used for X3_ALLOW (subset check)."""
    out: list[str] = []
    for j in judges:
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        if j.get("provider_status") != "MODEL_BACKED_PASS":
            continue
        if j.get("pass") is False:
            continue
        if j.get("decisive_failure"):
            continue
        ns = j.get("normalized_score")
        nt = j.get("normalized_threshold")
        if ns is not None and nt is not None and float(ns) < float(nt):
            continue
        pk = j.get("provider_key")
        if pk:
            out.append(str(pk))
    return out


def _blocked_judge_detail_rows(judges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for j in judges:
        if not _is_blocked_judge(j):
            continue
        err = j.get("exact_provider_error")
        rows.append(
            {
                "provider_key": j.get("provider_key"),
                "evaluator_mode": j.get("evaluator_mode"),
                "provider_status": j.get("provider_status"),
                "provider_blocked": bool(j.get("provider_blocked")),
                "exact_provider_error": err if isinstance(err, str) else str(err or ""),
            }
        )
    return rows


def aggregate_x3(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]],
    x1d_judges: list[dict[str, Any]],
    runtime_generation_status: str,
    product_quality_status: str,
    canonical_claims_for_hash: list[dict[str, Any]] | None = None,
    section_input_usage_ledger: dict[str, Any] | None = None,
    judge_required_for_allow: bool = True,
) -> X3Disposition:
    failed_gates = [g["gate_id"] for g in x2_gates if not g.get("pass")]

    authority_reasons: list[str] = []
    if section_input_usage_ledger is None:
        authority_reasons.append("section_input_usage_ledger missing for X3 authority check")
    elif section_input_usage_ledger.get("schema") != "section_input_usage_ledger_v1":
        authority_reasons.append("section_input_usage_ledger schema is not section_input_usage_ledger_v1")
    else:
        eb_raw = section_input_usage_ledger.get("evidence_boundary")
        if not isinstance(eb_raw, dict):
            authority_reasons.append("evidence_boundary missing or invalid on section_input_usage_ledger")
        else:
            if eb_raw.get("non_evidence_inputs_used_as_claim_evidence") is True:
                authority_reasons.append(
                    "evidence_boundary.non_evidence_inputs_used_as_claim_evidence must not be true"
                )
            if eb_raw.get("non_evidence_inputs_in_source_fact_ids") is True:
                authority_reasons.append(
                    "evidence_boundary.non_evidence_inputs_in_source_fact_ids must not be true"
                )
        css = section_input_usage_ledger.get("claim_support_summary") or {}
        if int(css.get("claims_with_targeting_input_in_source_fact_ids") or 0) > 0:
            authority_reasons.append(
                "claim_support_summary claims_with_targeting_input_in_source_fact_ids must be 0"
            )
        if int(css.get("claims_with_context_input_in_source_fact_ids") or 0) > 0:
            authority_reasons.append(
                "claim_support_summary claims_with_context_input_in_source_fact_ids must be 0"
            )

    blocked_detail_rows = _blocked_judge_detail_rows(x1d_judges)
    mb_pass_keys = _model_backed_pass_provider_keys(x1d_judges)

    blocked = [j["provider_key"] for j in x1d_judges if _is_blocked_judge(j)]
    mocked = [j["provider_key"] for j in x1d_judges if _is_mocked_judge(j)]
    decisive = [
        j["provider_key"]
        for j in x1d_judges
        if j.get("evaluator_mode") == "MODEL_BACKED" and j.get("decisive_failure")
    ]
    soft_failed = [j["provider_key"] for j in x1d_judges if _is_model_backed_soft_fail(j)]

    modes = {j.get("evaluator_mode") for j in x1d_judges}
    if modes == {"MODEL_BACKED"}:
        x1d_mode = "MODEL_BACKED"
    elif "MOCKED" in modes:
        x1d_mode = "MOCKED"
    elif any(m in BLOCKED_MODES for m in modes):
        x1d_mode = "BLOCKED_PROVIDER_UNAVAILABLE"
    else:
        x1d_mode = "BLOCKED_PROVIDER_UNAVAILABLE"

    remediation: list[str] = []
    if failed_gates:
        remediation.append(f"Fix failed X2 gates: {', '.join(failed_gates)}")
    if authority_reasons:
        remediation.append(f"Fix input authority violations: {'; '.join(authority_reasons)}")
    if blocked:
        remediation.append(f"Configure blocked judge providers: {', '.join(blocked)}")
    if mocked:
        remediation.append("Replace mocked judges with model-backed or approved calibrated judges.")
        if runtime_generation_status in ("REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS):
            remediation.append(
                "Generation artifacts exist; X1D proof blocked because judges were mocked "
                f"(runtime_generation_status={runtime_generation_status!r})."
            )
    if soft_failed:
        remediation.append(f"Address soft-failed judges below threshold: {', '.join(soft_failed)}")
    if decisive:
        remediation.append(f"Remediate decisive judge failures: {', '.join(decisive)}")
    if product_quality_status != "PASS":
        remediation.append(f"Product quality must be PASS, currently {product_quality_status}.")

    summary_hash = hashlib.sha256(resume_display_text.encode()).hexdigest()[:16]
    ledger_payload = canonical_claims_for_hash if canonical_claims_for_hash is not None else claim_ledger
    ledger_hash = hashlib.sha256(json.dumps(ledger_payload, sort_keys=True).encode()).hexdigest()[:16]

    review_reason = ""
    if failed_gates or authority_reasons:
        code = "X3_BLOCK"
        _parts: list[str] = []
        if failed_gates:
            _parts.append("X2 deterministic gate failure")
        if authority_reasons:
            _parts.append(f"Input authority violation: {'; '.join(authority_reasons)}")
        reason = "; ".join(_parts)
        scope = "PLUMBING_ONLY"
        allowed = False
    elif runtime_generation_status == "BLOCKED":
        code = "X3_BLOCK"
        reason = "Runtime generation is BLOCKED."
        scope = "PLUMBING_ONLY"
        allowed = False
    elif product_quality_status == "FAIL":
        code = "X3_BLOCK"
        reason = "Product quality is FAIL."
        scope = "PLUMBING_ONLY"
        allowed = False
    elif judge_required_for_allow and blocked:
        code = "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"
        reason = "One or more required X1D judge providers are blocked."
        review_reason = reason
        scope = "PLUMBING_ONLY"
        allowed = False
    elif judge_required_for_allow and mocked:
        code = "X3_REVIEW_MOCKED_PLUMBING_ONLY"
        reason = "One or more X1D judges are mocked."
        review_reason = reason
        scope = "PLUMBING_ONLY"
        allowed = False
    elif runtime_generation_status == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
        code = "X3_REVIEW_MOCKED_PLUMBING_ONLY"
        reason = (
            "Offline Qwen contract stub (APPS_RG_QWEN_OFFLINE_CONTRACT_STUB); "
            "not live LLM transport proof."
        )
        review_reason = reason
        scope = "PLUMBING_ONLY"
        allowed = False
    elif runtime_generation_status != "REAL_LLM":
        code = "X3_REVIEW_MOCKED_PLUMBING_ONLY"
        reason = "Runtime generation is not REAL_LLM. Mocked/blocked generation proves plumbing only."
        review_reason = reason
        scope = "PLUMBING_ONLY"
        allowed = False
    elif product_quality_status != "PASS":
        code = "X3_REVIEW_PRODUCT_QUALITY"
        reason = "Product quality is not PASS."
        review_reason = reason
        scope = "PLUMBING_ONLY"
        allowed = False
    elif judge_required_for_allow and decisive:
        code = "X3_BLOCK"
        reason = "X1D decisive judge failure"
        scope = "PLUMBING_ONLY"
        allowed = False
    elif judge_required_for_allow and soft_failed:
        code = "X3_REVIEW_JUDGE_SOFT_FAIL"
        reason = "One or more required X1D judges scored below threshold without decisive failure."
        review_reason = reason
        scope = "REVIEW_ONLY"
        allowed = False
    else:
        if not judge_required_for_allow:
            code = "X3_ALLOW"
            reason = (
                "REAL_LLM output, X2 pass, product quality PASS; "
                "X1D judges advisory-only for this section (not required for allow)."
            )
            review_reason = ""
            scope = "PRODUCT_QUALITY"
            allowed = True
        elif not x1d_judges:
            code = "X3_REVIEW_JUDGE_SOFT_FAIL"
            reason = "No X1D judge rows present for a section that requires judges."
            review_reason = reason
            scope = "REVIEW_ONLY"
            allowed = False
        else:
            all_model_backed_pass = all(
                j.get("evaluator_mode") == "MODEL_BACKED"
                and j.get("provider_status") == "MODEL_BACKED_PASS"
                and j.get("pass") is not False
                and not j.get("decisive_failure")
                and (
                    j.get("normalized_score") is None
                    or j.get("normalized_threshold") is None
                    or float(j["normalized_score"]) >= float(j["normalized_threshold"])
                )
                for j in x1d_judges
            )
            if all_model_backed_pass:
                code = "X3_ALLOW"
                reason = "REAL_LLM output, X2 pass, all X1D judges model-backed pass, product quality PASS."
                review_reason = ""
                scope = "PRODUCT_QUALITY"
                allowed = True
            else:
                code = "X3_REVIEW_JUDGE_SOFT_FAIL"
                reason = "One or more required X1D judges scored below threshold without decisive failure."
                review_reason = reason
                scope = "REVIEW_ONLY"
                allowed = False
                soft_failed = [
                    j["provider_key"]
                    for j in x1d_judges
                    if j.get("provider_key") not in soft_failed and _is_model_backed_soft_fail(j)
                ] or soft_failed

    proof_requires = (
        "every_configured_x1d_judge_model_backed_pass"
        if judge_required_for_allow
        else "x2_pass_only_x1d_advisory_optional"
    )

    return X3Disposition(
        x3_code=code,
        decisive_reason=reason,
        review_reason=review_reason,
        authorization_scope=scope,
        proceed_to_runtime=allowed,
        pass_=allowed,
        runtime_generation_status=runtime_generation_status,
        x1d_evaluator_mode=x1d_mode,
        product_quality_status=product_quality_status,
        x2_failed_gates=failed_gates,
        blocked_judges=blocked,
        mocked_judges=mocked,
        soft_failed_judges=soft_failed,
        decisive_judge_failures=decisive,
        final_summary_hash=summary_hash,
        claim_ledger_hash=ledger_hash,
        required_remediation=remediation,
        blocked_judge_detail_rows=blocked_detail_rows,
        model_backed_pass_provider_keys=mb_pass_keys,
        proof_eligible_allow_requires=proof_requires,
    )
