#!/usr/bin/env python3
"""post_cursor_agent_plans_dup_audit.py — advisory duplicate-POST detector.

Scans Cursor Agent response text for any ``API-post-page`` targeting the Plans
DB whose Slug already maps to one or more active rows in the local
plan_registration_cache.json snapshot.

Why advisory (post-cursor-agent) and not blocking (pre-mcp): Windsurf's
``pre_mcp_tool_use`` hook does NOT expose tool arguments to scripts (verified
in pre_mcp_gate.py). Content-level validation of the POST payload is only
possible after the response is emitted. Pair this with the fail-closed CI
gate ``ops_scripts/ci/check_notion_plans_no_duplicates.py``.

Violations are appended to:
    artifacts/cursor/notion_plans_dup_violations.jsonl

Bypass: ``NOTION_PLANS_DUP_BYPASS=1``.

RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B.
Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2c).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from _plans_dup_detector import (  # noqa: E402
    PlansPostInvocation,
    extract_plans_post_invocations,
)

CACHE_PATH = REPO_ROOT / ".claude" / "state" / "plan_registration_cache.json"
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "windsurf" / "notion_plans_dup_violations.jsonl"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _is_bypass() -> bool:
    return os.environ.get("NOTION_PLANS_DUP_BYPASS", "").strip() == "1"


def _append(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        info = payload.get("tool_info", payload)
        if isinstance(info, dict):
            for k in ("response", "text", "content"):
                v = info.get(k)
                if isinstance(v, str) and v.strip():
                    return v
        for k in ("response", "text", "content"):
            v = payload.get(k)
            if isinstance(v, str) and v.strip():
                return v
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def detect(
    response_text: str,
    cache: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return one violation record per Plans-DB POST whose slug already exists."""
    if cache is None:
        cache = _load_cache()
    invocations: list[PlansPostInvocation] = extract_plans_post_invocations(
        response_text
    )
    if not invocations:
        return []

    plans_map = (cache or {}).get("plans") or {}
    if not isinstance(plans_map, dict):
        plans_map = {}

    violations: list[dict[str, Any]] = []
    for inv in invocations:
        if not inv.slug:
            # Cannot dedupe without a slug; emit a low-severity advisory.
            violations.append({
                "timestamp": _now_iso(),
                "severity": "warning",
                "violation_type": "plans_post_missing_slug",
                "invoke_index": inv.invoke_index,
                "message": (
                    "Plans-DB POST emitted without a parseable Slug — "
                    "register_plan_idempotent() requires a slug for dedup."
                ),
            })
            continue
        entry = plans_map.get(inv.slug) if isinstance(plans_map, dict) else None
        if entry:  # cache says the slug already has a Plans row
            page_id = ""
            status = ""
            if isinstance(entry, dict):
                page_id = str(entry.get("page_id") or "")
                status = str(entry.get("status") or "")
            violations.append({
                "timestamp": _now_iso(),
                "severity": "error",
                "violation_type": "plans_post_for_existing_slug",
                "invoke_index": inv.invoke_index,
                "slug": inv.slug,
                "existing_page_id": page_id,
                "existing_status": status,
                "message": (
                    f"Plans-DB POST for slug={inv.slug!r} would create a duplicate. "
                    f"Existing row: page_id={page_id!r} status={status!r}. "
                    "Use register_plan_idempotent() to dedup."
                ),
                "remediation": (
                    "Replace direct API-post-page with "
                    "tools/notion/_plan_registration_helpers.register_plan_idempotent()."
                ),
                "rule": "constitutional.md §36, RCA NOTION_PLANS_STATUS_RCA_2026-05-10",
                "plan": "notion-plans-status-rca-followups-b8e3f2",
            })
    return violations


def main() -> int:
    if sys.stdin.isatty():
        return 0
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    if _is_bypass():
        _append([{
            "timestamp": _now_iso(),
            "severity": "info",
            "violation_type": "bypass",
            "reason": "NOTION_PLANS_DUP_BYPASS=1",
        }])
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    violations = detect(text)
    if violations:
        _append(violations)
        # Print a one-liner advisory to stderr per violation.
        for v in violations:
            print(
                f"[plans_dup_audit] {v.get('severity', 'error').upper()} "
                f"{v.get('violation_type')} slug={v.get('slug', '?')!r}: "
                f"{v.get('message', '')}",
                file=sys.stderr,
            )
    return 0  # advisory only — never block


if __name__ == "__main__":
    sys.exit(main())
