#!/usr/bin/env python3
"""Fail-closed MCP sync integrity gate.

Validates three invariants:
1) `.windsurf/mcp_config.json` is structurally valid.
2) AGENTS.md MCP Quick Reference section exactly matches generated content.
3) Optional: global Windsurf MCP config mirror matches repo SSOT.

Usage:
  python ops_scripts/ci/check_mcp_sync_integrity.py
  python ops_scripts/ci/check_mcp_sync_integrity.py --check-global
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT_DIR = REPO_ROOT / ".windsurf" / "scripts"
if str(SYNC_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SYNC_SCRIPT_DIR))

from sync_mcp_config import (  # noqa: E402
    AGENTS_MD,
    GLOBAL_CONFIG,
    REPO_CONFIG,
    extract_agents_quick_reference,
    generate_agents_quick_reference,
    load_repo_config,
    validate_config,
)


def _read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return data


def _check_repo_config() -> list[str]:
    issues: list[str] = []
    try:
        data = load_repo_config(REPO_CONFIG)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"could not load repo MCP config: {exc}"]

    issues.extend(validate_config(data))
    return issues


def _check_agents_sync() -> list[str]:
    issues: list[str] = []
    if not AGENTS_MD.exists():
        return [f"AGENTS.md not found at {AGENTS_MD}"]

    current = extract_agents_quick_reference(AGENTS_MD.read_text(encoding="utf-8"))
    expected = generate_agents_quick_reference().strip()
    if not current:
        issues.append("AGENTS.md missing MCP Quick Reference section")
    elif current != expected:
        issues.append(
            "AGENTS.md MCP Quick Reference drift detected; run 'python .windsurf/scripts/sync_mcp_config.py'"
        )
    return issues


def _check_global_sync() -> list[str]:
    issues: list[str] = []
    if not GLOBAL_CONFIG.exists():
        return [f"global MCP config not found at {GLOBAL_CONFIG}"]

    try:
        repo_data = _read_json(REPO_CONFIG)
        global_data = _read_json(GLOBAL_CONFIG)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"could not compare repo/global MCP config: {exc}"]

    if repo_data != global_data:
        issues.append("global MCP config drift detected; run 'python .windsurf/scripts/sync_mcp_config.py'")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-global", action="store_true")
    args = parser.parse_args()

    issues: list[str] = []
    issues.extend(_check_repo_config())
    issues.extend(_check_agents_sync())
    if args.check_global:
        issues.extend(_check_global_sync())

    if issues:
        print("[mcp_sync_integrity] FAIL:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        return 1

    print("[mcp_sync_integrity] OK: repo MCP config + AGENTS Quick Reference are in sync.", flush=True)
    if args.check_global:
        print("[mcp_sync_integrity] OK: global MCP config mirror matches repo SSOT.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
