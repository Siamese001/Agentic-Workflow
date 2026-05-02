"""Tests for apps_rg.integrations.hops._ensemble_runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.integrations.hops._ensemble_runner import run_ensemble
from apps_rg.integrations.length_budget import budget_for_section


def test_run_ensemble_produces_n_candidates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    captured: list[str] = []

    def fake_gen(label: str, prompt: str) -> str:
        captured.append(label)
        return f"Delivered consulting outcomes for clients ({label})."

    result = run_ensemble(
        section_id="test_section",
        seed_text="Delivered consulting outcomes for clients.",
        prompt_variants=[("a", "p1"), ("b", "p2"), ("c", "p3")],
        budget=budget_for_section("t", target_words=8, tolerance=0.50),
        mirror_terms=["consulting", "outcomes"],
        archive_dir=tmp_path,
        gen_fn=fake_gen,
        n_candidates=3,
    )
    assert len(result.candidates) == 3
    assert captured == ["a", "b", "c"]


def test_run_ensemble_archives_candidates(tmp_path: Path) -> None:
    def fake_gen(label: str, prompt: str) -> str:
        return f"Delivered consulting outcomes for clients ({label})."

    result = run_ensemble(
        section_id="archived_section",
        seed_text="seed",
        prompt_variants=[("a", "p1")],
        budget=None,
        mirror_terms=["consulting"],
        archive_dir=tmp_path,
        gen_fn=fake_gen,
        n_candidates=2,
    )
    written = list(tmp_path.glob("archived_section_*.json"))
    assert len(written) >= 2  # candidates + scorecard
    assert any("scorecard" in p.name for p in written)


def test_run_ensemble_no_archive_dir_skips_writes(tmp_path: Path) -> None:
    def fake_gen(label: str, prompt: str) -> str:
        return "Delivered consulting outcomes."

    result = run_ensemble(
        section_id="no_archive",
        seed_text="seed",
        prompt_variants=[("a", "p1")],
        budget=None,
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=fake_gen,
        n_candidates=1,
    )
    assert result.archive_paths == []


def test_run_ensemble_picks_best_accepted(tmp_path: Path) -> None:
    def gen_fn(label: str, prompt: str) -> str:
        # Variant 'b' has stronger consulting mirror coverage.
        if label == "b":
            return "Delivered consulting outcomes consulting outcomes for clients today."
        return "leveraged synergy across world-class platforms."  # filler -> reject

    result = run_ensemble(
        section_id="best_pick",
        seed_text="seed",
        prompt_variants=[("a", "p"), ("b", "p"), ("c", "p")],
        budget=budget_for_section("t", target_words=9, tolerance=0.50),
        mirror_terms=["consulting", "outcomes"],
        archive_dir=None,
        gen_fn=gen_fn,
        n_candidates=3,
    )
    if result.accepted:
        assert result.winner.prompt_variant == "b"


def test_run_ensemble_unaccepted_when_all_fail(tmp_path: Path) -> None:
    def gen_fn(label: str, prompt: str) -> str:
        return "leveraging synergy"  # filler -> always reject

    result = run_ensemble(
        section_id="all_fail",
        seed_text="seed",
        prompt_variants=[("a", "p")],
        budget=None,
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=gen_fn,
        n_candidates=2,
    )
    assert not result.accepted
    assert result.fail_reason is not None
