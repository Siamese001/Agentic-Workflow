"""Manual replay of the post_agent_response hook chain.

Workaround for legacy editor 2.0.67 bug where post_agent_response hooks
silently stop firing mid-session (pre_user_prompt hooks continue to work).

Usage
-----
    # From stdin (paste Codex response text):
    python .claude/governance/scripts/manual_post_agent_replay.py < response.txt

    # From clipboard (Windows / pyperclip):
    python .claude/governance/scripts/manual_post_agent_replay.py --clipboard

    # From a file:
    python .claude/governance/scripts/manual_post_agent_replay.py --file response.txt

    # Dry-run (show what would run without invoking hooks):
    python .claude/governance/scripts/manual_post_agent_replay.py --file response.txt --dry-run

What it does
------------
Reads the response text, wraps it in the legacy editor payload shape
``{"tool_info": {"response": "..."}}``, and pipes that JSON through
every entry in ``hooks.post_agent_response`` from ``.claude/settings.json``.
Reports each hook's exit code + stderr summary so silent failures surface.

Why this exists
---------------
legacy editor's post_agent_response hook dispatcher stops invoking hooks
mid-session (root cause upstream; affected 2.0.67). pre_user_prompt
hooks continue working, proving hooks.json is valid. This script is the
fallback that keeps DEFERRED_SCOPE capture, writeback audit, ADG audit,
and heartbeat functioning until the upstream bug is fixed.

Evidence: ``artifacts/governance/post_agent_heartbeat.jsonl`` gap.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS_CONFIG = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
EVENT = "post_agent_response"
TIMEOUT_SECONDS = 120


def _read_response(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.clipboard:
        try:
            import pyperclip  # type: ignore[import-not-found]
        except ImportError:
            print(
                "[manual_replay] --clipboard requires pyperclip. "
                "Install with: pip install pyperclip",
                file=sys.stderr,
            )
            sys.exit(2)
        text: str = str(pyperclip.paste())
        if not text:
            print("[manual_replay] clipboard is empty.", file=sys.stderr)
            sys.exit(2)
        return text
    if sys.stdin.isatty():
        print(
            "[manual_replay] no input. Use --file, --clipboard, or pipe stdin.",
            file=sys.stderr,
        )
        sys.exit(2)
    return sys.stdin.read()


def _load_hooks() -> list[dict]:
    if not HOOKS_CONFIG.exists():
        print(f"[manual_replay] hooks.json not found at {HOOKS_CONFIG}", file=sys.stderr)
        sys.exit(2)
    cfg = json.loads(HOOKS_CONFIG.read_text(encoding="utf-8"))
    hooks: list[dict] = list(cfg.get("hooks", {}).get(EVENT, []))
    if not hooks:
        print(f"[manual_replay] no {EVENT} hooks configured.", file=sys.stderr)
        sys.exit(2)
    return hooks


def _run_hook(hook: dict, payload: str, dry_run: bool) -> tuple[int, str]:
    cmd = hook.get("command") or hook.get("powershell") or ""
    cwd = hook.get("working_directory") or str(REPO_ROOT)
    argv = cmd.split()
    if dry_run:
        return 0, f"DRY-RUN: would run {argv} cwd={cwd}"
    try:
        result = subprocess.run(  # noqa: S603 - argv list, shell=False
            argv,
            cwd=cwd,
            input=payload,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
        tail = (result.stderr or result.stdout or "").strip().splitlines()
        summary = tail[-1] if tail else "(no output)"
        return result.returncode, summary
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except FileNotFoundError as exc:
        return 127, f"FileNotFoundError: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--file", help="Read Codex response from this file.")
    src.add_argument("--clipboard", action="store_true", help="Read from clipboard.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show hook invocation plan without executing.",
    )
    args = parser.parse_args()

    response_text = _read_response(args).strip()
    if not response_text:
        print("[manual_replay] empty response input.", file=sys.stderr)
        return 2

    hooks = _load_hooks()
    payload = json.dumps({"tool_info": {"response": response_text}})
    payload_size = len(payload)

    print(f"[manual_replay] replaying {len(hooks)} post_agent_response hooks")
    print(f"[manual_replay] payload size: {payload_size} bytes")
    if args.dry_run:
        print("[manual_replay] DRY RUN — no hooks invoked")

    failed = 0
    for i, hook in enumerate(hooks, start=1):
        script_name = Path((hook.get("command") or "").split()[-1]).name
        rc, summary = _run_hook(hook, payload, args.dry_run)
        status = "OK" if rc == 0 else f"FAIL rc={rc}"
        print(f"  [{i}/{len(hooks)}] {script_name:<50} {status:<12} {summary}")
        if rc != 0:
            failed += 1

    print(
        f"[manual_replay] done. hooks={len(hooks)} failed={failed} "
        f"(0 = all chain steps completed; non-zero = investigate individually)"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
