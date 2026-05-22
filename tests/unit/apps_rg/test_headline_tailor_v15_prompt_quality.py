"""Prompt-only quality checks for headline_tailor_v1 (no runtime proof claims)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from apps_rg.runtime.validators.headline_x2 import (
    _EXTRA_HYPE_MARKERS_RE,
    _KEYWORD_STUFF_RE,
    _METRIC_RE,
    headline_word_count,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_PATH = REPO_ROOT / "apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml"

_BANNED_VOICE_FRAGMENTS = (
    "visionary",
    "thought leader",
    "digital transformation",
    "innovation leadership",
    "strategic leader",
    "ai evangelist",
    "technology evangelist",
    "results-driven",
    "proven leader",
    "world-class",
    "cutting-edge",
    "leveraging",
)


def _extract_many_shot_headlines(txt: str) -> list[str]:
    start = txt.index("<many_shot_examples>")
    end = txt.index("</many_shot_examples>")
    block = txt[start:end]
    return [ln.strip() for ln in block.splitlines() if ln.strip().startswith("SVP Engineering |")]


def test_template_version_is_1_5() -> None:
    raw = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert raw.get("version") == "1.5"


def test_many_shot_examples_word_counts_and_banned_patterns() -> None:
    txt = TEMPLATE_PATH.read_text(encoding="utf-8")
    examples = _extract_many_shot_headlines(txt)
    assert len(examples) >= 6
    for hl in examples:
        assert hl.count(" | ") == 3
        assert hl.startswith("SVP Engineering | ")
        wc = headline_word_count(hl)
        assert 10 <= wc <= 13, (hl, wc)
        assert _METRIC_RE.search(hl) is None
        assert _KEYWORD_STUFF_RE.search(hl) is None
        assert _EXTRA_HYPE_MARKERS_RE.search(hl) is None
        assert not re.search(r"\d", hl), hl
        low = hl.lower()
        for frag in _BANNED_VOICE_FRAGMENTS:
            assert frag not in low, (frag, hl)


def test_many_shot_examples_material_theme_variation() -> None:
    txt = TEMPLATE_PATH.read_text(encoding="utf-8")
    examples = _extract_many_shot_headlines(txt)
    triples: list[tuple[str, str, str]] = []
    for hl in examples:
        parts = [p.strip() for p in hl.split(" | ")]
        assert len(parts) == 4
        assert parts[0] == "SVP Engineering"
        triples.append((parts[1].lower(), parts[2].lower(), parts[3].lower()))
    assert len(set(triples)) >= 4


def test_contrastive_section_preserves_mechanical_copy_warning() -> None:
    txt = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "<contrastive_examples>" in txt
    assert "Agentic AI Platforms | Distributed AI Infrastructure" in txt
    assert "flat ledger" in txt.lower() or "flat bul_" in txt.lower()


@pytest.fixture(scope="module")
def template_yaml() -> dict:
    return yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))


def test_slot_bodies_contain_required_sections(template_yaml: dict) -> None:
    slots = template_yaml["slot_bodies"]
    for key in ("S0", "D0", "I0", "E0", "R0"):
        assert key in slots
        body = slots[key]
        assert isinstance(body, str)
        assert len(body.strip()) > 50


def test_hash_fields_include_critical_slots(template_yaml: dict) -> None:
    hf = template_yaml.get("hash_fields") or []
    assert "slot_bodies.S0" in hf
    assert "slot_bodies.I0" in hf
    assert "slot_bodies.R0" in hf
