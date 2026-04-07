#!/usr/bin/env python3
"""Sync MCP configuration from YAML SSOT to global Windsurf config.

This script reads config/mcp_servers.yaml and converts it to the JSON format
expected by Windsurf at the global config path.

Usage:
    python tools/adg/sync_yaml_to_global.py           # Sync YAML to global
    python tools/adg/sync_yaml_to_global.py --check   # Check drift (no writes)
    python tools/adg/sync_yaml_to_global.py --dry-run # Show what would change
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

def load_dotenv(env_path: Path) -> dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
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

def substitute_env_vars(value: str, env_vars: dict[str, str]) -> str:
    """Substitute ${VAR} patterns with values from env_vars."""
    pattern = re.compile(r"\$\{(\w+)\}")
    def replacer(match):
        var_name = match.group(1)
        return env_vars.get(var_name, match.group(0))
    return pattern.sub(replacer, value)

try:
    from agentic_core.config.mcp_loader import MCPLoader
except ImportError as e:
    print(f"[ERROR] Cannot import MCPLoader: {e}")
    print("[INFO] Ensure you're running from the repo root or tools/adg/")
    sys.exit(1)

# Paths
YAML_CONFIG_PATH = REPO_ROOT / "config" / "mcp_servers.yaml"
GLOBAL_CONFIG_PATH = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
BACKUP_DIR = Path.home() / ".codeium" / "windsurf" / "backups"
ENV_PATH = REPO_ROOT / ".env"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def yaml_to_windsurf_json(yaml_config: Any, env_vars: dict[str, str]) -> dict[str, Any]:
    """
    Convert YAML config to Windsurf's expected JSON format.

    This function takes a YAML config and converts it to the JSON format
    expected by Windsurf. It also substitutes environment variables in the
    config.

    Args:
        yaml_config (Any): The YAML config to convert.
        env_vars (dict[str, str]): A dictionary of environment variables to
            substitute in the config.

    Returns:
        dict[str, Any]: The converted JSON config.
    """
    windsurf_config: dict[str, Any] = {"mcpServers": {}}

    for server_name, server in yaml_config.servers.items():
        if not server.enabled:
            continue

        # Windows: bare 'npx' is not executable — must use 'npx.cmd'
        command = substitute_env_vars(server.command or "", env_vars)
        if command == "npx" and sys.platform == "win32":
            command = "npx.cmd"

        # Substitute ${VAR} in args list
        resolved_args = [substitute_env_vars(str(a), env_vars) for a in (server.args or [])]

        server_config: dict[str, Any] = {
            "command": command,
            "args": resolved_args,
        }

        # Add optional fields — substitute ${REPO_ROOT} in cwd
        resolved_cwd = substitute_env_vars(server.cwd or "", env_vars) if server.cwd else None
        # npx.cmd servers without an explicit cwd default to REPO_ROOT so Windows can locate the command
        if resolved_cwd:
            server_config["cwd"] = resolved_cwd
        elif command in ("npx.cmd", "npx"):
            server_config["cwd"] = str(REPO_ROOT)

        if server.env:
            # Substitute ${VAR} patterns and filter unresolved
            substituted_env = {}
            for k, v in server.env.items():
                if v and v.startswith("${") and v.endswith("}"):
                    # Template - try to substitute
                    substituted = substitute_env_vars(v, env_vars)
                    if substituted != v:  # Successfully substituted
                        substituted_env[k] = substituted
                elif v and not v.startswith("${"):
                    # Literal value
                    substituted_env[k] = v
            if substituted_env:
                server_config["env"] = substituted_env

        windsurf_config["mcpServers"][server_name] = server_config

    return windsurf_config


def load_global_config() -> dict[str, Any] | None:
    # Load existing global config if present
    if not GLOBAL_CONFIG_PATH.exists():
        return None

    try:
        with open(GLOBAL_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load global config: {e}")
        return None


def backup_global_config() -> Path | None:
    # Create timestamped backup of global config
    if not GLOBAL_CONFIG_PATH.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"mcp_config_{timestamp}.json"

    try:
        shutil.copy2(GLOBAL_CONFIG_PATH, backup_path)
        logger.info(f"Backed up global config to: {backup_path}")
        return backup_path
    except OSError as e:
        logger.error(f"Failed to create backup: {e}")
        return None


def write_global_config(config: dict[str, Any]) -> bool:
    # Write config to global path
    try:
        GLOBAL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(GLOBAL_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except OSError as e:
        logger.error(f"Failed to write global config: {e}")
        return False


def configs_equal(config1: dict[str, Any], config2: dict[str, Any]) -> bool:
    # Compare two configs for equality (ignoring formatting)
    return json.dumps(config1, sort_keys=True) == json.dumps(config2, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync MCP config from YAML SSOT to global Windsurf config",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check drift without writing (exit 0 = synced, exit 1 = drift)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate YAML exists
    if not YAML_CONFIG_PATH.exists():
        logger.error(f"YAML config not found: {YAML_CONFIG_PATH}")
        logger.error("Create it with: python ops_scripts/ci/extract_mcp_tools_to_yaml.py")
        return 1

    # Load YAML config
    try:
        loader = MCPLoader(YAML_CONFIG_PATH)
        yaml_config = loader.load()
        logger.debug(f"Loaded {len(yaml_config.servers)} servers from YAML")
    except FileNotFoundError as e:
        logger.error(f"YAML config not found: {e}")
        return 1
    except ImportError as e:
        logger.error(f"Missing dependency for YAML loading: {e}")
        return 1
    except ValueError as e:
        logger.error(f"YAML validation error: {e}")
        return 1

    # Load .env file for env var substitution
    env_vars = load_dotenv(ENV_PATH)
    if env_vars:
        logger.debug(f"Loaded {len(env_vars)} env vars from {ENV_PATH}")

    # Always inject REPO_ROOT so ${REPO_ROOT} in cwd/args/command resolves correctly
    env_vars.setdefault("REPO_ROOT", str(REPO_ROOT))

    # Convert to Windsurf format
    new_global_config = yaml_to_windsurf_json(yaml_config, env_vars)
    logger.debug(f"Converted to {len(new_global_config['mcpServers'])} servers for Windsurf")

    # Load existing global config
    old_global_config = load_global_config()

    # Check mode
    if args.check:
        if old_global_config is None:
            logger.info("Global config does not exist (would create)")
            return 1
        if configs_equal(old_global_config, new_global_config):
            logger.info("Global config matches YAML SSOT")
            return 0
        else:
            logger.info("Drift detected: global config differs from YAML SSOT")
            return 1

    # Dry-run mode
    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"YAML source: {YAML_CONFIG_PATH}")
        print(f"Global target: {GLOBAL_CONFIG_PATH}")
        print(f"Servers to sync: {len(new_global_config['mcpServers'])}")
        for name in sorted(new_global_config["mcpServers"].keys()):
            print(f"  - {name}")

        if old_global_config:
            old_servers = set(old_global_config.get("mcpServers", {}).keys())
            new_servers = set(new_global_config["mcpServers"].keys())
            added = new_servers - old_servers
            removed = old_servers - new_servers
            if added:
                print(f"\nServers to ADD: {added}")
            if removed:
                print(f"Servers to REMOVE: {removed}")
        return 0

    # Check if update needed
    if old_global_config and configs_equal(old_global_config, new_global_config):
        logger.info("Global config already matches YAML SSOT (no changes needed)")
        return 0

    # Backup existing
    if old_global_config:
        backup_path = backup_global_config()
        if not backup_path:
            logger.warning("Could not create backup, proceeding anyway")

    # Write new config
    if write_global_config(new_global_config):
        logger.info(f"Synced {len(new_global_config['mcpServers'])} servers to global config")
        logger.info(f"Global config: {GLOBAL_CONFIG_PATH}")
        logger.info("Restart Windsurf to apply changes")
        return 0
    else:
        logger.error("Failed to sync to global config")
        return 1


if __name__ == "__main__":
    sys.exit(main())
