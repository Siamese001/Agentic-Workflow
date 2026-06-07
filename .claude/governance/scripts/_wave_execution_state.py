"""
_wave_execution_state.py — Shared state helper for multi-wave plan execution.

Purpose
-------
Cursor Agent marks a multi-wave plan as "in-progress" at the start of Wave 1 and
clears the mark after the final wave completes. While the mark is set,
pre_mcp_gate.py blocks Notion MCP calls so all Notion plan/backlog writes
are batched at the end of the plan instead of stalling between waves.

Rationale: remote MCPs (notion, tavily, deepwiki, context7, GitKraken) are
serialized per constitutional §25. A mid-wave Notion write stalls the turn,
forcing the user to issue "next wave" prompts manually. Batching eliminates
the stalls.

Session-scoped via VSCODE_PID (falls back to PPID) — matches pre_mcp_gate
session-state convention so parallel IDE windows do not collide.

State file shape
----------------
JSON at artifacts/cursor/wave_execution_<session>.json:
    {
      "plan": "<slug-6hex>",
      "started_at": "<iso-utc>",
      "started_at_epoch": <float>
    }

Absent file or empty dict => not active => Notion calls allowed.

Public API
----------
    is_active()                 -> dict | None     # state dict if active
    set_active(plan_slug)       -> Path            # writes state, returns path
    clear()                     -> bool            # removes state file
    state_path()                -> Path            # canonical path for this session
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ARTIFACT_DIR = _REPO_ROOT / "artifacts" / "cursor"


def _session_id() -> str:
    return os.environ.get("VSCODE_PID") or str(os.getppid())


def state_path() -> Path:
    return _ARTIFACT_DIR / f"wave_execution_{_session_id()}.json"


def is_active() -> dict | None:
    """Return the state dict if a multi-wave plan is in-progress, else None.

    Fail-open: any I/O or JSON error returns None (treated as inactive).
    """
    path = state_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("plan"):
            return data
    except (OSError, json.JSONDecodeError):
        return None
    return None


def set_active(plan_slug: str) -> Path:
    """Mark a plan as in-progress. Overwrites any prior state.

    Returns the state file path (useful for logging / tests).
    """
    if not plan_slug or not isinstance(plan_slug, str):
        raise ValueError("plan_slug must be a non-empty string")
    _ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    payload = {
        "plan": plan_slug,
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at_epoch": now,
    }
    path = state_path()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def clear() -> bool:
    """Remove the state file. Returns True if a file was removed, False otherwise."""
    path = state_path()
    if path.exists():
        try:
            path.unlink()
            return True
        except OSError:
            return False
    return False
