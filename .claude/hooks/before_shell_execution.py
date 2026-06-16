import sys
from pathlib import Path

from lib.claude_hook_common import allow, block, contains_legacy_execution_token, read_payload, text_from_payload, write_receipt

# Wire the turn-hanging command guards (python -c quote-hazard + interactive/pager) from the
# governance gate into this live PreToolUse Bash hook. Previously pre_run_gate.py implemented
# these but was never dispatched, so the bans (constitutional §26 + python-dash-c-quote-hazard.md)
# were doctrine-only. Fail-open if the module is unavailable — a missing gate must never wedge shells.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance" / "scripts"))
try:
    from pre_run_gate import shell_command_block_reason
except Exception:  # guardian: allow-broad-exception -- hook fail-open if gate module is unavailable
    shell_command_block_reason = None


def _command_text(p: dict) -> str:
    """Best-effort extraction of the shell command string from the PreToolUse payload."""
    ti = p.get("tool_input")
    if isinstance(ti, dict) and isinstance(ti.get("command"), str):
        return ti["command"]
    if isinstance(p.get("command"), str):
        return p["command"]
    info = p.get("tool_info")
    if isinstance(info, dict) and isinstance(info.get("command_line"), str):
        return info["command_line"]
    return ""


payload = read_payload()
text = text_from_payload(payload)
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = "Shell command targets legacy execution surface: " + ", ".join(legacy)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

risky = []
for token in ("rm -rf .cursor", "rmdir /s .cursor", "del /s .cursor", "Remove-Item .cursor"):
    if token in text:
        risky.append(token)
if risky:
    reason = "Shell command risks deleting active Cursor controls: " + ", ".join(risky)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

# Turn-hanging command guard (quote-hazard / interactive / pager), enforced via pre_run_gate.
if shell_command_block_reason is not None:
    command = _command_text(payload)
    if command:
        hang_reason = shell_command_block_reason(command)
        if hang_reason:
            write_receipt("beforeShellExecution", payload, "block", hang_reason)
            raise SystemExit(block(hang_reason))

# Branch/worktree naming is advisory on Bash commands. The edit hook remains the
# hard safety boundary by blocking protected-checkout mutations.

write_receipt("beforeShellExecution", payload, "allow", "command accepted")
raise SystemExit(allow("command accepted"))
