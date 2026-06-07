#!/usr/bin/env python3
"""
post_cursor_agent_wave_lifecycle_capture.py — Capture wave-lifecycle markers.

Hook: post_cursor_agent_response (show_output=false).

Scans the Cursor Agent response for ``WAVE_START:`` / ``WAVE_COMPLETE:`` /
``PHASE_COMPLETE:`` / ``PLAN_COMPLETE:`` markers and applies each as a
direct-HTTP Notion patch via ``tools.notion.wave_lifecycle_writer``. The
writer bypasses the MCP layer entirely — no ``<invoke name="mcp*_API-*">``
tags emitted, so this hook does NOT trip remote-MCP audit rules or
``notion-plan-wave-deferral.md``.

Also updates the wave-status cells in the on-disk plan ``.md`` file via
``tools.windsurf._plan_wave_table_updater``, so the Wave Structure / Phase-
Level Summary tables stay in sync with actual progress without requiring
manual edits. Bypass: WAVE_TABLE_UPDATE_BYPASS=1.

Marker grammar (one per line)::

    WAVE_START: plan=<slug-6hex> wave=<N> [note="<short high-signal one-liner>"]
    WAVE_COMPLETE: plan=<slug-6hex> wave=<N> [note="..."]
    PHASE_COMPLETE: plan=<slug-6hex> phase=<id> [note="..."]
    PLAN_COMPLETE: plan=<slug-6hex> [note="..."]

The optional ``note="..."`` field carries a succinct (~240-char cap)
one-liner appended to the Notion Summary column, e.g.::

    WAVE_COMPLETE: plan=foo-abc123 wave=3 note="4 files, +12 tests, scope=summary-signal"

renders as ``[Wave-Log <ts>] W3 DONE — 4 files, +12 tests, scope=summary-signal``
on the Plans DB row's Summary. Without ``note=`` the line stays terse.

Markers MUST start at the beginning of a line (regex anchor ``^``) so
quoted prose mentions are excluded.

Fail policy: OPEN (exit 0 always). Never blocks. Never raises.

Bypass: WAVE_LIFECYCLE_CAPTURE_BYPASS=1.
       WAVE_LIFECYCLE_NOTION_BYPASS=1 (writer-side; logs but doesn't PATCH).
       WAVE_TABLE_UPDATE_BYPASS=1 (plan .md update skipped).

Constitutional ties: §25 (preserved), §35 (preserved), §36 (extended).

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W3.P3.1).
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_PATH = REPO_ROOT / "artifacts" / "windsurf" / "wave_lifecycle_capture.jsonl"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB


def _log(event: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _extract_response_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""
    for key in ("response_text", "text", "content"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val
    tool_info = payload.get("tool_info")
    if isinstance(tool_info, dict):
        val = tool_info.get("response_text")
        if isinstance(val, str):
            return val
    return ""


def _load_writer():
    """Lazy-import the writer so a missing module never breaks the hook."""
    sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("tools.notion.wave_lifecycle_writer")
    except ImportError as exc:
        _log({"event": "writer_import_failed", "error": repr(exc)})
        return None


def _load_updater():
    """Lazy-import the plan wave table updater."""
    sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("tools.windsurf._plan_wave_table_updater")
    except ImportError as exc:
        _log({"event": "updater_import_failed", "error": repr(exc)})
        return None


def _update_plan_files(markers: list[Any]) -> None:
    """Apply wave-table status updates to on-disk plan .md files.

    Iterates parsed WaveLifecycleMarker objects and calls update_wave_in_plan
    for each. Fail-open: logs errors, never raises.
    """
    if os.environ.get("WAVE_TABLE_UPDATE_BYPASS") == "1":
        _log({"event": "wave_table_update_bypass"})
        return

    updater = _load_updater()
    if updater is None:
        return

    for marker in markers:
        kind = marker.kind
        slug = marker.slug
        wave = marker.wave  # may be None for plan_complete / phase_complete

        if kind == "phase_complete":
            # Phase inline field updates (PHASE_STATUS, PHASE_COMPLETE in prose)
            phase_id = marker.phase or ""
            if not phase_id:
                _log({"event": "phase_complete_no_phase_id", "slug": slug})
                continue
            try:
                ok, msg = updater._update_phase_in_plan(REPO_ROOT, slug, phase_id, kind)
            except Exception as exc:  # noqa: BLE001
                _log({"event": "phase_table_update_error", "slug": slug, "phase": phase_id, "error": repr(exc)})
                continue
            _log({"event": "phase_table_update", "slug": slug, "phase": phase_id, "ok": ok, "msg": msg})
            if not ok:
                print(
                    f"[wave_lifecycle_capture] plan-file update failed slug={slug} phase={phase_id}: {msg}",
                    file=sys.stderr,
                )
            continue

        # plan_complete: wave=None signals "mark all remaining as done"
        effective_wave = wave if wave is not None else -1

        try:
            ok, msg = updater.update_wave_in_plan(REPO_ROOT, slug, effective_wave, kind)
        except Exception as exc:  # noqa: BLE001
            _log({"event": "wave_table_update_error", "slug": slug, "kind": kind, "error": repr(exc)})
            continue

        _log({"event": "wave_table_update", "slug": slug, "kind": kind, "wave": wave, "ok": ok, "msg": msg})
        if not ok:
            print(
                f"[wave_lifecycle_capture] plan-file update failed slug={slug} kind={kind}: {msg}",
                file=sys.stderr,
            )

        # Auto-capture test/scope delta from note= into wave table columns
        if kind == "wave_complete" and wave is not None and getattr(marker, "note", None):
            try:
                note_ok, note_msg = updater.update_wave_note_columns(REPO_ROOT, slug, wave, marker.note)
            except Exception as exc:  # noqa: BLE001
                _log({"event": "note_column_update_error", "slug": slug, "wave": wave, "error": repr(exc)})
                continue
            _log({"event": "note_column_update", "slug": slug, "wave": wave, "ok": note_ok, "msg": note_msg})


def _warn_unresolvable_slugs(markers: list[Any]) -> None:
    """Emit a loud stderr warning for any marker whose slug can't resolve to a plan file.

    This makes silent misses visible — previously markers were dropped silently
    when the slug didn't match the exact filename (e.g. numeric-prefix plans,
    non-hex-suffix master plans).
    """
    updater = _load_updater()
    if updater is None:
        return
    seen: set[str] = set()
    for marker in markers:
        slug = marker.slug
        if not slug or slug in seen:
            continue
        seen.add(slug)
        plan_file = updater._find_plan_file(REPO_ROOT, slug)
        if plan_file is None:
            msg = (
                f"[wave_lifecycle_capture] WARN: slug '{slug}' in marker "
                f"kind={marker.kind} could not be resolved to a plan file under "
                f".claude/plans/. The wave/phase status table was NOT updated. "
                f"Check that the plan_id: frontmatter or filename matches the slug "
                f"used in the WAVE_COMPLETE:/PHASE_COMPLETE: marker."
            )
            print(msg, file=sys.stderr)
            _log({"event": "unresolvable_slug", "slug": slug, "kind": marker.kind})


def main() -> int:
    if os.environ.get("WAVE_LIFECYCLE_CAPTURE_BYPASS") == "1":
        _log({"event": "capture_bypass"})
        return 0

    if sys.stdin.isatty():
        # Standalone-invocation guard: avoid hanging on inherited stdin.
        return 0

    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return 0
    if not raw.strip():
        return 0
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"response_text": raw}

    text = _extract_response_text(payload)
    if not text:
        return 0

    writer = _load_writer()
    if writer is None:
        return 0

    # W1.P1 (plan-complete-notion-status-enforcement-a7e2d1): warn loudly when
    # NOTION_TOKEN is absent so silent-skip failures are observable.
    if not (os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")):
        print(
            "[wave_lifecycle_capture] WARN: NOTION_TOKEN not set — "
            "wave lifecycle markers parsed but Notion PATCH will be skipped",
            file=sys.stderr,
        )
        _log({"event": "capture_no_token_warn"})

    # Parse markers once so both Notion sync and plan-file update share the same list.
    sys.path.insert(0, str(REPO_ROOT))
    try:
        helpers = importlib.import_module("tools.notion._wave_lifecycle_helpers")
        markers = helpers.parse_wave_lifecycle_markers(text)
    except (ImportError, Exception) as exc:
        _log({"event": "marker_parse_failed", "error": repr(exc)})
        markers = []

    try:
        rows = writer.emit_from_markers(text, dry_run=False)
    except (OSError, ValueError) as exc:
        _log({"event": "emit_from_markers_failed", "error": repr(exc)})
        rows = []

    # Update on-disk plan .md wave tables.
    if markers:
        _update_plan_files(markers)
        _warn_unresolvable_slugs(markers)

    if not rows:
        return 0

    captured = sum(1 for _slug, ok, _msg in rows if ok)
    failed = sum(1 for _slug, ok, _msg in rows if not ok)

    _log(
        {
            "event": "capture_summary",
            "captured": captured,
            "failed": failed,
            "rows": [{"slug": s, "ok": ok, "msg": m} for s, ok, m in rows],
        }
    )

    if captured or failed:
        print(
            f"[wave_lifecycle_capture] applied {captured} marker(s); "
            f"{failed} failed (see artifacts/cursor/wave_lifecycle_capture.jsonl)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
