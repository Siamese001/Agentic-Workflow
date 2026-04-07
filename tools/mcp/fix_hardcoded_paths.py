#!/usr/bin/env python3
"""Replace hardcoded C:\Git\Agentic-Workflow paths with ${REPO_ROOT} placeholder."""

from pathlib import Path

YAML_FILE = Path(__file__).resolve().parents[2] / "config" / "mcp_servers.yaml"

content = YAML_FILE.read_text(encoding="utf-8")
content = content.replace(r"C:\Git\Agentic-Workflow", "${REPO_ROOT}")
YAML_FILE.write_text(content, encoding="utf-8")
print("Replaced hardcoded paths with ${REPO_ROOT} placeholder")
