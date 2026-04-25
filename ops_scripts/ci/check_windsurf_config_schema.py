#!/usr/bin/env python3
"""Constitutional §26 — Windsurf config schema purity.

Validates that `.windsurf/hooks.json` and `.windsurf/mcp_config.json` contain
only fields published in the official Windsurf schema. Unknown keys (e.g.
`powershell`, `bash`, `shell`, `env_override`, `platform`) silently disable
the hook entry or MCP server — Windsurf's parser rejects the entry with no
error surfaced to the user.

Precedent (2026-04-23):
    A `powershell` field added to 23 hook entries silently disabled the
    entire `post_cascade_response` chain across a full Windsurf restart.
    Detected only via heartbeat-log forensics.

Schema whitelists (per docs/windsurf/hooks.md + docs/windsurf/mcp.md):

    hooks.json per-entry:    command, working_directory, show_output
    mcp_config.json per srv: command, args, env, disabled

Top-level wrapper keys (`hooks`, `mcpServers`, `_note`, schema version) are
allowed. This gate is deterministic, has no external deps, and exits 1 on
any unrecognized field.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS_PATH = ROOT / ".windsurf" / "hooks.json"
MCP_PATH = ROOT / ".windsurf" / "mcp_config.json"

# Schema whitelists — extend ONLY when docs/windsurf/*.md is updated upstream.
# Underscore-prefixed keys (e.g. `_note`, `_comment`) are universally allowed
# as an inline-documentation convention; Windsurf's parser tolerates them.
HOOK_ENTRY_FIELDS = {"command", "working_directory", "show_output"}
# MCP servers support two transports:
#   - Local stdio:   command + args + env
#   - Remote HTTP:   url + optional type/transport
# `disabled` is universal.
MCP_SERVER_FIELDS = {
    "command",
    "args",
    "env",
    "disabled",
    "url",
    "type",
    "transport",
}

# Top-level keys that may appear alongside the documented schema.
HOOKS_TOP_LEVEL = {"hooks", "schema_version", "version"}
MCP_TOP_LEVEL = {"mcpServers", "schema_version", "version"}

# Fields that LOOK plausible but are known to silently break Windsurf.
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
}


def _check_entry(entry: dict, allowed: set[str], path: str, violations: list[str]) -> None:
    for key in entry.keys():
        if key in allowed:
            continue
        if key.startswith("_"):
            # Underscore-prefixed = documentation/metadata convention. Tolerated
            # by Windsurf's parser across both hooks.json and mcp_config.json.
            continue
        if key in KNOWN_POISON_FIELDS:
            violations.append(
                f"  ❌ {path}: forbidden field '{key}' — this silently disables "
                f"the entry in Windsurf. See constitutional §26."
            )
        else:
            violations.append(
                f"  ❌ {path}: unknown field '{key}' — not in documented schema "
                f"{sorted(allowed)}. Remove or verify against docs/windsurf/."
            )


def _validate_hooks(violations: list[str]) -> None:
    if not HOOKS_PATH.exists():
        return
    try:
        data = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(f"  ❌ {HOOKS_PATH}: invalid JSON — {exc}")
        return

    unknown_top = set(data.keys()) - HOOKS_TOP_LEVEL
    for key in sorted(unknown_top):
        if key.startswith("_"):
            continue
        violations.append(f"  ❌ {HOOKS_PATH.name}: unknown top-level key '{key}'")

    hooks_block = data.get("hooks", {})
    if not isinstance(hooks_block, dict):
        violations.append(
            f"  ❌ {HOOKS_PATH.name}: 'hooks' must be an object, got {type(hooks_block).__name__}"
        )
        return

    for event_name, entries in hooks_block.items():
        if not isinstance(entries, list):
            violations.append(
                f"  ❌ {HOOKS_PATH.name}.hooks.{event_name}: must be a list, got {type(entries).__name__}"
            )
            continue
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                violations.append(
                    f"  ❌ {HOOKS_PATH.name}.hooks.{event_name}[{idx}]: must be an "
                    f"object, got {type(entry).__name__}"
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
        return
    try:
        data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        violations.append(f"  ❌ {MCP_PATH}: invalid JSON — {exc}")
        return

    unknown_top = set(data.keys()) - MCP_TOP_LEVEL
    for key in sorted(unknown_top):
        if key.startswith("_"):
            continue
        violations.append(f"  ❌ {MCP_PATH.name}: unknown top-level key '{key}'")

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        violations.append(
            f"  ❌ {MCP_PATH.name}: 'mcpServers' must be an object, got {type(servers).__name__}"
        )
        return

    for server_name, server_cfg in servers.items():
        if not isinstance(server_cfg, dict):
            violations.append(
                f"  ❌ {MCP_PATH.name}.mcpServers.{server_name}: must be an "
                f"object, got {type(server_cfg).__name__}"
            )
            continue
        _check_entry(
            server_cfg,
            MCP_SERVER_FIELDS,
            f"{MCP_PATH.name}.mcpServers.{server_name}",
            violations,
        )


def main() -> int:
    print("🔍 Validating Windsurf config schema purity (constitutional §26)")
    violations: list[str] = []
    _validate_hooks(violations)
    _validate_mcp(violations)

    if violations:
        print(f"❌ Windsurf config schema violations ({len(violations)} issue(s)):")
        for v in violations:
            print(v)
        print(
            "\nWhy this matters: Windsurf's config parser silently rejects "
            "entries with unknown fields. The hook or MCP server goes dark "
            "with no error surfaced. See constitutional §26 and the "
            "2026-04-23 post_cascade hook-chain failure RCA."
        )
        return 1

    print("✅ Windsurf config schema purity validated (hooks.json + mcp_config.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
