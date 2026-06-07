"""Assert apps_eval/fixtures/{dev,holdout}/ scaffold exists.

Plan: `docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-residual-a2d9c7.md` W2.P2.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "apps_eval" / "fixtures"


def test_fixtures_root_exists():
    assert FIXTURES.is_dir(), f"missing {FIXTURES}"


def test_dev_subdir_exists():
    assert (FIXTURES / "dev").is_dir()


def test_holdout_subdir_exists():
    assert (FIXTURES / "holdout").is_dir()


def test_readme_documents_holdout_isolation():
    readme = FIXTURES / "README.md"
    assert readme.is_file()
    text = readme.read_text(encoding="utf-8")
    assert "holdout" in text.lower()
    assert "release-gate" in text.lower() or "RELEASE-GATE" in text


def test_dev_has_package_marker():
    assert (FIXTURES / "dev" / "__init__.py").is_file()


def test_holdout_has_package_marker():
    assert (FIXTURES / "holdout" / "__init__.py").is_file()
