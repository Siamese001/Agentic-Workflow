"""afterAgentResponse — unified governance dispatch (W3 cursor-governance-two-tier).

Reads agent response stdin once, then runs (fail-open, exit 0):
  1. ADG-first audit
  2. Post-response audits (MCP hygiene, long-command). Author-Gate capture chain
     RETIRED W1 (claude-native-supersession-9d3f7a): native AskUserQuestion supersedes it.
  3. In-process post_agent_dispatch (POST_AGENT_DISPATCHER=1)

Notion status advisory auditor REMOVED (notion-wave-enforcement-removal): the
windsurf/cursor-era Notion plan/status/wave enforcement never functioned (advisory +
token-gated, archived DBs) and is retired.

Replaces three separate subprocess hook wrappers to cut spawn overhead while
preserving deterministic coverage. This file is the post-response chain SSOT.
(The former AG-WIRE CI gate ``ops_scripts/ci/check_ag_hook_wiring.py`` was
decommissioned with the legacy tree — see tests/_archived_obsolete/legacy_tree/.)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from lib.claude_hook_common import cursor_response_payload, read_payload

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / ".claude" / "governance" / "scripts"

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


def _run_script(name: str, raw: str, env: dict[str, str]) -> None:
    script = SCRIPTS / name
    if not script.is_file():
        return
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
        return


def _run_dispatch(parsed_raw: str) -> None:
    import importlib.util
    import io

    os.environ["POST_AGENT_DISPATCHER"] = "1"
    # The dispatch module imports `_post_handlers` (sibling under .claude/governance/scripts) and repo-root
    # packages; ensure both are importable since the hook runs from .claude/hooks.
    for extra in (str(REPO_ROOT), str(SCRIPTS)):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    dispatch = SCRIPTS / "post_agent_dispatch.py"
    if not dispatch.is_file():
        return
    saved_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(parsed_raw)
        spec = importlib.util.spec_from_file_location("post_agent_dispatch", dispatch)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "main"):
            mod.main()
    except Exception as err:  # guardian: allow-broad-exception -- fail-soft; siblings must not break hook
        print(f"[governance_dispatch] dispatch failed: {err}", file=sys.stderr)
    finally:
        sys.stdin = saved_stdin


def main() -> int:
    # Claude Code `Stop` payload carries no response text — recover the final assistant
    # message from the transcript and re-shape it to the legacy afterAgentResponse payload
    # the governance chain scripts parse. Fail-open: empty response => no-op.
    payload = read_payload()
    raw = cursor_response_payload(payload)
    if not str(payload.get("response") or "").strip():
        return 0

    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}

    _run_script("post_agent_adg_audit.py", raw, env)

    for name in _AG_CHAIN:
        _run_script(name, raw, env)

    _run_dispatch(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
