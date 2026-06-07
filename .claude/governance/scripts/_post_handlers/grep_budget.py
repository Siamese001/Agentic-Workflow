"""Grep-budget handler — advisory cap on grep_search + code_search per response.

In-process equivalent of `.claude/governance/scripts/post_agent_grep_budget_audit.py`.
Logs a row to `artifacts/governance/grep_budget_violations.jsonl` when combined
text-search invocations exceed the soft cap (3) or when bypass is set.
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

SOFT_CAP = 3

_GREP_PAT = re.compile(r'<invoke\s+name="grep_search"', re.IGNORECASE)
_CODE_SEARCH_PAT = re.compile(r'<invoke\s+name="code_search"', re.IGNORECASE)


def _append(path: Path, row: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as err:
        print(f"[grep-budget] write failed: {err}", file=sys.stderr)


def run(parsed: ParsedResponse, repo_root: Path) -> None:
    text = parsed.response_text or parsed.raw
    if not text:
        return

    grep_n = len(_GREP_PAT.findall(text))
    code_n = len(_CODE_SEARCH_PAT.findall(text))
    total = grep_n + code_n
    bypass = os.environ.get("GREP_BUDGET_BYPASS", "").strip() == "1"

    if total <= SOFT_CAP and not bypass:
        return

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "grep_search_count": grep_n,
        "code_search_count": code_n,
        "total": total,
        "cap": SOFT_CAP,
        "bypass": bypass,
        "over_cap": total > SOFT_CAP,
        "via": "dispatcher",
    }
    log_path = repo_root / "artifacts" / "governance" / "grep_budget_violations.jsonl"
    _append(log_path, row)

    if total > SOFT_CAP and not bypass:
        print(
            f"[grep-budget] WARNING: {total} text-search invocations "
            f"(cap={SOFT_CAP}) — consider ADG MCP or narrower scope.",
            file=sys.stderr,
        )
