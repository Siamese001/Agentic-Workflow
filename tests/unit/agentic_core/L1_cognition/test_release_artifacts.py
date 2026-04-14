"""Smoke tests for release and CI support files."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_support_files_exist():
    expected = {
        ".gitignore",
        "MANIFEST.in",
        "Makefile",
        "README.md",
        "pyproject.toml",
    }
    assert expected.issubset({path.name for path in ROOT.iterdir()})


def test_ci_workflow_exists():
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_release_scripts_exist():
    assert (ROOT / "scripts" / "run_quality.sh").exists()
    assert (ROOT / "scripts" / "package_bundle.sh").exists()
