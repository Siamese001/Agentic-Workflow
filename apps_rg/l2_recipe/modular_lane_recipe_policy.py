"""Recipe-level PASS policy for modular R4 section lanes (apps_rg only).

Classifies each lane row in ``section_provider_calls.json`` for **Phase 1 product**
runs. Phase 0 synthetic assembly records skip product enforcement via
``enforce_product_lane_requirements=False``.
"""

from __future__ import annotations

from typing import Any, Final, Literal, Mapping

LaneRecipeEligibility = Literal["FATAL", "DEGRADED_ALLOWED", "PASS"]

RECIPE_PASS_POLICY_VERSION: Final[str] = "apps_rg.modular_lane_recipe_policy.v1"

_FATAL_GENERATION_STATUSES: Final[frozenset[str]] = frozenset({"MOCKED", "MISSING_LANE_RUN"})
_FATAL_SCHEMA_STATUSES: Final[frozenset[str]] = frozenset({"lane_x2_fail", "missing"})
_FATAL_DECISIVE_CODES: Final[frozenset[str]] = frozenset(
    {
        "X3_REVIEW_MOCKED_PLUMBING_ONLY",
        "PHASE1_NO_RUN_DIR",
        "PHASE0_NO_PROVIDER",
        "UNKNOWN",
    },
)
# Deterministic / security-style blocks that cannot be waived by judge availability.
_FATAL_DECISIVE_EVEN_IF_X2_PASS: Final[frozenset[str]] = frozenset(
    {
        "X3_BLOCKED_DETERMINISTIC_GATES",
    },
)

_DEGRADED_IF_X2_PASS: Final[frozenset[str]] = frozenset(
    {
        "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        "X3_REVIEW_JUDGE_SOFT_FAIL",
        "X3_BLOCK",
        "X3_REVIEW_PRODUCT_QUALITY",
        "X3_REVIEW_SECTION_JUDGE_STATUS",
    },
)


def classify_modular_lane_recipe_eligibility(
    lane_receipt: Mapping[str, Any],
    *,
    enforce_product_lane_requirements: bool,
) -> LaneRecipeEligibility:
    """Return lane-level eligibility under modular recipe policy v1."""
    if not enforce_product_lane_requirements:
        return "PASS"

    gen = str(lane_receipt.get("generation_status") or "").strip()
    attempted = lane_receipt.get("provider_call_attempted")
    schema = str(lane_receipt.get("section_schema_validation_status") or "").strip()
    code = str(lane_receipt.get("decisive_reason_code") or "").strip()

    if gen in _FATAL_GENERATION_STATUSES:
        return "FATAL"
    if gen and gen != "REAL_LLM":
        return "FATAL"
    if attempted is not True:
        return "FATAL"
    if schema in _FATAL_SCHEMA_STATUSES:
        return "FATAL"
    if schema not in ("lane_x2_pass",):
        return "FATAL"

    if code in _FATAL_DECISIVE_EVEN_IF_X2_PASS:
        return "FATAL"
    if code in _FATAL_DECISIVE_CODES:
        return "FATAL"

    if code == "X3_ALLOW":
        return "PASS"
    if code in _DEGRADED_IF_X2_PASS:
        return "DEGRADED_ALLOWED"

    return "FATAL"


def _fatal_reason(rec: Mapping[str, Any]) -> str:
    return (
        f"generation_status={rec.get('generation_status')!r} "
        f"schema={rec.get('section_schema_validation_status')!r} "
        f"attempted={rec.get('provider_call_attempted')!r} "
        f"x3={rec.get('decisive_reason_code')!r}"
    )


def summarize_modular_lane_recipe_policy(
    records: list[dict[str, Any]],
    *,
    enforce_product_lane_requirements: bool,
) -> dict[str, Any]:
    """Build receipt fields for ``section_provider_calls.json`` / ``extras``."""
    fatal: list[dict[str, str]] = []
    degraded: list[dict[str, str]] = []
    det_pass = 0
    judge_blocked = 0

    for raw in records:
        if not isinstance(raw, dict):
            continue
        lane = str(raw.get("section_lane") or "")
        code = str(raw.get("decisive_reason_code") or "")
        if str(raw.get("section_schema_validation_status") or "") == "lane_x2_pass":
            det_pass += 1
        if code == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED":
            judge_blocked += 1

        elig = classify_modular_lane_recipe_eligibility(
            raw,
            enforce_product_lane_requirements=enforce_product_lane_requirements,
        )
        if elig == "FATAL":
            fatal.append(
                {
                    "section_lane": lane,
                    "reason": _fatal_reason(raw),
                    "decisive_reason_code": code,
                },
            )
        elif elig == "DEGRADED_ALLOWED":
            degraded.append(
                {
                    "section_lane": lane,
                    "decisive_reason_code": code,
                    "note": "Lane deterministic X2 passed; X3 reflects judge/review signal only (policy v1).",
                },
            )

    why = ""
    if degraded and not fatal:
        why = (
            "Recipe PASS allowed under v1: every required generated lane has REAL_LLM output, "
            "provider was attempted, and lane deterministic X2 passed. "
            "Remaining signals are classified as non-fatal judge/provider degradation "
            "(e.g. external judge rate-limited or soft-fail) — not deterministic section failure."
        )

    return {
        "recipe_pass_policy_version": RECIPE_PASS_POLICY_VERSION,
        "enforce_product_lane_requirements": enforce_product_lane_requirements,
        "fatal_lane_failures": fatal,
        "degraded_allowed_lane_warnings": degraded,
        "judge_provider_blocked_count": judge_blocked,
        "deterministic_lane_pass_count": det_pass,
        "why_recipe_pass_allowed_despite_lane_warnings": why,
        "deterministic_gates_required_for_product_pass": True,
        "final_rg_output_schema_required_for_recipe_pass": True,
    }


__all__ = [
    "LaneRecipeEligibility",
    "RECIPE_PASS_POLICY_VERSION",
    "classify_modular_lane_recipe_eligibility",
    "summarize_modular_lane_recipe_policy",
]
