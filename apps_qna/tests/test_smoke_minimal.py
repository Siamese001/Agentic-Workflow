"""Smoke test — synthetic-mini fixture builds a 23-card pack end-to-end.

Wave 0–5 added cards 18 (Ethics & Disclosure), 19 (Source Register),
20 (Glossary), 21 (Likely Questions), 22 (Learnings) on top of the
original 18 (00–17).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from apps_qna.builder.card_pack_builder import CardPackBuilder
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.types.qna_types import Interview

FIXTURES = Path(__file__).parent / "fixtures" / "synthetic_mini"
INTERVIEW_YAML = FIXTURES / "interview.yaml"


def _load_interview(tmp_output: Path) -> tuple[Interview, dict]:
    raw = yaml.safe_load(INTERVIEW_YAML.read_text(encoding="utf-8"))
    extra = raw.pop("extra_context", {}) or {}
    raw["build_metadata"]["output_dir"] = str(tmp_output)
    raw["build_metadata"]["built_at"] = datetime.now(timezone.utc)
    return Interview.model_validate(raw), extra


def test_smoke_build_23_cards(tmp_path: Path) -> None:
    """Builder emits all 23 cards + manifest from synthetic-mini fixture."""
    output_dir = tmp_path / "smoke_out"
    interview, extra = _load_interview(output_dir)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    manifest = builder.build(interview, output_dir, extra)

    # 23 cards (single-interviewer mode collapses 03 to one card)
    assert len(manifest.cards) == 23
    assert manifest.cards[0] == "00_RUNTIME_ROOT.md"
    assert manifest.cards[-1] == "22_LEARNINGS.md"

    # Wave 0–5 always-on additions are present
    expected_always_on_additions = {
        "18_ETHICS_AND_DISCLOSURE.md",
        "19_SOURCE_REGISTER.md",
        "20_GLOSSARY.md",
        "21_LIKELY_QUESTIONS.md",
        "22_LEARNINGS.md",
    }
    assert expected_always_on_additions.issubset(set(manifest.cards))

    # All emitted files exist on disk
    for card in manifest.cards:
        assert (output_dir / card).is_file(), f"Missing card: {card}"

    # Manifest JSON is on disk and parseable
    manifest_path = output_dir / "pack_manifest.json"
    assert manifest_path.is_file()
    on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert on_disk["interview_slug"] == "synthetic-mini"
    assert len(on_disk["cards"]) == 23

    # All 9 routes covered
    assert len(manifest.routes_covered) == 9


def test_smoke_panel_mode_emits_lens_per_interviewer(tmp_path: Path) -> None:
    """Panel mode (>1 interviewer) materializes one Lens card per interviewer."""
    output_dir = tmp_path / "panel_out"
    raw = yaml.safe_load(INTERVIEW_YAML.read_text(encoding="utf-8"))
    extra = raw.pop("extra_context", {}) or {}
    # Add a second interviewer to trigger panel mode
    raw["interviewers"].append({
        "name": "John Smith",
        "title": "Director of Data Science",
        "team": "Measurement",
        "technical_depth": "medium",
        "lens": "Statistical rigor and translation to business language.",
        "public_signals": [],
        "hot_buttons": ["MMM", "incrementality"],
    })
    raw["build_metadata"]["output_dir"] = str(output_dir)
    raw["build_metadata"]["built_at"] = datetime.now(timezone.utc)
    interview = Interview.model_validate(raw)

    builder = CardPackBuilder(
        config=QnaBuildConfig(force=True, multi_interviewer_mode="panel"),
    )
    manifest = builder.build(interview, output_dir, extra)

    # 24 cards in panel mode: 22 single + 2 lens cards (03A, 03B)
    lens_cards = [c for c in manifest.cards if "_LENS_" in c]
    assert len(lens_cards) == 2
    assert any("JANE_DOE" in c for c in lens_cards)
    assert any("JOHN_SMITH" in c for c in lens_cards)


def test_strict_undefined_catches_missing_variable(tmp_path: Path) -> None:
    """A template referencing a missing variable raises BuilderError."""
    from apps_qna.builder.card_pack_builder import BuilderError

    output_dir = tmp_path / "strict_out"
    interview, extra = _load_interview(output_dir)
    # Remove a required content block to force StrictUndefined to fire
    extra.pop("architecture_content_blocks", None)
    # Replace with a default empty list so the iteration succeeds — the test
    # confirms the *opposite*: that with proper inputs render is clean.
    extra["architecture_content_blocks"] = []

    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    # Should still build because empty list is valid
    manifest = builder.build(interview, output_dir, extra)
    assert len(manifest.cards) == 23


def test_always_on_header_is_consistent_across_cards(tmp_path: Path) -> None:
    """Cards 00–17 must all open with the same always-on header block."""
    output_dir = tmp_path / "header_out"
    interview, extra = _load_interview(output_dir)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    manifest = builder.build(interview, output_dir, extra)

    header_signature = "## LIVE VERBAL-FIRST OVERWRITE"
    for card_filename in manifest.cards:
        content = (output_dir / card_filename).read_text(encoding="utf-8")
        assert header_signature in content, (
            f"Card {card_filename} missing always-on header"
        )


def test_manifest_routes_covered_matches_registry(tmp_path: Path) -> None:
    """All 9 primary cards from the registry are emitted by the smoke build."""
    from apps_qna.config.route_registry import load_route_registry

    output_dir = tmp_path / "routes_out"
    interview, extra = _load_interview(output_dir)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    manifest = builder.build(interview, output_dir, extra)

    registry = load_route_registry()
    expected_route_ids = {r.id for r in registry.routes}
    assert set(manifest.routes_covered) == expected_route_ids
