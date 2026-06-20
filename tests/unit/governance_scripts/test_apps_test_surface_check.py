"""Unit tests for _apps_test_surface_check.py helper.

Tests verify:
  - All violation kinds are detected correctly
  - Clean repos return empty lists
  - Partial presence (dir exists but __init__.py missing) is flagged
  - Forbidden tests/integration/apps_<x>/ is flagged
  - Custom app lists are respected

Plan: apps-test-surface-consolidation-11acd9-v2 W6.4.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the helper importable without a package layout (mirrors sibling tests).
# Canonical path — _apps_test_surface_check.py lives in governance/scripts/, not _legacy_windsurf/
_HELPER_DIR = Path(__file__).resolve().parents[3] / ".codex" / "governance" / "scripts"
if str(_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_HELPER_DIR))

from _apps_test_surface_check import ALL_APPS, ViolationKind, Violation, check  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    """Create a minimal clean repo structure for one app."""
    app = "apps_rg"
    (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
    (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
    (tmp_path / "tests" / app).mkdir(parents=True)
    (tmp_path / "tests" / app / "__init__.py").write_text("")
    return tmp_path


@pytest.fixture()
def multi_clean_repo(tmp_path: Path) -> Path:
    """Create a clean repo for 3 apps."""
    for app in ("apps_rg", "apps_qna", "apps_eval"):
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
        (tmp_path / "tests" / app).mkdir(parents=True)
        (tmp_path / "tests" / app / "__init__.py").write_text("")
    return tmp_path


# ---------------------------------------------------------------------------
# Clean scenarios
# ---------------------------------------------------------------------------

class TestClean:
    def test_clean_single_app(self, clean_repo: Path) -> None:
        violations = check(clean_repo, apps=["apps_rg"])
        assert violations == []

    def test_clean_multiple_apps(self, multi_clean_repo: Path) -> None:
        violations = check(multi_clean_repo, apps=["apps_rg", "apps_qna", "apps_eval"])
        assert violations == []

    def test_empty_app_list(self, tmp_path: Path) -> None:
        violations = check(tmp_path, apps=[])
        assert violations == []


# ---------------------------------------------------------------------------
# MISSING_UNIT_DIR
# ---------------------------------------------------------------------------

class TestMissingUnitDir:
    def test_missing_unit_dir_flagged(self, tmp_path: Path) -> None:
        app = "apps_rg"
        (tmp_path / "tests" / app).mkdir(parents=True)
        (tmp_path / "tests" / app / "__init__.py").write_text("")
        # No tests/unit/apps_rg/
        violations = check(tmp_path, apps=[app])
        kinds = [v.kind for v in violations]
        assert ViolationKind.MISSING_UNIT_DIR in kinds

    def test_missing_unit_dir_message_contains_path(self, tmp_path: Path) -> None:
        app = "apps_shared"
        (tmp_path / "tests" / app).mkdir(parents=True)
        (tmp_path / "tests" / app / "__init__.py").write_text("")
        violations = check(tmp_path, apps=[app])
        unit_viols = [v for v in violations if v.kind == ViolationKind.MISSING_UNIT_DIR]
        assert len(unit_viols) == 1
        assert f"tests/unit/{app}/" in unit_viols[0].path
        assert app in unit_viols[0].app

    def test_missing_unit_dir_correct_app(self, multi_clean_repo: Path) -> None:
        """Only the app missing the unit dir should be flagged."""
        import shutil
        shutil.rmtree(multi_clean_repo / "tests" / "unit" / "apps_qna")
        violations = check(multi_clean_repo, apps=["apps_rg", "apps_qna", "apps_eval"])
        flagged_apps = [v.app for v in violations if v.kind == ViolationKind.MISSING_UNIT_DIR]
        assert flagged_apps == ["apps_qna"]


# ---------------------------------------------------------------------------
# MISSING_UNIT_INIT
# ---------------------------------------------------------------------------

class TestMissingUnitInit:
    def test_missing_unit_init_flagged(self, tmp_path: Path) -> None:
        app = "apps_lic"
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        # Dir exists but no __init__.py
        (tmp_path / "tests" / app).mkdir(parents=True)
        (tmp_path / "tests" / app / "__init__.py").write_text("")
        violations = check(tmp_path, apps=[app])
        kinds = [v.kind for v in violations]
        assert ViolationKind.MISSING_UNIT_INIT in kinds

    def test_missing_unit_init_path(self, tmp_path: Path) -> None:
        app = "apps_lic"
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / app).mkdir(parents=True)
        (tmp_path / "tests" / app / "__init__.py").write_text("")
        violations = check(tmp_path, apps=[app])
        init_viols = [v for v in violations if v.kind == ViolationKind.MISSING_UNIT_INIT]
        assert len(init_viols) == 1
        assert "__init__.py" in init_viols[0].path


# ---------------------------------------------------------------------------
# MISSING_INTG_DIR
# ---------------------------------------------------------------------------

class TestMissingIntgDir:
    def test_missing_intg_dir_flagged(self, tmp_path: Path) -> None:
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
        violations = check(tmp_path, apps=[app])
        kinds = [v.kind for v in violations]
        assert ViolationKind.MISSING_INTG_DIR in kinds

    def test_missing_intg_dir_message(self, tmp_path: Path) -> None:
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
        violations = check(tmp_path, apps=[app])
        intg_viols = [v for v in violations if v.kind == ViolationKind.MISSING_INTG_DIR]
        assert len(intg_viols) == 1
        assert f"tests/{app}/" in intg_viols[0].path


# ---------------------------------------------------------------------------
# MISSING_INTG_INIT
# ---------------------------------------------------------------------------

class TestMissingIntgInit:
    def test_missing_intg_init_flagged(self, tmp_path: Path) -> None:
        app = "apps_eval"
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
        (tmp_path / "tests" / app).mkdir(parents=True)
        # Dir exists but no __init__.py
        violations = check(tmp_path, apps=[app])
        kinds = [v.kind for v in violations]
        assert ViolationKind.MISSING_INTG_INIT in kinds

    def test_missing_intg_init_path(self, tmp_path: Path) -> None:
        app = "apps_eval"
        (tmp_path / "tests" / "unit" / app).mkdir(parents=True)
        (tmp_path / "tests" / "unit" / app / "__init__.py").write_text("")
        (tmp_path / "tests" / app).mkdir(parents=True)
        violations = check(tmp_path, apps=[app])
        init_viols = [v for v in violations if v.kind == ViolationKind.MISSING_INTG_INIT]
        assert len(init_viols) == 1
        assert "__init__.py" in init_viols[0].path


# ---------------------------------------------------------------------------
# FORBIDDEN_INTG_SUBDIR
# ---------------------------------------------------------------------------

class TestForbiddenIntgSubdir:
    def test_forbidden_intg_subdir_flagged(self, clean_repo: Path) -> None:
        app = "apps_rg"
        (clean_repo / "tests" / "integration" / app).mkdir(parents=True)
        violations = check(clean_repo, apps=[app])
        kinds = [v.kind for v in violations]
        assert ViolationKind.FORBIDDEN_INTG_SUBDIR in kinds

    def test_forbidden_intg_subdir_path(self, clean_repo: Path) -> None:
        app = "apps_rg"
        (clean_repo / "tests" / "integration" / app).mkdir(parents=True)
        violations = check(clean_repo, apps=[app])
        forbidden_viols = [v for v in violations if v.kind == ViolationKind.FORBIDDEN_INTG_SUBDIR]
        assert len(forbidden_viols) == 1
        assert f"tests/integration/{app}/" in forbidden_viols[0].path

    def test_forbidden_intg_subdir_clean_when_absent(self, clean_repo: Path) -> None:
        violations = check(clean_repo, apps=["apps_rg"])
        forbidden_viols = [v for v in violations if v.kind == ViolationKind.FORBIDDEN_INTG_SUBDIR]
        assert forbidden_viols == []

    def test_forbidden_intg_subdir_does_not_affect_other_apps(
        self, multi_clean_repo: Path
    ) -> None:
        (multi_clean_repo / "tests" / "integration" / "apps_eval").mkdir(parents=True)
        violations = check(multi_clean_repo, apps=["apps_rg", "apps_qna", "apps_eval"])
        forbidden_apps = [v.app for v in violations if v.kind == ViolationKind.FORBIDDEN_INTG_SUBDIR]
        assert forbidden_apps == ["apps_eval"]


# ---------------------------------------------------------------------------
# Multiple violations in one app
# ---------------------------------------------------------------------------

class TestMultipleViolations:
    def test_all_three_missing(self, tmp_path: Path) -> None:
        app = "apps_research"
        violations = check(tmp_path, apps=[app])
        kinds = {v.kind for v in violations}
        assert ViolationKind.MISSING_UNIT_DIR in kinds
        assert ViolationKind.MISSING_INTG_DIR in kinds

    def test_violation_count_all_missing(self, tmp_path: Path) -> None:
        app = "apps_research"
        violations = check(tmp_path, apps=[app])
        assert len(violations) == 2  # MISSING_UNIT_DIR + MISSING_INTG_DIR


# ---------------------------------------------------------------------------
# Violation dataclass contract
# ---------------------------------------------------------------------------

class TestViolationShape:
    def test_violation_is_frozen(self, tmp_path: Path) -> None:
        app = "apps_exec"
        violations = check(tmp_path, apps=[app])
        assert violations
        v = violations[0]
        with pytest.raises((AttributeError, TypeError)):
            v.app = "other"  # type: ignore[misc]

    def test_violation_has_all_fields(self, tmp_path: Path) -> None:
        app = "apps_exec"
        violations = check(tmp_path, apps=[app])
        for v in violations:
            assert v.app
            assert v.kind
            assert v.path
            assert v.message


# ---------------------------------------------------------------------------
# ALL_APPS completeness
# ---------------------------------------------------------------------------

class TestAllApps:
    def test_all_apps_contains_nine(self) -> None:
        assert len(ALL_APPS) == 9

    def test_all_apps_contains_apps_exec(self) -> None:
        assert "apps_exec" in ALL_APPS

    def test_all_apps_no_duplicates(self) -> None:
        assert len(ALL_APPS) == len(set(ALL_APPS))

    def test_all_apps_all_prefixed(self) -> None:
        for app in ALL_APPS:
            assert app.startswith("apps_"), f"{app} does not start with 'apps_'"
