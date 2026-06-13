from __future__ import annotations

from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_scorecard_is_stable_across_repeated_snapshot_runs(tmp_path: Path) -> None:
    request = EvalRequest(
        suite_id="apps_rg.dev.resume_generation",
        mode="snapshot",
        deterministic_only=True,
        out_dir=str(tmp_path),
    )
    first = run_eval(request)
    second = run_eval(request)
    assert first.record_id == second.record_id
    assert first.created_at == second.created_at == "1970-01-01T00:00:00Z"
    assert first.scorecard.to_dict() == second.scorecard.to_dict()
    assert first.scenario_results == second.scenario_results
