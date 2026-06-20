"""Tracked Markdown/docs must not document invalid Competencies CLI spellings.

Invalid guidance omits ``--`` before ``section`` (subparser-style typo).

Canonical product entry remains::

    python -m apps_rg --section competencies

Alias::

    python -m apps_rg --competencies

Allowed intentional occurrences live only under intentional deprecation tests
(e.g. ``assert "... invalid ..." not in text``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_INVALID_SECTION_NEEDLE = "python -m apps_rg section "
_SECOND_MISSPELLED_NEEDLE = "apps_rg section competencies"


def _md_paths_under_docs() -> list[Path]:
    docs = REPO_ROOT / "docs"
    if not docs.is_dir():
        return []
    out: list[Path] = []
    for path in docs.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".mdc"}:
            continue
        out.append(path)
    return sorted(out)


def _paths_under_cursor_rules() -> list[Path]:
    rules = REPO_ROOT / ".codex" / "rules"
    if not rules.is_dir():
        return []
    out: list[Path] = []
    for path in rules.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".mdc"}:
            out.append(path)
    return sorted(out)


def test_cursor_rules_avoids_missing_double_hyphen_before_section_flag() -> None:
    offenders: list[str] = []
    for path in _paths_under_cursor_rules():
        text = path.read_text(encoding="utf-8")
        if _INVALID_SECTION_NEEDLE in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert offenders == [], f"Fix CLI wording under .codex/rules (need `--section`): {offenders}"


def test_docs_markdown_avoids_missing_double_hyphen_before_section_flag() -> None:
    offenders: list[str] = []
    for path in _md_paths_under_docs():
        text = path.read_text(encoding="utf-8")
        if _INVALID_SECTION_NEEDLE in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    assert offenders == [], f"Fix CLI wording under docs (need `--section`): {offenders}"


@pytest.mark.parametrize("needle", [_INVALID_SECTION_NEEDLE, _SECOND_MISSPELLED_NEEDLE])
def test_root_readme_avoids_invalid_competencies_cli_spellings(needle: str) -> None:
    readme = REPO_ROOT / "README.md"
    if not readme.is_file():
        pytest.skip("README.md absent")
    body = readme.read_text(encoding="utf-8")
    assert needle not in body


def test_competencies_lane_head_comment_documents_canonical_double_hyphen_section_flag() -> None:
    lane = REPO_ROOT / "apps_rg" / "runtime" / "sections" / "competencies_lane.py"
    text = lane.read_text(encoding="utf-8")
    assert "--section competencies" in text
