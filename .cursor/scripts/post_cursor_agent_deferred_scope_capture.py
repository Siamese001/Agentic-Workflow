#!/usr/bin/env python3
"""
post_cursor_agent_deferred_scope_capture.py — Windsurf post_cursor_agent_response hook.

Parses DEFERRED_SCOPE markers in Cursor Agent's response, scores each to a P1..P5
priority band via tools.priority.deferred_scope_scorer, and either confirms
a matching Notion writeback happened in the same response (via WRITEBACK:
receipt) or auto-posts a Wave/Phase Convergence row.

Policy SSOT: .cursor/rules/deferred-scope-capture.md
Scorer SSOT: tools/priority/deferred_scope_scorer.py
Notion DB:   aa8d2507-101e-4384-81d9-60ea3fe33876 (Wave/Phase Convergence)

Marker format (from rule):
    DEFERRED_SCOPE: plan=<slug> wave=<wave_id> phase=<phase_id>
        layer=<L0..L6|L_*> fan_in=<N> surface=<surface>
        coverage_gap_pct=<N.N> est_tokens=<N> reason=<short>

Behavior (ADVISORY — always exits 0):
    - Detected markers logged to artifacts/cursor/deferred_scope_capture.jsonl
    - Missing-writeback markers trigger auto-POST to Notion (if NOTION_TOKEN set)
    - Auto-post failures logged as 'pending' for next-session recovery
    - Malformed markers logged as violations

Escape hatch: DEFERRED_SCOPE_CAPTURE_BYPASS=1 → logs bypass row and exits 0.

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — repo_root resolved from __file__.
No third-party deps — urllib only.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys as _sys

_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    NOTION_HTTP_TIMEOUT_S,
    NOTION_POST_URL,
    PLANS_DATA_SOURCE_ID,
    WAVE_PHASE_DATA_SOURCE_ID as WAVE_PHASE_DS_ID,
    WAVE_PHASE_DB_ID,
)


try:
    from tqdm import tqdm as _tqdm
except ImportError:  # fail-open: tqdm unavailable in hook context
    _tqdm = None  # type: ignore[assignment]

FAIL_POLICY = "open"
REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_LOG_NAME = "deferred_scope_capture.jsonl"
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"

# Notion target

# Wave/Phase Convergence data_source_id (reads). Distinct from database_id (writes).

NOTION_QUERY_URL = f"https://api.notion.com/v1/data_sources/{WAVE_PHASE_DS_ID}/query"

# Dedup window: local log lookback widened from 60 min to 7 days (10080 min).
# Notion pre-check catches older/cross-session duplicates authoritatively.
DEDUP_WINDOW_MINUTES = 10080

# Numeric Priority field values per band — ensures Notion sorts/filters work
# regardless of whether the [Pn] prefix is parsed from Phase Title.
BAND_TO_PRIORITY: dict[str, int] = {
    "P1": 10,
    "P2": 20,
    "P3": 30,
    "P4": 40,
    "P5": 50,
}

# Ensure repo root on path so scorer import works, and scripts dir for sibling helpers.
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from tools.priority.deferred_scope_scorer import score_deferred_scope  # type: ignore
except ImportError:  # fail-open if scorer missing
    score_deferred_scope = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Marker parsing
# ---------------------------------------------------------------------------

# Captures key=value pairs; value is non-space chunk OR quoted-string.
# `reason=` is the last field and may contain spaces — captured greedily to EOL.
MARKER_RE = re.compile(
    r"^\s*DEFERRED_SCOPE:\s*(?P<body>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
KV_RE = re.compile(r"(\w+)=((?:\"[^\"]*\")|(?:\S+))")
REASON_RE = re.compile(r"reason=(.+?)(?:\s+(?:\w+)=|\s*$)", re.IGNORECASE)

REQUIRED_FIELDS = {
    "plan",
    "wave",
    "phase",
    "layer",
    "fan_in",
    "surface",
    "coverage_gap_pct",
    "est_tokens",
    "reason",
}

# Writeback receipt format (match writeback_audit)
RECEIPT_RE = re.compile(
    r"WRITEBACK:\s*target=notion\s*,\s*kind=wave_phase\s*,\s*id=(?P<id>[\S]+)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _capture_log_path() -> Path:
    from ops_scripts.ci._governance_paths import governance_artifact_log  # noqa: PLC0415

    return governance_artifact_log(CAPTURE_LOG_NAME)


def _append_log(record: dict[str, Any]) -> None:
    try:
        from ops_scripts.ci._governance_paths import append_governance_artifact_jsonl  # noqa: PLC0415

        append_governance_artifact_jsonl(CAPTURE_LOG_NAME, record)
    except OSError as exc:
        print(f"[deferred_scope_capture] log write failed: {exc}", file=sys.stderr)


def _read_stdin_response() -> str:
    try:
        payload = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return ""
    # Delegate to shared extractor — handles tool_info.response nesting
    # (documented Windsurf post_cursor_agent_response shape).
    from _post_cursor_agent_payload import extract_response_text  # noqa: PLC0415

    return extract_response_text(payload)


def _parse_marker(body: str) -> dict[str, str]:
    """Parse a single DEFERRED_SCOPE body into a kv dict.

    Handles `reason=...` specially since it may contain spaces and must be last.
    """
    fields: dict[str, str] = {}

    # Extract reason first (everything after reason= until next key= or EOL)
    reason_match = REASON_RE.search(body)
    if reason_match:
        fields["reason"] = reason_match.group(1).strip().strip('"')
        # Remove the reason portion from body before KV parsing
        body_without_reason = body[: reason_match.start()]
    else:
        body_without_reason = body

    for match in KV_RE.finditer(body_without_reason):
        key = match.group(1).lower()
        value = match.group(2).strip('"')
        fields[key] = value

    return fields


def _validate_marker(fields: dict[str, str]) -> list[str]:
    missing = sorted(REQUIRED_FIELDS - set(fields.keys()))
    return missing


# ---------------------------------------------------------------------------
# Notion API (urllib — stdlib only)
# ---------------------------------------------------------------------------


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


PLANS_QUERY_URL = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"


def _plans_query(filter_obj: dict[str, Any], token: str) -> list[dict[str, Any]]:
    """POST a filter query to the Plans data-source; returns results list (fail-open)."""
    try:
        body = json.dumps({"filter": filter_obj, "page_size": 1}).encode("utf-8")
        req = urllib.request.Request(
            PLANS_QUERY_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_API_VERSION,
            },
        )
        with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("results") or []
    except Exception:  # noqa: BLE001  # guardian: allow-broad -- fail-open resolver
        return []


def _resolve_plan_page_id(plan_slug: str, token: str) -> str | None:
    """Resolve a plan slug to a Plans-DB page id.

    Tries three filters in order, each fail-open:
      1. Slug property exact match (if property exists)
      2. Plan File Path rich_text contains slug
      3. Title (Name) contains slug
    Returns None on any failure or miss.
    """
    for filt in (
        {"property": "Slug", "rich_text": {"equals": plan_slug}},
        {"property": "Plan File Path", "rich_text": {"contains": plan_slug}},
        {"property": "Name", "title": {"contains": plan_slug}},
    ):
        results = _plans_query(filt, token)
        if results:
            return results[0].get("id")
    return None


def _build_notion_payload(fields: dict[str, str], band: str, impact: float, token: str | None = None) -> dict[str, Any]:  # noqa: PLR0914
    plan = fields["plan"]
    if plan.startswith("NEW:"):
        plan_slug = plan[4:]
        plan_file = f"{plan_slug}.md"
    else:
        plan_file = plan if plan.endswith(".md") else f"{plan}.md"
        plan_slug = plan_file[:-3] if plan_file.endswith(".md") else plan_file

    wave = fields["wave"]
    phase = fields["phase"]
    reason = fields["reason"]
    layer = fields["layer"]
    fan_in = fields["fan_in"]
    surface = fields["surface"]
    gap = fields["coverage_gap_pct"]
    est_tokens_raw = fields["est_tokens"]
    try:
        est_tokens = int(est_tokens_raw)
    except ValueError:
        est_tokens = 0

    # MECE schema v2 (2026-04-24): Phase Title is pure human name — no [P{band}]
    # or Wave/Phase prefix. P-Band, Wave ID, Phase ID are separate fields already.
    phase_title = reason
    # Evidence merges what were 3 separate prose fields (Success Criteria, Blocking
    # Items, Dependencies) into one authoritative outcome string.
    evidence = (
        f"Success: Auto-captured from DEFERRED_SCOPE marker {_utc_today_iso()} "
        f"— Cursor Agent to fill on execution. "
        f"| Blocking: {reason}. Layer={layer}, fan_in={fan_in}, surface={surface}, "
        f"coverage_gap_pct={gap}. Priority impact score: {impact}. "
        f"| Deps: pending review (auto-captured)."
    )

    try:
        fan_in_int = int(fan_in)
    except (ValueError, TypeError):
        fan_in_int = None

    properties: dict[str, Any] = {
        # Identity axis (3)
        "Phase Title": {"title": [{"text": {"content": phase_title}}]},
        "Phase ID": {"rich_text": [{"text": {"content": phase}}]},
        # Wave ID retained (legacy; used for dedup pre-check query). Schema-MECE gate
        # will flip this to derivation from Phase ID in a later refactor.
        "Wave ID": {"rich_text": [{"text": {"content": wave}}]},
        # Plan File retained for dedup pre-check query; Plan relation below is SSOT.
        "Plan File": {"rich_text": [{"text": {"content": plan_file}}]},
        # Classification axis (5)
        "P-Band": {"select": {"name": band}},
        "Layer": {"select": {"name": layer}},
        "Surface": {"select": {"name": surface}},
        "Impact Score": {"number": round(float(impact), 2)},
        # Lifecycle axis (3) — Status=Not Started (canonical Plans-DB taxonomy; was "Todo"
        # which is not a valid option in Backlog Items DB as of 2026-05-03; renamed
        # from "Draft" → "Not Started" 2026-05-03).
        "Status": {"select": {"name": "Not Started"}},
        "Est Tokens": {"number": est_tokens},
        "Last Updated": {"date": {"start": _utc_today_iso()}},
        # Outcome (1) — MECE v2 merged field
        "Evidence": {"rich_text": [{"text": {"content": evidence}}]},
    }
    if fan_in_int is not None:
        properties["Fan-In"] = {"number": fan_in_int}
    # Plan relation (best-effort, fail-open). Requires NOTION_TOKEN + Plans-DB access.
    if token:
        page_id = _resolve_plan_page_id(plan_slug, token)
        if page_id:
            properties["Plan"] = {"relation": [{"id": page_id}]}
    # MECE v2 deleted from Backlog Items DB 2026-05-03:
    #   Files In Scope, Coverage Gap %, Last Scored, Parent Plan Summary, Sub-Wave,
    #   Blocking Items, Success Criteria, Dependencies.

    return {
        "parent": {"database_id": WAVE_PHASE_DB_ID},
        "properties": properties,
    }


def _notion_post(payload: dict[str, Any], token: str) -> dict[str, Any]:
    """POST to Notion API. Returns parsed JSON response; raises on non-200."""
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


# ---------------------------------------------------------------------------
# Dedup check (lightweight — queries memory DB for recent capture of same key)
# ---------------------------------------------------------------------------


def _notion_duplicate_exists(plan_file: str, wave: str, phase: str, token: str) -> bool:
    """Query Notion Wave/Phase Convergence for an existing non-closed row.

    Matches on (Plan File, Wave ID, Phase ID). Returns True if any row exists
    with Status not in {"Done", "Closed", "Cancelled"}. Fail-open: returns
    False on any network/parse error so a legit post is never suppressed.
    """
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
        body = json.dumps(query).encode("utf-8")
        req = urllib.request.Request(
            NOTION_QUERY_URL,
            data=body,
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
        return False  # fail-open — do not block posting on query failure

    closed_statuses = {"Done", "Closed", "Cancelled", "Archived"}
    for page in data.get("results", []):
        if page.get("archived") or page.get("in_trash"):
            continue
        status_prop = page.get("properties", {}).get("Status", {}).get("select") or {}
        status_name = status_prop.get("name", "")
        if status_name not in closed_statuses:
            return True
    return False


def _recent_duplicate(plan: str, wave: str, phase: str, window_minutes: int = DEDUP_WINDOW_MINUTES) -> bool:
    """Return True if the same (plan, wave, phase) was logged in the last hour."""
    capture_log = _capture_log_path()
    if not capture_log.exists():
        from ops_scripts.ci._governance_paths import read_governance_artifact_jsonl_paths  # noqa: PLC0415

        paths = read_governance_artifact_jsonl_paths(CAPTURE_LOG_NAME)
        if not paths:
            return False
        capture_log = paths[0]
    if not capture_log.exists():
        return False
    cutoff = datetime.now(timezone.utc).timestamp() - window_minutes * 60
    key = f"{plan}|{wave}|{phase}"
    try:
        with capture_log.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
        iterator = _tqdm(lines, desc="dedup-scan", unit="line", disable=True) if _tqdm else lines
        try:
            for line in iterator:
                # progress: bounded hot-hook scan (<1 ms typical); tqdm disabled by design (§16 compliant)
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
        except (json.JSONDecodeError, ValueError, OSError):
            return False
    except OSError:
        return False
    return False


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------


def _process_marker(
    fields: dict[str, str],
    has_receipt: bool,
    token: str | None,
) -> dict[str, Any]:
    """Process one parsed marker. Returns a record to append to the log."""
    missing = _validate_marker(fields)
    if missing:
        return {
            "timestamp": _utc_now_iso(),
            "kind": "malformed_marker",
            "missing_fields": missing,
            "marker": fields,
        }

    if score_deferred_scope is None:
        return {
            "timestamp": _utc_now_iso(),
            "kind": "scorer_unavailable",
            "marker": fields,
        }

    try:
        v2_kwargs: dict[str, Any] = {}
        if "prod_invocations" in fields:
            v2_kwargs["prod_invocations"] = int(fields["prod_invocations"])
        if "trajectory_defect_rate" in fields:
            v2_kwargs["trajectory_defect_rate"] = float(fields["trajectory_defect_rate"])
        if "reversibility" in fields:
            v2_kwargs["reversibility"] = fields["reversibility"]
        if "item_class" in fields:
            v2_kwargs["item_class"] = fields["item_class"]
        if "adds_complexity" in fields:
            v2_kwargs["adds_complexity"] = fields["adds_complexity"].lower() in {"1", "true", "yes"}
        result = score_deferred_scope(
            layer=fields["layer"],
            fan_in=int(fields["fan_in"]),
            surface=fields["surface"],
            coverage_gap_pct=float(fields["coverage_gap_pct"]),
            **v2_kwargs,
        )
    except (ValueError, TypeError) as exc:
        return {
            "timestamp": _utc_now_iso(),
            "kind": "scoring_error",
            "error": str(exc),
            "marker": fields,
        }

    base_record = {
        "timestamp": _utc_now_iso(),
        "marker": fields,
        "band": result.band,
        "impact_score": result.impact_score,
    }

    # Cursor Agent already wrote to Notion — just record the confirmation
    if has_receipt:
        return {**base_record, "kind": "confirmed_by_receipt"}

    # Dedup guard — tier 1: local log (fast, wide 7-day window)
    if _recent_duplicate(fields["plan"], fields["wave"], fields["phase"]):
        return {**base_record, "kind": "skipped_recent_duplicate"}

    # Auto-post to Notion
    if not token:
        return {
            **base_record,
            "kind": "pending_no_token",
            "reason": "NOTION_TOKEN not set; next session will pick up",
        }

    # Dedup guard — tier 2: Notion authoritative pre-check (catches cross-session
    # and cross-machine duplicates the local log can't see). Fail-open so a
    # transient Notion query failure never blocks a legit post.
    plan = fields["plan"]
    plan_file_for_check = (
        f"{plan[4:]}.md" if plan.startswith("NEW:") else (plan if plan.endswith(".md") else f"{plan}.md")
    )
    if _notion_duplicate_exists(plan_file_for_check, fields["wave"], fields["phase"], token):
        return {**base_record, "kind": "skipped_notion_duplicate"}

    try:
        payload = _build_notion_payload(fields, result.band, result.impact_score, token=token)
        resp = _notion_post(payload, token)
    except urllib.error.HTTPError as exc:
        return {
            **base_record,
            "kind": "post_http_error",
            "status": exc.code,
            "error": str(exc),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            **base_record,
            "kind": "post_transport_error",
            "error": str(exc),
        }
    except (json.JSONDecodeError, ValueError) as exc:
        return {
            **base_record,
            "kind": "post_decode_error",
            "error": str(exc),
        }

    return {
        **base_record,
        "kind": "auto_posted",
        "notion_page_id": resp.get("id"),
        "notion_url": resp.get("url"),
    }


def main() -> int:
    if os.environ.get("DEFERRED_SCOPE_CAPTURE_BYPASS") == "1":
        _append_log(
            {
                "timestamp": _utc_now_iso(),
                "kind": "bypass",
                "reason": "DEFERRED_SCOPE_CAPTURE_BYPASS=1",
            }
        )
        return 0

    # Standalone-invocation guard: if stdin is a TTY, no hook payload will
    # ever arrive and sys.stdin.read() would block forever. Exit cleanly so
    # this script is safe to invoke manually via `run_command` / pwsh.
    if sys.stdin.isatty():
        print(
            "[deferred_scope_capture] no stdin payload (TTY detected) — "
            "exiting 0. This script is a post_cursor_agent_response hook and "
            "expects Cursor Agent's response JSON on stdin.",
            file=sys.stderr,
        )
        return 0

    response = _read_stdin_response()
    if not response or "DEFERRED_SCOPE:" not in response:
        return 0

    marker_bodies = [m.group("body") for m in MARKER_RE.finditer(response)]
    if not marker_bodies:
        return 0

    has_receipt = bool(RECEIPT_RE.search(response))
    token = _notion_token()

    summary_counts: dict[str, int] = {}
    for body in marker_bodies:
        fields = _parse_marker(body)
        record = _process_marker(fields, has_receipt, token)
        _append_log(record)
        kind = record.get("kind", "unknown")
        summary_counts[kind] = summary_counts.get(kind, 0) + 1

    if summary_counts:
        summary = ", ".join(f"{k}={v}" for k, v in sorted(summary_counts.items()))
        print(
            f"[deferred_scope_capture] markers={len(marker_bodies)} {summary} "
            f"-> log: {_capture_log_path().relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )

    # W4.3: tail-call snapshot regeneration (throttled, fail-open).
    # Only fire when we actually posted something new — avoids regen on
    # pure confirm_by_receipt / duplicate-skip passes.
    if summary_counts.get("auto_posted", 0) > 0 and token:
        _maybe_regenerate_snapshot(token)

    return 0


# ---------------------------------------------------------------------------
# W4.3: Snapshot regeneration (throttled, fail-open)
# ---------------------------------------------------------------------------

SNAPSHOT_THROTTLE_S = 30
SNAPSHOT_LOCKFILE = REPO_ROOT / "artifacts" / "windsurf" / ".snapshot_last_run"


def _maybe_regenerate_snapshot(token: str) -> None:
    """Call snapshot_renderer.regenerate() if last run was >30s ago.

    Fail-open: any exception is swallowed to keep the hook advisory.
    The in-process import avoids spawning a subprocess (no shared-shell risk).
    """
    try:
        now = datetime.now(timezone.utc).timestamp()
        if SNAPSHOT_LOCKFILE.exists():
            try:
                last = float(SNAPSHOT_LOCKFILE.read_text(encoding="utf-8").strip())
                if now - last < SNAPSHOT_THROTTLE_S:
                    return
            except (ValueError, OSError):
                pass  # corrupt lockfile -> regenerate anyway
        # Import lazily so the hook stays importable even if snapshot_renderer is absent.
        from tools.notion.snapshot_renderer import regenerate  # noqa: PLC0415
        from tools.notion.snapshot_renderer import PAGE_ID_FILE  # noqa: PLC0415

        if not PAGE_ID_FILE.exists():
            return
        page_id = PAGE_ID_FILE.read_text(encoding="utf-8").strip()
        result = regenerate(token, page_id)
        SNAPSHOT_LOCKFILE.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_LOCKFILE.write_text(str(now), encoding="utf-8")
        print(
            f"[deferred_scope_capture] snapshot regenerated "
            f"(rows={result.get('rows')}, {result.get('elapsed_s')}s)",
            file=sys.stderr,
        )
    except (ImportError, OSError, RuntimeError, ValueError) as exc:  # fail-open
        print(
            f"[deferred_scope_capture] snapshot regen skipped: {exc}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[deferred_scope_capture] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
