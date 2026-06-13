from __future__ import annotations

import json
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_l6_handoff_is_shape_only_and_non_mutating(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_lic.dev.outreach_message",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
            emit_l6_handoff=True,
        )
    )
    handoff_path = Path(record.artifact_paths["l6_handoff"])
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert handoff["record_id"] == record.record_id
    assert handoff["suite_id"] == "apps_lic.dev.outreach_message"
    assert handoff["current_run_mutated"] is False
    assert handoff["requested_action"] == "consume_completed_eval_record_only"
