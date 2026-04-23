"""Coverage test: every Python MCP server from mcp_config.json must call
guard_single_instance() at startup.

Rationale
    Orphan MCP server processes from stale Cascade sessions share stdio
    with the active session and trigger the upstream MCP client race
    documented in .windsurf/rules/mcp-serialization.md. The
    ``guard_single_instance()`` helper terminates any sibling process
    before the new one starts serving. Without adoption, orphans survive.

    This test enforces adoption across the fleet. Node-based MCP servers
    (filesystem, notion, task_manager) are third-party npx wrappers and
    are excluded — they cannot be patched here; rely on the Windsurf-level
    orphan killer hook instead.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
MCP_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"

# Third-party / npx-based servers cannot carry an in-process guard.
NODE_EXCLUDED_SERVERS = {
    "filesystem",          # node filesystem_mcp_launcher.js
    "notion",              # npx @notionhq/notion-mcp-server
    "task_manager",        # npx @blizzy/mcp-task-manager
    "deepwiki",            # remote sse — no local process
    "GitKraken",           # external binary
}


def _resolve_python_server_path(args: list[str]) -> Path | None:
    """Return the repo-relative .py path this python invocation runs.

    Handles two patterns:
        1. ['-u', '${env:AGENTIC_REPO_ROOT}/tools/foo/bar.py']
        2. ['-u', '-m', 'tools.foo.bar']
    """
    # Scan for a .py path-like arg first.
    for a in args:
        if isinstance(a, str) and a.endswith(".py"):
            # Strip leading env var + slash then join to repo root.
            rel = re.sub(r"^\$\{env:[^}]+\}[/\\]?", "", a)
            return REPO_ROOT / rel
    # Module-invocation form: -m pkg.mod
    for i, a in enumerate(args):
        if a == "-m" and i + 1 < len(args):
            mod_path = args[i + 1]
            if isinstance(mod_path, str):
                return (REPO_ROOT / mod_path.replace(".", "/")
                        ).with_suffix(".py")
    return None


def _python_mcp_servers() -> list[tuple[str, Path]]:
    data = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    servers: list[tuple[str, Path]] = []
    for name, cfg in data.get("mcpServers", {}).items():
        if name in NODE_EXCLUDED_SERVERS:
            continue
        cmd = (cfg.get("command") or "").lower()
        if cmd not in {"python", "python.exe", "py", "py.exe"}:
            continue
        args = cfg.get("args") or []
        path = _resolve_python_server_path(list(args))
        if path is not None:
            servers.append((name, path))
    return servers


def test_mcp_config_has_python_servers() -> None:
    """Sanity: we found at least one python MCP server to enforce."""
    servers = _python_mcp_servers()
    assert servers, (
        "Parser did not identify any python MCP servers in "
        f"{MCP_CONFIG}; coverage test cannot enforce adoption"
    )


@pytest.mark.parametrize("server_name, server_path", _python_mcp_servers())
def test_python_mcp_server_calls_guard(
    server_name: str, server_path: Path
) -> None:
    """Every python MCP server MUST call guard_single_instance()."""
    assert server_path.exists(), (
        f"MCP config references missing file: {server_path} "
        f"(server {server_name!r})"
    )
    src = server_path.read_text(encoding="utf-8")
    # Tolerate both import forms.
    has_call = bool(
        re.search(r"\bguard_single_instance\s*\(", src)
    )
    assert has_call, (
        f"Python MCP server {server_name!r} ({server_path.name}) does NOT "
        "call guard_single_instance(). Add it in the __main__ block per "
        "tools/mcp/mcp_bootstrap.py. Stale siblings survive window reloads "
        "without it. See 2026-04-23 RCA."
    )


@pytest.mark.parametrize("server_name, server_path", _python_mcp_servers())
def test_python_mcp_server_guard_inside_main_block(
    server_name: str, server_path: Path
) -> None:
    """The guard call must sit inside the __main__ block (not at import)."""
    src = server_path.read_text(encoding="utf-8")
    main_idx = src.find('if __name__ == "__main__":')
    guard_idx = src.find("guard_single_instance(")
    if guard_idx == -1:
        pytest.skip(f"{server_name}: already covered by adoption test")
    assert main_idx != -1, (
        f"{server_name}: no __main__ block found"
    )
    assert guard_idx > main_idx, (
        f"{server_name}: guard_single_instance() must be INSIDE the "
        "__main__ block, not at import time (calling at import can "
        "recursively kill test harnesses that import the module)."
    )
