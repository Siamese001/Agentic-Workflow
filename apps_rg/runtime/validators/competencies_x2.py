"""Deterministic X2 gates for competencies runtime slice (8 ATS-oriented categories)."""
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

_STOPWORDS = frozenset(
    {
        "and",
        "or",
        "the",
        "a",
        "an",
        "of",
        "for",
        "to",
        "in",
        "on",
        "with",
        "via",
        "per",
        "by",
        "at",
        "from",
        "into",
        "across",
        "over",
        "under",
        "between",
        "within",
        "without",
        "using",
        "based",
        "enterprise",
        "platform",
        "systems",
        "engineering",
        "delivery",
        "quality",
        "data",
        "ai",
        "ml",
    }
)

# Common ATS hallucinations unless they appear in resume/support blob.
_TOOL_HALLUCINATION_TOKENS = (
    "pytorch",
    "tensorflow",
    "keras",
    "langchain",
    "langgraph",
    "huggingface",
    "kubernetes",
    "terraform",
    "ansible",
    "jenkins",
    "circleci",
    "gitlab ci",
    "react",
    "angular",
    "vue.js",
    "nodejs",
    "node.js",
    "nestjs",
    "django",
    "flask",
    "spring boot",
    "mysql",
    "mongodb",
    "postgresql",
    "postgres",
    "elasticsearch",
    "splunk",
    "snowflake",
    "tableau",
    "power bi",
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
        if claim.get("source_fact_id"):
            ids.add(str(claim["source_fact_id"]).split("_metric_")[0])
    return ids


def _flatten_terms(competencies: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for cat in competencies:
        for t in cat.get("terms") or []:
            if isinstance(t, str) and t.strip():
                out.append(t.strip())
    return out


def _bullet_restatement(term: str, bullet_lower: list[str]) -> bool:
    tn = term.lower().strip()
    if len(tn) < 36:
        return False
    for b in bullet_lower:
        if tn in b:
            return True
    return False


def _tool_unsupported(term: str, resume_blob: str) -> str | None:
    low = term.lower()
    blob = resume_blob.lower()
    for tok in _TOOL_HALLUCINATION_TOKENS:
        if tok in low and tok not in blob:
            return tok
    return None


def find_bullet_restatement_term(
    competencies: list[dict[str, Any]],
    bullet_texts_lower: list[str],
) -> str | None:
    for t in _flatten_terms(competencies):
        if _bullet_restatement(t, bullet_texts_lower):
            return t
    return None


def run_competencies_x2_gates(
    *,
    competencies: list[dict[str, Any]],
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    jd_text: str,
    bullet_texts_lower: list[str],
    resume_support_blob: str,
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

    n_cats = len(competencies) if isinstance(competencies, list) else 0
    add(
        "x2_competency_exactly_8_categories",
        n_cats == 8,
        n_cats,
        8,
        "Must have exactly 8 competency categories.",
    )

    format_ok = True
    fmt_reason = None
    if n_cats != 8:
        format_ok = False
        fmt_reason = "wrong category count"
    else:
        for i, cat in enumerate(competencies):
            if not isinstance(cat, dict):
                format_ok = False
                fmt_reason = f"category {i} not object"
                break
            label = str(cat.get("category_label", "")).strip()
            terms = cat.get("terms")
            sf = cat.get("source_fact_ids")
            if not label or len(label) > 72 or ":" in label or "\n" in label:
                format_ok = False
                fmt_reason = f"bad category_label idx {i}"
                break
            if not isinstance(terms, list) or len(terms) < 2 or len(terms) > 7:
                format_ok = False
                fmt_reason = f"terms count idx {i}"
                break
            if not isinstance(sf, list) or not sf:
                format_ok = False
                fmt_reason = f"source_fact_ids idx {i}"
                break
            if not all(isinstance(t, str) and t.strip() for t in terms):
                format_ok = False
                fmt_reason = f"non-string term idx {i}"
                break
    add(
        "x2_competency_format_category_colon_terms",
        format_ok,
        fmt_reason or "ok",
        "label+terms[]+source_fact_ids[]",
        None if format_ok else fmt_reason,
    )

    all_text = " ".join(
        [str(c.get("category_label", "")) for c in competencies]
        + _flatten_terms(competencies)
        if isinstance(competencies, list)
        else []
    )
    sentence_like = False
    reason_sn = None
    for t in _flatten_terms(competencies):
        tl = t.strip()
        if re.search(r"[.!?]\s", tl) or (tl.endswith(".") and len(tl) > 1):
            sentence_like = True
            reason_sn = t
            break
        if len(tl.split()) > 9:
            sentence_like = True
            reason_sn = t
            break
        if re.match(r"^(the|a|an)\s+\w+", tl, re.I):
            sentence_like = True
            reason_sn = t
            break
    add(
        "x2_no_full_sentences",
        not sentence_like,
        reason_sn or "ok",
        "short noun phrases",
        None if not sentence_like else "Sentence-like term or label.",
    )

    bullet_fmt_bad = None
    for t in _flatten_terms(competencies):
        s = t.strip()
        if s.startswith(("-", "*", "•", "·")):
            bullet_fmt_bad = t
            break
    add(
        "x2_no_bullet_format",
        bullet_fmt_bad is None,
        bullet_fmt_bad or "ok",
        "no leading bullet chars",
        None if bullet_fmt_bad is None else "Bullet marker in term.",
    )

    ids_ok = True
    ids_reason = None
    flat_ids: set[str] = set()
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        for fid in cat.get("source_fact_ids") or []:
            fs = str(fid).split("_metric_")[0]
            flat_ids.add(fs)
            if fs not in allowed_fact_ids:
                ids_ok = False
                ids_reason = f"{fs} not allowed idx {i}"
                break
        if not ids_ok:
            break
    ledger_ids = _ledger_fact_ids(claim_ledger)
    ledger_subset = ledger_ids <= allowed_fact_ids if ledger_ids else False
    terms = _flatten_terms(competencies)
    term_to_ledger = {str(e.get("claim_text", "")).strip().lower() for e in claim_ledger if isinstance(e, dict)}
    terms_mapped = all(t.lower() in term_to_ledger for t in terms) if terms and claim_ledger else False
    mapping_ok = ids_ok and ledger_subset and terms_mapped and bool(terms)
    add(
        "x2_all_terms_source_fact_ids",
        mapping_ok,
        ids_reason or ("ledger" if not ledger_subset else "term_map" if not terms_mapped else "ok"),
        "bul_* only + claim_ledger rows per term",
        None if mapping_ok else (ids_reason or "claim_ledger must list each term with source_fact_ids."),
    )

    jd_only = False
    jd_hit = None
    blob_l = resume_support_blob.lower()
    for t in _flatten_terms(competencies):
        copied, phrase = has_jd_phrase_copy(t, jd_text, max_words=4)
        if copied and phrase and phrase not in blob_l:
            jd_only = True
            jd_hit = phrase
            break
    add(
        "x2_no_jd_only_skills",
        not jd_only,
        jd_hit or "ok",
        "no jd-only lift",
        None if not jd_only else "JD phrase in term without resume support.",
    )

    lowered = [t.lower().strip() for t in _flatten_terms(competencies)]
    dup_bad = None
    for i, a in enumerate(lowered):
        for j in range(i + 1, len(lowered)):
            b = lowered[j]
            if a == b:
                dup_bad = a
                break
            if len(a) >= 10 and len(b) >= 10 and (a in b or b in a):
                dup_bad = f"{a}|{b}"
                break
        if dup_bad:
            break
    add(
        "x2_duplicate_variants_collapsed",
        dup_bad is None,
        dup_bad or "ok",
        "unique terms",
        None if dup_bad is None else "Duplicate or near-duplicate terms.",
    )

    restate_bad = None
    for t in _flatten_terms(competencies):
        if _bullet_restatement(t, bullet_texts_lower):
            restate_bad = t
            break
    add(
        "x2_no_bullet_outcome_restatement",
        restate_bad is None,
        restate_bad or "ok",
        "no long bullet substring",
        None if restate_bad is None else "Term restates bullet text.",
    )

    tool_bad = None
    for t in _flatten_terms(competencies):
        hit = _tool_unsupported(t, resume_support_blob)
        if hit:
            tool_bad = f"{t}:{hit}"
            break
    add(
        "x2_no_unsupported_tools_frameworks_models",
        tool_bad is None,
        tool_bad or "ok",
        "resume-supported tools only",
        None if tool_bad is None else "Unsupported tool or framework token.",
    )

    words: list[str] = []
    for t in _flatten_terms(competencies):
        for w in re.findall(r"[a-z]{3,}", t.lower()):
            if w not in _STOPWORDS:
                words.append(w)
    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    over = max(freq.values()) if freq else 0
    stuffing_ok = over <= 5
    add(
        "x2_no_keyword_stuffing",
        stuffing_ok,
        over,
        "<=5 repeat non-stopword",
        None if stuffing_ok else "Keyword repetition across terms.",
    )

    serialized = json.dumps(parsed_output or {}, sort_keys=True)
    add(
        "x2_no_inline_source_tags",
        not INLINE_SOURCE_PATTERN.search(serialized),
        "tags",
        "absent",
        "Inline source tags in payload.",
    )
    add(
        "x2_no_first_person",
        not FIRST_PERSON_PATTERN.search(all_text),
        "first person",
        "absent",
        "First person in competencies.",
    )
    add("x2_no_em_dash", EM_DASH not in all_text, "em dash", "absent", "Em dash in competencies.")

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

    return gates


__all__ = ["run_competencies_x2_gates", "X2GateResult", "find_bullet_restatement_term"]
