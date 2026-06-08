"""IBM narrative-only proof accounting helpers (generation vs judges vs authorization)."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.offline_contract_status import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS


def classify_generation_class(
    *,
    runtime_generation_status: str,
    offline_contract_stub_active: bool,
    test_only_mock_provider: bool,
) -> str:
    if offline_contract_stub_active:
        return "offline_stub"
    if test_only_mock_provider:
        return "mock_provider"
    if runtime_generation_status == "REAL_LLM":
        return "real_llm"
    if runtime_generation_status == "BLOCKED":
        return "blocked"
    return "unknown"


def classify_judge_class(x1d_judges: list[dict[str, Any]] | None) -> str:
    modes = {str(j.get("evaluator_mode") or "") for j in (x1d_judges or [])}
    if not modes:
        return "blocked"
    if modes == {"MOCKED"}:
        return "mocked"
    if modes == {"MODEL_BACKED"}:
        return "model_backed"
    if any(m.startswith("BLOCKED") for m in modes) and modes.intersection({"MOCKED"}):
        return "mixed"
    if any(m.startswith("BLOCKED") for m in modes):
        return "blocked"
    if "MOCKED" in modes:
        return "mixed"
    return "mixed"


def classify_proof_class(*, bundle: dict[str, Any], x3_code: str, x3_pass: bool) -> str:
    if x3_pass and x3_code == "X3_ALLOW":
        return "allow_class"
    if str(bundle.get("proof_scope") or "") == "plumbing_only":
        return "plumbing_only"
    if x3_code == "X3_BLOCK" or not x3_code:
        return "blocked"
    if str(x3_code).startswith("X3_REVIEW"):
        return "review_class"
    return "review_class"


def classify_certification_class(*, bundle: dict[str, Any], x3_code: str, x3_pass: bool) -> str:
    if x3_pass and x3_code == "X3_ALLOW" and bundle.get("proof_eligible"):
        return "runtime_slice_allow"
    if bundle.get("proof_eligible") is False and str(bundle.get("proof_scope")) == "plumbing_only":
        return "runtime_slice_review"
    if str(x3_code or "").startswith("X3_REVIEW"):
        return "runtime_slice_review"
    return "not_certified"


def compute_decisive_accounting_label(
    *,
    command_fault: bool,
    runtime_generation_status: str,
    x2_failure_count: int,
    x3_code: str,
    x3_pass: bool,
    proceed_to_runtime: bool,
    mock_judges_active: bool,
    proof_eligible: bool,
    preflight_blocked: bool,
    bundle_proof_scope: str,
) -> str:
    """Human-facing coarse label separating shell success from release authorization."""
    if command_fault:
        return "BLOCKED"
    if preflight_blocked:
        return "BLOCKED"
    structurally_present = runtime_generation_status in {"REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS}
    if not structurally_present:
        return "FAIL"
    if x2_failure_count > 0:
        return "FAIL"
    if mock_judges_active or bundle_proof_scope == "plumbing_only":
        return "PASS_PLUMBING_ONLY"
    if (
        proof_eligible
        and proceed_to_runtime
        and x3_pass
        and x3_code == "X3_ALLOW"
        and not mock_judges_active
        and bundle_proof_scope != "plumbing_only"
    ):
        return "PASS_ALLOW_CLASS"
    if str(x3_code).startswith("X3_REVIEW"):
        return "PASS_REVIEW_CLASS"
    return "FAIL"


def build_clean_x3_allow_readiness_document(
    *,
    section_id: str,
    run_id: str,
    clean_allow_possible_at_start: bool,
    required_judges: list[str],
    provider_preflight_status_by_judge: dict[str, Any],
    mocked_judges_present: bool,
    blocked_judges_present: bool,
    mocked_judge_flags_active: bool,
    x2_hard_gates_required: int,
    x2_hard_gates_passed: int,
    x3_code: str,
    proceed_to_runtime: bool,
    product_authorized: bool,
    proof_eligible: bool,
    proof_scope: str,
    decisive_blockers: list[str],
    recommended_next_action: str,
    preflight_artifact_written: bool,
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "run_id": run_id,
        "clean_allow_possible_at_start": clean_allow_possible_at_start,
        "required_judges": list(required_judges),
        "provider_preflight_status_by_judge": dict(provider_preflight_status_by_judge),
        "mocked_judges_present": mocked_judges_present,
        "blocked_judges_present": blocked_judges_present,
        "mocked_judge_flags_active": mocked_judge_flags_active,
        "x2_hard_gates_required": int(x2_hard_gates_required),
        "x2_hard_gates_passed": int(x2_hard_gates_passed),
        "x3_code": x3_code,
        "proceed_to_runtime": bool(proceed_to_runtime),
        "product_authorized": bool(product_authorized),
        "proof_eligible": bool(proof_eligible),
        "proof_scope": proof_scope,
        "decisive_blockers": list(decisive_blockers),
        "recommended_next_action": recommended_next_action,
        "preflight_artifact_written": bool(preflight_artifact_written),
    }


__all__ = [
    "build_clean_x3_allow_readiness_document",
    "classify_certification_class",
    "classify_generation_class",
    "classify_judge_class",
    "classify_proof_class",
    "compute_decisive_accounting_label",
]
