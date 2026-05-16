#!/usr/bin/env python3
"""post_cursor_agent_long_command_audit.py — session-level timeout observability.

Reads the Cursor Agent response from stdin (post-agent payload). Scans
``run_command`` invocations in the response for patterns known to run long
(pytest, pre-commit run, git commit at root, npm/pnpm install, docker build,
cargo build, python ``tools/generate_full_adg.py``) and flags those that lack
an explicit timeout guard in the command line.

Subcommands:
  agent_response — **Cursor ``afterAgentResponse`` path** (W1.4): structured
    stderr (NOT_APPLICABLE / ALLOW / VIOLATION), logs under ``artifacts/cursor/``.
    **Advisory only** — always exits 0. **Never** claims to block already-emitted
    ``run_command`` calls.

  (default, no subcommand) — **legacy stdin** dispatch (e.g. shadow
    ``post_cursor_agent_dispatch.py``): fail-open; writes violations only under
    ``artifacts/cursor/`` (no ``artifacts/windsurf`` dependency).

Companion rule: ``.cursor/rules/constitutional.md`` §14 (subprocess timeout)
+ §11 (terminal lifecycle).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]

# Cursor-native paths only (W1.4).
violations_log = repo_root / "artifacts" / "cursor" / "long_command_violations.jsonl"
post_agent_audit_log = repo_root / "artifacts" / "cursor" / "long_command_post_agent_audit.jsonl"

MAX_RESPONSE_BYTES = 512 * 1024

# ---------------------------------------------------------------------------
# Known-long command patterns
# ---------------------------------------------------------------------------

_LONG_COMMAND_PATTERNS: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"\bpytest\b", re.IGNORECASE), "pytest", 60),
    (re.compile(r"\bpre-commit\s+run\b", re.IGNORECASE), "pre-commit run", 30),
    (re.compile(r"\bgit\s+commit\b"), "git commit (triggers pre-commit)", 30),
    (re.compile(r"\bnpm\s+(install|ci)\b"), "npm install", 120),
    (re.compile(r"\bpnpm\s+install\b"), "pnpm install", 120),
    (re.compile(r"\byarn\s+install\b"), "yarn install", 120),
    (re.compile(r"\bdocker\s+(build|compose\s+up)\b"), "docker build/up", 180),
    (re.compile(r"\bcargo\s+(build|test)\b"), "cargo build/test", 120),
    (re.compile(r"\bmaven\b|\bmvn\s+(install|test|package)\b"), "maven", 180),
    (re.compile(r"tools[\\/]generate_full_adg\.py"), "generate_full_adg", 120),
    (re.compile(r"tools[\\/]generate[\\/]generate_full_adg\.py"), "generate_full_adg", 120),
]

# ---------------------------------------------------------------------------
# run_command call extraction
# ---------------------------------------------------------------------------

_RUN_COMMAND_INVOKE_RE = re.compile(
    r'<invoke\s+name="run_command">(.*?)</invoke>',
    re.DOTALL | re.IGNORECASE,
)

_RUN_COMMAND_SURFACE_RE = re.compile(
    r'<invoke\s+name="run_command"',
    re.IGNORECASE,
)

_PARAM_RE = re.compile(
    r'<parameter\s+name="(?P<name>[A-Za-z0-9_]+)">(?P<value>.*?)</parameter>',
    re.DOTALL,
)


def _parse_invoke(block: str) -> dict[str, str]:
    params: dict[str, str] = {}
    for match in _PARAM_RE.finditer(block):
        params[match.group("name")] = match.group("value")
    return params


def _has_inline_timeout(cmd: str) -> bool:
    if re.search(r"(?:^|\s|;|&&|\|\|)timeout\s+\d+", cmd):
        return True
    if re.search(r"--timeout[=\s]\d+", cmd):
        return True
    if re.search(r"\btimeout=\d+", cmd):
        return True
    return False


def _match_long_command(cmd: str) -> tuple[str, int] | None:
    for pattern, label, expected in _LONG_COMMAND_PATTERNS:
        if pattern.search(cmd):
            return (label, expected)
    return None


def detect_violations(response_text: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for match in _RUN_COMMAND_INVOKE_RE.finditer(response_text):
        params = _parse_invoke(match.group(1))
        cmd = params.get("CommandLine", "").strip()
        if not cmd:
            continue
        hit = _match_long_command(cmd)
        if hit is None:
            continue
        if _has_inline_timeout(cmd):
            continue

        label, expected = hit
        blocking = params.get("Blocking", "").strip().lower() == "true"
        violations.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "violation_type": "long_command_no_timeout",
                "code": "LONG_COMMAND_NO_TIMEOUT",
                "severity": "warning",
                "command_label": label,
                "expected_seconds": expected,
                "blocking": blocking,
                "command_preview": cmd[:200],
                "rule": "constitutional.md §11 + §14",
                "remediation": (
                    "Prefix with `timeout N` (Unix/WSL), pass an explicit "
                    "--timeout flag, or start non-blocking with WaitMsBeforeAsync "
                    "so a hung invocation does not wedge the turn."
                ),
            }
        )
    return violations


def _append_violations(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _append_audit_row(row: dict[str, Any]) -> None:
    try:
        post_agent_audit_log.parent.mkdir(parents=True, exist_ok=True)
        with open(post_agent_audit_log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    except OSError:
        pass


def _is_bypass() -> bool:
    return os.environ.get("LONG_COMMAND_AUDIT_BYPASS", "") == "1"


def _read_stdin() -> str:
    try:
        return sys.stdin.read(MAX_RESPONSE_BYTES)
    except OSError:
        return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_agent_response_text(payload: object) -> str:
    """Best-effort text from Cursor afterAgentResponse stdin (dict or string)."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info")
        if isinstance(tool_info, dict):
            nested = _extract_agent_response_text(tool_info)
            if nested.strip():
                return nested
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


def _response_has_run_command_surface(text: str) -> bool:
    if not text or not text.strip():
        return False
    return bool(_RUN_COMMAND_SURFACE_RE.search(text))


def cmd_agent_response(args: argparse.Namespace) -> int:
    """
    Post-agent **advisory** audit: stdin = agent response envelope or raw text.

    Policy: always exit 0. Does not block run_command.
    """
    if _is_bypass():
        print(
            "[LONG_CMD_POST] NOT_APPLICABLE reason=bypass_env LONG_COMMAND_AUDIT_BYPASS",
            file=sys.stderr,
        )
        return 0

    if sys.stdin.isatty():
        print("[LONG_CMD_POST] NOT_APPLICABLE reason=stdin_is_tty", file=sys.stderr)
        return 0

    raw = _read_stdin()
    digest = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:12]

    if not raw.strip():
        print(
            f"[LONG_CMD_POST] NOT_APPLICABLE reason=empty_stdin digest={digest}",
            file=sys.stderr,
        )
        _append_audit_row({"ts": _now_iso(), "event": "not_applicable", "reason": "empty_stdin", "digest12": digest})
        return 0

    try:
        parsed: object = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw

    text = _extract_agent_response_text(parsed)
    if not text.strip():
        print(
            f"[LONG_CMD_POST] NOT_APPLICABLE reason=empty_response_text digest={digest}",
            file=sys.stderr,
        )
        _append_audit_row(
            {"ts": _now_iso(), "event": "not_applicable", "reason": "empty_response_text", "digest12": digest}
        )
        return 0

    if not _response_has_run_command_surface(text):
        print(
            f"[LONG_CMD_POST] NOT_APPLICABLE reason=no_run_command_surface digest={digest}",
            file=sys.stderr,
        )
        _append_audit_row(
            {
                "ts": _now_iso(),
                "event": "not_applicable",
                "reason": "no_run_command_surface",
                "digest12": digest,
            }
        )
        return 0

    try:
        violations = detect_violations(text)
    except re.error:
        print(
            f"[LONG_CMD_POST] NOT_APPLICABLE reason=regex_internal_error digest={digest}",
            file=sys.stderr,
        )
        _append_audit_row(
            {"ts": _now_iso(), "event": "not_applicable", "reason": "regex_internal_error", "digest12": digest}
        )
        return 0

    if violations:
        _append_violations(violations)
        labels = sorted({v["command_label"] for v in violations})
        print(
            f"[LONG_CMD_VIOLATION] code=LONG_COMMAND_NO_TIMEOUT count={len(violations)} "
            f"labels={','.join(labels)} digest={digest} "
            f"(advisory — does not block already-emitted run_command)",
            file=sys.stderr,
        )
        _append_audit_row(
            {
                "ts": _now_iso(),
                "event": "violation_advisory",
                "code": "LONG_COMMAND_NO_TIMEOUT",
                "count": len(violations),
                "labels": labels,
                "digest12": digest,
            }
        )
        return 0

    print(
        f"[LONG_CMD_POST] APPLICABLE outcome=ALLOW reason=long_command_guard_ok digest={digest}",
        file=sys.stderr,
    )
    _append_audit_row(
        {
            "ts": _now_iso(),
            "event": "allow",
            "reason": "long_command_guard_ok",
            "digest12": digest,
        }
    )
    return 0


def cmd_legacy_stdin() -> int:
    """Legacy dispatch: same stdin contract as historical standalone hook (dispatcher-friendly)."""
    if sys.stdin.isatty():
        return 0
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0
    if _is_bypass():
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_agent_response_text(payload)
    if not text.strip():
        return 0

    try:
        violations = detect_violations(text)
    except re.error:
        return 0

    if violations:
        _append_violations(violations)
        print(
            f"[long_command_audit] DETECTED {len(violations)} long-command "
            f"invocation(s) without an explicit timeout. Advisory only — does not block "
            f"already-emitted run_command. See: artifacts/cursor/long_command_violations.jsonl",
            file=sys.stderr,
        )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="post_cursor_agent_long_command_audit")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("agent_response", help="Cursor afterAgentResponse stdin audit (advisory)")
    args = parser.parse_args()
    if args.cmd == "agent_response":
        return cmd_agent_response(args)
    return cmd_legacy_stdin()


if __name__ == "__main__":
    sys.exit(main())
