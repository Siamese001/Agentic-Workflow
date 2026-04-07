#!/usr/bin/env python3
"""Sync MCP configuration from YAML SSOT to global Windsurf config.

Reads config/mcp_servers.yaml (the canonical SSOT), expands build-time
variables (${REPO_ROOT}, ${GITKRAKEN_EXE}), converts to the JSON format
Windsurf reads, and writes to the global config path.

Runtime env vars like ${BRAVE_API_KEY} are kept as-is — Windsurf resolves
those from its secrets store at startup.

Usage:
    python tools/adg/sync_yaml_to_global.py           # Sync YAML to global
    python tools/adg/sync_yaml_to_global.py --check   # Check drift (no writes)
    python tools/adg/sync_yaml_to_global.py --dry-run # Show what would change
    python tools/adg/sync_yaml_to_global.py --verify  # Sync then run health check
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
YAML_CONFIG = REPO_ROOT / "config" / "mcp_servers.yaml"
GLOBAL_CONFIG = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
BACKUP_DIR = Path.home() / ".codeium" / "windsurf" / "backups"
ENV_PATH = REPO_ROOT / ".env"


# ---------------------------------------------------------------------------
# Variable expansion
# ---------------------------------------------------------------------------
def _expand_vars(text: str, variables: dict[str, str]) -> str:
    """Expand ${VAR} patterns using the variables dict.

    Only expands variables present in the dict.  Leaves unknown ${VAR}
    patterns (like ${BRAVE_API_KEY}, ${REDIS_HOST:-localhost}) untouched —
    Windsurf resolves those from its secrets store at runtime.
    """
    if not isinstance(text, str) or "${" not in text:
        return text
    for key, value in variables.items():
        text = text.replace(f"${{{key}}}", value)
    return text


def _expand_deep(obj: Any, variables: dict[str, str]) -> Any:
    """Recursively expand variables in strings, lists, dicts."""
    if isinstance(obj, str):
        return _expand_vars(obj, variables)
    if isinstance(obj, list):
        return [_expand_deep(item, variables) for item in obj]
    if isinstance(obj, dict):
        return {k: _expand_deep(v, variables) for k, v in obj.items()}
    return obj


def _load_dotenv(env_path: Path) -> dict[str, str]:
    """Load key=value pairs from a .env file (if it exists)."""
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    except OSError:
        pass
    return env_vars


# ---------------------------------------------------------------------------
# YAML → Windsurf JSON conversion
# ---------------------------------------------------------------------------
def yaml_to_windsurf(config: dict[str, Any]) -> dict[str, Any]:
    """Convert YAML config to Windsurf mcpServers JSON format.

    Rules:
    - Only enabled servers are included.
    - ``windsurf_name`` overrides the YAML key as the JSON server name
      (needed when YAML key differs from what Windsurf expects, e.g.
      brave_search → brave-search, gitkraken → GitKraken).
    - URL-based servers (deepwiki) get a ``url`` field instead of command.
    - All env vars are preserved — unresolved ${VAR} pass through for
      Windsurf to resolve from its secrets store.
    """
    # Build variable substitution table — BUILD-TIME vars only.
    # API keys (BRAVE_API_KEY, FIGMA_API_KEY, etc.) are deliberately NOT expanded
    # so they stay as ${VAR} placeholders for Windsurf to resolve from its secrets.
    repo_root = str(config.get("repo_root", str(REPO_ROOT))).replace("\\", "/")
    defaults = config.get("defaults", {})

    variables: dict[str, str] = {"REPO_ROOT": repo_root}
    # YAML defaults section (e.g., GITKRAKEN_EXE) — env vars override if set
    for key, value in defaults.items():
        variables[key] = os.environ.get(key, str(value))

    servers = config.get("servers", {})
    mcp_servers: dict[str, Any] = {}

    for yaml_key, server_def in servers.items():
        if not isinstance(server_def, dict):
            continue
        if not server_def.get("enabled", True):
            continue

        # Windsurf server name (may differ from YAML key)
        ws_name = server_def.get("windsurf_name", yaml_key)

        entry: dict[str, Any] = {}

        # URL-based servers (e.g., deepwiki)
        if "url" in server_def:
            entry["url"] = _expand_vars(str(server_def["url"]), variables)
            entry["disabled"] = False

        # Command-based servers
        if "command" in server_def:
            entry["command"] = _expand_vars(str(server_def["command"]), variables)
            if "args" in server_def:
                entry["args"] = _expand_deep(list(server_def["args"]), variables)
            entry["disabled"] = False

        # Environment variables — keep ALL, including unresolved ${VAR}
        if "env" in server_def and server_def["env"]:
            resolved_env = {}
            for k, v in server_def["env"].items():
                resolved_env[k] = _expand_vars(str(v), variables)
            entry["env"] = resolved_env

        if not entry:
            continue  # skip servers with neither url nor command

        mcp_servers[ws_name] = entry

    return {"mcpServers": mcp_servers}


# ---------------------------------------------------------------------------
# Global config I/O
# ---------------------------------------------------------------------------
def _load_global() -> dict[str, Any] | None:
    """Load existing global config, or None if absent/corrupt."""
    if not GLOBAL_CONFIG.exists():
        return None
    try:
        return json.loads(GLOBAL_CONFIG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _backup_global() -> Path | None:
    """Create timestamped backup of global config."""
    if not GLOBAL_CONFIG.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"mcp_config_{ts}.json"
    try:
        shutil.copy2(GLOBAL_CONFIG, backup)
        return backup
    except OSError:
        return None


def _configs_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Compare two configs for equality (ignoring formatting)."""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync MCP config from YAML SSOT to global Windsurf config",
    )
    parser.add_argument("--check", action="store_true",
                        help="Check drift without writing (exit 0=synced, 1=drift)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show generated config without writing")
    parser.add_argument("--verify", action="store_true",
                        help="Run health check after sync")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    # --- Load YAML ---
    if not YAML_CONFIG.exists():
        print(f"ERROR: YAML SSOT not found: {YAML_CONFIG}")
        return 1

    with open(YAML_CONFIG, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not config or "servers" not in config:
        print("ERROR: YAML has no 'servers' section")
        return 1

    # --- Convert ---
    new_config = yaml_to_windsurf(config)
    server_count = len(new_config["mcpServers"])

    print(f"YAML SSOT:     {YAML_CONFIG}")
    print(f"Global target: {GLOBAL_CONFIG}")
    print(f"Servers:       {server_count}")

    for name in sorted(new_config["mcpServers"]):
        s = new_config["mcpServers"][name]
        kind = "URL" if "url" in s else s.get("command", "?")
        print(f"  {name:.<30s} {kind}")

    # --- Check mode ---
    old_config = _load_global()

    if args.check:
        if old_config and _configs_equal(old_config, new_config):
            print("\nOK — global config matches YAML SSOT")
            return 0
        print("\nDRIFT — global config differs from YAML SSOT")
        if old_config:
            old_names = set(old_config.get("mcpServers", {}).keys())
            new_names = set(new_config["mcpServers"].keys())
            added = new_names - old_names
            removed = old_names - new_names
            if added:
                print(f"  Would add:    {sorted(added)}")
            if removed:
                print(f"  Would remove: {sorted(removed)}")
        return 1

    # --- Dry-run mode ---
    if args.dry_run:
        print("\n--- Generated config ---")
        print(json.dumps(new_config, indent=2))
        return 0

    # --- Already in sync? ---
    if old_config and _configs_equal(old_config, new_config):
        print("\nOK — already in sync (no changes needed)")
        return 0

    # --- Backup + write ---
    if old_config:
        backup = _backup_global()
        if backup:
            print(f"Backup:        {backup}")

    GLOBAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    GLOBAL_CONFIG.write_text(
        json.dumps(new_config, indent=2) + "\n", encoding="utf-8",
    )
    print(f"\nWrote {server_count} servers to {GLOBAL_CONFIG}")
    print("Restart Windsurf to apply changes.")

    # --- Verify mode ---
    if args.verify:
        health_script = REPO_ROOT / "ops_scripts" / "ci" / "mcp_health_check.py"
        if health_script.exists():
            print("\n--- Health Check ---")
            return subprocess.call([sys.executable, str(health_script), "--fix"])
        print("WARN: Health check script not found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
