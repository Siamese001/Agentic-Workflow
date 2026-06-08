"""CI gate: every post_agent_*.py hook must use the shared payload extractor.

The 2026-04-23 RCA found two hooks (`post_agent_deferred_scope_capture.py`
and `post_agent_writeback_audit.py`) silently dropping DEFERRED_SCOPE
markers because they ignored the documented Windsurf payload shape
``{"tool_info": {"response": "..."}}`` and fell through to `json.dumps`
which escapes newlines and breaks multiline regex anchors.

This gate enforces:

  1. Every ``.claude/governance/scripts/post_agent_*.py`` hook (excluding helpers
     prefixed with `_` and the heartbeat which has no payload) MUST
     ``from _post_agent_payload import extract_response_text`` OR
     accept raw stdin without JSON parsing (the heartbeat/cleanup case).
  2. No hook may reimplement the old broken pattern of
     ``json.loads(...).get("response")`` without a fallback into
     ``tool_info``.

Exit codes:
    0 — OK
    1 — violations found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / ".claude" / "governance/scripts"

# Hooks that legitimately do not read stdin — they are pure-side-effect writers.
_NO_STDIN_HOOKS: frozenset[str] = frozenset(
    {
        "post_agent_heartbeat.py",
        "post_agent_cleanup.py",
        "post_agent_hitl_capture.py",  # thin shim, no payload reading
        "post_agent_plan_supersession_retire.py",  # drains stdin; scans plan files
    }
)

_WIRED_HOOKS: frozenset[str] = frozenset(
    {
        "post_agent_adg_audit.py",
        "post_agent_mcp_hygiene_audit.py",
        "post_agent_long_command_audit.py",
        "post_agent_adg_burndown_inline_audit.py",
        "post_agent_dispatch.py",
        "post_agent_scope_drift_detector.py",
        "post_agent_writeback_audit.py",
        "post_agent_deferred_scope_capture.py",
        "post_agent_next_step_capture.py",
        "post_agent_next_step_miss_detector.py",
        "post_agent_wave_lifecycle_capture.py",
        "post_agent_wave_completion_audit.py",
        "post_agent_mcp_preflight_audit.py",
        "post_agent_plan_evidence_gate.py",
        "post_agent_plan_wave_summary_audit.py",
        "post_agent_plan_registration_capture.py",
        "post_agent_plan_supersession_retire.py",
        "post_agent_fortknox_integrity_audit.py",
    }
)

_REQUIRED_IMPORT = "from _post_agent_payload import extract_response_text"
_BROKEN_PATTERN = re.compile(
    # json.loads(...).get("response") / payload.get("response") without tool_info
    r"""payload\.get\(\s*['"]response['"]\s*\)""",
)
_TOOL_INFO_ACCESS = re.compile(r"tool_info")


def _should_check(path: Path) -> bool:
    name = path.name
    if not name.startswith("post_agent_"):
        return False
    if not name.endswith(".py"):
        return False
    if name.startswith("_"):
        return False  # helper modules
    return name not in _NO_STDIN_HOOKS


def check_file(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path.name}: read failed: {exc}"]

    uses_shared_extractor = _REQUIRED_IMPORT in source

    # Fast path: if it uses the shared extractor, it's compliant.
    if uses_shared_extractor:
        return []

    # Otherwise it must not roll its own by calling payload.get("response")
    # without also consulting tool_info.
    has_broken = _BROKEN_PATTERN.search(source) is not None
    has_tool_info = _TOOL_INFO_ACCESS.search(source) is not None

    if has_broken and not has_tool_info:
        problems.append(
            f"{path.name}: reads payload.get('response') without consulting "
            f"tool_info. Replace with `{_REQUIRED_IMPORT}` (see "
            f".claude/governance/scripts/_post_agent_payload.py)."
        )
    elif not has_tool_info and "sys.stdin" in source:
        problems.append(
            f"{path.name}: reads sys.stdin but does not import "
            f"extract_response_text and does not reference tool_info. "
            f"Windsurf delivers payload at tool_info.response — this hook "
            f"will silently drop real payloads. Replace with "
            f"`{_REQUIRED_IMPORT}`."
        )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    targets = sorted(
        p for p in (_SCRIPTS / name for name in _WIRED_HOOKS) if p.is_file() and _should_check(p)
    )
    if args.verbose:
        print(f"[check_post_agent_payload] scanning {len(targets)} hook(s)")
        for t in targets:
            print(f"  - {t.name}")

    all_problems: list[str] = []
    for path in targets:
        all_problems.extend(check_file(path))

    if all_problems:
        print("\n[check_post_agent_payload] VIOLATIONS:")
        for msg in all_problems:
            print(f"  - {msg}")
        print(
            "\nRemediation: each post_agent_*.py hook MUST use\n"
            f"    {_REQUIRED_IMPORT}\n"
            "See .claude/governance/scripts/_post_agent_payload.py for the SSOT."
        )
        return 1

    if args.verbose:
        print("[check_post_agent_payload] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
