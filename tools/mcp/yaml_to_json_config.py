#!/usr/bin/env python3
"""
Convert YAML MCP config to JSON format for Windsurf.

Reads config/mcp_servers.yaml (SSOT), expands ${REPO_ROOT} placeholders,
converts to proper JSON format (no comments), and writes to .windsurf/mcp_config.json.

Usage:
    python tools/mcp/yaml_to_json_config.py
"""

import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

# Determine repo root
if "REPO_ROOT" in os.environ:
    REPO_ROOT = Path(os.environ["REPO_ROOT"])
else:
    REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIG_YAML = Path(__file__).resolve().parents[2] / "config" / "mcp_servers.yaml"
OUTPUT_JSON = Path(__file__).resolve().parents[2] / ".windsurf" / "mcp_config.json"


def expand_placeholders(text: str) -> str:
    """Expand ${REPO_ROOT} placeholders in text."""
    if "${REPO_ROOT}" in text:
        # Convert to forward slashes for YAML compatibility
        repo_root_slashes = str(REPO_ROOT).replace("\\", "/")
        return text.replace("${REPO_ROOT}", repo_root_slashes)
    return text


def main():
    print(f"Converting MCP config with REPO_ROOT={REPO_ROOT}")
    print(f"Reading YAML from: {CONFIG_YAML}")

    if not CONFIG_YAML.exists():
        print(f"ERROR: {CONFIG_YAML} not found")
        sys.exit(1)

    # Read YAML
    yaml_content = CONFIG_YAML.read_text(encoding="utf-8")

    # Debug: print first 500 chars to verify content
    print(f"First 500 chars of YAML:\n{yaml_content[:500]}")

    # Expand placeholders before parsing
    expanded_content = expand_placeholders(yaml_content)

    # Parse YAML to Python dict
    try:
        config_dict = yaml.safe_load(expanded_content)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse YAML: {e}")
        sys.exit(1)

    # Count replacements
    original_count = yaml_content.count("${REPO_ROOT}")
    expanded_count = expanded_content.count("${REPO_ROOT}")

    if original_count == 0:
        print("WARNING: No ${REPO_ROOT} placeholders found in config")
    else:
        print(f"Expanded {original_count - expanded_count} ${REPO_ROOT} placeholders")

    # Write as JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)

    print(f"Wrote JSON config to {OUTPUT_JSON}")
    print(f"Config contains {len(config_dict.get('servers', {}))} MCP servers")


if __name__ == "__main__":
    main()
