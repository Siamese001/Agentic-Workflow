"""Inventory + retirement proof for legacy ``competencies_dispatch`` CLI (non-canonical).

Canonical runtime proof must use ``python -m apps_rg --section competencies`` /
``apps_rg.runtime.sections.competencies_lane`` — not ``python -m ...competencies_dispatch``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_FORBIDDEN_SUBPROCESS_SNIPPETS = (
    '"-m", "apps_rg.runtime.sections.competencies_lane_runtime"',
    "'-m', 'apps_rg.runtime.sections.competencies_lane_runtime'",
)


@pytest.mark.parametrize("snippet", _FORBIDDEN_SUBPROCESS_SNIPPETS)
def test_contract_tests_do_not_spawn_standalone_competencies_dispatch_module(snippet: str) -> None:
    """Regression: standalone dispatch subprocess must not be primary proof."""
    contract_dir = REPO_ROOT / "tests" / "_apps_contract"
    offenders: list[str] = []
    allow = frozenset({"test_competencies_dispatch_retirement_inventory.py"})
    for path in sorted(contract_dir.glob("*.py")):
        if path.name in allow:
            continue
        text = path.read_text(encoding="utf-8")
        if snippet in text:
            offenders.append(path.as_posix())
    assert offenders == [], f"Remove standalone competencies_dispatch subprocess from: {offenders}"


def test_deprecated_competencies_dispatch_module_main_is_non_executable_product_path() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.sections.competencies_lane_runtime"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    combined = (proc.stderr or "") + (proc.stdout or "")
    assert "Deprecated" in combined or "python -m apps_rg" in combined


def test_competencies_lane_docs_use_double_dash_section_flag() -> None:
    lane = REPO_ROOT / "apps_rg" / "runtime" / "sections" / "competencies_lane.py"
    text = lane.read_text(encoding="utf-8")
    assert "--section competencies" in text
    assert "python -m apps_rg section competencies" not in text


def test_competencies_primary_surface_is_sections_lane_not_dispatch_cli() -> None:
    lane = REPO_ROOT / "apps_rg" / "runtime" / "sections" / "competencies_lane.py"
    lane_exec = REPO_ROOT / "apps_rg" / "runtime" / "sections" / "competencies_lane_execution.py"
    lane_text = lane.read_text(encoding="utf-8")
    exec_text = lane_exec.read_text(encoding="utf-8")
    assert "competencies_lane_execution" in lane_text
    assert "run_competencies_lane_execution" in lane_text
    lane_code = lane_text.replace("``run_competencies_execution``", "")
    assert "run_competencies_execution(" not in lane_code
    assert "trace_runtime_path" in exec_text
    assert "apps_rg.runtime.sections.competencies_lane" in exec_text
    assert "run_competencies_execution" in exec_text
