from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps_eval.adapters.apps_rg import normalize_existing_apps_rg_run_snapshot, run_apps_rg_live
from apps_eval.artifacts.apps_rg_resolver import resolve_apps_rg_artifact
from apps_eval.contracts import EvalRequest
from apps_eval.coverage.apps_rg import load_apps_rg_contracts
from apps_eval.tests._apps_rg_evidence import emit_verified_current_run_evidence


def test_apps_rg_live_requires_preexisting_product_run(tmp_path: Path) -> None:
    source_root = tmp_path / "run"
    with pytest.raises(ValueError, match="existing product run root"):
        run_apps_rg_live("resume_tailor_basic", {}, source_root)

    assert not source_root.exists()


def test_apps_rg_live_rejects_unsigned_status_preflight(tmp_path: Path) -> None:
    source_root = tmp_path / "run"
    source_root.mkdir()
    (source_root / "apps_rg_live_preflight.json").write_text(
        '{"status":"passed"}',
        encoding="utf-8",
    )
    before = {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in source_root.rglob("*")
        if path.is_file()
    }

    with pytest.raises(ValueError, match="product authorization seal is invalid"):
        run_apps_rg_live("resume_tailor_basic", {}, source_root)

    after = {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_apps_rg_live_normalizes_sealed_existing_run_read_only(
    monkeypatch,
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "run"
    out_dir = source_root / "outputs"
    evidence_dir = source_root / "evidence"
    out_dir.mkdir(parents=True)
    evidence_dir.mkdir()
    evidence = evidence_dir / "leadership.json"
    evidence.write_text('{"fact":"led modernization"}', encoding="utf-8")
    evidence_digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    generated = {
        "sections": {
            "summary": {"text": "Strategic technology leader for enterprise AI platforms."},
            "experience": [
                {
                    "title": "SVP Engineering",
                    "bullets": [
                        {
                            "text": "Led modernization programs.",
                            "source_ref": "evidence/leadership.json",
                            "source_digest": f"sha256:{evidence_digest}",
                        }
                    ],
                }
            ],
            "skills": {"categories": [{"name": "AI strategy"}]},
        }
    }
    (out_dir / "generated_resume.json").write_text(
        json.dumps(generated, indent=2),
        encoding="utf-8",
    )
    emit_verified_current_run_evidence(source_root, monkeypatch)
    before = {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in source_root.rglob("*")
        if path.is_file()
    }

    snapshot = run_apps_rg_live("resume_tailor_basic", {}, source_root)

    assert snapshot.x3_disposition == "X3D_ALLOW_FINISH"
    assert "resume.md" not in snapshot.artifacts
    assert "generated_resume.json" in snapshot.artifacts
    assert snapshot.output["sections"]["executive_summary"].startswith("Strategic technology")
    assert "Led modernization programs" in snapshot.output["sections"]["experience"]
    assert "AI strategy" in snapshot.output["sections"]["skills"]
    assert snapshot.provenance["evidence_refs"] == ["evidence/leadership.json"]
    assert snapshot.provenance["supported_evidence_refs"] == ["evidence/leadership.json"]
    assert snapshot.claims[0]["supported"] is True
    assert snapshot.provenance["preflight_verified"] is True
    assert snapshot.provenance["source_seal_verified"] is True
    assert snapshot.provenance["source_unchanged"] is True
    after = {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    assert after == before
    assert not (source_root / "resume.md").exists()


def test_existing_run_snapshot_indexes_modular_section_pointer_artifacts(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    (artifact_dir / "outputs").mkdir(parents=True)
    (artifact_dir / "outputs" / "generated_resume.json").write_text(
        json.dumps({"sections": {"summary": {"text": "summary"}}}),
        encoding="utf-8",
    )
    lane_root = artifact_dir / "section_attempts" / "full_resume_headline"
    lane_root.mkdir(parents=True)
    payloads = {
        "l2_output.json": {"runtime_generation_status": "REAL_LLM"},
        "runtime_payload.json": {"proof_pool_metadata": {}},
        "x2_gate_outputs.json": {"all_pass": True},
        "x1d_llm_judge_outputs.json": {"overall": "PASS"},
        "x3_disposition.json": {"x3_code": "X3D"},
        "l6_shadow_eval_package.json": {"current_run_mutated": False},
    }
    for name, payload in payloads.items():
        (lane_root / name).write_text(json.dumps(payload), encoding="utf-8")
    pointer_dir = artifact_dir / "modular_r4" / "sections" / "headline"
    pointer_dir.mkdir(parents=True)
    (pointer_dir / "latest_successful_real_run.json").write_text(
        json.dumps(
            {
                "section_id": "headline",
                "identity": {
                    "parent_run_id": "parent-1",
                    "child_run_id": "child-1",
                },
                "artifact_links": {
                    name: (lane_root / name).as_posix()
                    for name in payloads
                },
            }
        ),
        encoding="utf-8",
    )

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={
            "x3_disposition": "X3D_ALLOW_FINISH",
            "parent_run_id": "parent-1",
            "child_run_id": "child-1",
        },
        artifact_dir=artifact_dir,
    )
    resolved = resolve_apps_rg_artifact(
        snapshot=snapshot,
        role="lane_x3_disposition",
        lane_id="headline",
        artifact_contract=load_apps_rg_contracts()["artifact_contract"],
    )

    assert snapshot.artifact_index["headline:lane_l2_output"]["payload"]["runtime_generation_status"] == "REAL_LLM"
    assert resolved.artifact_ref == (lane_root / "x3_disposition.json").as_posix()
    assert resolved.payload["x3_code"] == "X3D"

    (lane_root / "x3_disposition.json").write_text(
        '{"x3_code":"X3D_ALLOW_FINISH","tampered":true}',
        encoding="utf-8",
    )
    tampered = resolve_apps_rg_artifact(
        snapshot=snapshot,
        role="lane_x3_disposition",
        lane_id="headline",
        artifact_contract=load_apps_rg_contracts()["artifact_contract"],
    )
    assert tampered.found is False
    assert tampered.failure_reason == "snapshot_artifact_index_digest_mismatch_or_missing"


def test_existing_run_snapshot_rejects_external_pointer_artifacts(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    pointer_dir = artifact_dir / "modular_r4" / "sections" / "headline"
    pointer_dir.mkdir(parents=True)
    external = tmp_path / "other_run" / "x3_disposition.json"
    external.parent.mkdir(parents=True)
    external.write_text('{"x3_code":"X3D_ALLOW_FINISH"}', encoding="utf-8")
    (pointer_dir / "latest_successful_real_run.json").write_text(
        json.dumps({"artifact_links": {"x3_disposition.json": external.as_posix()}}),
        encoding="utf-8",
    )

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={"x3_disposition": "X3D_ALLOW_FINISH"},
        artifact_dir=artifact_dir,
    )
    resolved = resolve_apps_rg_artifact(
        snapshot=snapshot,
        role="lane_x3_disposition",
        lane_id="headline",
        artifact_contract=load_apps_rg_contracts()["artifact_contract"],
    )

    assert "headline:lane_x3_disposition" not in snapshot.artifact_index
    assert resolved.found is False


def test_existing_run_snapshot_rejects_stale_contained_pointer(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    pointer_dir = artifact_dir / "modular_r4" / "sections" / "headline"
    pointer_dir.mkdir(parents=True)
    stale = artifact_dir / "attempts" / "stale" / "x3_disposition.json"
    stale.parent.mkdir(parents=True)
    stale.write_text('{"x3_code":"X3D_ALLOW_FINISH"}', encoding="utf-8")
    (pointer_dir / "latest_successful_real_run.json").write_text(
        json.dumps(
            {
                "identity": {
                    "parent_run_id": "parent-1",
                    "child_run_id": "stale-child",
                },
                "artifact_links": {"x3_disposition.json": stale.as_posix()},
            }
        ),
        encoding="utf-8",
    )

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={
            "parent_run_id": "parent-1",
            "child_run_id": "current-child",
        },
        artifact_dir=artifact_dir,
    )
    resolved = resolve_apps_rg_artifact(
        snapshot=snapshot,
        role="lane_x3_disposition",
        lane_id="headline",
        artifact_contract=load_apps_rg_contracts()["artifact_contract"],
    )

    assert "headline:lane_x3_disposition" not in snapshot.artifact_index
    assert resolved.found is False


def test_existing_run_claim_requires_contained_digest_bound_evidence(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    evidence = artifact_dir / "evidence" / "leadership.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{"fact":"led modernization"}', encoding="utf-8")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    outputs = artifact_dir / "outputs"
    outputs.mkdir(parents=True)
    (outputs / "generated_resume.json").write_text(
        json.dumps(
            {
                "sections": {
                    "experience": {
                        "text": "Led modernization.",
                        "source_ref": "evidence/leadership.json",
                        "source_digest": f"sha256:{digest}",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={"x3_disposition": "X3D_ALLOW_FINISH"},
        artifact_dir=artifact_dir,
    )

    assert snapshot.claims[0]["supported"] is True
    assert snapshot.claims[0]["containment_verified"] is True
    assert snapshot.claims[0]["digest_verified"] is True
    assert snapshot.claims[0]["evidence_digest"] == digest


def test_existing_run_claim_without_declared_digest_is_unsupported(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    evidence = artifact_dir / "evidence" / "leadership.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{"fact":"led modernization"}', encoding="utf-8")
    outputs = artifact_dir / "outputs"
    outputs.mkdir()
    (outputs / "generated_resume.json").write_text(
        json.dumps(
            {
                "sections": {
                    "experience": {
                        "text": "Led modernization.",
                        "source_ref": "evidence/leadership.json",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={},
        artifact_dir=artifact_dir,
    )

    assert snapshot.claims[0]["supported"] is False
    assert snapshot.claims[0]["digest_verified"] is False
    assert snapshot.claims[0]["source_resolution_status"] == "EXPECTED_DIGEST_MISSING"


def test_apps_rg_live_rejects_tampered_signed_preflight(
    tmp_path: Path,
    monkeypatch,
) -> None:
    artifact_dir = tmp_path / "run"
    outputs = artifact_dir / "outputs"
    outputs.mkdir(parents=True)
    (outputs / "generated_resume.json").write_text(
        '{"sections":{"summary":"verified"}}',
        encoding="utf-8",
    )
    emit_verified_current_run_evidence(artifact_dir, monkeypatch)
    continuation_path = artifact_dir / "e2e_preflight_continuation_receipt.json"
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    continuation["continuation_nonce"] = "tampered"
    continuation_path.write_text(json.dumps(continuation), encoding="utf-8")

    with pytest.raises(ValueError, match="signed preflight evidence is invalid"):
        run_apps_rg_live("current-run", {}, artifact_dir)


def test_existing_run_rejects_conflicting_source_identity(
    tmp_path: Path,
    monkeypatch,
) -> None:
    artifact_dir = tmp_path / "run"
    outputs = artifact_dir / "outputs"
    outputs.mkdir(parents=True)
    (outputs / "generated_resume.json").write_text(
        '{"sections":{"summary":"verified"}}',
        encoding="utf-8",
    )
    emit_verified_current_run_evidence(artifact_dir, monkeypatch)

    with pytest.raises(ValueError, match="apps_rg_source_identity_conflict:parent_run_id"):
        run_apps_rg_live(
            "current-run",
            {"existing_run_result": {"parent_run_id": "different-parent"}},
            artifact_dir,
        )


def test_existing_run_ignores_caller_authored_passed_preflight(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "run"
    artifact_dir.mkdir()

    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result={"x3_disposition": "X3D_ALLOW_FINISH"},
        artifact_dir=artifact_dir,
        preflight={"status": "passed", "resolved_inputs": {"invented": True}},
    )

    assert snapshot.provenance["preflight"] == "unknown"
    assert snapshot.provenance["preflight_ref"] == ""
    assert snapshot.provenance["resolved_inputs"] == {}
    assert snapshot.x3_disposition == "UNKNOWN"


def test_apps_rg_live_runner_requires_existing_sealed_source_root(tmp_path: Path) -> None:
    from apps_eval.runner import core as runner

    with pytest.raises(PermissionError, match="live_adapter is read-only"):
        runner.run_eval(
            EvalRequest(
                suite_id="apps_rg.dev.resume_generation",
                mode="live_adapter",
                deterministic_only=False,
                out_dir=str(tmp_path),
                emit_l6_handoff=True,
            )
        )
