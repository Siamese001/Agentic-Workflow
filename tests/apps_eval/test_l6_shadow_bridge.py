from __future__ import annotations

import json
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_apps_eval_l6_shadow_bridge_emitted_with_handoff(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_lic.dev.outreach_message",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
            emit_l6_handoff=True,
        )
    )

    bridge_path = Path(record.artifact_paths["l6_shadow_bridge"])
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

    assert bridge["record_id"] == record.record_id
    assert bridge["boundary_scope"] == "L6_1_2_BOUNDARY_ONLY"
    assert bridge["readiness_decision"] == "HOLD_FOR_MISSING_EVIDENCE"
    assert bridge["g28_audit_completeness"]["verdict"] == "FAIL"
    assert "l5_certification_ref" in bridge["g28_audit_completeness"]["missing_refs"]
    assert bridge["g29_learning_firewall"]["verdict"] == "PASS"
    assert bridge["current_run_mutated"] is False
    assert Path(record.artifact_paths["l6_shadow_bridge_spans"]).is_file()
