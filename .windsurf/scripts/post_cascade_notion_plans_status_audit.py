#!/usr/bin/env python3
"""post_cascade_notion_plans_status_audit.py — Plans DB Status drift detector.

Reads the Cascade response from stdin (post_cascade_response payload).
Detects any API-post-page / API-patch-page invocation in the response that
targets the Plans DB and writes a non-canonical Status value.

Why post-cascade (advisory) instead of pre_mcp_tool_use (blocking):
Windsurf's pre_mcp_tool_use hook does NOT expose tool arguments to hook
scripts (verified in pre_mcp_gate.py line ~1042). Content-level validation
of a Notion write payload is impossible at the pre-MCP layer. Post-cascade
scanning of the emitted response text is the only hook that can see the
actual Status value being written.

Violations are logged to
  artifacts/windsurf/notion_plans_status_violations.jsonl

Policy: advisory only -- always exits 0, never blocks. The CI drift gate
ops_scripts/ci/check_notion_plans_status_drift.py is the second line of
defense that queries the live DB.

Constitutional rule: .windsurf/rules/notion-plans-taxonomy.md > CANONICAL
Status option strings (2026-05-03).

Bypass: NOTION_PLANS_STATUS_BYPASS=1 env var -- logs a bypass row and exits 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]
violations_log = (
    repo_root / "artifacts" / "windsurf" / "notion_plans_status_violations.jsonl"
)

# Make helper importable when hook runs from any cwd.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from _notion_plans_status_check import decide as _decide  # type: ignore
    from _notion_plans_status_check import PLANS_DB_ID, PLANS_DATA_SOURCE_ID  # type: ignore
except ImportError:  # fail-open: missing helper must never wedge a turn
    _decide = None  # type: ignore[assignment]
    PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
    PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"


# ---------------------------------------------------------------------------
# Response-text scanning regexes.
# ---------------------------------------------------------------------------

# Match an <invoke name="API-post-page"> or API-patch-page block and capture
# the inner text. Name may carry an "mcpN_" prefix from the Windsurf tool-
# proxy layer -- we strip it implicitly via the optional non-capturing group.
_INVOKE_BLOCK_RE = re.compile(
    r'<invoke\s+name="(?:mcp\d+_)?(API-(?:post|patch)-page)">(.*?)</invoke>',
    re.DOTALL,
)

# A <parameter name="X">VALUE block inside an invoke. We intentionally do
# NOT match the closing tag here to avoid colliding with any nested markup;
# the value captures until the next </ (close-tag start) OR the next
# <parameter which starts a sibling parameter.
_PARAM_BLOCK_RE = re.compile(
    r'<parameter\s+name="([^"]+)">(.*?)(?=</parameter>|<parameter\s+name=")',
    re.DOTALL,
)

# Match a Status.select.name write anywhere in a JSON-ish parameter body.
# Accepts single or double quotes around the key/value and arbitrary
# whitespace. Covers these shapes:
#   "Status": {"select": {"name": "Draft"}}
#   'Status': { 'select': { 'name': 'Draft' } }
_STATUS_SELECT_RE = re.compile(
    r'["\']Status["\']\s*:\s*\{\s*["\']select["\']\s*:\s*\{\s*["\']name["\']\s*:'
    r"\s*[\"']([^\"']+)[\"']",
    re.DOTALL,
)

# Match a parent.database_id or direct database_id inside the properties
# parameter to identify the write target.
_DB_ID_RE = re.compile(
    r'["\'](?:database_id|data_source_id)["\']\s*:\s*["\']([0-9a-fA-F\-]+)["\']'
)


def _is_plans_id(candidate: str) -> bool:
    norm = candidate.replace("-", "").lower()
    return norm in {
        PLANS_DB_ID.replace("-", "").lower(),
        PLANS_DATA_SOURCE_ID.replace("-", "").lower(),
    }


def detect_violations(response_text: str) -> list[dict[str, Any]]:
    """Scan response_text and return Plans-Status violations.

    A violation is any API-post-page / API-patch-page invocation whose body
    (a) references a Plans DB / data-source id AND (b) writes a Status
    value outside the canonical six-option set.
    """
    violations: list[dict[str, Any]] = []
    if not response_text or _decide is None:
        return violations

    for invoke_idx, match in enumerate(_INVOKE_BLOCK_RE.finditer(response_text)):
        tool_name = match.group(1)
        body = match.group(2)

        # Collect every database_id / data_source_id mentioned in the invoke
        # body. If none of them are the Plans surface, skip.
        candidate_ids = _DB_ID_RE.findall(body)
        plans_match = any(_is_plans_id(cid) for cid in candidate_ids)

        # Second signal: page_id writes on Plans use API-patch-page with
        # page_id alone -- no database_id in the body. We can't be 100%
        # sure those target Plans from response text alone. Conservative
        # policy: only flag when we can positively identify a Plans id in
        # the body. This keeps the audit low-false-positive.
        if not plans_match:
            continue

        for status_match in _STATUS_SELECT_RE.finditer(body):
            value = status_match.group(1)
            verdict = _decide(PLANS_DB_ID, "Status", value)
            if verdict is None:
                continue
            violations.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "severity": "error",
                    "tool": tool_name,
                    "invoke_index": invoke_idx,
                    "offending_value": value,
                    "suggested": verdict.suggested,
                    "message": verdict.message,
                    "rule": "constitutional.md, notion-plans-taxonomy.md",
                    "plan": "notion-plans-status-enforcement-7a1e2d",
                }
            )

    return violations


def _append(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit write non-fatal
        pass


def _append_bypass() -> None:
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": "info",
                        "violation_type": "bypass",
                        "reason": "NOTION_PLANS_STATUS_BYPASS=1",
                    }
                )
                + "\n"
            )
    except OSError:  # guardian: allow-silent-swallow -- audit write non-fatal
        pass


def _is_bypass() -> bool:
    return os.environ.get("NOTION_PLANS_STATUS_BYPASS", "").strip() == "1"


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info", payload)
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        for key in ("response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def main() -> int:
    # Standalone-invocation guard
    if sys.stdin.isatty():
        return 0
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    if _is_bypass():
        _append_bypass()
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    try:
        violations = detect_violations(text)
    except re.error:
        return 0

    if violations:
        _append(violations)
        print(
            f"[notion_plans_status_audit] DETECTED {len(violations)} "
            f"non-canonical Plans Status write(s). See: "
            f"artifacts/windsurf/notion_plans_status_violations.jsonl",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
