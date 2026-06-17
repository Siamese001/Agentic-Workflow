#!/usr/bin/env python3
"""Constitutional §26 — legacy editor config schema purity.

Validates that `.claude/settings.json` and `.mcp.json` contain
only fields published in the official legacy editor schema. Unknown keys (e.g.
`powershell`, `bash`, `shell`, `env_override`, `platform`) silently disable
the hook entry or MCP server — legacy editor's parser rejects the entry with no
error surfaced to the user.

Precedent (2026-04-23):
    A `powershell` field added to 23 hook entries silently disabled the
    entire `post_agent_response` chain across a full legacy editor restart.
    Detected only via heartbeat-log forensics.

Bypass (legacy editor-only / no legacy editor mirror maintenance):
    ``WINDSURF_CONFIG_SCHEMA_BYPASS=1`` — skip validation of
    ``.claude/settings.json`` and ``.mcp.json`` only. CI must
    NOT set this; legacy editor schema is still enforced by
    ``check_cursor_config_schema.py``.

Schema whitelists (per docs/cursor/hooks.md + docs/cursor/mcp.md):

    hooks.json per-entry:    command, working_directory, show_output
    mcp_config.json per srv: command, args, env, disabled

Top-level wrapper keys (`hooks`, `mcpServers`, `_note`, schema version) are
allowed. This gate is deterministic, has no external deps, and exits 1 on
any unrecognized field.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS_PATH = ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
MCP_PATH = ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"

# Schema whitelists — extend ONLY when docs/cursor/*.md is updated upstream.
# Underscore-prefixed keys (e.g. `_note`, `_comment`) are universally allowed
# as an inline-documentation convention; legacy editor's parser tolerates them.
HOOK_ENTRY_FIELDS = {
    "command",
    "working_directory",
    "show_output",
    # Governance metadata (enriched hooks.json — plan plan-update-enforcement-template-fix-e7a3c1).
    # legacy editor tolerates underscore-prefixed keys; these are explicit non-_ fields.
    "hook_id",
    "lifecycle_stage",
    "priority",
    "entrypoint",
    "blocking_mode",
    "bypass_env_var",
    "emits_receipt",
    "owner_rule_ref",
    "replacement_for",
    "consolidation_phase",
    "status",
    "note",
}
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

# Fields that LOOK plausible but are known to silently break legacy editor.
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


def _validate_working_directory(
    working_dir: str,
    path: str,
    violations: list[str],
    entry: dict,
) -> None:
    """Fail when a hooks.json entry carries a hardcoded absolute path that
    does not resolve to the active repo root.

    Why: legacy editor hook runner resolves ``working_directory`` literally. A stale
    clone path (e.g. ``C:\\Git\\Agentic-Workflow`` when the active workspace is
    ``C:\\Git\\Agentic-Workflow-FRESH``) silently misdirects every hook invocation
    to the wrong directory, causing all hook scripts to fail or run against stale
    code with no user-visible error.

    CI-safe design: the repo root is derived from ``ROOT`` (resolved from ``__file__``
    of this gate, which lives at ``<repo>/ops_scripts/ci/``). No hardcoded machine
    path is used. This works on any developer machine and in any CI runner.

    Waiver: if the entry contains a ``_local_only_waiver`` key (underscore-prefix
    = tolerated by legacy editor schema), the working_directory check is skipped for
    that entry. The waiver must be explicitly set and is visible in code review.
    """
    if entry.get("_local_only_waiver"):
        return
    wd_path = Path(working_dir)
    if not wd_path.is_absolute():
        return  # relative paths are fine — legacy editor resolves them against workspace
    try:
        resolved = wd_path.resolve()
        if resolved != ROOT.resolve():
            violations.append(
                f"  ❌ {path}: working_directory '{working_dir}' resolves to "
                f"'{resolved}' but the active repo root is '{ROOT.resolve()}'. "
                f"This silently misdirects the hook. Fix by updating "
                f"working_directory to the active repo path, or add "
                f"'_local_only_waiver': true to the entry with a comment."
            )
    except OSError:
        pass  # Path exists check failure on non-existent paths is non-fatal


def _check_entry(entry: dict, allowed: set[str], path: str, violations: list[str]) -> None:
    for key in entry.keys():
        if key in allowed:
            continue
        if key.startswith("_"):
            # Underscore-prefixed = documentation/metadata convention. Tolerated
            # by legacy editor's parser across both hooks.json and mcp_config.json.
            continue
        if key in KNOWN_POISON_FIELDS:
            violations.append(
                f"  ❌ {path}: forbidden field '{key}' — this silently disables "
                f"the entry in legacy editor. See constitutional §26."
            )
        else:
            violations.append(
                f"  ❌ {path}: unknown field '{key}' — not in documented schema "
                f"{sorted(allowed)}. Remove or verify against docs/cursor/."
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
            entry_path = f"{HOOKS_PATH.name}.hooks.{event_name}[{idx}]"
            _check_entry(
                entry,
                HOOK_ENTRY_FIELDS,
                entry_path,
                violations,
            )
            wd = entry.get("working_directory")
            if isinstance(wd, str):
                _validate_working_directory(wd, entry_path, violations, entry)


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
    if os.environ.get("WINDSURF_CONFIG_SCHEMA_BYPASS", "").strip() in (
        "1",
        "true",
        "yes",
    ):
        print(
            "[windsurf-config-schema] BYPASS — WINDSURF_CONFIG_SCHEMA_BYPASS=1 "
            "(legacy editor hooks/MCP files not validated; legacy editor gate is separate)"
        )
        return 0

    print("🔍 Validating legacy editor config schema purity (constitutional §26)")
    violations: list[str] = []
    _validate_hooks(violations)
    _validate_mcp(violations)

    if violations:
        print(f"❌ legacy editor config schema violations ({len(violations)} issue(s)):")
        for v in violations:
            print(v)
        print(
            "\nWhy this matters: legacy editor's config parser silently rejects "
            "entries with unknown fields. The hook or MCP server goes dark "
            "with no error surfaced. See constitutional §26 and the "
            "2026-04-23 post-agent hook-chain failure RCA."
        )
        return 1

    print("✅ legacy editor config schema purity validated (hooks.json + mcp_config.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
