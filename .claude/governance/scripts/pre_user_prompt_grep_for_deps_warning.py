#!/usr/bin/env python3
"""
pre_user_prompt_grep_for_deps_warning.py — Pre-prompt grep-for-deps detector (P4).

Cursor ``pre_user_prompt`` hook. Scans the user's prompt text for
dependency-analysis intent ("grep for imports of X", "who uses Y",
"find references to Z", "what depends on W") and prints a warning to
stderr so Cursor Agent sees the injected signal in the next turn.

Does NOT block the prompt — advisory only. The companion post-response
hook ``post_cursor_agent_adg_audit.py`` remains the enforcement point.

Rationale: Wave 14 changelog — "Users can now configure Cursor Agent Hooks
on user prompts for logging all user prompts and blocking policy-violating
prompts." We use the logging facet, not the blocking facet, because the
user phrasing is not itself a violation — only the downstream tool choice
is.

Fail policy: OPEN — any error → exit 0 silently.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_LOG_PATH = _ROOT / "artifacts" / "governance" / "pre_prompt_grep_warnings.jsonl"
_BYPASS_ENV = "PRE_PROMPT_GREP_WARNING_BYPASS"

# Patterns that indicate the user wants dependency analysis.
_DEP_INTENT_PATTERNS = [
    re.compile(r"\bgrep\b.*\b(import|imports|uses|usage|reference|references)\b", re.IGNORECASE),
    re.compile(r"\b(who|what)\s+(uses|depends on|imports|references|calls)\b", re.IGNORECASE),
    re.compile(r"\bfind\s+(imports?|references?|consumers?|callers?|usages?)\b", re.IGNORECASE),
    re.compile(r"\b(fan[- ]?in|fan[- ]?out|blast\s+radius)\b", re.IGNORECASE),
    re.compile(r"\b(depends\s+on|dependency|dependencies)\s+(of|for)\b", re.IGNORECASE),
]


def _extract_prompt_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("prompt", "user_prompt", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
            if isinstance(val, dict):
                for inner in ("text", "content", "prompt"):
                    iv = val.get(inner)
                    if isinstance(iv, str) and iv.strip():
                        return iv
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def _detect_intent(prompt: str) -> list[str]:
    matched: list[str] = []
    for pat in _DEP_INTENT_PATTERNS:
        m = pat.search(prompt)
        if m:
            matched.append(m.group(0))
    return matched


_BREADCRUMB_PATH = _ROOT / "artifacts" / "governance" / "_grep_deps_intent_turn.flag"


def _drop_intent_breadcrumb(matches: list[str]) -> None:
    """Stamp a per-turn flag so pre_grep_gate.py can hard-block a structural grep
    issued in the same turn the user asked a dependency question. Best-effort; the
    grep gate is fail-open and treats a stale/missing flag as "no breadcrumb"."""
    try:
        _BREADCRUMB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _BREADCRUMB_PATH.write_text(
            json.dumps({"stamped_at": datetime.now(timezone.utc).isoformat(),
                        "matched_patterns": matches}),
            encoding="utf-8",
        )
    except OSError:
        pass


def _log_warning(prompt: str, matches: list[str]) -> None:
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "prompt_snippet": prompt[:300],
                        "matched_patterns": matches,
                    }
                )
                + "\n"
            )
    except OSError:
        pass


def main() -> int:
    if sys.stdin.isatty():
        return 0
    if os.environ.get(_BYPASS_ENV):
        return 0

    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    prompt_text = _extract_prompt_text(payload)
    if not prompt_text.strip():
        return 0

    matches = _detect_intent(prompt_text)
    if not matches:
        return 0

    _log_warning(prompt_text, matches)
    _drop_intent_breadcrumb(matches)

    # Inject ADG-first reminder via stderr (Cursor surfaces pre_user_prompt
    # hook stderr into the next model turn's context).
    print(
        "[pre_prompt_grep_for_deps_warning] ADG-FIRST INTENT DETECTED.\n"
        f"  Matched patterns: {matches}\n"
        "  REQUIRED TOOL: adg_sqlite MCP (adg_nodes_by_file, adg_edge_fanin, "
        "adg_edge_fanout) or direct sqlite3 query of "
        "artifacts/adg/adg_indexed_*.sqlite.\n"
        "  FORBIDDEN: grep_search for dependency analysis (constitutional §ADG-First, §28).\n"
        "  Fallback ladder: (1) adg_sqlite MCP → (2) direct SQLite → (3) grep ONLY after "
        "both fail with DEGRADED_FALLBACK: reason=... emitted.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
