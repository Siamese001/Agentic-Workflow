"""
_plan_wave_table_updater.py — Update wave-status cells in plan .md files.

Pure logic: no I/O side-effects beyond the file write. No Notion calls. No
subprocess. Called by post_cascade_wave_lifecycle_capture.py after each
WAVE_START / WAVE_COMPLETE / PLAN_COMPLETE marker is processed.

Status cell mapping:
    wave_start    -> 🔄 IN PROGRESS  (only if cell is 🔲 TODO)
    wave_complete -> ✅ DONE
    plan_complete -> marks any remaining 🔄 IN PROGRESS cells as ✅ DONE

Wave number matching:
    Matches table rows whose first cell is one of:
        W<N>  |  **W<N>**  |  W<N>.5  |  **W<N>.5**
    where N equals the integer wave number from the marker.
    Also matches the PLAN_COMPLETE case: any row with 🔄 IN PROGRESS.

The plan file is located by scanning .windsurf/plans/<slug>.md. The slug
must match the SLUG_RE pattern from _wave_lifecycle_helpers (alphanum-dash
ending in 6 hex chars).

Fail policy: OPEN — all errors are returned as (False, reason) tuples.
Never raises publicly.

Bypass: WAVE_TABLE_UPDATE_BYPASS=1 env var.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Status tokens used in the wave table
# ---------------------------------------------------------------------------

STATUS_TODO = "🔲 TODO"
STATUS_IN_PROGRESS = "🔄 IN PROGRESS"
STATUS_DONE = "✅ DONE"
STATUS_BLOCKED = "❌ BLOCKED"

# ---------------------------------------------------------------------------
# Table-row regex
# ---------------------------------------------------------------------------

# Matches a markdown pipe-delimited table row whose first cell content is a
# wave label of the form:  W<N>  |  W<N>.5  |  **W<N>**  |  **W<N>.5**
# The row must contain at least two pipe chars so we don't touch header/divider rows.
# Captures:
#   row_prefix — everything up to and including the status cell pipe separator
#   status     — the current status text
#   row_suffix — everything after the status value up to end-of-line
_ROW_RE = re.compile(
    r"^(?P<row_prefix>"
    r"\|\s*\*{0,2}"
    r"(?P<wave_label>W\d+(?:\.\d+)?)"
    r"\*{0,2}\s*"
    r"(?:\|[^|\n]*){1,6}"  # 1-6 middle cells (handles Wave Structure + Phase-Level Summary)
    r"\|\s*)"
    r"(?P<status>[^\|\n]*?)"
    r"(?P<row_suffix>\s*\|[^\n]*)",
    re.MULTILINE,
)

# Phase-level summary table row: first cell is also W<N> / W<N>.5
# Same structure — we treat it identically.

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _find_plan_file(repo_root: Path, slug: str) -> Path | None:
    """Resolve slug -> .windsurf/plans/<slug>.md. Return None if not found."""
    candidate = repo_root / ".windsurf" / "plans" / f"{slug}.md"
    if candidate.is_file():
        return candidate
    return None


def _wave_label_matches(label: str, wave: int) -> bool:
    """Return True if label (e.g. 'W3', 'W1.5', '**W3**') matches wave int."""
    bare = label.strip("*").strip()
    # Accept W<N> or W<N>.<anything> (e.g. W1.5 matches wave=1)
    m = re.fullmatch(r"W(\d+)(?:\.\d+)?", bare)
    if not m:
        return False
    return int(m.group(1)) == wave


def _replace_status_in_row(row: str, new_status: str, old_statuses: Iterable[str]) -> tuple[str, bool]:
    """Replace the status cell value in a single table row string.

    Returns (new_row, changed). Only replaces when current status is in
    old_statuses. Returns original row + False when no change needed.
    """
    m = _ROW_RE.match(row)
    if not m:
        return row, False
    current = m.group("status").strip()
    if current not in old_statuses:
        return row, False
    new_row = m.group("row_prefix") + new_status + m.group("row_suffix")
    return new_row, True


def update_wave_in_plan(
    repo_root: Path,
    slug: str,
    wave: int,
    kind: str,
) -> tuple[bool, str]:
    """Update wave-status cells in the plan .md for slug/wave/kind.

    kind must be one of: 'wave_start', 'wave_complete', 'plan_complete'.
    For 'phase_complete' this is a no-op (phase rows not in the wave table).

    Returns (ok, message).
    """
    if os.environ.get("WAVE_TABLE_UPDATE_BYPASS") == "1":
        return True, "bypassed"

    if kind not in ("wave_start", "wave_complete", "plan_complete"):
        return True, f"no-op for kind={kind}"

    plan_file = _find_plan_file(repo_root, slug)
    if plan_file is None:
        return False, f"plan file not found for slug={slug}"

    try:
        original = plan_file.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"read failed: {exc}"

    lines = original.splitlines(keepends=True)
    changed_count = 0
    new_lines: list[str] = []

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")

        if kind == "wave_start":
            m = _ROW_RE.match(stripped)
            if m and _wave_label_matches(m.group("wave_label"), wave):
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_IN_PROGRESS, {STATUS_TODO}
                )
                if changed:
                    changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        elif kind == "wave_complete":
            m = _ROW_RE.match(stripped)
            if m and _wave_label_matches(m.group("wave_label"), wave):
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_DONE, {STATUS_TODO, STATUS_IN_PROGRESS}
                )
                if changed:
                    changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        elif kind == "plan_complete":
            # wave == -1 means "mark every wave row" (all TODO/IN_PROGRESS -> DONE)
            m = _ROW_RE.match(stripped)
            if m:
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_DONE, {STATUS_TODO, STATUS_IN_PROGRESS}
                )
                if changed:
                    changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        new_lines.append(line)

    if changed_count == 0:
        return True, f"no matching rows found/changed for wave={wave} kind={kind}"

    new_content = "".join(new_lines)
    try:
        plan_file.write_text(new_content, encoding="utf-8")
    except OSError as exc:
        return False, f"write failed: {exc}"

    return True, f"updated {changed_count} row(s) wave={wave} kind={kind}"
