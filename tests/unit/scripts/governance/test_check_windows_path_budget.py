"""Tests for scripts/governance/check_windows_path_budget.py."""

from __future__ import annotations

import sys
from pathlib import Path, PureWindowsPath

REPO_IMPORT_ROOT = Path(__file__).resolve().parents[4]
WINDOWS_RCA_ROOT = PureWindowsPath("C:/Git/Agentic-Workflow-FRESH-l6-v40-shadow-observability-gap-closure")
sys.path.insert(0, str(REPO_IMPORT_ROOT / "scripts" / "governance"))

import check_windows_path_budget as mod  # noqa: E402


def _max_projection(out_dir: PureWindowsPath) -> mod.ProjectedPath:
    projections = mod.projected_paths(out_dir, suite="apps_rg.dev.resume_generation")
    return max(projections, key=lambda projection: projection.length)


def test_reported_long_apps_eval_root_exceeds_reserved_budget() -> None:
    out_dir = WINDOWS_RCA_ROOT / "artifacts" / "apps_eval" / "independent_apps_rg_live_runtime"

    max_projection = _max_projection(out_dir)
    failures, warnings = mod.budget_violations([max_projection])

    assert max_projection.length == 260
    assert failures == [max_projection]
    assert warnings == []


def test_short_apps_eval_root_stays_within_reserved_budget() -> None:
    out_dir = WINDOWS_RCA_ROOT / "artifacts" / "ae_rg_live"

    max_projection = _max_projection(out_dir)
    failures, warnings = mod.budget_violations([max_projection])

    assert max_projection.length == 228
    assert failures == []
    assert warnings == []


def test_custom_suffix_templates_can_check_new_artifact_shapes() -> None:
    projections = mod.projected_paths(
        PureWindowsPath("C:/short"),
        suite="apps_rg.dev.resume_generation",
        suffix_templates=("{suite_path}/{run_id}/{scenario}/custom.json",),
    )

    assert str(projections[0].path).endswith(
        "apps_rg_dev_resume_generation\\0000000000000000\\resume_tailor_escalation\\custom.json"
    )
