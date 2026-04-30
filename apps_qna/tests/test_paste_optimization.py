"""Wave 7 — Multi-tier paste optimization tests.

Validates:
- pasted_cards excludes post_rehearsal (card 22) ALWAYS.
- pasted_cards keeps ALL always_on rules unconditionally.
- pasted_cards trims skill cards by interview.research.likely_questions.
- Falls back to full skill set when likely_questions is empty.
- Sets paste_exceeds_chatgpt_limit=True when len(pasted) > 25.
- Manifest JSON on disk carries the new fields.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from apps_qna.builder.card_pack_builder import (
    _CHATGPT_PROJECT_FILE_CAP,
    CardPackBuilder,
)
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.types.qna_types import Interview

FIXTURES = Path(__file__).parent / "fixtures" / "synthetic_mini"
INTERVIEW_YAML = FIXTURES / "interview.yaml"


def _load_interview_raw() -> dict:
    return yaml.safe_load(INTERVIEW_YAML.read_text(encoding="utf-8"))


def _build_with(
    raw: dict,
    output_dir: Path,
    multi_interviewer_mode: str = "single",
):
    extra = raw.pop("extra_context", {}) or {}
    raw["build_metadata"]["output_dir"] = str(output_dir)
    raw["build_metadata"]["built_at"] = datetime.now(timezone.utc)
    interview = Interview.model_validate(raw)
    builder = CardPackBuilder(
        config=QnaBuildConfig(force=True, multi_interviewer_mode=multi_interviewer_mode),
    )
    return builder.build(interview, output_dir, extra), interview


# ----- Always excluded: post_rehearsal -----


def test_post_rehearsal_card_always_excluded_from_paste(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    manifest, _ = _build_with(raw, tmp_path / "out")
    # Card 22 is rendered to disk
    assert "22_LEARNINGS.md" in manifest.cards
    # but NEVER in the paste set
    assert "22_LEARNINGS.md" not in manifest.pasted_cards


# ----- Always included: rules -----


_ALWAYS_ON_FILES = {
    "00_RUNTIME_ROOT.md",
    "01_ROUTING_MANIFEST.md",
    "02_LIVE_MODE.md",
    "03_INTERVIEWER_LENS.md",
    "04_COMPANY_OVERLAY.md",
    "18_ETHICS_AND_DISCLOSURE.md",
    "19_SOURCE_REGISTER.md",
    "20_GLOSSARY.md",
    "21_LIKELY_QUESTIONS.md",
}


def test_all_rule_cards_always_included_when_likely_questions_empty(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    raw.setdefault("research", {})["likely_questions"] = []
    manifest, _ = _build_with(raw, tmp_path / "out")
    pasted = set(manifest.pasted_cards)
    # All non-post_rehearsal rule cards present
    assert _ALWAYS_ON_FILES.issubset(pasted)


def test_all_rule_cards_included_when_likely_questions_declared(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    raw.setdefault("research", {})["likely_questions"] = [
        {"route_id": "architecture", "questions": ["How would you build it?"]},
    ]
    manifest, _ = _build_with(raw, tmp_path / "out")
    pasted = set(manifest.pasted_cards)
    assert _ALWAYS_ON_FILES.issubset(pasted)


# ----- Skill cards trim correctly -----


def test_likely_questions_trims_to_only_relevant_skills(tmp_path: Path) -> None:
    """One declared route → only that route's primary + specialists kept."""
    raw = _load_interview_raw()
    raw.setdefault("research", {})["likely_questions"] = [
        {
            "route_id": "architecture",
            "questions": ["How would you build a governed agentic platform?"],
        },
    ]
    manifest, _ = _build_with(raw, tmp_path / "out")
    pasted = set(manifest.pasted_cards)
    # architecture primary + its specialists (06, 08, 09) are present
    assert "05_ARCHITECTURE_CORE.md" in pasted
    assert "06_DATA_PLATFORM.md" in pasted
    assert "08_GOVERNANCE.md" in pasted
    assert "09_SEMANTIC_GROUNDING.md" in pasted
    # Cards belonging to OTHER routes' primaries that aren't specialists for
    # architecture must be excluded:
    assert "10_DS_TO_PLATFORM.md" not in pasted  # ds_to_platform primary, not arch specialist
    assert "11_GLOBAL_ENGINEERING.md" not in pasted
    assert "12_PRODUCTIZATION.md" not in pasted
    assert "13_EXECUTIVE_FIT.md" not in pasted
    assert "14_STAR_BANK.md" not in pasted
    assert "15_RCA.md" not in pasted


def test_empty_likely_questions_keeps_all_skill_cards(tmp_path: Path) -> None:
    """Conservative default — empty likely_questions = full skill set."""
    raw = _load_interview_raw()
    raw.setdefault("research", {})["likely_questions"] = []
    manifest, _ = _build_with(raw, tmp_path / "out")
    pasted = set(manifest.pasted_cards)
    # All 13 skill cards 05..17 in
    for filename in [
        "05_ARCHITECTURE_CORE.md", "06_DATA_PLATFORM.md", "07_MEASUREMENT.md",
        "08_GOVERNANCE.md", "09_SEMANTIC_GROUNDING.md", "10_DS_TO_PLATFORM.md",
        "11_GLOBAL_ENGINEERING.md", "12_PRODUCTIZATION.md", "13_EXECUTIVE_FIT.md",
        "14_STAR_BANK.md", "15_RCA.md", "16_CROSS_EXAM.md",
        "17_QUESTIONS_AND_90_DAY_PLAN.md",
    ]:
        assert filename in pasted


# ----- Card count math vs ChatGPT cap -----


def test_single_interview_default_under_cap(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    manifest, _ = _build_with(raw, tmp_path / "out")
    # Default (empty likely_questions): 22 paste-eligible cards (23 - card22)
    assert len(manifest.pasted_cards) == 22
    assert manifest.paste_exceeds_chatgpt_limit is False


def test_panel_two_interviewers_under_cap(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    raw["interviewers"].append(
        {
            "name": "John Smith",
            "title": "Director",
            "team": "Engineering",
            "technical_depth": "medium",
            "lens": "Velocity over polish.",
            "public_signals": [],
            "hot_buttons": ["Velocity"],
        }
    )
    manifest, _ = _build_with(raw, tmp_path / "out", multi_interviewer_mode="panel")
    # 2 lens cards + 21 single-mode (no card 22) = 23 paste cards
    assert len(manifest.pasted_cards) == 23
    assert manifest.paste_exceeds_chatgpt_limit is False


def test_chatgpt_cap_constant_is_25() -> None:
    assert _CHATGPT_PROJECT_FILE_CAP == 25


def test_trim_dramatically_reduces_paste_count(tmp_path: Path) -> None:
    """A 2-route declaration should drop the paste set substantially."""
    raw = _load_interview_raw()
    raw.setdefault("research", {})["likely_questions"] = [
        {"route_id": "architecture", "questions": ["?"]},
        {"route_id": "executive_fit", "questions": ["?"]},
    ]
    manifest, _ = _build_with(raw, tmp_path / "out")
    # Always-on rules (9) + arch primary (1) + arch specialists (3: 06,08,09) +
    # exec_fit primary (1) + exec_fit specialists in registry (03 + 04 — already
    # always-on; no new skills) = 14
    assert len(manifest.pasted_cards) < 22  # less than the conservative default
    assert "13_EXECUTIVE_FIT.md" in manifest.pasted_cards
    assert "05_ARCHITECTURE_CORE.md" in manifest.pasted_cards
    # Out-of-scope skills dropped
    assert "10_DS_TO_PLATFORM.md" not in manifest.pasted_cards
    assert "14_STAR_BANK.md" not in manifest.pasted_cards


# ----- Manifest JSON on disk carries the new fields -----


def test_manifest_json_has_pasted_cards_and_flag(tmp_path: Path) -> None:
    raw = _load_interview_raw()
    manifest, _ = _build_with(raw, tmp_path / "out")
    on_disk = json.loads((tmp_path / "out" / "pack_manifest.json").read_text(encoding="utf-8"))
    assert "pasted_cards" in on_disk
    assert "paste_exceeds_chatgpt_limit" in on_disk
    assert on_disk["pasted_cards"] == manifest.pasted_cards
    assert on_disk["paste_exceeds_chatgpt_limit"] is False


def test_paste_exceeds_flag_when_over_cap(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Force the cap below the actual count to exercise the warning path."""
    monkeypatch.setattr(
        "apps_qna.builder.card_pack_builder._CHATGPT_PROJECT_FILE_CAP", 5
    )
    raw = _load_interview_raw()
    with caplog.at_level("WARNING", logger="apps_qna.builder.card_pack_builder"):
        manifest, _ = _build_with(raw, tmp_path / "out")
    assert manifest.paste_exceeds_chatgpt_limit is True
    assert any("exceeding ChatGPT" in rec.message for rec in caplog.records)
