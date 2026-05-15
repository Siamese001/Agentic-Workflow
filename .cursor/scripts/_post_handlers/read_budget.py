"""Read-budget handler - advisory cap on file-read tool invocations per response.

In-process equivalent of `.cursor/scripts/post_cursor_agent_read_budget_audit.py`.
Logs a row to `artifacts/cursor/read_budget_violations.jsonl` when combined
read-tool invocations exceed the soft cap (10) or when bypass is set.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import ParsedResponse

SOFT_CAP = 10

_READ_FILE_PAT = re.compile(r'<invoke\s+name="read_file"', re.IGNORECASE)
_READ_NOTEBOOK_PAT = re.compile(r'<invoke\s+name="read_notebook"', re.IGNORECASE)
_READ_URL_PAT = re.compile(r'<invoke\s+name="read_url_content"', re.IGNORECASE)
_MCP_READ_TEXT_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_text_file"', re.IGNORECASE)
_MCP_READ_FILE_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_file"', re.IGNORECASE)
_MCP_READ_MULTI_PAT = re.compile(r'<invoke\s+name="mcp\d+_read_multiple_files"', re.IGNORECASE)


def _append(path: Path, row: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as err:
        print(f"[read-budget] write failed: {err}", file=sys.stderr)


def _count_invocations(text: str) -> dict[str, int]:
    return {
        "read_file": len(_READ_FILE_PAT.findall(text)),
        "read_notebook": len(_READ_NOTEBOOK_PAT.findall(text)),
        "read_url_content": len(_READ_URL_PAT.findall(text)),
        "mcp_read_text_file": len(_MCP_READ_TEXT_PAT.findall(text)),
        "mcp_read_file": len(_MCP_READ_FILE_PAT.findall(text)),
        "mcp_read_multiple_files": len(_MCP_READ_MULTI_PAT.findall(text)),
    }


def run(parsed: ParsedResponse, repo_root: Path) -> None:
    text = parsed.response_text or parsed.raw
    if not text:
        return

    counts = _count_invocations(text)
    total = sum(counts.values())
    bypass = os.environ.get("READ_BUDGET_BYPASS", "").strip() == "1"

    if total <= SOFT_CAP and not bypass:
        return

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "total": total,
        "cap": SOFT_CAP,
        "bypass": bypass,
        "over_cap": total > SOFT_CAP,
        "via": "dispatcher",
    }
    log_path = repo_root / "artifacts" / "cursor" / "read_budget_violations.jsonl"
    _append(log_path, row)

    if total > SOFT_CAP and not bypass:
        print(
            f"[read-budget] WARNING: {total} read invocations "
            f"(cap={SOFT_CAP}) - consider narrowing scope or using ADG MCP "
            f"for structured queries instead of bulk reads.",
            file=sys.stderr,
        )
