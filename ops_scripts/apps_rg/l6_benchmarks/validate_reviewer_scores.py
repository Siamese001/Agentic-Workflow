#!/usr/bin/env python3
"""Structural validation of reviewer score files (no kappa / Spearman)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    ALLOWED_CONFIDENCE,
    ALLOWED_REVIEWER_ROLES,
    REASON_CODE_OPTIONS,
    load_json,
    write_json_report,
)

KNOWN_REASON_CODES = set(REASON_CODE_OPTIONS)


def _validate_entry(entry: dict, packet_ids: set[str], index: int) -> list[str]:
    errors: list[str] = []
    bid = entry.get("benchmark_id")
    if not bid:
        errors.append(f"entries[{index}]: missing benchmark_id")
    elif bid not in packet_ids:
        errors.append(f"entries[{index}]: benchmark_id {bid!r} not in packet")

    role = entry.get("reviewer_role")
    if role is not None and role not in ALLOWED_REVIEWER_ROLES:
        errors.append(f"entries[{index}]: invalid reviewer_role {role!r}")

    conf = entry.get("reviewer_confidence")
    if conf is not None and conf not in ALLOWED_CONFIDENCE:
        errors.append(f"entries[{index}]: invalid reviewer_confidence {conf!r}")

    dims = entry.get("dimension_scores")
    if dims is not None:
        if not isinstance(dims, dict):
            errors.append(f"entries[{index}]: dimension_scores must be object")
        else:
            for dim, score in dims.items():
                if score is not None and not (isinstance(score, int) and 1 <= score <= 5):
                    errors.append(
                        f"entries[{index}]: dimension_scores.{dim} must be null or int 1-5"
                    )

    codes = entry.get("reason_codes")
    if codes is not None:
        if not isinstance(codes, list):
            errors.append(f"entries[{index}]: reason_codes must be array")
        else:
            for code in codes:
                if code not in KNOWN_REASON_CODES:
                    errors.append(f"entries[{index}]: unknown reason_code {code!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate reviewer score file structure.")
    parser.add_argument("--scores", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    scores_doc = load_json(Path(args.scores))
    packet_doc = load_json(Path(args.packet))

    if scores_doc.get("placeholder") is not True:
        return _fail_report(
            Path(args.out),
            ["scores file must set placeholder=true for dry-run"],
        )

    packet_ids = {p.get("benchmark_id") for p in packet_doc.get("packets", [])}
    packet_ids.discard(None)

    entries = scores_doc.get("entries", scores_doc.get("scores", []))
    if not isinstance(entries, list):
        return _fail_report(Path(args.out), ["entries/scores must be a list"])

    all_errors: list[str] = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            all_errors.append(f"entries[{i}]: must be object")
            continue
        for dim, score in (entry.get("dimension_scores") or {}).items():
            if score is not None:
                all_errors.append(
                    f"entries[{i}]: fabricated label: dimension_scores.{dim} must be null in placeholder"
                )
        all_errors.extend(_validate_entry(entry, packet_ids, i))

    status = "PASS" if not all_errors else "FAIL"
    report = {
        "tool": "validate_reviewer_scores",
        "status": status,
        "dry_run": True,
        "proof_eligible": False,
        "placeholder_only": True,
        "cohen_kappa_computed": False,
        "spearman_computed": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores_path": str(Path(args.scores).as_posix()),
        "packet_path": str(Path(args.packet).as_posix()),
        "entry_count": len(entries),
        "errors": all_errors,
    }
    write_json_report(Path(args.out), report)
    return 0 if status == "PASS" else 1


def _fail_report(out: Path, errors: list[str]) -> int:
    write_json_report(
        out,
        {
            "tool": "validate_reviewer_scores",
            "status": "FAIL",
            "errors": errors,
        },
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
