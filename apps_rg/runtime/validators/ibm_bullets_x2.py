"""Deterministic X2 gates for ibm_bullets runtime slice (five IBM employment bullets)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
)

IBM_BULLET_IDS = (
    "bul_ibm_001",
    "bul_ibm_002",
    "bul_ibm_003",
    "bul_ibm_004",
    "bul_ibm_005",
)
IBM_DEFAULT_DISTRIBUTION = {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5}
VALID_INTENSITIES = frozenset({"HEAVY", "MODERATE", "LIGHT_PROTECTED"})

UNIFY_RUNTIME_TERM_PATTERNS = (
    r"\bagentic\s+ai\b",
    r"\bgraphrag\b",
    r"\bmulti[- ]?agent\s+orchestration\b",
    r"\bdeterministic\s+routing\b",
    r"\bsandboxed\s+execution\b",
    r"\breplayable\s+traces\b",
    r"\bgoverned\s+ai\s+runtime\b",
    r"\bprompt\s+assembly\b",
    r"\bc0\b",
    r"\bl2\b",
    r"\bexit\b",
    r"\buwg\b",
)

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

CORE_METRIC_TOKENS = ("$15M", "99.9%", "30%", "25%", "50%")


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


def _metric_granularity_ok(bullets: list[dict[str, Any]], claim_ledger: list[dict[str, Any]]) -> bool:
    """Metric-bearing bullet or ledger text must cite the matching bul_ibm_* root."""

    rules: list[tuple[tuple[str, ...], str]] = [
        (("99.9",), "bul_ibm_001"),
        (("30%", "30 %"), "bul_ibm_002"),
        (("25%", "25 %"), "bul_ibm_003"),
        (("50%", "50 %"), "bul_ibm_004"),
        (("$15m", "$15 m"), "bul_ibm_005"),
    ]

    def check_text(text: str, ids_raw: list[str]) -> bool:
        tl = text.lower()
        ids_lower = [i.lower() for i in ids_raw]
        for needles, root in rules:
            if any(n.lower() in tl for n in needles):
                if not any(root in i for i in ids_lower):
                    return False
        return True

    for b in bullets:
        if not check_text(str(b.get("bullet_text", "")), [str(i) for i in (b.get("source_fact_ids") or [])]):
            return False
    for c in claim_ledger:
        if not check_text(str(c.get("claim_text", "")), [str(i) for i in (c.get("source_fact_ids") or [])]):
            return False
    return True


def run_ibm_bullets_x2_gates(
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
    del artifacts_dir  # API parity with unify_bullets_x2; unused here.
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
    combined_lower = combined.lower()
    dist = rewrite_distribution or (parsed_output or {}).get("rewrite_distribution") or {}
    intensity_counts = _count_intensities(bullets)

    add("x2_ibm_bullet_count_5", len(bullets) == 5, len(bullets), 5, "Must output exactly 5 IBM bullets.")

    dist_valid = (
        dist.get("HEAVY") == IBM_DEFAULT_DISTRIBUTION["HEAVY"]
        and dist.get("MODERATE") == IBM_DEFAULT_DISTRIBUTION["MODERATE"]
        and dist.get("LIGHT_PROTECTED") == IBM_DEFAULT_DISTRIBUTION["LIGHT_PROTECTED"]
        and (dist.get("total") == 5 or sum(intensity_counts.values()) == 5)
    )
    add(
        "x2_ibm_rewrite_distribution_valid",
        dist_valid
        and intensity_counts["HEAVY"] == 0
        and intensity_counts["MODERATE"] == 3
        and intensity_counts["LIGHT_PROTECTED"] == 2,
        {"declared": dist, "observed": intensity_counts},
        IBM_DEFAULT_DISTRIBUTION,
        "IBM rewrite distribution must be 0 HEAVY, 3 MODERATE, 2 LIGHT_PROTECTED.",
    )

    add(
        "x2_ibm_heavy_rewrites_zero",
        intensity_counts["HEAVY"] == 0,
        intensity_counts["HEAVY"],
        0,
        "HEAVY rewrites are forbidden for IBM bullets.",
    )

    metrics_preserved = (
        ("$15M" in combined or "$15m" in combined_lower)
        and "99.9%" in combined
        and "30%" in combined
        and "25%" in combined
        and "50%" in combined
    )
    add(
        "x2_ibm_metrics_preserved",
        metrics_preserved,
        combined[:240],
        CORE_METRIC_TOKENS,
        "Core IBM metrics ($15M, 99.9%, 30%, 25%, 50%) must appear in bullet text.",
    )

    source_ids = _all_source_fact_ids(parsed_output, claim_ledger)
    scope_ok = bool(source_ids) and all(str(sid).startswith("bul_ibm_") for sid in source_ids)
    scope_ok = scope_ok and all(
        sid.split("_metric_")[0] in allowed_fact_ids or sid in allowed_fact_ids for sid in source_ids
    )
    add("x2_ibm_only_fact_scope", scope_ok, sorted(source_ids), "bul_ibm_*", "Fact scope must be IBM bullets only.")

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    add(
        "x2_no_unify_fact_leakage",
        "bul_unify_" not in serialized,
        "bul_unify_",
        "absent",
        "Unify bullet fact leakage detected.",
    )

    term_hits = [pat for pat in UNIFY_RUNTIME_TERM_PATTERNS if re.search(pat, combined, re.I)]
    add(
        "x2_no_unify_runtime_terms",
        not term_hits,
        term_hits,
        [],
        "Unify runtime vocabulary leaked into IBM bullets.",
    )

    add(
        "x2_no_agentic_inflation",
        not re.search(r"\bagentic\b", combined, re.I),
        "agentic token",
        "absent",
        "Agentic inflation language in IBM bullets.",
    )

    jd_copy, jd_phrase = has_jd_phrase_copy(combined, jd_text)
    add(
        "x2_no_jd_only_claims",
        not jd_copy,
        jd_phrase or "none",
        "no JD copy as proof",
        "JD phrase copied into bullet proof.",
    )

    required_bullet_ids = set(IBM_BULLET_IDS)
    output_ids = {b.get("bullet_id") for b in bullets}
    ledger_roots: set[str] = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ledger_roots.add(str(fid).split("_metric_")[0])
    coverage_ok = required_bullet_ids <= output_ids and required_bullet_ids <= ledger_roots
    add(
        "x2_claim_ledger_coverage_100",
        coverage_ok and len(claim_ledger) >= 5,
        {"output_ids": sorted(output_ids), "ledger_roots": sorted(ledger_roots)},
        sorted(required_bullet_ids),
        "Every bul_ibm_* bullet must appear in output and claim_ledger.",
    )

    add(
        "x2_metric_fact_id_granularity",
        _metric_granularity_ok(bullets, claim_ledger),
        len(claim_ledger),
        "metric claims map to bul_ibm_*",
        "Metric claims lack matching bul_ibm_* source_fact_ids in claim_ledger.",
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


__all__ = [
    "IBM_BULLET_IDS",
    "IBM_DEFAULT_DISTRIBUTION",
    "REQUIRED_TOP_LEVEL",
    "run_ibm_bullets_x2_gates",
]
