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


def _term_phrase(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("text") or raw.get("phrase") or raw.get("term") or "").strip()
    return str(raw).strip()


def check_structured_term_primary_facts(
    competencies: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    """When any term is structured (dict), require all terms in that category to declare one source_fact_id."""
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms") or []
        if not any(isinstance(t, dict) for t in terms_raw):
            continue
        for j, t in enumerate(terms_raw):
            if not isinstance(t, dict):
                return False, f"category {i} term {j} must be object when structured terms are present"
            if t.get("source_fact_ids"):
                return False, f"category {i} term {j} must not use term-level source_fact_ids; use source_fact_id only"
            phrase = _term_phrase(t)
            sid = t.get("source_fact_id")
            if not phrase or not sid:
                return False, f"category {i} term {j} missing text or source_fact_id"
            fs = str(sid).split("_metric_")[0]
            if fs not in allowed_fact_ids:
                return False, f"{fs} not allowed at category {i} term {j}"
    return True, None


def term_primary_support_overlap(term_text: str, primary_fid: str, resume_blob_lower: str) -> bool:
    """Expose resume-overlap heuristic for deterministic post-processing outside this module."""

    return _term_primary_support_ok(term_text, primary_fid, resume_blob_lower)


def _term_primary_support_ok(term_text: str, primary_fid: str, resume_blob_lower: str) -> bool:
    """Light check: at least one substantive token from the term appears in resume support blob."""
    tl = term_text.lower()
    for w in re.findall(r"[a-z][a-z0-9+/-]{3,}", tl):
        if w in _STOPWORDS:
            continue
        if w in resume_blob_lower:
            return True
    return False


def check_competency_schema_top_level(parsed_output: dict[str, Any] | None) -> tuple[bool, str | None]:
    if not parsed_output or not isinstance(parsed_output, dict):
        return False, "missing parsed output"
    required = ("competencies", "selected_fact_plan", "claim_ledger", "jd_alignment")
    for k in required:
        if k not in parsed_output:
            return False, f"missing {k}"
    jd = parsed_output.get("jd_alignment")
    if isinstance(jd, dict) and jd.get("jd_used_as_proof") is True:
        return False, "jd_used_as_proof must not be true"
    return True, None


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
            p = _term_phrase(t)
            if p:
                out.append(p)
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
            for t in terms:
                if isinstance(t, dict):
                    if not _term_phrase(t):
                        format_ok = False
                        fmt_reason = f"empty structured term idx {i}"
                        break
                elif not (isinstance(t, str) and t.strip()):
                    format_ok = False
                    fmt_reason = f"non-string term idx {i}"
                    break
            if not format_ok:
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

    structured_ok, structured_reason = check_structured_term_primary_facts(
        competencies if isinstance(competencies, list) else [],
        allowed_fact_ids,
    )
    add(
        "x2_structured_term_primary_facts",
        structured_ok,
        structured_reason or "skipped_or_ok",
        "structured_terms_have_source_fact_id",
        None if structured_ok else structured_reason,
    )

    schema_ok, schema_reason = check_competency_schema_top_level(
        parsed_output if isinstance(parsed_output, dict) else None
    )
    add(
        "x2_competency_schema_valid",
        schema_ok,
        schema_reason or "ok",
        "top_level_keys+jdsafe",
        None if schema_ok else schema_reason,
    )

    primary_present_ok = True
    primary_present_reason: str | None = None
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        for j, raw_t in enumerate(cat.get("terms") or []):
            if isinstance(raw_t, dict):
                if not raw_t.get("source_fact_id"):
                    primary_present_ok = False
                    primary_present_reason = f"category {i} term {j} missing source_fact_id"
                    break
            else:
                if not (cat.get("source_fact_ids") or []):
                    primary_present_ok = False
                    primary_present_reason = f"category {i} needs source_fact_ids for string terms"
                    break
        if not primary_present_ok:
            break
    add(
        "x2_competency_term_primary_fact_present",
        primary_present_ok,
        primary_present_reason or "ok",
        "one_primary_per_term",
        primary_present_reason,
    )

    unique_primary_ok = True
    unique_primary_reason: str | None = None
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        for j, raw_t in enumerate(cat.get("terms") or []):
            if isinstance(raw_t, dict) and raw_t.get("source_fact_ids"):
                unique_primary_ok = False
                unique_primary_reason = f"category {i} term {j}: use source_fact_id only"
                break
        if not unique_primary_ok:
            break
    add(
        "x2_competency_term_primary_fact_unique",
        unique_primary_ok,
        unique_primary_reason or "ok",
        "no_term_level_source_fact_ids_array",
        unique_primary_reason,
    )

    blob_lower = resume_support_blob.lower()
    support_ok = True
    support_reason: str | None = None
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        for raw_t in cat.get("terms") or []:
            if isinstance(raw_t, dict):
                phrase = _term_phrase(raw_t)
                pid = str(raw_t.get("source_fact_id") or "").split("_metric_")[0]
                if pid and phrase and not _term_primary_support_ok(phrase, pid, blob_lower):
                    support_ok = False
                    support_reason = f"term not resume-grounded: {phrase[:40]!r}"
                    break
        if not support_ok:
            break
    add(
        "x2_competency_term_supported",
        support_ok,
        support_reason or "ok",
        "resume_blob_overlap",
        support_reason,
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
    add(
        "x2_competency_jd_mirroring_within_limit",
        not jd_only,
        jd_hit or "ok",
        "<=4w jd mirror or grounded",
        None if not jd_only else "JD mirroring exceeds allowed grounding.",
    )

    jd_al = (parsed_output or {}).get("jd_alignment") if isinstance(parsed_output, dict) else {}
    companion_pf_ok = (
        isinstance(jd_al, dict) and jd_al.get("jd_used_as_proof") is not True
    )
    add(
        "x2_competency_companion_context_not_proof",
        companion_pf_ok,
        jd_al if isinstance(jd_al, dict) else "missing",
        "jd_used_as_proof_false_or_absent",
        None if companion_pf_ok else "jd_used_as_proof must be false",
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
    add(
        "x2_competency_duplicate_variant_absent",
        dup_bad is None,
        dup_bad or "ok",
        "no_dup_variants",
        None if dup_bad is None else "Duplicate competency variants present.",
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


__all__ = [
    "find_bullet_restatement_term",
    "run_competencies_x2_gates",
    "term_primary_support_overlap",
    "X2GateResult",
]
