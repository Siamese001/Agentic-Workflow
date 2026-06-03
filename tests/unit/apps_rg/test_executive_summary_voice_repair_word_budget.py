"""Regression tests for exec-summary voice repair word budget and canonical arc rebuild.

Covers fix(exec-summary) W1/W3.1: judge regen must trim 141–145 word drafts instead of
rejecting them, and polish must rebuild a six-sentence arc when synthesis collapses.
"""

from __future__ import annotations

import re

import pytest

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    _rebuild_canonical_six_sentence_arc,
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MAX_WORDS


def _word_count(sentences: list[str]) -> int:
    return len(re.findall(r"\S+", " ".join(sentences)))


def _canonical_selected_facts() -> list[dict[str, str]]:
    return [
        {"fact_id": "fact_governance_003", "claim_text": "Basel lineage"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA actuarial"},
        {"fact_id": "fact_consulting_001", "claim_text": "Consulting delivery"},
        {"fact_id": "fact_exec_002", "claim_text": "Team scale"},
    ]


def test_trim_paragraph_word_budget_noop_when_under_cap() -> None:
    sents = ["Short one.", "Short two.", "Short three."]
    assert _trim_paragraph_word_budget(sents, max_words=EXEC_SUMMARY_MAX_WORDS) == sents


def test_trim_paragraph_word_budget_fsa_established_through_strategy() -> None:
    """Strategy 1: drop redundant 'established through' on FSA sentence to meet 140-word X2 cap."""
    s1 = (
        "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, "
        "and commercialization into one IT strategy and innovation agenda for decentralized "
        "regulated enterprises driving digital innovation programs."
    )
    s2 = (
        "Designed and operationalized a governed agentic AI platform with deterministic routing, "
        "multi-agent orchestration, sandboxed tool execution, and validation-ready delivery "
        "across enterprise architecture and cloud-native platform engineering programs."
    )
    s3 = (
        "Platform commercialization generated twenty-two million dollars in IP-led revenue and "
        "expanded gross margins while scaling delivery across productization and accelerator "
        "adoption for regulated financial services and insurance technology portfolios."
    )
    s4 = (
        "Applied across enterprise programs, Basel III and CCAR data lineage and automated "
        "validation frameworks cut regulatory reporting errors by forty percent while improving "
        "audit readiness across decentralized operating units and federated data domains."
    )
    s5 = (
        "That regulatory foundation is grounded in quantitative rigor established through "
        "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
        "informing data governance and AI strategy at scale across enterprise risk programs."
    )
    s6 = (
        "Innovation incubation and architecture standards will federate governed platform "
        "capabilities across autonomous business units without weakening lineage discipline "
        "or deterministic controls for agentic AI delivery and runtime governance."
    )
    before = [s1, s2, s3, s4, s5, s6]
    assert _word_count(before) > EXEC_SUMMARY_MAX_WORDS

    trimmed = _trim_paragraph_word_budget(before, max_words=EXEC_SUMMARY_MAX_WORDS)
    assert _word_count(trimmed) < _word_count(before)
    fsa_sentence = next(s for s in trimmed if "fsa-chartered" in s.lower())
    assert "established through" not in fsa_sentence.lower()
    assert "through fsa-chartered" in fsa_sentence.lower()


def test_rebuild_canonical_six_sentence_arc_from_degenerate_output() -> None:
    thesis = "Enterprise technology leader who unifies governed AI platforms into one agenda."
    collapsed = [thesis, "Only one fact sentence with a metric and platform delivery."]
    rebuilt = _rebuild_canonical_six_sentence_arc(
        collapsed,
        selected_facts=_canonical_selected_facts(),
    )
    assert len(rebuilt) == 6
    assert rebuilt[0] == thesis
    assert "basel iii" in rebuilt[1].lower()
    assert "dependency graph" in rebuilt[2].lower()
    assert "fsa-chartered" in rebuilt[3].lower()


def test_polish_rebuilds_arc_when_fewer_than_six_sentences() -> None:
    """Polish must not silently skip when synthesis collapses below six sentences."""
    pytest.importorskip("tqdm")

    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who unifies governed AI platforms. "
            "Degenerate two-sentence collapse."
        ),
        "claim_ledger": [],
    }
    polished, receipt = polish_executive_summary_judge_alignment(
        parsed,
        selected_facts=_canonical_selected_facts(),
    )
    text = str(polished.get("resume_display_text") or "")
    assert receipt.get("applied") is True
    assert "canonical_arc_rebuild" in (receipt.get("actions") or [])
    assert text.count(".") >= 5
