#!/usr/bin/env python3
"""Shim — SSOT: ``.codex/governance/scripts/pre_mcp_gate.py``.

Windsurf ``pre_mcp_tool_use`` may still invoke this path. Library tests that
``sys.path.insert(0, ".../.windsurf/scripts")`` and ``import pre_mcp_gate`` load
this file, which re-exports the Cursor implementation (plan
``cursor-only-governance-ssot-d9e4b1`` W3).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SSOT = (
    # parent       = _legacy_windsurf/
    # parent.parent = .codex/governance/scripts/  ← real SSOT lives here
    # (old: parents[2] = .codex/governance/ → double-path bug)
    Path(__file__).resolve().parent.parent
    / "pre_mcp_gate.py"
)

_spec = importlib.util.spec_from_file_location("pre_mcp_gate", _SSOT)
if _spec is None or _spec.loader is None:
    print(f"[pre_mcp_gate] FATAL: SSOT missing at {_SSOT}", file=sys.stderr)
    sys.exit(2)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

if __name__ != "__main__":
    sys.modules[__name__] = _mod

if __name__ == "__main__":
    raise SystemExit(_mod.main())
