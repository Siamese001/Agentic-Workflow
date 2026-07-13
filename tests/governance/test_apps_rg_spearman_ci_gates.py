from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import yaml

from agentic_core.L6_observability.shadow_eval._digest import compute_digest
from agentic_core.L6_observability.shadow_eval.spearman_calibration import (
    CalibrationSample,
    SpearmanCalibrationProfile,
    compute_spearman_calibration,
)
from ops_scripts.ci._apps_rg_spearman_gate_common import finish
from ops_scripts.ci.check_apps_rg_spearman_calibration import validate_calibration
from ops_scripts.ci.check_apps_rg_spearman_dataset import validate_dataset
from ops_scripts.ci.check_apps_rg_spearman_identity import validate_identity
from ops_scripts.ci.check_apps_rg_spearman_l6_placement import validate_placement

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_active_apps_rg_identity_gate_is_clean():
    assert validate_identity() == []


def test_apps_rg_human_holdout_is_required(tmp_path: Path):
    missing = tmp_path / "missing-human-holdout.jsonl"
    findings = validate_dataset(dataset_path=missing)
    assert any("human semantic holdout is missing" in finding for finding in findings)


def test_holdout_digest_must_bind_candidate_text(tmp_path: Path):
    profile = {
        "task_class": "resume_generation",
        "judge_id": "rg::executive_positioning_judge::v1",
        "rubric_hash": "rubric-hash",
        "rubric_version": "1.0.0",
        "dataset_id": "dataset-1",
        "dataset_version": "v1",
        "semantic_alignment": {"minimum_samples": 4},
    }
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")
    rows = []
    for index in range(4):
        candidate = f"candidate {index}"
        rows.append(
            {
                "sample_id": f"sample-{index}",
                "dataset_id": "dataset-1",
                "dataset_version": "v1",
                "task_class": profile["task_class"],
                "judge_id": profile["judge_id"],
                "rubric_hash": profile["rubric_hash"],
                "rubric_version": profile["rubric_version"],
                "candidate_text": candidate,
                "target_role": "role",
                "target_level": "level",
                "target_company": "company",
                "human_score": index + 1,
                "human_rank_band": f"band-{index}",
                "reviewer_refs": [f"reviewer-a-{index}", f"reviewer-b-{index}"],
                "adjudication_ref": "",
                "label_policy": "two-reviewer-v1",
                "label_source": "human_semantic_review",
                "split": "holdout",
                "tags": ["HUMAN_SEMANTIC_RELEASE_GATE"],
                "content_digest": hashlib.sha256(candidate.encode()).hexdigest(),
                "created_at": "2026-07-13T12:00:00+00:00",
            }
        )
    rows[0]["content_digest"] = "0" * 64
    dataset = tmp_path / "holdout.jsonl"
    dataset.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    findings = validate_dataset(
        dataset_path=dataset,
        profile_path=profile_path,
        fixtures_root=tmp_path / "other-fixtures",
    )
    assert "row 1 content_digest does not bind candidate_text" in findings


def test_calibration_gate_recomputes_numeric_thresholds(tmp_path: Path):
    profile = SpearmanCalibrationProfile(
        app_id="apps_rg",
        task_class="resume_generation",
        judge_id="rg::executive_positioning_judge::v1",
        judge_version="v1",
        rubric_hash="rubric-hash",
        rubric_version="1.0.0",
        provider_profile_ref="local_qwen_generator",
        minimum_samples=4,
        minimum_spearman_rho=0.8,
        maximum_p_value=0.05,
    )
    samples = tuple(
        CalibrationSample(
            sample_id=f"sample-{index}",
            dataset_id="dataset-1",
            dataset_version="v1",
            human_score=float(index),
            judge_score=float(index),
            label_source="human_semantic_review",
            reviewer_refs=(f"reviewer-a-{index}", f"reviewer-b-{index}"),
            content_digest=f"{index:064x}",
            task_class=profile.task_class,
            judge_id=profile.judge_id,
            rubric_hash=profile.rubric_hash,
            rubric_version=profile.rubric_version,
        )
        for index in range(4)
    )
    result = asdict(compute_spearman_calibration(samples, profile))
    result["spearman_rho"] = 0.1
    result["threshold_met"] = True
    result["deterministic_digest"] = compute_digest(result)
    artifact_path = tmp_path / "calibration.json"
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": "apps-rg-spearman-calibration/v1",
                "app_id": "apps_rg",
                "result": result,
            }
        ),
        encoding="utf-8",
    )
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(
        yaml.safe_dump(
            {
                "app_id": profile.app_id,
                "judge_id": profile.judge_id,
                "judge_version": profile.judge_version,
                "rubric_hash": profile.rubric_hash,
                "rubric_version": profile.rubric_version,
                "provider_profile_ref": profile.provider_profile_ref,
                "dataset_id": "dataset-1",
                "dataset_version": "v1",
                "semantic_alignment": {
                    "minimum_samples": profile.minimum_samples,
                    "minimum_spearman_rho": profile.minimum_spearman_rho,
                    "maximum_p_value": profile.maximum_p_value,
                },
            }
        ),
        encoding="utf-8",
    )
    findings = validate_calibration(
        artifact_path=artifact_path,
        profile_path=profile_path,
    )
    assert "result rho is below the semantic threshold" in findings


def test_calibration_gate_preserves_nonpassing_failure_reasons(tmp_path: Path):
    profile = SpearmanCalibrationProfile(
        app_id="apps_rg",
        task_class="resume_generation",
        judge_id="rg::executive_positioning_judge::v1",
        judge_version="v1",
        rubric_hash="rubric-hash",
        rubric_version="1.0.0",
        provider_profile_ref="local_qwen_generator",
        minimum_samples=40,
        minimum_spearman_rho=0.8,
        maximum_p_value=0.05,
        dataset_id="dataset-1",
        dataset_version="v1",
    )
    result = asdict(compute_spearman_calibration((), profile))
    artifact_path = tmp_path / "calibration.json"
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": "apps-rg-spearman-calibration/v1",
                "app_id": "apps_rg",
                "result": result,
            }
        ),
        encoding="utf-8",
    )
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(
        yaml.safe_dump(
            {
                "app_id": profile.app_id,
                "judge_id": profile.judge_id,
                "judge_version": profile.judge_version,
                "rubric_hash": profile.rubric_hash,
                "rubric_version": profile.rubric_version,
                "provider_profile_ref": profile.provider_profile_ref,
                "dataset_id": profile.dataset_id,
                "dataset_version": profile.dataset_version,
                "semantic_alignment": {
                    "minimum_samples": profile.minimum_samples,
                    "minimum_spearman_rho": profile.minimum_spearman_rho,
                    "maximum_p_value": profile.maximum_p_value,
                },
            }
        ),
        encoding="utf-8",
    )

    findings = validate_calibration(
        artifact_path=artifact_path,
        profile_path=profile_path,
    )

    assert "calibration status is not PASS" in findings
    assert "passing calibration carries failure reason codes" not in findings


def test_exit_has_no_live_spearman_computation():
    assert validate_placement() == []


def test_apps_rg_spearman_gate_is_registered():
    registry = (REPO_ROOT / "ops_scripts/ci/_run_contract_gates_impl.py").read_text(encoding="utf-8")
    for gate in (
        "check_apps_rg_spearman_identity.py",
        "check_apps_rg_spearman_dataset.py",
        "check_apps_rg_spearman_calibration.py",
        "check_apps_rg_spearman_l6_placement.py",
        "check_apps_rg_spearman_promotion.py",
    ):
        assert gate in registry


def test_advisory_gate_can_be_promoted_to_fail_closed(monkeypatch):
    monkeypatch.setenv("APPS_RG_SPEARMAN_TEST_FAIL_CLOSED", "1")
    assert (
        finish(
            "RG-SPEARMAN-TEST",
            ["missing evidence"],
            fail_closed_env="APPS_RG_SPEARMAN_TEST_FAIL_CLOSED",
        )
        == 1
    )
