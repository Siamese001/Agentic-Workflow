from __future__ import annotations

import sys
import tomllib
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[3] / ".codex" / "governance" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import sync_mcp_config  # noqa: E402


def test_render_codex_user_mcp_block_preserves_http_required_routes() -> None:
    data = {
        "mcpServers": {
            "adg_sqlite": {"url": "http://127.0.0.1:8765/mcp"},
            "memory": {"url": "http://127.0.0.1:8766/mcp"},
        }
    }

    block = sync_mcp_config.render_codex_user_mcp_block(data)

    assert "[mcp_servers.adg_sqlite]" in block
    assert 'url = "http://127.0.0.1:8765/mcp"' in block
    assert "[mcp_servers.memory]" in block
    assert 'url = "http://127.0.0.1:8766/mcp"' in block
    assert block.count("required = true") == 2
    assert "command =" not in block


def test_repo_local_codex_config_uses_http_for_adg_and_memory() -> None:
    config_path = Path(__file__).resolve().parents[3] / ".codex" / "config.toml"
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    servers = data["mcp_servers"]

    expected_urls = {
        "adg_sqlite": "http://127.0.0.1:8765/mcp",
        "memory": "http://127.0.0.1:8766/mcp",
    }
    for server_id, url in expected_urls.items():
        config = servers[server_id]
        assert config["url"] == url
        assert "command" not in config
        assert "args" not in config
        assert "cwd" not in config
