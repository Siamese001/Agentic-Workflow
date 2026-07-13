#!/usr/bin/env python3
"""Public MCP sync entrypoint with the consolidated Codex skill catalog mapping.

The mature synchronization implementation remains in ``_sync_mcp_config_impl.py``. This adapter
changes only the skill-routing metadata and generated narrative while preserving the tested config,
Notion-map, user-projection, and CLI behavior.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_IMPL_PATH = Path(__file__).with_name("_sync_mcp_config_impl.py")
_SPEC = importlib.util.spec_from_file_location("agentic_workflow_sync_mcp_config_impl", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Unable to load MCP sync implementation: {_IMPL_PATH}")
_IMPL = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _IMPL
_SPEC.loader.exec_module(_IMPL)

_CONSOLIDATED_SERVERS = {
    "GitKraken",
    "context7",
    "deepwiki",
    "filesystem",
    "memory",
    "notion",
    "otel_mcp",
    "playwright",
    "pytest_mcp",
    "redis",
    "task_manager",
    "tavily",
    "vector_db",
}


def _consolidate_server_rows(
    rows: list[tuple[str, str, str, str, str]],
) -> list[tuple[str, str, str, str, str]]:
    """Map server-specific documentation links to the canonical MCP integration skill."""

    return [
        (
            server_id,
            use_for,
            tools,
            notes,
            "mcp-integration" if server_id in _CONSOLIDATED_SERVERS else skill,
        )
        for server_id, use_for, tools, notes, skill in rows
    ]


_IMPL.server_rows = _consolidate_server_rows(_IMPL.server_rows)
_ORIGINAL_GENERATE_AGENTS_QUICK_REFERENCE = _IMPL.generate_agents_quick_reference
_OLD_NARRATIVE = (
    "Per-server `SKILL.md` files under `.codex/skills/<name>/` are **redirect stubs**; "
    "procedural SSOT is [`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) sections §1–§13."
)
_NEW_NARRATIVE = (
    "Server-specific MCP procedures are indexed by "
    "[`mcp-integration`](.codex/skills/mcp-integration/SKILL.md) sections §1–§13. "
    "`adg-sqlite` remains the dedicated structural-analysis skill."
)


def generate_agents_quick_reference() -> str:
    """Render the canonical MCP section without active redirect-skill claims."""

    rendered = _ORIGINAL_GENERATE_AGENTS_QUICK_REFERENCE()
    if _OLD_NARRATIVE not in rendered:
        raise RuntimeError("MCP quick-reference narrative changed; update the consolidation adapter")
    return rendered.replace(_OLD_NARRATIVE, _NEW_NARRATIVE, 1)


_IMPL.generate_agents_quick_reference = generate_agents_quick_reference

# Re-export the implementation's public API so existing imports remain stable. Functions retain the
# implementation module as their globals, where server_rows and the narrative renderer are patched.
for _name in dir(_IMPL):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_IMPL, _name)
server_rows = _IMPL.server_rows
generate_agents_quick_reference = _IMPL.generate_agents_quick_reference


def main() -> int:
    return _IMPL.main()


if __name__ == "__main__":
    raise SystemExit(main())
