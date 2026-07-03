from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime import post_x3_completion as subject


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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
        _write_json(eval_record, {"record_id": "eval-1"})
        _write_json(l6_bridge, {"future_run_only": True, "current_run_mutated": False})
        scorecard = SimpleNamespace(
            coverage_summary={
                "coverage_complete": True,
                "release_blocked": False,
                "passed_required": 134,
                "required_microsteps": 134,
            },
            score=1.0,
            verdict="pass",
        )
        return SimpleNamespace(
            record_id="eval-1",
            artifact_paths={
                "eval_record": eval_record.as_posix(),
                "l6_shadow_bridge": l6_bridge.as_posix(),
                "scorecard_rows": (eval_dir / "scorecard_rows.jsonl").as_posix(),
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
    assert commit_receipt["commit_status"] == "COMMITTED"
    assert commit_receipt["output_hash"] == expected_hash
    assert (tmp_path / "commit_request.json").is_file()
    assert (tmp_path / "uwg_validation_receipt.json").is_file()
