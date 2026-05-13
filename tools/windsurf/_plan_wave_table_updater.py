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

Inline field sync (plan-wave-inline-status-sync-8b4d2f):
    Also updates free-form prose inline fields within each ## Wave N section:
        WAVE_STATUS, WAVE_COMPLETE, PHASE_STATUS, PHASE_COMPLETE, - Status: (DoD)
    Updates are monotonic (never downgrade), idempotent, section-scoped, and
    code-fence-excluding.

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
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Status tokens used in the wave table
# ---------------------------------------------------------------------------

STATUS_TODO = "🔲 TODO"
STATUS_TODO_BARE = "🔲"  # bare variant used by many plans
STATUS_IN_PROGRESS = "🔄 IN PROGRESS"
STATUS_DONE = "✅ DONE"
STATUS_BLOCKED = "❌ BLOCKED"

# All values that should be treated as "TODO" for replacement purposes
_TODO_VARIANTS = {STATUS_TODO, STATUS_TODO_BARE}

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
    r"(?P<wave_label>W\d+(?:[A-Za-z])?(?:\.\d+)?)"
    r"\*{0,2}\s*"
    r"(?:\|[^|\n]*){1,6}"  # 1-6 middle cells (handles Wave Structure + Phase-Level Summary)
    r"\|\s*)"
    r"(?P<status>[^\|\n]*?)"
    r"(?P<row_suffix>\s*\|[^\n]*)",
    re.MULTILINE,
)

# Phase-level summary table row: first cell is Phase ID like W<N>, W<N>.P<M>, W<N>.5
# Captures: phase_id (e.g., W1, W1.P1, W5.P8, W10.P12) and status cell
_PHASE_ROW_RE = re.compile(
    r"^(?P<row_prefix>"
    r"\|\s*"
    r"(?P<phase_id>W\d+(?:\.\d+)?(?:\.P\d+)?)"
    r"\s*"
    r"(?:\|[^|\n]*){1,4}"
    r"\|\s*)"
    r"(?P<status>[^|\n]*?)"
    r"(?P<row_suffix>\s*\|[^\n]*)",
    re.MULTILINE,
)

# Frontmatter last_updated pattern
_LAST_UPDATED_RE = re.compile(
    r"^(last_updated:\s*)(\S*)",
    re.MULTILINE,
)

# ---------------------------------------------------------------------------
# Inline-field sync helpers (plan-wave-inline-status-sync-8b4d2f)
# ---------------------------------------------------------------------------

# Matches ## Wave N section headers (case-insensitive)
_WAVE_SECTION_HEADER_RE = re.compile(
    r"^(##\s+Wave\s+(\d+)\b[^\n]*)",
    re.MULTILINE | re.IGNORECASE,
)

# Matches fenced code blocks (``` ... ```)
_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)

# Inline prose field regexes — applied only to non-fenced content
_INLINE_WAVE_STATUS_RE = re.compile(r"^(WAVE_STATUS:\s*)(\S+)", re.MULTILINE)
_INLINE_WAVE_COMPLETE_RE = re.compile(r"^(WAVE_COMPLETE:\s*)(\S+)", re.MULTILINE)
_INLINE_PHASE_STATUS_RE = re.compile(r"(PHASE_STATUS:\s*)(\S+)")
_INLINE_PHASE_COMPLETE_RE = re.compile(r"(PHASE_COMPLETE:\s*)(\S+)")
_INLINE_DOD_STATUS_RE = re.compile(r"^(- Status:\s*)(\S+)", re.MULTILINE)

# Values that are already terminal — never overwrite
_TERMINAL_VALUES = {"done", "yes", "deferred", "retired", "archived"}

# Values that represent "open" for each field type
_WAVE_STATUS_OPEN = {"todo", "in_progress", "in progress"}
_WAVE_COMPLETE_OPEN = {"no"}
_PHASE_STATUS_OPEN = {"todo", "in_progress", "in progress"}
_PHASE_COMPLETE_OPEN = {"no"}
_DOD_STATUS_OPEN = {"todo", "in_progress", "in progress", "blocked"}


def _split_wave_sections(text: str) -> list[tuple[int | None, str, int, int]]:
    """Split text into (wave_num, section_text, start, end) tuples.

    wave_num=None for content before the first ## Wave N header.
    Each section spans from its header to the character before the next header
    (or end of text).
    """
    matches = list(_WAVE_SECTION_HEADER_RE.finditer(text))
    if not matches:
        return [(None, text, 0, len(text))]

    sections: list[tuple[int | None, str, int, int]] = []
    # Preamble before first wave section
    first_start = matches[0].start()
    if first_start > 0:
        sections.append((None, text[:first_start], 0, first_start))

    for i, m in enumerate(matches):
        wave_num = int(m.group(2))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((wave_num, text[start:end], start, end))

    return sections


def _strip_fenced_blocks(text: str) -> tuple[str, list[tuple[int, int, str]]]:
    """Replace fenced code blocks with whitespace of the same byte length.

    Returns (stripped_text, fence_map) where fence_map is a list of
    (start, end, original_text) tuples for later restoration.
    """
    fence_map: list[tuple[int, int, str]] = []
    result = list(text)
    for m in _FENCE_RE.finditer(text):
        start, end = m.start(), m.end()
        fence_map.append((start, end, text[start:end]))
        # Replace with same-length whitespace so char offsets remain valid
        for i in range(start, end):
            result[i] = " " if text[i] != "\n" else "\n"
    return "".join(result), fence_map


def _restore_fenced_blocks(text: str, fence_map: list[tuple[int, int, str]]) -> str:
    """Restore original fenced blocks from fence_map (applied in reverse order)."""
    result = list(text)
    for start, end, original in fence_map:
        result[start:end] = list(original)
    return "".join(result)


def _monotonic_replace(pattern: re.Pattern[str], text: str, target: str, open_values: set[str]) -> str:
    """Apply pattern substitution only when current value is in open_values.

    Pattern must have two capture groups: (prefix, current_value).
    Skips replacement when current value is terminal or not in open_values.
    """
    def _sub(m: re.Match[str]) -> str:
        current = m.group(2).strip().lower()
        if current in _TERMINAL_VALUES:
            return m.group(0)
        if current not in open_values:
            return m.group(0)
        return m.group(1) + target

    return pattern.sub(_sub, text)


def _update_inline_fields_in_section(
    section_text: str,
    kind: str,
    phase_id: str = "",
) -> str:
    """Apply inline-field updates to a single wave section body.

    kind must be one of: wave_start | wave_complete | phase_complete | plan_complete.
    phase_id is used only for phase_complete to scope which phase bullet lines change.

    Returns modified section_text. Never raises.
    """
    stripped, fence_map = _strip_fenced_blocks(section_text)

    if kind == "wave_start":
        stripped = _monotonic_replace(_INLINE_WAVE_STATUS_RE, stripped, "IN_PROGRESS", _WAVE_STATUS_OPEN)
        # WAVE_COMPLETE not changed on wave_start

    elif kind == "wave_complete":
        stripped = _monotonic_replace(_INLINE_WAVE_STATUS_RE, stripped, "DONE", _WAVE_STATUS_OPEN | {"in_progress"})
        stripped = _monotonic_replace(_INLINE_WAVE_COMPLETE_RE, stripped, "YES", _WAVE_COMPLETE_OPEN)
        # PHASE_STATUS / PHASE_COMPLETE not touched on wave_complete (hardening #5)
        stripped = _monotonic_replace(_INLINE_DOD_STATUS_RE, stripped, "DONE", _DOD_STATUS_OPEN)

    elif kind == "phase_complete" and phase_id:
        # Scope to lines containing the specific phase ID (e.g. W1.2)
        # Phase IDs are unique across the plan so no extra section scoping needed.
        lines = stripped.splitlines(keepends=True)
        new_lines = []
        for line in lines:
            if phase_id in line:
                line = _monotonic_replace(_INLINE_PHASE_STATUS_RE, line, "DONE", _PHASE_STATUS_OPEN | {"in_progress"})
                line = _monotonic_replace(_INLINE_PHASE_COMPLETE_RE, line, "YES", _PHASE_COMPLETE_OPEN)
            new_lines.append(line)
        stripped = "".join(new_lines)

    elif kind == "plan_complete":
        stripped = _monotonic_replace(_INLINE_WAVE_STATUS_RE, stripped, "DONE", _WAVE_STATUS_OPEN | {"in_progress"})
        stripped = _monotonic_replace(_INLINE_WAVE_COMPLETE_RE, stripped, "YES", _WAVE_COMPLETE_OPEN)
        stripped = _monotonic_replace(_INLINE_PHASE_STATUS_RE, stripped, "DONE", _PHASE_STATUS_OPEN | {"in_progress"})
        stripped = _monotonic_replace(_INLINE_PHASE_COMPLETE_RE, stripped, "YES", _PHASE_COMPLETE_OPEN)
        stripped = _monotonic_replace(_INLINE_DOD_STATUS_RE, stripped, "DONE", _DOD_STATUS_OPEN)

    return _restore_fenced_blocks(stripped, fence_map)


def _update_inline_fields_in_plan(
    content: str,
    slug: str,
    wave: int,
    kind: str,
    phase_id: str = "",
) -> tuple[str, bool, str]:
    """Apply inline prose field updates to plan content string.

    Args:
        content:  Full plan markdown text (read from disk by caller).
        slug:     Plan slug (used for diagnostic messages only).
        wave:     Target wave number; -1 means all waves (plan_complete).
        kind:     One of: wave_start | wave_complete | phase_complete | plan_complete.
        phase_id: Phase identifier (e.g. "W1.2"); required for phase_complete.

    Returns:
        (new_content, changed, message)
        changed is True when any character in the content was modified.
    """
    if kind not in ("wave_start", "wave_complete", "phase_complete", "plan_complete"):
        return content, False, f"no-op for kind={kind}"

    sections = _split_wave_sections(content)

    if kind == "plan_complete":
        # Update all wave sections
        new_parts: list[str] = []
        for wave_num, section_text, _start, _end in sections:
            if wave_num is None:
                new_parts.append(section_text)
            else:
                new_parts.append(_update_inline_fields_in_section(section_text, kind, phase_id))
        new_content = "".join(new_parts)
        changed = new_content != content
        return new_content, changed, f"plan_complete inline update; changed={changed}"

    if kind == "phase_complete":
        # phase_complete scopes by phase_id globally (phase IDs are plan-unique)
        new_parts = []
        for wave_num, section_text, _start, _end in sections:
            if wave_num is None:
                new_parts.append(section_text)
            else:
                new_parts.append(_update_inline_fields_in_section(section_text, "phase_complete", phase_id))
        new_content = "".join(new_parts)
        changed = new_content != content
        return new_content, changed, f"phase_complete phase={phase_id} inline update; changed={changed}"

    # wave_start / wave_complete — target a specific wave section
    target_sections = [(wn, st, s, e) for wn, st, s, e in sections if wn == wave]

    if not target_sections:
        return content, False, f"no matching wave section for wave={wave}"

    if len(target_sections) > 1:
        print(
            f"[inline_updater] WARN: duplicate Wave {wave} sections in {slug}; skipping",
            file=sys.stderr,
        )
        return content, False, f"duplicate wave sections — skipped"

    wave_num, section_text, start, end = target_sections[0]
    new_section = _update_inline_fields_in_section(section_text, kind, phase_id)
    if new_section == section_text:
        return content, False, f"no inline fields changed for wave={wave} kind={kind}"

    new_content = content[:start] + new_section + content[end:]
    return new_content, True, f"inline fields updated for wave={wave} kind={kind}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _find_plan_file(repo_root: Path, slug: str) -> Path | None:
    """Resolve slug -> .windsurf/plans/<slug>.md. Return None if not found."""
    candidate = repo_root / ".windsurf" / "plans" / f"{slug}.md"
    if candidate.is_file():
        return candidate
    return None


def _phase_id_matches(phase_id: str, target_phase: str) -> bool:
    """Return True if phase_id matches target_phase exactly.

    Supports:
        - W<N> (e.g., W1, W10)
        - W<N>.P<M> (e.g., W1.P1, W5.P8, W10.P12)
        - W<N>.<decimal> (e.g., W1.5)
    """
    # Normalize: strip whitespace and compare exact match
    return phase_id.strip() == target_phase.strip()


def _refresh_last_updated(content: str) -> str:
    """Refresh last_updated timestamp in frontmatter."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    return _LAST_UPDATED_RE.sub(rf"\g<1>{now}", content)


def _wave_label_matches(label: str, wave: int) -> bool:
    """Return True if label (e.g. 'W3', 'W1.5', '**W3**') matches wave int."""
    bare = label.strip("*").strip()
    # Accept W<N>, W<N><letter>, or W<N>.<digit> (e.g. W1.5, W2R match wave int)
    m = re.fullmatch(r"W(\d+)(?:[A-Za-z])?(?:\.\d+)?", bare)
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

    Also applies inline prose field updates (WAVE_STATUS, WAVE_COMPLETE, DoD
    - Status:) within the target wave section. Both table-row and inline updates
    operate on the same in-memory content string; the file is written once.

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

    # --- table-row update (existing logic) ---
    lines = original.splitlines(keepends=True)
    table_changed_count = 0
    new_lines: list[str] = []

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")

        if kind == "wave_start":
            m = _ROW_RE.match(stripped)
            if m and _wave_label_matches(m.group("wave_label"), wave):
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_IN_PROGRESS, _TODO_VARIANTS
                )
                if changed:
                    table_changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        elif kind == "wave_complete":
            m = _ROW_RE.match(stripped)
            if m and _wave_label_matches(m.group("wave_label"), wave):
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_DONE, _TODO_VARIANTS | {STATUS_IN_PROGRESS}
                )
                if changed:
                    table_changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        elif kind == "plan_complete":
            m = _ROW_RE.match(stripped)
            if m:
                new_stripped, changed = _replace_status_in_row(
                    stripped, STATUS_DONE, _TODO_VARIANTS | {STATUS_IN_PROGRESS}
                )
                if changed:
                    table_changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        new_lines.append(line)

    after_table = "".join(new_lines)

    # --- inline prose field update (plan-wave-inline-status-sync-8b4d2f) ---
    after_inline, inline_changed, inline_msg = _update_inline_fields_in_plan(
        after_table, slug, wave, kind
    )

    if table_changed_count == 0 and not inline_changed:
        return True, f"no matching rows found/changed for wave={wave} kind={kind}"

    new_content = _refresh_last_updated(after_inline)
    try:
        plan_file.write_text(new_content, encoding="utf-8")
    except OSError as exc:
        return False, f"write failed: {exc}"

    return True, (
        f"updated {table_changed_count} table row(s) wave={wave} kind={kind}; {inline_msg}"
    )


def _replace_phase_status_in_row(row: str, new_status: str, old_statuses: Iterable[str]) -> tuple[str, bool]:
    """Replace the status cell value in a Phase-Level Summary table row.

    Returns (new_row, changed). Only replaces when current status is in
    old_statuses. Returns original row + False when no change needed.
    """
    m = _PHASE_ROW_RE.match(row)
    if not m:
        return row, False
    current = m.group("status").strip()
    if current not in old_statuses:
        return row, False
    new_row = m.group("row_prefix") + new_status + m.group("row_suffix")
    return new_row, True


def _update_phase_in_plan(
    repo_root: Path,
    slug: str,
    phase: str,
    kind: str,
) -> tuple[bool, str]:
    """Update phase-status cells in the Phase-Level Summary table for slug/phase/kind.

    phase must be a phase ID like: W1.P1, W5.P8, W10.P12, or W1, W5, etc.
    kind must be one of: 'phase_start', 'phase_complete'.

    Also applies inline PHASE_STATUS/PHASE_COMPLETE prose field updates for
    phase_complete. Both table-row and inline updates operate on the same
    in-memory content string; the file is written once.

    Returns (ok, message).
    """
    if os.environ.get("WAVE_TABLE_UPDATE_BYPASS") == "1":
        return True, "bypassed"

    if kind not in ("phase_start", "phase_complete"):
        return True, f"no-op for kind={kind}"

    plan_file = _find_plan_file(repo_root, slug)
    if plan_file is None:
        return False, f"plan file not found for slug={slug}"

    try:
        original = plan_file.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"read failed: {exc}"

    # --- table-row update (existing logic) ---
    lines = original.splitlines(keepends=True)
    table_changed_count = 0
    new_lines: list[str] = []

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")

        if kind == "phase_start":
            m = _PHASE_ROW_RE.match(stripped)
            if m and _phase_id_matches(m.group("phase_id"), phase):
                new_stripped, changed = _replace_phase_status_in_row(
                    stripped, STATUS_IN_PROGRESS, _TODO_VARIANTS
                )
                if changed:
                    table_changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        elif kind == "phase_complete":
            m = _PHASE_ROW_RE.match(stripped)
            if m and _phase_id_matches(m.group("phase_id"), phase):
                new_stripped, changed = _replace_phase_status_in_row(
                    stripped, STATUS_DONE, _TODO_VARIANTS | {STATUS_IN_PROGRESS}
                )
                if changed:
                    table_changed_count += 1
                    eol = line[len(stripped):]
                    new_lines.append(new_stripped + eol)
                    continue

        new_lines.append(line)

    after_table = "".join(new_lines)

    # --- inline prose field update (phase_complete only) ---
    inline_changed = False
    inline_msg = "no inline update for phase_start"
    if kind == "phase_complete":
        after_inline, inline_changed, inline_msg = _update_inline_fields_in_plan(
            after_table, slug, -1, "phase_complete", phase_id=phase
        )
    else:
        after_inline = after_table

    if table_changed_count == 0 and not inline_changed:
        return True, f"no matching rows found/changed for phase={phase} kind={kind}"

    new_content = _refresh_last_updated(after_inline)
    try:
        plan_file.write_text(new_content, encoding="utf-8")
    except OSError as exc:
        return False, f"write failed: {exc}"

    return True, (
        f"updated {table_changed_count} table row(s) phase={phase} kind={kind}; {inline_msg}"
    )
