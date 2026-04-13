"""Tests for heal-classifier training pipeline and artifact packager.

Coverage:
  - Artifact structure: all required files present after pack()
  - model_version_hash: 16 hex chars, deterministic from artifact files
  - Feature schema: feature_order matches ClassifierFeatures field declaration order
  - Metadata consistency: row counts match split sizes
  - Calibration + OOD metadata emitted with required fields
"""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tools.heal_classifier.constants import (
    ARTIFACT_FILES,
    FEATURE_ORDER,
    HASH_INPUT_FILES,
    REPAIR_OUTCOME_CLASSES,
)
from tools.heal_classifier.dataset import apply_exclusions, deduplicate, make_split
from tools.heal_classifier.packager import ArtifactPackager, compute_model_version_hash
from tools.heal_classifier.trainer import HealClassifierTrainer, TrainerConfig

# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

_RNG = np.random.default_rng(42)


def _make_synthetic_df(n: int = 600, seed: int = 42) -> pd.DataFrame:
    """Generate a minimal but complete synthetic training dataset.

    All rows pass all exclusion rules so the full set is available for splitting.
    Class balance: 4 failure_class × 4 repair_outcome, each represented.
    """
    rng = np.random.default_rng(seed)

    # Ensure every repair_outcome class is represented (at least n//4 each)
    outcomes = np.tile(REPAIR_OUTCOME_CLASSES, n // 4 + 1)[:n]
    rng.shuffle(outcomes)

    return pd.DataFrame(
        {
            "run_id": [f"run-{i}" for i in range(n)],
            "signal_hash": [f"sig-{i}" for i in range(n)],
            "failure_class": rng.integers(0, 4, size=n),       # 0–3, no UNKNOWN
            "retry_count": rng.integers(0, 5, size=n),
            "error_code_hash": rng.integers(0, 2**16, size=n).astype(int),
            "lineage_hash_prefix": rng.integers(0, 2**16, size=n).astype(int),
            "budget_remaining": rng.uniform(0.0, 0.9, size=n),  # not sentinel 1.0
            "source_layer_id": rng.integers(0, 100, size=n).astype(int),
            "repair_outcome": outcomes,
            "ood_flag": [False] * n,
            "source": ["ML_CLASSIFIER"] * n,
            "divergence_flag": [True] * n,
            "run_clock": np.arange(n, dtype=float),
        }
    )


def _fast_config() -> TrainerConfig:
    """Minimal config for fast test training (no quality guarantees)."""
    return TrainerConfig(
        n_estimators=10,
        max_depth=2,
        learning_rate=0.1,
        subsample=1.0,
        min_samples_leaf=1,
        random_state=0,
    )


@pytest.fixture(scope="module")
def packed_artifact(tmp_path_factory: pytest.TempPathFactory) -> dict:
    """Run the full training + packaging pipeline once per module."""
    tmp = tmp_path_factory.mktemp("artifact")
    df = _make_synthetic_df()
    split = make_split(df)

    trainer = HealClassifierTrainer(_fast_config())
    result = trainer.train(
        split.X_train,
        split.y_train,
        split.X_calib,
        split.y_calib,
        split.X_val,
        split.y_val,
        list(split.label_encoder.classes_),
        failure_class_train=split.failure_class_train,
        failure_class_val=split.failure_class_val,
    )

    packager = ArtifactPackager()
    meta = packager.pack(
        result,
        tmp,
        window_start_run_clock=0.0,
        window_end_run_clock=float(len(df)),
        total_rows_before_filter=len(df),
        inference_latency_us=50.0,
        rows_per_failure_class={"0": 150, "1": 150, "2": 150, "3": 150},
        rows_per_repair_outcome={"HEALED_LOCAL": 150, "HEALED_LLM": 150,
                                 "HEALED_HITL": 150, "FAILED": 150},
    )

    return {
        "artifact_dir": tmp,
        "meta": meta,
        "result": result,
        "split": split,
        "n_train": result.n_train,
        "n_calib": result.n_calib,
        "n_val": result.n_val,
    }


# ---------------------------------------------------------------------------
# TestArtifactStructure
# ---------------------------------------------------------------------------

class TestArtifactStructure:
    def test_all_required_files_present(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        for fname in ARTIFACT_FILES:
            assert (artifact_dir / fname).exists(), f"Missing: {fname}"

    def test_model_pkl_is_loadable(self, packed_artifact: dict) -> None:
        path = packed_artifact["artifact_dir"] / "model.pkl"
        with path.open("rb") as fh:
            model = pickle.load(fh)
        assert hasattr(model, "predict_proba")

    def test_ood_detector_pkl_is_loadable(self, packed_artifact: dict) -> None:
        path = packed_artifact["artifact_dir"] / "ood_detector.pkl"
        with path.open("rb") as fh:
            detector = pickle.load(fh)
        assert hasattr(detector, "decision_function")

    def test_json_files_are_valid_json(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        for fname in ARTIFACT_FILES:
            if fname.endswith(".json"):
                content = (artifact_dir / fname).read_text(encoding="utf-8")
                json.loads(content)  # raises if invalid


# ---------------------------------------------------------------------------
# TestModelVersionHash
# ---------------------------------------------------------------------------

class TestModelVersionHash:
    def test_hash_is_16_hex_chars(self, packed_artifact: dict) -> None:
        mvh: str = packed_artifact["meta"].model_version_hash
        assert len(mvh) == 16
        int(mvh, 16)  # raises ValueError if not hex

    def test_hash_file_matches_computed(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        stored = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
        recomputed = compute_model_version_hash(artifact_dir)
        assert stored == recomputed

    def test_hash_derives_from_correct_inputs(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        content = b"".join(
            (artifact_dir / f).read_bytes() for f in HASH_INPUT_FILES
        )
        expected = hashlib.sha256(content).hexdigest()[:16]
        stored = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
        assert stored == expected

    def test_hash_changes_when_feature_schema_changes(
        self, packed_artifact: dict, tmp_path: Path
    ) -> None:
        """Mutating feature_schema.json must produce a different hash."""
        artifact_dir: Path = packed_artifact["artifact_dir"]
        import shutil

        alt_dir = tmp_path / "alt_artifact"
        shutil.copytree(artifact_dir, alt_dir)

        schema = json.loads((alt_dir / "feature_schema.json").read_text(encoding="utf-8"))
        schema["schema_version"] = "MUTATED"
        (alt_dir / "feature_schema.json").write_text(
            json.dumps(schema, sort_keys=True), encoding="utf-8"
        )

        original_hash = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()
        mutated_hash = compute_model_version_hash(alt_dir)
        assert mutated_hash != original_hash

    def test_hash_is_not_stub_hash(self, packed_artifact: dict) -> None:
        from agentic_core.L2_execution.healers.heal_classifier_model import _StubHealClassifier

        mvh: str = packed_artifact["meta"].model_version_hash
        assert mvh != _StubHealClassifier.STUB_HASH


# ---------------------------------------------------------------------------
# TestFeatureSchemaContract
# ---------------------------------------------------------------------------

class TestFeatureSchemaContract:
    def test_feature_order_matches_classifier_features(
        self, packed_artifact: dict
    ) -> None:
        from agentic_core.L2_execution.healers.heal_classifier_model import ClassifierFeatures

        expected = list(ClassifierFeatures.__dataclass_fields__.keys())
        artifact_dir: Path = packed_artifact["artifact_dir"]
        schema = json.loads(
            (artifact_dir / "feature_schema.json").read_text(encoding="utf-8")
        )
        assert schema["feature_order"] == expected

    def test_feature_order_matches_constants(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        schema = json.loads(
            (artifact_dir / "feature_schema.json").read_text(encoding="utf-8")
        )
        assert schema["feature_order"] == FEATURE_ORDER

    def test_schema_version_present(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        schema = json.loads(
            (artifact_dir / "feature_schema.json").read_text(encoding="utf-8")
        )
        assert "schema_version" in schema
        assert schema["schema_version"] == "1.0"

    def test_label_classes_present_and_sorted(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        schema = json.loads(
            (artifact_dir / "feature_schema.json").read_text(encoding="utf-8")
        )
        assert "label_classes" in schema
        # Label classes should match REPAIR_OUTCOME_CLASSES (sorted by LabelEncoder)
        assert set(schema["label_classes"]) == set(REPAIR_OUTCOME_CLASSES)


# ---------------------------------------------------------------------------
# TestMetadataConsistency
# ---------------------------------------------------------------------------

class TestMetadataConsistency:
    def test_row_counts_sum_correctly(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        meta = json.loads(
            (artifact_dir / "training_meta.json").read_text(encoding="utf-8")
        )
        total = meta["total_rows_after_filter"]
        assert total == meta["n_train"] + meta["n_calib"] + meta["n_val"]

    def test_row_counts_match_training_result(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        meta = json.loads(
            (artifact_dir / "training_meta.json").read_text(encoding="utf-8")
        )
        assert meta["n_train"] == packed_artifact["n_train"]
        assert meta["n_calib"] == packed_artifact["n_calib"]
        assert meta["n_val"] == packed_artifact["n_val"]

    def test_model_config_fields_present(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        meta = json.loads(
            (artifact_dir / "training_meta.json").read_text(encoding="utf-8")
        )
        required = {
            "n_estimators", "max_depth", "learning_rate",
            "subsample", "min_samples_leaf", "random_state",
        }
        assert required.issubset(set(meta["model_config"].keys()))

    def test_artifact_version_is_v1(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        meta = json.loads(
            (artifact_dir / "training_meta.json").read_text(encoding="utf-8")
        )
        assert meta["artifact_version"] == "v1"


# ---------------------------------------------------------------------------
# TestCalibrationAndOodMeta
# ---------------------------------------------------------------------------

class TestCalibrationAndOodMeta:
    def test_calibration_meta_required_fields(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        calib = json.loads(
            (artifact_dir / "calibration_meta.json").read_text(encoding="utf-8")
        )
        required = {"ece", "macro_f1", "macro_auroc", "method", "n_calib",
                    "per_class_f1", "per_failure_class_f1", "classification_report"}
        assert required.issubset(set(calib.keys()))

    def test_calibration_method_is_isotonic(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        calib = json.loads(
            (artifact_dir / "calibration_meta.json").read_text(encoding="utf-8")
        )
        assert calib["method"] == "isotonic"

    def test_ece_is_non_negative(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        calib = json.loads(
            (artifact_dir / "calibration_meta.json").read_text(encoding="utf-8")
        )
        assert calib["ece"] >= 0.0

    def test_ood_meta_required_fields(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        ood = json.loads(
            (artifact_dir / "ood_meta.json").read_text(encoding="utf-8")
        )
        required = {"fpr_train", "method", "nu", "kernel", "threshold",
                    "sentinel_budget_remaining", "sentinel_failure_class_unknown_index"}
        assert required.issubset(set(ood.keys()))

    def test_ood_method_is_svm(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        ood = json.loads(
            (artifact_dir / "ood_meta.json").read_text(encoding="utf-8")
        )
        assert ood["method"] == "OneClassSVM"

    def test_ood_sentinel_values_correct(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        ood = json.loads(
            (artifact_dir / "ood_meta.json").read_text(encoding="utf-8")
        )
        assert ood["sentinel_budget_remaining"] == 1.0
        assert ood["sentinel_failure_class_unknown_index"] == 4

    def test_hash_manifest_covers_model_pkl(self, packed_artifact: dict) -> None:
        artifact_dir: Path = packed_artifact["artifact_dir"]
        manifest = json.loads(
            (artifact_dir / "hash_manifest.json").read_text(encoding="utf-8")
        )
        assert "model.pkl" in manifest
        assert len(manifest["model.pkl"]) == 64  # SHA-256 hex = 64 chars


# ---------------------------------------------------------------------------
# TestExclusionRules
# ---------------------------------------------------------------------------

class TestExclusionRules:
    def test_ood_flag_rows_excluded(self) -> None:
        df = _make_synthetic_df(100)
        df.loc[:9, "ood_flag"] = True
        included, excluded = apply_exclusions(df)
        assert len(excluded) >= 10
        assert (excluded["exclusion_reason"] == "ood_flag").sum() >= 10

    def test_unknown_failure_class_excluded(self) -> None:
        df = _make_synthetic_df(100)
        df.loc[:4, "failure_class"] = 4  # UNKNOWN
        included, excluded = apply_exclusions(df)
        reasons = excluded["exclusion_reason"]
        assert (reasons == "unknown_failure_class").sum() >= 5

    def test_budget_sentinel_excluded(self) -> None:
        df = _make_synthetic_df(100)
        df.loc[:4, "budget_remaining"] = 1.0
        included, excluded = apply_exclusions(df)
        reasons = excluded["exclusion_reason"]
        assert (reasons == "budget_sentinel").sum() >= 5

    def test_heuristic_fallback_no_divergence_excluded(self) -> None:
        df = _make_synthetic_df(100)
        df.loc[:4, "source"] = "HEURISTIC_FALLBACK"
        df.loc[:4, "divergence_flag"] = False
        included, excluded = apply_exclusions(df)
        reasons = excluded["exclusion_reason"]
        assert (reasons == "heuristic_fallback_no_divergence").sum() >= 5

    def test_clean_rows_not_excluded(self) -> None:
        df = _make_synthetic_df(100)
        included, excluded = apply_exclusions(df)
        assert len(included) == 100
        assert len(excluded) == 0

    def test_deduplication_keeps_first(self) -> None:
        df = _make_synthetic_df(50)
        df.loc[10:14, "signal_hash"] = "sig-0"  # duplicate of row 0
        df.loc[10:14, "run_id"] = "run-0"
        deduped = deduplicate(df)
        # Each (run_id, signal_hash) pair appears once
        pairs = deduped.set_index(["run_id", "signal_hash"])
        assert pairs.index.is_unique
