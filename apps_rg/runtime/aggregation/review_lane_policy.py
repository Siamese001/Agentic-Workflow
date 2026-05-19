"""W6 REVIEW-lane and product ALLOW policy for aggregation package."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS

POLICY_SCHEMA = "apps_rg.review_lane_policy.v1"

X3_ALLOW = "X3_ALLOW"
MOCK_RUNTIME_STATUSES = frozenset({"OFFLINE_CONTRACT_STUB", "MOCKED", "MOCK"})


def _classify_lane(
    *,
    lane: str,
    x3_code: str,
    runtime_generation_status: str | None,
    authorization_scope: str | None,
    product_quality_status: str | None,
) -> dict[str, Any]:
    code_u = x3_code.upper()
    rgs = str(runtime_generation_status or "").upper()
    auth = str(authorization_scope or "").upper()

    if code_u.startswith("X3_BLOCK") or ("BLOCKED" in code_u and "REVIEW" not in code_u):
        disposition_class = "BLOCKED"
        can_structural_package = False
        product_review_required = False
        supports_product_allow = False
        reason = "blocked_x3"
    elif (
        "MOCK" in code_u
        or "PLUMBING" in code_u
        or rgs in MOCK_RUNTIME_STATUSES
        or auth == "PLUMBING_ONLY"
    ):
        disposition_class = "MOCK_PLUMBING_ONLY"
        can_structural_package = True
        product_review_required = True
        supports_product_allow = False
        reason = "mock_or_plumbing_only_lane"
    elif code_u == X3_ALLOW and rgs == "REAL_LLM":
        disposition_class = "ALLOW"
        can_structural_package = True
        product_review_required = False
        supports_product_allow = True
        reason = "x3_allow_real_llm"
    elif "REVIEW" in code_u:
        disposition_class = "REVIEW"
        can_structural_package = True
        product_review_required = True
        supports_product_allow = False
        reason = "review_x3_not_product_allow"
        if product_quality_status == "FAIL":
            can_structural_package = False
            reason = "review_x3_with_product_quality_fail"
    else:
        disposition_class = "UNKNOWN"
        can_structural_package = False
        product_review_required = True
        supports_product_allow = False
        reason = f"unclassified_x3:{x3_code}"

    return {
        "lane": lane,
        "disposition_class": disposition_class,
        "x3_code": x3_code,
        "runtime_generation_status": runtime_generation_status,
        "authorization_scope": authorization_scope,
        "product_quality_status": product_quality_status,
        "can_structural_package": can_structural_package,
        "product_review_required": product_review_required,
        "supports_product_allow": supports_product_allow,
        "reason": reason,
    }


def _load_x3_and_l2(
    repo: Path, run_dir_rel: str
) -> tuple[str, str | None, str | None, str | None]:
    run_dir = repo / run_dir_rel.replace("\\", "/")
    x3_code = ""
    rgs: str | None = None
    auth: str | None = None
    x3p = run_dir / "x3_disposition.json"
    if x3p.is_file():
        import json

        x3 = json.loads(x3p.read_text(encoding="utf-8"))
        x3_code = str(x3.get("x3_code") or "")
        rgs = str(x3.get("runtime_generation_status") or "") or None
        auth = str(x3.get("authorization_scope") or "") or None
    l2p = run_dir / "l2_output.json"
    pq: str | None = None
    if l2p.is_file():
        import json

        l2 = json.loads(l2p.read_text(encoding="utf-8"))
        pq = str(l2.get("product_quality_status") or "") or None
        if not rgs:
            rgs = str(l2.get("runtime_generation_status") or "") or None
    return x3_code, rgs, pq if pq else None, auth


def evaluate_review_lane_policy(
    *,
    repo: Path,
    rollup_blob: dict[str, Any],
    sealed_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lanes = rollup_blob.get("lanes") or {}
    pointers = {}
    if sealed_index:
        pointers = {str(p["lane"]): p for p in (sealed_index.get("pointers") or []) if isinstance(p, dict)}

    per_lane: list[dict[str, Any]] = []
    for lane in GENERATED_LANE_IDS:
        row = lanes.get(lane) if isinstance(lanes, dict) else None
        ptr = pointers.get(lane) or {}
        rd = ""
        if isinstance(row, dict):
            rd = str(row.get("latest_successful_real_artifact_path") or row.get("rollup_source_run_dir") or "")
        x3_code = str(ptr.get("x3_code") or (row or {}).get("x3_code") or "")
        rgs = ptr.get("runtime_generation_status") or None
        auth = None
        pq = ptr.get("product_quality_status") or None
        if rd:
            loaded_x3, loaded_rgs, loaded_pq, auth_scope = _load_x3_and_l2(repo, rd)
            if not x3_code and loaded_x3:
                x3_code = loaded_x3
            if not rgs and loaded_rgs:
                rgs = loaded_rgs
            if not pq and loaded_pq:
                pq = loaded_pq
            if auth_scope:
                auth = auth_scope
        per_lane.append(
            _classify_lane(
                lane=lane,
                x3_code=x3_code,
                runtime_generation_status=str(rgs) if rgs else None,
                authorization_scope=str(auth) if auth else None,
                product_quality_status=str(pq) if pq else None,
            ),
        )

    allow_lanes = [p["lane"] for p in per_lane if p["disposition_class"] == "ALLOW"]
    review_lanes = [p["lane"] for p in per_lane if p["disposition_class"] == "REVIEW"]
    blocked_lanes = [p["lane"] for p in per_lane if p["disposition_class"] == "BLOCKED"]
    mock_lanes = [p["lane"] for p in per_lane if p["disposition_class"] == "MOCK_PLUMBING_ONLY"]

    all_allow = len(allow_lanes) == len(GENERATED_LANE_IDS)
    any_review = bool(review_lanes)
    any_mock = bool(mock_lanes)
    any_blocked = bool(blocked_lanes)
    product_review_required = any_review or any_mock or any(
        p.get("product_review_required") for p in per_lane
    )
    structural_package_ok = all(p.get("can_structural_package") for p in per_lane)
    product_allow_claimed = all_allow and structural_package_ok and not any_blocked and not any_mock

    return {
        "schema": POLICY_SCHEMA,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_rules": {
            "ALLOW": "X3_ALLOW + REAL_LLM — eligible for product ALLOW rollup",
            "REVIEW": "X3_REVIEW* — structural package permitted; product_review_required=true; not product ALLOW",
            "BLOCKED": "X3_BLOCK* / BLOCKED — fails structural assembly",
            "MOCK_PLUMBING_ONLY": "mock/plumbing-only — not product ALLOW; product_review_required=true",
        },
        "per_lane": per_lane,
        "summary": {
            "allow_lanes": allow_lanes,
            "review_lanes": review_lanes,
            "blocked_lanes": blocked_lanes,
            "mock_plumbing_lanes": mock_lanes,
            "all_lanes_allow": all_allow,
            "product_review_required": product_review_required,
            "structural_package_ok": structural_package_ok,
            "product_allow_claimed": product_allow_claimed,
        },
        "explicit_non_claims": [
            "REVIEW lanes are not hidden; they are labeled product_review_required.",
            "MOCK/plumbing-only lanes cannot support product ALLOW.",
            "JD/briefing remain targeting-only; not proof.",
        ],
    }
