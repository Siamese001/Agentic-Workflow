#!/usr/bin/env python3
"""
pre_write_gate.py — Windsurf pre_write_code hard gate (Phase 1.2).

Reads JSON payload from stdin. Payload fields:
  tool_info.file_path  — path of file being written
  tool_info.edits      — list of {old_string, new_string} dicts

Blocks (exit 2) on:
  - T2/T3 writes without a Task Manager task created in current session
  - Anti-patterns in new_string values:
      * bare 'except:' (no exception type)
      * 'except Exception' without '# guardian: allow-' on same line
      * shell=True in subprocess calls
      * subprocess.run/Popen/call without timeout= (constitutional §14)
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

fail_policy = "closed"

repo_root = Path(__file__).resolve().parents[2]
session_state = repo_root / "artifacts" / "windsurf" / "session_state.json"

_BARE_EXCEPT_RE = re.compile(r"^\s*except\s*:", re.MULTILINE)
_BROAD_EXCEPT_RE = re.compile(r"except\s+Exception(\s*:|\s+as\s+\w+\s*:)")
_GUARDIAN_RE = re.compile(r"#\s*guardian:\s*allow-")
_SHELL_TRUE_RE = re.compile(r"shell\s*=\s*True")
# Matches subprocess call sites — used to enforce timeout= (constitutional §14)
_SUBPROCESS_CALL_RE = re.compile(r"subprocess\.(run|Popen|call|check_output|check_call)\s*\(")
_TIMEOUT_RE = re.compile(r"timeout\s*=")

mcp_config_suffix = "mcp_config.json"
_RISKY_MCP_PATTERNS = [
    re.compile(r'"mcpServers"\s*:\s*\{'),
    re.compile(r'"command"\s*:'),
    re.compile(r'"serverUrl"\s*:'),
    re.compile(r'"env"\s*:'),
]


def check_task_exists(file_path: str) -> str | None:
    """
    Return a block reason if the task lifecycle pre-execution invariants are not met.
    Returns None if write is allowed.
    Fail-open: missing/corrupt state file allows the write.

    Check order (per approved design):
      1. task_created  — T2/T3: create_task must have been called
      2. task_decomposed — T3 only: decompose_task must have been called
      3. task_started  — T2/T3: update_task must have been called (pre-start transition)
    """
    # Only gate .py files in repo — don't block config/docs edits
    if not file_path.endswith(".py"):
        return None

    # Writes to hook scripts themselves are exempt (bootstrap problem)
    if ".windsurf/scripts/" in file_path.replace("\\", "/"):
        return None

    try:
        if not session_state.exists():
            return None  # fail-open: no state file yet
        state = json.loads(session_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None  # fail-open

    tier = state.get("current_tier", "T0")
    if tier not in ("T2", "T3"):
        return None

    # Check 1: task_created
    if not state.get("task_created", False):
        return (
            f"{tier} write attempted without Task Manager task. "
            "Call create_task (task_manager MCP) before editing files. "
            "SR_MANDATE step 2 requires task registration for T2/T3 work."
        )

    # Check 2: task_decomposed (T3 only)
    if tier == "T3" and not state.get("task_decomposed", False):
        return (
            "T3 write blocked: decompose_task not called. "
            "Complex T3 work requires decomposition via decompose_task "
            "(task_manager MCP) before execution."
        )

    # Check 3: task_started (T2/T3)
    if not state.get("task_started", False):
        return (
            f"{tier} write blocked: update_task not called before execution. "
            "Call update_task with status='in_progress' on the active task "
            "before editing files."
        )

    return None


def _exit_block(reason: str) -> int:
    print(f"[pre_write_gate] BLOCKED: {reason}", file=sys.stderr)
    return 2


def _warn(reason: str) -> None:
    print(f"[pre_write_gate] WARNING: {reason}", file=sys.stderr)


def _extract_call_window(text: str, start: int, max_chars: int = 400) -> str:
    """
    Return the substring from start to the balanced closing paren of the call
    that begins at or shortly after start.  Falls back to a fixed max_chars
    window if parens are unbalanced (e.g. incomplete snippet).
    """
    depth = 0
    limit = min(start + max_chars, len(text))
    for i in range(start, limit):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:limit]


def scan_antipatterns(new_string: str) -> list[str]:
    """Return list of violation messages found in new_string."""
    violations = []

    for line in new_string.splitlines():
        stripped = line.strip()

        # Skip comment lines — anti-pattern regexes must not fire on comments
        # to avoid false positives when code is documented with examples.
        if stripped.startswith("#"):
            continue

        if _BARE_EXCEPT_RE.match(line):
            violations.append(
                "Bare 'except:' found — use 'except SpecificError:' (Column 5 Precise Exceptions).",
            )
        if _BROAD_EXCEPT_RE.search(line) and not _GUARDIAN_RE.search(line):
            violations.append(
                "'except Exception' without guardian exemption — narrow exception type or add "
                "'# guardian: allow-broad-exception -- <specific justification>'.",
            )
        if _SHELL_TRUE_RE.search(stripped) and "subprocess" in new_string:
            violations.append(
                "shell=True in subprocess is forbidden — use argv list with shell=False per constitutional §0.",
            )

    # Enforce timeout= on every subprocess call site (constitutional §14).
    # Use paren-depth counting to find the correct closing paren, so that nested
    # calls (e.g. subprocess.run(shlex.split(cmd), timeout=5)) are not falsely
    # flagged as missing timeout.
    for match in _SUBPROCESS_CALL_RE.finditer(new_string):
        window_start = match.start()
        window = _extract_call_window(new_string, window_start)
        if not _TIMEOUT_RE.search(window):
            violations.append(
                f"subprocess.{match.group(1)}() missing timeout= — "
                "constitutional §14: all subprocess calls MUST include timeout=<seconds>. "
                "Omitting timeout= is a zombie subprocess risk.",
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
        if not isinstance(edit, dict):
            continue
        old = edit.get("old_string", "") or ""
        new = edit.get("new_string", "") or ""
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
    if not file_path.endswith(mcp_config_suffix):
        return False, []

    if not edits:
        return True, ["mcp_config.json deletion is DENIED — MCP config is critical infrastructure."]

    warnings = []
    for edit in edits:
        new = edit.get("new_string", "")
        old = edit.get("old_string", "")
        if old and not new:
            warnings.append(
                "mcp_config.json: server block removed — verify this is intentional.",
            )
        for pat in _RISKY_MCP_PATTERNS:
            if pat.search(new):
                warnings.append(
                    "mcp_config.json: risky edit detected (server/transport/env change) — review carefully.",
                )
                break

    return False, warnings


def main() -> int:
    # Fast path: if Windsurf passes file path as argv[1], check it before reading stdin.
    # This prevents fail-closed stdin logic from blocking non-.py/.json writes.
    if len(sys.argv) > 1:
        argv_path = sys.argv[1]
        if not argv_path.endswith(".py") and not argv_path.endswith(mcp_config_suffix):
            return 0

    raw = sys.stdin.read()
    if not raw.strip():
        if fail_policy == "closed":
            print("[pre_write_gate] BLOCKED: empty stdin payload.", file=sys.stderr)
            return 2
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        if fail_policy == "closed":
            print(f"[pre_write_gate] BLOCKED: malformed JSON payload — {exc}", file=sys.stderr)
            return 2
        return 0

    if not isinstance(payload, dict):
        if fail_policy == "closed":
            print("[pre_write_gate] BLOCKED: payload is not a JSON object.", file=sys.stderr)
            return 2
        return 0

    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return 0

    file_path = tool_info.get("file_path", "")
    if not isinstance(file_path, str):
        file_path = ""

    # Normalise edits: null or non-list → treat as empty list
    edits = tool_info.get("edits", [])
    if not isinstance(edits, list):
        edits = []

    # Payload-level file type check (covers cases where argv is not provided).
    if not file_path.endswith(".py") and not file_path.endswith(mcp_config_suffix):
        return 0

    # --- Task existence check for T2/T3 (enforce plan-first discipline) ---
    task_block = check_task_exists(file_path)
    if task_block:
        return _exit_block(task_block)

    violations = []

    for edit in edits:
        if not isinstance(edit, dict):
            continue
        new_string = edit.get("new_string", "")
        if not isinstance(new_string, str):
            continue
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
