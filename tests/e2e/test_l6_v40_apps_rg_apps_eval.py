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
        session_id="sess-l6-v40-e2e",
        tenant_id="tenant-l6-v40-e2e",
        l5_certification_ref="l5-cert-ref:e2e",
    )
    rg_package = json.loads(rg_outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8"))
    rg_alignment = json.loads(rg_outputs["l6_apps_eval_alignment"].read_text(encoding="utf-8"))

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
    eval_alignment = json.loads(Path(eval_record.artifact_paths["l6_apps_eval_alignment"]).read_text(encoding="utf-8"))
    eval_grain_parity = json.loads(Path(eval_record.artifact_paths["l6_apps_eval_grain_parity"]).read_text(encoding="utf-8"))

    assert rg_package["valid_v40_shadow_exhaust"] is True
    assert rg_package["g28_audit_completeness"]["verdict"] == "PASS"
    assert rg_package["g29_learning_firewall"]["verdict"] == "PASS"
    assert rg_package["current_run_mutation_assertion"] is False
    assert rg_package["current_run_x3_mutation_assertion"] is False
    assert rg_package["direct_l4_write_assertion"] is False
    assert rg_package["future_run_only_assertion"] is True
    assert rg_package["l6_microstep_observations_ref"]
    assert rg_package["l6_apps_eval_alignment_ref"]
    assert rg_package["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert rg_package["l6_trace_observability_summary_ref"]
    assert rg_package["l6_observability_closure_receipt_ref"]
    assert rg_alignment["missing_in_l6"] == []
    assert rg_alignment["authority_mismatch"] is False

    assert eval_bridge["g28_audit_completeness"]["verdict"] == "PASS"
    assert eval_bridge["g29_learning_firewall"]["verdict"] == "PASS"
    assert eval_bridge["current_run_mutated"] is False
    assert eval_bridge["direct_l4_write_attempted"] is False
    assert eval_bridge["durable_write_attempted"] is False
    assert eval_bridge["future_run_only"] is True
    assert eval_bridge["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert eval_bridge["projection_consistency_only"] is True
    assert eval_bridge["l6_microstep_artifact_refs"]["l6_apps_eval_alignment"]
    assert eval_bridge["diagnostic_artifact_refs"]["diagnostic_rows"] == eval_record.artifact_paths["diagnostic_rows"]
    assert eval_bridge["diagnostic_artifact_refs"]["diagnostic_summary"] == eval_record.artifact_paths["diagnostic_summary"]
    required_rows = [
        row for row in eval_record.scorecard.scorecard_rows if row.get("required", True)
    ]
    assert eval_alignment["rows_expected"] == len(required_rows)
    assert eval_alignment["alignment_source"] == "contract_only_pseudo_rows"
    assert eval_alignment["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert eval_alignment["projection_consistency_only"] is True
    assert eval_alignment["apps_eval_rows_bound"] is False
    assert eval_grain_parity["grain_parity_status"] == "WARN"
    assert eval_grain_parity["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert eval_grain_parity["projection_consistency_only"] is True
    assert eval_alignment["missing_in_l6"] == []
    assert eval_alignment["missing_in_apps_eval"] == []
    assert eval_grain_parity["missing_in_l6"] == []
    assert eval_grain_parity["missing_in_apps_eval"] == []
    assert eval_grain_parity["verdict_mismatches"] == []
    assert eval_grain_parity["authority_mismatch"] is False
    assert eval_alignment["authority_mismatch"] is False
