"""Tests for Waves 0–5 enhancements (RAG/Skills alignment).

Covers:
- New always-on cards (18-22) emit and pass all linters.
- Card-meta block (Rules vs Skills frontmatter) appears in every card.
- LINT-7 token-budget validator.
- self-eval CLI subcommand prints a delta report.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import yaml

from apps_qna.builder.card_pack_builder import CardPackBuilder
from apps_qna.config.build_config import QnaBuildConfig
from apps_qna.config.route_registry import load_route_registry
from apps_qna.router.pack_loader import load_pack
from apps_qna.scripts.run_qna import main as cli_main
from apps_qna.types.qna_types import Interview
from apps_qna.validators import run_all_validators
from apps_qna.validators.token_budget import (
    _DEFAULT_WORD_CAP,
    _count_words,
    check_token_budget,
)

FIXTURES = Path(__file__).parent / "fixtures" / "synthetic_mini"
INTERVIEW_YAML = FIXTURES / "interview.yaml"


def _build_smoke_pack(tmp_path: Path, sub: str = "pack") -> Path:
    output_dir = tmp_path / sub
    raw = yaml.safe_load(INTERVIEW_YAML.read_text(encoding="utf-8"))
    extra = raw.pop("extra_context", {}) or {}
    raw["build_metadata"]["output_dir"] = str(output_dir)
    raw["build_metadata"]["built_at"] = datetime.now(timezone.utc)
    interview = Interview.model_validate(raw)
    builder = CardPackBuilder(config=QnaBuildConfig(force=True))
    builder.build(interview, output_dir, extra)
    return output_dir


# ----- New always-on cards -----


def test_wave2_source_register_card_emitted(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    assert (pack_dir / "19_SOURCE_REGISTER.md").is_file()


def test_wave3_glossary_and_likely_questions_emitted(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    assert (pack_dir / "20_GLOSSARY.md").is_file()
    assert (pack_dir / "21_LIKELY_QUESTIONS.md").is_file()


def test_wave5_learnings_card_emitted(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    card = pack_dir / "22_LEARNINGS.md"
    assert card.is_file()
    content = card.read_text(encoding="utf-8")
    # Pathology codes must be present
    assert "P-DRIFT" in content
    assert "P-CITE-MISS" in content


# ----- Card-meta block (Wave 1) -----


def test_card_meta_frontmatter_in_every_card(tmp_path: Path) -> None:
    """Every card must contain a card-meta HTML comment block."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    for card in pack.cards:
        assert "<!-- card-meta" in card.content, (
            f"Card {card.filename} missing card-meta block"
        )
        assert "card_id:" in card.content
        assert "card_type:" in card.content
        assert "priority:" in card.content


def test_card_meta_distinguishes_rule_and_skill(tmp_path: Path) -> None:
    """Always-on cards are rules; route specialists are skills."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)

    rule_card = pack.card_by_filename("19_SOURCE_REGISTER.md")
    assert rule_card is not None
    assert "card_type: rule" in rule_card.content

    skill_card = pack.card_by_filename("05_ARCHITECTURE_CORE.md")
    assert skill_card is not None
    assert "card_type: skill" in skill_card.content


# ----- LINT-7 token budget (Wave 4) -----


def test_lint7_positive(tmp_path: Path) -> None:
    """Smoke pack stays within the default per-card word cap."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_token_budget(pack, load_route_registry())
    assert result.ok, f"Unexpected errors: {result.errors}"


def test_lint7_negative_with_low_cap(tmp_path: Path) -> None:
    """A pathologically low cap fires LINT-7 on every card."""
    pack_dir = _build_smoke_pack(tmp_path)
    pack = load_pack(pack_dir)
    result = check_token_budget(pack, load_route_registry(), word_cap=10)
    assert not result.ok
    assert all(e.code == "LINT-7" for e in result.errors)


def test_lint7_default_cap_constant() -> None:
    """The default cap is 1500 words (sanity guard, not a stylistic constraint)."""
    assert _DEFAULT_WORD_CAP == 1500


def test_lint7_in_runner(tmp_path: Path) -> None:
    """run_all_validators wires LINT-7 (smoke pack should still pass all)."""
    pack_dir = _build_smoke_pack(tmp_path)
    result = run_all_validators(pack_dir)
    assert result.ok, f"Unexpected errors: {result.errors}"


def test_count_words_basic() -> None:
    assert _count_words("hello world") == 2
    # \w+ treats foo_bar as one word; markdown punctuation is stripped.
    assert _count_words("- bullet **bold** *italic* foo_bar") == 4
    assert _count_words("") == 0


# ----- Wave 5: self-eval CLI -----


def test_self_eval_no_previous_prints_summary(tmp_path: Path) -> None:
    pack_dir = _build_smoke_pack(tmp_path)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(["self-eval", "--pack", str(pack_dir)])
    assert rc == 0
    out = buf.getvalue()
    assert "Self-eval" in out
    assert "Cards: **22**" in out
    assert "Routes covered: **9**" in out


def test_self_eval_with_previous_prints_diff(tmp_path: Path) -> None:
    pack_a = _build_smoke_pack(tmp_path, sub="pack_a")
    pack_b = _build_smoke_pack(tmp_path, sub="pack_b")
    # Mutate pack_b: drop one card to create a real removed-set
    (pack_b / "06_DATA_PLATFORM.md").unlink()
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(
            [
                "self-eval",
                "--pack",
                str(pack_b),
                "--previous",
                str(pack_a),
            ]
        )
    assert rc == 0
    out = buf.getvalue()
    assert "Diff vs" in out
    assert "Removed: **1**" in out
    assert "06_DATA_PLATFORM.md" in out


def test_self_eval_pack_missing_returns_2(tmp_path: Path) -> None:
    rc = cli_main(["self-eval", "--pack", str(tmp_path / "nope")])
    assert rc == 2
