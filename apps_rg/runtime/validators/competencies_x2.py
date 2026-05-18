"""Deterministic X2 gates for the competencies section lane (8 ATS-oriented categories)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.validators.competencies_proof_markers import scan_mock_fixture_markers
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


_STYLE_HYGIENE_GATE_IDS = frozenset(
    {
        "x2_no_inline_source_tags",
        "x2_no_first_person",
        "x2_no_em_dash",
        "x2_no_bullet_format",
        "x2_no_full_sentences",
        "x2_no_mock_fixture_markers_in_real_llm_output",
    }
)

_ALLOWED_STYLE_PASS_STRINGS = frozenset({"ok", "absent", "skipped_not_real_llm", "no_mock_fixture_language"})


def resolve_competencies_provider_transport_x2(
    *,
    cli_provider: str,
    runtime_generation_status: str,
    live_preflight_blocked: bool,
) -> tuple[bool, str, str]:
    """Return (transport_ok, cli_label, attempted_transport_label)."""
    cli = str(cli_provider).strip().lower()
    rgs = str(runtime_generation_status).strip()
    if live_preflight_blocked:
        return False, cli, "blocked_http_models_preflight"
    if cli == "qwen_vllm":
        if rgs == "REAL_LLM":
            return True, cli, "qwen_vllm_http"
        if rgs == OFFLINE_CONTRACT_STUB_RUNTIME_STATUS:
            return True, cli, "offline_contract_stub"
        if rgs == "BLOCKED":
            return False, cli, "qwen_vllm_transport_blocked"
        if rgs == "MOCKED":
            return False, cli, "mocked_generation"
        return False, cli, rgs.lower()
    if cli == "mock":
        return True, cli, rgs.lower()
    return True, cli, rgs.lower()


def _style_hygiene_pass_observed_ok(gate_id: str, passed: bool, observed: Any) -> bool:
    if not passed or gate_id not in _STYLE_HYGIENE_GATE_IDS:
        return True
    if observed is True or observed is False or observed == 0:
        return True
    if isinstance(observed, list) and len(observed) == 0:
        return True
    if isinstance(observed, str):
        olow = observed.strip().lower()
        if olow in _ALLOWED_STYLE_PASS_STRINGS:
            return True
        forbidden = (
            "em dash",
            "first person",
            "bullet",
            "sentence",
            "mock",
            "fixture",
            "inline",
            "present",
            "leading bullet",
        )
        if any(x in olow for x in forbidden):
            return False
        return True
    return True


def competencies_x2_gate_rows_internally_consistent(gates: list[X2GateResult]) -> tuple[bool, list[str]]:
    consistency_bad: list[str] = []
    for row in gates:
        rd = row.to_dict()
        gid = str(rd.get("gate_id") or "")
        passed = bool(rd.get("pass"))
        fr = rd.get("failure_reason")
        obs = rd.get("observed_value")
        if passed and fr is not None and str(fr).strip() != "":
            consistency_bad.append(gid)
        if not passed and (fr is None or str(fr).strip() == ""):
            consistency_bad.append(gid)
        if not _style_hygiene_pass_observed_ok(gid, passed, obs):
            consistency_bad.append(gid)
    return len(consistency_bad) == 0, consistency_bad


def _term_phrase(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("text") or raw.get("phrase") or raw.get("term") or "").strip()
    return str(raw).strip()


def check_canonical_competency_terms(
    competencies: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    """Persisted proof shape: every term is ``{text, source_fact_id, source_fact_ids[]}``.

    ``source_fact_id`` must appear in ``source_fact_ids``. All ids must be allowed bul_* rows.
    Optional ``jd_signal_ids`` must be a list when present.
    """
    for i, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        terms_raw = cat.get("terms") or []
        for j, t in enumerate(terms_raw):
            if not isinstance(t, dict):
                return False, f"category {i} term {j} must be canonical structured object (got non-object)"
            phrase = _term_phrase(t)
            sid = t.get("source_fact_id")
            sids_raw = t.get("source_fact_ids")
            if t.get("jd_signal_ids") is not None and not isinstance(t.get("jd_signal_ids"), list):
                return False, f"category {i} term {j}: jd_signal_ids must be an array when present"
            if not phrase or sid is None or str(sid).strip() == "":
                return False, f"category {i} term {j} missing text or source_fact_id"
            if not isinstance(sids_raw, list) or not sids_raw:
                return False, f"category {i} term {j} missing non-empty source_fact_ids array"
            pid = str(sid).split("_metric_")[0]
            norm_ids = [str(x).split("_metric_")[0] for x in sids_raw]
            if pid not in norm_ids:
                return False, f"category {i} term {j}: source_fact_id not listed in source_fact_ids"
            for fid in norm_ids:
                if fid not in allowed_fact_ids:
                    return False, f"{fid} not allowed at category {i} term {j}"
    return True, None


def check_structured_term_primary_facts(
    competencies: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    """Backward-compatible alias — canonical structured term enforcement."""
    return check_canonical_competency_terms(competencies, allowed_fact_ids)


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


def _one_token_technical_cap_ok(term: str) -> bool:
    """Heuristic: acronym / product token shapes (GraphRAG, AWS, vLLM, ChromaDB)."""
    p = term.strip()
    if len(p) < 2:
        return False
    if re.match(r"^[A-Z0-9]{2,}$", p):
        return True
    if re.match(r"^[A-Za-z][A-Za-z0-9./+\-]*(?:[A-Z][a-z0-9]*)+$", p):
        return True
    if re.search(r"\d", p) and re.match(r"^[A-Za-z0-9./+\-]+$", p):
        return True
    return False


def _term_compact_phrase_ok(
    phrase: str,
    *,
    primary_fact_id: str,
    proof_blob_lower: str,
) -> tuple[bool, str | None]:
    """Compact phrase policy: typ. 2–5 words; single-token only when grounded or technical token; hard max 6 words."""
    p = phrase.strip()
    if not p:
        return False, "empty"
    wc = len(p.split())
    if wc > 6:
        return False, "over_max_words"
    if wc >= 2:
        return True, None
    pid = str(primary_fact_id).split("_metric_")[0]
    if pid and _term_primary_support_ok(p, pid, proof_blob_lower):
        return True, None
    if _one_token_technical_cap_ok(p):
        return True, None
    return False, "unsupported_one_token_generic"


def check_competency_schema_top_level(parsed_output: dict[str, Any] | None) -> tuple[bool, str | None]:
    if not parsed_output or not isinstance(parsed_output, dict):
        return False, "missing parsed output"
    required = ("competencies", "selected_fact_plan", "claim_ledger", "jd_alignment")
    for k in required:
        if k not in parsed_output:
            return False, f"missing {k}"
    jd = parsed_output.get("jd_alignment")
    if isinstance(jd, dict):
        if jd.get("targeting_only") is not True:
            return False, "jd_alignment.targeting_only must be true"
        if jd.get("jd_used_as_proof") is True:
            return False, "jd_used_as_proof must not be true"
        if jd.get("briefing_used_as_proof") is True:
            return False, "briefing_used_as_proof must not be true"
        if jd.get("companion_context_used_as_proof") is True:
            return False, "companion_context_used_as_proof must not be true"
    else:
        return False, "jd_alignment must be object"
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
    briefing_text: str = "",
    bullet_texts_lower: list[str],
    resume_support_blob: str,
    c0_proof_blob: str | None = None,
    allowed_fact_ids: set[str],
    runtime_generation_status: str,
    cli_provider: str | None = None,
    live_preflight_blocked: bool = False,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    artifacts_dir: Any | None = None,
    text_claim_coverage: dict[str, Any] | None = None,
    srfs_source_fact_slice_gate_active: bool = False,
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []
    proof_blob = (c0_proof_blob if c0_proof_blob is not None else resume_support_blob).lower()

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
        None if n_cats == 8 else "Must have exactly 8 competency categories.",
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
            if not isinstance(terms, list) or len(terms) < 2 or len(terms) > 6:
                format_ok = False
                fmt_reason = f"terms count idx {i}"
                break
            if not isinstance(sf, list) or not sf:
                format_ok = False
                fmt_reason = f"source_fact_ids idx {i}"
                break
            for t in terms:
                if not isinstance(t, dict) or not _term_phrase(t):
                    format_ok = False
                    fmt_reason = f"terms must be structured objects idx {i}"
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

    claim_nonempty_ok = True
    claim_nonempty_reason: str | None = None
    for i, row in enumerate(claim_ledger):
        if not isinstance(row, dict):
            claim_nonempty_ok = False
            claim_nonempty_reason = f"claim_ledger row {i} not object"
            break
        ct = str(row.get("claim_text", "") or "").strip()
        if not ct:
            claim_nonempty_ok = False
            claim_nonempty_reason = f"claim_ledger row {i} empty claim_text"
            break
    add(
        "x2_claim_ledger_claim_text_non_empty",
        claim_nonempty_ok,
        claim_nonempty_reason or "ok",
        "non_empty_claim_text",
        None if claim_nonempty_ok else claim_nonempty_reason,
    )

    word_ok = True
    word_bad = None
    for cat in competencies if isinstance(competencies, list) else []:
        if not isinstance(cat, dict):
            continue
        for raw_t in cat.get("terms") or []:
            phrase = _term_phrase(raw_t)
            pid = ""
            if isinstance(raw_t, dict):
                pid = str(raw_t.get("source_fact_id") or "").split("_metric_")[0]
            ok_w, _why = _term_compact_phrase_ok(
                phrase,
                primary_fact_id=pid,
                proof_blob_lower=proof_blob,
            )
            if not ok_w:
                word_ok = False
                word_bad = phrase
                break
        if not word_ok:
            break
    add(
        "x2_competency_term_compact_word_count",
        word_ok,
        word_bad or "ok",
        "2–5 words typical; 1-token only when resume-grounded or technical/acronym token; hard max 6 words",
        None if word_ok else "Term violates compact phrase policy (too long or unsupported one-token).",
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

    canonical_terms_ok, canonical_terms_reason = check_canonical_competency_terms(
        competencies if isinstance(competencies, list) else [],
        allowed_fact_ids,
    )
    add(
        "x2_structured_term_primary_facts",
        canonical_terms_ok,
        canonical_terms_reason or "ok",
        "canonical_term_objects",
        None if canonical_terms_ok else canonical_terms_reason,
    )
    add(
        "x2_competency_terms_canonical_structured",
        canonical_terms_ok,
        canonical_terms_reason or "ok",
        "text+source_fact_id+source_fact_ids",
        None if canonical_terms_ok else canonical_terms_reason,
    )
    add(
        "x2_competency_term_primary_fact_present",
        canonical_terms_ok,
        canonical_terms_reason or "ok",
        "primary_declared",
        None if canonical_terms_ok else canonical_terms_reason,
    )
    add(
        "x2_competency_term_primary_fact_unique",
        canonical_terms_ok,
        canonical_terms_reason or "ok",
        "primary_in_source_fact_ids_list",
        None if canonical_terms_ok else canonical_terms_reason,
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

    blob_lower = proof_blob
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
        None if support_ok else support_reason,
    )

    jd_only = False
    jd_hit = None
    for t in _flatten_terms(competencies):
        copied, phrase = has_jd_phrase_copy(t, jd_text, max_words=4)
        if copied and phrase and phrase not in proof_blob:
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

    briefing_only = False
    br_hit = None
    br = str(briefing_text or "").strip()
    if br:
        for t in _flatten_terms(competencies):
            copied, phrase = has_jd_phrase_copy(t, br, max_words=4)
            if copied and phrase and phrase not in proof_blob:
                briefing_only = True
                br_hit = phrase
                break
    add(
        "x2_no_briefing_only_skills",
        not briefing_only,
        br_hit or "ok",
        "no briefing-only lift",
        None if not briefing_only else "Briefing phrase in term without C0 resume support.",
    )

    jd_al = (parsed_output or {}).get("jd_alignment") if isinstance(parsed_output, dict) else {}
    companion_pf_ok = (
        isinstance(jd_al, dict)
        and jd_al.get("jd_used_as_proof") is not True
        and jd_al.get("briefing_used_as_proof") is not True
        and jd_al.get("companion_context_used_as_proof") is not True
    )
    add(
        "x2_competency_companion_context_not_proof",
        companion_pf_ok,
        jd_al if isinstance(jd_al, dict) else "missing",
        "proof_flags_false",
        None if companion_pf_ok else "jd_used_as_proof, briefing_used_as_proof, and companion_context_used_as_proof must be false.",
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
        hit = _tool_unsupported(t, proof_blob)
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
    inl = INLINE_SOURCE_PATTERN.search(serialized)
    add(
        "x2_no_inline_source_tags",
        inl is None,
        (inl.group(0)[:120] if inl else "ok"),
        "absent",
        None if inl is None else "Inline source tags in payload.",
    )
    fp_hit = FIRST_PERSON_PATTERN.search(all_text)
    add(
        "x2_no_first_person",
        fp_hit is None,
        (fp_hit.group(0)[:120] if fp_hit else "ok"),
        "absent",
        None if fp_hit is None else "First person in competencies.",
    )
    em_hit = EM_DASH in all_text
    add(
        "x2_no_em_dash",
        not em_hit,
        "present" if em_hit else "ok",
        "absent",
        None if not em_hit else "Em dash in competencies.",
    )

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add(
        "x2_json_parse_valid",
        json_ok,
        json_reason if not json_ok else "ok",
        None,
        None if json_ok else json_reason,
    )

    cli_effective = str(cli_provider or provider_requested or "qwen_vllm").strip().lower()
    provider_ok, req_lbl, att_lbl = resolve_competencies_provider_transport_x2(
        cli_provider=cli_effective,
        runtime_generation_status=str(runtime_generation_status),
        live_preflight_blocked=live_preflight_blocked,
    )
    add(
        "x2_provider_requested_attempted",
        provider_ok,
        f"{req_lbl}->{att_lbl}",
        "cli_intent_matches_transport_surface",
        None
        if provider_ok
        else "Provider transport does not match CLI intent (substitution, blocked TCP preflight, or mock).",
    )
    no_silent_mock = not (cli_effective == "qwen_vllm" and runtime_generation_status == "MOCKED")
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM",
        None if no_silent_mock else "Silent mock fallback detected.",
    )

    proof_blob_scan = "\n".join(
        [
            raw_output or "",
            serialized,
        ]
    )
    marker_hits = scan_mock_fixture_markers(proof_blob_scan) if runtime_generation_status == "REAL_LLM" else []
    markers_clean = len(marker_hits) == 0
    marker_gate_pass = (runtime_generation_status != "REAL_LLM") or markers_clean
    marker_observed: Any = (
        "skipped_not_real_llm" if runtime_generation_status != "REAL_LLM" else (marker_hits or "ok")
    )
    add(
        "x2_no_mock_fixture_markers_in_real_llm_output",
        marker_gate_pass,
        marker_observed,
        "no_mock_fixture_language",
        None
        if marker_gate_pass
        else f"Forbidden mock/test markers in REAL_LLM artifacts: {', '.join(marker_hits)}",
    )

    judges_ok, judges_reason = check_judge_rows_present(x1d_judges)
    add(
        "x2_x1d_required_judges_present",
        judges_ok,
        judges_reason or "ok",
        REQUIRED_JUDGE_PROVIDERS,
        None if judges_ok else judges_reason,
    )

    if x1d_judges:
        blocked_invalid = []
        for judge in x1d_judges:
            if str(judge.get("evaluator_mode", "")).startswith("BLOCKED_"):
                schema_ok2, _ = check_judge_schema_valid(judge)
                if not schema_ok2:
                    blocked_invalid.append(judge.get("provider_key"))
        schema_blocked_ok = not blocked_invalid
        add(
            "x2_x1d_schema_valid",
            schema_blocked_ok,
            blocked_invalid if not schema_blocked_ok else "ok",
            [],
            None if schema_blocked_ok else f"Blocked judges invalid schema: {blocked_invalid}",
        )
    else:
        add(
            "x2_x1d_schema_valid",
            False,
            "no judges",
            "present",
            "No judges.",
        )

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    if srfs_source_fact_slice_gate_active:
        from apps_rg.runtime.sections import selected_role_fact_set as _srfs_w4

        coll_co = _srfs_w4.collect_source_fact_ids_from_competencies_struct(competencies, claim_ledger)
        ok_co, env_co, fail_co = _srfs_w4.evaluate_srfs_slice_source_fact_gate(
            section_id="competencies",
            collected_ids=coll_co,
            allowed_fact_ids=set(allowed_fact_ids),
        )
        add(
            "x2_competencies_source_fact_ids_within_srfs_slice",
            ok_co,
            env_co,
            "srfs_slice_allowlist_exact",
            fail_co,
        )

    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/competencies"),
        allowed_fact_ids=allowed_fact_ids,
        claim_ledger=claim_ledger,
        text_claim_coverage=text_claim_coverage,
    )

    consistency_ok, consistency_bad = competencies_x2_gate_rows_internally_consistent(gates)
    add(
        "x2_gate_rows_are_internally_consistent",
        consistency_ok,
        consistency_bad or "ok",
        "pass_rows_have_null_failure_and_fail_rows_have_reason_and_style_observed_values",
        None
        if consistency_ok
        else f"Inconsistent gate rows: {', '.join(consistency_bad)}",
    )

    return gates


__all__ = [
    "check_canonical_competency_terms",
    "check_structured_term_primary_facts",
    "competencies_x2_gate_rows_internally_consistent",
    "find_bullet_restatement_term",
    "resolve_competencies_provider_transport_x2",
    "run_competencies_x2_gates",
    "term_primary_support_overlap",
    "X2GateResult",
]
