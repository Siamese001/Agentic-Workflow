"""Tests for check_mcp_adg_redis_consistency.py — S-08 verification gate."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_repo():
    """Provide a temporary repo structure with mcp_config.json."""
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp)
        windsurf_dir = repo_root / ".windsurf"
        windsurf_dir.mkdir()
        yield repo_root


def test_gate_passes_with_consistent_env_var(temp_repo: Path) -> None:
    """Both servers using ${env:ADG_REDIS_URL} should pass."""
    config = {
        "mcpServers": {
            "adg_sqlite": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "${env:ADG_REDIS_URL}"}
            },
            "memory": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "${env:ADG_REDIS_URL}"}
            }
        }
    }
    config_path = temp_repo / ".windsurf" / "mcp_config.json"
    config_path.write_text(json.dumps(config))

    # Import and run the check
    import sys
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
        from ops_scripts.ci.check_mcp_adg_redis_consistency import main, MCP_CONFIG_PATH

        # Monkey-patch the config path
        import ops_scripts.ci.check_mcp_adg_redis_consistency as check_module
        original_config_path = check_module.MCP_CONFIG_PATH
        check_module.MCP_CONFIG_PATH = config_path

        result = main()
        assert result == 0

        # Restore
        check_module.MCP_CONFIG_PATH = original_config_path
    finally:
        sys.path = original_path


def test_gate_fails_with_hardcoded_adg_sqlite(temp_repo: Path) -> None:
    """adg_sqlite with hardcoded default should fail."""
    config = {
        "mcpServers": {
            "adg_sqlite": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "redis://localhost:6379/0"}
            },
            "memory": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "${env:ADG_REDIS_URL}"}
            }
        }
    }
    config_path = temp_repo / ".windsurf" / "mcp_config.json"
    config_path.write_text(json.dumps(config))

    import sys
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
        from ops_scripts.ci.check_mcp_adg_redis_consistency import main, MCP_CONFIG_PATH
        import ops_scripts.ci.check_mcp_adg_redis_consistency as check_module

        original_config_path = check_module.MCP_CONFIG_PATH
        check_module.MCP_CONFIG_PATH = config_path

        result = main()
        assert result == 1

        check_module.MCP_CONFIG_PATH = original_config_path
    finally:
        sys.path = original_path


def test_gate_fails_with_hardcoded_memory(temp_repo: Path) -> None:
    """memory with hardcoded default should fail."""
    config = {
        "mcpServers": {
            "adg_sqlite": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "${env:ADG_REDIS_URL}"}
            },
            "memory": {
                "command": "python",
                "env": {"ADG_REDIS_URL": "redis://localhost:6379/0"}
            }
        }
    }
    config_path = temp_repo / ".windsurf" / "mcp_config.json"
    config_path.write_text(json.dumps(config))

    import sys
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
        from ops_scripts.ci.check_mcp_adg_redis_consistency import main, MCP_CONFIG_PATH
        import ops_scripts.ci.check_mcp_adg_redis_consistency as check_module

        original_config_path = check_module.MCP_CONFIG_PATH
        check_module.MCP_CONFIG_PATH = config_path

        result = main()
        assert result == 1

        check_module.MCP_CONFIG_PATH = original_config_path
    finally:
        sys.path = original_path


def test_gate_bypass_env_var() -> None:
    """MCP_ADG_REDIS_CONSISTENCY_BYPASS=1 should skip check."""
    os.environ["MCP_ADG_REDIS_CONSISTENCY_BYPASS"] = "1"
    try:
        import sys
        original_path = sys.path.copy()
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
            from ops_scripts.ci.check_mcp_adg_redis_consistency import main
            result = main()
            assert result == 0
        finally:
            sys.path = original_path
    finally:
        del os.environ["MCP_ADG_REDIS_CONSISTENCY_BYPASS"]


def test_gate_error_on_missing_config(temp_repo: Path) -> None:
    """Missing mcp_config.json should return error exit code 2."""
    # Don't create config file
    import sys
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
        from ops_scripts.ci.check_mcp_adg_redis_consistency import main, MCP_CONFIG_PATH
        import ops_scripts.ci.check_mcp_adg_redis_consistency as check_module

        original_config_path = check_module.MCP_CONFIG_PATH
        check_module.MCP_CONFIG_PATH = temp_repo / ".windsurf" / "mcp_config.json"

        result = main()
        assert result == 2

        check_module.MCP_CONFIG_PATH = original_config_path
    finally:
        sys.path = original_path


def test_gate_error_on_missing_servers(temp_repo: Path) -> None:
    """Missing required servers should return error exit code 2."""
    config = {"mcpServers": {}}  # Empty servers
    config_path = temp_repo / ".windsurf" / "mcp_config.json"
    config_path.write_text(json.dumps(config))

    import sys
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
        from ops_scripts.ci.check_mcp_adg_redis_consistency import main, MCP_CONFIG_PATH
        import ops_scripts.ci.check_mcp_adg_redis_consistency as check_module

        original_config_path = check_module.MCP_CONFIG_PATH
        check_module.MCP_CONFIG_PATH = config_path

        result = main()
        assert result == 2

        check_module.MCP_CONFIG_PATH = original_config_path
    finally:
        sys.path = original_path
