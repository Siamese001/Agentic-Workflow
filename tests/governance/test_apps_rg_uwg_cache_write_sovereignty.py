"""Governance tests — apps_rg UWG cache-write sovereignty.

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f

W0 (baseline):
  test_section_pipeline_currently_violates_gate — xfail(strict=True)
  Proves check_no_direct_semantic_cache_write exits non-zero on the unmodified codebase.
  W1.P3 will remove the xfail marker once the violation is fixed.

W1 (added by W1.P3):
  test_gate_clean_after_w1
  test_section_pipeline_produces_inert_proposal_not_cache_write
  test_semantic_cache_dir_not_written_during_section_pipeline
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_no_direct_semantic_cache_write.py"


# ---------------------------------------------------------------------------
# W0 baseline — violation must be detected before W1 lands
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="W0 baseline: direct cache write violation expected until W1 lands",
)
def test_section_pipeline_currently_violates_gate() -> None:
    """Gate must exit non-zero on the unmodified codebase (G2 violation present)."""
    result = subprocess.run(
        [sys.executable, str(GATE_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Expected gate to detect violation (exit 1) but it exited {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_gate_identifies_section_pipeline_as_violator() -> None:
    """Gate output must name section_agentic_pipeline.py as the violating file."""
    result = subprocess.run(
        [sys.executable, str(GATE_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    combined = result.stdout + result.stderr
    assert "section_agentic_pipeline" in combined, (
        "Gate did not identify section_agentic_pipeline as the violating file.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
