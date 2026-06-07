"""post_cascade_grep_budget_audit.py — advisory grep/code_search budget cap.

Counts native text-search tool invocations (`grep_search`, `code_search`) in
each Cursor Agent response and logs a violation row when the combined total exceeds
the soft cap. This exists because:

  1. `grep_search` / `code_search` are native Cursor Agent tools with NO pre-hook,
     so only retroactive detection is possible (see global_rules.md ADG-First).
  2. Unbounded text search is a proxy for "reviewing entire codebase every
     run" — the containment failure mode the grep budget targets.
  3. Advisory-only: this hook NEVER blocks; it logs. Deterministic-but-soft,
     mirroring `post_cascade_adg_audit.py`.

Soft cap: 3 combined invocations per response.

Bypass: set environment variable `GREP_BUDGET_BYPASS=1`. Bypass rows are still
logged with `bypass=true` for audit.

Fail-open: any internal error → exit 0 and diagnostic to stderr.

Violations log: `artifacts/windsurf/grep_budget_violations.jsonl`
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
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "grep_budget_violations.jsonl"
SOFT_CAP = 3

# Match the tool-invocation markers Cursor Agent emits in its response envelope.
# We look for the tool name appearing as a function-call name token — same
# detection shape as post_cascade_adg_audit.py.
_GREP_PAT = re.compile(r'<invoke\s+name="grep_search"', re.IGNORECASE)
_CODE_SEARCH_PAT = re.compile(r'<invoke\s+name="code_search"', re.IGNORECASE)


def _read_response_text() -> str:
    """Read the Cursor Agent response envelope from stdin.

    Windsurf delivers the post-hook payload on stdin as JSON. We try to parse
    it; if that fails, we treat stdin as raw text (covers manual smoke tests).
    """
    try:
        raw = sys.stdin.read() or ""
    except (OSError, ValueError):
        return ""
    if not raw.strip():
        return ""
    # Try JSON envelope; fall back to raw.
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            # Common envelope keys used by sibling hooks.
            for key in ("response_text", "response", "text", "content"):
                val = payload.get(key)
                if isinstance(val, str):
                    return val
            return json.dumps(payload)
        return raw
    except (ValueError, TypeError):
        return raw


def _count_invocations(text: str) -> tuple[int, int]:
    return (len(_GREP_PAT.findall(text)), len(_CODE_SEARCH_PAT.findall(text)))


def _append_violation(row: dict[str, Any]) -> None:
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    try:
        text = _read_response_text()
        if not text:
            return 0
        grep_n, code_n = _count_invocations(text)
        total = grep_n + code_n
        bypass = os.environ.get("GREP_BUDGET_BYPASS", "").strip() == "1"

        if total <= SOFT_CAP and not bypass:
            return 0

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "grep_search_count": grep_n,
            "code_search_count": code_n,
            "total": total,
            "cap": SOFT_CAP,
            "bypass": bypass,
            "over_cap": total > SOFT_CAP,
        }
        _append_violation(row)
        if total > SOFT_CAP and not bypass:
            sys.stderr.write(
                f"[grep-budget-audit] WARNING: {total} text-search invocations "
                f"(cap={SOFT_CAP}) — consider ADG MCP or narrower scope.\n"
            )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"[grep-budget-audit] fail-open: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
