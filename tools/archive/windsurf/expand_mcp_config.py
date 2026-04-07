#!/usr/bin/env python3
"""
Expand ${REPO_ROOT} environment variable in mcp_servers.yaml.

Reads config/mcp_servers.yaml, expands ${REPO_ROOT} placeholders,
and writes resolved config to .windsurf/mcp_config.json for Windsurf.

Usage:
    python tools/mcp/expand_mcp_config.py

Environment variables:
    REPO_ROOT: Repository root path (defaults to git root if not set)
"""

import os
import sys
from pathlib import Path

# Determine repo root
if "REPO_ROOT" in os.environ:
    REPO_ROOT = Path(os.environ["REPO_ROOT"])
else:
    # Default to git root
    REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIG_YAML = Path(__file__).resolve().parents[2] / "config" / "mcp_servers.yaml"
OUTPUT_JSON = Path(__file__).resolve().parents[2] / ".windsurf" / "mcp_config.json"


def expand_placeholders(text: str) -> str:
    """Expand ${REPO_ROOT} placeholders in text."""
    if "${REPO_ROOT}" in text:
        return text.replace("${REPO_ROOT}", str(REPO_ROOT))
    return text


def main():
    print(f"Expanding MCP config with REPO_ROOT={REPO_ROOT}")

    if not CONFIG_YAML.exists():
        print(f"ERROR: {CONFIG_YAML} not found")
        sys.exit(1)

    # Read YAML
    yaml_content = CONFIG_YAML.read_text(encoding="utf-8")

    # Expand placeholders
    expanded_content = expand_placeholders(yaml_content)

    # Count replacements
    original_count = yaml_content.count("${REPO_ROOT}")
    expanded_count = expanded_content.count("${REPO_ROOT}")

    if original_count == 0:
        print("WARNING: No ${REPO_ROOT} placeholders found in config")
    else:
        print(f"Expanded {original_count - expanded_count} ${REPO_ROOT} placeholders")

    # Write output
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(expanded_content, encoding="utf-8")
    print(f"Wrote resolved config to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
