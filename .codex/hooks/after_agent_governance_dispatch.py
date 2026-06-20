"""afterAgentResponse — unified governance dispatch (W3 cursor-governance-two-tier).

Reads the agent response once, then runs (fail-open, exit 0):
  1. ADG-first audit
  2. Post-response audits (MCP hygiene, long-command). Author-Gate capture chain
     RETIRED W1 (claude-native-supersession-9d3f7a): native AskUserQuestion supersedes it.
  3. In-process post_agent_dispatch (POST_AGENT_DISPATCHER=1)
  4. Delivered-worktree cleanup sweep (merged worktrees/branches only)

Notion status advisory auditor REMOVED (notion-wave-enforcement-removal): the
windsurf/cursor-era Notion plan/status/wave enforcement never functioned (advisory +
token-gated, archived DBs) and is retired.

Replaces three separate subprocess hook wrappers to cut spawn overhead while
preserving deterministic coverage. This file is the post-response chain SSOT.
(The former AG-WIRE CI gate ``ops_scripts/ci/check_ag_hook_wiring.py`` was
decommissioned with the legacy tree — see tests/_archived_obsolete/legacy_tree/.)

W1 (claude-enforcement-runtime-truth-hardening): the live Claude ``Stop`` payload
carries **no** inline response text — it carries ``transcript_path`` (a JSONL of the
turn). The previous implementation *claimed* transcript recovery in a comment but
never read the transcript, so ``payload.get("response")`` was always empty and the
ENTIRE governance chain silently no-opped on every real Stop event. This module now
actually recovers the final assistant message from the transcript, and — critically —
emits a per-Stop dispatch receipt to
``artifacts/governance/post_turn_dispatch_receipts.jsonl`` so a no-op is **visible**
(``dispatch_result=response_unavailable``) rather than silent. Still fail-open: any
internal error exits 0 and never blocks the Stop.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from lib.codex_hook_common import (
    cursor_response_payload,
    read_payload,
    recover_response_from_transcript,
    resolve_response_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / ".codex" / "governance" / "scripts"
_DISPATCH_RECEIPT = REPO_ROOT / "artifacts" / "governance" / "post_turn_dispatch_receipts.jsonl"
_CLEANUP_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "prune_merged_chat_worktrees.py"
_CLEANUP_PREFIXES = "chat/,feat/,codex-,claude-,bcg-"

_SCRIPT_EXTRA_ARGS: dict[str, tuple[str, ...]] = {
    "post_agent_mcp_hygiene_audit.py": ("agent_response",),
    "post_agent_long_command_audit.py": ("agent_response",),
}

# [W1 claude-native-supersession-9d3f7a] Author-Gate audit members removed; native
# AskUserQuestion supersedes the packet/marker/ledger pipeline. Only non-AG
# post-response audits remain.
_AG_CHAIN: tuple[str, ...] = (
    "post_agent_mcp_hygiene_audit.py",
    "post_agent_long_command_audit.py",
    "post_agent_adg_burndown_inline_audit.py",
    "post_agent_work_classification_audit.py",  # Operating Model 2026-06-10: plan-reflex detection
    "post_agent_runtime_rca_audit.py",  # constitutional §37: RCA-on-runtime-failure enforcement
    "post_agent_recommendation_gate_audit.py",  # trigger side: decision surfaced in prose without AskUserQuestion
)


def _write_dispatch_receipt(
    session_id: str,
    *,
    response_present: bool,
    attempted: list[str],
    missing: list[str],
    timed_out: list[str],
    failed_open: list[str],
    result: str,
) -> None:
    """Append one per-Stop dispatch receipt. Best-effort; never raises."""
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "hook": "after_agent_governance_dispatch",
        "session_id": session_id,
        "response_present": response_present,
        "scripts_attempted": attempted,
        "scripts_missing": missing,
        "scripts_timed_out": timed_out,
        "scripts_failed_open": failed_open,
        "dispatch_result": result,
    }
    try:
        _DISPATCH_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        with _DISPATCH_RECEIPT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        return


def _run_script(name: str, raw: str, env: dict[str, str]) -> str:
    """Run one governance sub-script. Returns a status token for the receipt:
    ``missing`` | ``ok`` | ``timeout`` | ``error`` (the last three all fail open)."""
    script = SCRIPTS / name
    if not script.is_file():
        return "missing"
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
        return "ok"
    except subprocess.TimeoutExpired:
        return "timeout"
    except OSError:
        return "error"


def _run_dispatch(parsed_raw: str) -> str:
    import importlib.util
    import io

    os.environ["POST_AGENT_DISPATCHER"] = "1"
    # The dispatch module imports `_post_handlers` (sibling under .codex/governance/scripts) and repo-root
    # packages; ensure both are importable since the hook runs from .codex/hooks.
    for extra in (str(REPO_ROOT), str(SCRIPTS)):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    dispatch = SCRIPTS / "post_agent_dispatch.py"
    if not dispatch.is_file():
        return "missing"
    saved_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(parsed_raw)
        spec = importlib.util.spec_from_file_location("post_agent_dispatch", dispatch)
        if spec is None or spec.loader is None:
            return "error"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "main"):
            mod.main()
        return "ok"
    except Exception as err:  # guardian: allow-broad-exception -- fail-soft; siblings must not break hook
        print(f"[governance_dispatch] dispatch failed: {err}", file=sys.stderr)
        return "error"
    finally:
        sys.stdin = saved_stdin


def _run_worktree_cleanup() -> str:
    if os.environ.get("WORKTREE_AUTOCLEANUP_BYPASS") == "1":
        return "bypassed"
    if not _CLEANUP_SCRIPT.is_file():
        return "missing"

    env = {**os.environ, "WORKTREE_REAP_DETACHED": "1"}
    env.setdefault("WORKTREE_REAP_BRANCH_PREFIXES", _CLEANUP_PREFIXES)
    env.setdefault("WORKTREE_PRUNE_BRANCH_PREFIXES", _CLEANUP_PREFIXES)
    try:
        proc = subprocess.run(
            [sys.executable, str(_CLEANUP_SCRIPT), "--delete-merged"],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        print("[governance_dispatch] worktree cleanup timed out", file=sys.stderr)
        return "timeout"
    except OSError as err:
        print(f"[governance_dispatch] worktree cleanup failed to launch: {err}", file=sys.stderr)
        return "error"

    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if proc.stdout:
        sys.stderr.write(proc.stdout)
        if not proc.stdout.endswith("\n"):
            sys.stderr.write("\n")
    return "ok"


def main() -> int:
    payload = read_payload()
    session_id = str(payload.get("session_id") or "")
    response_text = resolve_response_text(payload)

    if not response_text:
        # Do NOT silently no-op (the W1 bug): emit a visible fail-open receipt so the
        # gap (real Stop payload with no recoverable response) is auditable.
        _write_dispatch_receipt(
            session_id,
            response_present=False,
            attempted=[],
            missing=[],
            timed_out=[],
            failed_open=[],
            result="response_unavailable",
        )
        _run_worktree_cleanup()
        return 0

    raw = cursor_response_payload({"response": response_text})

    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}

    attempted: list[str] = []
    missing: list[str] = []
    timed_out: list[str] = []
    failed_open: list[str] = []

    def _record(name: str, status: str) -> None:
        if status == "missing":
            missing.append(name)
        elif status == "timeout":
            timed_out.append(name)
            attempted.append(name)
        elif status == "error":
            failed_open.append(name)
            attempted.append(name)
        else:  # ok
            attempted.append(name)

    _record("post_agent_adg_audit.py", _run_script("post_agent_adg_audit.py", raw, env))
    for name in _AG_CHAIN:
        _record(name, _run_script(name, raw, env))
    _record("post_agent_dispatch.py", _run_dispatch(raw))

    _write_dispatch_receipt(
        session_id,
        response_present=True,
        attempted=attempted,
        missing=missing,
        timed_out=timed_out,
        failed_open=failed_open,
        result="dispatched",
    )
    _run_worktree_cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
