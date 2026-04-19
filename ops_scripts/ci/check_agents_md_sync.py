#!/usr/bin/env python3
"""Fail-closed AGENTS.md autogen-block integrity gate (T6d).

Regenerates each autogen block from its SSOT source and compares byte-for-byte
against the current content in AGENTS.md. Any drift fails the check.

Blocks validated:
  - MCP-QUICK-REFERENCE  (SSOT: .windsurf/mcp_config.json + server_rows)
  - NOTION-MAP           (SSOT: config/notion_databases.yaml)

Complements:
  - check_mcp_sync_integrity.py  (section-level MCP table drift)
  - check_agents_mcp_coverage.py (every server in config has a row)

Usage:
  python ops_scripts/ci/check_agents_md_sync.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC_SCRIPT_DIR = REPO_ROOT / ".windsurf" / "scripts"
if str(SYNC_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SYNC_SCRIPT_DIR))

from sync_mcp_config import (  # noqa: E402
    AGENTS_MD,
    generate_mcp_quick_reference_block,
    generate_notion_map_block,
)


def _extract_block(text: str, marker: str) -> tuple[str | None, str]:
    """Return (inner_content, status_msg) for the named autogen block.

    inner_content is None when markers are missing or malformed. status_msg
    describes the failure for reporting.
    """
    start_tag = f"<!-- {marker}:START -->"
    end_tag = f"<!-- {marker}:END -->"
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    if start_idx == -1 and end_idx == -1:
        return None, f"autogen markers for '{marker}' are missing"
    if start_idx == -1 or end_idx == -1:
        return None, f"autogen markers for '{marker}' are malformed (only one tag present)"
    if end_idx < start_idx:
        return None, f"autogen markers for '{marker}' are out of order"
    inner = text[start_idx + len(start_tag) : end_idx]
    return inner, ""


def _normalise(s: str) -> str:
    """Trim surrounding blank lines so whitespace-only differences don't trip the gate."""
    return s.strip("\n")


def _check_block(text: str, marker: str, generator) -> list[str]:
    issues: list[str] = []
    current, status = _extract_block(text, marker)
    if current is None:
        issues.append(
            f"AGENTS.md: {status}; add the markers and run 'python .windsurf/scripts/sync_mcp_config.py'"
        )
        return issues
    try:
        expected = generator()
    except FileNotFoundError as exc:
        issues.append(f"AGENTS.md: '{marker}' generator failed: {exc}")
        return issues
    if _normalise(current) != _normalise(expected):
        issues.append(
            f"AGENTS.md: '{marker}' autogen block drifted from SSOT; run "
            "'python .windsurf/scripts/sync_mcp_config.py' to regenerate"
        )
    return issues


def main() -> int:
    if not AGENTS_MD.exists():
        print(f"[agents_md_sync] FAIL: AGENTS.md not found at {AGENTS_MD}", flush=True)
        return 1

    text = AGENTS_MD.read_text(encoding="utf-8")

    issues: list[str] = []
    issues.extend(_check_block(text, "MCP-QUICK-REFERENCE", generate_mcp_quick_reference_block))
    issues.extend(_check_block(text, "NOTION-MAP", generate_notion_map_block))

    if issues:
        print("[agents_md_sync] FAIL:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        return 1

    print("[agents_md_sync] OK: all AGENTS.md autogen blocks match SSOT.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
