#!/usr/bin/env python3
"""Constitutional §27 — Cursor config schema purity.

Validates `.cursor/hooks.json` and `.cursor/mcp.json` contain only fields that
Cursor's parser accepts. Unknown keys can silently disable hooks or MCP servers.

Bypass: CURSOR_CONFIG_SCHEMA_BYPASS=1
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import REPO_ROOT  # noqa: E402

ROOT = REPO_ROOT
HOOKS_PATH = ROOT / ".cursor" / "hooks.json"
MCP_PATH = ROOT / ".cursor" / "mcp.json"

HOOK_ENTRY_FIELDS = {"command", "working_directory", "show_output"}
MCP_SERVER_FIELDS = {
    "command",
    "args",
    "env",
    "disabled",
    "url",
    "type",
    "transport",
}
HOOKS_TOP_LEVEL = {"hooks", "version", "schema_version"}
MCP_TOP_LEVEL = {"mcpServers", "schema_version", "version"}
KNOWN_POISON_FIELDS = {
    "powershell",
    "bash",
    "sh",
    "shell",
    "cmd",
    "platform",
    "os",
    "env_override",
    "runner",
    "interpreter",
    "when",
    "registry",
}


def _check_entry(entry: dict, allowed: set[str], path: str, violations: list[str]) -> None:
    for key in entry.keys():
        if key in allowed or key.startswith("_"):
            continue
        if key in KNOWN_POISON_FIELDS:
            violations.append(
                f"  ❌ {path}: forbidden field '{key}' — may silently disable the entry."
            )
        else:
            violations.append(
                f"  ❌ {path}: unknown field '{key}' — not in documented schema {sorted(allowed)}."
            )


def _validate_hooks(violations: list[str]) -> None:
    if not HOOKS_PATH.exists():
        violations.append(f"  ❌ missing {HOOKS_PATH}")
        return
    try:
        data = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(f"  ❌ {HOOKS_PATH}: invalid JSON — {exc}")
        return

    unknown_top = set(data.keys()) - HOOKS_TOP_LEVEL
    for key in sorted(unknown_top):
        if not key.startswith("_"):
            violations.append(f"  ❌ {HOOKS_PATH.name}: unknown top-level key '{key}'")

    hooks_block = data.get("hooks", {})
    if not isinstance(hooks_block, dict):
        violations.append(f"  ❌ {HOOKS_PATH.name}: 'hooks' must be an object")
        return

    for event_name, entries in hooks_block.items():
        if not isinstance(entries, list):
            violations.append(f"  ❌ {HOOKS_PATH.name}.hooks.{event_name}: must be a list")
            continue
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                violations.append(
                    f"  ❌ {HOOKS_PATH.name}.hooks.{event_name}[{idx}]: must be an object"
                )
                continue
            _check_entry(
                entry,
                HOOK_ENTRY_FIELDS,
                f"{HOOKS_PATH.name}.hooks.{event_name}[{idx}]",
                violations,
            )


def _validate_mcp(violations: list[str]) -> None:
    if not MCP_PATH.exists():
        violations.append(f"  ❌ missing {MCP_PATH}")
        return
    try:
        data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(f"  ❌ {MCP_PATH}: invalid JSON — {exc}")
        return

    unknown_top = set(data.keys()) - MCP_TOP_LEVEL
    for key in sorted(unknown_top):
        if not key.startswith("_"):
            violations.append(f"  ❌ {MCP_PATH.name}: unknown top-level key '{key}'")

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        violations.append(f"  ❌ {MCP_PATH.name}: 'mcpServers' must be an object")
        return

    for server_name, server_cfg in servers.items():
        if not isinstance(server_cfg, dict):
            violations.append(
                f"  ❌ {MCP_PATH.name}.mcpServers.{server_name}: must be an object"
            )
            continue
        _check_entry(
            server_cfg,
            MCP_SERVER_FIELDS,
            f"{MCP_PATH.name}.mcpServers.{server_name}",
            violations,
        )


def main() -> int:
    if os.environ.get("CURSOR_CONFIG_SCHEMA_BYPASS") == "1":
        print("[check_cursor_config_schema] BYPASS=1 — skipping", file=sys.stderr)
        return 0

    print("🔍 Validating Cursor config schema purity (constitutional §27)")
    violations: list[str] = []
    _validate_hooks(violations)
    _validate_mcp(violations)

    if violations:
        print(f"❌ Cursor config schema violations ({len(violations)} issue(s)):")
        for item in violations:
            print(item)
        return 1

    print("✅ Cursor config schema purity validated (hooks.json + mcp.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
