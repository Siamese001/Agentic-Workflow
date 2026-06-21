"""Tests for the apps_* testing-model CI gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_test_model.py"


def test_app_contract_marker_passes() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/_apps_contract/test_apps_rg_exit.py": (
                '"""apps-test-model: APP CONTRACT."""\n\n'
                "def test_exit_contract():\n"
                "    assert True\n"
            )
        }
    )

    assert result.ok
    assert result.violations == []


def test_law_marker_passes_for_unit_app_test() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/unit/apps_rg/test_product_authority.py": (
                "# apps-test-model: LAW\n\n"
                "def test_no_fabricated_product_proof():\n"
                "    assert True\n"
            )
        }
    )

    assert result.ok


def test_apps_eval_marker_passes() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/unit/apps_eval/contracts/test_grader.py": (
                "# apps-test-model: EVAL CONTRACT\n\n"
                "def test_eval_does_not_promote():\n"
                "    assert True\n"
            )
        }
    )

    assert result.ok


def test_contract_alias_is_normalized() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/apps_rg/test_cli.py": (
                "# apps-test-model: CONTRACT\n\n"
                "def test_cli_shape():\n"
                "    assert True\n"
            )
        }
    )

    assert result.ok


def test_missing_marker_fails_for_app_test() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/apps_rg/test_cli.py": (
                "def test_cli_shape():\n"
                "    assert True\n"
            )
        }
    )

    assert not result.ok
    assert result.violations
    assert result.violations[0].code == "missing_marker"
    assert "tests/apps_rg/test_cli.py" in result.violations[0].path


def test_invalid_bucket_fails() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/_apps_contract/test_apps_rg_exit.py": (
                "# apps-test-model: LEGACY\n\n"
                "def test_exit_contract():\n"
                "    assert True\n"
            )
        }
    )

    assert not result.ok
    assert result.violations[0].code == "invalid_bucket"
    assert "LEGACY" in result.violations[0].message


def test_non_app_test_is_ignored() -> None:
    from ops_scripts.ci.check_apps_test_model import check_paths

    result = check_paths(
        {
            "tests/unit/ops_scripts/ci/test_some_gate.py": (
                "def test_gate():\n"
                "    assert True\n"
            )
        }
    )

    assert result.ok
    assert result.scanned == 0


def test_cli_paths_exit_one_on_missing_marker(tmp_path: Path) -> None:
    app_test = tmp_path / "tests" / "apps_rg" / "test_cli.py"
    app_test.parent.mkdir(parents=True)
    app_test.write_text("def test_cli_shape():\n    assert True\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(GATE_SCRIPT), "--paths", str(app_test)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert proc.returncode == 1
    assert "missing_marker" in proc.stderr


def test_cli_paths_exit_zero_on_valid_marker(tmp_path: Path) -> None:
    app_test = tmp_path / "tests" / "apps_rg" / "test_cli.py"
    app_test.parent.mkdir(parents=True)
    app_test.write_text("# apps-test-model: SPINE BINDING\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(GATE_SCRIPT), "--paths", str(app_test)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "APPS-TEST-MODEL: OK" in proc.stdout


def test_changed_files_includes_untracked_files(tmp_path: Path) -> None:
    from ops_scripts.ci.check_apps_test_model import changed_files

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True, timeout=30)
    app_test = tmp_path / "tests" / "apps_rg" / "test_new_contract.py"
    app_test.parent.mkdir(parents=True)
    app_test.write_text("# apps-test-model: LAW\n", encoding="utf-8")

    assert "tests/apps_rg/test_new_contract.py" in changed_files(tmp_path)


@pytest.mark.parametrize(
    "path",
    [
        "tests/_apps_contract/test_apps_rg_exit.py",
        "tests/apps_lic/test_contract.py",
        "tests/unit/apps_research/test_contract.py",
        "tests/apps_eval/test_contract.py",
        "tests/unit/apps_underwriting_ai/test_contract.py",
    ],
)
def test_app_test_path_detection(path: str) -> None:
    from ops_scripts.ci.check_apps_test_model import is_app_test_path

    assert is_app_test_path(path)
