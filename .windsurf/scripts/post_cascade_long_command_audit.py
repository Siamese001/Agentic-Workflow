#!/usr/bin/env python3
"""post_cascade_long_command_audit.py — session-level timeout observability.

Reads the Cascade response from stdin (post_cascade_response payload).
Scans ``run_command`` invocations in the response for patterns known to
run long (pytest, pre-commit run, git commit at root, npm/pnpm install,
docker build, cargo build, python ``tools/generate_full_adg.py``) and
flags those that lack an explicit timeout guard in either the command
line itself or a sibling ``command_status WaitDurationSeconds``.

Policy: **advisory only** — always exits 0. Never blocks. Logs to
``artifacts/windsurf/long_command_violations.jsonl`` so session-level
timeout discipline becomes measurable even though the tool schema has no
native ``timeout`` field.

Companion rule: ``.windsurf/rules/constitutional.md`` §14 (subprocess
timeout) + §11 (terminal lifecycle). Workflow:
``.windsurf/workflows/timeout-progress-enforcement.md``.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[2]
violations_log = repo_root / "artifacts" / "windsurf" / "long_command_violations.jsonl"

# ---------------------------------------------------------------------------
# Known-long command patterns
# ---------------------------------------------------------------------------

# Each entry: (pattern, label, default_expected_seconds)
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

# Matches <invoke name="run_command">...</invoke> blocks in response text.
_RUN_COMMAND_INVOKE_RE = re.compile(
    r'<invoke\s+name="run_command">(.*?)</invoke>',
    re.DOTALL,
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
    """Return True if the command line itself expresses a timeout."""

    # Unix: `timeout 60 ...`
    if re.search(r"(?:^|\s|;|&&|\|\|)timeout\s+\d+", cmd):
        return True
    # gtimeout, PowerShell's Start-Process -Wait -Timeout, Python-side -timeout flags
    if re.search(r"--timeout[=\s]\d+", cmd):
        return True
    # subprocess.run(..., timeout=N) directly on the command line (rare)
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


def _append(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    try:
        violations_log.parent.mkdir(parents=True, exist_ok=True)
        with open(violations_log, "a", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
        pass


def _is_bypass() -> bool:
    return os.environ.get("LONG_COMMAND_AUDIT_BYPASS", "") == "1"


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

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    try:
        violations = detect_violations(text)
    except re.error:  # defensive
        return 0

    if violations:
        _append(violations)
        print(
            f"[long_command_audit] DETECTED {len(violations)} long-command "
            f"invocation(s) without an explicit timeout. See: "
            f"artifacts/windsurf/long_command_violations.jsonl",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
