from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_eval.baselines import load_baseline, promote_baseline
from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import compare_record_to_baseline, run_eval


def test_promote_and_load_named_baseline(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path / "runs"),
        )
    )

    baseline_path = promote_baseline(
        record.artifact_paths["eval_record"],
        "apps_rg.dev.resume_generation",
        baseline_dir=tmp_path / "baselines",
    )
    baseline = load_baseline("apps_rg.dev.resume_generation", tmp_path / "baselines")

    assert baseline_path.is_file()
    assert baseline["record_id"] == record.record_id
    assert compare_record_to_baseline(record.to_dict(), baseline).verdict == "pass"


def test_promote_baseline_rejects_failing_record(tmp_path: Path) -> None:
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps({"scorecard": {"verdict": "fail"}}), encoding="utf-8")

    with pytest.raises(ValueError):
        promote_baseline(record_path, "apps_rg.dev.resume_generation", baseline_dir=tmp_path / "baselines")


def test_load_baseline_rejects_legacy_schema(tmp_path: Path) -> None:
    baseline_dir = tmp_path / "baselines"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    legacy_baseline = baseline_dir / "apps_rg.dev.resume_generation.json"
    legacy_baseline.write_text(
        json.dumps({"record_id": "rid", "scorecard": {"score": 1.0}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="schema_version mismatch"):
        load_baseline("apps_rg.dev.resume_generation", baseline_dir)
