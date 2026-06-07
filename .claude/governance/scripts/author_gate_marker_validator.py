#!/usr/bin/env python3
"""
author_gate_marker_validator.py — Validate DECISION_CAPTURED marker completeness.

Audits every capture event for the v2 marker grammar. Missing required fields
are logged to artifacts/cursor/author_gate_capture_violations.jsonl so the
coverage gate can alarm on capture rot.

CALLED BY
    - post_cursor_agent_author_gate_capture.py (advisory — logs then proceeds)
    - audit_ledger_coverage.py (retrospective audit of existing rows)
    - CLI: python .claude/governance/scripts/author_gate_marker_validator.py --marker "<text>"

GRAMMAR (v2, 2026-04-24)
    DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<label>, outcome=<status>
        [, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>]

    Required: type, repo_area, selected, outcome
    Recommended (v2 calibration): confidence, gap, principle, latency_ms
    Optional: override (defaults to false)

    When decision_type in {refactor_scope, architecture_choice, anti_pattern,
    deletion_strategy, dependency_addition, test_strategy, error_handling}
    the v2 calibration fields are REQUIRED for meta-learning correctness.

FAIL POLICY — OPEN
    Invalid markers still get captured (data-loss is worse than malformed data).
    Violations are logged; a future CI gate may promote to error.

CONSTITUTIONAL
    - No shell, subprocess, or PowerShell
    - UTF-8 explicit
    - Specific exceptions: ValueError, OSError
    - Idempotent — safe to call repeatedly per response
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "cursor" / "author_gate_capture_violations.jsonl"

# Decision types for which v2 calibration fields are required
_REFACTOR_CLASS_TYPES = frozenset({
    "refactor_scope",
    "architecture_choice",
    "anti_pattern",
    "deletion_strategy",
    "dependency_addition",
    "test_strategy",
    "error_handling",
})

_MARKER_RE = re.compile(
    r"DECISION_CAPTURED:\s*type=(?P<dtype>[\w_]+),\s*"
    r"repo_area=(?P<area>[^,]+),\s*"
    r"selected=(?P<selected>[^,]+),\s*"
    r"outcome=(?P<outcome>\w+)"
    r"(?P<tail>[^\n]*)",
    re.MULTILINE,
)

_V2_PATTERNS = {
    "confidence": re.compile(r"confidence\s*=\s*(?P<v>[01](?:\.\d+)?)"),
    "gap": re.compile(r"gap\s*=\s*(?P<v>[01](?:\.\d+)?)"),
    "override": re.compile(r"override\s*=\s*(?P<v>true|false)", re.IGNORECASE),
    "latency_ms": re.compile(r"latency_ms\s*=\s*(?P<v>\d+)"),
    "principle": re.compile(r"principle\s*=\s*(?P<v>[^,\n]{1,80})"),
}


def validate_marker(text: str) -> dict[str, Any]:
    """Validate a response text containing zero-or-more DECISION_CAPTURED markers.

    Returns:
        {
            "markers_found": int,
            "valid": bool,                       # overall — True iff every marker passes
            "results": [per_marker_dict, ...],
        }

    Per-marker result:
        {
            "raw": str,                          # original matched text (truncated)
            "required_present": bool,
            "missing_required": [str, ...],
            "missing_recommended": [str, ...],   # only populated for refactor-class types
            "decision_type": str,
            "refactor_class": bool,
        }
    """
    results: list[dict[str, Any]] = []
    for m in _MARKER_RE.finditer(text):
        dtype = m.group("dtype")
        area = m.group("area").strip()
        selected = m.group("selected").strip()
        outcome = m.group("outcome").strip()
        tail = m.groupdict().get("tail") or ""
        raw = m.group(0)[:300]

        missing_required: list[str] = []
        if not dtype:
            missing_required.append("type")
        if not area:
            missing_required.append("repo_area")
        if not selected:
            missing_required.append("selected")
        if not outcome:
            missing_required.append("outcome")

        # v2 calibration check for refactor-class
        missing_recommended: list[str] = []
        is_refactor_class = dtype in _REFACTOR_CLASS_TYPES
        if is_refactor_class:
            for field, pattern in _V2_PATTERNS.items():
                if field == "override":  # defaults to false, not required
                    continue
                if not pattern.search(tail):
                    missing_recommended.append(field)

        results.append({
            "raw": raw,
            "required_present": not missing_required,
            "missing_required": missing_required,
            "missing_recommended": missing_recommended,
            "decision_type": dtype,
            "refactor_class": is_refactor_class,
        })

    overall_valid = all(r["required_present"] and not r["missing_recommended"] for r in results)
    return {
        "markers_found": len(results),
        "valid": overall_valid,
        "results": results,
    }


def log_violation(report: dict[str, Any], context: str = "capture_hook") -> None:
    """Append a violation row per imperfect marker. Fail-open on IO error."""
    try:
        VIOLATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with VIOLATIONS_PATH.open("a", encoding="utf-8") as fh:
            for r in report["results"]:
                if r["required_present"] and not r["missing_recommended"]:
                    continue
                severity = "error" if r["missing_required"] else "warn"
                fh.write(json.dumps({
                    "timestamp": ts,
                    "context": context,
                    "severity": severity,
                    "decision_type": r.get("decision_type"),
                    "missing_required": r["missing_required"],
                    "missing_recommended": r["missing_recommended"],
                    "raw": r["raw"],
                }) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- violation log: non-fatal, fail-open
        pass


def main() -> int:
    p = argparse.ArgumentParser(description="Validate DECISION_CAPTURED markers")
    p.add_argument("--marker", help="Marker text to validate (else read stdin)")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of prose")
    args = p.parse_args()

    text = args.marker if args.marker else sys.stdin.read()
    report = validate_marker(text)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"markers_found={report['markers_found']} valid={report['valid']}")
        for i, r in enumerate(report["results"]):
            mark = "OK" if r["required_present"] and not r["missing_recommended"] else "WARN"
            print(f"  [{mark}] #{i+1} type={r['decision_type']} "
                  f"missing_required={r['missing_required']} "
                  f"missing_recommended={r['missing_recommended']}")

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
