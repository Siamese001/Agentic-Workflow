"""Tests for the 3 CI gates landed by Author-Gate dec_19dedcd1c109ebf25.

Plan refs:
- holdout-corpus-authoring-b5d2f6
- judge-spearman-calibration-a7e4c9
- legacy-yaml-deletion-audit-c8e3a4
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci import (
    check_calibration_evidence_authenticity,
    check_holdout_isolation,
    check_legacy_yaml_no_silent_delete,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


# ----- check_holdout_isolation ----------------------------------------------


def test_holdout_isolation_passes_against_real_fixtures():
    rc = check_holdout_isolation.check()
    assert rc == 0


def test_holdout_isolation_fails_on_ambiguous_row(tmp_path: Path):
    holdout_dir = tmp_path / "holdout"
    holdout_dir.mkdir()
    (holdout_dir / "apps_x.jsonl").write_text(
        json.dumps({"input": "x", "tags": ["holdout_scaffold"]}) + "\n",
        encoding="utf-8",
    )
    rc = check_holdout_isolation.check(holdout_dir)
    assert rc == 1


def test_holdout_isolation_fails_on_contradiction(tmp_path: Path):
    holdout_dir = tmp_path / "holdout"
    holdout_dir.mkdir()
    (holdout_dir / "apps_x.jsonl").write_text(
        json.dumps({"input": "x", "tags": ["SYNTHETIC_SEED_ONLY", "RELEASE_GATE"]}) + "\n",
        encoding="utf-8",
    )
    rc = check_holdout_isolation.check(holdout_dir)
    assert rc == 1


def test_holdout_isolation_passes_on_release_gate_tagged(tmp_path: Path):
    holdout_dir = tmp_path / "holdout"
    holdout_dir.mkdir()
    (holdout_dir / "apps_x.jsonl").write_text(
        json.dumps({"input": "x", "tags": ["RELEASE_GATE", "human_curated"]}) + "\n",
        encoding="utf-8",
    )
    rc = check_holdout_isolation.check(holdout_dir)
    assert rc == 0


def test_holdout_isolation_bypass_disables_gate(tmp_path: Path, monkeypatch):
    holdout_dir = tmp_path / "holdout"
    holdout_dir.mkdir()
    (holdout_dir / "apps_x.jsonl").write_text(
        json.dumps({"input": "x", "tags": []}) + "\n",  # would normally fail
        encoding="utf-8",
    )
    monkeypatch.setenv("HOLDOUT_ISOLATION_BYPASS", "1")
    rc = check_holdout_isolation.check(holdout_dir)
    assert rc == 0


# ----- check_calibration_evidence_authenticity ------------------------------


def test_calibration_authenticity_passes_against_real_artifact():
    rc = check_calibration_evidence_authenticity.check()
    assert rc == 0


def test_calibration_authenticity_passes_when_artifact_missing(tmp_path: Path):
    rc = check_calibration_evidence_authenticity.check(tmp_path / "nope.json")
    assert rc == 0


def test_calibration_authenticity_fails_on_synthetic_meets(tmp_path: Path):
    artifact = tmp_path / "judge_spearman.json"
    artifact.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "judge_id": "x::v2",
                        "is_synthetic_smoke": True,
                        "meets_threshold": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rc = check_calibration_evidence_authenticity.check(artifact)
    assert rc == 1


def test_calibration_authenticity_fails_on_rollup_contradiction(tmp_path: Path):
    artifact = tmp_path / "judge_spearman.json"
    artifact.write_text(
        json.dumps(
            {
                "any_synthetic_smoke": True,
                "all_meet_threshold": True,
                "results": [],
            }
        ),
        encoding="utf-8",
    )
    rc = check_calibration_evidence_authenticity.check(artifact)
    assert rc == 1


def test_calibration_authenticity_passes_on_real_corpus_meets(tmp_path: Path):
    artifact = tmp_path / "judge_spearman.json"
    artifact.write_text(
        json.dumps(
            {
                "any_synthetic_smoke": False,
                "all_meet_threshold": True,
                "results": [
                    {
                        "judge_id": "x::v2",
                        "is_synthetic_smoke": False,
                        "meets_threshold": True,
                        "spearman_rho": 0.84,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    rc = check_calibration_evidence_authenticity.check(artifact)
    assert rc == 0


# ----- check_legacy_yaml_no_silent_delete -----------------------------------


def test_legacy_yaml_no_silent_delete_passes_against_real_repo():
    rc = check_legacy_yaml_no_silent_delete.check()
    assert rc == 0


def test_legacy_yaml_no_silent_delete_fails_when_file_missing(tmp_path: Path, monkeypatch):
    # Stage a fake repo with no enumerated files.
    monkeypatch.setattr(check_legacy_yaml_no_silent_delete, "MARKERS_FILE", tmp_path / "missing.jsonl")
    rc = check_legacy_yaml_no_silent_delete.check(tmp_path)
    # Real DISPOSITIONS table = 13 files, none exist in tmp_path, no marker → fail.
    assert rc == 1


def test_legacy_yaml_no_silent_delete_bypass_disables_gate(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(check_legacy_yaml_no_silent_delete, "MARKERS_FILE", tmp_path / "x.jsonl")
    monkeypatch.setenv("LEGACY_YAML_DELETION_BYPASS", "1")
    rc = check_legacy_yaml_no_silent_delete.check(tmp_path)
    assert rc == 0
