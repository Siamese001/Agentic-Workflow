#!/usr/bin/env python3
"""_serialization_sentinel.py — cross-process detector for MCP serialization.

Layer 1 of the MCP serialization defense-in-depth (constitutional §25,
``mcp-serialization.md``). Designed to run inside Windsurf pre-* gate hooks,
which fire as separate Python processes per dispatched tool call. Because
multiple tools dispatched in the same ``<function_calls>`` block run roughly
simultaneously (typically within ~100ms), we correlate them via timestamped
filesystem entries inside a short window.

Mechanism (race-free by construction):
  1. Each pre-* gate calls ``record_and_check(kind, identifier)`` on entry.
  2. The function APPENDS a JSONL row ``{ts, pid, kind, id}`` to a per-session
     log file, then READS BACK every row within the last ``WINDOW_SECONDS``.
  3. If any sibling row from a different PID exists AND the combination is
     forbidden (any pair where one side is "mcp"), it returns ``True`` (block).

Both racing processes append before either reads, so both see each other's
row. Both block. Cascade gets the error and self-corrects on the next turn.

Bypass: ``MCP_SERIAL_BYPASS=1`` (matches ``post_cascade_mcp_serialization_audit.py``).

Sunset: honors ``.windsurf/config/mcp_serialization_ttl.json`` ``retired_after``
date — same TTL contract as the post-cascade audit hook.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

# Time window for correlating sibling dispatches. Must be:
#   - long enough to catch genuinely simultaneous dispatches in one block
#     (Cascade pipeline = tens to low-hundreds of ms),
#   - short enough not to cross response boundaries (Cascade typically takes
#     >2s between responses to compose).
# 1.0s is the empirical sweet spot.
WINDOW_SECONDS: float = float(os.environ.get("MCP_SERIAL_WINDOW_S", "1.0"))

# Entries older than this are pruned on read (keeps log file bounded).
PRUNE_SECONDS: float = 60.0

# Max bytes for the dispatch log before we truncate to its last 500 lines.
# Defensive only — append-only with prune should never reach this in normal use.
MAX_LOG_BYTES: int = 256 * 1024

# Tool kinds. Any pair where at least one side is "mcp" is a violation.
KIND_MCP = "mcp"
KIND_RUN = "run"
KIND_READ = "read"
KIND_WRITE = "write"
_KNOWN_KINDS = frozenset({KIND_MCP, KIND_RUN, KIND_READ, KIND_WRITE})

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_repo_root = Path(__file__).resolve().parents[2]
_artifacts = _repo_root / "artifacts" / "windsurf"
_ttl_config = _repo_root / ".windsurf" / "config" / "mcp_serialization_ttl.json"


def _session_id() -> str:
    """Per-IDE-window isolation. Matches pre_mcp_gate.py session-state convention."""
    return os.environ.get("VSCODE_PID") or str(os.getppid())


def _log_path() -> Path:
    return _artifacts / f"dispatch_log_{_session_id()}.jsonl"


# ---------------------------------------------------------------------------
# Sunset / bypass
# ---------------------------------------------------------------------------


def _is_retired() -> bool:
    if not _ttl_config.exists():
        return False
    try:
        payload = json.loads(_ttl_config.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    retired_after = payload.get("retired_after")
    if not isinstance(retired_after, str):
        return False
    try:
        cutoff = datetime.fromisoformat(retired_after.replace("Z", "+00:00"))
    except ValueError:
        return False
    if cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= cutoff


def _is_bypass() -> bool:
    return os.environ.get("MCP_SERIAL_BYPASS", "").strip() == "1"


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def _read_log_entries(log_path: Path, now: float) -> list[dict]:
    """Read all log entries; silently skip malformed lines. Fail-open on I/O error."""
    if not log_path.exists():
        return []
    try:
        raw = log_path.read_text(encoding="utf-8")
    except OSError:
        return []
    entries: list[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        ts = row.get("ts")
        if not isinstance(ts, (int, float)):
            continue
        # Drop entries older than PRUNE_SECONDS at read time.
        if (now - float(ts)) > PRUNE_SECONDS:
            continue
        entries.append(row)
    return entries


def _append_entry(log_path: Path, entry: dict) -> None:
    """Append one JSONL row. Best-effort; fail-open on I/O error."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        # Defensive truncation: if the file has grown unexpectedly, rotate it.
        if log_path.exists() and log_path.stat().st_size > MAX_LOG_BYTES:
            try:
                tail = log_path.read_text(encoding="utf-8").splitlines()[-500:]
                log_path.write_text("\n".join(tail) + "\n", encoding="utf-8")
            except OSError:
                pass
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _is_violation_pair(my_kind: str, other_kind: str) -> bool:
    """A pair is a violation iff at least one side is an MCP call."""
    return KIND_MCP in (my_kind, other_kind)


def record_and_check(kind: str, identifier: str) -> tuple[bool, str | None]:
    """Record this dispatch and check for a sibling violation in the window.

    Returns ``(should_block, reason)``. ``reason`` is None when allowed.
    Fail-open on every internal error: a broken sentinel never wedges a turn.
    """
    if kind not in _KNOWN_KINDS:
        return False, None
    if _is_retired() or _is_bypass():
        return False, None

    now = time.time()
    self_pid = os.getpid()
    log_path = _log_path()

    entry = {
        "ts": now,
        "pid": self_pid,
        "kind": kind,
        "id": (identifier or "")[:200],  # bound id length defensively
    }

    # Append BEFORE reading. Any racing sibling that started before us has
    # already appended, and any that starts after us will see our row.
    _append_entry(log_path, entry)

    siblings = _read_log_entries(log_path, now)
    window_start = now - WINDOW_SECONDS
    for row in siblings:
        if row.get("pid") == self_pid:
            continue
        ts = float(row.get("ts", 0))
        if ts < window_start:
            continue
        other_kind = row.get("kind", "")
        if other_kind not in _KNOWN_KINDS:
            continue
        if _is_violation_pair(kind, other_kind):
            reason = (
                f"MCP serialization violation: this {kind!r} dispatch "
                f"({identifier!r}) ran concurrently with a {other_kind!r} dispatch "
                f"({row.get('id', '')!r}, pid={row.get('pid')}, "
                f"delta={now - ts:.3f}s) in the same response. "
                "MCP calls MUST be issued one per response with no sibling tool "
                "calls of any kind (constitutional §25, "
                "anthropics/claude-agent-sdk-typescript#41). "
                "Re-issue this MCP call alone in its own response. "
                "Bypass: set MCP_SERIAL_BYPASS=1."
            )
            return True, reason

    return False, None


# ---------------------------------------------------------------------------
# Convenience helper for gate scripts
# ---------------------------------------------------------------------------


def block_if_violation(kind: str, identifier: str, *, gate_name: str = "pre_gate") -> int:
    """Convenience wrapper used by pre-* gates. Returns 0 (allow) or 2 (block)."""
    should_block, reason = record_and_check(kind, identifier)
    if should_block and reason is not None:
        print(f"[{gate_name}] BLOCKED: {reason}", file=sys.stderr)
        return 2
    return 0
