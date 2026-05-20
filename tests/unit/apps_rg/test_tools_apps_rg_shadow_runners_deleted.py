"""Retired tools/apps_rg shadow runners must be physically absent."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

DELETED_TOOL_RUNNERS = (
    "tools/apps_rg/run_w5a_lane_matrix.py",
    "tools/apps_rg/run_w5b_lane_matrix.py",
    "tools/apps_rg/run_w6_lane_matrix.py",
    "tools/apps_rg/run_w7_lane_matrix.py",
    "tools/apps_rg/run_w8_lane_matrix.py",
    "tools/apps_rg/run_w9_lane_matrix.py",
    "tools/apps_rg/benchmark_exec_summary.py",
    "tools/apps_rg/warm_r1b_cache.py",
    "tools/apps_rg/migrate_r1a_cache.py",
    "tools/apps_rg/render_resume_docx.py",
    "tools/apps_rg/resume_docx_renderer.py",
    "tools/apps_rg/build_coherent_aggregation_rollup.py",
    "tools/apps_rg/relocate_runtime_proof_contract_harness.py",
    "tools/apps_rg/emit_one_spine_master_closeout_w9.py",
    "ops_scripts/apps_rg/rg_live_fire.py",
)


@pytest.mark.parametrize("rel_path", DELETED_TOOL_RUNNERS)
def test_shadow_runner_file_absent(rel_path: str) -> None:
    path = REPO_ROOT / rel_path.replace("/", "\\") if sys.platform == "win32" else REPO_ROOT / rel_path
    assert not path.is_file(), rel_path


@pytest.mark.parametrize(
    "rel_path",
    (
        "tools/apps_rg/run_w6_lane_matrix.py",
        "tools/apps_rg/benchmark_exec_summary.py",
        "ops_scripts/apps_rg/rg_live_fire.py",
    ),
)
def test_direct_python_execution_file_not_found(rel_path: str) -> None:
    proc = subprocess.run(
        [sys.executable, rel_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode != 0
    blob = (proc.stderr or "") + (proc.stdout or "")
    assert "can't open file" in blob.lower() or "cannot find the file" in blob.lower() or "No such file" in blob
