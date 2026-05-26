#!/usr/bin/env python3
"""post_cursor_agent_notion_plans_status_audit.py — Plans DB Status drift detector.

Reads the Cursor Agent response from stdin (post_cursor_agent_response payload).
Detects any API-post-page / API-patch-page invocation in the response that
targets the Plans DB and writes a non-canonical Status value.

Why post-cursor-agent (advisory) instead of pre_mcp_tool_use (blocking):
Windsurf's pre_mcp_tool_use hook does NOT expose tool arguments to hook
scripts (verified in pre_mcp_gate.py line ~1042). Content-level validation
of a Notion write payload is impossible at the pre-MCP layer. Post-cursor-agent
scanning of the emitted response text is the only hook that can see the
actual Status value being written.

Violations are logged to ``artifacts/cursor/notion_plans_status_violations.jsonl``
(legacy path). Prefer ``tools.notion.unified_notion_status_auditor`` (same logic;
vendor-specific path under ``artifacts/<cursor|windsurf>/``).

**Hook registration:** this script is **not** wired in ``.cursor/hooks.json``.
Windsurf may still chain older equivalents; CI uses NP drift gates. For Cursor
post-turn parity use ``.cursor/hooks/after_agent_notion_status_audit.py`` → SSOT auditor.

Policy: advisory only — always exits 0, never blocks. The CI drift gate

Constitutional rule: .cursor/rules/notion-plans-taxonomy.md > CANONICAL
Status option strings (2026-05-03).

Bypass: NOTION_PLANS_STATUS_BYPASS=1 env var -- logs a bypass row and exits 0.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

fail_policy = "open"

_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"
_TIMEOUT = 15.0

# Regex to extract a Slug/title value from an invoke body.
_SLUG_RE = re.compile(
    r'["\'](?:Slug|title)["\']\s*:\s*\{[^}]*["\']content["\']\s*:\s*["\']([^"\'\']+)["\']',
    re.DOTALL,
)

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
    from _notion_plans_status_check import decide_waiting_for as _decide_waiting_for  # type: ignore
    from _notion_plans_status_check import decide_waiting_for_quality as _decide_waiting_for_quality  # type: ignore
    from _notion_plans_status_check import (  # type: ignore
        PLANS_DB_ID, PLANS_DATA_SOURCE_ID,
        BACKLOG_DB_ID, BACKLOG_DATA_SOURCE_ID,
    )
except ImportError:  # fail-open: missing helper must never wedge a turn
    _decide = None  # type: ignore[assignment]
    _decide_waiting_for = None  # type: ignore[assignment]
    _decide_waiting_for_quality = None  # type: ignore[assignment]
    PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
    PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
    BACKLOG_DB_ID = "aa8d2507-101e-4384-81d9-60ea3fe33876"
    BACKLOG_DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


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

# Match a page_id parameter inside an API-patch-page invoke body.
_PAGE_ID_RE = re.compile(
    r'<parameter\s+name="page_id">\s*([0-9a-fA-F\-]{32,36})\s*</parameter>',
    re.IGNORECASE,
)

# Match the text content of a "Waiting For" rich_text property write.
# Covers shapes like:
#   "Waiting For": {"rich_text": [{"text": {"content": "some text"}}]}
#   'Waiting For': { 'rich_text': [{ 'text': { 'content': 'some text' } }] }
# Also detects when the property is present but content is empty ("").
_WAITING_FOR_RE = re.compile(
    r'["\']Waiting\s+For["\']\s*:\s*\{[^}]*["\']rich_text["\']\s*:\s*\[.*?'
    r'["\']content["\']\s*:\s*["\']([^"\']*)["\']',
    re.DOTALL,
)


def _is_plans_id(candidate: str) -> bool:
    """Return True when candidate targets either the Plans DB or Backlog Items DB.

    Both surfaces enforce the Waiting→non-blank-Waiting-For rule (DS-3).
    """
    norm = candidate.replace("-", "").lower()
    return norm in {
        PLANS_DB_ID.replace("-", "").lower(),
        PLANS_DATA_SOURCE_ID.replace("-", "").lower(),
        BACKLOG_DB_ID.replace("-", "").lower(),
        BACKLOG_DATA_SOURCE_ID.replace("-", "").lower(),
    }


def _notion_token() -> str:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY") or ""


def _notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_notion_token()}",
        "Content-Type": "application/json",
        "Notion-Version": _NOTION_VERSION,
    }


def _find_page_id_by_slug(slug: str) -> str:
    """Query Plans DB for a page with the given slug. Returns page_id or ''."""
    tok = _notion_token()
    if not tok:
        return ""
    url = f"{_NOTION_API}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    body = json.dumps({
        "filter": {"property": "Slug", "title": {"equals": slug}},
        "page_size": 1,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results", [])
        return results[0]["id"] if results else ""
    except Exception:  # guardian: allow-broad -- auto-patch non-fatal
        return ""


def _patch_status(page_id: str, canonical_status: str) -> bool:
    """PATCH a Plans DB page to the canonical status. Returns True on success."""
    tok = _notion_token()
    if not tok or not page_id:
        return False
    url = f"{_NOTION_API}/pages/{page_id}"
    body = json.dumps({
        "properties": {"Status": {"select": {"name": canonical_status}}}
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.status < 300
    except Exception:  # guardian: allow-broad -- auto-patch non-fatal
        return False


def _append_waiting_reminder_block(page_id: str) -> bool:
    """Append a ⚠️ reminder paragraph to the Notion page body (DS-5).

    Belt-and-braces for human editors working directly in Notion: adds a
    visible callout asking them to populate 'Waiting For'.

    Returns True when the PATCH succeeded; False otherwise.  Always fail-soft.
    """
    tok = _notion_token()
    if not tok or not page_id:
        return False
    url = f"{_NOTION_API}/blocks/{page_id}/children"
    body = json.dumps({
        "children": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": (
                                    "⚠️ This plan is Waiting. Please populate the "
                                    "'Waiting For' property above with the specific "
                                    "blocker before leaving this page."
                                )
                            },
                            "annotations": {"bold": True, "color": "orange"},
                        }
                    ]
                },
            }
        ]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH", headers=_notion_headers())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.status < 300
    except Exception:  # guardian: allow-broad -- reminder append non-fatal
        return False


def _auto_patch_violation(violation: dict[str, Any], invoke_body: str) -> dict[str, Any]:
    """Attempt to self-heal a stale-status violation. Returns patch result metadata."""
    canonical = violation.get("suggested", "")
    if not canonical:
        return {"auto_patch": "skipped", "reason": "no_suggested_canonical"}

    slug_match = _SLUG_RE.search(invoke_body)
    if not slug_match:
        return {"auto_patch": "skipped", "reason": "slug_not_found_in_body"}

    slug = slug_match.group(1).strip()
    page_id = _find_page_id_by_slug(slug)
    if not page_id:
        return {"auto_patch": "skipped", "reason": f"page_not_found_for_slug:{slug}"}

    ok = _patch_status(page_id, canonical)
    if ok:
        print(
            f"[notion_plans_status_audit] AUTO-PATCHED slug={slug!r} "
            f"{violation['offending_value']!r} → {canonical!r} (page_id={page_id})",
            file=sys.stderr,
        )
        return {"auto_patch": "ok", "slug": slug, "page_id": page_id, "canonical": canonical}
    return {"auto_patch": "failed", "slug": slug, "page_id": page_id}


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
            rec: dict[str, Any] = {
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
            patch_meta = _auto_patch_violation(rec, body)
            rec["auto_patch_result"] = patch_meta
            violations.append(rec)

        # Waiting-For completeness check (NP10 + DS-3 Backlog parity).
        # If this invoke writes Status=Waiting, verify Waiting For is also
        # populated in the same body.  Absent property = blank.
        # DS-1: include an advisory remediation hint so the author knows
        # exactly what action to take.
        if _decide_waiting_for is not None:
            for status_match in _STATUS_SELECT_RE.finditer(body):
                status_value = status_match.group(1)
                if status_value != "Waiting":
                    continue
                # Identify which surface this invoke targets.
                db_id_for_check = PLANS_DB_ID
                for cid in candidate_ids:
                    norm = cid.replace("-", "").lower()
                    if norm in {
                        BACKLOG_DB_ID.replace("-", "").lower(),
                        BACKLOG_DATA_SOURCE_ID.replace("-", "").lower(),
                    }:
                        db_id_for_check = BACKLOG_DB_ID
                        break
                # Extract Waiting For text from the same invoke body (may be absent).
                wf_match = _WAITING_FOR_RE.search(body)
                wf_text = wf_match.group(1).strip() if wf_match else ""
                wf_verdict = _decide_waiting_for(db_id_for_check, status_value, wf_text or None)
                if wf_verdict is not None:
                    violation_rec: dict[str, Any] = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": "error",
                        "violation_type": "WAITING_EMPTY_WAITING_FOR",
                        "tool": tool_name,
                        "invoke_index": invoke_idx,
                        "offending_value": "Waiting",
                        "waiting_for_found": wf_text,
                        "message": wf_verdict.message,
                        "rule": "notion-plans-taxonomy.md > Field Requirements (NP10)",
                        "plan": "notion-plans-status-enforcement-7a1e2d",
                        # DS-1: advisory remediation hint
                        "remediation_hint": (
                            "Re-issue the write with a populated 'Waiting For' "
                            "property describing the specific blocker (person, "
                            "system, decision, or time-bound trigger). "
                            "Example: \"Waiting For\": {\"rich_text\": "
                            "[{\"text\": {\"content\": \"<blocker description>\"}}]}"
                        ),
                    }
                    # DS-5: for patch-page writes we know the page_id; append
                    # a reminder block so the Notion page itself signals the
                    # missing field to human editors.
                    if tool_name == "API-patch-page":
                        page_id_match = _PAGE_ID_RE.search(body)
                        if page_id_match:
                            reminder_ok = _append_waiting_reminder_block(page_id_match.group(1))
                            violation_rec["reminder_block_appended"] = reminder_ok
                    violations.append(violation_rec)
                    continue  # blank already reported; skip quality check
                # DS-2: also check for weak placeholder strings.
                if _decide_waiting_for_quality is not None:
                    quality_verdict = _decide_waiting_for_quality(
                        db_id_for_check, status_value, wf_text or None
                    )
                    if quality_verdict is not None:
                        violations.append({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "severity": "warn",
                            "violation_type": "WAITING_WEAK_WAITING_FOR",
                            "tool": tool_name,
                            "invoke_index": invoke_idx,
                            "offending_value": wf_text,
                            "message": quality_verdict.message,
                            "rule": "notion-plans-taxonomy.md > Field Requirements (NP10/DS-2)",
                            "plan": "notion-np10-deferred-scope-c8f1a4",
                            "remediation_hint": (
                                f"Replace placeholder 'Waiting For' value {wf_text!r} "
                                "with a concrete description of the specific blocker."
                            ),
                        })

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
            f"artifacts/cursor/notion_plans_status_violations.jsonl",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
