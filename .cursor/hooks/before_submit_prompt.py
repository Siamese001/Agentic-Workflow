"""beforeSubmitPrompt — legacy guard + ADG-first intent warning injection."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from lib.cursor_hook_common import (
    allow,
    contains_legacy_execution_token,
    text_from_payload,
    warn,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GREP_WARNING = REPO_ROOT / ".cursor" / "scripts" / "pre_user_prompt_grep_for_deps_warning.py"


def _parse_payload(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else {"value": value}
    except json.JSONDecodeError:
        return {"raw": raw}


def _run_grep_for_deps_warning(raw_stdin: str) -> None:
    if not GREP_WARNING.is_file() or not raw_stdin.strip():
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
    except (subprocess.TimeoutExpired, OSError):
        pass


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
    _run_grep_for_deps_warning(raw_stdin)

write_receipt("beforeSubmitPrompt", payload, "allow", "prompt accepted")
raise SystemExit(allow("prompt accepted"))
