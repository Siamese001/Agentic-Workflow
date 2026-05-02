"""Tests for cross-cutting meta-prompt defense in _ensemble_runner."""

from __future__ import annotations

import pytest

from apps_rg.integrations.hops._ensemble_runner import _looks_like_meta_prompt, run_ensemble
from apps_rg.integrations.hops.competencies_ensemble import is_meta_prompt
from apps_rg.integrations.length_budget import budget_for_section


# -------------------------------------------- _looks_like_meta_prompt (ensemble)


def test_lead_i_need_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt("I need the JD facets to produce competencies.")


def test_lead_please_provide_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt("Please provide the candidate's quantified outcomes.")


def test_lead_to_create_i_need_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt(
        "To create a resume headline, I need details about the candidate."
    )


def test_lead_it_looks_like_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt("It looks like you want a headline but haven't provided data.")


def test_numbered_clarification_request_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt(
        "Help me build the summary.\n1. The candidate's role\n2. The company priority"
    )


def test_short_response_ending_in_question_mark_is_meta_prompt() -> None:
    assert _looks_like_meta_prompt("What is the candidate's primary achievement?")


def test_long_narrative_is_not_meta_prompt() -> None:
    text = (
        "Delivered consulting outcomes across ten years for Fortune 500 clients, "
        "architecting agentic AI platforms and governed delivery pipelines. "
        "Scaled engineering teams from eight to twenty-eight specialists."
    )
    assert not _looks_like_meta_prompt(text)


def test_narrative_starting_with_i_is_not_meta_prompt() -> None:
    # "Innovated" starts with I but shouldn't trip the detector
    assert not _looks_like_meta_prompt(
        "Innovated a new agentic platform architecture across five Fortune 500 clients."
    )


def test_empty_or_tiny_text_is_not_meta_prompt() -> None:
    assert not _looks_like_meta_prompt("")
    assert not _looks_like_meta_prompt("ok")


# -------------------------------------------- is_meta_prompt (4C local)


def test_is_meta_prompt_matches_i_cannot() -> None:
    assert is_meta_prompt("I cannot produce competencies without JD facets.")


def test_is_meta_prompt_matches_could_you_provide() -> None:
    assert is_meta_prompt("Could you provide the target company's priorities?")


def test_is_meta_prompt_empty_returns_true() -> None:
    assert is_meta_prompt("")
    assert is_meta_prompt("   ")


def test_is_meta_prompt_legit_output_returns_false() -> None:
    assert not is_meta_prompt(
        "Agentic AI Platforms: multi-agent orchestration, governed autonomy, sandboxed execution"
    )


# -------------------------------------------- ensemble runner integration


def test_ensemble_replaces_meta_prompt_candidate_with_seed() -> None:
    """When gen_fn returns a meta-prompt, the candidate text falls back to seed_text."""
    def meta_gen(label: str, prompt: str, **kwargs) -> str:
        return "I need the JD facets to generate this section."

    result = run_ensemble(
        section_id="test_meta_defense",
        seed_text="Delivered consulting outcomes for clients.",
        prompt_variants=[("a", "p"), ("b", "p"), ("c", "p")],
        budget=budget_for_section("t", target_words=6, tolerance=0.50),
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=meta_gen,
        n_candidates=3,
    )
    # All three candidates should have fallen back to seed
    for c in result.candidates:
        assert "I need" not in c.text
        assert c.text == "Delivered consulting outcomes for clients."


def test_ensemble_keeps_mix_of_meta_and_valid_outputs() -> None:
    """Mixed generator — some meta-prompts, some valid — only meta fall back."""
    calls = {"n": 0}

    def mixed_gen(label: str, prompt: str, **kwargs) -> str:
        calls["n"] += 1
        if label == "b":
            return "I cannot produce this without more details."
        return "Delivered consulting outcomes for Fortune 500 clients today."

    result = run_ensemble(
        section_id="test_mix",
        seed_text="Seed fallback text.",
        prompt_variants=[("a", "p"), ("b", "p"), ("c", "p")],
        budget=budget_for_section("t", target_words=8, tolerance=0.50),
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=mixed_gen,
        n_candidates=3,
    )
    texts = [c.text for c in result.candidates]
    # a, c got real content; b got seed
    assert "I cannot produce" not in " ".join(texts)
    # exactly one candidate was replaced with seed
    seed_hits = sum(1 for t in texts if t == "Seed fallback text.")
    assert seed_hits == 1
