from __future__ import annotations

import json
from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval
from apps_rg.runtime.spine.l6_shadow_eval_runner import run_l6_v40_shadow_eval_for_section

from tests.l6_observability.test_runtime_exhaust_v40_adapter import _seed_artifacts


def test_l6_v40_apps_rg_and_apps_eval_bridge_e2e(tmp_path: Path) -> None:
    apps_rg_dir = tmp_path / "apps_rg"
    apps_rg_dir.mkdir()
    _seed_artifacts(apps_rg_dir)

    rg_outputs = run_l6_v40_shadow_eval_for_section(
        apps_rg_dir,
        section_id="summary",
        repo_root=tmp_path,
        l5_certification_ref="l5-cert-ref:e2e",
    )
    rg_package = json.loads(rg_outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8"))

    eval_record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path / "apps_eval"),
            emit_l6_handoff=True,
        )
    )
    eval_bridge = json.loads(Path(eval_record.artifact_paths["l6_shadow_bridge"]).read_text(encoding="utf-8"))

    assert rg_package["g28_audit_completeness"]["verdict"] == "PASS"
    assert rg_package["g29_learning_firewall"]["verdict"] == "PASS"
    assert eval_bridge["g28_audit_completeness"]["verdict"] == "PASS"
    assert eval_bridge["g29_learning_firewall"]["verdict"] == "PASS"
