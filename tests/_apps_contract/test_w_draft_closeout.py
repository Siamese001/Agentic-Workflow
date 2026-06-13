"""Tests for the 3 Draft-plan close-out deliverables.

Covers:
- legacy-yaml-deletion-audit-c8e3a4 — disposition module + headers
- judge-spearman-calibration-a7e4c9 — calibration scaffold
- holdout-corpus-authoring-b5d2f6 — seeds with rubric_dim_human_scores
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ----- legacy_yaml_disposition ---------------------------------------------


def test_legacy_yaml_disposition_module_importable():
    from ops_scripts.maintenance import legacy_yaml_disposition as mod

    assert hasattr(mod, "apply")
    assert hasattr(mod, "Disposition")
    assert hasattr(mod, "DISPOSITIONS")
    assert len(mod.DISPOSITIONS) == 11  # active legacy files covered


def test_legacy_yaml_disposition_covers_all_expected_files():
    from ops_scripts.maintenance.legacy_yaml_disposition import DISPOSITIONS

    expected = {
        "config/routing_thresholds.yaml",
        "apps_eval/config/eval_policies.yaml",
        "apps_eval/config/eval_thresholds.yaml",
        "apps_exec/config/exec_policies.yaml",
        "apps_exec/config/exec_thresholds.yaml",
        "apps_lic/config/lic_policies.yaml",
        "apps_lic/config/lic_thresholds.yaml",
        "apps_research/config/research_policies.yaml",
        "apps_research/config/research_thresholds.yaml",
        "apps_rg/config/rg_policies.yaml",
        "apps_rg/config/rg_thresholds.yaml",
    }
    covered = {d.rel_path for d in DISPOSITIONS}
    assert covered == expected


def test_legacy_yaml_disposition_classifies_routing_thresholds_as_canonical():
    from ops_scripts.maintenance.legacy_yaml_disposition import DISPOSITIONS, Disposition

    for d in DISPOSITIONS:
        if d.rel_path == "config/routing_thresholds.yaml":
            assert d.disposition is Disposition.CANONICAL_SSOT
            assert d.consumers  # must declare at least one consumer
            return
    pytest.fail("config/routing_thresholds.yaml not in DISPOSITIONS")


def test_legacy_yaml_headers_applied_to_live_files():
    """At least one canonical-ssot file must carry the new header marker."""
    path = REPO_ROOT / "config" / "routing_thresholds.yaml"
    if not path.is_file():
        pytest.skip(f"file not present: {path}")
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
    assert "CANONICAL SSOT" in head
    assert "legacy-yaml-deletion-audit-c8e3a4" in head


def test_legacy_yaml_disposition_dry_run_does_not_write(tmp_path: Path):
    from ops_scripts.maintenance.legacy_yaml_disposition import apply

    summary = apply(tmp_path, dry_run=True)
    # Every entry is skipped_missing since tmp_path has no files.
    assert all(e.get("action") == "skipped_missing" for e in summary)


# ----- judge_spearman_calibration ------------------------------------------


def test_judge_spearman_calibration_module_importable():
    from ops_scripts.calibration import judge_spearman_calibration as mod

    assert hasattr(mod, "run_all")
    assert hasattr(mod, "calibrate_judge")
    assert hasattr(mod, "CalibrationResult")
    assert mod.SPEARMAN_THRESHOLD == 0.80
    assert len(mod.JUDGE_CALIBRATION_TARGETS) == 3


def test_judge_spearman_calibration_runs_against_synthetic_holdout():
    from ops_scripts.calibration.judge_spearman_calibration import run_all

    fixtures_root = REPO_ROOT / "apps_eval" / "fixtures"
    results = run_all(fixtures_root)
    assert len(results) == 4
    # Every result either imports successfully (n>=0) or reports import_error.
    for r in results:
        if r.error:
            assert r.n == 0
        else:
            assert r.n >= 0


def test_judge_spearman_flags_synthetic_as_not_meeting_threshold():
    """Synthetic smoke MUST NOT meet threshold even if rho is high (guard rail)."""
    from ops_scripts.calibration.judge_spearman_calibration import run_all

    fixtures_root = REPO_ROOT / "apps_eval" / "fixtures"
    results = run_all(fixtures_root)
    for r in results:
        if r.is_synthetic_smoke:
            assert r.meets_threshold is False, (
                f"Judge {r.judge_id}: synthetic smoke MUST NOT report meets_threshold=True "
                "(would falsely claim production-ready calibration)"
            )


# ----- holdout seeds carry rubric_dim_human_scores -------------------------


@pytest.mark.parametrize(
    "app_id",
    [
        "apps_qna", "apps_research", "apps_exec",
        "apps_underwriting_ai", "apps_rg", "apps_lic", "apps_eval",
    ],
)
def test_holdout_seeds_carry_human_score_dict(app_id: str):
    fixture = REPO_ROOT / "apps_eval" / "fixtures" / "holdout" / f"{app_id}.jsonl"
    assert fixture.is_file(), f"missing: {fixture}"
    rows = [
        json.loads(line)
        for line in fixture.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows, f"empty: {fixture}"
    for row in rows:
        assert "rubric_dim_human_scores" in row, (
            f"Row in {app_id}.jsonl missing rubric_dim_human_scores — required for "
            "judge_spearman_calibration scaffold"
        )
        assert isinstance(row["rubric_dim_human_scores"], dict)
        # AG dec_19dede3a5e4d6507f flipped tags after user-as-curator approval.
        # Holdout rows now carry exactly one of SYNTHETIC_SEED_ONLY|RELEASE_GATE.
        tags = row.get("tags", [])
        assert ("SYNTHETIC_SEED_ONLY" in tags) ^ ("RELEASE_GATE" in tags), (
            f"Row in {app_id}.jsonl must carry exactly one of SYNTHETIC_SEED_ONLY|RELEASE_GATE, got {tags}"
        )
