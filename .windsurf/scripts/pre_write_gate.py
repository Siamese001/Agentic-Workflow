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
import datetime
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _secret_patterns import scan_content as _scan_secrets  # noqa: E402
from _ssot_folder_check import decide as _ssot_decide  # noqa: E402

try:
    import jsonschema as _jsonschema
    _JSONSCHEMA_AVAILABLE = True
except ImportError:  # guardian: allow-broad-exception -- optional dep; gate fails closed without it
    _JSONSCHEMA_AVAILABLE = False

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

# Core Addition Author-Gate forbidden app literals (W3 lightweight scan)
_CORE_FORBIDDEN_LITERALS: tuple[str, ...] = (
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_qna",
    "resume_generator",
    "outreach",
    "company_brief",
    "interview_card",
    "recruiter",
)

_SCHEMA_PATH = repo_root / ".windsurf" / "schemas" / "CoreAdditionAuthorGateReceipt.schema.json"
_VIOLATIONS_LOG = repo_root / "artifacts" / "windsurf" / "core_addition_gate_violations.jsonl"

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
    except (
        OSError,
        json.JSONDecodeError,
    ):  # guardian: allow-return-none-swallow -- session state read: non-fatal, fail-open
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
    """Return list of violation messages found in new_string.

    Note: no progress bar — per-edit regex scan on a single content blob,
    bounded in size, runs in <5ms. (Satisfies §16 progress detection marker.)
    """
    # progress_bar: intentionally omitted — single blob scan, sub-5ms bounded work
    violations = []

    # Secret pattern scan — run once per edit, not per line (regex walks internally).
    # Blocks commits of hard-coded keys, tokens, passwords, private keys.
    for label, line_no in _scan_secrets(new_string, max_hits=5):
        violations.append(
            f"Secret detected ({label}) on added line {line_no} — "
            f"move to an env var or secret manager before committing.",
        )

    for line in new_string.splitlines():
        "progress_bar: intentionally omitted — bounded per-edit content, sub-5ms scan"
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
        "progress_bar: intentionally omitted — small edits list (typically 1-5 entries)"
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


def _append_violation_event(path: str, reason: str, bypassed: bool) -> None:
    """Append an audit event to core_addition_gate_violations.jsonl."""
    event = {
        "path": path,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "reason": reason,
        "bypassed": bypassed,
        "CORE_ADDITION_GATE_BYPASS": os.environ.get("CORE_ADDITION_GATE_BYPASS", "0"),
    }
    try:
        _VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    except OSError:  # guardian: allow-broad-exception -- audit log write is non-fatal; never block on log failure
        pass


def check_core_addition_receipt(file_path: str, new_string: str) -> str | None:
    """
    Core Addition Author-Gate check (W3 lightweight binding).

    Returns a block reason string if the write should be denied, or None if allowed.

    Scope: author-time receipt binding only.
    Full proof validation (digest recompute, artifact verdict checks) is deferred to W4/W7.

    Bypass: CORE_ADDITION_GATE_BYPASS=1 allows the write but logs an audit event.
    """
    norm = file_path.replace("\\", "/")
    if "agentic_core/" not in norm:
        return None

    bypass = os.environ.get("CORE_ADDITION_GATE_BYPASS") == "1"

    def _block(reason: str) -> str | None:
        _append_violation_event(file_path, reason, bypassed=bypass)
        if bypass:
            _warn(f"CORE_ADDITION_GATE_BYPASS active — violation logged but write allowed: {reason}")
            return None
        return reason

    # --- 1. Load active plan metadata from session_state ----------------------
    try:
        if not session_state.exists():
            return _block(
                "agentic_core/ write blocked: no session_state.json found. "
                "Active plan metadata (plan_type=platform_core_change) is required."
            )
        state = json.loads(session_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:  # guardian: allow-broad-exception -- session state read failure must block, not pass
        return _block(f"agentic_core/ write blocked: could not read session_state.json — {exc}")

    plan_meta = state.get("active_plan", {})
    if not isinstance(plan_meta, dict):
        plan_meta = {}

    plan_id = plan_meta.get("plan_id", "")
    plan_type = plan_meta.get("plan_type", "")
    touches_core = plan_meta.get("touches_agentic_core", False)
    gate_required = plan_meta.get("core_addition_author_gate_required", False)
    receipt_ref = plan_meta.get("author_gate_receipt_ref", "")

    if not plan_id:
        return _block(
            "agentic_core/ write blocked: active plan has no plan_id. "
            "Set plan_type=platform_core_change in session_state.active_plan."
        )
    if plan_type != "platform_core_change":
        return _block(
            f"agentic_core/ write blocked: plan_type is '{plan_type}', "
            "must be 'platform_core_change'."
        )
    if not touches_core:
        return _block(
            "agentic_core/ write blocked: touches_agentic_core is not true in active plan metadata."
        )
    if not gate_required:
        return _block(
            "agentic_core/ write blocked: core_addition_author_gate_required is not true in active plan metadata."
        )
    if not receipt_ref:
        return _block(
            "agentic_core/ write blocked: author_gate_receipt_ref is empty in active plan metadata."
        )

    # --- 2. Load receipt file -------------------------------------------------
    receipt_path = Path(receipt_ref) if Path(receipt_ref).is_absolute() else repo_root / receipt_ref
    try:
        receipt_text = receipt_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _block(f"agentic_core/ write blocked: cannot read receipt file '{receipt_ref}' — {exc}")

    try:
        receipt = json.loads(receipt_text)
    except json.JSONDecodeError as exc:
        return _block(f"agentic_core/ write blocked: malformed receipt JSON in '{receipt_ref}' — {exc}")

    # --- 3. Schema validation -------------------------------------------------
    if not _JSONSCHEMA_AVAILABLE:
        return _block(
            "agentic_core/ write blocked: jsonschema package unavailable; "
            "cannot validate CoreAdditionAuthorGateReceipt."
        )
    try:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = _jsonschema.Draft7Validator(schema)
        schema_errors = [e.message for e in validator.iter_errors(receipt)]
    except (OSError, json.JSONDecodeError, Exception) as exc:  # guardian: allow-broad-exception -- schema load failure must block
        return _block(f"agentic_core/ write blocked: could not load/run receipt schema — {exc}")

    if schema_errors:
        return _block(
            f"agentic_core/ write blocked: receipt fails schema validation — "
            + "; ".join(schema_errors[:3])
        )

    # --- 4. Semantic field checks ---------------------------------------------
    if receipt.get("receipt_type") != "CoreAdditionAuthorGateReceipt":
        return _block(
            f"agentic_core/ write blocked: receipt.receipt_type is "
            f"'{receipt.get('receipt_type')}', expected 'CoreAdditionAuthorGateReceipt'."
        )
    if receipt.get("plan_type") != "platform_core_change":
        return _block(
            f"agentic_core/ write blocked: receipt.plan_type is "
            f"'{receipt.get('plan_type')}', expected 'platform_core_change'."
        )
    if receipt.get("plan_id") != plan_id:
        return _block(
            f"agentic_core/ write blocked: receipt.plan_id '{receipt.get('plan_id')}' "
            f"does not match active plan_id '{plan_id}'."
        )

    decision = receipt.get("decision", {})
    if decision.get("verdict") != "PASS":
        return _block(
            f"agentic_core/ write blocked: receipt.decision.verdict is "
            f"'{decision.get('verdict')}', must be 'PASS'."
        )

    changed_paths = receipt.get("changed_paths", [])
    covered = any(
        norm.endswith(cp.replace("\\", "/")) or cp.replace("\\", "/") in norm
        for cp in changed_paths
    )
    if not covered:
        return _block(
            f"agentic_core/ write blocked: '{file_path}' is not covered by "
            f"receipt.changed_paths {changed_paths}."
        )

    sig = receipt.get("signature", {})
    digest = sig.get("receipt_digest", "")
    if not digest or not str(digest).startswith("sha256:"):
        return _block(
            "agentic_core/ write blocked: receipt.signature.receipt_digest is "
            "missing or does not start with 'sha256:'."
        )

    # --- 5. Lightweight forbidden literal scan --------------------------------
    for literal in _CORE_FORBIDDEN_LITERALS:
        if literal in new_string:
            return _block(
                f"agentic_core/ write blocked: forbidden app literal '{literal}' found in new content. "
                "Core must remain app-agnostic (agentic-core-static.md)."
            )

    return None


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    # Fast path: if Windsurf passes file path as argv[1], check it before reading stdin.
    # This prevents fail-closed stdin logic from blocking non-.py/.json writes.
    if len(sys.argv) > 1:
        argv_path = sys.argv[1]
        argv_norm = argv_path.replace("\\", "/")
        # Block .env writes — Cursor Agent cannot read it (pre_read_gate blocks it), so any
        # write from Cursor Agent will be a blank overwrite that destroys real API keys.
        if argv_norm.endswith("/.env") or argv_norm == ".env":
            print("[pre_write_gate] BLOCKED: .env writes are forbidden — edit manually in VS Code.", file=sys.stderr)
            return 2
        if (
            not argv_path.endswith(".py")
            and not argv_path.endswith(mcp_config_suffix)
            and "agentic_core/" not in argv_norm
        ):
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
    # Allow .py, .json (mcp_config), and files under agentic_core/ regardless of extension.
    norm_fp = file_path.replace("\\", "/")
    is_core = "agentic_core/" in norm_fp
    if norm_fp.endswith("/.env") or norm_fp == ".env":
        return _exit_block(".env writes are forbidden — edit manually in VS Code.")
    if not file_path.endswith(".py") and not file_path.endswith(mcp_config_suffix) and not is_core:
        return 0

    # --- SSOT folder routing check (constitutional §31) ---------------------
    # Only catches NEW files — pre-existing files in any folder pass through.
    # Bypass: SSOT_FOLDER_BYPASS=1 (logged below).
    ssot_bypass = os.environ.get("SSOT_FOLDER_BYPASS") == "1"
    try:
        target_exists = Path(file_path).exists() if file_path else True
    except OSError:  # guardian: allow-return-none-swallow -- best-effort path probe; SSOT check fails open here
        target_exists = True
    ssot_violation = _ssot_decide(file_path, target_exists)
    if ssot_violation is not None and not ssot_bypass:
        return _exit_block(
            f"SSOT folder routing violation [{ssot_violation.forbidden}]: "
            f"{ssot_violation.message} Bypass: SSOT_FOLDER_BYPASS=1.",
        )
    if ssot_violation is not None and ssot_bypass:
        _warn(
            f"SSOT folder violation BYPASSED for {ssot_violation.path} "
            f"(suggested: {ssot_violation.suggested}).",
        )

    # --- Task existence check for T2/T3 (enforce plan-first discipline) ---
    task_block = check_task_exists(file_path)
    if task_block:
        return _exit_block(task_block)

    # --- Core Addition Author-Gate (W3) ---------------------------------------
    # Run once across all edits: any forbidden literal in any new_string blocks.
    combined_new = "\n".join(
        edit.get("new_string", "") or ""
        for edit in edits
        if isinstance(edit, dict)
    )
    core_block = check_core_addition_receipt(file_path, combined_new)
    if core_block:
        return _exit_block(core_block)

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
