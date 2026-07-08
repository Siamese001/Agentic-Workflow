from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime import post_x3_completion as subject


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _scorecard_row() -> dict[str, object]:
    return {
        "row_id": "row-headline-x2",
        "microstep_id": "headline.X2.gates.pass",
        "stage_id": "X2",
        "component_id": "apps_rg.section_lane",
        "subcomponent_id": "x2",
        "lane_id": "headline",
        "gate_id": "headline_x2_gates_pass",
        "artifact_role": "lane_x2_gate_outputs",
        "artifact_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_digest": "sha256:x2",
        "verdict": "PASS",
        "required": True,
        "decisive_reason": "x2 gates passed",
    }


def _seed_success_artifacts(tmp_path: Path) -> None:
    generated = {
        "schema_version": "master_resume_v2.16",
        "sections": {"summary": {"text": "Grounded executive summary."}},
        "citations": [{"source_id": "src_1"}],
    }
    _write_json(tmp_path / "outputs" / "generated_resume.json", generated)
    (tmp_path / "outputs" / "resume.docx").write_bytes(b"DOCX")
    _write_json(
        tmp_path / "apps_rg_output_manifest.json",
        {
            "schema_version": "apps_rg_output_manifest.v1",
            "generated_resume_json_relpath": "outputs/generated_resume.json",
            "apps_rg_generation_status": "REAL_RESUME",
            "full_resume_generated": True,
            "resume_shape": "REAL_RESUME",
            "docx_output_required": True,
            "resume_docx_relpath": "outputs/resume.docx",
            "docx_verified": True,
            "required_artifacts": {
                "generated_resume_json": "verified",
                "resume_docx": "verified",
                "docx_verified": True,
            },
        },
    )
    _write_json(
        tmp_path / "route_contract.json",
        {
            "payload": {
                "route_contract_id": "route-1",
                "request_id": "req-1",
                "trace_root": "trace-1",
                "policy_hash": "ph-1",
                "blueprint_hash": "bh-1",
                "replay_key": "replay-1",
            }
        },
    )
    _write_json(tmp_path / "runtime_identity_envelope.json", {"payload": {"run_id": "run-1"}})
    _write_json(tmp_path / "r4_run_manifest.json", {"run_id": "run-1", "request_id": "req-1"})
    _write_json(tmp_path / "exit_review_packet.json", {"payload": {"x3_disposition": "X3D"}})
    _write_json(tmp_path / "x3_disposition_receipt.json", {"payload": {"x3_disposition": "X3D"}})


def test_post_x3_completion_commits_generated_resume_and_binds_eval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    generated = {
        "schema_version": "master_resume_v2.16",
        "sections": {"summary": {"text": "Grounded executive summary."}},
        "citations": [{"source_id": "src_1"}],
    }
    _write_json(tmp_path / "outputs" / "generated_resume.json", generated)
    (tmp_path / "outputs" / "resume.docx").write_bytes(b"DOCX")
    _write_json(
        tmp_path / "apps_rg_output_manifest.json",
        {
            "schema_version": "apps_rg_output_manifest.v1",
            "generated_resume_json_relpath": "outputs/generated_resume.json",
            "apps_rg_generation_status": "REAL_RESUME",
            "full_resume_generated": True,
            "resume_shape": "REAL_RESUME",
            "docx_output_required": True,
            "resume_docx_relpath": "outputs/resume.docx",
            "docx_verified": True,
            "required_artifacts": {
                "generated_resume_json": "verified",
                "resume_docx": "verified",
                "docx_verified": True,
            },
        },
    )
    _write_json(
        tmp_path / "route_contract.json",
        {
            "payload": {
                "route_contract_id": "route-1",
                "request_id": "req-1",
                "trace_root": "trace-1",
                "policy_hash": "ph-1",
                "blueprint_hash": "bh-1",
                "replay_key": "replay-1",
            }
        },
    )
    _write_json(tmp_path / "runtime_identity_envelope.json", {"payload": {"run_id": "run-1"}})
    _write_json(tmp_path / "r4_run_manifest.json", {"run_id": "run-1", "request_id": "req-1"})
    _write_json(tmp_path / "exit_review_packet.json", {"payload": {"x3_disposition": "X3D"}})
    _write_json(tmp_path / "x3_disposition_receipt.json", {"payload": {"x3_disposition": "X3D"}})

    def fake_eval(**kwargs):
        eval_dir = tmp_path / "apps_eval" / "fake"
        eval_record = eval_dir / "eval_record.json"
        l6_bridge = eval_dir / "l6_shadow_bridge.json"
        scorecard_rows = eval_dir / "scorecard_rows.jsonl"
        row = _scorecard_row()
        _write_json(eval_record, {"record_id": "eval-1"})
        _write_json(
            l6_bridge,
            {
                "runtime_exhaust_bundle_id": "reb-eval-1",
                "future_run_only": True,
                "current_run_mutated": False,
            },
        )
        scorecard_rows.parent.mkdir(parents=True, exist_ok=True)
        scorecard_rows.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
        scorecard = SimpleNamespace(
            coverage_summary={
                "coverage_complete": True,
                "release_blocked": False,
                "passed_required": 134,
                "required_microsteps": 134,
            },
            score=1.0,
            verdict="pass",
            scorecard_rows=[row],
        )
        return SimpleNamespace(
            record_id="eval-1",
            artifact_paths={
                "eval_record": eval_record.as_posix(),
                "l6_shadow_bridge": l6_bridge.as_posix(),
                "scorecard_rows": scorecard_rows.as_posix(),
                "coverage_matrix": (eval_dir / "coverage_matrix.csv").as_posix(),
            },
            scorecard=scorecard,
        )

    monkeypatch.setattr(subject, "_run_current_eval", fake_eval)

    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={
            "exit_status": "success",
            "execution_status": "completed",
            "outcome_authorized": True,
            "x3_disposition": "X3D",
            "fault": "",
            "artifact_dir": str(tmp_path),
            "run_id": "run-1",
            "request_id": "req-1",
        },
        raw_request={"target_company": "Anthropic", "target_role": "Partnerships"},
    )

    expected_hash = hashlib.sha256((tmp_path / "outputs" / "generated_resume.json").read_bytes()).hexdigest()
    receipt = json.loads((tmp_path / subject.POST_X3_COMPLETION_RECEIPT).read_text(encoding="utf-8"))
    commit_receipt = json.loads((tmp_path / "uwg" / "uwg_commit_receipt.json").read_text(encoding="utf-8"))

    assert result["completed"] is True
    assert receipt["x3_to_uwg_to_eval_to_l6_completed"] is True
    assert receipt["l6_shadow"]["alignment_source"] == "apps_eval_scorecard_rows"
    assert receipt["l6_shadow"]["apps_eval_rows_bound"] is True
    assert receipt["l6_shadow"]["evidence_class"] == "APPS_EVAL_BOUND_PROOF"
    assert receipt["l6_shadow"]["grain_parity_status"] == "PASS"
    assert (tmp_path / receipt["l6_shadow"]["l6_apps_eval_grain_parity_ref"]).is_file()
    assert (tmp_path / receipt["l6_shadow"]["l6_section_apps_eval_bindings_ref"]).is_file()
    assert receipt["l6_shadow"]["l6_section_apps_eval_bindings_summary"]["apps_eval_rows_bound"] == 1
    assert commit_receipt["commit_status"] == "COMMITTED"
    assert commit_receipt["output_hash"] == expected_hash
    assert (tmp_path / "commit_request.json").is_file()
    assert (tmp_path / "uwg_validation_receipt.json").is_file()


def test_l6_section_bindings_follow_modular_section_latest_run_pointer(tmp_path: Path) -> None:
    lane_run = tmp_path / "runtime_proofs" / "full_resume_headline"
    _write_json(
        lane_run / "l6_v40_shadow_eval_package.json",
        {
            "schema_version": "apps_rg.l6_v40_shadow_eval.v1",
            "grain_parity_status": "PASS",
            "alignment_source": "apps_eval_scorecard_rows",
        },
    )
    pointer_dir = tmp_path / "modular_r4" / "sections" / "headline"
    _write_json(
        pointer_dir / "latest_successful_real_run.json",
        {
            "section_id": "headline",
            "run_dir": lane_run.as_posix(),
        },
    )
    row = _scorecard_row()
    eval_record = SimpleNamespace(
        record_id="eval-1",
        artifact_paths={"eval_record": "apps_eval/fake/eval_record.json"},
        scorecard=SimpleNamespace(scorecard_rows=[row]),
    )

    result = subject._emit_l6_section_apps_eval_bindings(
        artifact_dir=tmp_path,
        eval_record=eval_record,
    )
    payload = json.loads((tmp_path / result["l6_section_apps_eval_bindings_ref"]).read_text(encoding="utf-8"))
    headline = next(item for item in payload["bindings"] if item["section_id"] == "headline")

    assert headline["binding_status"] == "PASS"
    assert headline["l6_v40_shadow_eval_package_ref"].endswith("runtime_proofs/full_resume_headline/l6_v40_shadow_eval_package.json")
    assert payload["summary"]["sections_bound"] == 1


def test_l6_section_bindings_accept_legacy_l6_pointer_when_v40_absent(tmp_path: Path) -> None:
    lane_run = tmp_path / "runtime_proofs" / "full_resume_headline"
    _write_json(
        lane_run / "l6_shadow_eval_package.json",
        {
            "schema_version": "apps_rg.l6_shadow_eval_package.v1",
            "current_run_mutated": False,
        },
    )
    pointer_dir = tmp_path / "modular_r4" / "sections" / "headline"
    _write_json(
        pointer_dir / "latest_successful_real_run.json",
        {
            "section_id": "headline",
            "artifact_links": {
                "l6_shadow_eval_package.json": (lane_run / "l6_shadow_eval_package.json").as_posix(),
            },
        },
    )
    row = _scorecard_row()
    eval_record = SimpleNamespace(
        record_id="eval-1",
        artifact_paths={"eval_record": "apps_eval/fake/eval_record.json"},
        scorecard=SimpleNamespace(scorecard_rows=[row]),
    )

    result = subject._emit_l6_section_apps_eval_bindings(
        artifact_dir=tmp_path,
        eval_record=eval_record,
    )
    payload = json.loads((tmp_path / result["l6_section_apps_eval_bindings_ref"]).read_text(encoding="utf-8"))
    headline = next(item for item in payload["bindings"] if item["section_id"] == "headline")

    assert headline["binding_status"] == "PASS"
    assert headline["l6_package_tier"] == "legacy"
    assert headline["l6_v40_shadow_eval_package_ref"] == ""
    assert headline["l6_shadow_eval_package_ref"].endswith("runtime_proofs/full_resume_headline/l6_shadow_eval_package.json")
    assert payload["summary"]["sections_bound"] == 1


def test_post_x3_uwg_failure_emits_failure_l6_bridge(tmp_path: Path, monkeypatch) -> None:
    _seed_success_artifacts(tmp_path)

    class FakeGateway:
        def commit(self, **kwargs):
            return None, {"blocked": True, "reason": "blocked-for-test"}, []

    monkeypatch.setattr(subject, "get_default_gateway", lambda: FakeGateway())

    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={"x3_disposition": "X3D", "run_id": "run-1", "request_id": "req-1"},
    )

    assert result["failure_stage"] == "uwg_commit"
    assert result["l6_shadow"]["grain_parity_status"] == "WARN"
    assert result["l6_shadow"]["alignment_source"] == "failure_terminal_no_apps_eval_rows"
    assert result["l6_shadow"]["evidence_class"] == "FAILURE_TERMINAL_ADVISORY"
    assert (tmp_path / subject.POST_X3_FAILURE_L6_SHADOW_BRIDGE).is_file()
    assert (tmp_path / subject.POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY).is_file()


def test_post_x3_fact_vector_writeback_failure_emits_failure_l6_bridge(tmp_path: Path, monkeypatch) -> None:
    _seed_success_artifacts(tmp_path)
    monkeypatch.setattr(
        subject,
        "_complete_fact_vector_writeback_after_x3",
        lambda **kwargs: {"status": "FAIL", "reason": "fact_vector_writeback_chain_failed"},
    )

    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={"x3_disposition": "X3D", "run_id": "run-1", "request_id": "req-1"},
    )

    assert result["failure_stage"] == "fact_vector_writeback"
    assert result["l6_shadow"]["grain_parity_status"] == "WARN"
    assert result["l6_shadow"]["apps_eval_rows_bound"] is False
    assert (tmp_path / subject.POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY).is_file()
