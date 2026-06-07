#!/usr/bin/env python3
"""post_cursor_agent_mcp_preflight_audit.py — MCP destructive-call health preflight audit.

Companion to the preflight check inside ``pre_mcp_gate.py``. Runs on every
``post_cursor_agent_response`` payload. Two responsibilities:

1. **Heartbeat writer** — when the response contains a successful
   ``adg_health`` / ``redis_health`` / ``memory_health`` invocation, stamp the
   per-server heartbeat file so the next turn's preflight check sees a fresh
   health signal.

2. **Audit logger** — when the response contains a destructive MCP call
   (``adg_close_connections``, ``adg_reopen_connections``, ``adg_reload``,
   ``redis_flush_namespace``, ``redis_del_key``, ``mem_cleanup_stale``, ...)
   without a preceding successful health call within 60 s, log a row to
   ``artifacts/cursor/mcp_preflight_violations.jsonl``.

Policy: **advisory only** — always exits 0, never blocks. Fail-open on any
internal error so a broken hook never wedges a turn.

Constitutional rule: §13 (MCP Green Light). Plan:
``.claude/plans/mcp-destructive-gate-preflight-e9a14b.md`` W1 Phase P2.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[2]
heartbeat_path = repo_root / "artifacts" / "windsurf" / "mcp_health_heartbeat.json"
violations_log = repo_root / "artifacts" / "windsurf" / "mcp_preflight_violations.jsonl"
ttl_config = repo_root / ".cursor" / "config" / "mcp_preflight_ttl.json"

# ---------------------------------------------------------------------------
# Tool classification (shared contract with pre_mcp_gate.py)
# ---------------------------------------------------------------------------

# Maps mcp<digits>_<tool> short-name → logical server identity used as the
# heartbeat key. The server prefix (mcp0_, mcp1_, ...) is NOT stable across
# Windsurf restarts — we key on the tool name, not the numeric prefix.
_HEALTH_TOOLS: dict[str, str] = {
    "adg_health": "adg_sqlite",
    "adg_status": "adg_sqlite",
    "redis_health": "redis",
    "memory_health": "memory",
    "mem_get_stats": "memory",
    "mem_recall_session_start": "memory",
    "otel_status": "otel_mcp",
    "otel_server_info": "otel_mcp",
    "pytest_mcp_health": "pytest_mcp",
}

# Destructive tools — any invocation without a recent health heartbeat for
# the same logical server emits a preflight-violation audit row.
_DESTRUCTIVE_TOOLS: dict[str, str] = {
    "adg_close_connections": "adg_sqlite",
    "adg_reopen_connections": "adg_sqlite",
    "adg_reload": "adg_sqlite",
    "redis_flush_namespace": "redis",
    "redis_del_key": "redis",
    "mem_cleanup_stale": "memory",
}

# Heartbeat freshness window — must match pre_mcp_gate.py _PREFLIGHT_MAX_AGE_S.
_HEARTBEAT_MAX_AGE_S: int = 60

# ---------------------------------------------------------------------------
# Regex primitives for MCP tool-call detection in cursor agent response text
# ---------------------------------------------------------------------------

_INVOKE_TAG_RE = re.compile(r'<invoke\s+name="([^"]+)"', re.IGNORECASE)
_FUNCTION_CALLS_BLOCK_RE = re.compile(
    r"<function_calls>(.*?)</function_calls>",
    re.DOTALL | re.IGNORECASE,
)
# mcp<digits>_<toolname>
_MCP_PREFIX_RE = re.compile(r"^mcp\d+_(.+)$")


def _strip_prefix(tool_name: str) -> str:
    m = _MCP_PREFIX_RE.match(tool_name)
    return m.group(1) if m else tool_name


def _is_retired() -> bool:
    if not ttl_config.exists():
        return False
    try:
        payload = json.loads(ttl_config.read_text(encoding="utf-8"))
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
    return os.environ.get("MCP_PREFLIGHT_BYPASS", "").strip() == "1"


# ---------------------------------------------------------------------------
# Heartbeat management
# ---------------------------------------------------------------------------


def _load_heartbeat() -> dict[str, float]:
    if not heartbeat_path.exists():
        return {}
    try:
        data = json.loads(heartbeat_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    # Filter to numeric values only — any stray keys are ignored.
    return {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}


def _save_heartbeat(heartbeat: dict[str, float]) -> None:
    try:
        heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
        heartbeat_path.write_text(
            json.dumps(heartbeat, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- heartbeat is a best-effort audit artifact; fail-open preserves turn availability
        pass


def _update_heartbeat_from_response(tool_invocations: list[str]) -> set[str]:
    """Stamp the heartbeat for any successful health-class tool invocations.

    We can only observe invocation, not success, from the raw response text.
    Operating principle: if a health tool was invoked in this response AND no
    explicit error marker follows within the same function-call block, treat
    it as success. This is an advisory heuristic — false positives here
    produce MORE heartbeats, which only risks NOT-blocking a subsequent
    destructive call. False negatives are not possible.

    Returns the set of logical servers whose heartbeats were refreshed.
    """
    if not tool_invocations:
        return set()

    refreshed: set[str] = set()
    now = datetime.now(timezone.utc).timestamp()

    for invocation in tool_invocations:
        short = _strip_prefix(invocation)
        server = _HEALTH_TOOLS.get(short)
        if server is None:
            continue
        refreshed.add(server)

    if not refreshed:
        return refreshed

    heartbeat = _load_heartbeat()
    for server in refreshed:
        heartbeat[server] = now
    _save_heartbeat(heartbeat)
    return refreshed


# ---------------------------------------------------------------------------
# Violation detection
# ---------------------------------------------------------------------------


def _extract_tool_invocations(response_text: str) -> list[tuple[int, str]]:
    """Return a list of (block_idx, tool_name) in order of appearance."""

    out: list[tuple[int, str]] = []
    for block_idx, block_match in enumerate(_FUNCTION_CALLS_BLOCK_RE.finditer(response_text)):
        for name in _INVOKE_TAG_RE.findall(block_match.group(1)):
            out.append((block_idx, name))
    return out


def detect_preflight_violations(
    tool_invocations: list[tuple[int, str]],
    heartbeat_before: dict[str, float],
) -> list[dict[str, Any]]:
    """For each destructive call in the response, check heartbeat freshness.

    A health call earlier in the SAME response also counts — we walk
    invocations in order and refresh a local heartbeat copy as we go, so a
    response that chains ``adg_health`` → ``adg_close_connections`` is
    compliant (exactly the pattern this rule wants to incentivize).
    """

    violations: list[dict[str, Any]] = []
    if not tool_invocations:
        return violations

    now = datetime.now(timezone.utc).timestamp()
    local_heartbeat = dict(heartbeat_before)

    for block_idx, invocation in tool_invocations:
        short = _strip_prefix(invocation)
        # Health tools — refresh local heartbeat before moving on
        health_server = _HEALTH_TOOLS.get(short)
        if health_server:
            local_heartbeat[health_server] = now
            continue
        # Destructive tools — check freshness
        destructive_server = _DESTRUCTIVE_TOOLS.get(short)
        if destructive_server is None:
            continue
        last_ok = local_heartbeat.get(destructive_server)
        if last_ok is not None and (now - last_ok) <= _HEARTBEAT_MAX_AGE_S:
            continue  # compliant — recent health or in-response health call
        age_s = None if last_ok is None else round(now - last_ok, 1)
        violations.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "violation_type": "missing_health_preflight",
                "severity": "warning",
                "block_index": block_idx,
                "tool": invocation,
                "short_name": short,
                "server": destructive_server,
                "heartbeat_age_s": age_s,
                "heartbeat_max_age_s": _HEARTBEAT_MAX_AGE_S,
                "remediation": (
                    f"Call the {destructive_server} health tool "
                    f"(adg_health/redis_health/mem_get_stats) in the SAME or a "
                    f"previous response within the last {_HEARTBEAT_MAX_AGE_S}s "
                    f"before invoking {short}. This avoids the MCP-client transport "
                    f"hang pattern that occurs when destructive calls are issued "
                    f"against an unverified server."
                ),
                "rule": "constitutional.md §13 (MCP Green Light)",
                "plan": "mcp-destructive-gate-preflight-e9a14b",
            }
        )

    return violations


# ---------------------------------------------------------------------------
# I/O (audit log write)
# ---------------------------------------------------------------------------


def _append_records(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _append_bypass() -> None:
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "violation_type": "bypass",
                        "severity": "info",
                        "reason": "MCP_PREFLIGHT_BYPASS=1",
                    }
                )
                + "\n"
            )
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info", payload)
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        for key in ("response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def main() -> int:
    if sys.stdin.isatty():
        return 0
    if _is_retired():
        return 0

    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    if _is_bypass():
        _append_bypass()
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    try:
        invocations = _extract_tool_invocations(text)
    except re.error:
        return 0

    heartbeat_before = _load_heartbeat()

    try:
        violations = detect_preflight_violations(invocations, heartbeat_before)
    except (KeyError, ValueError, TypeError):
        violations = []

    # Stamp heartbeats AFTER violation detection so we don't self-absolve
    # retrospectively (violation detector already accounts for in-response
    # health calls via its local_heartbeat walk).
    try:
        _update_heartbeat_from_response([inv for _, inv in invocations])
    except OSError:  # guardian: allow-silent-swallow -- heartbeat write failure must not wedge the turn
        pass

    if violations:
        _append_records(violations)
        print(
            f"[mcp_preflight] DETECTED {len(violations)} preflight violation(s). "
            f"See: artifacts/cursor/mcp_preflight_violations.jsonl",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
