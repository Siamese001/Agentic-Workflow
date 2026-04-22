#!/usr/bin/env python3
"""
post_cascade_deferred_scope_capture.py — Windsurf post_cascade_response hook.

Parses DEFERRED_SCOPE markers in Cascade's response, scores each to a P1..P5
priority band via tools.priority.deferred_scope_scorer, and either confirms
a matching Notion writeback happened in the same response (via WRITEBACK:
receipt) or auto-posts a Wave/Phase Convergence row.

Policy SSOT: .windsurf/rules/deferred-scope-capture.md
Scorer SSOT: tools/priority/deferred_scope_scorer.py
Notion DB:   aa8d2507-101e-4384-81d9-60ea3fe33876 (Wave/Phase Convergence)

Marker format (from rule):
    DEFERRED_SCOPE: plan=<slug> wave=<wave_id> phase=<phase_id>
        layer=<L0..L6|L_*> fan_in=<N> surface=<surface>
        coverage_gap_pct=<N.N> est_tokens=<N> reason=<short>

Behavior (ADVISORY — always exits 0):
    - Detected markers logged to artifacts/windsurf/deferred_scope_capture.jsonl
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

FAIL_POLICY = "open"
REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "deferred_scope_capture.jsonl"
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"

# Notion target
WAVE_PHASE_DB_ID = "aa8d2507-101e-4384-81d9-60ea3fe33876"
NOTION_API_VERSION = "2025-09-03"
NOTION_POST_URL = "https://api.notion.com/v1/pages"
NOTION_HTTP_TIMEOUT_S = 15.0

# Ensure repo root on path so scorer import works
sys.path.insert(0, str(REPO_ROOT))
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


def _ensure_log_parent() -> None:
    CAPTURE_LOG.parent.mkdir(parents=True, exist_ok=True)


def _append_log(record: dict[str, Any]) -> None:
    _ensure_log_parent()
    try:
        with CAPTURE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[deferred_scope_capture] log write failed: {exc}", file=sys.stderr)


def _read_stdin_response() -> str:
    try:
        payload = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return ""
    if not payload:
        return ""
    try:
        obj = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return payload
    if isinstance(obj, dict):
        for key in ("response", "content", "text", "message"):
            value = obj.get(key)
            if isinstance(value, str) and value:
                return value
        return json.dumps(obj)
    return payload


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


def _build_notion_payload(fields: dict[str, str], band: str, impact: float) -> dict[str, Any]:
    plan = fields["plan"]
    if plan.startswith("NEW:"):
        plan_slug = plan[4:]
        plan_file = f"{plan_slug}.md"
    else:
        plan_file = plan if plan.endswith(".md") else f"{plan}.md"

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

    phase_title = f"[{band}] {wave} {phase} — {reason}"
    sub_wave = f"{wave}-{band}-AUTO"
    blocking_items = (
        f"{reason}. Layer={layer}, fan_in={fan_in}, surface={surface}, "
        f"coverage_gap_pct={gap}. Priority impact score: {impact}. "
        f"Auto-captured from DEFERRED_SCOPE marker {_utc_today_iso()}."
    )
    parent_summary = (
        f"{plan_file}: deferred scope auto-captured {_utc_today_iso()} via "
        f"post_cascade_deferred_scope_capture hook."
    )

    properties = {
        "Phase Title": {"title": [{"text": {"content": phase_title}}]},
        "Phase ID": {"rich_text": [{"text": {"content": phase}}]},
        "Wave ID": {"rich_text": [{"text": {"content": wave}}]},
        "Sub-Wave": {"rich_text": [{"text": {"content": sub_wave}}]},
        "Dependencies": {
            "rich_text": [
                {
                    "text": {
                        "content": (
                            "Auto-captured from DEFERRED_SCOPE marker. "
                            "Review before execution."
                        )
                    }
                }
            ]
        },
        "Success Criteria": {
            "rich_text": [
                {
                    "text": {
                        "content": (
                            "See Blocking Items for scope; Cascade to fill "
                            "on execution start."
                        )
                    }
                }
            ]
        },
        "Files In Scope": {
            "rich_text": [
                {"text": {"content": "TBD — Cascade to fill on execution start."}}
            ]
        },
        "Parent Plan Summary": {"rich_text": [{"text": {"content": parent_summary}}]},
        "Plan File": {"rich_text": [{"text": {"content": plan_file}}]},
        "Status": {"select": {"name": "Todo"}},
        "Est Tokens": {"number": est_tokens},
        "Blocking Items": {"rich_text": [{"text": {"content": blocking_items}}]},
    }

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


def _recent_duplicate(plan: str, wave: str, phase: str, window_minutes: int = 60) -> bool:
    """Return True if the same (plan, wave, phase) was logged in the last hour."""
    if not CAPTURE_LOG.exists():
        return False
    cutoff = datetime.now(timezone.utc).timestamp() - window_minutes * 60
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
                rec_key = (
                    f"{marker.get('plan', '')}|"
                    f"{marker.get('wave', '')}|"
                    f"{marker.get('phase', '')}"
                )
                if rec_key == key:
                    return True
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
        result = score_deferred_scope(
            layer=fields["layer"],
            fan_in=int(fields["fan_in"]),
            surface=fields["surface"],
            coverage_gap_pct=float(fields["coverage_gap_pct"]),
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

    # Cascade already wrote to Notion — just record the confirmation
    if has_receipt:
        return {**base_record, "kind": "confirmed_by_receipt"}

    # Dedup guard
    if _recent_duplicate(fields["plan"], fields["wave"], fields["phase"]):
        return {**base_record, "kind": "skipped_recent_duplicate"}

    # Auto-post to Notion
    if not token:
        return {
            **base_record,
            "kind": "pending_no_token",
            "reason": "NOTION_TOKEN not set; next session will pick up",
        }

    try:
        payload = _build_notion_payload(fields, result.band, result.impact_score)
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
            f"-> log: {CAPTURE_LOG.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[deferred_scope_capture] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
