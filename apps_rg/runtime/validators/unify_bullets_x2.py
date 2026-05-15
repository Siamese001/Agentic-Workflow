"""Deterministic X2 gates for unify_bullets runtime slice."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    ALLOWED_MODELS,
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_json_parse_valid,
    check_judge_raw_responses_written,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
)

UNIFY_BULLET_IDS = (
    "bul_unify_001",
    "bul_unify_002",
    "bul_unify_003",
    "bul_unify_004",
    "bul_unify_005",
    "bul_unify_006",
)
DEFAULT_DISTRIBUTION = {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6}
PROTECTED_BULLET_DEFAULT = "bul_unify_006"
VALID_INTENSITIES = frozenset({"HEAVY", "MODERATE", "LIGHT_PROTECTED"})
FORBIDDEN_FACT_PREFIXES = ("bul_ibm_", "bul_insurtech_", "bul_ey_", "exp_ibm_", "exp_insurtech_", "exp_ey_")

REQUIRED_TOP_LEVEL = {
    "bullets",
    "selected_fact_plan",
    "claim_ledger",
    "jd_alignment",
    "gap_notes",
    "change_log",
    "rewrite_distribution",
    "self_check",
}


@dataclass
class X2GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def _combined_bullet_text(bullets: list[dict[str, Any]]) -> str:
    return "\n".join(str(b.get("bullet_text", "")) for b in bullets)


def _count_intensities(bullets: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets:
        intensity = str(bullet.get("rewrite_intensity", "")).upper()
        if intensity in counts:
            counts[intensity] += 1
    return counts


def _all_source_fact_ids(parsed: dict[str, Any] | None, claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for bullet in (parsed or {}).get("bullets") or []:
        for fid in bullet.get("source_fact_ids") or []:
            ids.add(str(fid))
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ids.add(str(fid))
        if claim.get("source_fact_id"):
            ids.add(str(claim["source_fact_id"]))
    return ids


def run_unify_bullets_x2_gates(
    *,
    bullets: list[dict[str, Any]],
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    jd_text: str,
    runtime_generation_status: str,
    artifacts_dir: Path | None = None,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    rewrite_distribution: dict[str, Any] | None = None,
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []

    def add(
        gate_id: str,
        passed: bool,
        observed: Any,
        threshold: Any = None,
        failure: str | None = None,
    ) -> None:
        gates.append(
            X2GateResult(
                gate_id=gate_id,
                gate_type="deterministic",
                pass_=passed,
                observed_value=observed,
                threshold=threshold,
                failure_reason=failure,
                evidence_ref=gate_id,
            )
        )

    combined = _combined_bullet_text(bullets)
    dist = rewrite_distribution or (parsed_output or {}).get("rewrite_distribution") or {}
    intensity_counts = _count_intensities(bullets)

    add("x2_unify_bullet_count_6", len(bullets) == 6, len(bullets), 6, "Must output exactly 6 bullets.")

    dist_valid = (
        dist.get("HEAVY") == DEFAULT_DISTRIBUTION["HEAVY"]
        and dist.get("MODERATE") == DEFAULT_DISTRIBUTION["MODERATE"]
        and dist.get("LIGHT_PROTECTED") == DEFAULT_DISTRIBUTION["LIGHT_PROTECTED"]
        and (dist.get("total") == 6 or sum(intensity_counts.values()) == 6)
    )
    add(
        "x2_unify_rewrite_distribution_valid",
        dist_valid and intensity_counts == {
            k: DEFAULT_DISTRIBUTION[k] for k in ("HEAVY", "MODERATE", "LIGHT_PROTECTED")
        },
        {"declared": dist, "observed": intensity_counts},
        DEFAULT_DISTRIBUTION,
        "Rewrite distribution must be 2 HEAVY, 3 MODERATE, 1 LIGHT_PROTECTED.",
    )

    add("x2_unify_max_heavy_3", intensity_counts["HEAVY"] <= 3, intensity_counts["HEAVY"], 3, "HEAVY count exceeds 3.")
    add(
        "x2_unify_min_light_protected_1",
        intensity_counts["LIGHT_PROTECTED"] >= 1,
        intensity_counts["LIGHT_PROTECTED"],
        1,
        "At least one LIGHT_PROTECTED bullet required.",
    )

    protected = next((b for b in bullets if b.get("bullet_id") == PROTECTED_BULLET_DEFAULT), None)
    protected_ok = bool(protected) and str(protected.get("rewrite_intensity", "")).upper() == "LIGHT_PROTECTED"
    protected_text = (protected or {}).get("bullet_text", "")
    metrics_ok = all(
        token in protected_text
        for token in ("$22M", "20%", "8", "28")
    )
    add(
        "x2_unify_protected_bullet_preserved_or_justified",
        protected_ok and metrics_ok,
        {"bullet_id": PROTECTED_BULLET_DEFAULT, "intensity": (protected or {}).get("rewrite_intensity")},
        "LIGHT_PROTECTED + core metrics",
        "Protected bul_unify_006 must be LIGHT_PROTECTED with $22M, 20%, and 8-to-28 scale.",
    )

    metrics_preserved = all(
        phrase in combined
        for phrase in ("$22M", "20%", "six months to three weeks")
    ) and ("8" in combined and "28" in combined)
    add(
        "x2_unify_metrics_preserved",
        metrics_preserved,
        combined[:200],
        "core metrics present",
        "Core metrics ($22M, 20%, 8 to 28, six months to three weeks) must appear in bullets.",
    )

    source_ids = _all_source_fact_ids(parsed_output, claim_ledger)
    scope_ok = bool(source_ids) and all(sid.startswith("bul_unify_") for sid in source_ids)
    scope_ok = scope_ok and not any(
        any(fid.startswith(prefix) for fid in source_ids) for prefix in FORBIDDEN_FACT_PREFIXES
    )
    scope_ok = scope_ok and all(
        sid in allowed_fact_ids or sid.split("_metric_")[0] in allowed_fact_ids for sid in source_ids
    )
    add("x2_unify_only_fact_scope", scope_ok, sorted(source_ids), "bul_unify_*", "Fact scope must be Unify bullets only.")

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    add("x2_no_ibm_fact_leakage", "bul_ibm_" not in serialized, "bul_ibm_", "absent", "IBM fact leakage detected.")
    add(
        "x2_no_insurtech_fact_leakage",
        "bul_insurtech_" not in serialized,
        "bul_insurtech_",
        "absent",
        "InsurTech fact leakage detected.",
    )
    add("x2_no_ey_fact_leakage", "bul_ey_" not in serialized, "bul_ey_", "absent", "EY fact leakage detected.")

    jd_copy, jd_phrase = has_jd_phrase_copy(combined, jd_text)
    add(
        "x2_no_jd_only_claims",
        not jd_copy,
        jd_phrase or "none",
        "no JD copy as proof",
        "JD phrase copied into bullet proof.",
    )

    required_bullet_ids = set(UNIFY_BULLET_IDS)
    output_ids = {b.get("bullet_id") for b in bullets}
    ledger_ids = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ledger_ids.add(str(fid).split("_metric_")[0])
    coverage_ok = required_bullet_ids <= output_ids and required_bullet_ids <= ledger_ids
    add(
        "x2_claim_ledger_coverage_100",
        coverage_ok and len(claim_ledger) >= 6,
        {"output_ids": sorted(output_ids), "ledger_roots": sorted(ledger_ids)},
        sorted(required_bullet_ids),
        "Every bul_unify_* bullet must appear in output and claim_ledger.",
    )

    metric_granular_ok = True
    for claim in claim_ledger:
        text = str(claim.get("claim_text", "")).lower()
        ids = claim.get("source_fact_ids") or []
        if "$22m" in text or "margin" in text:
            metric_granular_ok = metric_granular_ok and any("bul_unify_006" in str(i) for i in ids)
        if "six months" in text or "three weeks" in text:
            metric_granular_ok = metric_granular_ok and any("bul_unify_004" in str(i) for i in ids)
    add(
        "x2_metric_fact_id_granularity",
        metric_granular_ok,
        len(claim_ledger),
        "metric claims map to bul_unify_004/006",
        "Metric claims lack granular source_fact_ids.",
    )

    add(
        "x2_no_inline_source_tags",
        not INLINE_SOURCE_PATTERN.search(combined),
        "inline tags",
        "absent",
        "Inline source tags found in bullet text.",
    )
    add(
        "x2_no_first_person",
        not FIRST_PERSON_PATTERN.search(combined),
        "first person",
        "absent",
        "First-person pronoun found.",
    )
    add("x2_no_em_dash", EM_DASH not in combined, "em dash", "absent", "Em dash found.")
    filler_hit = next((f for f in GENERIC_FILLER if f.lower() in combined.lower()), None)
    add("x2_no_generic_filler", filler_hit is None, filler_hit or "none", "absent", "Generic filler phrase found.")

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_ok, json_reason, None, json_reason)

    provider_ok = provider_requested == provider_attempted if provider_requested else True
    add(
        "x2_provider_requested_attempted",
        provider_ok,
        f"{provider_requested}->{provider_attempted}",
        "match",
        "Provider requested does not match attempted.",
    )
    no_silent_mock = not (provider_requested == "qwen_vllm" and runtime_generation_status == "MOCKED")
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM when qwen requested",
        "Silent mock fallback detected.",
    )

    judges_ok, judges_reason = check_judge_rows_present(x1d_judges)
    add("x2_x1d_required_judges_present", judges_ok, judges_reason, REQUIRED_JUDGE_PROVIDERS, judges_reason)

    if x1d_judges:
        blocked_invalid = []
        for judge in x1d_judges:
            if str(judge.get("evaluator_mode", "")).startswith("BLOCKED_"):
                schema_ok, _ = check_judge_schema_valid(judge)
                if not schema_ok:
                    blocked_invalid.append(judge.get("provider_key"))
        add(
            "x2_x1d_schema_valid",
            not blocked_invalid,
            blocked_invalid,
            [],
            f"Blocked judges with invalid schema: {blocked_invalid}",
        )
    else:
        add("x2_x1d_schema_valid", False, "no judges", "present", "No X1D judges.")

    return gates
