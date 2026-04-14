"""Smoke tests for quality-tooling support files."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_quality_tooling_files_exist():
    expected = {
        ".editorconfig",
        ".gitattributes",
        ".pre-commit-config.yaml",
        "ruff.toml",
    }
    assert expected.issubset({path.name for path in ROOT.iterdir()})


def test_lint_script_exists():
    assert (ROOT / "scripts" / "run_lint.sh").exists()


def test_makefile_quality_target_mentions_lint_script():
    content = (ROOT / "Makefile").read_text()
    assert "bash scripts/run_lint.sh" in content
