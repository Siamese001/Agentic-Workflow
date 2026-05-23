"""Deterministic display repairs aligned with rigor-critical X2 gates (apps_rg only)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences


def _sentence_fails_credential_dump(sentence: str) -> bool:
    from apps_rg.runtime.sections.competencies_certification_contract import (
        is_credential_competency_term,
    )

    markers = (
        "aws certified",
        "databricks",
        "fellow of the society of actuaries",
        "society of actuaries",
        "fsa",
        "basel iii",
        "ccar",
        "certified solutions architect",
        "lakehouse fundamentals",
    )
    low = sentence.lower()
    hits = sum(1 for m in markers if m in low)
    if hits >= 3:
        return True
    if is_credential_competency_term(sentence) and hits >= 2:
        return True
    if re.search(r"\bcredentials?\s+reinforce\b", low) and hits >= 2:
        return True
    return False


def strip_target_company_tailoring_sentences(
    resume_display_text: str,
    target_company: str,
) -> tuple[str, list[str]]:
    """Remove sentences that name TARGET_COMPANY as employer/alignment (x2_target_company_as_experience_zero)."""
    company = str(target_company or "").strip()
    if not company:
        return resume_display_text, []
    co_pat = re.escape(company)
    employer_hit = re.compile(rf"\b(?:at|for|with)\s+{co_pat}\b", re.IGNORECASE)
    align_hit = re.compile(rf"align\s+with\s+{co_pat}\b", re.IGNORECASE)
    sents = split_sentences(str(resume_display_text or "").strip())
    if not sents:
        return resume_display_text, []
    kept: list[str] = []
    removed: list[str] = []
    for sent in sents:
        if employer_hit.search(sent) or align_hit.search(sent):
            removed.append(sent[:120])
        else:
            kept.append(sent)
    if not kept or len(kept) == len(sents):
        return resume_display_text, removed
    return " ".join(kept).strip(), removed


def strip_exec_summary_credential_dump_sentences(resume_display_text: str) -> tuple[str, list[str]]:
    """Remove credential-inventory sentences so x2_exec_summary_no_credential_dump can pass."""
    sents = split_sentences(str(resume_display_text or "").strip())
    if not sents:
        return resume_display_text, []
    kept: list[str] = []
    removed: list[str] = []
    for sent in sents:
        if _sentence_fails_credential_dump(sent):
            removed.append(sent[:120])
        else:
            kept.append(sent)
    if not kept:
        return resume_display_text, removed
    return " ".join(kept).strip(), removed


def _exec_summary_shape_ok(resume_display_text: str, parsed: dict[str, Any]) -> tuple[bool, str]:
    from apps_rg.runtime.validators.executive_summary_x2 import (
        check_exec_summary_meta_filler_patterns,
        check_exec_summary_no_credential_dump,
        check_exec_summary_paragraph_max_words,
        check_exec_summary_sentence_count_6,
    )

    failures: list[str] = []
    bounds_ok, bounds_reason = check_exec_summary_paragraph_max_words(resume_display_text, parsed)
    if not bounds_ok and bounds_reason:
        failures.append(bounds_reason)
    meta_ok, meta_reason = check_exec_summary_meta_filler_patterns(resume_display_text)
    if not meta_ok and meta_reason:
        failures.append(meta_reason)
    cred_ok, cred_reason = check_exec_summary_no_credential_dump(resume_display_text)
    if not cred_ok and cred_reason:
        failures.append(cred_reason)
    sent_ok, sent_reason = check_exec_summary_sentence_count_6(resume_display_text)
    if not sent_ok and sent_reason:
        failures.append(sent_reason)
    if failures:
        return False, "; ".join(failures)
    return True, ""


def apply_exec_summary_display_authority_repairs(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str] | None = None,
    plan_facts: list[dict[str, Any]] | None = None,
    artifact_dir: Path | None = None,
    target_company: str = "",
) -> dict[str, Any]:
    """In-place repair of resume_display_text for rigor-critical X2 gates."""
    if not isinstance(parsed, dict):
        return parsed
    text = str(parsed.get("resume_display_text") or "").strip()
    if not text:
        return parsed
    clog = list(parsed.get("change_log") or [])
    repaired, removed = strip_exec_summary_credential_dump_sentences(text)
    if removed and repaired != text:
        text = repaired
        clog.append(
            {
                "operation": "strip_credential_dump_sentences",
                "reason": f"removed_{len(removed)}_sentences",
            }
        )
    co_repaired, co_removed = strip_target_company_tailoring_sentences(text, target_company)
    if co_removed and co_repaired != text:
        text = co_repaired
        clog.append(
            {
                "operation": "strip_target_company_tailoring_sentences",
                "reason": f"removed_{len(co_removed)}_sentences",
            }
        )
        if artifact_dir is not None:
            from apps_rg.runtime.section_repair_ledger import (
                KIND_MECHANICAL,
                record_repair,
            )

            record_repair(
                artifact_dir,
                kind=KIND_MECHANICAL,
                operation="strip_credential_dump_sentences",
                reason=f"removed_{len(removed)}_sentences",
                replaced_l2=False,
            )
    parsed["resume_display_text"] = text
    parsed["change_log"] = clog
    shape_ok, reject_reason = _exec_summary_shape_ok(text, parsed)
    if shape_ok:
        return parsed
    from apps_rg.runtime.section_repair_policy import exec_summary_display_graph_fallback_allowed

    if not exec_summary_display_graph_fallback_allowed():
        if artifact_dir is not None:
            from apps_rg.runtime.section_repair_ledger import record_repair

            record_repair(
                artifact_dir,
                kind="blocked_deterministic_rewrite",
                operation="graph_only_display_authority_fallback",
                reason=(reject_reason or "shape_fail")[:240],
                replaced_l2=False,
            )
        return parsed
    facts = plan_facts
    if facts is None:
        sfp = parsed.get("selected_fact_plan")
        if isinstance(sfp, dict):
            facts = list(sfp.get("facts") or [])
    allowed = allowed_fact_ids
    if allowed is None and facts:
        allowed = {
            str(f.get("fact_id") or f.get("candidate_fact_id") or "").strip()
            for f in facts
            if isinstance(f, dict) and str(f.get("fact_id") or f.get("candidate_fact_id") or "").strip()
        }
    if not facts or not allowed:
        return parsed
    from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
        build_graph_only_executive_summary_from_facts,
    )

    resume, ledger = build_graph_only_executive_summary_from_facts(facts, allowed)
    if not resume:
        return parsed
    post_ok, _ = _exec_summary_shape_ok(resume, parsed)
    if not post_ok:
        return parsed
    parsed["resume_display_text"] = resume
    parsed["claim_ledger"] = ledger
    clog.append(
        {
            "operation": "graph_only_display_authority_fallback",
            "reason": reject_reason[:240],
        }
    )
    parsed["change_log"] = clog
    if artifact_dir is not None:
        from apps_rg.runtime.section_repair_ledger import (
            KIND_DETERMINISTIC_REWRITE,
            record_repair,
        )

        record_repair(
            artifact_dir,
            kind=KIND_DETERMINISTIC_REWRITE,
            operation="graph_only_display_authority_fallback",
            reason=(reject_reason or "")[:240],
            replaced_l2=True,
        )
    return parsed


_IBM_META_TAIL_RE = re.compile(
    r"\s+without\s+(?:claiming|asserting)\b[^.]*\.?\s*$",
    re.IGNORECASE,
)
_IBM_CAREER_BRIDGE_RE = re.compile(
    r"\s+(?:supported\s+later|subsequent\s+roles|later\s+production\s+ai)\b[^.]*\.?\s*$",
    re.IGNORECASE,
)


def sanitize_ibm_narrative_display_text(narrative_sentence: str) -> tuple[str, bool]:
    """Strip meta-disclaimer and career-bridge tails from IBM narrative display."""
    text = str(narrative_sentence or "").strip()
    if not text:
        return text, False
    original = text
    text = _IBM_META_TAIL_RE.sub(".", text).strip()
    text = _IBM_CAREER_BRIDGE_RE.sub(".", text).strip()
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\.{2,}", ".", text)
    if text and text[-1] not in ".!?":
        text = text + "."
    return text, text != original


def prune_competencies_rigor_failing_terms(parsed: dict[str, Any]) -> list[str]:
    """Drop or remap terms that fail low-rigor / metrics-as-skills X2 gates."""
    from apps_rg.runtime.sections.competencies_certification_contract import (
        is_credential_competency_term,
    )
    from apps_rg.runtime.sections.competencies_capability_projection import map_to_capability_synonym
    from apps_rg.runtime.sections.competencies_rigor import (
        CAPABILITY_CONTEXT_WORDS,
        _METRICS_ONLY_RE,
        _is_low_rigor_two_word_phrase,
    )
    from apps_rg.runtime.sections.competencies_term_phrase import term_phrase
    from apps_rg.runtime.sections.competencies_v3_contract import sync_categories_competencies

    removed: list[str] = []
    cats = parsed.get("competencies") or parsed.get("categories") or []
    if not isinstance(cats, list):
        return removed
    for cat in cats:
        if not isinstance(cat, dict):
            continue
        label = str(cat.get("category_label") or cat.get("label") or "")
        terms_in = cat.get("terms") or []
        kept: list[Any] = []
        for raw in terms_in:
            phrase = term_phrase(raw)
            if not phrase:
                continue
            drop = False
            if _is_low_rigor_two_word_phrase(phrase):
                mapped = map_to_capability_synonym(phrase)
                if mapped and isinstance(raw, dict):
                    raw = dict(raw)
                    raw["text"] = mapped
                    raw["term"] = mapped
                    phrase = mapped
                else:
                    removed.append(f"low_rigor_two_word:{label}:{phrase}")
                    drop = True
            if not drop and _METRICS_ONLY_RE.search(phrase):
                low = phrase.lower()
                if not any(ctx in low for ctx in CAPABILITY_CONTEXT_WORDS) and not is_credential_competency_term(
                    phrase
                ):
                    mapped = map_to_capability_synonym(phrase)
                    if mapped and "platform" in mapped.lower():
                        if isinstance(raw, dict):
                            raw = dict(raw)
                            raw["text"] = mapped
                            raw["term"] = mapped
                    else:
                        removed.append(f"metrics_as_skill:{label}:{phrase}")
                        drop = True
            if not drop:
                kept.append(raw)
        cat["terms"] = kept
    sync_categories_competencies(parsed)
    return removed


__all__ = [
    "apply_exec_summary_display_authority_repairs",
    "prune_competencies_rigor_failing_terms",
    "sanitize_ibm_narrative_display_text",
    "strip_exec_summary_credential_dump_sentences",
]
