"""Unit tests for :mod:`.windsurf.scripts._deferred_scope_plan_scaffold`."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
SCAFFOLD_MODULE_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_deferred_scope_plan_scaffold.py"


def _load_module():
    """Load the scaffolder module by file path.

    The ``.claude/governance/scripts/`` directory is not a Python package; the hook
    tooling imports these modules via ``sys.path`` manipulation. Tests do
    the same by spec-loading, so no conftest plumbing is required.
    """
    spec = importlib.util.spec_from_file_location("_deferred_scope_plan_scaffold", SCAFFOLD_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = _load_module()


def _marker(**overrides) -> dict[str, str]:
    base = {
        "plan": "NEW:widget-audit",
        "wave": "W1",
        "phase": "W1.1",
        "layer": "L4",
        "fan_in": "7",
        "surface": "State",
        "coverage_gap_pct": "60.0",
        "est_tokens": "12000",
        "reason": "Widget audit deferred",
    }
    base.update(overrides)
    return base


def test_new_slug_scaffolds_file(tmp_path: Path) -> None:
    result = SCAFFOLD.scaffold_plan_if_needed(_marker(), tmp_path)
    assert result.created is True
    assert result.plan_path.exists()
    assert re.fullmatch(r"widget-audit-[0-9a-f]{6}\.md", result.plan_filename)
    content = result.plan_path.read_text(encoding="utf-8")
    # Template essentials present
    assert "plan_id: widget-audit-" in content
    assert "DEFERRED_SCOPE:" in content
    assert "Widget audit deferred" in content


def test_new_slug_is_idempotent(tmp_path: Path) -> None:
    first = SCAFFOLD.scaffold_plan_if_needed(_marker(), tmp_path)
    assert first.created is True
    second = SCAFFOLD.scaffold_plan_if_needed(_marker(), tmp_path)
    assert second.created is False
    assert second.plan_filename == first.plan_filename
    assert second.plan_path == first.plan_path


def test_existing_plan_resolves_without_creating(tmp_path: Path) -> None:
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    existing = plans_dir / "authored-plan-abcdef.md"
    existing.write_text("# existing", encoding="utf-8")

    result = SCAFFOLD.scaffold_plan_if_needed(
        _marker(plan="authored-plan"),  # no NEW: prefix; slug only
        tmp_path,
    )
    assert result.created is False
    assert result.plan_filename == "authored-plan-abcdef.md"
    assert result.plan_path == existing


def test_existing_plan_exact_filename_resolves(tmp_path: Path) -> None:
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    existing = plans_dir / "my-plan-123abc.md"
    existing.write_text("x", encoding="utf-8")

    result = SCAFFOLD.scaffold_plan_if_needed(_marker(plan="my-plan-123abc.md"), tmp_path)
    assert result.created is False
    assert result.plan_path == existing


def test_missing_existing_plan_reports_drift(tmp_path: Path) -> None:
    # User said "existing" but no disk file → no scaffold, reason explains.
    result = SCAFFOLD.scaffold_plan_if_needed(_marker(plan="ghost-plan"), tmp_path)
    assert result.created is False
    assert "not found on disk" in result.reason
    assert not result.plan_path.exists()


def test_invalid_new_slug_is_rejected(tmp_path: Path) -> None:
    # Slug contains illegal characters → refuse to scaffold.
    result = SCAFFOLD.scaffold_plan_if_needed(_marker(plan="NEW:Invalid Name!"), tmp_path)
    assert result.created is False
    assert "invalid slug" in result.reason.lower()


def test_new_prefix_case_insensitive(tmp_path: Path) -> None:
    result = SCAFFOLD.scaffold_plan_if_needed(_marker(plan="new:case-insensitive-slug"), tmp_path)
    assert result.created is True
    assert result.plan_filename.startswith("case-insensitive-slug-")


def test_missing_plan_field_returns_reason(tmp_path: Path) -> None:
    result = SCAFFOLD.scaffold_plan_if_needed({}, tmp_path)
    assert result.created is False
    assert "no plan field" in result.reason


def test_scaffolded_file_has_required_plan_frontmatter(tmp_path: Path) -> None:
    result = SCAFFOLD.scaffold_plan_if_needed(_marker(), tmp_path)
    content = result.plan_path.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "plan_type:" in content
    # Contains the DEFERRED_SCOPE marker so pre-commit gate sees it inside the file.
    assert "DEFERRED_SCOPE:" in content
    # Contains a Phase-Level Summary header so T2/T3 plan-format gates accept it.
    assert "Phase-Level Summary" in content


def test_path_traversal_in_existing_plan_is_contained(tmp_path: Path) -> None:
    # A plan value containing a relative path must not escape the plans dir.
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "legit-plan-aaaaaa.md").write_text("x", encoding="utf-8")

    result = SCAFFOLD.scaffold_plan_if_needed(_marker(plan="../../etc/legit-plan"), tmp_path)
    # Must not write or resolve outside plans_dir.
    if result.plan_path.exists():
        assert result.plan_path.is_relative_to(plans_dir)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("-starts-with-dash", None),
        ("has spaces", None),
        ("path/traversal", None),
        ("", None),
        ("a", None),  # 1 char — below minimum (regex requires 2+)
        ("UPPERCASE", "uppercase"),  # lowercased on purpose
        ("too-short", "too-short"),  # valid
        ("valid-slug-123", "valid-slug-123"),
    ],
)
def test_slug_validator_behavior(value: str, expected: str | None) -> None:
    """Sanitizer lowercases and enforces the ``^[a-z0-9][a-z0-9-]{1,63}$`` shape."""

    assert SCAFFOLD._sanitize_slug(value) == expected  # noqa: SLF001
