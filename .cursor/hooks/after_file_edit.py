import json
import os
import subprocess
import sys
from pathlib import Path

from lib.cursor_hook_common import (
    allow,
    block_exit_code,
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


def _audit_plan_wave_summary_top(norm_path: str) -> int | None:
    """Return hook exit code when plan violates consolidated wave summary at top."""
    if not norm_path.replace("\\", "/").startswith(".cursor/plans/"):
        return None
    if not norm_path.endswith(".md"):
        return None
    if "/plans/_archive/" in norm_path.replace("\\", "/"):
        return None

    plan_file = REPO_ROOT / norm_path.replace("/", os.sep)
    if not plan_file.is_file():
        return None

    from ops_scripts.ci.plan_wave_summary_top import (
        WaveSummarySeverity,
        validate_consolidated_wave_summary_at_top,
    )

    rel = norm_path.replace("\\", "/")
    try:
        content = plan_file.read_text(encoding="utf-8")
    except OSError:
        return None

    fails = [
        v
        for v in validate_consolidated_wave_summary_at_top(content, rel)
        if v.severity == WaveSummarySeverity.FAIL
    ]
    if not fails:
        return None

    first = fails[0]
    reason = (
        f"Plan missing consolidated wave summary at top ({first.rule_id}): {first.message} "
        "Add `## Status Tables` → `### Wave Progress` with the canonical wave table "
        "before the first `## Wave N` section. See plan-location.mdc."
    )
    strict = os.environ.get("PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT", "").strip() in (
        "1",
        "true",
        "yes",
    )
    decision = "block" if strict else "warn"
    write_receipt("afterFileEdit", payload, decision, reason)
    if strict:
        print(
            '{"decision": "block", "reason": '
            + json.dumps(reason)
            + "}",
            flush=True,
        )
        return block_exit_code()
    raise SystemExit(warn(reason))


_wave_top_exit = _audit_plan_wave_summary_top(file_path.replace("\\", "/"))
if _wave_top_exit is not None:
    raise SystemExit(_wave_top_exit)

_trigger_mcp_sync(file_path)
write_receipt("afterFileEdit", payload, "allow", "edit accepted")
raise SystemExit(allow("edit accepted"))
