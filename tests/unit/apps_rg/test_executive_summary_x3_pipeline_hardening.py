"""Regression tests for exec-summary X3_ALLOW pipeline hardening (2026-05-27).

Covers:
- canonical six-sentence arc rebuild when polish sees <6 sentences (voice repair skip fix)
- deterministic paragraph word trim before judge-regen pre-accept reject (W3.1)
"""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _CANONICAL_DISPLAY_SENTENCES,
    _CANONICAL_FACT_SLOT,
    _rebuild_canonical_six_sentence_arc,
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_WORDS,
    split_sentences,
)


def _canonical_fact_rows() -> list[dict[str, str]]:
    return [
        {"fact_id": fid, "claim_text": f"claim for {fid}"}
        for fid in sorted(_CANONICAL_FACT_SLOT, key=lambda f: _CANONICAL_FACT_SLOT[f])
    ]


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _six_sentence_canonical_display(*, extra_tail_words: int = 0) -> str:
    s1 = (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, "
        "and digital innovation programs into one IT strategy agenda for regulated enterprises."
    )
    ordered = sorted(_CANONICAL_FACT_SLOT, key=lambda f: _CANONICAL_FACT_SLOT[f])
    parts = [s1, *[_CANONICAL_DISPLAY_SENTENCES[fid] for fid in ordered]]
    text = " ".join(parts)
    if extra_tail_words > 0:
        text = f"{text} {' '.join(['supplemental'] * extra_tail_words)}"
    return text


def _six_sentence_over_cap_display() -> str:
    """Canonical arc is ~136 words; regen models often land at 141–145."""
    text = _six_sentence_canonical_display(extra_tail_words=8)
    assert _word_count(text) > EXEC_SUMMARY_MAX_WORDS
    return text


def test_rebuild_canonical_six_sentence_arc_restores_missing_slots() -> None:
    facts = _canonical_fact_rows()
    degenerate = [
        "Enterprise technology leader who unifies governed AI platforms.",
        "Through that operating model, Basel III cut errors.",
        "Graph intelligence enables analysis.",
        "FSA work informs strategy.",
        "Consulting delivery across domains.",
    ]
    rebuilt = _rebuild_canonical_six_sentence_arc(degenerate, selected_facts=facts)
    assert len(rebuilt) == 6
    assert rebuilt[0].startswith("Enterprise technology leader")
    assert "Basel III" in rebuilt[1]
    assert "dependency graph intelligence" in rebuilt[2].lower()
    assert "fsa-chartered" in rebuilt[3].lower()


def test_polish_rebuilds_canonical_arc_when_fewer_than_six_sentences() -> None:
    facts = _canonical_fact_rows()
    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who unifies governed AI platforms. "
            "Through that operating model, Basel III cut errors. "
            "Graph intelligence enables analysis. "
            "FSA work informs strategy. "
            "Consulting delivery across domains."
        ),
        "claim_ledger": [],
    }
    polished, receipt = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    assert receipt.get("applied") is True
    assert "canonical_arc_rebuild" in (receipt.get("actions") or [])
    sents = split_sentences(str(polished.get("resume_display_text") or ""))
    assert len(sents) == 6
    assert "fsa-chartered" in str(polished.get("resume_display_text") or "").lower()


def test_trim_paragraph_word_budget_removes_established_through() -> None:
    sents = split_sentences(_six_sentence_over_cap_display())
    before_wc = _word_count(" ".join(sents))
    assert before_wc > EXEC_SUMMARY_MAX_WORDS
    trimmed = _trim_paragraph_word_budget(sents, max_words=EXEC_SUMMARY_MAX_WORDS)
    joined = " ".join(trimmed)
    after_wc = _word_count(joined)
    assert after_wc <= EXEC_SUMMARY_MAX_WORDS
    assert "established through" not in joined.lower()
    assert "fsa-chartered actuarial work" in joined.lower()


def test_judge_regen_pre_accept_trim_gate_accepts_trimmed_candidate() -> None:
    """W3.1 gate: over-cap regen is accepted when deterministic trim fits EXEC_SUMMARY_MAX_WORDS."""
    regen_display = _six_sentence_over_cap_display()
    regen_wc = _word_count(regen_display)
    assert regen_wc > EXEC_SUMMARY_MAX_WORDS

    trimmed_sents = _trim_paragraph_word_budget(
        split_sentences(regen_display),
        max_words=EXEC_SUMMARY_MAX_WORDS,
    )
    trimmed_display = " ".join(s.strip() for s in trimmed_sents if s.strip())
    trimmed_wc = _word_count(trimmed_display)

    draft_parse_ok = trimmed_wc <= EXEC_SUMMARY_MAX_WORDS and trimmed_display != regen_display
    assert draft_parse_ok is True
    assert "established through" not in trimmed_display.lower()
