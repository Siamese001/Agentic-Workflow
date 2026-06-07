#!/usr/bin/env python3
"""post_cursor_agent_next_step_capture.py — Windsurf post_cursor_agent_response hook.

Sibling to post_cursor_agent_deferred_scope_capture.py. Parses `NEXT_STEP:`
markers emitted by Cursor Agent when suggesting follow-up work, scaffolds a plan
file if requested (`plan=NEW:<slug>`), and auto-posts to the Wave/Phase
Convergence Notion DB with a `[NEXT·P{n}]` Phase Title prefix so next-step
rows are visually distinct from scored DEFERRED rows.

Policy SSOT: .claude/rules/next-step-capture.md
Scaffolder:  .claude/governance/scripts/_deferred_scope_plan_scaffold.py (shared)
Notion DB:   aa8d2507-101e-4384-81d9-60ea3fe33876 (Wave/Phase Convergence)

Marker format:
    NEXT_STEP: plan=<slug-or-NEW:slug> title=<short> priority=<P2..P5>
        est_tokens=<N> reason=<why> [wave=...] [phase=...] [depends_on=...]

Behavior (ADVISORY — always exits 0):
    - Valid markers → auto-POST to Notion (if NOTION_TOKEN set)
    - Missing token  → log 'pending_no_token' for next-session recovery
    - Malformed      → log violation, skip
    - Duplicates     → dedup local log (7-day) + Notion authoritative query

Escape hatch: NEXT_STEP_CAPTURE_BYPASS=1
Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths; stdlib only (urllib for Notion API).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CAPTURE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "next_step_capture.jsonl"

import sys as _sys

_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_HTTP_TIMEOUT_S,
    NOTION_POST_URL,
    WAVE_PHASE_DATA_SOURCE_ID as WAVE_PHASE_DS_ID,
    WAVE_PHASE_DB_ID,
    query_url,
)

NOTION_QUERY_URL = query_url(WAVE_PHASE_DS_ID)

DEDUP_WINDOW_MINUTES = 10080  # 7 days — same as DEFERRED_SCOPE

ALLOWED_PRIORITIES = {"P2", "P3", "P4", "P5"}
DEFAULT_WAVE = "W-NEXT"

# Path wiring so sibling modules import cleanly
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _deferred_scope_plan_scaffold import scaffold_plan_if_needed  # type: ignore
except ImportError:  # fail-open if scaffolder missing
    scaffold_plan_if_needed = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Marker parsing
# ---------------------------------------------------------------------------

MARKER_RE = re.compile(
    r"^\s*NEXT_STEP:\s*(?P<body>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
KV_RE = re.compile(r"(\w+)=((?:\"[^\"]*\")|(?:\S+))")
# `reason=` and `title=` may contain spaces — captured greedily up to (but not
# consuming) the next ``<key>=`` boundary. Lookahead keeps match.end() at the
# boundary so subsequent KV parsing still sees the following fields.
_TRAILING_FIELD_RE = {
    "reason": re.compile(r"reason=(.+?)(?=\s+\w+=|\s*$)", re.IGNORECASE),
    "title": re.compile(r"title=(.+?)(?=\s+\w+=|\s*$)", re.IGNORECASE),
}

REQUIRED_FIELDS = {"plan", "title", "priority", "est_tokens", "reason"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _append_log(record: dict[str, Any]) -> None:
    try:
        CAPTURE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CAPTURE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[next_step_capture] log write failed: {exc}", file=sys.stderr)


def _read_stdin_response() -> str:
    try:
        payload = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return ""
    try:
        # Reuse the shared Cursor Agent payload extractor for tool_info.response nesting.
        from _post_cursor_agent_payload import extract_response_text  # noqa: PLC0415

        return extract_response_text(payload)
    except ImportError:
        # Fallback: try JSON parse then raw text.
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                info = obj.get("tool_info") or {}
                return str(info.get("response") or obj.get("response") or payload)
        except (json.JSONDecodeError, ValueError):
            pass
        return payload


def _parse_marker(body: str) -> dict[str, str]:
    """Parse a NEXT_STEP body into a kv dict.

    Handles `reason=` and `title=` specially since both may contain spaces.
    Extracts the greediest-allowed instance of each, then KV-parses the rest.
    """

    fields: dict[str, str] = {}
    working = body
    # Extract multi-word fields first, longest match wins (reason before title
    # arbitrarily — both are disjoint in practice).
    for key, pattern in _TRAILING_FIELD_RE.items():
        match = pattern.search(working)
        if match:
            fields[key] = match.group(1).strip().strip('"')
            # Remove the matched substring so KV parsing doesn't double-count.
            working = working[: match.start()] + working[match.end() :]
    for match in KV_RE.finditer(working):
        key = match.group(1).lower()
        if key in fields:
            continue  # already captured by the multi-word extractor
        value = match.group(2).strip('"')
        fields[key] = value
    return fields


def _validate_marker(fields: dict[str, str]) -> list[str]:
    missing = sorted(REQUIRED_FIELDS - set(fields.keys()))
    if missing:
        return missing
    priority = fields.get("priority", "").upper()
    if priority not in ALLOWED_PRIORITIES:
        return [f"priority must be one of {sorted(ALLOWED_PRIORITIES)}; got {priority!r}"]
    try:
        int(fields["est_tokens"])
    except (ValueError, TypeError):
        return [f"est_tokens must be an integer; got {fields.get('est_tokens')!r}"]
    title = fields.get("title", "").strip()
    if not title or title.upper() == "TBD":
        return ["title must be non-empty and not 'TBD'"]
    return []


def _default_phase_id(slug_or_plan: str, title: str) -> str:
    """Derive a stable phase id from the plan slug + title.

    Hash makes it deterministic per (slug, title) pair so duplicate markers
    within a window dedupe cleanly.
    """

    base = f"{slug_or_plan}|{title}".lower().encode("utf-8")
    digest = hashlib.sha1(base, usedforsecurity=False).hexdigest()[:8]
    return f"NEXT-{digest}"


# ---------------------------------------------------------------------------
# Notion API (stdlib urllib)
# ---------------------------------------------------------------------------


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _build_notion_payload(fields: dict[str, str], plan_filename: str) -> dict[str, Any]:  # noqa: PLR0914
    priority = fields["priority"].upper()
    title = fields["title"].strip()
    reason = fields["reason"].strip()
    wave = (fields.get("wave") or DEFAULT_WAVE).strip()
    phase = fields.get("phase") or _default_phase_id(plan_filename, title)
    depends_on = fields.get("depends_on") or "none declared"
    try:
        est_tokens = int(fields["est_tokens"])
    except ValueError:
        est_tokens = 0

    # MECE schema v2 (2026-04-24): Phase Title is pure human name. NEXT-class
    # markers are distinguished by low Impact Score (0.0) and Wave ID prefix
    # conventions, not by a title-text prefix. Evidence merges what were 3
    # prose fields into one.
    phase_title = title
    evidence = (
        f"Success: TBD — Cursor Agent suggested follow-up; fill on execution start. "
        f"| Blocking: {reason}. Priority={priority}. Auto-captured from NEXT_STEP "
        f"marker {_utc_today_iso()}. "
        f"| Deps: {depends_on}."
    )

    properties: dict[str, Any] = {
        # Identity axis
        "Phase Title": {"title": [{"text": {"content": phase_title}}]},
        "Phase ID": {"rich_text": [{"text": {"content": phase}}]},
        "Wave ID": {"rich_text": [{"text": {"content": wave}}]},
        "Plan File": {"rich_text": [{"text": {"content": plan_filename}}]},
        # Classification axis
        "P-Band": {"select": {"name": priority}},
        "Impact Score": {"number": 0.0},  # next-step does not use the scorer
        # Lifecycle axis
        "Status": {"select": {"name": "Todo"}},
        "Est Tokens": {"number": est_tokens},
        # Files & outcome
        "Files In Scope": {"rich_text": [{"text": {"content": "TBD — Cursor Agent to fill on execution start."}}]},
        "Evidence": {"rich_text": [{"text": {"content": evidence}}]},
    }
    # MECE v2 RETIRED (stop writing): Sub-Wave, Parent Plan Summary, Blocking Items,
    # Success Criteria, Dependencies, Last Scored. Merged into Evidence or derivable.

    return {
        "parent": {"database_id": WAVE_PHASE_DB_ID},
        "properties": properties,
    }


def _notion_post(payload: dict[str, Any], token: str) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        NOTION_POST_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data) if data else {}


def _notion_duplicate_exists(plan_file: str, wave: str, phase: str, token: str) -> bool:
    query = {
        "filter": {
            "and": [
                {"property": "Plan File", "rich_text": {"equals": plan_file}},
                {"property": "Wave ID", "rich_text": {"equals": wave}},
                {"property": "Phase ID", "rich_text": {"equals": phase}},
            ]
        },
        "page_size": 5,
    }
    try:
        req = urllib.request.Request(
            NOTION_QUERY_URL,
            data=json.dumps(query).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        ValueError,
    ):
        return False  # fail-open — do not suppress legit posts on transient error

    closed = {"Done", "Closed", "Cancelled", "Archived"}
    for page in data.get("results", []):
        if page.get("archived") or page.get("in_trash"):
            continue
        status = (page.get("properties", {}).get("Status", {}).get("select") or {}).get("name", "")
        if status not in closed:
            return True
    return False


def _recent_duplicate(plan: str, wave: str, phase: str) -> bool:
    if not CAPTURE_LOG.exists():
        return False
    cutoff = datetime.now(timezone.utc).timestamp() - DEDUP_WINDOW_MINUTES * 60
    key = f"{plan}|{wave}|{phase}"
    try:
        with CAPTURE_LOG.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if rec.get("kind") != "auto_posted":
                    continue
                ts_iso = rec.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_iso).timestamp()
                except (ValueError, TypeError):
                    continue
                if ts < cutoff:
                    continue
                marker = rec.get("marker", {})
                rec_key = f"{marker.get('plan', '')}|{marker.get('wave', '')}|{marker.get('phase', '')}"
                if rec_key == key:
                    return True
    except OSError:
        return False
    return False


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------


def _process_marker(fields: dict[str, str], token: str | None) -> dict[str, Any]:
    missing = _validate_marker(fields)
    if missing:
        return {
            "timestamp": _utc_now_iso(),
            "kind": "malformed_marker",
            "errors": missing,
            "marker": fields,
        }

    # Normalize priority to upper-case for consistency.
    fields = {**fields, "priority": fields["priority"].upper()}

    # Scaffold plan file if NEW:<slug>. Shared with DEFERRED_SCOPE.
    plan_filename = ""
    scaffold_info: dict[str, Any] = {}
    if scaffold_plan_if_needed is not None:
        try:
            scaffold_result = scaffold_plan_if_needed(fields, REPO_ROOT)
            plan_filename = scaffold_result.plan_filename
            scaffold_info = {
                "plan_filename": scaffold_result.plan_filename,
                "created": scaffold_result.created,
                "reason": scaffold_result.reason,
            }
        except (OSError, RuntimeError, ValueError) as exc:
            scaffold_info = {"error": f"scaffold failed: {exc}"}

    # Fall-back if scaffold unavailable — derive a filename from the plan field.
    if not plan_filename:
        raw_plan = fields["plan"]
        if raw_plan.upper().startswith("NEW:"):
            raw_plan = raw_plan[4:]
        plan_filename = raw_plan if raw_plan.endswith(".md") else f"{raw_plan}.md"

    # Normalize wave/phase defaults now so dedup works consistently.
    wave = (fields.get("wave") or DEFAULT_WAVE).strip()
    phase = fields.get("phase") or _default_phase_id(plan_filename, fields["title"])
    fields = {**fields, "wave": wave, "phase": phase}

    base_record: dict[str, Any] = {
        "timestamp": _utc_now_iso(),
        "marker": fields,
        "plan_filename": plan_filename,
    }
    if scaffold_info:
        base_record["scaffold"] = scaffold_info

    if _recent_duplicate(plan_filename, wave, phase):
        return {**base_record, "kind": "skipped_recent_duplicate"}

    if not token:
        return {
            **base_record,
            "kind": "pending_no_token",
            "reason": "NOTION_TOKEN not set; next session will pick up",
        }

    if _notion_duplicate_exists(plan_filename, wave, phase, token):
        return {**base_record, "kind": "skipped_notion_duplicate"}

    try:
        payload = _build_notion_payload(fields, plan_filename)
        resp = _notion_post(payload, token)
    except urllib.error.HTTPError as exc:
        return {
            **base_record,
            "kind": "post_http_error",
            "status": exc.code,
            "error": str(exc),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {**base_record, "kind": "post_transport_error", "error": str(exc)}
    except (json.JSONDecodeError, ValueError) as exc:
        return {**base_record, "kind": "post_decode_error", "error": str(exc)}

    return {
        **base_record,
        "kind": "auto_posted",
        "notion_page_id": resp.get("id"),
        "notion_url": resp.get("url"),
    }


def main() -> int:
    if os.environ.get("NEXT_STEP_CAPTURE_BYPASS") == "1":
        _append_log(
            {
                "timestamp": _utc_now_iso(),
                "kind": "bypass",
                "reason": "NEXT_STEP_CAPTURE_BYPASS=1",
            }
        )
        return 0

    if sys.stdin.isatty():
        print(
            "[next_step_capture] no stdin payload (TTY detected) — exiting 0. "
            "This script is a post_cursor_agent_response hook.",
            file=sys.stderr,
        )
        return 0

    response = _read_stdin_response()
    if not response or "NEXT_STEP:" not in response:
        return 0

    marker_bodies = [m.group("body") for m in MARKER_RE.finditer(response)]
    if not marker_bodies:
        return 0

    token = _notion_token()
    summary: dict[str, int] = {}
    for body in marker_bodies:
        fields = _parse_marker(body)
        record = _process_marker(fields, token)
        _append_log(record)
        kind = record.get("kind", "unknown")
        summary[kind] = summary.get(kind, 0) + 1

    if summary:
        summary_str = ", ".join(f"{k}={v}" for k, v in sorted(summary.items()))
        print(
            f"[next_step_capture] markers={len(marker_bodies)} {summary_str} "
            f"-> log: {CAPTURE_LOG.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[next_step_capture] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
