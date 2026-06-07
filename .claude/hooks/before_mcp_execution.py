"""beforeMCPExecution — legacy-token guard + pre_mcp_gate + plan auditor + MCP hygiene (W1.2)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from lib.claude_hook_common import (
    allow,
    block,
    block_exit_code,
    contains_legacy_execution_token,
    normalize_mcp_payload,
    text_from_payload,
    write_receipt,
)
from lib.mcp_before_hygiene import run_mcp_before_hygiene_stage

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_MCP_GATE = REPO_ROOT / ".claude" / "governance" / "scripts" / "pre_mcp_gate.py"
UNIFIED_PLAN_AUDITOR = REPO_ROOT / ".claude" / "governance" / "scripts" / "unified_plan_creation_auditor.py"


def _parse_payload(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {"value": value}
    except json.JSONDecodeError:
        return {"raw": raw}


def _run_pre_mcp_gate(payload: dict[str, Any]) -> int:
    if not PRE_MCP_GATE.is_file():
        write_receipt("beforeMCPExecution", payload, "allow", "pre_mcp_gate missing — fail-open")
        return allow("pre_mcp_gate script not found")

    normalized = normalize_mcp_payload(payload)
    try:
        proc = subprocess.run(
            [sys.executable, str(PRE_MCP_GATE)],
            input=json.dumps(normalized),
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(REPO_ROOT),
            },
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        write_receipt("beforeMCPExecution", payload, "allow", f"pre_mcp_gate error: {exc}")
        return allow(f"pre_mcp_gate unreachable: {exc}")

    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")

    if proc.returncode == 2:
        reason = proc.stderr.strip() or "pre_mcp_gate blocked MCP execution"
        write_receipt("beforeMCPExecution", payload, "block", reason[:500])
        print(json.dumps({"decision": "block", "reason": reason[:500]}))
        return block_exit_code()

    return 0


def _run_unified_plan_auditor(normalized_payload: dict[str, Any]) -> int:
    """
    Stage 2: Notion plan-create MCP audit (after pre_mcp_gate allows).

    stdin to the auditor is a merge of the original Cursor payload + normalized tool_info.
    """
    if not UNIFIED_PLAN_AUDITOR.is_file():
        print(
            "[PLAN_AUDITOR] NOT_APPLICABLE reason=unified_plan_creation_auditor_script_missing",
            file=sys.stderr,
        )
        return 0

    os_mod = __import__("os")
    try:
        proc = subprocess.run(
            [sys.executable, str(UNIFIED_PLAN_AUDITOR), "mcp_before"],
            input=json.dumps(normalized_payload),
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env={
                **dict(os_mod.environ),
                "PYTHONPATH": str(REPO_ROOT),
            },
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(
            f"[PLAN_AUDITOR_BLOCK] code=MCP_AUDITOR_UNREACHABLE reason={exc}",
            file=sys.stderr,
        )
        write_receipt(
            "beforeMCPExecution",
            normalized_payload,
            "block",
            f"plan auditor subprocess error: {exc}"[:500],
        )
        print(json.dumps({"decision": "block", "reason": f"plan auditor unreachable: {exc}"[:500]}))
        return block_exit_code()

    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")

    if proc.returncode == 2:
        reason = proc.stderr.strip() or "unified_plan_creation_auditor blocked MCP execution"
        write_receipt("beforeMCPExecution", normalized_payload, "block", reason[:500])
        print(json.dumps({"decision": "block", "reason": reason[:500]}))
        return block_exit_code()

    if proc.returncode != 0:
        # cursor-decommission W7: FAIL-SOFT. Exit 2 (intentional block) is handled
        # above. Any OTHER non-zero means the advisory plan-create auditor itself
        # malfunctioned — that must NOT block all MCP traffic. Warn and allow.
        print(
            f"[PLAN_AUDITOR_WARN] code=PLAN_AUDITOR_NONZERO_EXIT reason=exit_{proc.returncode} "
            "(fail-soft: allowing MCP call)",
            file=sys.stderr,
        )
        write_receipt(
            "beforeMCPExecution",
            normalized_payload,
            "warn",
            f"plan auditor exit {proc.returncode} (fail-soft allow)"[:500],
        )
        return 0

    return 0


raw_stdin = sys.stdin.read() if not sys.stdin.isatty() else ""
payload = _parse_payload(raw_stdin)

# pre_mcp_gate keys its session_state file on VSCODE_PID, else getppid(). Under Claude Code
# every hook is a fresh process, so getppid() changes each call and the memory-first /
# heartbeat state never persists. Pin a stable per-session key from Claude's session_id.
_sid = str(payload.get("session_id") or "").strip()
if _sid and not os.environ.get("VSCODE_PID"):
    os.environ["VSCODE_PID"] = "claude-" + _sid

# The gate only auto-marks memory_recalled on its degrade-open paths; a successful
# mem_recall_session_start returns early (Rule 1) without marking. Mark it here so the
# memory-first precondition is satisfied for subsequent MCP calls this session.
_tn = str(payload.get("tool_name") or payload.get("toolName") or "")
if _tn.endswith("mem_recall_session_start"):
    try:
        _vp = os.environ.get("VSCODE_PID") or str(os.getppid())
        _ss = REPO_ROOT / "artifacts" / "governance" / f"session_state_{_vp}.json"
        _st = json.loads(_ss.read_text(encoding="utf-8")) if _ss.exists() else {}
        if not isinstance(_st, dict):
            _st = {}
        _st["memory_recalled"] = True
        _st["max_memory_block_attempts"] = 0
        _ss.parent.mkdir(parents=True, exist_ok=True)
        _ss.write_text(json.dumps(_st), encoding="utf-8")
    except Exception:  # noqa: BLE001 - fail-open: gate degrades open after 3 attempts anyway
        pass

text = text_from_payload(payload) or raw_stdin
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = "MCP request targets legacy execution surface: " + ", ".join(legacy)
    write_receipt("beforeMCPExecution", payload, "block", reason)
    raise SystemExit(block(reason))

gate_rc = _run_pre_mcp_gate(payload)
if gate_rc != 0:
    raise SystemExit(gate_rc)

normalized_for_auditor = normalize_mcp_payload(payload)
auditor_rc = _run_unified_plan_auditor(normalized_for_auditor)
if auditor_rc != 0:
    raise SystemExit(auditor_rc)

hygiene_rc = run_mcp_before_hygiene_stage(normalized_for_auditor)
if hygiene_rc != 0:
    reason = "mcp_before_hygiene blocked — see stderr for [MCP_HYGIENE_BLOCK]"
    write_receipt("beforeMCPExecution", payload, "block", reason[:500])
    print(json.dumps({"decision": "block", "reason": reason[:500]}))
    raise SystemExit(block_exit_code())

write_receipt(
    "beforeMCPExecution",
    payload,
    "allow",
    "MCP request accepted (pre_mcp_gate + plan auditor + mcp_before_hygiene)",
)
raise SystemExit(allow("MCP request accepted"))
