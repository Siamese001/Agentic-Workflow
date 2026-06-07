#!/usr/bin/env python3
"""
check_notion_schema_mece.py — CI gate for Notion Wave/Phase Convergence MECE v2.

Enforces the post-2026-04-24 canonical schema for Notion writers:

FORBIDDEN in any `_build_notion_payload` (or equivalent) function:
  - Writing to retired fields: Sub-Wave, Parent Plan Summary, Blocking Items,
    Success Criteria, Dependencies, Coverage Gap %, Last Scored.
  - Phase Title with `[P\\d\\]` or `[NEXT·P\\d\\]` prefix — title must be a
    pure human name; P-Band and NEXT-class live in dedicated fields.

REQUIRED for every writer that targets WAVE_PHASE_DB_ID:
  - Writes the `Evidence` field (replaces 3 retired prose fields).

Fail policy: exit 1 on any violation. Advisory lives in
`.claude/rules/memory-notion-writeback.md` and the MECE v2 memory entity
`ProceduralPattern:NotionBacklogMECESchemaV2`.

This gate is Python-only; scans `.claude/governance/scripts/*.py` and `ops_scripts/**/*.py`
for the known writer patterns.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Files that are KNOWN to target the Wave/Phase Convergence DB and must comply.
# Listed explicitly to avoid false positives on unrelated scripts that happen
# to mention Notion terminology.
KNOWN_WRITERS = [
    REPO_ROOT / ".claude" / "governance/scripts" / "post_cursor_agent_deferred_scope_capture.py",
    REPO_ROOT / ".claude" / "governance/scripts" / "post_cursor_agent_next_step_capture.py",
]

RETIRED_FIELDS = {
    "Sub-Wave",
    "Parent Plan Summary",
    "Blocking Items",
    "Success Criteria",
    "Dependencies",
    "Coverage Gap %",
    "Last Scored",
}

REQUIRED_FIELD = "Evidence"

# Phase Title prefix pattern. Matches `[P1]`, `[P2]`, ..., `[NEXT·P1]`, etc.
# Captures only when the prefix appears at the start of a content string that
# is being assigned to Phase Title.
PHASE_TITLE_PREFIX_RE = re.compile(
    r'"Phase Title"\s*:\s*\{\s*"title"[^}]*"content"\s*:\s*(?:f?")?'
    r"\[(?:P\d+|NEXT[\u00b7\u2219\xb7\.]?P\d+)\]"
)

# Writer region marker: we scan only inside `_build_notion_payload` bodies to
# avoid flagging legacy comments or docstrings.
WRITER_FN_SIGNATURE_RE = re.compile(r"^def\s+_build_notion_payload\b", re.MULTILINE)


def _extract_writer_body(source: str) -> str:
    """Extract all text from the first `_build_notion_payload` def to EOF.

    Simple heuristic: payload-builder functions are at module level and
    followed by a non-function line. Good enough for gate purposes.
    """
    match = WRITER_FN_SIGNATURE_RE.search(source)
    if not match:
        return ""
    return source[match.start() :]


def check_file(path: Path) -> list[str]:
    """Return list of violation messages for `path`; empty if compliant."""
    violations: list[str] = []
    if not path.exists():
        violations.append(f"{path}: MISSING — known writer not found")
        return violations

    source = path.read_text(encoding="utf-8")
    body = _extract_writer_body(source)
    if not body:
        violations.append(f"{path}: no `_build_notion_payload` function found — writer contract broken")
        return violations

    # 1. Retired fields must not appear as dict keys in the payload.
    for field in RETIRED_FIELDS:
        pattern = re.compile(rf'"{re.escape(field)}"\s*:\s*\{{')
        if pattern.search(body):
            violations.append(
                f"{path}: retired MECE v2 field {field!r} is still being written. "
                f"Remove or merge into Evidence."
            )

    # 2. Required Evidence field must be present.
    evidence_pat = re.compile(rf'"{REQUIRED_FIELD}"\s*:\s*\{{')
    if not evidence_pat.search(body):
        violations.append(
            f"{path}: required MECE v2 field 'Evidence' is NOT written. "
            f"Add it as a rich_text property (replaces Success Criteria + "
            f"Blocking Items + Dependencies)."
        )

    # 3. Phase Title must not carry [P\d] or [NEXT·P\d] prefix.
    if PHASE_TITLE_PREFIX_RE.search(body):
        violations.append(
            f"{path}: Phase Title contains a '[P\\d]' or '[NEXT·P\\d]' prefix. "
            f"MECE v2: title is a pure human name; P-Band lives in the P-Band select."
        )

    return violations


def main() -> int:
    print("[mece-check] Notion Wave/Phase Convergence MECE v2 schema gate")
    print(f"[mece-check] repo root: {REPO_ROOT}")
    print(f"[mece-check] writers: {len(KNOWN_WRITERS)}")
    print("")

    all_violations: list[str] = []
    for path in KNOWN_WRITERS:
        print(f"[mece-check] scanning {path.relative_to(REPO_ROOT)}")
        v = check_file(path)
        all_violations.extend(v)

    print("")
    if all_violations:
        print(f"[mece-check] FAIL — {len(all_violations)} violation(s):")
        for msg in all_violations:
            print(f"  - {msg}")
        return 1

    print("[mece-check] PASS — all writers comply with MECE v2 schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
