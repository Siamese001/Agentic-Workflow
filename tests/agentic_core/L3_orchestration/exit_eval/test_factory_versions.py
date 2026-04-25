"""Tests for version-aware rubric loading in exit_eval factory.

Covers the migration of X1D/X1F to v2 rubrics per
.windsurf/plans/runtime-gate-coverage-hardening-7e3f1a.md follow-up.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.factory import (
    _FALLBACK_VERSION,
    _resolve_rubric_version,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
RUBRIC_DIR = REPO_ROOT / "config" / "exit_eval_rubrics"


def test_versions_yaml_exists_and_parses() -> None:
    """The SSOT _versions.yaml must exist and parse."""
    import yaml

    path = RUBRIC_DIR / "_versions.yaml"
    assert path.exists(), f"missing version SSOT: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "versions" in data
    assert isinstance(data["versions"], dict)


def test_x1d_resolves_to_v2_by_default() -> None:
    """X1D defaulted to v2 on 2026-04-25 (G5 hard groundedness veto)."""
    assert _resolve_rubric_version("X1D", RUBRIC_DIR) == "v2"


def test_x1f_resolves_to_v2_by_default() -> None:
    """X1F defaulted to v2 on 2026-04-25 (G7 indirect injection)."""
    assert _resolve_rubric_version("X1F", RUBRIC_DIR) == "v2"


def test_x1a_x1b_remain_v1() -> None:
    """Other gates remain on v1 — only X1D/X1F migrated."""
    assert _resolve_rubric_version("X1A", RUBRIC_DIR) == "v1"
    assert _resolve_rubric_version("X1B", RUBRIC_DIR) == "v1"


def test_unknown_gate_falls_back_to_v1() -> None:
    """A gate not declared in the SSOT falls back to v1."""
    assert _resolve_rubric_version("XZZ", RUBRIC_DIR) == _FALLBACK_VERSION


def test_env_var_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    """EXIT_EVAL_RUBRIC_VERSION_X1D=v1 wins over the SSOT default."""
    monkeypatch.setenv("EXIT_EVAL_RUBRIC_VERSION_X1D", "v1")
    assert _resolve_rubric_version("X1D", RUBRIC_DIR) == "v1"


def test_missing_versions_yaml_falls_back(tmp_path: Path) -> None:
    """If _versions.yaml is absent, factory falls back to v1."""
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_v2_files_exist() -> None:
    """The v2 rubric files referenced by _versions.yaml must be on disk."""
    assert (RUBRIC_DIR / "x1d_v2.yaml").exists()
    assert (RUBRIC_DIR / "x1f_v2.yaml").exists()


def test_v1_files_retained_for_backcompat() -> None:
    """v1 files retained so explicit-path callers (and rollback) still work."""
    assert (RUBRIC_DIR / "x1d_v1.yaml").exists()
    assert (RUBRIC_DIR / "x1f_v1.yaml").exists()
