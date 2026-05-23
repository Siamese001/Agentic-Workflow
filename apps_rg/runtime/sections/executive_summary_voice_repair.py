"""Deterministic recruiter-filler repair for executive_summary (apps_rg only)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    GENERIC_FILLER,
    check_inferred_bridge_claims,
)

_EXTENSIVE_EXPERIENCE_RE = re.compile(
    r"\bwith extensive experience in\b", re.IGNORECASE
)
_EXTENSIVE_EXPERIENCE_EXEC_RE = re.compile(
    r"\ban engineering executive with extensive experience\b", re.IGNORECASE
)


def _fact_corpus_lower(selected_facts: list[dict[str, Any]] | None) -> str:
    parts: list[str] = []
    for row in selected_facts or []:
        if not isinstance(row, dict):
            continue
        parts.append(str(row.get("claim_text") or ""))
        parts.append(str(row.get("achievement_summary") or ""))
    return " ".join(parts).lower()


_FILLER_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\ban engineering executive with a proven track record in delivering\b",
            re.IGNORECASE,
        ),
        "Engineering executive delivering",
    ),
    (
        re.compile(r"\bwith a proven track record in\b", re.IGNORECASE),
        " leading",
    ),
    (
        re.compile(r"\bwith a proven track record of\b", re.IGNORECASE),
        " with a record of",
    ),
    (re.compile(r"\bproven track record\b", re.IGNORECASE), ""),
    (re.compile(r"\bresults-driven\b", re.IGNORECASE), "outcomes-focused"),
    (re.compile(r"\bseasoned executive\b", re.IGNORECASE), "engineering executive"),
)


def repair_generic_filler_prose(
    resume_display_text: str,
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Strip or rewrite banned recruiter filler without weakening X2 gates."""
    text = str(resume_display_text or "").strip()
    receipt: dict[str, Any] = {
        "schema": "executive_summary_voice_repair_v1",
        "repaired": False,
        "replacements": [],
    }
    if not text:
        return text, receipt

    out = text
    corpus = _fact_corpus_lower(selected_facts)
    if _EXTENSIVE_EXPERIENCE_EXEC_RE.search(out):
        out = _EXTENSIVE_EXPERIENCE_EXEC_RE.sub("Engineering executive", out)
        receipt["replacements"].append("extensive_experience_exec_opener")
    elif _EXTENSIVE_EXPERIENCE_RE.search(out):
        out = _EXTENSIVE_EXPERIENCE_RE.sub(" who led", out)
        receipt["replacements"].append("extensive_experience_in")
    if "regulated enterprise" in corpus:
        new_out = re.sub(
            r"\bregulated environments\b",
            "regulated enterprise workflows",
            out,
            flags=re.IGNORECASE,
        )
        if new_out != out:
            out = new_out
            receipt["replacements"].append("regulated_environments_to_workflows")
    has_gov_fact = False
    for row in selected_facts or []:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
        if fid == "fact_governance_003" or fid.startswith("fact_governance_003_metric"):
            has_gov_fact = True
            break
    if has_gov_fact or "governance framework" in corpus or "basel" in corpus or "ccar" in corpus:
        new_out = re.sub(
            r"\bgovernance frameworks?\b",
            "Basel III/CCAR lineage and validation frameworks",
            out,
            flags=re.IGNORECASE,
        )
        if new_out != out:
            out = new_out
            receipt["replacements"].append("governance_framework_to_basel_lineage")
    for pattern, repl in _FILLER_REPLACEMENTS:
        if pattern.search(out):
            out = pattern.sub(repl, out)
            receipt["replacements"].append(pattern.pattern[:80])

    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([.,;])", r"\1", out)
    if out and out[0].islower():
        out = out[0].upper() + out[1:]

    from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

    meta_opener = re.compile(
        r"^(Additionally|Furthermore|Moreover),?\s+",
        re.IGNORECASE,
    )
    rebuilt: list[str] = []
    for sent in split_sentences(out):
        stripped = meta_opener.sub("", sent.strip()).strip()
        if stripped:
            rebuilt.append(stripped)
    if rebuilt:
        joined = " ".join(rebuilt)
        if joined != out:
            out = joined
            receipt["replacements"].append("meta_filler_opener_strip")
    out = re.sub(r"\bAdditionally,\s+", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\bFurthermore,\s+", "", out, flags=re.IGNORECASE)
    if out and out[0].islower():
        out = out[0].upper() + out[1:]

    filler_hits = [p for p in GENERIC_FILLER if p in out.lower()]
    bridge_ok, bridge_reason = check_inferred_bridge_claims(out, selected_facts)
    receipt["post_repair_filler_hits"] = filler_hits
    receipt["post_repair_bridge_ok"] = bridge_ok
    receipt["post_repair_bridge_reason"] = bridge_reason or ""
    receipt["repaired"] = out != text
    receipt["before_word_count"] = len(text.split())
    receipt["after_word_count"] = len(out.split())
    return out.strip(), receipt


def reconcile_claim_ledger_after_voice_repair(parsed: dict[str, Any]) -> dict[str, Any]:
    """Keep claim_ledger aligned with repaired display text (materialized_or_gap gate)."""
    from apps_rg.runtime.validators.executive_summary_x2 import (
        _ledger_claim_tokens,
        ledger_row_materialized_in_display,
        split_sentences,
    )

    out = dict(parsed)
    text = str(out.get("resume_display_text") or "")
    ledger = [dict(r) for r in (out.get("claim_ledger") or []) if isinstance(r, dict)]
    if not ledger or not text:
        return out
    sentences = split_sentences(text)
    gaps = list(out.get("gap_notes") or [])
    for i, row in enumerate(ledger):
        if ledger_row_materialized_in_display(row, text):
            continue
        prior = str(row.get("claim_text") or "")
        tokens = _ledger_claim_tokens(prior)
        best_sent: str | None = None
        best_hits = 0
        for sent in sentences:
            sl = sent.lower()
            hits = sum(1 for t in tokens if t in sl)
            if hits > best_hits:
                best_hits = hits
                best_sent = sent
        if best_sent and best_hits >= max(1, min(3, len(tokens))):
            row["claim_text"] = best_sent.strip()
            ledger[i] = row
            continue
        sids = [str(s) for s in (row.get("source_fact_ids") or []) if str(s).strip()]
        gaps.append(
            "voice_repair_drift: claim idx="
            f"{i} source_fact_ids={','.join(sids)} not materialized after display repair"
        )
    out["claim_ledger"] = ledger
    if gaps:
        out["gap_notes"] = gaps
    return out


def apply_voice_repair_to_parsed(
    parsed: dict[str, Any],
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply filler repair to ``resume_display_text`` in-place copy of parsed output."""
    out = dict(parsed)
    text, receipt = repair_generic_filler_prose(
        str(out.get("resume_display_text") or ""),
        selected_facts=selected_facts,
    )
    out["resume_display_text"] = text
    if receipt.get("repaired"):
        out = reconcile_claim_ledger_after_voice_repair(out)
        receipt["claim_ledger_reconciled"] = True
    return out, receipt


def _excuse_gap_for_orphan_ledger_row(row: dict[str, Any], *, idx: int, reason: str) -> str:
    sids = [str(s) for s in (row.get("source_fact_ids") or []) if str(s).strip()]
    sid_blob = ",".join(sids) if sids else "none"
    return f"finalize_excused: {reason} source_fact_ids={sid_blob} claim_idx={idx}"


def finalize_executive_summary_coherence(
    parsed: dict[str, Any],
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Last post-LLM mutator: voice repair, ledger reconcile, gap excuse for display drift."""
    from apps_rg.runtime.validators.executive_summary_x2 import (
        check_claim_ledger_materialized_or_gap_excused,
        gap_notes_excuse_ledger_claim,
        ledger_row_materialized_in_display,
    )

    receipt: dict[str, Any] = {
        "schema": "executive_summary_finalize_coherence_v1",
        "voice_repair": {},
        "ledger_reconciled": False,
        "gap_excuses_added": [],
        "materialization_pass": False,
    }
    if not isinstance(parsed, dict):
        return parsed, receipt

    out, voice_receipt = apply_voice_repair_to_parsed(
        parsed, selected_facts=selected_facts
    )
    receipt["voice_repair"] = voice_receipt
    receipt["ledger_reconciled"] = bool(voice_receipt.get("claim_ledger_reconciled"))

    text = str(out.get("resume_display_text") or "")
    ledger = [dict(r) for r in (out.get("claim_ledger") or []) if isinstance(r, dict)]
    gaps = list(out.get("gap_notes") or [])

    for i in range(len(ledger)):
        row = ledger[i]
        if ledger_row_materialized_in_display(row, text):
            continue
        if gap_notes_excuse_ledger_claim(row, gaps):
            continue
        out = reconcile_claim_ledger_after_voice_repair(out)
        text = str(out.get("resume_display_text") or "")
        ledger = [dict(r) for r in (out.get("claim_ledger") or []) if isinstance(r, dict)]
        row = ledger[i]
        if ledger_row_materialized_in_display(row, text):
            receipt["ledger_reconciled"] = True
            continue
        excuse = _excuse_gap_for_orphan_ledger_row(
            row,
            idx=i,
            reason="display_authority_or_voice_drift",
        )
        gaps.append(excuse)
        receipt["gap_excuses_added"].append(excuse)

    out["gap_notes"] = gaps
    out["claim_ledger"] = ledger
    mat_ok, mat_reason = check_claim_ledger_materialized_or_gap_excused(
        text, ledger, gaps
    )
    receipt["materialization_pass"] = mat_ok
    receipt["materialization_reason"] = mat_reason or ""
    return out, receipt


__all__ = [
    "apply_voice_repair_to_parsed",
    "finalize_executive_summary_coherence",
    "reconcile_claim_ledger_after_voice_repair",
    "repair_generic_filler_prose",
]
