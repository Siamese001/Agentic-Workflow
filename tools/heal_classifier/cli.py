"""CLI entry point for the heal-classifier offline pipeline.

Commands:
    train   -- load dataset, train, package artifact
    report  -- generate eval reports + promotion packet from artifact
    verify  -- check promotion packet completeness
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_train(args: argparse.Namespace) -> int:
    from tools.heal_classifier.dataset import (
        apply_exclusions,
        deduplicate,
        load_dataset,
        make_split,
    )
    from tools.heal_classifier.packager import ArtifactPackager
    from tools.heal_classifier.trainer import HealClassifierTrainer, TrainerConfig

    print(f"Loading dataset: {args.dataset}")
    df = load_dataset(args.dataset)
    print(f"  Raw rows: {len(df)}")

    df, excluded = apply_exclusions(df)
    df = deduplicate(df)
    print(f"  After exclusions/dedup: {len(df)}  (excluded: {len(excluded)})")

    split = make_split(df)
    print(
        f"  Split: train={len(split.X_train)}"
        f"  calib={len(split.X_calib)}"
        f"  val={len(split.X_val)}"
    )

    trainer = HealClassifierTrainer(TrainerConfig())
    print("Training GBDT + calibration + OOD detector ...")
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

    latency_us = trainer.measure_inference_latency_us(result.model, split.X_val)
    print(f"  Val macro F1 : {result.val_metrics.macro_f1:.4f}")
    print(f"  Val ECE      : {result.val_metrics.ece:.4f}")
    print(f"  Latency (med): {latency_us:.1f} us")

    output_dir = Path(args.output_dir)
    rows_per_fc = df["failure_class"].value_counts().to_dict()
    rows_per_outcome = df["repair_outcome"].value_counts().to_dict()

    packager = ArtifactPackager()
    meta = packager.pack(
        result,
        output_dir,
        window_start_run_clock=float(df["run_clock"].min()) if "run_clock" in df.columns else 0.0,
        window_end_run_clock=float(df["run_clock"].max()) if "run_clock" in df.columns else 0.0,
        total_rows_before_filter=len(df) + len(excluded),
        inference_latency_us=latency_us,
        rows_per_failure_class={str(k): int(v) for k, v in rows_per_fc.items()},
        rows_per_repair_outcome={str(k): int(v) for k, v in rows_per_outcome.items()},
    )

    print(f"Artifact written: {output_dir}")
    print(f"model_version_hash: {meta.model_version_hash}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from tools.heal_classifier.packager import PackageMetadata, compute_model_version_hash
    from tools.heal_classifier.promotion_packet import PromotionPacketBuilder
    from tools.heal_classifier.report_generator import (
        EvalReportGenerator,
        check_promotion_thresholds,
    )

    artifact_dir = Path(args.artifact_dir)
    packet_dir = Path(args.packet_dir)

    calib_meta = json.loads((artifact_dir / "calibration_meta.json").read_text(encoding="utf-8"))
    training_meta = json.loads((artifact_dir / "training_meta.json").read_text(encoding="utf-8"))
    ood_meta = json.loads((artifact_dir / "ood_meta.json").read_text(encoding="utf-8"))
    mvh = (artifact_dir / "model_version_hash").read_text(encoding="utf-8").strip()

    threshold_result = check_promotion_thresholds(
        macro_f1=calib_meta["macro_f1"],
        per_failure_class_f1=calib_meta.get("per_failure_class_f1", {}),
        ece=calib_meta["ece"],
        macro_auroc=calib_meta["macro_auroc"],
        fallback_rate=calib_meta.get("fallback_rate", 0.0),
        inference_latency_us=training_meta.get("inference_latency_us_median", 0.0),
        ood_fpr_train=ood_meta.get("fpr_train", 0.0),
    )

    shadow_data: dict | None = None
    if getattr(args, "shadow_data", None):
        shadow_data = json.loads(Path(args.shadow_data).read_text(encoding="utf-8"))

    artifact_meta = PackageMetadata(
        artifact_dir=artifact_dir,
        model_version_hash=mvh,
        hash_manifest=json.loads(
            (artifact_dir / "hash_manifest.json").read_text(encoding="utf-8")
        ),
    )

    EvalReportGenerator().generate(
        packet_dir, artifact_dir, threshold_result, shadow_data=shadow_data
    )

    result = PromotionPacketBuilder().build(
        artifact_meta=artifact_meta,
        threshold_result=threshold_result,
        packet_dir=packet_dir,
        promotion_author=getattr(args, "author", "offline_trainer"),
    )

    verdict = "PASS" if threshold_result.passed else "FAIL"
    print(f"Promotion packet: {packet_dir}")
    print(f"Threshold verdict: {verdict}")
    print(f"Proposed activation mode: {result.activation_mode}")
    return 0 if threshold_result.passed else 1


def _cmd_verify(args: argparse.Namespace) -> int:
    from tools.heal_classifier.promotion_packet import verify_promotion_packet

    complete, issues = verify_promotion_packet(Path(args.packet_dir))
    if complete:
        print(f"Promotion packet COMPLETE: {args.packet_dir}")
        return 0
    print(f"Promotion packet INCOMPLETE: {args.packet_dir}")
    for issue in issues:
        print(f"  {issue}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Heal-classifier offline pipeline",
        prog="python -m tools.heal_classifier",
    )
    sub = parser.add_subparsers(dest="cmd")

    t = sub.add_parser("train", help="Train and package artifact")
    t.add_argument("--dataset", required=True, help="Path to labeled dataset CSV/Parquet")
    t.add_argument("--output-dir", required=True, help="Artifact output directory")

    r = sub.add_parser("report", help="Generate eval reports and promotion packet")
    r.add_argument("--artifact-dir", required=True)
    r.add_argument("--packet-dir", required=True)
    r.add_argument("--shadow-data", default=None, help="Optional shadow telemetry JSON")
    r.add_argument("--author", default="offline_trainer")

    v = sub.add_parser("verify", help="Verify promotion packet completeness")
    v.add_argument("--packet-dir", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "train":
        return _cmd_train(args)
    if args.cmd == "report":
        return _cmd_report(args)
    if args.cmd == "verify":
        return _cmd_verify(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
