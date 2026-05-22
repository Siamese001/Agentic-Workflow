"""Executive capability projection — replaces phrase-extraction repair for competencies v3."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.competencies_certification_contract import (
    credential_term_to_skill_term,
    is_credential_competency_term,
    sanitize_competencies_no_certification_category,
)
from apps_rg.runtime.sections.competencies_rigor import (
    MIN_ITEMS_PER_CATEGORY,
    _is_low_rigor_two_word_phrase,
    check_competencies_no_all_generic_skill_phrase,
)
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase
from apps_rg.runtime.sections.competencies_v3_contract import (
    SUPPORT_CLASS_FACT_AND_SKILL_GRAPH,
    SUPPORT_CLASS_FACT_ONLY,
    SUPPORT_CLASS_SKILL_GRAPH_ONLY,
    extract_categories,
    label_for_category_id,
    legacy_category_from_v3,
    load_executive_capability_taxonomy,
    resolve_approved_category_label,
    sync_categories_competencies,
)
from apps_rg.runtime.validators.competencies_x2 import term_supports_resume_or_graph

# Never repair INTO these outputs (regression anchors).
_FORBIDDEN_REPAIR_OUTPUTS: frozenset[str] = frozenset(
    {
        "databricks lakehouse fundamentals",
        "databricks lakehouse platform",
        "designed",
        "platform leads",
        "including senior engineers",
        "enterprise sales",
        "data-driven decision-making",
    }
)

# Source fragment / weak phrase -> executive capability synonym (not raw scrape).
_CAPABILITY_SYNONYMS: dict[str, str] = {
    "unified data platform": "Unified data platform modernization",
    "multi-cloud deployment": "Multi-cloud platform deployment",
    "career development": "Engineering talent development",
    "budget optimization": "Operating model optimization",
    "synergy modeling": "Synergy and integration modeling",
    "team scaling": "Engineering organization scale-out",
    "enterprise adoption": "Enterprise platform adoption",
    "pipeline analytics": "Revenue pipeline analytics",
    "margin expansion": "Commercial margin expansion",
    "data-driven decision-making": "Enterprise platform operating model",
    "data-informed operating decisions": "Enterprise platform operating model",
    "enterprise sales": "Enterprise platform GTM",
    "platform leads": "Platform engineering leadership",
    "including senior engineers": "",
    "designed": "",
    "databricks lakehouse fundamentals": "Databricks Lakehouse platform",
    "cataloging": "Data cataloging",
    "cohesive standards": "Enterprise architecture standards",
    "data lineage": "Enterprise data lineage",
    "unified data lakehouse": "Unified data platform modernization",
    "synergy models": "Synergy and integration modeling",
    "synergy modeling": "Synergy and integration modeling",
    "cost optimization": "Operating cost optimization",
}

_BARE_VERB_RE = re.compile(
    r"^(designed|including|led|managed|built|created|developed|implemented|delivered|owned|scaled)$",
    re.IGNORECASE,
)
_FRAGMENT_RE = re.compile(
    r"^(including\s+.+|platform\s+leads?|senior\s+engineers?)$",
    re.IGNORECASE,
)


def _norm(phrase: str) -> str:
    return re.sub(r"\s+", " ", str(phrase or "").strip().lower()).rstrip(".")


def is_raw_fragment_term(phrase: str) -> bool:
    p = str(phrase or "").strip()
    if not p:
        return True
    low = _norm(p)
    if low in _FORBIDDEN_REPAIR_OUTPUTS:
        return True
    if len(p.split()) == 1:
        if _BARE_VERB_RE.match(p):
            return True
        if map_to_capability_synonym(p):
            return False
        return True
    if _FRAGMENT_RE.match(p):
        return True
    if low.startswith("including "):
        return True
    return False


def map_to_capability_synonym(phrase: str) -> str | None:
    low = _norm(phrase)
    if not low:
        return None
    if low in _CAPABILITY_SYNONYMS:
        mapped = _CAPABILITY_SYNONYMS[low].strip()
        return mapped if mapped else None
    if is_credential_competency_term(phrase):
        mapped = credential_term_to_skill_term(phrase)
        if mapped and _norm(mapped) not in _FORBIDDEN_REPAIR_OUTPUTS:
            return mapped
        return None
    for key, val in _CAPABILITY_SYNONYMS.items():
        if key in low or low in key:
            v = val.strip()
            if v and _norm(v) not in _FORBIDDEN_REPAIR_OUTPUTS:
                return v
    return None


def _term_support_ok(
    term: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str],
    resume_support_blob_lower: str,
) -> bool:
    return term_supports_resume_or_graph(
        term,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        resume_support_blob_lower=resume_support_blob_lower,
    )


def _coerce_term_support(
    term: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str],
    skill_rows_by_id: dict[str, dict[str, Any]],
    default_fact_id: str,
) -> dict[str, Any] | None:
    phrase = term_phrase(term)
    if len(phrase.split()) == 1:
        expanded = map_to_capability_synonym(phrase)
        if expanded:
            phrase = expanded
    if not phrase or is_raw_fragment_term(phrase):
        mapped = map_to_capability_synonym(phrase)
        if not mapped or is_raw_fragment_term(mapped):
            return None
        phrase = mapped

    from apps_rg.runtime.sections.competencies_lane_runtime import _fix_fact_id_typos

    sids: list[str] = []
    for x in term.get("source_fact_ids") or []:
        if not str(x).strip():
            continue
        base = _fix_fact_id_typos(str(x), allowed_fact_ids).split("_metric_")[0]
        if base in allowed_fact_ids and base not in sids:
            sids.append(base)
    skill_ids = [str(x) for x in (term.get("source_skill_ids") or []) if str(x).strip()]
    if not sids and default_fact_id in allowed_fact_ids:
        sids = [default_fact_id]
    for sk_id, row in skill_rows_by_id.items():
        if sk_id not in allowed_skill_ids:
            continue
        name = str(row.get("skill_name") or row.get("display_name") or "").strip().lower()
        if name and (_norm(phrase) in name or name in _norm(phrase)):
            if sk_id not in skill_ids:
                skill_ids.append(sk_id)
            for fid in row.get("fact_id_links") or []:
                fid_s = str(fid).split("_metric_")[0]
                if fid_s in allowed_fact_ids and fid_s not in sids:
                    sids.append(fid_s)

    if not sids and not skill_ids:
        return None

    support = SUPPORT_CLASS_FACT_ONLY
    if skill_ids and sids:
        support = SUPPORT_CLASS_FACT_AND_SKILL_GRAPH
    elif skill_ids:
        support = SUPPORT_CLASS_SKILL_GRAPH_ONLY

    out = {
        "term": phrase,
        "source_fact_ids": sids,
        "source_skill_ids": skill_ids,
        "support_class": support,
    }
    if is_credential_competency_term(phrase):
        return None
    if _is_low_rigor_two_word_phrase(phrase):
        ok, _ = check_competencies_no_all_generic_skill_phrase(
            [{"category_label": "x", "terms": [{"text": phrase, "source_fact_id": sids[0] if sids else "", "source_fact_ids": sids}]}]
        )
        if not ok:
            mapped = map_to_capability_synonym(phrase)
            if not mapped:
                return None
            out["term"] = mapped
    return out


def _select_default_bullet_fact_id(
    allowed_fact_ids: set[str],
    skill_rows_by_id: dict[str, dict[str, Any]],
) -> str:
    bullet_fids = sorted(x for x in allowed_fact_ids if str(x).startswith("bul_"))
    default_fid = bullet_fids[0] if bullet_fids else (sorted(allowed_fact_ids)[0] if allowed_fact_ids else "")
    if default_fid.startswith("fact_certs"):
        for fid in bullet_fids:
            default_fid = fid
            break
    for sk_row in skill_rows_by_id.values():
        for fid in sk_row.get("fact_id_links") or []:
            fid_s = str(fid).split("_metric_")[0]
            if fid_s in allowed_fact_ids and fid_s.startswith("bul_"):
                return fid_s
    return default_fid


def _accumulate_keyword_freq_from_categories(categories: list[dict[str, Any]]) -> dict[str, int]:
    from apps_rg.runtime.sections.competencies_rigor import GENERIC_SKILL_WORDS, _tokenize_phrase

    freq: dict[str, int] = {}
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        for raw_t in cat.get("terms") or []:
            phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "")
            for w in _tokenize_phrase(phrase):
                if w in GENERIC_SKILL_WORDS or len(w) < 4:
                    continue
                freq[w] = freq.get(w, 0) + 1
    return freq


def _phrase_violates_keyword_budget(
    phrase: str,
    freq: dict[str, int],
    *,
    max_token_repeat: int = 3,
) -> bool:
    from apps_rg.runtime.sections.competencies_rigor import GENERIC_SKILL_WORDS, _tokenize_phrase

    for w in _tokenize_phrase(phrase):
        if w in GENERIC_SKILL_WORDS or len(w) < 4:
            continue
        if freq.get(w, 0) + 1 > max_token_repeat:
            return True
    return False


def _register_phrase_keyword_freq(phrase: str, freq: dict[str, int]) -> None:
    from apps_rg.runtime.sections.competencies_rigor import GENERIC_SKILL_WORDS, _tokenize_phrase

    for w in _tokenize_phrase(phrase):
        if w in GENERIC_SKILL_WORDS or len(w) < 4:
            continue
        freq[w] = freq.get(w, 0) + 1


def _backfill_terms_for_category(
    cat: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str],
    skill_rows_by_id: dict[str, dict[str, Any]],
    resume_support_blob_lower: str,
    changelog: list[dict[str, Any]],
    default_fid: str = "",
    global_keyword_freq: dict[str, int] | None = None,
) -> None:
    terms = cat.get("terms")
    if not isinstance(terms, list):
        terms = []
        cat["terms"] = terms

    def _count() -> int:
        return sum(1 for t in terms if isinstance(t, dict) and term_phrase(t))

    tax = load_executive_capability_taxonomy()
    cid = str(cat.get("category_id") or "").strip()
    if not default_fid:
        default_fid = _select_default_bullet_fact_id(allowed_fact_ids, skill_rows_by_id)

    seen = {_norm(term_phrase(t)) for t in terms if term_phrase(t)}
    keyword_freq = global_keyword_freq if global_keyword_freq is not None else _accumulate_keyword_freq_from_categories([cat])

    backfill_rows = [
        row
        for row in (tax.get("backfill_capabilities") or [])
        if isinstance(row, dict) and str(row.get("category_id") or "") == cid
    ]
    while _count() < MIN_ITEMS_PER_CATEGORY and backfill_rows:
        added_any = False
        for row in backfill_rows:
            if _count() >= MIN_ITEMS_PER_CATEGORY:
                break
            phrase = str(row.get("term") or "").strip()
            if not phrase or _norm(phrase) in seen:
                continue
            if is_raw_fragment_term(phrase) or is_credential_competency_term(phrase):
                continue
            if _phrase_violates_keyword_budget(phrase, keyword_freq):
                continue
            candidate = {
                "term": phrase,
                "source_fact_ids": [default_fid] if default_fid else [],
                "source_skill_ids": [],
                "support_class": SUPPORT_CLASS_FACT_ONLY,
            }
            terms.append(candidate)
            seen.add(_norm(phrase))
            _register_phrase_keyword_freq(phrase, keyword_freq)
            added_any = True
            changelog.append(
                {
                    "operation": "backfill_taxonomy_capability",
                    "category_id": cid,
                    "term": phrase,
                }
            )
        if not added_any:
            for row in tax.get("backfill_capabilities") or []:
                if _count() >= MIN_ITEMS_PER_CATEGORY:
                    break
                if not isinstance(row, dict):
                    continue
                phrase = str(row.get("term") or "").strip()
                if not phrase or _norm(phrase) in seen:
                    continue
                if is_raw_fragment_term(phrase) or is_credential_competency_term(phrase):
                    continue
                if _phrase_violates_keyword_budget(phrase, keyword_freq):
                    continue
                candidate = {
                    "term": phrase,
                    "source_fact_ids": [default_fid] if default_fid else [],
                    "source_skill_ids": [],
                    "support_class": SUPPORT_CLASS_FACT_ONLY,
                }
                terms.append(candidate)
                seen.add(_norm(phrase))
                _register_phrase_keyword_freq(phrase, keyword_freq)
                changelog.append(
                    {
                        "operation": "backfill_taxonomy_capability_global_fallback",
                        "category_id": cid,
                        "term": phrase,
                    }
                )
                added_any = True
                break
        if not added_any:
            break


def _resolve_category_id(raw_label: str, raw_cid: str = "") -> str | None:
    from apps_rg.runtime.sections.competencies_v3_contract import approved_category_id_by_label

    if raw_cid and label_for_category_id(raw_cid):
        return raw_cid
    resolved = resolve_approved_category_label(raw_label)
    if resolved:
        return approved_category_id_by_label().get(resolved.lower())
    return approved_category_id_by_label().get(str(raw_label or "").strip().lower())


def _dedupe_terms(terms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for t in terms:
        if not isinstance(t, dict):
            continue
        ph = _norm(term_phrase(t))
        if not ph or ph in seen:
            continue
        seen.add(ph)
        out.append(t)
    return out


def apply_executive_capability_projection(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str] | None = None,
    skill_rows_by_id: dict[str, dict[str, Any]] | None = None,
    resume_support_blob_lower: str = "",
) -> dict[str, Any]:
    """Project LLM output into approved taxonomy buckets; drop fragments; backfill capabilities."""
    allowed_skill_ids = allowed_skill_ids or set()
    skill_rows_by_id = skill_rows_by_id or {}
    changelog = list(parsed.get("change_log") or [])
    if not isinstance(changelog, list):
        changelog = []

    default_fid = _select_default_bullet_fact_id(allowed_fact_ids, skill_rows_by_id)
    global_keyword_freq: dict[str, int] = {}

    sync_categories_competencies(parsed)
    tax = load_executive_capability_taxonomy()
    buckets: dict[str, list[dict[str, Any]]] = {
        str(row.get("category_id") or ""): []
        for row in tax.get("categories") or []
        if isinstance(row, dict) and row.get("category_id")
    }

    for cat in extract_categories(parsed):
        if not isinstance(cat, dict):
            continue
        cid = _resolve_category_id(
            str(cat.get("category_label") or ""),
            str(cat.get("category_id") or ""),
        )
        if not cid or cid not in buckets:
            changelog.append(
                {
                    "operation": "drop_unmapped_category",
                    "category_label": cat.get("category_label"),
                }
            )
            continue
        for raw_t in cat.get("terms") or []:
            coerced = _coerce_term_support(
                raw_t if isinstance(raw_t, dict) else {"term": str(raw_t)},
                allowed_fact_ids=allowed_fact_ids,
                allowed_skill_ids=allowed_skill_ids,
                skill_rows_by_id=skill_rows_by_id,
                default_fact_id=default_fid,
            )
            if coerced is None:
                orig = term_phrase(raw_t)
                if orig:
                    changelog.append({"operation": "drop_unsupported_term", "term": orig})
                continue
            if _norm(term_phrase(coerced)) in _FORBIDDEN_REPAIR_OUTPUTS:
                continue
            buckets[cid].append(coerced)
            _register_phrase_keyword_freq(term_phrase(coerced), global_keyword_freq)

    projected: list[dict[str, Any]] = []
    for row in tax.get("categories") or []:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("category_id") or "").strip()
        label = str(row.get("category_label") or "").strip()
        terms = _dedupe_terms(buckets.get(cid) or [])
        cat_fact_ids: list[str] = []
        for t in terms:
            for fid in t.get("source_fact_ids") or []:
                fs = str(fid).split("_metric_")[0]
                if fs in allowed_fact_ids and fs not in cat_fact_ids:
                    cat_fact_ids.append(fs)
        if not cat_fact_ids and default_fid:
            cat_fact_ids = [default_fid]
        new_cat = {
            "category_id": cid,
            "category_label": label,
            "terms": terms,
            "source_fact_ids": cat_fact_ids,
        }
        _backfill_terms_for_category(
            new_cat,
            allowed_fact_ids=allowed_fact_ids,
            allowed_skill_ids=allowed_skill_ids,
            skill_rows_by_id=skill_rows_by_id,
            resume_support_blob_lower=resume_support_blob_lower,
            changelog=changelog,
            default_fid=default_fid,
            global_keyword_freq=global_keyword_freq,
        )
        projected.append(new_cat)

    from apps_rg.runtime.sections.competencies_v3_contract import category_v3_from_legacy

    legacy_cats = [legacy_category_from_v3(c) for c in projected]
    sanitized, cert_log = sanitize_competencies_no_certification_category(legacy_cats)
    if cert_log:
        changelog.extend(cert_log)
    v3_cats = [category_v3_from_legacy(c) for c in sanitized]
    for cat in v3_cats:
        _backfill_terms_for_category(
            cat,
            allowed_fact_ids=allowed_fact_ids,
            allowed_skill_ids=allowed_skill_ids,
            skill_rows_by_id=skill_rows_by_id,
            resume_support_blob_lower=resume_support_blob_lower,
            changelog=changelog,
            default_fid=default_fid,
            global_keyword_freq=global_keyword_freq,
        )
        cat_fact_ids: list[str] = []
        for t in cat.get("terms") or []:
            if not isinstance(t, dict):
                continue
            for fid in t.get("source_fact_ids") or []:
                fs = str(fid).split("_metric_")[0]
                if fs in allowed_fact_ids and fs not in cat_fact_ids:
                    cat_fact_ids.append(fs)
        if not cat_fact_ids and default_fid:
            cat_fact_ids = [default_fid]
        cat["source_fact_ids"] = cat_fact_ids
    parsed["categories"] = v3_cats
    sync_categories_competencies(parsed)
    parsed["change_log"] = changelog
    return parsed


def run_competencies_v3_post_llm_pipeline(
    parsed: dict[str, Any],
    *,
    bullet_rows: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str] | None = None,
    skill_rows_by_id: dict[str, dict[str, Any]] | None = None,
    resume_support_blob: str,
    c0_proof_blob: str,
    bullet_texts_lower: list[str],
) -> dict[str, Any]:
    """Mirror competencies_lane_execution post-LLM repairs with finalize-last projection."""
    from apps_rg.runtime.sections.competencies_lane_runtime import (
        canonicalize_competency_terms_for_proof,
        coerce_structured_competencies_resume_support,
        collapse_duplicate_competency_terms,
        dedupe_structured_competency_terms,
        prune_claim_ledger_bullet_paste,
        rebuild_claim_ledger_from_competencies,
        reduce_competency_keyword_stuffing,
        repair_structured_competencies_source_facts,
    )

    allowed_skill_ids = allowed_skill_ids or set()
    skill_rows_by_id = skill_rows_by_id or {}
    sync_categories_competencies(parsed)
    collapse_duplicate_competency_terms(parsed, bullet_rows, resume_support_blob)
    repair_structured_competencies_source_facts(
        parsed,
        allowed_fact_ids=allowed_fact_ids,
        resume_support_blob_lower=c0_proof_blob,
    )
    coerce_structured_competencies_resume_support(
        parsed,
        bullet_rows,
        c0_proof_blob,
        bullet_texts_lower,
        allowed_fact_ids=allowed_fact_ids,
    )
    dedupe_structured_competency_terms(parsed)
    reduce_competency_keyword_stuffing(parsed)
    canonicalize_competency_terms_for_proof(parsed, allowed_fact_ids=allowed_fact_ids)
    coerce_structured_competencies_resume_support(
        parsed,
        bullet_rows,
        c0_proof_blob,
        bullet_texts_lower,
        allowed_fact_ids=allowed_fact_ids,
    )
    dedupe_structured_competency_terms(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
    prune_claim_ledger_bullet_paste(parsed)
    return finalize_competencies_v3_output(
        parsed,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=c0_proof_blob,
    )


def _swap_offending_term_for_safe_backfill(
    cat: dict[str, Any],
    worst_token: str,
    *,
    allowed_fact_ids: set[str],
    default_fid: str,
    keyword_freq: dict[str, int],
    changelog: list[dict[str, Any]],
) -> bool:
    """Replace one term containing worst_token when category is at MIN_ITEMS floor."""
    from apps_rg.runtime.sections.competencies_rigor import GENERIC_SKILL_WORDS, _tokenize_phrase

    from apps_rg.runtime.sections.competencies_v3_contract import (
        approved_category_id_by_label,
        resolve_approved_category_label,
    )

    cid = str(cat.get("category_id") or "").strip()
    if not cid:
        resolved = resolve_approved_category_label(str(cat.get("category_label") or ""))
        if resolved:
            cid = approved_category_id_by_label().get(resolved.lower()) or ""
    terms = cat.get("terms")
    if not isinstance(terms, list):
        return False
    tax = load_executive_capability_taxonomy()
    backfill_rows = [
        row
        for row in (tax.get("backfill_capabilities") or [])
        if isinstance(row, dict) and str(row.get("category_id") or "") == cid
    ]
    for raw_t in terms:
        if not isinstance(raw_t, dict):
            continue
        phrase = term_phrase(raw_t)
        words = [
            w
            for w in _tokenize_phrase(phrase)
            if w not in GENERIC_SKILL_WORDS and len(w) >= 4
        ]
        if worst_token not in words:
            continue
        for row in backfill_rows:
            candidate = str(row.get("term") or "").strip()
            if not candidate or is_raw_fragment_term(candidate):
                continue
            cand_words = [
                w
                for w in _tokenize_phrase(candidate)
                if w not in GENERIC_SKILL_WORDS and len(w) >= 4
            ]
            if worst_token in cand_words:
                continue
            trial_freq = dict(keyword_freq)
            for w in words:
                if w in trial_freq:
                    trial_freq[w] = max(0, trial_freq[w] - 1)
            if _phrase_violates_keyword_budget(candidate, trial_freq, max_token_repeat=3):
                continue
            for w in words:
                if w in keyword_freq:
                    keyword_freq[w] = max(0, keyword_freq[w] - 1)
            raw_t["term"] = candidate
            if "text" in raw_t:
                raw_t["text"] = candidate
            sids = [x for x in (raw_t.get("source_fact_ids") or []) if str(x).split("_metric_")[0] in allowed_fact_ids]
            if not sids and default_fid:
                sids = [default_fid]
            raw_t["source_fact_ids"] = sids
            if raw_t.get("source_fact_id") and sids:
                raw_t["source_fact_id"] = sids[0]
            _register_phrase_keyword_freq(candidate, keyword_freq)
            changelog.append(
                {
                    "operation": "swap_keyword_repeat_for_safe_backfill",
                    "category_id": cid,
                    "from_term": phrase,
                    "to_term": candidate,
                    "overloaded_token": worst_token,
                }
            )
            return True
    return False


def _trim_excess_keyword_repeats(
    parsed: dict[str, Any],
    *,
    max_token_repeat: int = 3,
    allowed_fact_ids: set[str] | None = None,
    default_fid: str = "",
) -> None:
    """Drop terms until x2_competencies_keyword_repetition_limit passes; preserve category floors."""
    from apps_rg.runtime.sections.competencies_rigor import (
        GENERIC_SKILL_WORDS,
        MIN_ITEMS_PER_CATEGORY,
        _tokenize_phrase,
        check_competencies_keyword_repetition_limit,
    )

    sync_categories_competencies(parsed)
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        return
    changelog = parsed.setdefault("change_log", [])
    if not isinstance(changelog, list):
        changelog = []
        parsed["change_log"] = changelog

    for _ in range(96):
        ok, reason = check_competencies_keyword_repetition_limit(
            comps, max_token_repeat=max_token_repeat
        )
        if ok:
            return
        worst_token = ""
        if reason:
            m = re.search(r"token='([^']+)'", reason)
            if m:
                worst_token = m.group(1)
        if not worst_token:
            return
        removed = False
        for cat in sorted(
            [c for c in comps if isinstance(c, dict)],
            key=lambda c: len(c.get("terms") or []),
            reverse=True,
        ):
            terms_raw = cat.get("terms")
            if not isinstance(terms_raw, list) or len(terms_raw) <= MIN_ITEMS_PER_CATEGORY:
                continue
            kept: list[Any] = []
            dropped = False
            for raw_t in terms_raw:
                phrase = term_phrase(raw_t) if isinstance(raw_t, dict) else str(raw_t or "")
                words = [
                    w
                    for w in _tokenize_phrase(phrase)
                    if w not in GENERIC_SKILL_WORDS and len(w) >= 4
                ]
                if not dropped and worst_token in words:
                    changelog.append(
                        {
                            "operation": "drop_keyword_repeat_for_x2_limit",
                            "category_label": cat.get("category_label"),
                            "phrase": phrase,
                            "overloaded_token": worst_token,
                        }
                    )
                    dropped = True
                    continue
                kept.append(raw_t)
            if dropped:
                cat["terms"] = kept
                removed = True
                break
        if not removed:
            if not allowed_fact_ids:
                return
            freq = _accumulate_keyword_freq_from_categories(extract_categories(parsed))
            swapped = False
            for cat in [c for c in comps if isinstance(c, dict)]:
                if _swap_offending_term_for_safe_backfill(
                    cat,
                    worst_token,
                    allowed_fact_ids=allowed_fact_ids,
                    default_fid=default_fid,
                    keyword_freq=freq,
                    changelog=changelog,
                ):
                    swapped = True
                    break
            if not swapped:
                return
    sync_categories_competencies(parsed)


def _reapply_taxonomy_floors(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str],
    skill_rows_by_id: dict[str, dict[str, Any]],
    resume_support_blob_lower: str,
) -> dict[str, Any]:
    """Re-backfill categories after post-projection dedupe/keyword reduction."""
    from apps_rg.runtime.sections.competencies_v3_contract import category_v3_from_legacy

    comps = parsed.get("competencies")
    if isinstance(comps, list) and comps:
        parsed["categories"] = [
            category_v3_from_legacy(c) for c in comps if isinstance(c, dict)
        ]
    changelog = list(parsed.get("change_log") or [])
    if not isinstance(changelog, list):
        changelog = []
    default_fid = _select_default_bullet_fact_id(allowed_fact_ids, skill_rows_by_id)
    sync_categories_competencies(parsed)
    cats = [c for c in extract_categories(parsed) if isinstance(c, dict)]
    global_keyword_freq = _accumulate_keyword_freq_from_categories(cats)
    for cat in cats:
        _backfill_terms_for_category(
            cat,
            allowed_fact_ids=allowed_fact_ids,
            allowed_skill_ids=allowed_skill_ids,
            skill_rows_by_id=skill_rows_by_id,
            resume_support_blob_lower=resume_support_blob_lower,
            changelog=changelog,
            default_fid=default_fid,
            global_keyword_freq=global_keyword_freq,
        )
        cat_fact_ids: list[str] = []
        for t in cat.get("terms") or []:
            if not isinstance(t, dict):
                continue
            for fid in t.get("source_fact_ids") or []:
                fs = str(fid).split("_metric_")[0]
                if fs in allowed_fact_ids and fs not in cat_fact_ids:
                    cat_fact_ids.append(fs)
        if not cat_fact_ids and default_fid:
            cat_fact_ids = [default_fid]
        cat["source_fact_ids"] = cat_fact_ids
    parsed["change_log"] = changelog
    sync_categories_competencies(parsed)
    return parsed


def finalize_competencies_v3_output(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str],
    allowed_skill_ids: set[str] | None = None,
    skill_rows_by_id: dict[str, dict[str, Any]] | None = None,
    resume_support_blob_lower: str = "",
) -> dict[str, Any]:
    """Final seam: executive projection must run after collapse/dedupe/keyword reduction."""
    from apps_rg.runtime.sections.competencies_lane_runtime import (
        dedupe_structured_competency_terms,
        rebuild_claim_ledger_from_competencies,
        reduce_competency_keyword_stuffing,
    )

    allowed_skill_ids = allowed_skill_ids or set()
    skill_rows_by_id = skill_rows_by_id or {}
    sync_categories_competencies(parsed)
    out = apply_executive_capability_projection(
        parsed,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    sync_categories_competencies(out)
    dedupe_structured_competency_terms(out)
    reduce_competency_keyword_stuffing(out)
    _reapply_taxonomy_floors(
        out,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    reduce_competency_keyword_stuffing(out)
    _reapply_taxonomy_floors(
        out,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    default_fid = _select_default_bullet_fact_id(allowed_fact_ids, skill_rows_by_id)
    _trim_excess_keyword_repeats(
        out,
        allowed_fact_ids=allowed_fact_ids,
        default_fid=default_fid,
    )
    from apps_rg.runtime.sections.section_authority_repairs import prune_competencies_rigor_failing_terms

    pruned = prune_competencies_rigor_failing_terms(out)
    if pruned:
        clog = list(out.get("change_log") or [])
        clog.append(
            {
                "operation": "prune_rigor_failing_competency_terms",
                "reason": "; ".join(pruned[:8]),
            }
        )
        out["change_log"] = clog
    _reapply_taxonomy_floors(
        out,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    _trim_excess_keyword_repeats(
        out,
        allowed_fact_ids=allowed_fact_ids,
        default_fid=default_fid,
    )
    from apps_rg.runtime.sections.competencies_lane_runtime import (
        repair_structured_competencies_source_facts,
    )

    repair_structured_competencies_source_facts(
        out,
        allowed_fact_ids=allowed_fact_ids,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    dedupe_structured_competency_terms(out)
    _reapply_taxonomy_floors(
        out,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=resume_support_blob_lower,
    )
    dedupe_structured_competency_terms(out)
    from apps_rg.runtime.sections.competencies_v3_contract import category_v3_from_legacy

    comps_final = out.get("competencies")
    if isinstance(comps_final, list):
        out["categories"] = [
            category_v3_from_legacy(c) for c in comps_final if isinstance(c, dict)
        ]
    rebuild_claim_ledger_from_competencies(out, allowed_fact_ids)
    sync_categories_competencies(out)
    return out


__all__ = [
    "apply_executive_capability_projection",
    "finalize_competencies_v3_output",
    "is_raw_fragment_term",
    "map_to_capability_synonym",
    "run_competencies_v3_post_llm_pipeline",
]
