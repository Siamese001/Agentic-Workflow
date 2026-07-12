from __future__ import annotations

import json
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_apps_eval_projection_is_advisory_until_independent_binding(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
            emit_l6_handoff=True,
        )
    )
    bridge = json.loads(Path(record.artifact_paths["l6_shadow_bridge"]).read_text(encoding="utf-8"))
    alignment = json.loads(Path(record.artifact_paths["l6_apps_eval_alignment"]).read_text(encoding="utf-8"))
    parity = json.loads(Path(record.artifact_paths["l6_apps_eval_grain_parity"]).read_text(encoding="utf-8"))

    assert bridge["projection_consistency_only"] is True
    assert bridge["independent_observation_required_for_bound_proof"] is True
    assert bridge["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert alignment["apps_eval_rows_bound"] is False
    assert alignment["projection_consistency_only"] is True
    assert parity["apps_eval_rows_bound"] is False
    assert parity["projection_consistency_only"] is True
    assert parity["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
