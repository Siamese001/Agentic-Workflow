"""beforeGrep — ADG-first PreToolUse gate for the native ``Grep`` tool.

Thin relay: reads the Claude Code event JSON once, delegates the decision to
``.codex/governance/scripts/pre_grep_gate.py`` (the testable SSOT), and translates the
gate's exit code into a Claude Code allow/block. Fail-open on every error so a broken gate
never wedges a turn. Plan: grep-pretooluse-adg-gate-a3f1c7.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from lib.codex_hook_common import CRIT_PRETOOL, allow, block, write_failopen_receipt, write_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_grep_gate.py"


def _read_raw() -> str:
    try:
        return sys.stdin.read()
    except OSError:
        return ""


raw = _read_raw()
try:
    payload = json.loads(raw) if raw.strip() else {}
    if not isinstance(payload, dict):
        payload = {"value": payload}
except json.JSONDecodeError:
    payload = {"raw": raw}

if not GATE.is_file():
    write_receipt("beforeGrep", payload, "allow", "pre_grep_gate missing — fail-open")
    write_failopen_receipt("beforeGrep", payload, "pre_grep_gate_script_missing", "pre_grep_gate.py absent", CRIT_PRETOOL)
    raise SystemExit(allow("pre_grep_gate not found"))

try:
    proc = subprocess.run(
        [sys.executable, str(GATE)],
        input=raw,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
except (subprocess.TimeoutExpired, OSError) as exc:
    write_receipt("beforeGrep", payload, "allow", f"pre_grep_gate error: {exc}")
    write_failopen_receipt("beforeGrep", payload, "pre_grep_gate_unreachable", str(exc), CRIT_PRETOOL)
    raise SystemExit(allow(f"pre_grep_gate unreachable: {exc}"))

if proc.stderr:
    sys.stderr.write(proc.stderr)

if proc.returncode == 2:
    reason = proc.stdout.strip() or "ADG-first: use adg_sqlite tools, not grep, for dependency analysis."
    write_receipt("beforeGrep", payload, "block", reason)
    raise SystemExit(block(reason))

write_receipt("beforeGrep", payload, "allow", "grep accepted")
raise SystemExit(allow("grep accepted"))
