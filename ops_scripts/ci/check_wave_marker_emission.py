#!/usr/bin/env python3
"""
check_wave_marker_emission.py — CI gate: wave marker emission completeness.

WAVE-MARKER gate (advisory by default).

Detects plan `.md` files whose Wave Structure table contains rows with
``🔲 TODO`` status even though the ``wave_lifecycle_capture.jsonl`` log
shows no ``WAVE_COMPLETE:`` / ``PLAN_COMPLETE:`` entries for that plan slug.

This catches the failure mode documented in RCA rca-wave-marker-emission-gap-
c7d3f1: Cursor Agent executed multiple waves but never emitted the required
``WAVE_COMPLETE:`` markers, leaving the plan table permanently stale.

Algorithm
---------
1. Scan ``.cursor/plans/*.md`` for Wave Structure tables with ``🔲 TODO``
   rows (skips plans where ALL rows are DONE or all are TODO — only flags
   mixed state, i.e. at least one ✅ DONE row alongside at least one 🔲 TODO).
   Mixed state indicates partial completion without terminal markers.
2. For each flagged slug, check ``artifacts/cursor/wave_lifecycle_capture.jsonl``
   for any entry with ``"slug": "<slug>"`` — if absent the audit log has no
   record of marker emission for this plan.
3. Report violations as WARN (advisory). Plans where the log has at least one
   real entry for the slug are NOT flagged (markers fired; table may just be
   stale due to hook failure — separate concern).

Exit codes
----------
0  — clean or advisory-only (default)
1  — fail-closed mode only (WAVE_MARKER_GATE_FAIL_CLOSED=1)

Bypass: WAVE_MARKER_EMISSION_BYPASS=1
Fail-closed: WAVE_MARKER_GATE_FAIL_CLOSED=1
Report: artifacts/ci/wave_marker_emission_gate.json

Plan: rca-wave-marker-emission-gap-c7d3f1 W2.P1
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
CAPTURE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "wave_lifecycle_capture.jsonl"
REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "wave_marker_emission_gate.json"

# Regex: a Wave Structure table row with 🔲 TODO
_TODO_ROW = re.compile(r"\|\s*Wave\s+\d+\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*🔲\s*TODO\s*\|")
_DONE_ROW = re.compile(r"\|\s*Wave\s+\d+\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*✅\s*DONE\s*\|")

# Simpler fallback patterns for tables with fewer columns
_TODO_CELL = re.compile(r"🔲\s*TODO")
_DONE_CELL = re.compile(r"✅\s*DONE")

# Frontmatter slug pattern
_SLUG_FM = re.compile(r"^plan_id:\s*([a-z0-9][a-z0-9\-]+[a-z0-9])\s*$", re.MULTILINE)

# Wave Structure table header detection
_WAVE_TABLE_HDR = re.compile(r"\|\s*Wave[s]?\s*\|", re.IGNORECASE)


def _slug_from_filename(path: Path) -> str:
    return path.stem


def _slug_from_frontmatter(text: str) -> str | None:
    m = _SLUG_FM.search(text)
    return m.group(1) if m else None


def _extract_wave_table(text: str) -> str:
    """Return only the portion of the text inside the Wave Structure table."""
    lines = text.splitlines()
    in_table = False
    table_lines: list[str] = []
    for line in lines:
        if not in_table:
            if _WAVE_TABLE_HDR.search(line):
                in_table = True
                table_lines.append(line)
        else:
            stripped = line.strip()
            if stripped.startswith("|"):
                table_lines.append(line)
            elif stripped == "" and table_lines:
                break  # blank line ends table
    return "\n".join(table_lines)


def _plan_has_mixed_state(text: str) -> tuple[bool, int, int]:
    """Return (is_mixed, done_count, todo_count) from the Wave Structure table."""
    table_text = _extract_wave_table(text)
    if not table_text:
        return False, 0, 0
    done = len(_DONE_CELL.findall(table_text))
    todo = len(_TODO_CELL.findall(table_text))
    return (done > 0 and todo > 0), done, todo


def _slugs_in_capture_log() -> set[str]:
    """Return the set of plan slugs mentioned in wave_lifecycle_capture.jsonl."""
    slugs: set[str] = set()
    if not CAPTURE_LOG.exists():
        return slugs
    try:
        for line in CAPTURE_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            # rows key carries list of {slug, ok, msg}
            rows = entry.get("rows", [])
            for row in rows:
                s = row.get("slug") if isinstance(row, dict) else None
                if s and isinstance(s, str):
                    slugs.add(s)
            # direct slug key (wave_table_update events)
            direct = entry.get("slug")
            if direct and isinstance(direct, str):
                slugs.add(direct)
    except OSError:
        pass
    return slugs


def _write_report(findings: list[dict[str, Any]], total_scanned: int) -> None:
    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "gate": "WAVE-MARKER",
            "total_scanned": total_scanned,
            "violations": len(findings),
            "findings": findings,
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    if os.environ.get("WAVE_MARKER_EMISSION_BYPASS") == "1":
        print("[WAVE-MARKER] bypass active")
        return 0

    plan_files = sorted(PLANS_DIR.glob("*.md"))
    logged_slugs = _slugs_in_capture_log()

    findings: list[dict[str, Any]] = []
    scanned = 0

    for path in plan_files:
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        scanned += 1

        slug = _slug_from_frontmatter(text) or _slug_from_filename(path)
        is_mixed, done_count, todo_count = _plan_has_mixed_state(text)

        if not is_mixed:
            continue

        # Mixed state: at least one DONE + at least one TODO
        # Only flag if the capture log has NO entry for this slug
        if slug in logged_slugs:
            continue  # markers were emitted at some point; not flagging

        try:
            file_rel = str(path.relative_to(REPO_ROOT))
        except ValueError:
            file_rel = str(path)
        findings.append({
            "slug": slug,
            "file": file_rel,
            "done_count": done_count,
            "todo_count": todo_count,
            "in_capture_log": False,
            "severity": "WARN",
            "message": (
                f"Plan has {done_count} DONE + {todo_count} TODO waves but "
                f"no WAVE_COMPLETE/PLAN_COMPLETE marker in capture log. "
                f"Emit markers at wave boundaries — see RCA rca-wave-marker-emission-gap-c7d3f1."
            ),
        })

    _write_report(findings, scanned)

    if findings:
        print(f"[WAVE-MARKER] WARN: {len(findings)} plan(s) with mixed wave state and no marker log entry:")
        for f in findings:
            print(f"  {f['slug']}: {f['done_count']} DONE / {f['todo_count']} TODO — {f['file']}")
        try:
            report_display = REPORT_PATH.relative_to(REPO_ROOT)
        except ValueError:
            report_display = REPORT_PATH
        print(f"  Report: {report_display}")
        print("  Fix: emit WAVE_COMPLETE: / WAVE_START: markers per wave. Bypass: WAVE_MARKER_EMISSION_BYPASS=1")
    else:
        print(f"[WAVE-MARKER] OK — {scanned} plans scanned, no mixed-state-without-marker violations.")

    fail_closed = os.environ.get("WAVE_MARKER_GATE_FAIL_CLOSED") == "1"
    return 1 if (findings and fail_closed) else 0


if __name__ == "__main__":
    sys.exit(main())
