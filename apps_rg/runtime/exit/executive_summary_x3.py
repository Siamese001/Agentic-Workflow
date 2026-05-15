"""X3 disposition aggregator for executive summary runtime slice."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any


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
    authorization_scope: str
    proceed_to_runtime: bool
    pass_: bool
    runtime_generation_status: str
    x1d_evaluator_mode: str
    product_quality_status: str
    x2_failed_gates: list[str]
    blocked_judges: list[str]
    mocked_judges: list[str]
    decisive_judge_failures: list[str]
    final_summary_hash: str
    claim_ledger_hash: str
    required_remediation: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def aggregate_x3(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    x2_gates: list[dict[str, Any]],
    x1d_judges: list[dict[str, Any]],
    runtime_generation_status: str,
    product_quality_status: str,
) -> X3Disposition:
    # X2 gate failures
    failed_gates = [g["gate_id"] for g in x2_gates if not g.get("pass")]
    
    # Blocked providers: any BLOCKED_* mode (not decisive failures)
    blocked = [
        j["provider_key"] for j in x1d_judges 
        if j.get("evaluator_mode") in BLOCKED_MODES
    ]
    
    # Mocked judges
    mocked = [j["provider_key"] for j in x1d_judges if j.get("evaluator_mode") == "MOCKED"]
    
    # Decisive judge failures: MODEL_BACKED with decisive_failure=true
    decisive = [
        j["provider_key"] for j in x1d_judges 
        if j.get("evaluator_mode") == "MODEL_BACKED" and j.get("decisive_failure")
    ]
    
    # X1D evaluator mode summary
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
    if blocked:
        remediation.append(f"Configure blocked judge providers: {', '.join(blocked)}")
    if mocked:
        remediation.append("Replace mocked judges with model-backed or approved calibrated judges.")
    if product_quality_status != "PASS":
        remediation.append(f"Product quality must be PASS, currently {product_quality_status}.")

    summary_hash = hashlib.sha256(resume_display_text.encode()).hexdigest()[:16]
    ledger_hash = hashlib.sha256(json.dumps(claim_ledger, sort_keys=True).encode()).hexdigest()[:16]

    # X3 disposition rules (in priority order):
    # 1. X2 fail => X3_BLOCK
    # 2. Runtime generation blocked => X3_BLOCK
    # 3. Product quality fail => X3_BLOCK
    # 4. Model-backed judge decisive failure => X3_BLOCK
    # 5. X2 pass + one or more blocked providers => X3_REVIEW_JUDGE_PROVIDER_BLOCKED
    # 6. X2 pass + mocked judges => X3_REVIEW_MOCKED_PLUMBING_ONLY
    # 7. All clear => X3_ALLOW

    if failed_gates:
        code = "X3_BLOCK"
        reason = "X2 deterministic gate failure"
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
    elif decisive:
        code = "X3_BLOCK"
        reason = "X1D decisive judge failure"
        scope = "PLUMBING_ONLY"
        allowed = False
    elif runtime_generation_status != "REAL_LLM":
        code = "X3_REVIEW_MOCKED_PLUMBING_ONLY"
        reason = "Runtime generation is not REAL_LLM. Mocked/blocked generation proves plumbing only."
        scope = "PLUMBING_ONLY"
        allowed = False
    elif product_quality_status != "PASS":
        code = "X3_REVIEW_PRODUCT_QUALITY"
        reason = "Product quality is not PASS."
        scope = "PLUMBING_ONLY"
        allowed = False
    elif blocked:
        code = "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"
        reason = "One or more required X1D judge providers are blocked."
        scope = "PLUMBING_ONLY"
        allowed = False
    elif mocked:
        code = "X3_REVIEW_MOCKED_PLUMBING_ONLY"
        reason = "One or more X1D judges are mocked."
        scope = "PLUMBING_ONLY"
        allowed = False
    else:
        code = "X3_ALLOW"
        reason = "REAL_LLM output, X2 pass, all X1D judges model-backed, product quality PASS."
        scope = "PRODUCT_QUALITY"
        allowed = True

    return X3Disposition(
        x3_code=code,
        decisive_reason=reason,
        authorization_scope=scope,
        proceed_to_runtime=allowed,
        pass_=allowed,
        runtime_generation_status=runtime_generation_status,
        x1d_evaluator_mode=x1d_mode,
        product_quality_status=product_quality_status,
        x2_failed_gates=failed_gates,
        blocked_judges=blocked,
        mocked_judges=mocked,
        decisive_judge_failures=decisive,
        final_summary_hash=summary_hash,
        claim_ledger_hash=ledger_hash,
        required_remediation=remediation,
    )
