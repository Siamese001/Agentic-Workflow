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


_HEADLINE_GENERIC_NOUN_STOPLIST: frozenset[str] = frozenset(
    {
        # Role-family / executive filler words \u2014 not specific enough to count as grounding.
        "ai", "ml", "platforms", "platform", "infrastructure", "infra", "systems", "system",
        "architecture", "engineering", "engineer", "engineered", "leadership", "strategy",
        "strategic", "innovation", "governance", "governed", "agentic", "agent", "agents",
        "enterprise", "enterprises", "scale", "scaling", "data", "delivery", "production",
        "runtime", "operations", "operational", "modern", "modernization", "transformation",
        "transformations", "transform", "lead", "leader", "led", "leading", "team", "teams",
        "team-based", "build", "built", "building", "manage", "managed", "managing",
        "established", "established", "across", "with", "from", "into", "using", "via",
        "and", "the", "for", "this", "that", "those", "these", "their", "they", "have", "has",
        "had", "been", "being", "were", "was", "are", "all", "any", "some", "more", "most",
        "less", "very", "such", "also", "while", "when", "where", "what", "which", "who",
        "whom", "whose", "him", "her", "his", "hers", "ours", "yours", "theirs", "them",
        "us", "we", "you", "i", "me", "my", "mine", "be", "do", "did", "does", "doing",
        "based", "level", "levels", "wide", "broad", "high", "low", "small", "large",
        "great", "core", "key", "main", "common", "general", "specific", "various",
        "different", "same", "other", "another", "first", "second", "third", "last",
        "next", "new", "old", "early", "late", "current", "recent", "future", "past",
        "long", "short", "term", "terms",
        # Generic framing nouns that are legitimate filler in executive headlines but don't
        # carry specific claims on their own. Allowing them as filler prevents the strict
        # grounding rule from forcing Qwen into awkward compositions.
        "workflows", "pipelines", "harness", "orchestration", "instrumentation",
        "observability", "reliability", "performance", "optimization", "programs",
        "services", "capabilities", "organizations", "functions", "foundations",
        "frameworks", "rigor", "discipline", "standards", "standardization",
        "practices", "methodology", "methodologies", "approach", "approaches",
        # NOTE: "catalogs" / "catalog" REMOVED from stoplist (Brown SVP run #14): ChatGPT
        # decisively rejects "Retrieval Telemetry Catalogs" as ungrounded because no cited
        # fact mentions catalogs. Requiring catalog/catalogs to be literally grounded lets
        # X2 catch this before regen, instead of relying on the judge to flag it.
        "registries", "registry", "controls", "patterns",
        "integration", "integrations", "integrated", "integrating", "integrator",
        "implementation", "implementations", "deployment", "deployments",
        "adoption", "adoptions", "rollout", "rollouts", "transformation",
        "transformations", "modernization", "modernizations", "migration", "migrations",
        "automation", "automations", "automated", "automating",
    }
)


def _tokenize_for_grounding(text: str) -> set[str]:
    """Lowercase content tokens (>=4 chars), strip punctuation, drop the generic stoplist."""
    if not text:
        return set()
    raw = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text.lower())
    return {tok for tok in raw if tok not in _HEADLINE_GENERIC_NOUN_STOPLIST}


def _extract_plan_fact_text_map(
    parsed_output: dict[str, Any] | None,
    fallback_facts: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    out: dict[str, str] = {}
    facts: list[dict[str, Any]] = []
    if isinstance(parsed_output, dict):
        sfp = parsed_output.get("selected_fact_plan")
        if isinstance(sfp, dict):
            candidate = sfp.get("facts")
            if isinstance(candidate, list):
                facts = [f for f in candidate if isinstance(f, dict)]
    if not facts and fallback_facts:
        facts = [f for f in fallback_facts if isinstance(f, dict)]
    for f in facts:
        fid = str(f.get("fact_id") or "").strip()
        if not fid:
            continue
        text = str(f.get("claim_text") or "").strip()
        if text:
            out[fid] = text
            base = fid.split("_metric_")[0]
            if base != fid and base not in out:
                out[base] = text
    return out


def repair_headline_segment_citations_for_grounding(
    *,
    headline_line: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Re-cite each X/Y/Z segment to the facts in selected_fact_plan whose claim_text shares
    the most content nouns with the segment. Closes Bug:HeadlineSegmentMiscitationByQwen
    (Brown SVP full_resume_01b4989c296a — Qwen cited fact_quant_hpc_002 for "Microservices
    Telemetry" which shares zero content nouns, while fact_engineering_platform_005
    contained "microservices" and fact_engineering_platform_003 contained "telemetry").

    Strategy: for each segment, find facts with non-empty shared_tokens; pick the union of
    facts whose claim_texts together cover all (or the majority of) segment content nouns,
    preferring the smallest covering set. If no improvement is possible, leave the citation
    unchanged so the X2 grounding gate can still fail honestly.
    """
    receipt: dict[str, Any] = {"per_segment": [], "any_changed": False}
    h = (headline_line or "").strip()
    if not h:
        return list(claim_ledger or []), receipt
    parts = [p.strip() for p in h.split(" | ")]
    if len(parts) < 4:
        return list(claim_ledger or []), receipt
    xyz = parts[1:4]

    fact_text_map = _extract_plan_fact_text_map(parsed_output)
    if not fact_text_map:
        return list(claim_ledger or []), receipt

    fact_tokens: dict[str, set[str]] = {
        fid: _tokenize_for_grounding(text) for fid, text in fact_text_map.items()
    }

    def _best_covering_fact_ids(seg_tokens: set[str], current_ids: list[str]) -> list[str]:
        """Greedy smallest set of facts whose union covers as many seg_tokens as possible."""
        if not seg_tokens:
            return current_ids
        remaining = set(seg_tokens)
        chosen: list[str] = []
        candidate_fids = sorted(fact_text_map.keys())
        while remaining:
            best_fid = None
            best_cover: set[str] = set()
            for fid in candidate_fids:
                if fid in chosen:
                    continue
                cover = fact_tokens.get(fid, set()) & remaining
                if len(cover) > len(best_cover):
                    best_fid = fid
                    best_cover = cover
            if not best_fid or not best_cover:
                break
            chosen.append(best_fid)
            remaining -= best_cover
        return chosen or current_ids

    rows_by_segment: dict[str, dict[str, Any]] = {}
    other_rows: list[dict[str, Any]] = []
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            other_rows.append(row)
            continue
        ct = str(row.get("claim_text") or "").strip().lower()
        if ct in {seg.lower() for seg in xyz}:
            rows_by_segment[ct] = dict(row)
        else:
            other_rows.append(row)

    new_rows: list[dict[str, Any]] = list(other_rows)
    for seg in xyz:
        seg_clean = seg.strip()
        seg_key = seg_clean.lower()
        seg_tokens = _tokenize_for_grounding(seg_clean)
        existing = rows_by_segment.get(seg_key) or {
            "claim_text": seg_clean,
            "source_fact_ids": [],
        }
        current_ids = [str(x).strip() for x in (existing.get("source_fact_ids") or []) if str(x).strip()]
        current_union = set().union(*(fact_tokens.get(fid, set()) for fid in current_ids))
        current_grounded = current_union & seg_tokens
        per_seg = {
            "segment": seg_clean,
            "before_cited": current_ids,
            "before_grounded_tokens": sorted(current_grounded),
        }
        if seg_tokens and (len(current_grounded) * 2 < len(seg_tokens) or not current_grounded):
            covering = _best_covering_fact_ids(seg_tokens, current_ids)
            after_union = set().union(*(fact_tokens.get(fid, set()) for fid in covering))
            after_grounded = after_union & seg_tokens
            if covering != current_ids and len(after_grounded) > len(current_grounded):
                existing["source_fact_ids"] = covering
                per_seg["after_cited"] = covering
                per_seg["after_grounded_tokens"] = sorted(after_grounded)
                per_seg["changed"] = True
                receipt["any_changed"] = True
            else:
                per_seg["changed"] = False
        else:
            per_seg["changed"] = False
        receipt["per_segment"].append(per_seg)
        new_rows.append(existing)

    return new_rows, receipt


def check_headline_xyz_literal_grounding(
    *,
    headline_line: str,
    claim_ledger: list[dict[str, Any]],
    fact_id_to_text: dict[str, str],
) -> tuple[bool, dict[str, Any], str | None]:
    """Each X/Y/Z phrase must share at least one content noun (>=4 chars, non-generic) with its cited fact's claim_text.

    Closes Bug:HeadlineXYZPhrasesNotGroundedInFactText (Brown SVP full_resume_183cf9252e02 headline
    X3_BLOCK). The previous run synthesized ``Governed Agentic Platforms`` cited to
    fact_engineering_platform_005 ("cloud-native microservices across AWS and Databricks Lakehouse...")
    and ``Distributed AI Infrastructure`` cited to fact_quant_hpc_002 ("AI-driven automated trading
    platform using parallel HPC workflows..."). Both phrases shared zero non-generic content nouns
    with their cited facts, so two X1D judges (OpenAI 2.0 decisive, Claude 3.2 soft) correctly flagged
    them as unsupported \u2014 but the existing X2 layer let them through because the fact_id was in
    the allowed list. This gate enforces the lexical grounding the rubric already requires.
    """
    h = (headline_line or "").strip()
    if not h:
        return False, {"reason": "empty_headline"}, "headline_line empty; cannot check grounding."
    parts = [p.strip() for p in h.split(" | ")]
    if len(parts) < 4:
        return True, {"reason": "skipped_not_four_segments"}, None  # other gate covers shape
    xyz = parts[1:4]

    ledger_by_text: dict[str, list[str]] = {}
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        ct = str(row.get("claim_text") or "").strip().lower()
        if not ct:
            continue
        fids = [str(f).strip() for f in (row.get("source_fact_ids") or []) if str(f).strip()]
        if fids:
            ledger_by_text[ct] = fids

    per_segment: list[dict[str, Any]] = []
    failures: list[str] = []
    for seg in xyz:
        seg_clean = seg.strip()
        seg_key = seg_clean.lower()
        fids = ledger_by_text.get(seg_key, [])
        seg_tokens = _tokenize_for_grounding(seg_clean)
        if not fids:
            per_segment.append({
                "segment": seg_clean,
                "ground_pass": False,
                "reason": "segment_has_no_claim_ledger_row",
                "cited_fact_ids": [],
                "shared_tokens": [],
            })
            failures.append(f"{seg_clean!r} has no claim_ledger row")
            continue
        # Hybrid rule (Wave F): require >=1 non-stoplist content noun grounded (deterministic
        # X2 floor) AND require the MAJORITY (>=50%) of non-stoplist content nouns to be
        # grounded. This lets common framing modifiers like "Integration", "Workflows" appear
        # in segments without forcing a regen loop, while still rejecting headlines where the
        # cited fact is mostly fictional cover. X1D LLM judges have semantic latitude to flag
        # nuance beyond this floor.
        per_fact_evidence: list[dict[str, Any]] = []
        union_grounded: set[str] = set()
        for fid in fids:
            text = fact_id_to_text.get(fid) or fact_id_to_text.get(fid.split("_metric_")[0]) or ""
            fact_tokens = _tokenize_for_grounding(text)
            shared = sorted(seg_tokens & fact_tokens)
            per_fact_evidence.append({"fact_id": fid, "shared_tokens": shared, "fact_text_known": bool(text)})
            union_grounded.update(shared)
        ungrounded = sorted(seg_tokens - union_grounded)
        total = len(seg_tokens)
        grounded_count = len(union_grounded)
        majority_grounded = grounded_count * 2 >= total if total else False
        seg_pass = bool(union_grounded) and majority_grounded
        per_segment.append({
            "segment": seg_clean,
            "ground_pass": seg_pass,
            "cited_fact_ids": fids,
            "evidence": per_fact_evidence,
            "ungrounded_tokens": ungrounded,
            "grounded_tokens": sorted(union_grounded),
            "majority_grounded": majority_grounded,
        })
        if not seg_tokens:
            failures.append(
                f"{seg_clean!r} has zero non-generic content nouns (all words are in stoplist) \u2014 "
                "cannot prove grounding"
            )
        elif not union_grounded:
            failures.append(
                f"{seg_clean!r} shares zero content nouns with cited fact(s) "
                f"{fids} \u2014 phrase is not lexically grounded in fact claim_text"
            )
        elif not majority_grounded:
            failures.append(
                f"{seg_clean!r} grounds only {grounded_count}/{total} content noun(s) in cited "
                f"fact(s) {fids}; ungrounded={ungrounded} \u2014 majority of segment nouns must "
                "literally appear in the cited fact"
            )
    overall = not failures
    observed = {"segments": per_segment, "checked": len(per_segment)}
    failure = None if overall else "; ".join(failures)
    return overall, observed, failure


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

    fact_text_map = _extract_plan_fact_text_map(parsed_output)
    grounding_pass, grounding_obs, grounding_fail = check_headline_xyz_literal_grounding(
        headline_line=h,
        claim_ledger=claim_ledger,
        fact_id_to_text=fact_text_map,
    )
    add(
        "x2_headline_xyz_literal_grounding",
        grounding_pass,
        grounding_obs,
        "each X/Y/Z segment shares >=1 content noun with its cited fact's claim_text",
        grounding_fail,
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

    # -----------------------------------------------------------------------
    # Headline positioning / seniority / anti-leakage quality gates
    # -----------------------------------------------------------------------
    from apps_rg.runtime.validators.headline_quality_x2 import (
        HEADLINE_E0_REFERENCE_TEXTS,
        check_headline_base_ngram_overlap,
        check_headline_e0_ngram_overlap,
        check_headline_no_narrowing_it_labels,
        check_headline_positioning_families,
    )

    # Gate: no narrowing IT labels (HARD FAIL)
    narrowing_r = check_headline_no_narrowing_it_labels(h)
    add(
        narrowing_r.gate_id,
        narrowing_r.passed,
        narrowing_r.observed_value,
        narrowing_r.threshold,
        narrowing_r.failure_reason,
    )

    # Gate: positioning family preservation (WARN mode — calibrate then promote)
    positioning_r = check_headline_positioning_families(h, min_families=2)
    add(
        positioning_r.gate_id,
        True,  # WARN mode: always pass in lane; record violation via failure_reason
        positioning_r.observed_value,
        positioning_r.threshold,
        None if positioning_r.passed else positioning_r.failure_reason,
    )

    # Gate: E0 n-gram overlap (WARN mode)
    e0_r = check_headline_e0_ngram_overlap(h, HEADLINE_E0_REFERENCE_TEXTS, warn_only=True)
    add(
        e0_r.gate_id,
        e0_r.passed,
        e0_r.observed_value,
        e0_r.threshold,
        e0_r.failure_reason,
    )

    # Gate: base resume headline n-gram overlap (WARN mode)
    base_hl_texts: list[str] = []
    if parsed_output and isinstance(parsed_output, dict):
        _rp = parsed_output.get("_runtime_payload_ref") or {}
        _base_hl = str(
            (_rp.get("base_resume", {}) or {}).get("headline_line", "")
            if isinstance(_rp, dict)
            else ""
        ).strip()
        if _base_hl:
            base_hl_texts = [_base_hl]
    base_r = check_headline_base_ngram_overlap(h, base_hl_texts, warn_only=True)
    add(
        base_r.gate_id,
        base_r.passed,
        base_r.observed_value,
        base_r.threshold,
        base_r.failure_reason,
    )

    # -----------------------------------------------------------------------
    # Headline positioning bundle gates (active only in bundle-consumption mode)
    # -----------------------------------------------------------------------
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        headline_positioning_consumption_active,
        run_headline_positioning_x2_gates,
    )

    if headline_positioning_consumption_active(proof_pool_metadata):
        for hp in run_headline_positioning_x2_gates(
            headline_line=h,
            parsed_output=parsed_output,
            proof_pool_metadata=proof_pool_metadata,
            jd_text=jd_text,
            base_headline_texts=base_hl_texts,
        ):
            add(hp.gate_id, hp.passed, hp.observed_value, hp.threshold, hp.failure_reason)

    return gates


__all__ = [
    "check_headline_xyz_literal_grounding",
    "headline_runtime_self_check_truth",
    "headline_word_count",
    "polish_claim_text_when_headline_has_no_metrics",
    "repair_headline_segment_citations_for_grounding",
    "run_headline_x2_gates",
    "validate_raw_headline_claim_ledger",
    "X2GateResult",
]
