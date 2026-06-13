from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps_eval.contracts import EvalRequest
from apps_eval.registry import load_suites_registry
from apps_eval.runner.core import run_eval


def test_holdout_suites_are_empty_and_release_gated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    suites = load_suites_registry()
    holdouts = {key: value for key, value in suites.items() if value["split"] == "holdout"}
    assert set(holdouts) == {"apps_rg.holdout.resume_generation", "apps_lic.holdout.outreach_message"}
    assert all(value["scenarios"] == [] for value in holdouts.values())
    monkeypatch.delenv("APPS_EVAL_RELEASE_GATE", raising=False)
    with pytest.raises(PermissionError):
        run_eval(
            EvalRequest(
                suite_id="apps_rg.holdout.resume_generation",
                mode="snapshot",
                deterministic_only=True,
                out_dir=str(tmp_path),
            )
        )
