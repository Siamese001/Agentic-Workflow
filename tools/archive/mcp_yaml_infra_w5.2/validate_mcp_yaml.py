#!/usr/bin/env python3
"""CI gate: Validate MCP YAML configuration.

Validates config/mcp_servers.yaml against schema and checks for issues:
- Schema validation (structure, types, required fields)
- Duplicate tool names across servers
- Orphaned aliases
- Invalid server prefixes
- Missing required fields

Exit codes:
    0 = Valid
    1 = Validation failed

Usage:
    python ops_scripts/ci/validate_mcp_yaml.py
    python ops_scripts/ci/validate_mcp_yaml.py --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

YAML_CONFIG_PATH = REPO_ROOT / "config" / "mcp_servers.yaml"


def validate_yaml_config() -> list[str]:
    """Validate the YAML config and return list of issues."""
    issues: list[str] = []

    # Check file exists
    if not YAML_CONFIG_PATH.exists():
        return [f"YAML config not found: {YAML_CONFIG_PATH}"]

    # Try to import and load
    try:
        from agentic_core.config.mcp_loader import MCPLoader
    except ImportError as e:
        return [f"Cannot import MCPLoader: {e}"]

    # Load and validate
    try:
        loader = MCPLoader(YAML_CONFIG_PATH)
        config = loader.load()
    except FileNotFoundError as e:
        return [f"Config file error: {e}"]
    except ImportError as e:
        return [f"Missing dependency: {e}"]
    except ValueError as e:
        return [f"Config validation error: {e}"]

    # Run validation
    validation_issues = loader.validate()
    issues.extend(validation_issues)

    # Additional checks
    valid_prefixes = {f"mcp{i}" for i in range(20)}  # mcp0 through mcp19

    for server_name, server in config.servers.items():
        # Check prefix format
        if server.prefix not in valid_prefixes:
            issues.append(
                f"Server '{server_name}' has invalid prefix: '{server.prefix}'",
            )

        # Check enabled servers have required fields
        if server.enabled:
            if not server.command:
                issues.append(
                    f"Enabled server '{server_name}' missing 'command' field",
                )

            # Check for tools
            if not server.tools:
                issues.append(
                    f"Enabled server '{server_name}' has no tools defined",
                )

            # Validate tool targets match prefix
            for tool_name, tool in server.tools.items():
                expected_prefix = server.prefix + "_"
                if not tool.target.startswith(expected_prefix):
                    issues.append(
                        f"Tool '{tool_name}' in '{server_name}' has target '{tool.target}' "
                        f"that doesn't match server prefix '{expected_prefix}'",
                    )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate MCP YAML configuration",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output even on success",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors",
    )

    args = parser.parse_args()

    print("[MCP-VALIDATE] Validating config/mcp_servers.yaml...")

    issues = validate_yaml_config()

    if issues:
        print(f"[MCP-VALIDATE] FAILED - {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    if args.verbose:
        print("[MCP-VALIDATE] Configuration is valid")
        # Show summary
        try:
            from agentic_core.config.mcp_loader import MCPLoader
            loader = MCPLoader(YAML_CONFIG_PATH)
            config = loader.load()
            print(f"[MCP-VALIDATE] Servers: {len(config.servers)}")
            print(f"[MCP-VALIDATE] Total tools: {config.total_tools}")
            enabled = sum(1 for s in config.servers.values() if s.enabled)
            print(f"[MCP-VALIDATE] Enabled servers: {enabled}")
        except (FileNotFoundError, ImportError, ValueError):
            pass  # Skip summary on error

    print("[MCP-VALIDATE] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
