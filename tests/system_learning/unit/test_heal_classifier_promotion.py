"""Tests for eval report generator and promotion packet builder.

Coverage:
  - Threshold checks: pass/fail for each metric individually
  - Report files: all three .md files + promotion_record.json + uwg_proposal.json generated
  - Promotion packet: all required files present after build()
  - Shadow invariant: proposed_activation_mode is always "shadow"
  - Verify function: correctly detects missing files and invalid activation mode
"""

from __future__ import annotations

import json
import pickle
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from tools.heal_classifier.constants import (
    ARTIFACT_FILES,
    PROMOTION_PACKET_FILES,
)
from tools.heal_classifier.packager import PackageMetadata
from tools.heal_classifier.promotion_packet import (
    PromotionPacketBuilder,
    verify_promotion_packet,
)
from tools.heal_classifier.report_generator import (
    EvalReportGenerator,
    ThresholdCheckResult,
    check_promotion_thresholds,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _passing_thresholds() -> dict:
    return dict(
        macro_f1=0.75,
        per_failure_class_f1={
            "DRIFT_DETECTION": 0.70,
            "IMPORT_BOUNDARY": 0.70,
            "LAYER_INVERSION": 0.70,
            "SSOT_DRIFT": 0.70,
        },
        ece=0.03,
        macro_auroc=0.85,
        fallback_rate=0.10,
        inference_latency_us=200.0,
        ood_fpr_train=0.005,
    )


def _minimal_artifact_dir(tmp_path: Path) -> Path:
    """Write minimal artifact files so the packager/report can read them."""
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()

    # model.pkl — tiny object
    with (artifact_dir / "model.pkl").open("wb") as fh:
        pickle.dump({"stub": True}, fh)

    # ood_detector.pkl
    with (artifact_dir / "ood_detector.pkl").open("wb") as fh:
        pickle.dump({"ood_stub": True}, fh)

    # feature_schema.json
    from tools.heal_classifier.constants import FEATURE_ORDER, FAILURE_CLASS_NAMES, REPAIR_OUTCOME_CLASSES
    feature_schema = {
        "schema_version": "1.0",
        "feature_order": FEATURE_ORDER,
        "feature_types": {f: "float" for f in FEATURE_ORDER},
        "value_ranges": {},
        "label_classes": REPAIR_OUTCOME_CLASSES,
        "failure_class_names": FAILURE_CLASS_NAMES,
    }
    (artifact_dir / "feature_schema.json").write_text(
        json.dumps(feature_schema, sort_keys=True), encoding="utf-8"
    )

    # Derive model_version_hash and hash_manifest
    import hashlib
    content = b"".join(
        (artifact_dir / f).read_bytes()
        for f in ["model.pkl", "ood_detector.pkl", "feature_schema.json"]
    )
    mvh = hashlib.sha256(content).hexdigest()[:16]

    # calibration_meta.json
    t = _passing_thresholds()
    calib_meta = {
        "ece": t["ece"],
        "macro_f1": t["macro_f1"],
        "macro_auroc": t["macro_auroc"],
        "method": "isotonic",
        "n_calib": 60,
        "per_class_f1": {k: 0.75 for k in REPAIR_OUTCOME_CLASSES},
        "per_failure_class_f1": t["per_failure_class_f1"],
        "fallback_rate": t["fallback_rate"],
        "classification_report": "mock report",
    }
    (artifact_dir / "calibration_meta.json").write_text(
        json.dumps(calib_meta, sort_keys=True), encoding="utf-8"
    )

    # training_meta.json
    training_meta = {
        "artifact_version": "v1",
        "inference_latency_us_median": t["inference_latency_us"],
        "model_config": {"n_estimators": 10, "max_depth": 2, "learning_rate": 0.1,
                         "subsample": 1.0, "min_samples_leaf": 1, "random_state": 0},
        "n_calib": 60,
        "n_train": 400,
        "n_val": 120,
        "rows_per_failure_class": {},
        "rows_per_repair_outcome": {},
        "total_rows_after_filter": 580,
        "total_rows_before_filter": 600,
        "window_end_run_clock": 600.0,
        "window_start_run_clock": 0.0,
    }
    (artifact_dir / "training_meta.json").write_text(
        json.dumps(training_meta, sort_keys=True), encoding="utf-8"
    )

    # ood_meta.json
    ood_meta = {
        "fpr_train": t["ood_fpr_train"],
        "gamma": "scale",
        "kernel": "rbf",
        "method": "OneClassSVM",
        "nu": 0.01,
        "sentinel_budget_remaining": 1.0,
        "sentinel_failure_class_unknown_index": 4,
        "threshold": -0.5,
    }
    (artifact_dir / "ood_meta.json").write_text(
        json.dumps(ood_meta, sort_keys=True), encoding="utf-8"
    )

    # hash_manifest.json + model_version_hash
    skip = {"hash_manifest.json", "model_version_hash"}
    manifest = {
        fname: hashlib.sha256((artifact_dir / fname).read_bytes()).hexdigest()
        for fname in ARTIFACT_FILES
        if fname not in skip and (artifact_dir / fname).exists()
    }
    (artifact_dir / "hash_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8"
    )
    (artifact_dir / "model_version_hash").write_text(mvh, encoding="utf-8")

    return artifact_dir


def _make_artifact_meta(artifact_dir: Path) -> PackageMetadata:
    mvh = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
    manifest = json.loads(
        (artifact_dir / "hash_manifest.json").read_text(encoding="utf-8")
    )
    return PackageMetadata(
        artifact_dir=artifact_dir,
        model_version_hash=mvh,
        hash_manifest=manifest,
    )


# ---------------------------------------------------------------------------
# TestThresholdChecks
# ---------------------------------------------------------------------------

class TestThresholdChecks:
    def test_all_passing_thresholds_yields_passed_true(self) -> None:
        result = check_promotion_thresholds(**_passing_thresholds())
        assert result.passed is True
        assert result.failing_checks == []

    def test_low_macro_f1_fails(self) -> None:
        kw = _passing_thresholds()
        kw["macro_f1"] = 0.50
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "macro_f1" in result.failing_checks

    def test_high_ece_fails(self) -> None:
        kw = _passing_thresholds()
        kw["ece"] = 0.10
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "ece" in result.failing_checks

    def test_low_auroc_fails(self) -> None:
        kw = _passing_thresholds()
        kw["macro_auroc"] = 0.60
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "macro_auroc" in result.failing_checks

    def test_high_fallback_rate_fails(self) -> None:
        kw = _passing_thresholds()
        kw["fallback_rate"] = 0.50
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "fallback_rate" in result.failing_checks

    def test_exceeded_latency_fails(self) -> None:
        kw = _passing_thresholds()
        kw["inference_latency_us"] = 1500.0
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "inference_latency" in result.failing_checks

    def test_high_ood_fpr_fails(self) -> None:
        kw = _passing_thresholds()
        kw["ood_fpr_train"] = 0.05
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert "ood_fpr" in result.failing_checks

    def test_per_failure_class_f1_below_threshold_fails(self) -> None:
        kw = _passing_thresholds()
        kw["per_failure_class_f1"]["DRIFT_DETECTION"] = 0.40
        result = check_promotion_thresholds(**kw)
        assert result.passed is False
        assert any("DRIFT_DETECTION" in k for k in result.failing_checks)

    def test_all_four_failure_class_keys_present_in_checks(self) -> None:
        result = check_promotion_thresholds(**_passing_thresholds())
        for fc in ("DRIFT_DETECTION", "IMPORT_BOUNDARY", "LAYER_INVERSION", "SSOT_DRIFT"):
            assert any(fc in k for k in result.checks)

    def test_details_dict_populated_for_every_check(self) -> None:
        result = check_promotion_thresholds(**_passing_thresholds())
        for check_key in result.checks:
            assert check_key in result.details
            assert len(result.details[check_key]) > 0


# ---------------------------------------------------------------------------
# TestReportGeneration
# ---------------------------------------------------------------------------

class TestReportGeneration:
    def test_all_report_files_generated(self, tmp_path: Path) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())

        EvalReportGenerator().generate(
            packet_dir, artifact_dir, threshold_result
        )

        assert (packet_dir / "offline_eval_report.md").exists()
        assert (packet_dir / "shadow_divergence_report.md").exists()
        assert (packet_dir / "hitl_cohort_review.md").exists()

    def test_offline_eval_report_contains_verdict(self, tmp_path: Path) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)

        content = (packet_dir / "offline_eval_report.md").read_text(encoding="utf-8")
        assert "PASS" in content

    def test_offline_eval_report_shows_fail_on_failing_thresholds(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        kw = _passing_thresholds()
        kw["macro_f1"] = 0.50
        threshold_result = check_promotion_thresholds(**kw)
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)

        content = (packet_dir / "offline_eval_report.md").read_text(encoding="utf-8")
        assert "FAIL" in content

    def test_shadow_report_shows_placeholder_when_no_data(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)

        content = (packet_dir / "shadow_divergence_report.md").read_text(encoding="utf-8")
        assert "shadow_rows_analyzed" in content

    def test_shadow_report_shows_data_when_provided(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        shadow_data = {
            "shadow_rows_analyzed": 512,
            "divergence_rate": 0.15,
            "divergence_by_failure_class": {"DRIFT_DETECTION": 0.12},
        }
        EvalReportGenerator().generate(
            packet_dir, artifact_dir, threshold_result, shadow_data=shadow_data
        )
        content = (packet_dir / "shadow_divergence_report.md").read_text(encoding="utf-8")
        assert "512" in content
        assert "0.15" in content


# ---------------------------------------------------------------------------
# TestPromotionPacketContents
# ---------------------------------------------------------------------------

class TestPromotionPacketContents:
    def test_all_required_top_level_items_present(self, tmp_path: Path) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        for item in PROMOTION_PACKET_FILES:
            assert (packet_dir / item).exists(), f"Missing: {item}"

    def test_artifact_subdir_contains_all_artifact_files(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        for fname in ARTIFACT_FILES:
            assert (packet_dir / "artifact" / fname).exists(), f"Missing artifact/{fname}"

    def test_promotion_record_json_is_valid(self, tmp_path: Path) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        result = PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        record = json.loads(
            (packet_dir / "promotion_record.json").read_text(encoding="utf-8")
        )
        required = {
            "model_version_hash", "artifact_window_start", "artifact_window_end",
            "offline_eval_passed", "proposed_activation_mode", "promotion_author",
            "shadow_divergence_rate", "shadow_rows_analyzed", "uwg_packet_id",
        }
        assert required.issubset(set(record.keys()))

    def test_uwg_proposal_has_binding_instruction(self, tmp_path: Path) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        proposal = json.loads(
            (packet_dir / "uwg_proposal.json").read_text(encoding="utf-8")
        )
        assert "binding_instruction" in proposal
        assert "EnvelopeBuilder" in proposal["binding_instruction"]

    def test_uwg_proposal_requires_second_proposal_for_active_mode(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        proposal = json.loads(
            (packet_dir / "uwg_proposal.json").read_text(encoding="utf-8")
        )
        assert proposal["requires_second_proposal_for_active_mode"] is True


# ---------------------------------------------------------------------------
# TestShadowModeInvariant
# ---------------------------------------------------------------------------

class TestShadowModeInvariant:
    def test_proposed_activation_mode_is_always_shadow(
        self, tmp_path: Path
    ) -> None:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        result = PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        assert result.activation_mode == "shadow"
        record = json.loads(
            (packet_dir / "promotion_record.json").read_text(encoding="utf-8")
        )
        assert record["proposed_activation_mode"] == "shadow"
        proposal = json.loads(
            (packet_dir / "uwg_proposal.json").read_text(encoding="utf-8")
        )
        assert proposal["proposed_activation_mode"] == "shadow"

    def test_shadow_mode_invariant_survives_failing_thresholds(
        self, tmp_path: Path
    ) -> None:
        """proposed_activation_mode must be 'shadow' even when thresholds fail."""
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        kw = _passing_thresholds()
        kw["macro_f1"] = 0.30  # deliberate failure
        threshold_result = check_promotion_thresholds(**kw)
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        result = PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )

        assert result.activation_mode == "shadow"
        record = json.loads(
            (packet_dir / "promotion_record.json").read_text(encoding="utf-8")
        )
        assert record["proposed_activation_mode"] == "shadow"
        assert record["offline_eval_passed"] is False


# ---------------------------------------------------------------------------
# TestVerifyPromotionPacket
# ---------------------------------------------------------------------------

class TestVerifyPromotionPacket:
    def _build_complete_packet(self, tmp_path: Path) -> Path:
        artifact_dir = _minimal_artifact_dir(tmp_path)
        packet_dir = tmp_path / "packet"
        threshold_result = check_promotion_thresholds(**_passing_thresholds())
        EvalReportGenerator().generate(packet_dir, artifact_dir, threshold_result)
        PromotionPacketBuilder().build(
            artifact_meta=_make_artifact_meta(artifact_dir),
            threshold_result=threshold_result,
            packet_dir=packet_dir,
        )
        return packet_dir

    def test_complete_packet_passes_verification(self, tmp_path: Path) -> None:
        packet_dir = self._build_complete_packet(tmp_path)
        complete, issues = verify_promotion_packet(packet_dir)
        assert complete is True
        assert issues == []

    def test_missing_report_file_fails_verification(self, tmp_path: Path) -> None:
        packet_dir = self._build_complete_packet(tmp_path)
        (packet_dir / "offline_eval_report.md").unlink()
        complete, issues = verify_promotion_packet(packet_dir)
        assert complete is False
        assert any("offline_eval_report.md" in i for i in issues)

    def test_missing_artifact_file_fails_verification(self, tmp_path: Path) -> None:
        packet_dir = self._build_complete_packet(tmp_path)
        (packet_dir / "artifact" / "model.pkl").unlink()
        complete, issues = verify_promotion_packet(packet_dir)
        assert complete is False
        assert any("model.pkl" in i for i in issues)

    def test_wrong_activation_mode_fails_verification(
        self, tmp_path: Path
    ) -> None:
        packet_dir = self._build_complete_packet(tmp_path)
        record_path = packet_dir / "promotion_record.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["proposed_activation_mode"] = "active"  # tampered
        record_path.write_text(
            json.dumps(record, sort_keys=True), encoding="utf-8"
        )
        complete, issues = verify_promotion_packet(packet_dir)
        assert complete is False
        assert any("proposed_activation_mode" in i for i in issues)
