#!/usr/bin/env python3
"""post_cursor_agent_mcp_hygiene_audit.py — Unified MCP Hygiene audit hook (W2.P5).

Subcommands:
  agent_response — **Cursor ``afterAgentResponse`` path** (W1.3): reads agent response
    JSON/text from stdin; detects MCP-related surface; runs **advisory** serialization
    checks; logs under ``artifacts/cursor/``. **Never blocks** (exit 0). **Never**
    invokes orphan process reap.

  preflight — stub preflight log (legacy CLI).

  orphan_reap — **explicit opt-in only**: may run ``check_orphan_mcp_processes.py --kill``.
    **Not** invoked from ``run_all`` or ``agent_response``.

  run_all — runs **preflight** only; **does not** run orphan_reap (safety).

See also: ``.cursor/hooks/after_agent_governance_dispatch.py`` (chain invokes
``python ... post_cursor_agent_mcp_hygiene_audit.py agent_response``).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATHS = {
    "preflight": REPO_ROOT / "artifacts" / "cursor" / "mcp_preflight_violations.jsonl",
    "orphan_reap": REPO_ROOT / "artifacts" / "cursor" / "mcp_orphan_reap.jsonl",
    "serialization": REPO_ROOT / "artifacts" / "cursor" / "mcp_serialization_violations.jsonl",
    "post_agent": REPO_ROOT / "artifacts" / "cursor" / "mcp_post_agent_hygiene.jsonl",
}
MAX_RESPONSE_BYTES = 512 * 1024

BYPASS_VARS = {
    "preflight": "MCP_PREFLIGHT_AUDIT_BYPASS",
    "orphan_reap": "MCP_ORPHAN_REAP_BYPASS",
}

# Remote / high-latency MCP name prefixes (legacy cascade contract).
_REMOTE_MCP_SHORT_NAMES = ("notion", "tavily", "deepwiki", "context7", "GitKraken")

_MCP_SURFACE_RE = re.compile(
    r"(mcp\d+_|<invoke\s+[^>]*name=\"(?:mcp\d+_)?|call_mcp|\bMCP\s*:\s*)",
    re.IGNORECASE,
)


def _read_stdin() -> str:
    try:
        return sys.stdin.read(MAX_RESPONSE_BYTES)
    except Exception:
        return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_log(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def _extract_agent_response_text(payload: object) -> str:
    """Best-effort text from Cursor afterAgentResponse stdin (dict or string)."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("response", "text", "content", "message", "agentMessage", "output"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        for nest in ("result", "data", "body"):
            sub = payload.get(nest)
            if isinstance(sub, dict):
                nested = _extract_agent_response_text(sub)
                if nested.strip():
                    return nested
        try:
            return json.dumps(payload, default=str)
        except (TypeError, ValueError):
            return ""
    return str(payload) if payload is not None else ""


def _response_has_mcp_surface(text: str) -> bool:
    if not text or not text.strip():
        return False
    return bool(_MCP_SURFACE_RE.search(text))


def _serialization_violations(text: str) -> list[str]:
    """Duplicate remote MCP prefix markers in one response (legacy heuristic)."""
    violations: list[str] = []
    for mcp in _REMOTE_MCP_SHORT_NAMES:
        needle = f"{mcp}_"
        if text.count(needle) > 1:
            violations.append(mcp)
    return violations


def cmd_agent_response(args: argparse.Namespace) -> int:
    """
    Post-agent **advisory** audit: stdin = agent response envelope or raw text.

    Policy: always exit 0. Emits stderr markers; appends JSONL only when material.
    """
    if os.environ.get("MCP_HYGIENE_BYPASS") == "1" or os.environ.get("MCP_POST_AGENT_HYGIENE_BYPASS") == "1":
        print(
            "[MCP_HYGIENE_POST] NOT_APPLICABLE reason=bypass_env MCP_POST_AGENT_HYGIENE_BYPASS or MCP_HYGIENE_BYPASS",
            file=sys.stderr,
        )
        return 0

    if sys.stdin.isatty():
        print("[MCP_HYGIENE_POST] NOT_APPLICABLE reason=stdin_is_tty", file=sys.stderr)
        return 0

    raw = _read_stdin()
    if not raw.strip():
        print("[MCP_HYGIENE_POST] NOT_APPLICABLE reason=empty_stdin", file=sys.stderr)
        return 0

    try:
        parsed: object = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw

    text = _extract_agent_response_text(parsed)
    digest = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:12]

    if not _response_has_mcp_surface(text):
        print(
            f"[MCP_HYGIENE_POST] NOT_APPLICABLE reason=no_mcp_surface_in_response digest={digest}",
            file=sys.stderr,
        )
        _append_log(
            LOG_PATHS["post_agent"],
            {
                "ts": _now_iso(),
                "event": "not_applicable",
                "reason": "no_mcp_surface_in_response",
                "digest12": digest,
            },
        )
        return 0

    violations = _serialization_violations(text)
    if violations:
        row = {
            "ts": _now_iso(),
            "event": "serialization_violation",
            "violations": violations,
            "digest12": digest,
        }
        _append_log(LOG_PATHS["serialization"], row)
        print(
            f"[MCP_HYGIENE_VIOLATION] code=SERIALIZATION_REMOTE_DUP "
            f"servers={','.join(violations)} digest={digest} "
            f"(advisory — MCP calls already executed)",
            file=sys.stderr,
        )
        _append_log(
            LOG_PATHS["post_agent"],
            {
                "ts": _now_iso(),
                "event": "violation_advisory",
                "code": "SERIALIZATION_REMOTE_DUP",
                "violations": violations,
                "digest12": digest,
            },
        )
        return 0

    print(
        f"[MCP_HYGIENE_POST] APPLICABLE outcome=ALLOW reason=serialization_ok digest={digest}",
        file=sys.stderr,
    )
    _append_log(
        LOG_PATHS["post_agent"],
        {
            "ts": _now_iso(),
            "event": "allow",
            "reason": "serialization_ok",
            "digest12": digest,
        },
    )
    return 0


def cmd_preflight(args: argparse.Namespace) -> int:
    """MCP preflight audit - check before MCP operations (stub)."""
    if os.environ.get(BYPASS_VARS["preflight"]) == "1" or os.environ.get("MCP_HYGIENE_BYPASS") == "1":
        return 0
    _append_log(LOG_PATHS["preflight"], {"ts": _now_iso(), "event": "preflight_checked", "stub": True})
    return 0


def cmd_orphan_reap(args: argparse.Namespace) -> int:
    """Reap orphan MCP server processes — **explicit subcommand only** (not from agent_response/run_all)."""
    if os.environ.get(BYPASS_VARS["orphan_reap"]) == "1" or os.environ.get("MCP_HYGIENE_BYPASS") == "1":
        return 0
    detector = REPO_ROOT / "tools" / "debug" / "check_orphan_mcp_processes.py"
    if detector.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(detector), "--kill"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            _append_log(
                LOG_PATHS["orphan_reap"],
                {"ts": _now_iso(), "exit_code": result.returncode, "output": result.stdout[:500]},
            )
        except Exception as e:
            _append_log(LOG_PATHS["orphan_reap"], {"ts": _now_iso(), "error": str(e)})
    return 0


def _cmd_run_all(args: argparse.Namespace) -> int:
    """Run preflight only. Orphan reap is opt-in via ``orphan_reap`` subcommand (W1.3 safety)."""
    try:
        cmd_preflight(args)
    except Exception as e:
        print(f"[mcp_hygiene] preflight error: {e}", file=sys.stderr)
    print(
        "[mcp_hygiene] run_all: orphan_reap skipped — invoke `orphan_reap` subcommand explicitly if needed.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="post_cursor_agent_mcp_hygiene_audit")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("agent_response", help="Cursor afterAgentResponse stdin audit (advisory; no reap)")
    sub.add_parser("preflight", help="MCP preflight audit (stub)")
    sub.add_parser("orphan_reap", help="Orphan MCP process reaping (explicit opt-in; uses --kill)")
    sub.add_parser("run_all", help="Preflight only; does not reap")
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0
    dispatch: dict[str, Any] = {
        "agent_response": cmd_agent_response,
        "preflight": cmd_preflight,
        "orphan_reap": cmd_orphan_reap,
        "run_all": _cmd_run_all,
    }
    return dispatch.get(args.cmd, lambda _: 0)(args)


if __name__ == "__main__":
    sys.exit(main())
