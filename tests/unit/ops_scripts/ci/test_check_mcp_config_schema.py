#!/usr/bin/env python3
"""Tests for check_mcp_config_schema.py — MCP Config Schema Validation Gate."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.check_mcp_config_schema import (
    REQUIRED_SERVERS,
    VALID_SERVER_KEYS,
    VALID_TOP_KEYS,
    check_required_servers,
    check_server_structure,
    check_vector_db_runtime_env,
    check_top_level_keys,
    evaluate,
    load_config,
)


def _valid_vector_db_env() -> dict[str, str]:
    return {
        "VECTOR_DB_DEVICE": "cuda",
        "EMBEDDING_DEVICE": "cuda",
        "VECTOR_DB_ENABLE_MODEL_PREWARM": "1",
        "VECTOR_DB_MODEL_LOAD_TIMEOUT": "75",
    }


def _required_server_configs() -> dict[str, dict[str, Any]]:
    servers = {name: {"command": "test", "args": []} for name in REQUIRED_SERVERS}
    if "vector_db" in servers:
        servers["vector_db"]["env"] = _valid_vector_db_env()
    return servers


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Loading a valid config returns data and no errors."""
        config = {"mcpServers": {"test": {"command": "python", "args": ["-m", "test"]}}}
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        # Patch CONFIG_PATH temporarily
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            data, errors = load_config()
            assert data is not None
            assert len(errors) == 0
            assert data["mcpServers"]["test"]["command"] == "python"
        finally:
            module.CONFIG_PATH = original_path

    def test_load_missing_config(self, tmp_path: Path) -> None:
        """Loading missing config returns None and error."""
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = tmp_path / "nonexistent.json"
        
        try:
            data, errors = load_config()
            assert data is None
            assert len(errors) == 1
            assert errors[0].code == "CONFIG_MISSING"
        finally:
            module.CONFIG_PATH = original_path

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Loading invalid JSON returns None and parse error."""
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text("{invalid json")
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            data, errors = load_config()
            assert data is None
            assert len(errors) == 1
            assert errors[0].code == "JSON_PARSE_ERROR"
        finally:
            module.CONFIG_PATH = original_path


class TestCheckTopLevelKeys:
    """Tests for check_top_level_keys function."""

    def test_valid_top_keys(self) -> None:
        """Valid top-level keys produce no violations."""
        data = {"_note": "test", "mcpServers": {}, "_bootstrap_env": "test"}
        violations = check_top_level_keys(data)
        assert len(violations) == 0

    def test_unknown_top_key(self) -> None:
        """Unknown top-level key produces ERROR violation."""
        data = {"mcpServers": {}, "unknownKey": "value"}
        violations = check_top_level_keys(data)
        assert len(violations) == 1
        assert violations[0].severity == "ERROR"
        assert violations[0].code == "UNKNOWN_TOP_KEY"
        assert "unknownKey" in violations[0].message


class TestCheckRequiredServers:
    """Tests for check_required_servers function."""

    def test_all_required_present(self) -> None:
        """All required servers present produces no violations."""
        servers = {name: {"command": "test", "args": []} for name in REQUIRED_SERVERS}
        violations = check_required_servers(servers)
        assert len(violations) == 0

    def test_missing_required_servers(self) -> None:
        """Missing required servers produces ERROR violations."""
        servers = {"GitKraken": {"command": "test", "args": []}}
        violations = check_required_servers(servers)
        
        missing_count = len(REQUIRED_SERVERS) - 1
        assert len(violations) == missing_count
        
        for v in violations:
            assert v.severity == "ERROR"
            assert v.code == "REQUIRED_SERVER_MISSING"

    def test_partial_required_servers(self) -> None:
        """Partial required servers reports only missing ones."""
        # Include half the required servers
        required_list = list(REQUIRED_SERVERS)
        servers = {
            name: {"command": "test", "args": []} 
            for name in required_list[:len(required_list)//2]
        }
        violations = check_required_servers(servers)
        
        expected_missing = len(REQUIRED_SERVERS) - len(servers)
        assert len(violations) == expected_missing


class TestCheckServerStructure:
    """Tests for check_server_structure function."""

    def test_valid_local_server(self) -> None:
        """Valid local server config produces no violations."""
        config = {"command": "python", "args": ["-m", "test"]}
        violations = check_server_structure("test_server", config)
        assert len(violations) == 0

    def test_valid_remote_server(self) -> None:
        """Valid remote server (url-based) produces no violations."""
        config = {"url": "https://example.com/mcp"}
        violations = check_server_structure("remote_server", config)
        assert len(violations) == 0

    def test_missing_command(self) -> None:
        """Local server without command produces ERROR."""
        config = {"args": ["-m", "test"]}
        violations = check_server_structure("test", config)
        assert any(v.code == "MISSING_COMMAND" for v in violations)

    def test_missing_args(self) -> None:
        """Server without args produces ERROR."""
        config = {"command": "python"}
        violations = check_server_structure("test", config)
        assert any(v.code == "MISSING_ARGS" for v in violations)

    def test_invalid_args_type(self) -> None:
        """Non-array args produces ERROR."""
        config = {"command": "python", "args": "not-an-array"}
        violations = check_server_structure("test", config)
        assert any(v.code == "INVALID_ARGS_TYPE" for v in violations)

    def test_invalid_disabled_type(self) -> None:
        """Non-boolean disabled produces ERROR."""
        config = {"command": "python", "args": [], "disabled": "yes"}
        violations = check_server_structure("test", config)
        assert any(v.code == "INVALID_DISABLED_TYPE" for v in violations)

    def test_invalid_env_type(self) -> None:
        """Non-object env produces ERROR."""
        config = {"command": "python", "args": [], "env": "not-an-object"}
        violations = check_server_structure("test", config)
        assert any(v.code == "INVALID_ENV_TYPE" for v in violations)

    def test_required_server_disabled_warning(self) -> None:
        """Disabled required server produces WARNING."""
        config = {"command": "python", "args": [], "disabled": True}
        violations = check_server_structure("adg_sqlite", config)  # Required server
        assert any(v.code == "REQUIRED_SERVER_DISABLED" for v in violations)

    def test_unknown_server_key_warning(self) -> None:
        """Unknown server key produces WARNING."""
        config = {"command": "python", "args": [], "unknown_field": "value"}
        violations = check_server_structure("test", config)
        assert any(v.code == "UNKNOWN_SERVER_KEY" for v in violations)

    def test_invalid_server_config_type(self) -> None:
        """Non-dict server config produces ERROR."""
        violations = check_server_structure("test", "not-a-dict")
        assert any(v.code == "INVALID_SERVER_CONFIG" for v in violations)

    def test_invalid_remote_url(self) -> None:
        """Invalid remote URL produces ERROR."""
        config = {"url": "not-a-valid-url"}
        violations = check_server_structure("remote", config)
        assert any(v.code == "INVALID_REMOTE_URL" for v in violations)

    def test_vector_db_runtime_env_valid(self) -> None:
        """vector_db must accept the CUDA/prewarm runtime envelope."""
        violations = check_server_structure(
            "vector_db",
            {"command": "python", "args": ["tools/mcp/vector_db_server.py"], "env": _valid_vector_db_env()},
        )
        assert violations == []

    def test_vector_db_runtime_env_requires_cuda_prewarm_and_bounded_timeout(self) -> None:
        """vector_db must fail config validation without the incident-preventing env."""
        violations = check_vector_db_runtime_env(
            {
                "VECTOR_DB_DEVICE": "cpu",
                "EMBEDDING_DEVICE": "cpu",
                "VECTOR_DB_ENABLE_MODEL_PREWARM": "0",
                "VECTOR_DB_MODEL_LOAD_TIMEOUT": "120",
            },
            ".mcpServers.vector_db",
        )
        codes = {v.code for v in violations}

        assert "VECTOR_DB_RUNTIME_ENV_MISSING" in codes
        assert "VECTOR_DB_MODEL_LOAD_TIMEOUT_UNBOUNDED" in codes


class TestEvaluate:
    """Tests for evaluate function."""

    def test_valid_config_report(self, tmp_path: Path) -> None:
        """Valid config produces valid report."""
        config: dict[str, Any] = {
            "_note": "test",
            "mcpServers": _required_server_configs(),
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            report = evaluate()
            assert report["valid"] is True
            assert len(report["errors"]) == 0
            assert report["server_count"] == len(REQUIRED_SERVERS)
            assert len(report["required_present"]) == len(REQUIRED_SERVERS)
        finally:
            module.CONFIG_PATH = original_path

    def test_invalid_config_report(self, tmp_path: Path) -> None:
        """Invalid config produces invalid report with errors."""
        config = {
            "mcpServers": {},  # Missing all required servers
            "extra_field": "value",  # Unknown top-level key
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            report = evaluate()
            assert report["valid"] is False
            assert len(report["errors"]) > 0
            assert len(report["required_missing"]) == len(REQUIRED_SERVERS)
        finally:
            module.CONFIG_PATH = original_path


class TestConstants:
    """Tests for module constants."""

    def test_required_servers_not_empty(self) -> None:
        """REQUIRED_SERVERS should not be empty."""
        assert len(REQUIRED_SERVERS) > 0

    def test_valid_server_keys_comprehensive(self) -> None:
        """VALID_SERVER_KEYS should cover common keys."""
        essential_keys = {"command", "args", "env", "disabled", "url"}
        assert essential_keys.issubset(VALID_SERVER_KEYS)

    def test_valid_top_keys_comprehensive(self) -> None:
        """VALID_TOP_KEYS should cover documented keys."""
        essential_keys = {"_note", "mcpServers", "_bootstrap_env"}
        assert essential_keys.issubset(VALID_TOP_KEYS)


class TestIntegration:
    """Integration tests simulating real gate execution."""

    def test_main_valid_config_exit_0(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Main function exits 0 on valid config."""
        config: dict[str, Any] = {
            "mcpServers": _required_server_configs(),
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        monkeypatch.setattr(module, "profile_config_path", lambda _profile, _mirror_path: config_file)
        
        try:
            result = module.main([])
            assert result == 0
        finally:
            module.CONFIG_PATH = original_path

    def test_main_fail_closed_exit_1(self, tmp_path: Path) -> None:
        """Main function exits 1 in fail-closed mode with errors."""
        config = {"mcpServers": {}}  # Missing all required servers
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            result = module.main(["--fail-closed"])
            assert result == 1
        finally:
            module.CONFIG_PATH = original_path

    def test_bypass_env_var(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """BYPASS env var causes exit 0 even with invalid config."""
        monkeypatch.setenv("MCP_CONFIG_SCHEMA_BYPASS", "1")
        
        import ops_scripts.ci.check_mcp_config_schema as module
        # Reload to pick up env var
        import importlib
        importlib.reload(module)
        
        result = module.main([])
        assert result == 0


class TestEdgeCases:
    """W4.2: Edge case test coverage expansion."""

    def test_env_var_interpolation_in_args(self, tmp_path: Path) -> None:
        """Config with ${env:VAR} syntax should be accepted."""
        # Include all required servers plus test server with env interpolation
        config: dict[str, Any] = {"mcpServers": _required_server_configs()}
        # Add test server with env var syntax in args
        config["mcpServers"]["test_env"] = {
            "command": "${env:TEST_CMD}",
            "args": ["-u", "${env:TEST_ARG}"],
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            report = evaluate()
            assert report["valid"] is True
        finally:
            module.CONFIG_PATH = original_path

    def test_empty_args_array(self, tmp_path: Path) -> None:
        """Empty args array should be valid."""
        config: dict[str, Any] = {"mcpServers": _required_server_configs()}
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            report = evaluate()
            assert report["valid"] is True
        finally:
            module.CONFIG_PATH = original_path

    def test_unicode_in_note_field(self, tmp_path: Path) -> None:
        """Unicode characters in _note should be handled."""
        config: dict[str, Any] = {
            "_note": "Test with unicode: 🚀 émojis 中文",
            "mcpServers": _required_server_configs(),
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config, ensure_ascii=False))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            report = evaluate()
            assert report["valid"] is True
        finally:
            module.CONFIG_PATH = original_path

    def test_fail_closed_env_var(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """MCP_CONFIG_SCHEMA_FAIL_CLOSED=1 env var activates fail-closed."""
        monkeypatch.setenv("MCP_CONFIG_SCHEMA_FAIL_CLOSED", "1")
        
        config = {"mcpServers": {}}  # Invalid - missing required
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        import importlib
        importlib.reload(module)
        
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        
        try:
            result = module.main([])  # No --fail-closed flag, but env var set
            assert result == 1
        finally:
            module.CONFIG_PATH = original_path

    def test_json_output_mode(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """--json flag outputs valid JSON."""
        config: dict[str, Any] = {
            "mcpServers": _required_server_configs(),
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))
        
        import ops_scripts.ci.check_mcp_config_schema as module
        original_path = module.CONFIG_PATH
        module.CONFIG_PATH = config_file
        monkeypatch.setattr(module, "profile_config_path", lambda _profile, _mirror_path: config_file)
        
        try:
            result = module.main(["--json"])
            captured = capsys.readouterr()
            assert result == 0
            # Verify output is valid JSON
            output_json = json.loads(captured.out)
            assert "valid" in output_json
            assert output_json["valid"] is True
        finally:
            module.CONFIG_PATH = original_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
