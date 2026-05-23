"""Deterministic X2 gates for headline runtime slice (SVP Engineering | X | Y | Z)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

from apps_rg.runtime.reasoning.prompt_control_proof import reasoning_receipt_denies_quality_certification
from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    check_target_title_inflation,
    has_jd_phrase_copy,
)

# Metrics and numeric proof patterns (headline must avoid all).
_METRIC_RE = re.compile(
    r"(\$\s*\d|\d+\s*%|%\d|\b\d{1,3}\s*m\b|\d+\s*→\s*\d+|\b99\.|\b\d{1,2}\.\d+\s*%)",
    re.IGNORECASE,
)

# Obvious ATS keyword-bag / stuffing patterns (deterministic reject; prefer false positives over stuffing).
_KEYWORD_STUFF_RE = re.compile(
    r"(?:\bai\s+ml\s+cloud\s+data\b|\bai\s+ml\s+cloud\b|\bdigital\s+transformation\b|"
    r"\binnovation\s+leadership\b|\btechnology\s+evangelist\b|\bthought\s+leader\b|\bai\s+evangelist\b|"
    r"\bstrategic\s+leader\b|\bvisionary\b|\bthought\s+leaders?\b|\bdigital\s+transformations?\b|"
    r"\binnovation\s+leaderships?\b|\btechnology\s+evangelists?\b|\bai\s+evangelists?\b)",
    re.IGNORECASE,
)

_SEGMENT_BANNED_FILLERS_RE = re.compile(
    r"(?:\bvisionary\b|\bthought\s+leader\b|\binnovation\s+leadership\b|\bdigital\s+transformation\b|"
    r"\bstrategic\s+leader\b|\bai\s+evangelist\b|\btechnology\s+evangelist\b)",
    re.IGNORECASE,
)

_EXTRA_HYPE_MARKERS_RE = re.compile(
    r"(?:\bFortune\s+500\b|\b10x\b|\b24x7\b|\b24/7\b)",
    re.IGNORECASE,
)

_HEADLINE_SCHEMA_KEYS = frozenset(
    {
        "headline_line",
        "selected_fact_plan",
        "claim_ledger",
        "jd_alignment",
        "gap_notes",
        "change_log",
        "self_check",
    }
)


def _model_jd_alignment_for_proof(parsed_output: dict[str, Any] | None) -> dict[str, Any] | None:
    """Prefer frozen ``raw_jd_alignment`` (pre-normalize model emission) for proof-boolean gates."""
    if not isinstance(parsed_output, dict):
        return None
    raw = parsed_output.get("raw_jd_alignment")
    if isinstance(raw, dict):
        return raw
    jd = parsed_output.get("jd_alignment")
    return jd if isinstance(jd, dict) else None


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


def _ledger_fact_ids(claim_ledger: list[Any]) -> set[str]:
    ids: set[str] = set()
    for claim in claim_ledger or []:
        if not isinstance(claim, dict):
            continue
        for fid in claim.get("source_fact_ids") or []:
            ids.add(str(fid).split("_metric_")[0])
    return ids


def headline_word_count(headline: str) -> int:
    flat = re.sub(r"\|", " ", headline.strip())
    return len([w for w in flat.split() if w.strip()])


def validate_raw_headline_claim_ledger(parsed: dict[str, Any] | None) -> tuple[bool, str, Any]:
    """Schema for model-emitted JSON **before** lane normalization.

    ``claim_ledger`` must be a non-empty list of objects with non-empty ``claim_text`` and non-empty
    ``source_fact_ids`` lists. A flat list of ``bul_*`` strings is invalid for proof-eligible runs.
    """
    if not isinstance(parsed, dict):
        return False, "parsed_not_dict", None
    cl = parsed.get("claim_ledger", None)
    if cl is None:
        return False, "claim_ledger_key_missing", None
    if not isinstance(cl, list):
        return False, "claim_ledger_not_array", type(cl).__name__
    if len(cl) == 0:
        return False, "claim_ledger_empty_array", []
    if all(isinstance(x, str) for x in cl):
        return False, "claim_ledger_flat_string_fact_ids_invalid", cl
    if not all(isinstance(x, dict) for x in cl):
        return False, "claim_ledger_rows_must_be_objects", cl
    for i, row in enumerate(cl):
        ct = str(row.get("claim_text") or "").strip()
        if not ct:
            return False, f"row_{i}_missing_claim_text", row
        ids = row.get("source_fact_ids")
        if not isinstance(ids, list) or not bool(ids):
            return False, f"row_{i}_invalid_source_fact_ids", row
    return True, "ok", None


def headline_runtime_self_check_truth(
    headline_line: str,
    *,
    target_company: str,
    employer_names_lower: list[str],
) -> dict[str, Any]:
    """Deterministic self-check slice comparable to model ``self_check`` JSON."""
    h = (headline_line or "").strip()
    wc = headline_word_count(h)
    sep = " | "
    sep_count = h.count(sep)
    parts = [p.strip() for p in h.split(sep)] if sep_count >= 3 else []
    segment_count = len(parts) if sep_count == 3 else 0
    fixed_prefix = h.startswith("SVP Engineering | ")
    hl_lower = h.lower()
    tc = (target_company or "").strip().lower()
    tc_bad = bool(tc) and len(tc) >= 6 and tc in hl_lower
    emp_hit = False
    for name in employer_names_lower:
        if len(name) >= 4 and name in hl_lower:
            emp_hit = True
            break
    return {
        "word_count": wc,
        "segment_count": segment_count,
        "separator_count": sep_count,
        "word_count_in_range": 10 <= wc <= 13,
        "fixed_prefix": fixed_prefix,
        "no_metrics": _METRIC_RE.search(h) is None,
        "no_employer_names": not emp_hit,
        "no_company_names": not tc_bad,
    }


def polish_claim_text_when_headline_has_no_metrics(headline_line: str, claim_text: str) -> str:
    """Strip metric phrasing from ledger ``claim_text`` only when that row itself carries metric tokens.

    Headline_line stays metric-free; do not strip bare ``%`` from segment claims unless the row is metric-heavy
    (avoids decoupling ``claim_text`` from metric-bearing ``source_fact_ids``).
    """
    h = (headline_line or "").strip()
    t = str(claim_text or "").strip()
    if not t or _METRIC_RE.search(h) or not _METRIC_RE.search(t):
        return t
    out = re.sub(
        r"\s+operating\s+at\s+\d+(?:\.\d+)?%\s+uptime\b(?:\s+[^\.]*)?",
        "",
        t,
        flags=re.IGNORECASE,
    )
    out = re.sub(r"\bat\s+\d+(?:\.\d+)?%\s+uptime\b", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\d+(?:\.\d+)?\s*%", "", out)
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r"\s+\.", ".", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def run_headline_x2_gates(
    *,
    headline_line: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    jd_text: str,
    target_company: str,
    target_title: str = "",
    resume_support_blob: str,
    employer_names_lower: list[str],
    allowed_fact_ids: set[str],
    runtime_generation_status: str,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    companion_context: str = "",
    candidate_name_tokens: list[str] | None = None,
    raw_model_parsed_before_normalize: dict[str, Any] | None = None,
    reasoning_execution_receipt: dict[str, Any] | None = None,
    artifacts_dir: Any | None = None,
    text_claim_coverage: dict[str, Any] | None = None,
    srfs_source_fact_slice_gate_active: bool = False,
    proof_pool_metadata: dict[str, Any] | None = None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
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

    _sep = " | "
    pipe_ok = False
    pipe_reason = None
    if h.count(_sep) != 3:
        pipe_reason = f'must have exactly three {_sep!r} separators (four segments)'
    elif not h.startswith("SVP Engineering | "):
        pipe_reason = 'headline_line must start with exact prefix "SVP Engineering | "'
    else:
        parts = [p.strip() for p in h.split(_sep)]
        if len(parts) != 4 or not all(parts):
            pipe_reason = "four non-empty segments required when splitting on ' | '"
        elif parts[0] != "SVP Engineering":
            pipe_reason = "first segment must be exactly SVP Engineering"
        else:
            pipe_ok = True
    add(
        "x2_headline_pipe_four_segments",
        pipe_ok,
        pipe_reason or "ok",
        "SVP Engineering | X | Y | Z",
        None if pipe_ok else pipe_reason,
    )

    seg_issues: list[str] = []
    if pipe_ok:
        parts = [p.strip() for p in h.split(_sep)]
        for si in (1, 2, 3):
            seg = parts[si]
            wc_seg = len(seg.split())
            if wc_seg < 2 or wc_seg > 5:
                seg_issues.append(f"seg{si + 1}_words:{wc_seg}")
            if seg.count(",") >= 2:
                seg_issues.append(f"seg{si + 1}_comma_heavy")
            if _SEGMENT_BANNED_FILLERS_RE.search(seg):
                seg_issues.append(f"seg{si + 1}_banned_filler")
        uniq_low = [parts[i].lower() for i in (1, 2, 3)]
        if len(set(uniq_low)) < 3:
            seg_issues.append("duplicate_segment_theme")
    add(
        "x2_headline_segments_quality",
        not seg_issues,
        seg_issues or "ok",
        "segments 2–4: 2–5 words, low comma load, no duplicate themes, no banned fillers",
        None if not seg_issues else "Segment quality gate failed.",
    )

    digit_hit = re.search(r"\d", h)
    add(
        "x2_headline_no_digit_tokens",
        digit_hit is None,
        digit_hit.group(0) if digit_hit else "ok",
        "no ASCII digits",
        None if digit_hit is None else "Digit-bearing token in headline.",
    )

    curr_pct_hit = bool(re.search(r"[\$%]", h))
    add(
        "x2_headline_no_currency_percent_literals",
        not curr_pct_hit,
        "$ or %" if curr_pct_hit else "ok",
        "none",
        None if not curr_pct_hit else "$ or % literal in headline.",
    )

    hype_hit = _EXTRA_HYPE_MARKERS_RE.search(h)
    add(
        "x2_headline_no_hype_markers",
        hype_hit is None,
        hype_hit.group(0) if hype_hit else "ok",
        "no Fortune 500 / 10x / 24x7 patterns",
        None if hype_hit is None else "Banned hype/numeric-adjacent marker in headline.",
    )

    stuff_hit = _KEYWORD_STUFF_RE.search(h)
    add(
        "x2_headline_no_keyword_stuffing_heuristic",
        stuff_hit is None,
        stuff_hit.group(0) if stuff_hit else "ok",
        "no banned filler patterns",
        None if stuff_hit is None else "Keyword-stuffing or banned filler phrase detected in headline.",
    )

    wc = headline_word_count(h) if h else 0
    wc_ok = 10 <= wc <= 13
    add(
        "x2_headline_word_count_10_to_13",
        wc_ok,
        wc,
        "10..13",
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
        "x2_headline_no_unsupported_employer_names",
        company_hit is None,
        company_hit or "ok",
        "no employers",
        None if company_hit is None else "Employer or company name appears in headline.",
    )

    name_tokens: set[str] = set()
    for raw_tok in candidate_name_tokens or []:
        t = str(raw_tok).strip()
        if len(t) >= 3:
            name_tokens.add(t.lower())
    rs = (resume_support_blob or "").strip()
    if not name_tokens and rs.startswith("{"):
        try:
            cand = json.loads(rs)
        except json.JSONDecodeError:
            cand = None
        if isinstance(cand, dict):
            cn = str(cand.get("candidate_name") or "").strip()
            hdr_nm = ""
            hdr_obj = cand.get("header")
            if isinstance(hdr_obj, dict):
                hdr_nm = str(hdr_obj.get("name") or "").strip()
            for nm in (cn, hdr_nm):
                if not nm:
                    continue
                for part in nm.split():
                    tok = re.sub(r"^[^\w]+|[^\w]+$", "", part)
                    if len(tok) >= 3:
                        name_tokens.add(tok.lower())
    leaked = sorted(t for t in name_tokens if t and t in hl)
    add(
        "x2_headline_no_candidate_name_tokens",
        len(leaked) == 0,
        leaked or "ok",
        "no personal-name tokens",
        None if not leaked else f"Personal name token(s) in headline: {leaked}",
    )

    fp_hit = FIRST_PERSON_PATTERN.search(h)
    fp_ok = fp_hit is None
    add(
        "x2_no_first_person",
        fp_ok,
        "absent" if fp_ok else "first_person_detected",
        "absent",
        None if fp_ok else "First person in headline.",
    )
    em_bad = EM_DASH in h
    add(
        "x2_no_em_dash",
        not em_bad,
        "absent" if not em_bad else "em_dash_present",
        "absent",
        None if not em_bad else "Em dash in headline.",
    )
    tag_hit = INLINE_SOURCE_PATTERN.search(h)
    tags_ok = tag_hit is None
    add(
        "x2_headline_no_inline_source_tags",
        tags_ok,
        "absent" if tags_ok else "inline_source_tag_detected",
        "absent",
        None if tags_ok else "Inline source tags in headline.",
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

    ledger_rows = [cl for cl in (claim_ledger or []) if isinstance(cl, dict)]
    ledger_has_rows = bool(ledger_rows) and all(isinstance(cl.get("source_fact_ids"), list) for cl in ledger_rows)
    rows_have_ids = bool(ledger_rows) and all(bool(cl.get("source_fact_ids")) for cl in ledger_rows)
    add(
        "x2_headline_claim_ledger_rows_present",
        ledger_has_rows and rows_have_ids,
        len(ledger_rows),
        ">=1 dict rows with non-empty source_fact_ids",
        None
        if ledger_has_rows and rows_have_ids
        else "claim_ledger must contain dict rows with non-empty source_fact_ids (no fabrication).",
    )

    seg_decomp_ok = True
    seg_decomp_obs: Any = "n/a"
    if pipe_ok:
        parts_xyz = [p.strip() for p in h.split(_sep)][1:4]
        expected_seg = {p.lower() for p in parts_xyz}
        if len(ledger_rows) < 3:
            seg_decomp_ok = False
            seg_decomp_obs = {"row_count": len(ledger_rows), "expected_segments": parts_xyz}
        else:
            matched: set[str] = set()
            for row in ledger_rows:
                ct = str(row.get("claim_text") or "").strip().lower()
                if ct in expected_seg:
                    matched.add(ct)
            seg_decomp_ok = matched == expected_seg
            seg_decomp_obs = {
                "matched_segments": sorted(matched),
                "expected_segments": parts_xyz,
                "row_count": len(ledger_rows),
            }
    add(
        "x2_headline_claim_ledger_segment_decomposition",
        seg_decomp_ok,
        seg_decomp_obs,
        ">=3 rows with claim_text matching X/Y/Z segments",
        None
        if seg_decomp_ok
        else "claim_ledger must include one row per positioning segment (X, Y, Z).",
    )

    dropped_rows = 0
    if isinstance(parsed_output, dict):
        dropped_rows = int(parsed_output.get("_headline_ledger_rows_dropped") or 0)
    add(
        "x2_headline_claim_ledger_no_silent_row_drop",
        dropped_rows == 0,
        dropped_rows,
        0,
        None
        if dropped_rows == 0
        else f"{dropped_rows} claim_ledger row(s) removed during normalize (no allowed source_fact_ids).",
    )

    tcov = text_claim_coverage if isinstance(text_claim_coverage, dict) else None
    if tcov and tcov.get("schema") == "headline_text_claim_coverage_v1":
        tcov_ok = bool(tcov.get("overall_pass"))
        tcov_obs: Any = tcov.get("segments")
        tcov_fail = None if tcov_ok else "Segment-level text_claim_coverage failed."
    else:
        tcov_ok = False
        tcov_obs = "missing_or_invalid_text_claim_coverage"
        tcov_fail = "text_claim_coverage must be headline_text_claim_coverage_v1 with overall_pass"
    add(
        "x2_headline_text_claim_coverage_integrity",
        tcov_ok,
        tcov_obs,
        "each X/Y/Z segment has matching claim_ledger support",
        tcov_fail,
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

    sfp = parsed_output.get("selected_fact_plan") if isinstance(parsed_output, dict) else None
    req_ids = set(sfp.get("required_fact_ids") or []) if isinstance(sfp, dict) else set()
    plan_matches = req_ids == ledger_ids and bool(req_ids)
    add(
        "x2_headline_selected_fact_plan_matches_ledger",
        plan_matches,
        {"required_fact_ids": sorted(req_ids), "ledger_union": sorted(ledger_ids)},
        "exact set equality",
        None if plan_matches else "selected_fact_plan.required_fact_ids must equal claim_ledger union.",
    )

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_ok, json_reason, None, json_reason)

    if runtime_generation_status != "REAL_LLM":
        add(
            "x2_headline_prompt_reasoning_receipt_clean",
            True,
            "n/a_not_real_llm",
            None,
            None,
        )
        add(
            "x2_headline_raw_model_schema_valid",
            True,
            "n/a_not_real_llm",
            None,
            None,
        )
        add(
            "x2_headline_self_check_consistent",
            True,
            "n/a_not_real_llm",
            None,
            None,
        )
    else:
        denied, deny_reasons = reasoning_receipt_denies_quality_certification(reasoning_execution_receipt)
        add(
            "x2_headline_prompt_reasoning_receipt_clean",
            not denied,
            deny_reasons or "ok",
            "no_aggregate_blocked_no_quality_denial",
            None if not denied else "reasoning_execution_receipt blocked certification for required controls",
        )
        raw_ok, raw_detail, raw_obs = validate_raw_headline_claim_ledger(raw_model_parsed_before_normalize)
        add(
            "x2_headline_raw_model_schema_valid",
            raw_ok,
            raw_detail if raw_ok else raw_obs,
            "dict_rows_with_claim_text_and_source_fact_ids",
            None if raw_ok else f"Raw model claim_ledger invalid: {raw_detail}",
        )
        sc_model = parsed_output.get("self_check") if isinstance(parsed_output, dict) else None
        rt_sc = headline_runtime_self_check_truth(
            h, target_company=target_company, employer_names_lower=employer_names_lower
        )
        sc_failures: list[str] = []
        if not isinstance(sc_model, dict):
            sc_failures.append("self_check_missing_or_not_object")
        else:
            comparable_keys = (
                "word_count",
                "segment_count",
                "separator_count",
                "word_count_in_range",
                "fixed_prefix",
                "no_metrics",
                "no_employer_names",
                "no_company_names",
            )
            for key in comparable_keys:
                if key not in sc_model:
                    sc_failures.append(f"model_missing:{key}")
                    continue
                mv = sc_model[key]
                rv = rt_sc[key]
                if key == "word_count":
                    try:
                        mv_int = int(float(mv))
                    except (TypeError, ValueError):
                        sc_failures.append(f"{key}:non_numeric_model_value")
                        continue
                    if mv_int != int(rv):
                        sc_failures.append(f"{key}:model={mv_int}_runtime={int(rv)}")
                    continue
                if isinstance(mv, bool) and isinstance(rv, bool):
                    if mv != rv:
                        sc_failures.append(f"{key}:model={mv}_runtime={rv}")
                    continue
                if mv != rv:
                    sc_failures.append(f"{key}:model={mv!r}_runtime={rv!r}")
        add(
            "x2_headline_self_check_consistent",
            not sc_failures,
            {"runtime": rt_sc, "model": sc_model if isinstance(sc_model, dict) else None},
            rt_sc,
            None if not sc_failures else "; ".join(sc_failures),
        )

    schema_ok = isinstance(parsed_output, dict) and _HEADLINE_SCHEMA_KEYS <= set(parsed_output.keys())
    missing = sorted(_HEADLINE_SCHEMA_KEYS - set(parsed_output.keys())) if isinstance(parsed_output, dict) else sorted(_HEADLINE_SCHEMA_KEYS)
    add(
        "x2_headline_schema_valid",
        schema_ok,
        "ok" if schema_ok else missing,
        sorted(_HEADLINE_SCHEMA_KEYS),
        None if schema_ok else f"Missing headline schema keys: {missing}",
    )

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
                judge_schema_ok, _ = check_judge_schema_valid(judge)
                if not judge_schema_ok:
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

    from apps_rg.runtime.sections.section_product_shape_ssot import HEADLINE_MAX_CHARS

    exec_ok = bool(h) and len(h) <= HEADLINE_MAX_CHARS
    add(
        "x2_headline_executive_length",
        exec_ok,
        len(h),
        f"<={HEADLINE_MAX_CHARS} chars",
        None if exec_ok else "Headline too long for ATS headline slot.",
    )

    infl_ok, infl_reason = check_target_title_inflation(h, target_company, target_title or None)
    add(
        "x2_headline_no_title_inflation",
        infl_ok,
        infl_reason or "ok",
        "no SVP at target framing",
        infl_reason,
    )

    proof_jd = _model_jd_alignment_for_proof(parsed_output if isinstance(parsed_output, dict) else None)
    jd_pf = isinstance(proof_jd, dict) and "jd_used_as_proof" in proof_jd and proof_jd.get("jd_used_as_proof") is False
    add(
        "x2_headline_jd_context_not_proof",
        jd_pf,
        proof_jd if isinstance(proof_jd, dict) else "missing",
        "jd_used_as_proof key present and false",
        None if jd_pf else "jd_used_as_proof must be present and exactly false",
    )

    br_pf = (
        isinstance(proof_jd, dict)
        and "briefing_used_as_proof" in proof_jd
        and proof_jd.get("briefing_used_as_proof") is False
    )
    add(
        "x2_headline_briefing_context_not_proof",
        br_pf,
        proof_jd if isinstance(proof_jd, dict) else "missing",
        "briefing_used_as_proof key present and false",
        None if br_pf else "briefing_used_as_proof must be present and exactly false",
    )

    cc = (companion_context or "").strip()
    cmp_raw = proof_jd.get("companion_used_as_proof") if isinstance(proof_jd, dict) else None
    if not cc:
        cmp_pf = cmp_raw is not True
        add(
            "x2_headline_companion_context_not_proof",
            cmp_pf,
            "no companion lanes",
            "companion_used_as_proof must not be true",
            None if cmp_pf else "companion_used_as_proof must not be true when no companion context exists",
        )
    else:
        cmp_pf = (
            isinstance(proof_jd, dict)
            and "companion_used_as_proof" in proof_jd
            and proof_jd.get("companion_used_as_proof") is False
        )
        add(
            "x2_headline_companion_context_not_proof",
            cmp_pf,
            proof_jd if isinstance(proof_jd, dict) else "missing",
            "companion_used_as_proof key present and false",
            None if cmp_pf else "companion_used_as_proof must be present and exactly false when companion exists",
        )

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    if srfs_source_fact_slice_gate_active or proof_pool_metadata:
        from apps_rg.runtime.sections import selected_role_fact_set as _srfs_w4
        from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
            evaluate_proof_pool_source_fact_gate,
            proof_pool_x2_gate_id,
        )

        collected_srfs = _srfs_w4.collect_source_fact_ids_from_claim_ledger(claim_ledger)
        ok_srfs, env_srfs, fail_srfs = evaluate_proof_pool_source_fact_gate(
            section_id="headline",
            collected_ids=collected_srfs,
            allowed_fact_ids=set(allowed_fact_ids),
            proof_pool_metadata=proof_pool_metadata,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
        )
        add(
            proof_pool_x2_gate_id(
                "headline",
                proof_pool_metadata=proof_pool_metadata,
                srfs_slice_gate_active=srfs_source_fact_slice_gate_active,
            ),
            ok_srfs,
            env_srfs,
            "active_proof_pool_allowlist_exact",
            fail_srfs,
        )

    if artifacts_dir is not None:
        append_section_input_usage_x2_gates(
            gates,
            artifacts_dir=artifacts_dir,
            allowed_fact_ids=allowed_fact_ids,
            claim_ledger=claim_ledger,
            text_claim_coverage=text_claim_coverage,
        )

    return gates


__all__ = [
    "headline_runtime_self_check_truth",
    "headline_word_count",
    "polish_claim_text_when_headline_has_no_metrics",
    "run_headline_x2_gates",
    "validate_raw_headline_claim_ledger",
    "X2GateResult",
]
