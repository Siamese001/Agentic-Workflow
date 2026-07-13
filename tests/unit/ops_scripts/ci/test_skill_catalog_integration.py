from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _load_module(relative_path: str, name: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mcp_sync_routes_server_docs_to_canonical_skills() -> None:
    module = _load_module(
        ".codex/governance/scripts/sync_mcp_config.py",
        "test_sync_mcp_config",
    )
    mapping = {server_id: skill for server_id, _use, _tools, _notes, skill in module.server_rows}
    assert mapping["adg_sqlite"] == "adg-sqlite"
    for server_id, skill in mapping.items():
        if server_id != "adg_sqlite":
            assert skill == "mcp-integration"
    rendered = module.generate_agents_quick_reference()
    assert "redirect stubs" not in rendered
    assert "mcp-integration" in rendered


def test_superseded_redirect_skill_directories_are_absent() -> None:
    skills_root = REPO_ROOT / ".codex" / "skills"
    superseded = {
        "context7",
        "deepwiki",
        "gitkraken",
        "ledger-consulter",
        "memory-mcp",
        "otel-telemetry",
        "playwright",
        "pytest-mcp",
        "redis-cache",
        "tavily-research",
        "vector-db",
    }
    assert not [name for name in sorted(superseded) if (skills_root / name).exists()]
