#!/usr/bin/env python3
"""Fail-closed MCP sync integrity gate.

Validates:
1) Root `.mcp.json` (Claude Code project SSOT) is structurally valid.
2) AGENTS.md MCP Quick Reference matches `.claude/governance/scripts/sync_mcp_config.py` output.
3) Optional: global Cursor MCP mirror matches repo SSOT (`--check-global`).
4) Optional: Windsurf mirror structural validity (`--check-windsurf-mirror`).

Usage:
  python ops_scripts/ci/check_mcp_sync_integrity.py
  python ops_scripts/ci/check_mcp_sync_integrity.py --check-global
  python ops_scripts/ci/check_mcp_sync_integrity.py --check-windsurf-mirror
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import WINDSURF_MCP_PATH, import_cursor_sync  # noqa: E402


def _read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return data


def _check_repo_config(sync) -> list[str]:
    issues: list[str] = []
    try:
        data = sync.load_repo_config(sync.REPO_CONFIG)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"could not load root MCP config: {exc}"]

    issues.extend(sync.validate_config(data))
    return issues


def _check_agents_sync(sync) -> list[str]:
    issues: list[str] = []
    if not sync.AGENTS_MD.exists():
        return [f"AGENTS.md not found at {sync.AGENTS_MD}"]

    current = sync.extract_agents_quick_reference(sync.AGENTS_MD.read_text(encoding="utf-8"))
    expected = sync.generate_agents_quick_reference().strip()
    if not current:
        issues.append("AGENTS.md missing MCP Quick Reference section")
    elif current != expected:
        issues.append(
            "AGENTS.md MCP Quick Reference drift detected; run "
            "'python .claude/governance/scripts/sync_mcp_config.py'"
        )
    return issues


def _check_global_sync(sync) -> list[str]:
    issues: list[str] = []
    if not sync.GLOBAL_CONFIG.exists():
        return [f"global Cursor MCP config not found at {sync.GLOBAL_CONFIG}"]

    try:
        repo_data = _read_json(sync.REPO_CONFIG)
        global_data = _read_json(sync.GLOBAL_CONFIG)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"could not compare repo/global Cursor MCP config: {exc}"]

    if repo_data != global_data:
        issues.append(
            "global Cursor MCP config drift detected; run "
            "'python .claude/governance/scripts/sync_mcp_config.py'"
        )
    return issues


def _check_windsurf_mirror(sync) -> list[str]:
    issues: list[str] = []
    if not WINDSURF_MCP_PATH.exists():
        return [f"Windsurf MCP mirror missing at {WINDSURF_MCP_PATH}"]
    try:
        data = _read_json(WINDSURF_MCP_PATH)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"could not load Windsurf MCP mirror: {exc}"]
    issues.extend(sync.validate_config(data))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-global", action="store_true")
    parser.add_argument("--check-windsurf-mirror", action="store_true")
    args = parser.parse_args()

    sync = import_cursor_sync()
    issues: list[str] = []
    issues.extend(_check_repo_config(sync))
    issues.extend(_check_agents_sync(sync))
    if args.check_global:
        issues.extend(_check_global_sync(sync))
    if args.check_windsurf_mirror:
        issues.extend(_check_windsurf_mirror(sync))

    if issues:
        print("[mcp_sync_integrity] FAIL:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        return 1

    print(
        "[mcp_sync_integrity] OK: .mcp.json + AGENTS Quick Reference are in sync.",
        flush=True,
    )
    if args.check_global:
        print("[mcp_sync_integrity] OK: global Cursor MCP mirror matches repo SSOT.", flush=True)
    if args.check_windsurf_mirror:
        print("[mcp_sync_integrity] OK: Windsurf MCP mirror is structurally valid.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
