import subprocess
import sys
from pathlib import Path

from lib.cursor_hook_common import (
    allow,
    contains_legacy_execution_token,
    payload_path,
    read_payload,
    text_from_payload,
    warn,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _trigger_mcp_sync(file_path: str) -> None:
    if not file_path.lower().endswith(".cursor/mcp.json"):
        return
    sync_script = REPO_ROOT / ".cursor" / "scripts" / "post_write_mcp_config_sync.py"
    if not sync_script.exists():
        return
    subprocess.run(
        [sys.executable, str(sync_script), file_path],
        cwd=str(REPO_ROOT),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


payload = read_payload()
text = text_from_payload(payload)
file_path = payload_path(payload)
legacy = contains_legacy_execution_token(text + "\n" + file_path)
if legacy and "/plans/_archive/" not in file_path:
    reason = "Edit references legacy execution surface outside archive: " + ", ".join(legacy)
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))

if file_path.startswith(".cursor/plans/_archive/") or "/plans/_archive/" in file_path:
    reason = "Edited archived historical plan material; confirm this was intentional reference maintenance."
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))

_trigger_mcp_sync(file_path)
write_receipt("afterFileEdit", payload, "allow", "edit accepted")
raise SystemExit(allow("edit accepted"))
