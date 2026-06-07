"""Shared fixtures for tests/governance/.

These tests codify the governance gap surfaced by the cheat-proof audit of
``python -m apps_rg`` on 2026-05-01 (see audit conversation; see
``docs/archive/windsurf/legacy-tree/plans/apps-rg-governed-runtime-b8d4f1.md``).

Every test in this directory is currently expected to FAIL because the
governance plumbing for the R3 grounded-read path does not exist yet. Each
test is marked ``@pytest.mark.xfail(strict=True)`` so:

  - CI master stays green while the remediation plan is in flight.
  - When a phase of the plan lands and a test starts passing, ``strict=True``
    will report XPASS UNEXPECTEDLY and force the implementing developer to
    remove the xfail marker, locking the gain in.

When ALL tests in this directory pass without xfail markers, ``apps_rg`` is
``FULLY_PROVEN`` per the audit standard.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_RUNS = REPO_ROOT / "artifacts" / "apps_rg" / "runs"


@pytest.fixture(scope="session")
def latest_apps_rg_run_dir() -> Path:
    """Locate the most recent ``artifacts/apps_rg/runs/<ts>/`` directory.

    Skips the test if no run has been produced yet (different from xfail —
    "no run to inspect" is a precondition gap, not a governance gap).
    """
    if not APPS_RG_RUNS.exists():
        pytest.skip(f"No apps_rg runs at {APPS_RG_RUNS} — execute python -m apps_rg first.")
    candidates = sorted(
        (p for p in APPS_RG_RUNS.iterdir() if p.is_dir() and p.name[:8].isdigit()),
        key=lambda p: p.name,
        reverse=True,
    )
    if not candidates:
        pytest.skip(f"No timestamped run dirs under {APPS_RG_RUNS}")
    return candidates[0]


@pytest.fixture(scope="session")
def latest_run_report(latest_apps_rg_run_dir: Path) -> dict:
    """Load the run_report.json from the latest apps_rg run."""
    report = latest_apps_rg_run_dir / "run_report.json"
    if not report.exists():
        pytest.skip(f"No run_report.json in {latest_apps_rg_run_dir}")
    return json.loads(report.read_text(encoding="utf-8"))
