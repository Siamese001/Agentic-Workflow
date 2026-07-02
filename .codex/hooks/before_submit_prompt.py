"""beforeSubmitPrompt — legacy guard + ADG-first intent warning injection."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from lib.codex_hook_common import (
    ADVISORY_CAPTURE,
    CRIT_PRETURN,
    allow,
    block,
    contains_legacy_execution_token,
    text_from_payload,
    warn,
    write_failopen_receipt,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GREP_WARNING = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_user_prompt_grep_for_deps_warning.py"
REQUIRED_MCP_GATE = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_user_prompt_required_mcp_gate.py"
ADG_SSOT_GATE = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_user_prompt_adg_ssot_gate.py"


def _parse_payload(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {"value": value}
    except json.JSONDecodeError:
        return {"raw": raw}


def _run_grep_for_deps_warning(raw_stdin: str, payload: dict[str, Any]) -> None:
    if not raw_stdin.strip():
        return
    if not GREP_WARNING.is_file():
        write_failopen_receipt(
            "beforeSubmitPrompt", payload, "grep_warning_script_missing",
            "pre_user_prompt_grep_for_deps_warning.py absent", ADVISORY_CAPTURE,
        )
        return
    try:
        proc = subprocess.run(
            [sys.executable, str(GREP_WARNING)],
            input=raw_stdin,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(REPO_ROOT),
            },
        )
        if proc.stderr:
            sys.stderr.write(proc.stderr)
            if not proc.stderr.endswith("\n"):
                sys.stderr.write("\n")
    except (subprocess.TimeoutExpired, OSError) as exc:
        write_failopen_receipt(
            "beforeSubmitPrompt", payload, "grep_warning_unreachable", str(exc), ADVISORY_CAPTURE,
        )


def _run_adg_ssot_gate(raw_stdin: str, payload: dict[str, Any]) -> int:
    """Dispatch the ADG SQLite-SSOT green-light gate; return its exit code (0 or 2).

    Surfaces the gate's stderr. Exit 2 means a T2/T3 prompt must be blocked because
    the ADG SQLite SSOT snapshot is unavailable (constitutional §13). Fail-open: any
    dispatch error returns 0 so a probe failure never blocks the prompt — but the fail-open
    is now recorded to the fail-open ledger (CRITICAL_PRETURN) so it is not invisible.
    """
    if not raw_stdin.strip():
        return 0
    if not ADG_SSOT_GATE.is_file():
        write_failopen_receipt(
            "beforeSubmitPrompt", payload, "adg_ssot_gate_script_missing",
            "pre_user_prompt_adg_ssot_gate.py absent — T2/T3 ADG green-light not enforced", CRIT_PRETURN,
        )
        return 0
    try:
        proc = subprocess.run(
            [sys.executable, str(ADG_SSOT_GATE)],
            input=raw_stdin,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)},
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        write_failopen_receipt(
            "beforeSubmitPrompt", payload, "adg_ssot_gate_unreachable", str(exc), CRIT_PRETURN,
        )
        return 0  # fail-open: do not block on dispatch failure
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")
    return proc.returncode


def _run_required_mcp_gate(raw_stdin: str, payload: dict[str, Any]) -> int:
    """Dispatch the all-required-MCP Codex transport gate.

    Unlike advisory prompt enrichment, this gate is fail-closed: if the gate
    cannot run, the hook cannot prove required MCP transports are green.
    """
    if not raw_stdin.strip():
        return 0
    if not REQUIRED_MCP_GATE.is_file():
        reason = "pre_user_prompt_required_mcp_gate.py absent - required MCP green-light not enforced"
        write_receipt("beforeSubmitPrompt", payload, "block", reason)
        print(f"[required_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
        return 2
    try:
        proc = subprocess.run(
            [sys.executable, str(REQUIRED_MCP_GATE)],
            input=raw_stdin,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=int(__import__("os").environ.get("REQUIRED_MCP_GATE_HOOK_TIMEOUT_SEC", "180")),
            check=False,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)},
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        reason = f"required MCP gate unreachable: {type(exc).__name__}: {exc}"
        write_receipt("beforeSubmitPrompt", payload, "block", reason)
        print(f"[required_mcp_gate] BLOCKED: {reason}", file=sys.stderr)
        return 2
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")
    return proc.returncode


raw_stdin = sys.stdin.read() if not sys.stdin.isatty() else ""
payload = _parse_payload(raw_stdin)
text = text_from_payload(payload) or raw_stdin
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = (
        "Prompt references legacy execution surface; treat as archive only "
        "unless the task is explicit migration: " + ", ".join(legacy)
    )
    write_receipt("beforeSubmitPrompt", payload, "warn", reason)
    raise SystemExit(warn(reason))

if raw_stdin.strip():
    _run_grep_for_deps_warning(raw_stdin, payload)

# Required Codex MCP transport green-light: every enabled repo MCP must be
# callable through its configured Codex transport before normal prompt handling.
if _run_required_mcp_gate(raw_stdin, payload) != 0:
    reason = (
        "Required Codex MCP transports unavailable before turn - "
        "repair MCP transport/callability first."
    )
    write_receipt("beforeSubmitPrompt", payload, "block", reason)
    raise SystemExit(block(reason))

# Constitutional §13 ADG SQLite-SSOT + MCP transport green-light (Redis is advisory hot cache only).
if _run_adg_ssot_gate(raw_stdin, payload) == 2:
    reason = (
        "ADG SQLite SSOT or MCP transport unavailable for T2/T3 prompt - "
        "restore active ADG callability before proceeding (constitutional §13)."
    )
    write_receipt("beforeSubmitPrompt", payload, "block", reason)
    raise SystemExit(block(reason))

write_receipt("beforeSubmitPrompt", payload, "allow", "prompt accepted")
raise SystemExit(allow("prompt accepted"))
