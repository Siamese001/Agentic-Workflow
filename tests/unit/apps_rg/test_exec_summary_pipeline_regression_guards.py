"""Regression guards for exec-summary pipeline fixes (canonical arc rebuild, word trim).

Covers production fixes from graph-only repair collapsing to <6 sentences and judge
regen outputs rejected for 141–145 words before deterministic trim (31d650f700).
Non-runtime: no live LLM.
"""

from __future__ import annotations

import re

from apps_rg.runtime.sections.cross_section_signal_guards import base_archive_ngram_overlap
from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_WORDS,
    split_sentences,
)

_CANONICAL_FACT_IDS = (
    "fact_governance_003",
    "fact_engineering_platform_002",
    "fact_quant_hpc_003",
    "fact_consulting_001",
    "fact_exec_002",
)


def _canonical_selected_facts() -> list[dict[str, str]]:
    return [{"fact_id": fid, "claim_text": f"claim for {fid}"} for fid in _CANONICAL_FACT_IDS]


def test_polish_rebuilds_canonical_arc_when_graph_repair_collapses_to_five_sentences() -> None:
    """Regression: len!=6 used to silently skip polish; now rebuilds canonical arc."""
    collapsed_five = (
        "Enterprise technology leader who unifies governed AI platforms into one IT strategy. "
        "Through that operating model, Basel III and CCAR data lineage cut errors by 40%. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis. "
        "That regulatory foundation is grounded in FSA-chartered actuarial work in capital modeling. "
        "Directed large-scale regulatory IT transformations for major financial institutions."
    )
    parsed = {"resume_display_text": collapsed_five, "claim_ledger": []}
    polished, receipt = polish_executive_summary_judge_alignment(
        parsed,
        selected_facts=_canonical_selected_facts(),
    )
    assert receipt.get("applied") is True
    assert "canonical_arc_rebuild" in (receipt.get("actions") or [])
    sentences = split_sentences(str(polished.get("resume_display_text") or ""))
    assert len(sentences) == 6
    assert "basel iii" in str(polished.get("resume_display_text") or "").lower()
    assert "8 to 28" in str(polished.get("resume_display_text") or "").lower()


def test_trim_paragraph_word_budget_fsa_established_through_brings_under_cap() -> None:
    """Regression: judge regen 141–145w outputs trim via FSA 'established through' removal."""
    long_fsa = (
        "That regulatory foundation is grounded in quantitative rigor established through "
        "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
        "informing data governance and AI strategy at scale across enterprise programs."
    )
    filler = " ".join(
        [
            "Enterprise technology leader who unifies governed AI platforms into one IT strategy "
            "and innovation agenda for decentralized regulated enterprises with digital innovation programs.",
            "Through that operating model, Basel III and CCAR data lineage and cataloging, and "
            "automated validation frameworks cut regulatory reporting errors by 40% consistently across programs.",
            "Software dependency graph intelligence enables accelerated legacy-system analysis, "
            "exposes architecture dependency chains, and improves transformation visibility broadly across complexity.",
            long_fsa,
            "Against that delivery foundation, directed large-scale regulatory IT transformations "
            "and legacy-modernization programs for major financial institutions across risk, "
            "compliance, data, cloud, and architecture domains with measurable enterprise outcomes.",
            "Innovation incubation and architecture standards will federate governed platform "
            "capabilities across autonomous business units without weakening lineage discipline enterprise-wide.",
        ]
    )
    sentences = split_sentences(filler)
    assert len(sentences) == 6
    before_wc = len(re.findall(r"\S+", " ".join(sentences)))
    assert before_wc > EXEC_SUMMARY_MAX_WORDS

    trimmed = _trim_paragraph_word_budget(sentences, max_words=EXEC_SUMMARY_MAX_WORDS)
    after_wc = len(re.findall(r"\S+", " ".join(trimmed)))
    assert after_wc <= EXEC_SUMMARY_MAX_WORDS
    joined = " ".join(trimmed).lower()
    assert "established through" not in joined
    assert "fsa-chartered actuarial work" in joined


def test_base_archive_ngram_overlap_detects_hydration_from_reference() -> None:
    output = "Delivered platform modernization with deterministic routing and replayable traces."
    reference = (
        "Delivered platform modernization with deterministic routing and replayable traces "
        "across the enterprise data estate."
    )
    overlap = base_archive_ngram_overlap(output, [reference], n=4)
    assert overlap > 0.25

    distinct = "Owned agentic AI platform delivery with governed multi-agent orchestration."
    assert base_archive_ngram_overlap(distinct, [reference], n=4) < overlap
