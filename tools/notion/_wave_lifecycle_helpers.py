"""
_wave_lifecycle_helpers.py — Pure-logic helpers for wave-lifecycle Notion sync.

SSOT for: marker parsing (WAVE_START / WAVE_COMPLETE / PHASE_COMPLETE / PLAN_COMPLETE),
status taxonomy alignment with constitutional rule notion-plans-taxonomy.md, and
NotionPatchSpec construction.

Pure: no I/O, no subprocess, no Notion API calls. Specific exceptions only.
Importable by tools/notion/wave_lifecycle_writer.py and the post-cursor-agent hook.

Constitutional tie-in: §25 (writers bypass MCP entirely), §27 (writers stay
schema-pure), §35 (preserves WAVE_COMPLETE / PHASE_COMPLETE markers).

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W1.P1.1).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CURSOR_SCRIPTS = _REPO_ROOT / ".claude" / "governance/scripts"
if str(_CURSOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CURSOR_SCRIPTS))

from _notion_plans_status_check import CANONICAL_STATUSES  # noqa: E402

# ---------------------------------------------------------------------------
# Status taxonomy — SSOT: _notion_plans_status_check.CANONICAL_STATUSES
# ---------------------------------------------------------------------------

STATUS_NOT_STARTED = "Not Started"
STATUS_IN_PROGRESS = "In Progress"
STATUS_WAITING = "Waiting"
STATUS_COMPLETED = "Completed"
STATUS_RETIRED = "Retired"
STATUS_ARCHIVED = "Archived"
STATUS_LOWER_PRIORITY = "Lower Priority"

# Statuses where WAVE_START should flip to In Progress.
# Already-In-Progress / Completed / Retired / Archived stay put.
_FLIPPABLE_TO_IN_PROGRESS: frozenset[str] = frozenset({STATUS_NOT_STARTED, STATUS_WAITING})

# ---------------------------------------------------------------------------
# Slug / property name constants
# ---------------------------------------------------------------------------

# Canonical slug: ends in exactly 6 hex chars (e.g. foo-bar-abc123)
# Relaxed slug: any kebab-case alphanum string ≥4 chars (covers master plans,
# numerically-prefixed plans like 01_apps-rg-..., and plans without hex suffix)
SLUG_RE = re.compile(
    r"^[a-z0-9_][a-z0-9_-]{3,}$"
)

PROP_SLUG = "Slug"
PROP_STATUS = "Status"
PROP_SUMMARY = "Summary"
# AI Summary has a trailing space in the Plans DB schema (memory 78c557a4).
PROP_AI_SUMMARY = "AI Summary "

# Wave-log lines are appended to the Summary rich_text. Marker shape:
#   "[Wave-Log <iso-ts>] W{N} DONE"
# When a marker carries note="...", the line is suffixed with " — {note}".
WAVE_LOG_PREFIX = "[Wave-Log "

# Cap on free-form ``note=`` content. Keeps the Summary column "succinct" so
# operators see one high-signal line per wave instead of paragraphs. Notes
# longer than this are truncated with an ellipsis.
MAX_NOTE_CHARS = 240

# ---------------------------------------------------------------------------
# Marker parser
# ---------------------------------------------------------------------------

# Markers must be at start of line (^) — prose mentions of "WAVE_COMPLETE:" in
# quoted plans / docs are excluded by requiring the marker to begin a line.
# Each kind has its own pattern so we can capture per-kind fields cleanly.
_WAVE_START_RE = re.compile(
    r"^\s*WAVE_START:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)
_WAVE_COMPLETE_RE = re.compile(
    r"^\s*WAVE_COMPLETE:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)
_PHASE_COMPLETE_RE = re.compile(
    r"^\s*PHASE_COMPLETE:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)
_PLAN_COMPLETE_RE = re.compile(
    r"^\s*PLAN_COMPLETE:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)

# Key/value parser. Values may be:
#   - double-quoted ("like this") to allow spaces / punctuation
#   - single-quoted ('like this')
#   - a bareword (no whitespace)
# This lets ``note="4 files, +12 tests"`` carry signal into Summary while
# bareword keys (plan=foo-abc123 wave=3) keep working unchanged.
_KV_RE = re.compile(
    r"\b(?P<key>plan|wave|phase|reason|note)="
    r"(?:"
    r'"(?P<qval>[^"]*)"'
    r"|"
    r"'(?P<sqval>[^']*)'"
    r"|"
    r"(?P<bval>\S+)"
    r")"
)


def _parse_kv(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _KV_RE.finditer(body):
        val = m.group("qval")
        if val is None:
            val = m.group("sqval")
        if val is None:
            val = m.group("bval") or ""
        out[m.group("key")] = val.strip()
    return out


def _sanitize_note(raw: str | None) -> str | None:
    """Trim, collapse whitespace, and cap at MAX_NOTE_CHARS.

    Returns None for empty / whitespace-only input. Newlines are flattened
    so a single Summary append never spans multiple log lines.
    """
    if not raw:
        return None
    flat = re.sub(r"\s+", " ", raw).strip()
    if not flat:
        return None
    if len(flat) > MAX_NOTE_CHARS:
        flat = flat[: MAX_NOTE_CHARS - 1].rstrip() + "\u2026"
    return flat


@dataclass(frozen=True)
class WaveLifecycleMarker:
    """One parsed marker from a Cursor Agent response."""

    kind: str  # "wave_start" | "wave_complete" | "phase_complete" | "plan_complete"
    slug: str
    wave: int | None = None
    phase: str | None = None
    reason: str | None = None
    # Free-form one-liner suffixed onto the Summary append ("— {note}").
    # Sanitized: whitespace-collapsed, capped at MAX_NOTE_CHARS. Optional.
    note: str | None = None


def parse_wave_lifecycle_markers(text: str) -> list[WaveLifecycleMarker]:
    """Parse all wave-lifecycle markers from Cursor Agent response text.

    Returns markers in document order. Rows missing a valid slug are dropped.
    Never raises.
    """
    if not text:
        return []
    out: list[WaveLifecycleMarker] = []

    for marker_kind, pattern in (
        ("wave_start", _WAVE_START_RE),
        ("wave_complete", _WAVE_COMPLETE_RE),
        ("phase_complete", _PHASE_COMPLETE_RE),
        ("plan_complete", _PLAN_COMPLETE_RE),
    ):
        for m in pattern.finditer(text):
            body = m.group("body")
            fields = _parse_kv(body)
            slug = fields.get("plan", "").strip()
            if not slug or not SLUG_RE.match(slug):
                continue
            wave_val: int | None = None
            if "wave" in fields:
                try:
                    wave_val = int(fields["wave"])
                except ValueError:
                    wave_val = None
            out.append(
                WaveLifecycleMarker(
                    kind=marker_kind,
                    slug=slug,
                    wave=wave_val,
                    phase=fields.get("phase"),
                    reason=fields.get("reason"),
                    note=_sanitize_note(fields.get("note")),
                )
            )
    return out


# ---------------------------------------------------------------------------
# Patch-spec construction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NotionPatchSpec:
    """A decision: what (if anything) should be patched on a Plans DB row.

    ``properties`` is a Notion API ``properties`` payload fragment ready to be
    sent in a PATCH request. ``summary_append`` is a single line to be appended
    to the Summary rich_text (writer is responsible for read-modify-write).

    A NotionPatchSpec with empty ``properties`` AND ``summary_append=None``
    is a no-op (the writer should skip).
    """

    slug: str
    properties: dict[str, Any] = field(default_factory=dict)
    summary_append: str | None = None
    reason: str = ""

    @property
    def is_noop(self) -> bool:
        return not self.properties and self.summary_append is None


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _status_property(status: str) -> dict[str, Any]:
    if status not in CANONICAL_STATUSES:
        raise ValueError(
            f"refusing to write non-canonical status {status!r}; "
            f"canonical: {sorted(CANONICAL_STATUSES)}"
        )
    return {PROP_STATUS: {"select": {"name": status}}}


def patch_for_marker(
    marker: WaveLifecycleMarker,
    current_status: str | None,
    *,
    now_iso: str | None = None,
) -> NotionPatchSpec:
    """Decide the patch for ``marker`` given the row's current Status.

    Decision matrix:

    +-----------------+----------------------------+--------------------------+
    | Marker kind     | Status flip                | Summary append           |
    +-----------------+----------------------------+--------------------------+
    | wave_start      | Not Started/Waiting        | "[Wave-Log <ts>] W{N}    |
    |                 | -> In Progress (else no-op)| START"                   |
    | wave_complete   | none (Status untouched)    | "[Wave-Log <ts>] W{N}    |
    |                 |                            | DONE"                    |
    | phase_complete  | none                       | "[Wave-Log <ts>] Phase   |
    |                 |                            | {id} DONE"               |
    | plan_complete   | -> Completed (always)      | "[Wave-Log <ts>] PLAN    |
    |                 |                            | COMPLETE"                |
    +-----------------+----------------------------+--------------------------+

    Markers with no actionable side-effect for the current state return a
    no-op NotionPatchSpec.
    """
    ts = now_iso or _now_iso_utc()
    props: dict[str, Any] = {}
    summary_append: str | None = None
    reason_parts: list[str] = []

    if marker.kind == "wave_start":
        wave_str = f"W{marker.wave}" if marker.wave is not None else "W?"
        if current_status in _FLIPPABLE_TO_IN_PROGRESS:
            props.update(_status_property(STATUS_IN_PROGRESS))
            reason_parts.append(f"status_flip:{current_status}->{STATUS_IN_PROGRESS}")
        elif current_status == STATUS_IN_PROGRESS:
            reason_parts.append("status_already_in_progress")
        elif current_status == STATUS_COMPLETED:
            # Guard: never flip a Completed plan back to In Progress.
            # plan notion-plan-status-hardening-e5f3a1 (W2.P1).
            reason_parts.append("status_completed_guard:noop")
            # Return immediately — no summary append either (no log noise on completed plans).
            return NotionPatchSpec(
                slug=marker.slug,
                properties={},
                summary_append=None,
                reason=";".join(reason_parts),
            )
        else:
            reason_parts.append(f"status_locked:{current_status}")
        summary_append = f"{WAVE_LOG_PREFIX}{ts}] {wave_str} START"

    elif marker.kind == "wave_complete":
        wave_str = f"W{marker.wave}" if marker.wave is not None else "W?"
        summary_append = f"{WAVE_LOG_PREFIX}{ts}] {wave_str} DONE"
        reason_parts.append("wave_done_log_only")

    elif marker.kind == "phase_complete":
        phase_id = marker.phase or "?"
        summary_append = f"{WAVE_LOG_PREFIX}{ts}] Phase {phase_id} DONE"
        reason_parts.append("phase_done_log_only")

    elif marker.kind == "plan_complete":
        if current_status == STATUS_COMPLETED:
            reason_parts.append("status_already_completed")
        else:
            props.update(_status_property(STATUS_COMPLETED))
            reason_parts.append(
                f"status_flip:{current_status or 'unknown'}->{STATUS_COMPLETED}"
            )
        summary_append = f"{WAVE_LOG_PREFIX}{ts}] PLAN COMPLETE"

    else:
        reason_parts.append(f"unknown_kind:{marker.kind}")

    # Suffix the optional high-signal note onto the log line. Sanitized at
    # parse time; we re-sanitize here for callers that built a marker by hand.
    if summary_append is not None:
        note = _sanitize_note(marker.note)
        if note:
            summary_append = f"{summary_append} \u2014 {note}"
            reason_parts.append("note_present")

    return NotionPatchSpec(
        slug=marker.slug,
        properties=props,
        summary_append=summary_append,
        reason=";".join(reason_parts) if reason_parts else "",
    )


def coalesce_specs(specs: Iterable[NotionPatchSpec]) -> dict[str, NotionPatchSpec]:
    """Coalesce multiple specs for the same slug into one combined spec.

    Status property: last writer wins (markers in document order).
    Summary appends: concatenated with newline separators.
    Empty / no-op specs are dropped.
    """
    by_slug: dict[str, NotionPatchSpec] = {}
    for spec in specs:
        if spec.is_noop:
            continue
        prior = by_slug.get(spec.slug)
        if prior is None:
            by_slug[spec.slug] = spec
            continue
        merged_props = dict(prior.properties)
        merged_props.update(spec.properties)
        merged_summary = "\n".join(
            x for x in (prior.summary_append, spec.summary_append) if x
        ) or None
        by_slug[spec.slug] = NotionPatchSpec(
            slug=spec.slug,
            properties=merged_props,
            summary_append=merged_summary,
            reason=";".join(x for x in (prior.reason, spec.reason) if x),
        )
    return by_slug


__all__ = [
    "STATUS_NOT_STARTED",
    "STATUS_IN_PROGRESS",
    "STATUS_WAITING",
    "STATUS_COMPLETED",
    "STATUS_RETIRED",
    "STATUS_ARCHIVED",
    "STATUS_LOWER_PRIORITY",
    "CANONICAL_STATUSES",
    "PROP_SLUG",
    "PROP_STATUS",
    "PROP_SUMMARY",
    "PROP_AI_SUMMARY",
    "WAVE_LOG_PREFIX",
    "MAX_NOTE_CHARS",
    "SLUG_RE",
    "WaveLifecycleMarker",
    "NotionPatchSpec",
    "parse_wave_lifecycle_markers",
    "patch_for_marker",
    "coalesce_specs",
]
