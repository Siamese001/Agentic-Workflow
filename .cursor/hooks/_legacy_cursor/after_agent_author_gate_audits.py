"""afterAgentResponse — LEGACY Author-Gate chain (superseded).

**SSOT:** ``.cursor/hooks/after_agent_governance_dispatch.py`` runs ADG + this chain +
Notion audit + ``post_cursor_agent_dispatch``. Do not add this file to ``hooks.json``.

Kept for unit tests and manual replay only. New wiring must target governance_dispatch.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / ".cursor" / "scripts"

# Scripts that need argv after the script path (Cursor post-agent contract).
_SCRIPT_EXTRA_ARGS: dict[str, tuple[str, ...]] = {
    "post_cursor_agent_mcp_hygiene_audit.py": ("agent_response",),
    "post_cursor_agent_long_command_audit.py": ("agent_response",),
}

_CHAIN: tuple[str, ...] = (
    "post_cursor_agent_author_gate_capture.py",
    "post_cursor_agent_author_gate_miss_detector.py",
    "post_cursor_agent_author_gate_ui_audit.py",
    "post_cursor_agent_author_gate_schema_audit.py",
    "post_cursor_agent_ask_user_question_packet_audit.py",
    "post_cursor_agent_author_gate_pipeline_audit.py",
    "post_cursor_agent_ag_queue_drain_audit.py",
    "post_cursor_agent_ag_queue_seed_capture.py",
    "post_cursor_agent_mcp_hygiene_audit.py",
    "post_cursor_agent_long_command_audit.py",
)


def main() -> int:
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)}
    for name in _CHAIN:
        script = SCRIPTS / name
        if not script.is_file():
            continue
        try:
            argv = [sys.executable, str(script), *_SCRIPT_EXTRA_ARGS.get(name, ())]
            proc = subprocess.run(
                argv,
                input=raw,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
                env=env,
            )
            if proc.stderr:
                sys.stderr.write(proc.stderr)
                if not proc.stderr.endswith("\n"):
                    sys.stderr.write("\n")
        except (subprocess.TimeoutExpired, OSError):
            continue
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
