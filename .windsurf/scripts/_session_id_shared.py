"""Single source of truth for Windsurf hook session-id derivation.

All three hook scripts (pre_mcp_gate, post_mcp_audit, pre_prompt_classifier)
must derive the session_id identically. Any divergence causes the hooks to
read/write different ``session_state_*.json`` files, which manifests as the
memory-first gate re-firing even after ``mem_recall_session_start`` has been
called this session.

Derivation priority (most stable first):
  1. ``WINDSURF_SESSION_ID`` — explicit, preferred if Windsurf ever exposes it
  2. ``CASCADE_SESSION_ID`` — explicit alias
  3. ``VSCODE_PID`` — set by the IDE for hook subprocesses
  4. Stable repo-root hash — deterministic fallback so ALL hooks agree even
     when the subprocess doesn't inherit ``VSCODE_PID`` (observed on Windows).

The repo-root fallback replaces the older ``"default"`` fallback used by
``pre_mcp_gate`` and the ``os.getppid()`` fallback used by the other two hooks.
Both were non-deterministic across subprocesses and caused session-state
divergence.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


def derive_session_id(repo_root: Path) -> str:
    """Return a stable, deterministic session identifier.

    Same inputs → same output across every hook subprocess spawned from the
    same IDE window, regardless of ``VSCODE_PID`` inheritance quirks.
    """
    explicit = os.environ.get("WINDSURF_SESSION_ID") or os.environ.get("CASCADE_SESSION_ID")
    if explicit:
        return str(explicit)
    vscode_pid = os.environ.get("VSCODE_PID")
    if vscode_pid:
        return str(vscode_pid)
    # Deterministic fallback: hash the repo_root so every hook process running
    # against the same repo computes the same session file path.
    digest = hashlib.sha1(str(repo_root).encode("utf-8")).hexdigest()[:12]
    return f"repo-{digest}"


__all__ = ["derive_session_id"]
