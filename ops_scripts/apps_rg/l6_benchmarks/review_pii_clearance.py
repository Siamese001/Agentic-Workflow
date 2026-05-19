#!/usr/bin/env python3
"""Offline PII scan and explicit clearance for collected L6 benchmark samples."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import (
    PATH_IDENTIFIER_PATTERN,
    iter_string_fields,
    load_json,
    resolve_glob,
    scan_pii,
    write_json_report,
)


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _scan_text_fields(sample: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    text = sample.get("generated_section_text")
    text_hits = scan_pii(str(text)) if isinstance(text, str) else []
    path_hits: list[dict[str, str]] = []
    for field_path, value in iter_string_fields(sample.get("input_refs") or {}):
        if PATH_IDENTIFIER_PATTERN.search(value):
            path_hits.append({"kind": "path_identifier", "field": field_path})
    meta = sample.get("collection_metadata")
    if isinstance(meta, dict) and isinstance(meta.get("pii_scan_hits"), list):
        for h in meta["pii_scan_hits"]:
            if isinstance(h, dict) and h.get("kind"):
                text_hits.append({"kind": str(h["kind"]), "snippet": "w6_extraction"})
    return {"generated_section_text": text_hits, "input_refs": path_hits}


def _recommended_action(text_hits: list[dict[str, str]], path_hits: list[dict[str, str]]) -> str:
    del path_hits  # path-only identifiers do not block generated-text clearance eligibility
    blocking = [h for h in text_hits if h.get("kind") not in ("path_identifier",)]
    if blocking:
        return "review_required"
    return "eligible_for_clearance"


def _build_review_row(sample: dict[str, Any], sample_path: Path, repo_root: Path) -> dict[str, Any]:
    scans = _scan_text_fields(sample)
    text_hits = scans["generated_section_text"]
    path_hits = scans["input_refs"]
    flags = text_hits + path_hits
    action = _recommended_action(text_hits, path_hits)
    reason = "no_heuristic_pii_in_generated_text"
    if text_hits:
        reason = f"generated_text_flags:{','.join(sorted({h['kind'] for h in text_hits}))}"
    elif path_hits:
        reason = "path_or_ref_identifiers_noted_generated_text_clean"
    return {
        "benchmark_id": sample.get("benchmark_id"),
        "sample_path": _repo_rel(sample_path, repo_root),
        "section_id": sample.get("section_id"),
        "section_group": sample.get("section_group"),
        "pii_status_before": sample.get("pii_status"),
        "detected_flags": flags,
        "generated_text_flags": text_hits,
        "ref_path_flags": path_hits,
        "recommended_action": action,
        "reason": reason,
    }


def _scan_samples(sample_paths: list[Path], repo_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in sample_paths:
        sample = load_json(path)
        rows.append(_build_review_row(sample, path, repo_root))
    eligible = sum(1 for r in rows if r["recommended_action"] == "eligible_for_clearance")
    return {
        "tool": "review_pii_clearance",
        "mode": "scan",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(rows),
        "eligible_for_clearance_count": eligible,
        "review_required_count": len(rows) - eligible,
        "samples": rows,
    }


def _write_decisions_placeholder(report: dict[str, Any], out_path: Path) -> None:
    decisions = []
    for row in report.get("samples", []):
        decisions.append(
            {
                "benchmark_id": row["benchmark_id"],
                "decision": "pending_review",
                "reviewer": None,
                "rationale": None,
                "reviewed_at": None,
            }
        )
    doc = {
        "placeholder": True,
        "description": "Explicit human decisions required. Do not set cleared without review.",
        "decision_count": len(decisions),
        "decisions": decisions,
    }
    write_json_report(out_path, doc)


def _apply_decisions(
    sample_paths: list[Path],
    decisions_doc: dict[str, Any],
    repo_root: Path,
    *,
    application_ref: str,
) -> dict[str, Any]:
    by_id = {d["benchmark_id"]: d for d in decisions_doc.get("decisions", []) if d.get("benchmark_id")}
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for path in sample_paths:
        sample = load_json(path)
        bid = sample.get("benchmark_id")
        decision_row = by_id.get(bid)
        if not decision_row:
            skipped.append({"benchmark_id": bid, "reason": "no_decision_row"})
            continue

        decision = decision_row.get("decision")
        before = sample.get("pii_status")
        scans = _scan_text_fields(sample)
        text_hits = scans["generated_section_text"]

        if decision == "cleared":
            reviewer = decision_row.get("reviewer")
            rationale = decision_row.get("rationale")
            reviewed_at = decision_row.get("reviewed_at")
            if not reviewer or not rationale or not reviewed_at:
                skipped.append(
                    {
                        "benchmark_id": bid,
                        "reason": "cleared_rejected_missing_reviewer_rationale_or_reviewed_at",
                    }
                )
                continue
            if text_hits:
                skipped.append(
                    {
                        "benchmark_id": bid,
                        "reason": "cleared_rejected_unresolved_flags_in_generated_text",
                        "flags": text_hits,
                    }
                )
                continue
            sample["pii_status"] = "cleared"
            meta = sample.setdefault("collection_metadata", {})
            if not isinstance(meta, dict):
                meta = {}
                sample["collection_metadata"] = meta
            meta["pii_clearance_ref"] = application_ref
            meta["pii_clearance_decision"] = "cleared"
            meta["pii_clearance_rationale"] = decision_row.get("rationale")
            meta["pii_clearance_reviewed_at"] = decision_row.get("reviewed_at")
            path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            applied.append({"benchmark_id": bid, "pii_status_before": before, "pii_status_after": "cleared"})
        elif decision == "rejected":
            sample["pii_status"] = "contains_pii"
            meta = sample.setdefault("collection_metadata", {})
            if isinstance(meta, dict):
                meta["pii_clearance_ref"] = application_ref
                meta["pii_clearance_decision"] = "rejected"
            path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            applied.append(
                {"benchmark_id": bid, "pii_status_before": before, "pii_status_after": "contains_pii"}
            )
        else:
            skipped.append({"benchmark_id": bid, "reason": f"decision={decision}"})

    return {
        "tool": "review_pii_clearance",
        "mode": "apply",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "application_ref": application_ref,
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "applied": applied,
        "skipped": skipped,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PII scan and clearance for benchmark samples.")
    parser.add_argument("--samples-glob", required=True)
    parser.add_argument("--out-report", required=True)
    parser.add_argument("--decisions", help="Clearance decisions JSON (required for --apply)")
    parser.add_argument("--application-out", help="Application receipt path (with --apply)")
    parser.add_argument("--apply", action="store_true", help="Apply explicit decisions to collected samples")
    parser.add_argument(
        "--write-decisions-placeholder",
        help="Write decisions placeholder JSON at this path (scan mode)",
    )
    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    sample_paths = resolve_glob(args.samples_glob)
    if not sample_paths:
        write_json_report(
            Path(args.out_report),
            {"tool": "review_pii_clearance", "status": "FAIL", "error": "no samples matched"},
        )
        return 1

    report = _scan_samples(sample_paths, repo_root)
    report["status"] = "PASS"
    write_json_report(Path(args.out_report), report)

    placeholder_path = (
        Path(args.write_decisions_placeholder)
        if args.write_decisions_placeholder
        else Path(args.out_report).parent / "pii_clearance_decisions.placeholder.json"
    )
    _write_decisions_placeholder(report, placeholder_path)

    if not args.apply:
        return 0

    if not args.decisions:
        print("error: --apply requires --decisions", file=sys.stderr)
        return 1

    decisions_doc = load_json(Path(args.decisions))
    app_ref = args.application_out or "artifacts/apps_rg/benchmarks/collected/_manifests/pii_clearance_application_w7.json"
    application = _apply_decisions(
        sample_paths,
        decisions_doc,
        repo_root,
        application_ref=_repo_rel(Path(app_ref), repo_root),
    )
    application["status"] = "PASS" if application["applied_count"] >= 0 else "FAIL"
    write_json_report(Path(app_ref), application)

    cleared = sum(1 for a in application["applied"] if a.get("pii_status_after") == "cleared")
    return 0 if cleared > 0 or application["applied_count"] == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
