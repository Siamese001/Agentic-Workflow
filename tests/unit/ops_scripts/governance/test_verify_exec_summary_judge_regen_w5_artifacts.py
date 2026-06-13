"""W5 artifact checklist verifier tests."""

from __future__ import annotations

import json
from pathlib import Path

from tools.cursor.verify_exec_summary_judge_regen_w5_artifacts import (
    REQUIRED_ARTIFACTS,
    verify_run_dir,
)


def test_verify_passes_minimal_v2_run_dir(tmp_path: Path) -> None:
    for name in REQUIRED_ARTIFACTS:
        (tmp_path / name).write_text("{}", encoding="utf-8")
    (tmp_path / "judge_remediation_cycles.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "schema": "executive_summary_judge_remediation_cycles_v2",
                "cycles": [],
                "regen_outcome": "floor_not_met",
                "final_publish_baseline": "scratch",
            },
        ),
        encoding="utf-8",
    )
    (tmp_path / "publish_integrity_receipt.json").write_text(
        json.dumps(
            {
                "published_candidate_digest": "abc",
                "final_artifact_digest_source": "abc",
            },
        ),
        encoding="utf-8",
    )
    report = verify_run_dir(tmp_path)
    assert report["passed"] is True
    assert report["schema_version_ok"] is True


def test_verify_fails_missing_artifacts(tmp_path: Path) -> None:
    report = verify_run_dir(tmp_path)
    assert report["passed"] is False
    assert report["missing_artifacts"]
