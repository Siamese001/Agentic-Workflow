"""ADG generator package hooks.

This lightweight hook emits the BCG-style executive synthesis after
``tools/generate/generate_full_adg.py`` completes. It is gated on the executable
name and can be disabled with ``ADG_BCG_EXECUTIVE_BYPASS=1``.
"""
from __future__ import annotations

import atexit
import os
import sys


def _should_emit_bcg_summary() -> bool:
    if os.environ.get("ADG_BCG_EXECUTIVE_BYPASS", "").strip().lower() in {"1", "true", "yes"}:
        return False
    argv0 = (sys.argv[0] if sys.argv else "").replace("\\", "/")
    return argv0.endswith("tools/generate/generate_full_adg.py") or argv0.endswith("generate_full_adg.py")


def _emit_bcg_summary_at_exit() -> None:
    if not _should_emit_bcg_summary():
        return
    try:
        from tools.reports.adg_bcg_executive_synthesis import emit_bcg_executive_summary_from_latest

        emit_bcg_executive_summary_from_latest(print_inline=True, fail_closed=False)
    except Exception as exc:  # pragma: no cover - best-effort post-run UX hook
        print(
            f"[adg_bcg_executive_summary] WARNING: post-run executive synthesis failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )


atexit.register(_emit_bcg_summary_at_exit)
