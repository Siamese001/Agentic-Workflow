"""beforeMCPExecution — legacy-token guard + pre_mcp_gate delegation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from lib.cursor_hook_common import (
    allow,
    block,
    block_exit_code,
    contains_legacy_execution_token,
    normalize_mcp_payload,
    text_from_payload,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_MCP_GATE = REPO_ROOT / ".cursor" / "scripts" / "pre_mcp_gate.py"


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

    write_receipt("beforeMCPExecution", payload, "allow", "MCP request accepted")
    return allow("MCP request accepted")


raw_stdin = sys.stdin.read() if not sys.stdin.isatty() else ""
payload = _parse_payload(raw_stdin)
text = text_from_payload(payload) or raw_stdin
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = "MCP request targets legacy execution surface: " + ", ".join(legacy)
    write_receipt("beforeMCPExecution", payload, "block", reason)
    raise SystemExit(block(reason))

raise SystemExit(_run_pre_mcp_gate(payload))
