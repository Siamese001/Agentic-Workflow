"""Tests for the ensemble temperature ladder (D7-bis, 2026-05-01)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.integrations.hops._ensemble_runner import (
    _DEFAULT_TEMP_LADDER,
    _resolve_temp_ladder,
    _stretch,
    run_ensemble,
)
from apps_rg.integrations.length_budget import budget_for_section


def test_default_ladder_is_three_rungs() -> None:
    assert _DEFAULT_TEMP_LADDER == (0.55, 0.75, 0.95)
    assert _DEFAULT_TEMP_LADDER[0] < _DEFAULT_TEMP_LADDER[1] < _DEFAULT_TEMP_LADDER[2]


def test_resolve_returns_default_ladder_for_n3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NARRATIVE_TEMP_LADDER", raising=False)
    ladder = _resolve_temp_ladder(3)
    assert ladder == (0.55, 0.75, 0.95)


def test_resolve_single_candidate_uses_balanced_middle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NARRATIVE_TEMP_LADDER", raising=False)
    ladder = _resolve_temp_ladder(1)
    # Median of (0.55, 0.75, 0.95) is 0.75 — NOT the conservative 0.55.
    assert ladder == (0.75,)


def test_resolve_two_candidates_keeps_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NARRATIVE_TEMP_LADDER", raising=False)
    ladder = _resolve_temp_ladder(2)
    # Should pick endpoints to maintain creative spread.
    assert ladder[0] == 0.55
    assert ladder[1] == 0.95


def test_resolve_cycles_when_n_exceeds_ladder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NARRATIVE_TEMP_LADDER", raising=False)
    ladder = _resolve_temp_ladder(5)
    assert len(ladder) == 5
    # Index 3 cycles back to ladder[0]
    assert ladder[3] == 0.55


def test_env_override_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NARRATIVE_TEMP_LADDER", "0.4,0.7,0.9")
    ladder = _resolve_temp_ladder(3)
    assert ladder == (0.4, 0.7, 0.9)


def test_env_override_invalid_falls_back_to_default(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("NARRATIVE_TEMP_LADDER", "junk,values,here")
    with caplog.at_level("WARNING"):
        ladder = _resolve_temp_ladder(3)
    assert ladder == _DEFAULT_TEMP_LADDER
    assert any("invalid NARRATIVE_TEMP_LADDER" in m for m in caplog.messages)


def test_env_override_out_of_range_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # 3.5 exceeds the [0, 2] safety band -> reject and fall back.
    monkeypatch.setenv("NARRATIVE_TEMP_LADDER", "0.5,1.0,3.5")
    ladder = _resolve_temp_ladder(3)
    assert ladder == _DEFAULT_TEMP_LADDER


def test_stretch_evenly_samples_for_smaller_n() -> None:
    rungs = (0.0, 0.25, 0.5, 0.75, 1.0)
    out = _stretch(rungs, 3)
    # Should be (0.0, 0.5, 1.0) — endpoints + middle
    assert out == (0.0, 0.5, 1.0)


# -------------- end-to-end: temperature flows into ensemble candidates


def test_run_ensemble_stamps_temperature_per_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("NARRATIVE_TEMP_LADDER", raising=False)
    received: list[float] = []

    def gen_fn(label: str, prompt: str, *, temperature: float | None = None) -> str:
        received.append(float(temperature) if temperature is not None else -1.0)
        return f"Delivered consulting outcomes for clients ({label})."

    result = run_ensemble(
        section_id="temp_test",
        seed_text="seed",
        prompt_variants=[("a", "p"), ("b", "p"), ("c", "p")],
        budget=budget_for_section("t", target_words=8, tolerance=0.50),
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=gen_fn,
        n_candidates=3,
    )
    assert received == [0.55, 0.75, 0.95]
    temps_on_candidates = [c.temperature for c in result.candidates]
    assert temps_on_candidates == [0.55, 0.75, 0.95]


def test_run_ensemble_falls_back_when_gen_fn_rejects_temp_kwarg(tmp_path: Path) -> None:
    """Test/stub generators that don't accept temperature= must still work."""

    def gen_fn(label: str, prompt: str) -> str:  # no temperature kwarg
        return f"Delivered consulting outcomes for clients ({label})."

    result = run_ensemble(
        section_id="legacy_gen",
        seed_text="seed",
        prompt_variants=[("a", "p"), ("b", "p"), ("c", "p")],
        budget=None,
        mirror_terms=["consulting"],
        archive_dir=None,
        gen_fn=gen_fn,
        n_candidates=3,
    )
    # Even though gen_fn ignored temp, the ladder is still recorded on the candidates.
    temps = [c.temperature for c in result.candidates]
    assert temps == [0.55, 0.75, 0.95]
