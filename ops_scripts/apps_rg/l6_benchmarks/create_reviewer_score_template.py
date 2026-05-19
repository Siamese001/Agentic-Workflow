#!/usr/bin/env python3
"""Build reviewer score template + null-only placeholder from a reviewer packet export."""

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

REQUIRED_REVIEWER_SLOTS = ("reviewer_1", "reviewer_2")


def _null_reviewer_entry(dimensions: list[str]) -> dict:
    return {
        "reviewer_role": None,
        "reviewer_id": None,
        "reviewer_confidence": None,
        "scores": {dim: None for dim in dimensions},
        "reason_codes": [],
        "notes": None,
        "reviewed_at": None,
    }


def _sample_from_packet(packet_row: dict) -> dict:
    section_group = packet_row.get("section_group")
    dims = list(packet_row.get("scoring_dimensions") or [])
    if not dims and section_group:
        dims = list(SCORING_DIMENSIONS_BY_GROUP.get(section_group, []))
    return {
        "benchmark_id": packet_row["benchmark_id"],
        "section_id": packet_row.get("section_id"),
        "section_group": section_group,
        "role_anchor": packet_row.get("role_anchor"),
        "scoring_dimensions": dims,
        "reviewer_entries": {
            slot: _null_reviewer_entry(dims) for slot in REQUIRED_REVIEWER_SLOTS
        },
    }


def build_template_doc(packet_doc: dict, *, source_path: Path) -> dict:
    packets = packet_doc.get("packets", [])
    if not isinstance(packets, list) or not packets:
        raise ValueError("reviewer packet has no packets")

    samples = [_sample_from_packet(p) for p in packets if isinstance(p, dict)]
    return {
        "schema_version": "1.0.0",
        "wave": "w8b",
        "kind": "reviewer_score_template",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_reviewer_packet": str(source_path.as_posix()),
        "proof_eligible": False,
        "human_labels_collected": False,
        "allowed_reviewer_roles": sorted(ALLOWED_REVIEWER_ROLES),
        "allowed_confidence": sorted(ALLOWED_CONFIDENCE),
        "allowed_reason_codes": list(REASON_CODE_OPTIONS),
        "required_reviewer_slots": list(REQUIRED_REVIEWER_SLOTS),
        "instructions_ref": "artifacts/apps_rg/benchmarks/reviewer_scoring_guide.md",
        "sample_count": len(samples),
        "samples": samples,
    }


def build_placeholder_doc(template_doc: dict) -> dict:
    return {
        **template_doc,
        "kind": "reviewer_scores_placeholder",
        "placeholder": True,
        "placeholder_scores_only": True,
        "human_labels_collected": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create reviewer score template from packet.")
    parser.add_argument("--reviewer-packet", required=True)
    parser.add_argument("--out", required=True, help="Template JSON path")
    parser.add_argument("--placeholder-out", required=True, help="Null-only placeholder path")
    args = parser.parse_args(argv)

    packet_path = Path(args.reviewer_packet)
    packet_doc = load_json(packet_path)
    template = build_template_doc(packet_doc, source_path=packet_path)

    out_path = Path(args.out)
    placeholder_path = Path(args.placeholder_out)
    write_json_report(out_path, template)
    write_json_report(placeholder_path, build_placeholder_doc(template))

    print(
        f"created template samples={template['sample_count']} -> {out_path.as_posix()}",
        file=sys.stderr,
    )
    print(
        f"created placeholder -> {placeholder_path.as_posix()}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
