"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/ssot.py."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def test_module_importable():
    """Module ssot must be importable."""
    import agentic_core.L5_safety.config.structure_blueprint.ssot  # noqa: F401


# ---------------------------------------------------------------------------
# SSOT root files: every actual root file must be covered
# ---------------------------------------------------------------------------

KNOWN_ROOT_FILES = [
    "README.md",
    "AGENTS.md",
    "conftest.py",
    "pyproject.toml",
    "pyrightconfig.json",
    "pytest.ini",
    ".codeiumignore",
    ".env",
    ".gitattributes",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".pylintrc",
    "ARCHITECTURE_LAYERS.md",
]

KNOWN_ROOT_DYNAMIC = [
    "trace_abc123.jsonl",
    "mission_run1.log",
    "deploy.bat",
    "setup.sh",
    "root_drift_fix.py",
]

SHOULD_NOT_MATCH = [
    "random_script.py",
    "notes.txt",
    "output.json",
    "somefile.yaml",
]


@pytest.fixture()
def root_allowed_patterns():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import ROOT_ALLOWED_PATTERNS

    return ROOT_ALLOWED_PATTERNS


@pytest.mark.parametrize("filename", KNOWN_ROOT_FILES)
def test_root_allowed_patterns_covers_known_root_files(filename, root_allowed_patterns):
    """Every known root-level file must match at least one ROOT_ALLOWED_PATTERNS entry."""
    matched = any(p.match(filename) for p in root_allowed_patterns)
    assert matched, (
        f"{filename!r} is a known root file but is NOT matched by ROOT_ALLOWED_PATTERNS. "
        f"Add a re.compile entry for it in ssot.py."
    )


@pytest.mark.parametrize("filename", KNOWN_ROOT_DYNAMIC)
def test_root_allowed_patterns_covers_dynamic_patterns(filename, root_allowed_patterns):
    """Dynamic root file patterns (traces, logs, scripts) must match."""
    matched = any(p.match(filename) for p in root_allowed_patterns)
    assert matched, f"{filename!r} should match a dynamic ROOT_ALLOWED_PATTERNS entry."


@pytest.mark.parametrize("filename", SHOULD_NOT_MATCH)
def test_root_allowed_patterns_rejects_unexpected_files(filename, root_allowed_patterns):
    """Files that don't belong at root must NOT match ROOT_ALLOWED_PATTERNS."""
    matched = any(p.match(filename) for p in root_allowed_patterns)
    assert not matched, (
        f"{filename!r} should NOT match ROOT_ALLOWED_PATTERNS but it does. Pattern is too broad."
    )


def test_root_allowed_patterns_is_non_empty(root_allowed_patterns):
    """ROOT_ALLOWED_PATTERNS must contain compiled regex patterns."""
    assert len(root_allowed_patterns) > 0
    for p in root_allowed_patterns:
        assert hasattr(p, "match"), f"Entry {p!r} is not a compiled regex pattern."


# ---------------------------------------------------------------------------
# PROJECT_ROOT_WHITELIST: folder-level checks
# ---------------------------------------------------------------------------

KNOWN_ROOT_DIRS = [
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "ops_scripts",
    "tests",
    "docs",
    "data",
]


@pytest.fixture()
def project_root_whitelist():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import PROJECT_ROOT_WHITELIST

    return PROJECT_ROOT_WHITELIST


@pytest.mark.parametrize("folder", KNOWN_ROOT_DIRS)
def test_project_root_whitelist_contains_known_dirs(folder, project_root_whitelist):
    """Every known top-level directory must be in PROJECT_ROOT_WHITELIST."""
    assert folder in project_root_whitelist, (
        f"{folder!r} is a known root directory but is missing from PROJECT_ROOT_WHITELIST."
    )


def test_project_root_whitelist_is_frozenset(project_root_whitelist):
    """PROJECT_ROOT_WHITELIST must be a frozenset (immutable)."""
    assert isinstance(project_root_whitelist, frozenset)


# ---------------------------------------------------------------------------
# territories.yaml __root__ section in sync with ROOT_ALLOWED_PATTERNS
# ---------------------------------------------------------------------------


def test_territories_yaml_root_allowed_files_in_sync(root_allowed_patterns):
    """territories.yaml __root__.allowed_files must all be matched by ROOT_ALLOWED_PATTERNS."""
    import yaml

    territories_path = Path(__file__).parents[6] / "config" / "structure_blueprint" / "territories.yaml"
    assert territories_path.exists(), f"territories.yaml not found at {territories_path}"
    with open(territories_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    root_section = data.get("territories", {}).get("__root__", {})
    allowed_files = root_section.get("allowed_files", [])
    assert allowed_files, "__root__.allowed_files in territories.yaml is empty."
    for filename in allowed_files:
        matched = any(p.match(filename) for p in root_allowed_patterns)
        assert matched, (
            f"{filename!r} is listed in territories.yaml __root__.allowed_files "
            f"but has no matching entry in ROOT_ALLOWED_PATTERNS in ssot.py. "
            f"Keep both in sync."
        )
