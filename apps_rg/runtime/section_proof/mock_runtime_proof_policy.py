"""Hatch helpers for mocked judges in section dispatch CLIs (plumbing-only path).

Generation provider is always ``qwen_vllm`` (offline contract tests use
``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1`` — emits ``OFFLINE_CONTRACT_STUB`` transport status).

Keeps deterministic exit codes + proof-field wiring shared across headline, competencies,
IBM bullets/narrative, unify narrative/bullets (legacy ``-m``), and orchestration harnesses."""

from __future__ import annotations

import sys
from typing import Any, Protocol

from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS


class _X3DispositionLike(Protocol):
    x3_code: str

    @property
    def pass_(self) -> bool: ...


MOCK_JUDGES_REJECT_EXIT_CODE = 9


def mock_judges_blocked_before_run(args: Any) -> bool:
    if not bool(getattr(args, "mock_judges", False)):
        return False
    return not bool(getattr(args, "allow_test_mock_judges", False))


def allow_non_allow_exit_zero_ok(args: Any) -> bool:
    return bool(getattr(args, "allow_non_allow_exit_zero", False))


def emit_mock_judges_blocked_stderr(*, dispatcher_label: str) -> None:
    print(
        "ERROR: `--mock-judges` requires `--allow-test-mock-judges` for test-only plumbing; "
        f"dispatcher={dispatcher_label!r}. Mock judges cannot certify X1D evidence.",
        file=sys.stderr,
    )


def infer_product_quality_blocked_or_mock(
    *,
    runtime_generation_status: str,
    x2_failed_gate_ids: list[str],
    pass_reason: str,
) -> tuple[str, str]:
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    if x2_failed_gate_ids:
        return "FAIL", f"X2 failed gates: {x2_failed_gate_ids}"
    if product_fail_closed_runtime():
        if runtime_generation_status != "REAL_LLM":
            return (
                "FAIL",
                f"Product run requires REAL_LLM generation; got {runtime_generation_status!r}.",
            )
        return "PASS", pass_reason
    if runtime_generation_status == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
        return (
            "PARTIAL",
            "Offline Qwen contract stub (APPS_RG_QWEN_OFFLINE_CONTRACT_STUB); plumbing-only (not live transport proof).",
        )
    if runtime_generation_status != "REAL_LLM":
        return "PARTIAL", "Mocked or blocked generation can prove plumbing only."
    return "PASS", pass_reason


def _any_judge_blocked(x1d_judges: list[dict[str, Any]] | None) -> bool:
    for j in x1d_judges or []:
        mode = str(j.get("evaluator_mode") or "")
        if mode.startswith("BLOCKED_"):
            return True
    return False


def _judge_counts_for_proof(
    x1d_judges: list[dict[str, Any]] | None,
    *,
    judge_required_for_proof: bool,
) -> tuple[bool, bool, bool]:
    """Return (has_mock, has_blocked, has_non_proof_eligible_required)."""
    rows = x1d_judges or []
    has_mock = any(str(j.get("evaluator_mode")) == "MOCKED" for j in rows)
    has_blocked = any(str(j.get("evaluator_mode", "")).startswith("BLOCKED_") for j in rows)
    if not judge_required_for_proof:
        return has_mock, has_blocked, False
    non_proof = False
    for j in rows:
        if j.get("mocked") is True:
            non_proof = True
            continue
        if j.get("advisory_only") is True and j.get("proof_eligible_judge") is False:
            non_proof = True
            continue
        if j.get("proof_eligible_judge") is False and str(j.get("evaluator_mode")) == "MODEL_BACKED":
            non_proof = True
    return has_mock, has_blocked, non_proof


def compute_lane_proof_bundle(
    args: Any,
    *,
    section_id: str = "",
    runtime_generation_status: str,
    x1d_judges: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]],
    x3: _X3DispositionLike | Any,
    offline_contract_stub_used: bool = False,
) -> dict[str, Any]:
    from apps_rg.runtime.section_judge_policy import get_section_judge_policy, normalize_section_id

    sid = normalize_section_id(
        section_id or str(getattr(args, "section", "") or getattr(args, "section_id", "") or "")
    )
    try:
        policy = get_section_judge_policy(sid)
    except KeyError:
        policy = None
    judge_required_for_proof = True if policy is None else policy.judge_required_for_proof

    cli_mock_judge = bool(getattr(args, "mock_judges", False))
    inspection_hatch = bool(getattr(args, "allow_non_allow_exit_zero", False))
    mock_judge_hatch = bool(getattr(args, "allow_test_mock_judges", False))

    mock_provider = str(getattr(args, "provider", "") or "").strip().lower() == "mock"
    plumbing_waiver = inspection_hatch
    hatch_mock_provider = bool(getattr(args, "allow_test_mock_provider", False)) or (
        plumbing_waiver and mock_provider
    )

    judge_rows_mock, judge_blocked, judge_non_proof = _judge_counts_for_proof(
        x1d_judges,
        judge_required_for_proof=judge_required_for_proof,
    )
    judge_rows_mock = judge_rows_mock or cli_mock_judge

    failed_x2 = [g["gate_id"] for g in (x2_gates or []) if not g.get("pass")]
    x3_allow = getattr(x3, "x3_code", "") == "X3_ALLOW"

    proofs_ok = not failed_x2 and x3_allow and bool(getattr(x3, "pass_", False))

    plumbing = (
        runtime_generation_status != "REAL_LLM"
        or (judge_required_for_proof and judge_rows_mock)
        or (judge_required_for_proof and judge_blocked)
        or (judge_required_for_proof and judge_non_proof)
        or mock_provider
        or mock_judge_hatch
        or offline_contract_stub_used
    )

    proof_eligible = bool(not plumbing and proofs_ok)

    if judge_required_for_proof:
        judge_pe = bool(
            proof_eligible
            and not judge_rows_mock
            and not cli_mock_judge
            and not judge_blocked
            and not judge_non_proof
        )
    else:
        judge_pe = False
    provider_pe = bool(
        proof_eligible
        and runtime_generation_status == "REAL_LLM"
        and not offline_contract_stub_used
        and not mock_provider
    )

    x1d_runtime = "MODEL_BACKED"
    if judge_rows_mock:
        x1d_runtime = "MOCKED"
    elif _any_judge_blocked(x1d_judges):
        x1d_runtime = "BLOCKED_PROVIDER_UNAVAILABLE"

    artifact_namespace_class = "NON_PROOF_PLUMBING" if not proof_eligible else "PRODUCT_PROOF_ELIGIBLE_RUN"
    if runtime_generation_status == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
        status_class = "OFFLINE_CONTRACT_STUB"
    elif runtime_generation_status == "MOCKED":
        status_class = "MOCKED_TRANSPORT"
    elif runtime_generation_status == "REAL_LLM":
        status_class = "REAL_LLM"
    elif runtime_generation_status == "STUBBED":
        status_class = "STUBBED_LLM"
    else:
        status_class = "OTHER_NON_PROOF"

    auth_scope = str(getattr(x3, "authorization_scope", "") or "")

    return {
        "section_id": sid or None,
        "judge_required_for_proof": judge_required_for_proof,
        "judge_tier": policy.judge_tier.value if policy else None,
        "proof_eligible": proof_eligible,
        "generation_runtime_status": runtime_generation_status,
        "mocked_provider_selected": mock_provider,
        "proof_scope": "plumbing_only" if plumbing or not proofs_ok else "product_quality",
        "proof_status": "PROOF_ELIGIBLE" if proof_eligible else "NOT_PROOF_ELIGIBLE",
        "authorization_scope": auth_scope,
        "test_only_mock_provider": mock_provider and hatch_mock_provider,
        "runtime_certification": proof_eligible,
        "x1d_runtime_status": x1d_runtime,
        "judge_proof_eligible": judge_pe,
        "provider_proof_eligible": provider_pe,
        "test_only_mock_judges": cli_mock_judge and mock_judge_hatch,
        "offline_contract_stub_used": bool(offline_contract_stub_used),
        "artifact_namespace_class": artifact_namespace_class,
        "runtime_generation_status_class": status_class,
        "allow_non_allow_exit_zero_cli": inspection_hatch,
        "allow_test_mock_judges_hatch": mock_judge_hatch,
        "proof_closeout_note": "",
    }


def attach_lane_proof_bundle_fields(
    target: dict[str, Any],
    *,
    runtime_generation_status: str,
    bundle: dict[str, Any],
) -> None:
    """Merge proof-bundle booleans/metadata onto outbound L2 / real-result dicts."""
    _ = runtime_generation_status
    for k, v in bundle.items():
        target[k] = v


__all__ = [
    "MOCK_JUDGES_REJECT_EXIT_CODE",
    "allow_non_allow_exit_zero_ok",
    "attach_lane_proof_bundle_fields",
    "compute_lane_proof_bundle",
    "emit_mock_judges_blocked_stderr",
    "infer_product_quality_blocked_or_mock",
    "mock_judges_blocked_before_run",
]
