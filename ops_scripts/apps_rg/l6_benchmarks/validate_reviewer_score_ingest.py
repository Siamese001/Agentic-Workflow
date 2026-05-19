#!/usr/bin/env python3
"""Structural validation of dual-reviewer score ingest files (no kappa / Spearman)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    ALLOWED_CONFIDENCE,
    ALLOWED_REVIEWER_ROLES,
    REASON_CODE_OPTIONS,
    SCORING_DIMENSIONS_BY_GROUP,
    load_json,
    write_json_report,
)

KNOWN_REASON_CODES = set(REASON_CODE_OPTIONS)
REQUIRED_REVIEWER_SLOTS = ("reviewer_1", "reviewer_2")


def _expected_dimensions(packet_row: dict) -> list[str]:
    dims = list(packet_row.get("scoring_dimensions") or [])
    if dims:
        return dims
    group = packet_row.get("section_group")
    return list(SCORING_DIMENSIONS_BY_GROUP.get(group or "", []))


def _count_non_null_scores(scores_doc: dict) -> int:
    count = 0
    for sample in scores_doc.get("samples", []):
        if not isinstance(sample, dict):
            continue
        entries = sample.get("reviewer_entries") or {}
        for slot in REQUIRED_REVIEWER_SLOTS:
            entry = entries.get(slot) or {}
            for score in (entry.get("scores") or {}).values():
                if score is not None:
                    count += 1
    return count


def _validate_reviewer_entry(
    entry: dict,
    *,
    expected_dims: list[str],
    sample_bid: str,
    slot: str,
    placeholder_mode: bool,
) -> list[str]:
    errors: list[str] = []
    prefix = f"{sample_bid}.{slot}"

    role = entry.get("reviewer_role")
    if role is not None and role not in ALLOWED_REVIEWER_ROLES:
        errors.append(f"{prefix}: invalid reviewer_role {role!r}")

    conf = entry.get("reviewer_confidence")
    if conf is not None and conf not in ALLOWED_CONFIDENCE:
        errors.append(f"{prefix}: invalid reviewer_confidence {conf!r}")

    scores = entry.get("scores")
    if not isinstance(scores, dict):
        errors.append(f"{prefix}: scores must be object")
        return errors

    expected_set = set(expected_dims)
    score_keys = set(scores.keys())
    if score_keys != expected_set:
        missing = expected_set - score_keys
        extra = score_keys - expected_set
        if missing:
            errors.append(f"{prefix}: scores missing dimensions {sorted(missing)}")
        if extra:
            errors.append(f"{prefix}: scores extra dimensions {sorted(extra)}")

    for dim, score in scores.items():
        if score is None:
            continue
        if placeholder_mode:
            errors.append(f"{prefix}: placeholder mode forbids non-null score for {dim}")
        elif not (isinstance(score, int) and 1 <= score <= 5):
            errors.append(f"{prefix}: scores.{dim} must be int 1-5 or null")

    codes = entry.get("reason_codes")
    if codes is not None:
        if not isinstance(codes, list):
            errors.append(f"{prefix}: reason_codes must be array")
        else:
            for code in codes:
                if code not in KNOWN_REASON_CODES:
                    errors.append(f"{prefix}: unknown reason_code {code!r}")

    return errors


def _validate_sample(
    sample: dict,
    *,
    packet_by_id: dict[str, dict],
    placeholder_mode: bool,
    index: int,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(sample, dict):
        return [f"samples[{index}]: must be object"]

    bid = sample.get("benchmark_id")
    if not bid:
        errors.append(f"samples[{index}]: missing benchmark_id")
        return errors

    packet_row = packet_by_id.get(bid)
    if packet_row is None:
        errors.append(f"samples[{index}]: benchmark_id {bid!r} not in reviewer packet")
        return errors

    expected_dims = _expected_dimensions(packet_row)
    sample_dims = list(sample.get("scoring_dimensions") or [])
    if sample_dims != expected_dims:
        errors.append(
            f"samples[{index}]: scoring_dimensions must match packet for {bid!r}"
        )
    group = packet_row.get("section_group") or ""
    canonical = SCORING_DIMENSIONS_BY_GROUP.get(group, [])
    if canonical and set(expected_dims) != set(canonical):
        errors.append(
            f"samples[{index}]: packet dimensions diverge from section_group {group!r} canonical"
        )

    entries = sample.get("reviewer_entries")
    if not isinstance(entries, dict):
        errors.append(f"samples[{index}]: reviewer_entries must be object")
        return errors

    for slot in REQUIRED_REVIEWER_SLOTS:
        if slot not in entries:
            errors.append(f"samples[{index}]: missing reviewer slot {slot!r}")
            continue
        entry = entries[slot]
        if not isinstance(entry, dict):
            errors.append(f"samples[{index}].{slot}: must be object")
            continue
        errors.extend(
            _validate_reviewer_entry(
                entry,
                expected_dims=expected_dims,
                sample_bid=bid,
                slot=slot,
                placeholder_mode=placeholder_mode,
            )
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate reviewer score ingest structure.")
    parser.add_argument("--reviewer-packet", required=True)
    parser.add_argument("--scores", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--placeholder-mode",
        action="store_true",
        help="Require all dimension scores to be null (no fabricated labels).",
    )
    args = parser.parse_args(argv)

    packet_doc = load_json(Path(args.reviewer_packet))
    scores_doc = load_json(Path(args.scores))

    packets = packet_doc.get("packets", [])
    if not packets:
        report = {
            "tool": "validate_reviewer_score_ingest",
            "status": "BLOCKED",
            "errors": ["reviewer packet is empty"],
        }
        write_json_report(Path(args.out), report)
        return 2

    packet_by_id = {p["benchmark_id"]: p for p in packets if isinstance(p, dict) and p.get("benchmark_id")}

    samples = scores_doc.get("samples", [])
    if not isinstance(samples, list):
        write_json_report(
            Path(args.out),
            {
                "tool": "validate_reviewer_score_ingest",
                "status": "FAIL",
                "errors": ["samples must be a list"],
            },
        )
        return 1

    placeholder_mode = args.placeholder_mode or scores_doc.get("placeholder") is True
    all_errors: list[str] = []

    packet_ids = set(packet_by_id.keys())
    sample_ids = {s.get("benchmark_id") for s in samples if isinstance(s, dict)}
    sample_ids.discard(None)
    missing = sorted(packet_ids - sample_ids)
    extra = sorted(sample_ids - packet_ids)
    if missing:
        all_errors.append(f"missing benchmark_ids in scores file: {missing}")
    if extra:
        all_errors.append(f"unknown benchmark_ids in scores file: {extra}")

    for i, sample in enumerate(samples):
        all_errors.extend(
            _validate_sample(
                sample,
                packet_by_id=packet_by_id,
                placeholder_mode=placeholder_mode,
                index=i,
            )
        )

    non_null_scores = _count_non_null_scores(scores_doc)
    human_labels_collected = non_null_scores > 0

    status = "PASS" if not all_errors else "FAIL"
    report = {
        "tool": "validate_reviewer_score_ingest",
        "status": status,
        "dry_run": True,
        "proof_eligible": False,
        "placeholder_mode": placeholder_mode,
        "placeholder_scores_only": placeholder_mode and non_null_scores == 0,
        "human_labels_collected": human_labels_collected,
        "cohen_kappa_computed": False,
        "spearman_computed": False,
        "calibration_computed": False,
        "judges_promoted": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reviewer_packet_path": str(Path(args.reviewer_packet).as_posix()),
        "scores_path": str(Path(args.scores).as_posix()),
        "reviewer_packet_count": len(packet_by_id),
        "sample_count": len(samples),
        "non_null_scores": non_null_scores,
        "errors": all_errors,
    }
    write_json_report(Path(args.out), report)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
