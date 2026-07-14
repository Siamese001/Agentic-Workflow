from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime import post_x3_completion as subject

_X2_DIGEST = "sha256:" + hashlib.sha256(b"X2").hexdigest()
_CONTRACT_DIGEST = "sha256:" + "c" * 64
_SNAPSHOT_DIGEST = "sha256:" + "d" * 64
_RUNTIME_EXHAUST_DIGEST = "sha256:" + "e" * 64


def _canonical_identity() -> dict[str, str]:
    return {
        "producer_app_id": "apps_research",
        "consumer_app_id": "apps_rg",
        "parent_run_id": "run-1",
        "child_run_id": "research-run-1",
        "request_id": "req-1",
        "trace_root": "trace-1",
        "tenant_id": "tenant-1",
        "target_company": "Anthropic",
        "target_role": "Applied AI Manager",
        "jd_sha256": "sha256:" + "1" * 64,
        "brief_sha256": "sha256:" + "2" * 64,
        "policy_hash": "sha256:" + "3" * 64,
        "blueprint_hash": "sha256:" + "4" * 64,
        "schema_version": "apps_research_rg_run_identity.v1",
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _row() -> dict[str, object]:
    return {
        "run_id": "eval-1",
        "runtime_exhaust_bundle_id": "reb-headline",
        "row_id": "row-headline-x2",
        "microstep_id": "headline.X2.gates.pass",
        "stage_id": "X2",
        "component_id": "apps_rg.generated_lane",
        "subcomponent_id": "lane_x2_deterministic_gates",
        "lane_id": "headline",
        "gate_id": "x2_gates_pass",
        "artifact_role": "lane_x2_gate_outputs",
        "artifact_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_digest": _X2_DIGEST,
        "parent_run_id": "run-1",
        "child_run_id": "lane-run-headline",
        "section_attempt_id": "headline-attempt-1",
        "eval_record_id": "eval-1",
        "snapshot_digest": _SNAPSHOT_DIGEST,
        "microstep_contract_digest": _CONTRACT_DIGEST,
        "registry_digest": _CONTRACT_DIGEST,
        "verdict": "PASS",
        "required": True,
        "severity": "BLOCK",
        "decisive_reason": "x2 gates passed",
    }


def _seed_product(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "outputs" / "generated_resume.json",
        {"schema_version": "master_resume_v2.16", "sections": {"summary": {"text": "ok"}}},
    )
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


def _seed_section_l6(tmp_path: Path) -> None:
    lane_run = tmp_path / "lanes" / "headline"
    source_path = lane_run / "x2_gate_outputs.json"
    observation = {
        **_row(),
        "record_type": "L6MicrostepObservation",
        "apps_eval_row_id": "",
        "runtime_exhaust_bundle_id": "reb-headline",
        "source_ref": "lanes/headline/x2_gate_outputs.json",
        "artifact_digest": _X2_DIGEST,
        "observed_status": "OBSERVED",
        "eval_verdict_seen": "NOT_RUN",
        "shadow_classification": "NORMAL",
        "root_cause_candidate": "UNKNOWN_ROOT_CAUSE",
        "future_run_recommendation": "retain",
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
        "orphan_observation": False,
    }
    lane_run.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(b"X2")
    (lane_run / "l6_microstep_observations.jsonl").write_text(
        json.dumps(observation, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    package_path = lane_run / "l6_v40_shadow_eval_package.json"
    _write_json(
        package_path,
        {
            "schema_version": "apps_rg.l6_v40_shadow_eval.v2",
            "section_id": "headline",
            "parent_run_id": "run-1",
            "child_run_id": "lane-run-headline",
            "section_attempt_id": "headline-attempt-1",
            "runtime_exhaust_bundle_id": "reb-headline",
            "runtime_exhaust_bundle_digest": _RUNTIME_EXHAUST_DIGEST,
            "microstep_contract_digest": _CONTRACT_DIGEST,
            "registry_digest": _CONTRACT_DIGEST,
            "l6_microstep_observations_ref": "l6_microstep_observations.jsonl",
            "l6_observability_closure_receipt_ref": "l6_observability_closure_receipt.json",
            "current_run_mutation_assertion": False,
            "direct_l4_write_assertion": False,
            "future_run_only_assertion": True,
        },
    )
    refs = {
        "l6_microstep_observations": "lanes/headline/l6_microstep_observations.jsonl",
        "l6_v40_shadow_eval_package": "lanes/headline/l6_v40_shadow_eval_package.json",
    }
    digests = {
        "l6_microstep_observations": "sha256:"
        + hashlib.sha256((lane_run / "l6_microstep_observations.jsonl").read_bytes()).hexdigest(),
        "l6_v40_shadow_eval_package": "sha256:"
        + hashlib.sha256(package_path.read_bytes()).hexdigest(),
    }
    checks = {"sealed_artifacts_present": True}
    closure_seed = {
        "runtime_exhaust_bundle_id": "reb-headline",
        "runtime_exhaust_bundle_digest": _RUNTIME_EXHAUST_DIGEST,
        "parent_run_id": "run-1",
        "child_run_id": "lane-run-headline",
        "section_attempt_id": "headline-attempt-1",
        "microstep_contract_digest": _CONTRACT_DIGEST,
        "registry_digest": _CONTRACT_DIGEST,
        "checks": checks,
        "artifact_digests": digests,
    }
    closure_digest = "sha256:" + hashlib.sha256(
        json.dumps(closure_seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    _write_json(
        lane_run / "l6_observability_closure_receipt.json",
        {
            "schema_version": "apps_rg.l6_observability_closure_receipt.v2",
            "runtime_exhaust_bundle_id": "reb-headline",
            "runtime_exhaust_bundle_digest": _RUNTIME_EXHAUST_DIGEST,
            "parent_run_id": "run-1",
            "child_run_id": "lane-run-headline",
            "section_attempt_id": "headline-attempt-1",
            "microstep_contract_digest": _CONTRACT_DIGEST,
            "registry_digest": _CONTRACT_DIGEST,
            "observability_closure_status": "PASS",
            "closure_status": "PASS",
            "checks": checks,
            "refs": refs,
            "artifact_digests": digests,
            "closure_digest": closure_digest,
        },
    )


def _eval_record(tmp_path: Path, *, coverage_complete: bool = True) -> SimpleNamespace:
    eval_dir = tmp_path / "apps_eval" / "run"
    eval_record = eval_dir / "eval_record.json"
    bridge = eval_dir / "l6_shadow_bridge.json"
    scorecard_rows = eval_dir / "scorecard_rows.jsonl"
    _write_json(eval_record, {"record_id": "eval-1"})
    _write_json(
        bridge,
        {
            "runtime_exhaust_bundle_id": "reb-eval-1",
            "evidence_class": "CONTRACT_ONLY_ADVISORY",
            "future_run_only": True,
            "current_run_mutated": False,
        },
    )
    scorecard_rows.parent.mkdir(parents=True, exist_ok=True)
    scorecard_rows.write_text(json.dumps(_row(), sort_keys=True) + "\n", encoding="utf-8")
    return SimpleNamespace(
        record_id="eval-1",
        snapshot_digest=_SNAPSHOT_DIGEST,
        registry_digest=_CONTRACT_DIGEST,
        artifact_paths={
            "eval_record": eval_record.as_posix(),
            "l6_shadow_bridge": bridge.as_posix(),
            "scorecard_rows": scorecard_rows.as_posix(),
            "coverage_matrix": (eval_dir / "coverage_matrix.csv").as_posix(),
        },
        scorecard=SimpleNamespace(
            coverage_summary={
                "coverage_complete": coverage_complete,
                "release_blocked": not coverage_complete,
                "passed_required": 1 if coverage_complete else 0,
                "required_microsteps": 1,
            },
            score=1.0 if coverage_complete else 0.0,
            verdict="pass" if coverage_complete else "fail",
            scorecard_rows=[_row()],
        ),
    )


def _install_fakes(tmp_path: Path, monkeypatch, events: list[str], *, coverage_complete: bool) -> None:
    monkeypatch.setattr(
        subject,
        "evaluate_apps_rg_full_success_eligibility",
        lambda **kwargs: (True, []),
    )
    monkeypatch.setattr(
        subject,
        "_build_commit_packet",
        lambda **kwargs: (
            SimpleNamespace(commit_request_id="cr-1"),
            [SimpleNamespace(state_diff_id="sd-1")],
            SimpleNamespace(rollback_plan_id="rp-1"),
            SimpleNamespace(refresh_plan_id="rfp-1"),
        ),
    )

    validation = SimpleNamespace(
        uwg_validation_receipt_id="uvr-1",
        validation_status="PASS",
    )
    commit_receipt = SimpleNamespace(
        commit_receipt_id="ucr-1",
        uwg_validation_receipt_ref="uvr-1",
    )

    class Gateway:
        def commit(self, **kwargs):
            events.append("uwg")
            return commit_receipt, None, []

        def get_validation_receipt(self, ref):
            return validation

    monkeypatch.setattr(subject, "get_default_gateway", lambda: Gateway())

    def fake_write_uwg(**kwargs):
        path = tmp_path / "uwg" / "uwg_commit_receipt.json"
        _write_json(path, {"commit_status": "COMMITTED", "commit_receipt_id": "ucr-1"})
        return {"uwg_commit_receipt": "uwg/uwg_commit_receipt.json"}

    monkeypatch.setattr(subject, "_write_uwg_artifacts", fake_write_uwg)

    def fake_eval(**kwargs):
        events.append("eval")
        return _eval_record(tmp_path, coverage_complete=coverage_complete)

    monkeypatch.setattr(subject, "_run_current_eval", fake_eval)
    monkeypatch.setattr(
        subject,
        "_complete_fact_vector_writeback_after_x3",
        lambda **kwargs: {"status": "EMPTY", "reason": "none", "promotions": []},
    )
    monkeypatch.setattr(subject, "_bind_completion_artifacts", lambda **kwargs: None)


def test_uwg_closes_before_apps_eval_and_l6(tmp_path: Path, monkeypatch) -> None:
    _seed_product(tmp_path)
    _seed_section_l6(tmp_path)
    events: list[str] = []
    _install_fakes(tmp_path, monkeypatch, events, coverage_complete=True)

    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={
            "x3_disposition": "X3D",
            "run_id": "run-1",
            "request_id": "req-1",
            "canonical_run_identity": _canonical_identity(),
        },
    )

    assert events == ["uwg", "eval"]
    assert result["status"] == "PASS"
    assert result["product_authorized"] is True
    assert result["pipeline_complete"] is True
    assert result["observability_repair_required"] is False
    assert result["durable_promotion_committed"] is True
    assert result["authority_order"]["uwg_closed_before_l6"] is True
    assert result["authority_order"]["l6_influenced_current_uwg_decision"] is False
    assert result["l6_shadow"]["alignment_source"] == "independent_persisted_observations"
    assert result["l6_shadow"]["apps_eval_rows_bound"] is True
    assert result["l6_shadow"]["evidence_class"] == "APPS_EVAL_BOUND_PROOF"
    assert result["l6_shadow"]["grain_parity_status"] == "PASS"
    assert (tmp_path / subject.POST_X3_AUTHORITY_ORDER_RECEIPT).is_file()
    assert (tmp_path / result["l6_shadow"]["l6_section_apps_eval_bindings_ref"]).is_file()


def test_post_boundary_eval_failure_does_not_veto_current_uwg(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _seed_product(tmp_path)
    _seed_section_l6(tmp_path)
    events: list[str] = []
    _install_fakes(tmp_path, monkeypatch, events, coverage_complete=False)

    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={
            "x3_disposition": "X3D",
            "run_id": "run-1",
            "request_id": "req-1",
            "canonical_run_identity": _canonical_identity(),
        },
    )

    assert events == ["uwg", "eval"]
    assert result["completed"] is True
    assert result["status"] == "PASS_WITH_POST_BOUNDARY_GAPS"
    assert result["product_authorized"] is True
    assert result["pipeline_complete"] is False
    assert result["observability_repair_required"] is True
    assert result["failure_stage"] == "apps_eval_post_boundary"
    assert result["durable_promotion_committed"] is True
    assert result["authority_order"]["apps_eval_influenced_current_uwg_decision"] is False
    assert result["l6_shadow"]["current_run_mutated"] is False


def test_post_boundary_exception_is_durable_reconciliation_not_revocation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _seed_product(tmp_path)
    _seed_section_l6(tmp_path)
    events: list[str] = []
    _install_fakes(tmp_path, monkeypatch, events, coverage_complete=True)

    def _raise_after_uwg(**kwargs):
        events.append("eval_exception")
        raise RuntimeError("post-boundary evaluator unavailable")

    monkeypatch.setattr(subject, "_run_current_eval", _raise_after_uwg)
    result = subject.complete_apps_rg_post_x3(
        artifact_dir=tmp_path,
        result={
            "x3_disposition": "X3D",
            "run_id": "run-1",
            "request_id": "req-1",
            "canonical_run_identity": _canonical_identity(),
        },
    )

    assert events == ["uwg", "eval_exception"]
    assert result["product_authorized"] is True
    assert result["pipeline_complete"] is False
    assert result["observability_repair_required"] is True
    assert result["failure_stage"] == "post_boundary_reconciliation"
    persisted = json.loads(
        (tmp_path / subject.POST_X3_COMPLETION_RECEIPT).read_text(encoding="utf-8")
    )
    assert persisted["product_authorized"] is True
    assert persisted["observability_repair_required"] is True


def test_legacy_package_is_advisory_not_bound_proof(tmp_path: Path) -> None:
    lane_run = tmp_path / "lanes" / "headline"
    _write_json(
        lane_run / "l6_shadow_eval_package.json",
        {
            "schema_version": "apps_rg.l6_shadow_eval_package.v1",
            "current_run_mutated": False,
        },
    )
    eval_record = _eval_record(tmp_path)
    result = subject._emit_l6_section_apps_eval_bindings(
        artifact_dir=tmp_path,
        eval_record=eval_record,
    )
    payload = json.loads(
        (tmp_path / result["l6_section_apps_eval_bindings_ref"]).read_text(encoding="utf-8")
    )
    headline = payload["bindings"][0]
    assert headline["binding_status"] == "LEGACY_PACKAGE_ADVISORY"
    assert headline["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert payload["summary"]["apps_eval_rows_bound"] is False


def test_latest_pointer_cannot_supply_certification_package(tmp_path: Path) -> None:
    stale = tmp_path / "stale" / "headline"
    _write_json(
        stale / "l6_v40_shadow_eval_package.json",
        {"schema_version": "apps_rg.l6_v40_shadow_eval.v2"},
    )
    _write_json(
        tmp_path / "modular_r4" / "sections" / "headline" / "latest_successful_real_run.json",
        {"run_dir": stale.as_posix()},
    )
    result = subject._emit_l6_section_apps_eval_bindings(
        artifact_dir=tmp_path,
        eval_record=_eval_record(tmp_path),
    )
    payload = json.loads(
        (tmp_path / result["l6_section_apps_eval_bindings_ref"]).read_text(encoding="utf-8")
    )
    assert payload["bindings"][0]["binding_status"] == "MISSING_PACKAGE"
    assert payload["summary"]["apps_eval_rows_bound"] is False


def test_closure_byte_tamper_fails_binding(tmp_path: Path) -> None:
    _seed_section_l6(tmp_path)
    (tmp_path / "lanes" / "headline" / "l6_microstep_observations.jsonl").write_text(
        "{}\n", encoding="utf-8"
    )
    result = subject._emit_l6_section_apps_eval_bindings(
        artifact_dir=tmp_path,
        eval_record=_eval_record(tmp_path),
    )
    payload = json.loads(
        (tmp_path / result["l6_section_apps_eval_bindings_ref"]).read_text(encoding="utf-8")
    )
    binding = payload["bindings"][0]
    assert binding["binding_status"] == "PARITY_FAIL"
    assert any("closure_artifact_digest_mismatch" in gap for gap in binding["proof_gaps"])
