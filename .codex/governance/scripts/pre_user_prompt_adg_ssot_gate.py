#!/usr/bin/env python3
"""pre_user_prompt_adg_ssot_gate.py — ADG SQLite-SSOT green-light for T2/T3 prompts.

Lean Claude Code ``UserPromptSubmit`` gate enforcing constitutional §13 with the
corrected SSOT semantics from plan ``adg-redis-hotcache-enforcement-b9f4c2``:

  - **ADG SQLite snapshot is the SSOT.** If no readable canonical
    ``artifacts/adg/adg_indexed_*.sqlite`` snapshot exists, a T2/T3 prompt is
    **BLOCKED** (exit 2): the agent cannot do reliable graph work without the
    source of truth.
  - **ADG Redis is a non-authoritative hot cache.** A cold/absent Redis hot cache
    is advisory only and **never blocks** — SQLite serves every query directly
    (constitutional §28 SQLite-direct fallback).

This reuses ``classify_tier`` / ``check_adg_health_red`` / ``check_redis_*`` from
``pre_prompt_classifier.py`` so the probe logic has a single source of truth. It
deliberately does NOT inject the structured-reasoning mandate or MCP routing
traces — that is the classifier's concern, out of scope for this green-light gate.

Payload: reads the ``UserPromptSubmit`` JSON from stdin. Accepts both the Claude
Code shape (``{"prompt": "..."}``) and the legacy ``{"tool_info": {...}}`` shape.

Exit codes: 0 for T0/T1 and healthy T2/T3; 2 to block a T2/T3 prompt when the
SQLite SSOT is unavailable. Fail-open on any unexpected error.

Bypass: ``ADG_SSOT_GATE_BYPASS=1``.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_GOV_DIR = Path(__file__).resolve().parent
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))


def _read_prompt(raw: str) -> str:
    """Extract the prompt text from either payload shape; '' if absent/invalid."""
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return ""
    if not isinstance(payload, dict):
        return ""
    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return ""
    return tool_info.get("user_prompt") or tool_info.get("prompt") or ""


def main() -> int:
    if os.getenv("ADG_SSOT_GATE_BYPASS") == "1":
        return 0
    try:
        if sys.stdin.isatty():
            return 0  # standalone-invocation guard: never hang waiting on a TTY
    except (ValueError, OSError):
        pass
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    prompt = _read_prompt(raw)
    if not prompt:
        return 0

    try:
        import pre_prompt_classifier as ppc
    except ImportError:
        return 0  # fail-open: probe logic unavailable, do not block

    tier = ppc.classify_tier(prompt)
    if tier not in ("T2", "T3"):
        return 0  # T0/T1 never gated

    try:
        sqlite_red = ppc.check_adg_health_red(ppc.repo_root)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- gate fail-soft contract (never block on probe error)
        return 0

    if sqlite_red:
        print(
            f"[adg_ssot_gate] BLOCKED: {tier} prompt — ADG SQLite SSOT is unavailable "
            "(no readable artifacts/adg/adg_indexed_*.sqlite snapshot). Regenerate with "
            "`python tools/generate/generate_full_adg.py`, then retry (constitutional §13).",
            file=sys.stderr,
        )
        return 2

    # SQLite SSOT green — surface advisory Redis hot-cache status (never blocks).
    try:
        if ppc.check_redis_up() and ppc.check_redis_adg_hot():
            print(
                f"[adg_ssot_gate] {tier}: ADG SQLite SSOT green; Redis hot cache warm.",
                file=sys.stderr,
            )
        else:
            print(
                f"[adg_ssot_gate] {tier}: ADG SQLite SSOT green; Redis hot cache cold/absent "
                "(advisory — not blocking). Warm it: python tools/adg/adg_redis_ingest.py --force",
                file=sys.stderr,
            )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- advisory Redis status only, never fatal
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
