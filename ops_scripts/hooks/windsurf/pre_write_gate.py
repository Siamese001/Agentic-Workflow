#!/usr/bin/env python3
"""
pre_write_gate.py — Windsurf pre_write_code hard gate (Phase 1.2).

Reads JSON payload from stdin. Payload fields:
  tool_info.file_path  — path of file being written
  tool_info.edits      — list of {old_string, new_string} dicts

Blocks (exit 2) on:
  - Anti-patterns in new_string values:
      * bare 'except:' (no exception type)
      * 'except Exception' without '# guardian: allow-' on same line
      * 'shell=True' in subprocess calls
  - Python syntax errors: reconstructs projected file, runs ast.parse()
  - Deletion of mcp_config.json (file_path ends with mcp_config.json, edits empty → DENY)

Warns (stderr, exit 0) on:
  - Risky mcp_config.json edits (server removal, transport change, env var change)

Fail policy: CLOSED — malformed/missing JSON → exit 2 with diagnostic.
Zero hardcoded paths.
"""

import ast
import json
import re
import sys
from pathlib import Path

FAIL_POLICY = "closed"

_BARE_EXCEPT_RE = re.compile(r"^\s*except\s*:", re.MULTILINE)
_BROAD_EXCEPT_RE = re.compile(r"except\s+Exception(\s*:|\s+as\s+\w+\s*:)")
_GUARDIAN_RE = re.compile(r"#\s*guardian:\s*allow-")
_SHELL_TRUE_RE = re.compile(r"shell\s*=\s*True")

MCP_CONFIG_SUFFIX = "mcp_config.json"
_RISKY_MCP_PATTERNS = [
    re.compile(r'"mcpServers"\s*:\s*\{'),
    re.compile(r'"command"\s*:'),
    re.compile(r'"serverUrl"\s*:'),
    re.compile(r'"env"\s*:'),
]


def _exit_block(reason: str) -> int:
    print(f"[pre_write_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def _warn(reason: str) -> None:
    print(f"[pre_write_gate] WARNING: {reason}", file=sys.stderr)


def scan_antipatterns(new_string: str) -> list[str]:
    """Return list of violation messages found in new_string."""
    violations = []

    for line in new_string.splitlines():
        stripped = line.strip()
        if _BARE_EXCEPT_RE.match(line):
            violations.append(
                "Bare 'except:' found — use 'except SpecificError:' (Column 5 Precise Exceptions)."
            )
        if _BROAD_EXCEPT_RE.search(line) and not _GUARDIAN_RE.search(line):
            violations.append(
                "'except Exception' without guardian exemption — narrow exception type or add "
                "'# guardian: allow-broad-exception -- <specific justification>'."
            )
        if _SHELL_TRUE_RE.search(stripped) and "subprocess" in new_string:
            violations.append(
                "'shell=True' in subprocess is forbidden — use argv list with shell=False per constitutional §0."
            )

    return violations


def reconstruct_projected_content(file_path: str, edits: list[dict]) -> str | None:
    """
    Apply edits sequentially to current on-disk file to produce projected content.
    Returns None if file does not exist (new file creation — use concatenation of new_strings).
    """
    path = Path(file_path)
    if path.exists():
        content = path.read_text(encoding="utf-8")
    else:
        content = ""

    for edit in edits:
        old = edit.get("old_string", "")
        new = edit.get("new_string", "")
        if old:
            content = content.replace(old, new, 1)
        else:
            content = content + new

    return content


def check_python_syntax(file_path: str, edits: list[dict]) -> list[str]:
    """Return list of syntax error messages (empty = clean)."""
    if not file_path.endswith(".py"):
        return []

    projected = reconstruct_projected_content(file_path, edits)
    if projected is None:
        return []

    try:
        ast.parse(projected)
        return []
    except SyntaxError as exc:
        return [f"Python syntax error after edit: {exc.msg} (line {exc.lineno})"]


def check_mcp_config(file_path: str, edits: list[dict]) -> tuple[bool, list[str]]:
    """
    Returns (should_block, warning_messages) for mcp_config.json edits.
    Block if: no edits provided (file being deleted).
    Warn if: risky patterns detected in new_string values.
    """
    if not file_path.endswith(MCP_CONFIG_SUFFIX):
        return False, []

    if not edits:
        return True, ["mcp_config.json deletion is DENIED — MCP config is critical infrastructure."]

    warnings = []
    for edit in edits:
        new = edit.get("new_string", "")
        old = edit.get("old_string", "")
        if old and not new:
            warnings.append(
                "mcp_config.json: server block removed — verify this is intentional."
            )
        for pat in _RISKY_MCP_PATTERNS:
            if pat.search(new):
                warnings.append(
                    "mcp_config.json: risky edit detected (server/transport/env change) — review carefully."
                )
                break

    return False, warnings


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        if FAIL_POLICY == "closed":
            print("[pre_write_gate] BLOCKED: empty stdin payload.", file=sys.stderr)
            return 2
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        if FAIL_POLICY == "closed":
            print(f"[pre_write_gate] BLOCKED: malformed JSON payload — {exc}", file=sys.stderr)
            return 2
        return 0

    tool_info = payload.get("tool_info", payload)
    file_path = tool_info.get("file_path", "")
    edits = tool_info.get("edits", [])

    violations = []

    for edit in edits:
        new_string = edit.get("new_string", "")
        violations.extend(scan_antipatterns(new_string))

    violations.extend(check_python_syntax(file_path, edits))

    mcp_block, mcp_warnings = check_mcp_config(file_path, edits)
    for w in mcp_warnings:
        _warn(w)
    if mcp_block:
        violations.extend(mcp_warnings)

    if violations:
        for v in violations:
            _exit_block(v)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
