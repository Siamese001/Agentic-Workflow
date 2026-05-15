"""Deterministic X2 gates for headline runtime slice (single X | Y | Z line)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
)

# Metrics and numeric proof patterns (headline must avoid all).
_METRIC_RE = re.compile(
    r"(\$\s*\d|\d+\s*%|%\d|\b\d{1,3}\s*m\b|\d+\s*→\s*\d+|\b99\.|\b\d{1,2}\.\d+\s*%)",
    re.IGNORECASE,
)


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


def _ledger_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ids.add(str(fid).split("_metric_")[0])
    return ids


def headline_word_count(headline: str) -> int:
    flat = re.sub(r"\|", " ", headline.strip())
    return len([w for w in flat.split() if w.strip()])


def run_headline_x2_gates(
    *,
    headline_line: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    jd_text: str,
    target_company: str,
    resume_support_blob: str,
    employer_names_lower: list[str],
    allowed_fact_ids: set[str],
    runtime_generation_status: str,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
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

    h = (headline_line or "").strip()
    one_line = "\n" not in h and "\r" not in h
    add(
        "x2_headline_exactly_one_line",
        bool(h) and one_line,
        "newlines" if not one_line else "ok",
        "none",
        None if h and one_line else "Headline must be a single line.",
    )

    pipe_ok = False
    pipe_reason = None
    if h.count("|") != 2:
        pipe_reason = "must have exactly two pipe separators"
    else:
        parts = [p.strip() for p in h.split("|")]
        pipe_ok = len(parts) == 3 and all(parts) and all("|" not in p for p in parts)
        if not pipe_ok:
            pipe_reason = "three non-empty segments required"
    add(
        "x2_headline_pipe_three_segments",
        pipe_ok,
        pipe_reason or "ok",
        "X | Y | Z",
        None if pipe_ok else pipe_reason,
    )

    wc = headline_word_count(h) if h else 0
    wc_ok = 8 <= wc <= 11
    add(
        "x2_headline_word_count_8_to_11",
        wc_ok,
        wc,
        "8..11",
        None if wc_ok else "Word count out of range (count words with pipes as spaces).",
    )

    metric_hit = _METRIC_RE.search(h)
    add(
        "x2_headline_no_metrics",
        metric_hit is None,
        metric_hit.group(0) if metric_hit else "ok",
        "none",
        None if metric_hit is None else "Metric or numeric proof token in headline.",
    )

    hl = h.lower()
    blob = resume_support_blob.lower()
    company_hit = None
    for name in employer_names_lower:
        if len(name) >= 4 and name in hl:
            company_hit = name
            break
    add(
        "x2_headline_no_company_names",
        company_hit is None,
        company_hit or "ok",
        "no employers",
        None if company_hit is None else "Employer or company name appears in headline.",
    )

    add(
        "x2_no_first_person",
        not FIRST_PERSON_PATTERN.search(h),
        "first person",
        "absent",
        "First person in headline.",
    )
    add("x2_no_em_dash", EM_DASH not in h, "em dash", "absent", "Em dash in headline.")
    add(
        "x2_no_inline_source_tags",
        not INLINE_SOURCE_PATTERN.search(h),
        "tags",
        "absent",
        "Inline source tags in headline.",
    )

    tc = (target_company or "").strip().lower()
    tc_bad = bool(tc) and len(tc) >= 6 and tc in hl
    add(
        "x2_no_target_company_as_experience",
        not tc_bad,
        tc if tc_bad else "ok",
        "not in headline",
        None if not tc_bad else "Target company name appears in headline.",
    )

    jd_copy, jd_phrase = has_jd_phrase_copy(h, jd_text, max_words=4)
    jd_only = jd_copy and jd_phrase and jd_phrase not in blob
    add(
        "x2_no_jd_only_claims",
        not jd_only,
        jd_phrase or "ok",
        "no jd-only",
        None if not jd_only else "JD phrase copied without resume support.",
    )

    ledger_ids = _ledger_fact_ids(claim_ledger)
    supported = bool(claim_ledger) and bool(ledger_ids) and ledger_ids <= allowed_fact_ids
    add(
        "x2_headline_source_supported",
        supported,
        sorted(ledger_ids),
        "bul_* subset",
        None if supported else "claim_ledger must cite allowed bul_* facts only.",
    )

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_ok, json_reason, None, json_reason)

    provider_ok = provider_requested == provider_attempted if provider_requested else True
    add(
        "x2_provider_requested_attempted",
        provider_ok,
        f"{provider_requested}->{provider_attempted}",
        "match",
        "Provider mismatch.",
    )
    no_silent_mock = not (provider_requested == "qwen_vllm" and runtime_generation_status == "MOCKED")
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM",
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
            f"Blocked judges invalid schema: {blocked_invalid}",
        )
    else:
        add("x2_x1d_schema_valid", False, "no judges", "present", "No judges.")

    exec_ok = bool(h) and len(h) <= 140
    add(
        "x2_headline_executive_length",
        exec_ok,
        len(h),
        "<=140 chars",
        None if exec_ok else "Headline too long for ATS headline slot.",
    )

    return gates


__all__ = ["run_headline_x2_gates", "X2GateResult", "headline_word_count"]
