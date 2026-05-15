"""post_cascade_read_budget_audit.py - advisory read-budget cap.

Counts native and MCP file-read tool invocations in each Cursor Agent response and
logs a violation row when the combined total exceeds the soft cap. Mirrors
`post_cascade_grep_budget_audit.py` exactly in shape.

This exists because:

  1. `read_file`, `mcp4_read_text_file`, `mcp4_read_multiple_files`,
     `read_notebook` are native or MCP read tools with NO pre-hook surface,
     so only retroactive detection is possible.
  2. Unbounded reads are the second-largest token-burn vector (after grep).
     Per Anthropic's "Effective Context Engineering" guidance, just-in-time
     loading should be bounded; per the agora-code benchmark, a 1000-line
     file read can cost ~8000 tokens.
  3. Advisory-only: this hook NEVER blocks; it logs. Deterministic-but-soft,
     mirroring `post_cascade_grep_budget_audit.py`.

Soft cap: 10 combined invocations per response.

Bypass: set environment variable `READ_BUDGET_BYPASS=1`. Bypass rows are still
logged with `bypass=true` for audit.

Fail-open: any internal error -> exit 0 and diagnostic to stderr.

Violations log: `artifacts/windsurf/read_budget_violations.jsonl`
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "read_budget_violations.jsonl"
SOFT_CAP = 10

# Match the tool-invocation markers Cursor Agent emits in its response envelope.
# Native read tools first, then MCP filesystem reads (any prefix mcpN_ is fine).
_READ_FILE_PAT = re.compile(r'<invoke\s+name="read_file"', re.IGNORECASE)
_READ_NOTEBOOK_PAT = re.compile(r'<invoke\s+name="read_notebook"', re.IGNORECASE)
_READ_URL_PAT = re.compile(r'<invoke\s+name="read_url_content"', re.IGNORECASE)
# MCP filesystem tools - prefix mcpN_ varies by server-order; match the suffix.
_MCP_READ_TEXT_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_text_file"', re.IGNORECASE)
_MCP_READ_FILE_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_file"', re.IGNORECASE)
_MCP_READ_MULTI_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_multiple_files"', re.IGNORECASE)


def _read_response_text() -> str:
    """Read the Cursor Agent response envelope from stdin.

    Same shape as post_cascade_grep_budget_audit.py.
    """
    try:
        raw = sys.stdin.read() or ""
    except (OSError, ValueError):
        return ""
    if not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            for key in ("response_text", "response", "text", "content"):
                val = payload.get(key)
                if isinstance(val, str):
                    return val
            return json.dumps(payload)
        return raw
    except (ValueError, TypeError):
        return raw


def _count_invocations(text: str) -> dict[str, int]:
    return {
        "read_file": len(_READ_FILE_PAT.findall(text)),
        "read_notebook": len(_READ_NOTEBOOK_PAT.findall(text)),
        "read_url_content": len(_READ_URL_PAT.findall(text)),
        "mcp_read_text_file": len(_MCP_READ_TEXT_PAT.findall(text)),
        "mcp_read_file": len(_MCP_READ_FILE_PAT.findall(text)),
        "mcp_read_multiple_files": len(_MCP_READ_MULTI_PAT.findall(text)),
    }


def _append_violation(row: dict[str, Any]) -> None:
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    try:
        text = _read_response_text()
        if not text:
            return 0
        counts = _count_invocations(text)
        total = sum(counts.values())
        bypass = os.environ.get("READ_BUDGET_BYPASS", "").strip() == "1"

        if total <= SOFT_CAP and not bypass:
            return 0

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counts": counts,
            "total": total,
            "cap": SOFT_CAP,
            "bypass": bypass,
            "over_cap": total > SOFT_CAP,
        }
        _append_violation(row)
        if total > SOFT_CAP and not bypass:
            sys.stderr.write(
                f"[read-budget-audit] WARNING: {total} read invocations "
                f"(cap={SOFT_CAP}) - consider narrowing scope or using ADG MCP "
                f"for structured queries instead of bulk reads.\n"
            )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"[read-budget-audit] fail-open: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
