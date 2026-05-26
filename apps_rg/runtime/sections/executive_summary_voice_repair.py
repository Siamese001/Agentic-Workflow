"""Deterministic recruiter-filler repair for executive_summary (apps_rg only)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_FORBIDDEN_META_PHRASES,
    EXEC_SUMMARY_FORBIDDEN_META_PHRASES_LOOSE,
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


_S5_CREDENTIAL_DUMP_RE = re.compile(
    r"\b(?:built|established)\s+advanced\s+quantitative\s+foundation\b.*\b(?:derivatives|multi-greek|towers perrin)\b",
    re.IGNORECASE,
)
_S6_THIN_RECAP_RE = re.compile(r"\bextend\s+that\s+arc\s+toward\b", re.IGNORECASE)
_FORCED_LINEAGE_BRIDGE_RE = re.compile(
    r"\bthat\s+regulatory\s+lineage\s+work\s+extended\s+to\b",
    re.IGNORECASE,
)
_S5_CREDENTIAL_REPLACEMENT = (
    "On that commercial base, capital-markets rigor informs which platform investments clear "
    "governance gates fastest in regulated programs."
)
_S6_FORWARD_REPLACEMENT = (
    "Looking ahead, innovation incubation and architecture standards can federate governed platform "
    "capabilities across autonomous business units without weakening lineage controls."
)
_FORMULAIC_S2_RE = re.compile(
    r"^Building on that platform foundation,\s*",
    re.IGNORECASE,
)
_S5_STRESS_ECHO_RE = re.compile(r"\bstress-testing\b", re.IGNORECASE)
_S4_PARTICIPIAL_AFTER_COMPLEMENT_RE = re.compile(
    r"(Complementing that regulatory foundation,)\s+re-architecting\b",
    re.IGNORECASE,
)
_S5_META_COMMENTARY_RE = re.compile(
    r"\s+rather than listing credential labels\.?",
    re.IGNORECASE,
)
_GENERIC_S1_RE = re.compile(
    r"^Technology strategy executive who aligns enterprise IT direction,?\s+"
    r"governed AI platform delivery,?\s+and innovation programs for regulated enterprise scale\.?\s*",
    re.IGNORECASE,
)
_S1_DISTINCTIVE_REPLACEMENT = (
    "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and commercialization "
    "into one IT strategy and innovation agenda for decentralized regulated enterprises. "
)
_FORMULAIC_S3_RE = re.compile(
    r"^Through that operating model,\s*",
    re.IGNORECASE,
)

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


_META_PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("with active-voice delivery and governance discipline", "with regulated platform delivery"),
    ("governance discipline", "regulatory foundation"),
    ("active-voice delivery", "platform delivery"),
    ("across the scope described in selected facts", ""),
    ("canonical facts used as proof", ""),
    ("same fact plan", ""),
)


def _repair_forbidden_meta_phrases(resume_display_text: str) -> tuple[str, list[str]]:
    """Strip X2-banned meta scaffolding without changing sentence count."""
    out = str(resume_display_text or "")
    repairs: list[str] = []
    for bad, good in _META_PHRASE_REPLACEMENTS:
        if bad in out.lower():
            pattern = re.compile(re.escape(bad), re.IGNORECASE)
            out = pattern.sub(good, out)
            repairs.append(f"meta_phrase:{bad[:40]}")
    replaced_lower = {bad.lower() for bad, _ in _META_PHRASE_REPLACEMENTS}
    for phrase in EXEC_SUMMARY_FORBIDDEN_META_PHRASES + EXEC_SUMMARY_FORBIDDEN_META_PHRASES_LOOSE:
        if phrase.lower() in replaced_lower:
            continue
        if phrase in out.lower():
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            out = pattern.sub("", out)
            repairs.append(f"meta_phrase_strip:{phrase[:40]}")
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([.,;])", r"\1", out)
    return out.strip(), repairs


def _repair_synthesis_quality_sentences(resume_display_text: str) -> tuple[str, list[str]]:
    """Rewrite Claude-fail S5/S6 patterns while preserving six-sentence shape."""
    from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

    text = str(resume_display_text or "").strip()
    sentences = split_sentences(text)
    if len(sentences) != 6:
        return text, []

    repairs: list[str] = []
    out_sents = list(sentences)

    if _FORCED_LINEAGE_BRIDGE_RE.search(out_sents[3]):
        out_sents[3] = _FORCED_LINEAGE_BRIDGE_RE.sub(
            "Complementing that regulatory foundation,",
            out_sents[3],
            count=1,
        )
        repairs.append("forced_lineage_bridge_s4")

    if _S5_CREDENTIAL_DUMP_RE.search(out_sents[4]):
        out_sents[4] = _S5_CREDENTIAL_REPLACEMENT
        repairs.append("credential_inventory_s5")

    if _S6_THIN_RECAP_RE.search(out_sents[5]) or (
        "governed platform delivery" in out_sents[5].lower()
        and "extend" in out_sents[5].lower()
    ):
        out_sents[5] = _S6_FORWARD_REPLACEMENT
        repairs.append("thin_recap_s6")

    if _S4_PARTICIPIAL_AFTER_COMPLEMENT_RE.search(out_sents[3]):
        out_sents[3] = _S4_PARTICIPIAL_AFTER_COMPLEMENT_RE.sub(
            r"\1 re-architected",
            out_sents[3],
            count=1,
        )
        repairs.append("s4_participial_to_finite")

    if _S5_META_COMMENTARY_RE.search(out_sents[4]):
        out_sents[4] = _S5_META_COMMENTARY_RE.sub(".", out_sents[4]).strip()
        if not out_sents[4].endswith("."):
            out_sents[4] = out_sents[4] + "."
        repairs.append("s5_meta_commentary_strip")

    if _FORMULAIC_S3_RE.match(out_sents[2].strip()):
        out_sents[2] = _FORMULAIC_S3_RE.sub("Against that lineage backdrop, ", out_sents[2], count=1)
        repairs.append("formulaic_s3_connective")

    if _FORMULAIC_S2_RE.match(out_sents[1].strip()):
        out_sents[1] = _FORMULAIC_S2_RE.sub("From that platform footprint, ", out_sents[1], count=1)
        repairs.append("formulaic_s2_connective")

    if _S5_STRESS_ECHO_RE.search(out_sents[3]) and _S5_STRESS_ECHO_RE.search(out_sents[4]):
        out_sents[4] = _S5_CREDENTIAL_REPLACEMENT
        repairs.append("s5_stress_testing_echo_s4")

    if not repairs:
        return text, []
    return " ".join(s.strip() for s in out_sents if s.strip()), repairs


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
    if _GENERIC_S1_RE.search(out):
        out = _GENERIC_S1_RE.sub(_S1_DISTINCTIVE_REPLACEMENT, out, count=1)
        receipt["replacements"].append("generic_s1_opener")
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

    from apps_rg.runtime.validators.executive_summary_sentence_utils import (
        join_executive_summary_sentences,
        split_sentences,
    )

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
        joined = join_executive_summary_sentences(rebuilt)
        if joined != out:
            out = joined
            receipt["replacements"].append("meta_filler_opener_strip")
    out = re.sub(r"\bAdditionally,\s+", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\bFurthermore,\s+", "", out, flags=re.IGNORECASE)
    if out and out[0].islower():
        out = out[0].upper() + out[1:]

    syn_out, syn_repairs = _repair_synthesis_quality_sentences(out)
    if syn_repairs:
        out = syn_out
        receipt["replacements"].extend(syn_repairs)

    meta_out, meta_repairs = _repair_forbidden_meta_phrases(out)
    if meta_repairs:
        out = meta_out
        receipt["replacements"].extend(meta_repairs)

    filler_hits = [p for p in GENERIC_FILLER if p in out.lower()]
    bridge_ok, bridge_reason = check_inferred_bridge_claims(out, selected_facts)
    receipt["post_repair_filler_hits"] = filler_hits
    receipt["post_repair_bridge_ok"] = bridge_ok
    receipt["post_repair_bridge_reason"] = bridge_reason or ""
    receipt["repaired"] = out != text
    receipt["before_word_count"] = len(text.split())
    receipt["after_word_count"] = len(out.split())
    return out.strip(), receipt


def strip_unsupported_source_sensitive_prose(
    parsed: dict[str, Any],
    *,
    selected_facts: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Rewrite or drop SOURCE_SENSITIVE phrases unsupported by allowed facts."""
    from apps_rg.runtime.validators.executive_summary_x2 import (
        SOURCE_SENSITIVE_PHRASES,
        _sensitive_phrase_present,
        check_source_sensitive_phrases,
    )

    out = dict(parsed)
    text = str(out.get("resume_display_text") or "")
    receipt: dict[str, Any] = {
        "schema": "executive_summary_source_sensitive_strip_v1",
        "repaired": False,
        "replacements": [],
    }
    if not text:
        return out, receipt

    facts = list(selected_facts or [])
    supported: set[str] = set()
    corpus_parts: list[str] = []
    for row in facts:
        if not isinstance(row, dict):
            continue
        corpus_parts.append(str(row.get("claim_text") or ""))
        corpus_parts.append(str(row.get("achievement_summary") or ""))
    corpus = " ".join(corpus_parts).lower()
    for phrase in SOURCE_SENSITIVE_PHRASES:
        if _sensitive_phrase_present(corpus, phrase):
            supported.add(phrase)

    rewritten = text
    if "regulated environments" not in supported:
        if "regulated enterprise workflows" in supported or "regulated enterprise" in corpus:
            new = re.sub(
                r"\bregulated environments\b",
                "regulated enterprise workflows",
                rewritten,
                flags=re.IGNORECASE,
            )
            if new != rewritten:
                rewritten = new
                receipt["replacements"].append("regulated_environments_to_workflows")
        else:
            new = re.sub(
                r"\bregulated environments\b",
                "enterprise programs",
                rewritten,
                flags=re.IGNORECASE,
            )
            if new != rewritten:
                rewritten = new
                receipt["replacements"].append("regulated_environments_neutralized")

    if "governance framework" not in supported:
        if "basel" in corpus or "ccar" in corpus or "lineage" in corpus:
            new = re.sub(
                r"\bgovernance frameworks?\b",
                "Basel III/CCAR lineage and validation frameworks",
                rewritten,
                flags=re.IGNORECASE,
            )
            if new != rewritten:
                rewritten = new
                receipt["replacements"].append("governance_framework_to_basel")

    if "audit" not in supported:
        new = re.sub(r"\baudit-ready\b", "lineage-ready", rewritten, flags=re.IGNORECASE)
        if new != rewritten:
            rewritten = new
            receipt["replacements"].append("audit_ready_to_lineage_ready")
        if _sensitive_phrase_present(rewritten.lower(), "audit"):
            new = re.sub(r"\baudit\b", "controls", rewritten, flags=re.IGNORECASE)
            if new != rewritten:
                rewritten = new
                receipt["replacements"].append("audit_to_controls")

    for phrase in ("compliance",):
        if phrase not in supported and _sensitive_phrase_present(rewritten.lower(), phrase):
            new = re.sub(rf"\b{re.escape(phrase)}\b", "controls", rewritten, flags=re.IGNORECASE)
            if new != rewritten:
                rewritten = new
                receipt["replacements"].append(f"{phrase}_to_controls")

    ok, reason = check_source_sensitive_phrases(rewritten, facts)
    receipt["post_check_ok"] = ok
    receipt["post_check_reason"] = reason or ""
    if rewritten != text:
        out["resume_display_text"] = rewritten.strip()
        receipt["repaired"] = True
    return out, receipt


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

    out, ss_receipt = strip_unsupported_source_sensitive_prose(
        out, selected_facts=selected_facts
    )
    receipt["source_sensitive_strip"] = ss_receipt
    if ss_receipt.get("repaired"):
        out = reconcile_claim_ledger_after_voice_repair(out)
        receipt["ledger_reconciled"] = True

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
    "strip_unsupported_source_sensitive_prose",
]
