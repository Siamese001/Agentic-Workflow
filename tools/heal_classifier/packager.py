"""Artifact packager — writes the complete versioned artifact directory."""

from __future__ import annotations

import hashlib
import json
import pickle
from dataclasses import dataclass
from pathlib import Path

from .constants import (
    ARTIFACT_FILES,
    ARTIFACT_VERSION,
    FAILURE_CLASS_NAMES,
    FEATURE_ORDER,
    HASH_INPUT_FILES,
    SCHEMA_VERSION,
)
from .trainer import TrainingResult


@dataclass
class PackageMetadata:
    artifact_dir: Path
    model_version_hash: str
    hash_manifest: dict[str, str]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_model_version_hash(artifact_dir: Path) -> str:
    """SHA-256( bytes(model.pkl) || bytes(ood_detector.pkl) || bytes(feature_schema.json) )[:16]."""
    content = b"".join((artifact_dir / fname).read_bytes() for fname in HASH_INPUT_FILES)
    return hashlib.sha256(content).hexdigest()[:16]


def compute_hash_manifest(artifact_dir: Path) -> dict[str, str]:
    """Per-file SHA-256 for all artifact files except manifest + hash files."""
    skip = {"hash_manifest.json", "model_version_hash"}
    return {
        fname: _sha256_file(artifact_dir / fname)
        for fname in ARTIFACT_FILES
        if fname not in skip and (artifact_dir / fname).exists()
    }


class ArtifactPackager:
    def pack(
        self,
        result: TrainingResult,
        output_dir: Path,
        window_start_run_clock: float = 0.0,
        window_end_run_clock: float = 0.0,
        total_rows_before_filter: int = 0,
        inference_latency_us: float = 0.0,
        rows_per_failure_class: dict[str, int] | None = None,
        rows_per_repair_outcome: dict[str, int] | None = None,
    ) -> PackageMetadata:
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. model.pkl
        with (output_dir / "model.pkl").open("wb") as fh:
            pickle.dump(result.model, fh, protocol=pickle.HIGHEST_PROTOCOL)

        # 2. ood_detector.pkl
        with (output_dir / "ood_detector.pkl").open("wb") as fh:
            pickle.dump(result.ood_detector, fh, protocol=pickle.HIGHEST_PROTOCOL)

        # 3. feature_schema.json  — sort_keys=True ensures determinism
        feature_schema = {
            "schema_version": SCHEMA_VERSION,
            "feature_order": FEATURE_ORDER,
            "feature_types": {f: "float" for f in FEATURE_ORDER},
            "value_ranges": {
                "budget_remaining": {"max": 1.0, "min": 0.0},
                "error_code_hash": {"max": 2**32 - 1, "min": 0},
                "failure_class": {"max": 3, "min": 0},
                "lineage_hash_prefix": {"max": 2**32 - 1, "min": 0},
                "retry_count": {"max": 5, "min": 0},
                "source_layer_id": {"max": 2**32 - 1, "min": 0},
            },
            "label_classes": result.label_classes,
            "failure_class_names": FAILURE_CLASS_NAMES,
        }
        (output_dir / "feature_schema.json").write_text(
            json.dumps(feature_schema, indent=2, sort_keys=True), encoding="utf-8"
        )

        # 4. calibration_meta.json
        calibration_meta = {
            "ece": result.val_metrics.ece,
            "macro_auroc": result.val_metrics.macro_auroc,
            "macro_f1": result.val_metrics.macro_f1,
            "method": "isotonic",
            "n_calib": result.n_calib,
            "per_class_f1": result.val_metrics.per_class_f1,
            "per_failure_class_f1": result.val_metrics.per_failure_class_f1,
            "classification_report": result.val_metrics.classification_report_text,
        }
        (output_dir / "calibration_meta.json").write_text(
            json.dumps(calibration_meta, indent=2, sort_keys=True), encoding="utf-8"
        )

        # 5. training_meta.json
        training_meta = {
            "artifact_version": ARTIFACT_VERSION,
            "inference_latency_us_median": inference_latency_us,
            "model_config": {
                "learning_rate": result.config.learning_rate,
                "max_depth": result.config.max_depth,
                "min_samples_leaf": result.config.min_samples_leaf,
                "n_estimators": result.config.n_estimators,
                "random_state": result.config.random_state,
                "subsample": result.config.subsample,
            },
            "n_calib": result.n_calib,
            "n_train": result.n_train,
            "n_val": result.n_val,
            "rows_per_failure_class": rows_per_failure_class or {},
            "rows_per_repair_outcome": rows_per_repair_outcome or {},
            "total_rows_after_filter": result.n_train + result.n_calib + result.n_val,
            "total_rows_before_filter": total_rows_before_filter,
            "window_end_run_clock": window_end_run_clock,
            "window_start_run_clock": window_start_run_clock,
        }
        (output_dir / "training_meta.json").write_text(
            json.dumps(training_meta, indent=2, sort_keys=True), encoding="utf-8"
        )

        # 6. ood_meta.json
        ood_meta = {
            "fpr_train": result.ood_fpr_train,
            "gamma": "scale",
            "kernel": "rbf",
            "method": "OneClassSVM",
            "nu": 0.01,
            "sentinel_budget_remaining": 1.0,
            "sentinel_failure_class_unknown_index": 4,
            "threshold": result.ood_threshold,
        }
        (output_dir / "ood_meta.json").write_text(
            json.dumps(ood_meta, indent=2, sort_keys=True), encoding="utf-8"
        )

        # 7. hash_manifest.json  — must come before model_version_hash
        manifest = compute_hash_manifest(output_dir)
        (output_dir / "hash_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )

        # 8. model_version_hash  — derived from HASH_INPUT_FILES only
        mvh = compute_model_version_hash(output_dir)
        (output_dir / "model_version_hash").write_text(mvh, encoding="utf-8")

        return PackageMetadata(
            artifact_dir=output_dir,
            model_version_hash=mvh,
            hash_manifest=manifest,
        )
