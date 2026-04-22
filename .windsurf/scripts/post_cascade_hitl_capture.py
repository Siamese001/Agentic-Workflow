"""Back-compat shim — DEPRECATED.

This module was renamed 2026-04-21 (harness-enforcement-rename W1) from
`post_cascade_hitl_capture` to `post_cascade_author_gate_capture` per
ADR-023 terminology: "HITL" is reserved for runtime exit-control
(v30 step [5] ESCALATE); developer-loop work uses "Author-Gate".

This shim re-exports the new module so any pre-W1 references (hooks.json
entries, external scripts, imports in historical tests) continue to work.

Removal date: 2026-07-21 (90-day deprecation per harness-enforcement-rename
plan §"Rollback / Shims"). Do NOT add new callers to this path.
"""

# pylint: disable=wildcard-import,unused-wildcard-import
from __future__ import annotations

import sys
import warnings

warnings.warn(
    "post_cascade_hitl_capture is deprecated — import from "
    "post_cascade_author_gate_capture instead. "
    "Removal target: 2026-07-21 (90-day deprecation window).",
    DeprecationWarning,
    stacklevel=2,
)

from post_cascade_author_gate_capture import *  # noqa: E402, F401, F403
from post_cascade_author_gate_capture import main  # noqa: E402, F401


if __name__ == "__main__":
    sys.exit(main())
