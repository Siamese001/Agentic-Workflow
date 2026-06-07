"""
Tests for check_mcp_gate_sync.py — MCP gate constant ↔ mcp_config.json sync gate.

Covers:
  - All current config keys are either gated or in FAIL_OPEN_SERVERS (no ungated servers)
  - All gate constants match actual config keys (no dead gates)
  - Adding a new config key without a gate constant is detected
  - Adding a gate constant without a config key is detected
  - FAIL_OPEN_SERVERS entries are correctly excluded from gating requirement
  - The gate passes cleanly against the real live config and gate file
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from ops_scripts.ci.check_mcp_gate_sync import (
    FAIL_OPEN_SERVERS,
    _load_config_keys,
    _load_gate_constants,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
MCP_CONFIG_PATH = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
GATE_PATH = REPO_ROOT / "ops_scripts" / "hooks" / "windsurf" / "pre_mcp_gate.py"


# ---------------------------------------------------------------------------
# Live integration: gate passes against real files right now
# ---------------------------------------------------------------------------


class TestLiveSync:
    """End-to-end: real mcp_config.json ↔ real pre_mcp_gate.py must be in sync."""

    def test_no_dead_gates(self):
        config_keys = _load_config_keys()
        gate_constants = _load_gate_constants()
        dead = gate_constants - config_keys
        assert not dead, (
            f"Dead gate constants (in pre_mcp_gate.py but not in mcp_config.json): {dead}\n"
            "Fix: remove the stale *_SERVER_NAME constant or restore the config key."
        )

    def test_no_ungated_servers(self):
        config_keys = _load_config_keys()
        gate_constants = _load_gate_constants()
        must_be_gated = config_keys - FAIL_OPEN_SERVERS
        ungated = must_be_gated - gate_constants
        assert not ungated, (
            f"Ungated servers (in mcp_config.json, not in FAIL_OPEN_SERVERS, no gate constant): {ungated}\n"
            "Fix: add a *_SERVER_NAME constant + gate function, or add to FAIL_OPEN_SERVERS with justification."
        )

    def test_main_exits_zero(self):
        assert main() == 0

    def test_fail_open_servers_not_in_gate_constants(self):
        """GitKraken and enhanced_http must NOT have gate constants — they're explicitly fail-open."""
        gate_constants = _load_gate_constants()
        accidentally_gated = FAIL_OPEN_SERVERS & gate_constants
        assert not accidentally_gated, (
            f"Fail-open servers accidentally have gate constants: {accidentally_gated}\n"
            "Remove the *_SERVER_NAME constant or remove from FAIL_OPEN_SERVERS."
        )

    def test_config_keys_loaded(self):
        keys = _load_config_keys()
        assert len(keys) >= 9, f"Expected at least 9 MCP servers in config, got {len(keys)}: {keys}"
        assert "adg_sqlite" in keys
        assert "redis" in keys
        assert "filesystem" in keys

    def test_gate_constants_loaded(self):
        constants = _load_gate_constants()
        assert "adg_sqlite" in constants
        assert "redis" in constants
        assert "filesystem" in constants
        assert "memory" in constants
        assert "pytest_mcp" in constants
        assert "task_manager" in constants
        assert "vector_db" in constants
        assert "otel_mcp" in constants
        assert "deepwiki" in constants


# ---------------------------------------------------------------------------
# Synthetic: detect specific regression scenarios using tmp files
# ---------------------------------------------------------------------------


class TestSyntheticRegression:
    """Simulate the exact failure modes that caused regressions in prior sessions."""

    def _run_with_files(self, config_text: str, gate_text: str, tmp_path: Path) -> int:
        config_file = tmp_path / "mcp_config.json"
        gate_file = tmp_path / "pre_mcp_gate.py"
        config_file.write_text(config_text, encoding="utf-8")
        gate_file.write_text(gate_text, encoding="utf-8")

        import ops_scripts.ci.check_mcp_gate_sync as _module

        with (
            patch.object(_module, "MCP_CONFIG_PATH", config_file),
            patch.object(_module, "GATE_PATH", gate_file),
        ):
            return _module.main()

    def test_matching_config_and_gate_passes(self, tmp_path):
        config = json.dumps(
            {"mcpServers": {"adg_sqlite": {}, "redis": {}, "GitKraken": {}, "enhanced_http": {}}}
        )
        gate = dedent("""\
            ADG_SERVER_NAME = "adg_sqlite"
            REDIS_SERVER_NAME = "redis"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 0

    def test_new_config_server_without_gate_fails(self, tmp_path):
        """Regression: adding 'new_mcp' to config without a gate constant → UNGATED_SERVER."""
        config = json.dumps(
            {
                "mcpServers": {
                    "adg_sqlite": {},
                    "redis": {},
                    "new_mcp": {},
                    "GitKraken": {},
                    "enhanced_http": {},
                }
            }
        )
        gate = dedent("""\
            ADG_SERVER_NAME = "adg_sqlite"
            REDIS_SERVER_NAME = "redis"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 1

    def test_renamed_gate_constant_without_config_update_fails(self, tmp_path):
        """Regression: renaming redis_mcp → redis in gate but forgetting config → DEAD_GATE."""
        config = json.dumps(
            {"mcpServers": {"adg_sqlite": {}, "redis": {}, "GitKraken": {}, "enhanced_http": {}}}
        )
        gate = dedent("""\
            ADG_SERVER_NAME = "adg_sqlite"
            REDIS_SERVER_NAME = "redis_mcp"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 1

    def test_inline_comment_on_server_name_line_handled(self, tmp_path):
        """Inline # comments on SERVER_NAME lines must not corrupt the parsed value."""
        config = json.dumps({"mcpServers": {"redis": {}, "GitKraken": {}, "enhanced_http": {}}})
        gate = dedent("""\
            REDIS_SERVER_NAME = "redis"          # mcp_config.json key is "redis", not "redis_mcp"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 0

    def test_fail_open_server_excluded_from_ungated_check(self, tmp_path):
        """GitKraken and enhanced_http in config but NOT in gate constants → must pass."""
        config = json.dumps({"mcpServers": {"adg_sqlite": {}, "GitKraken": {}, "enhanced_http": {}}})
        gate = dedent("""\
            ADG_SERVER_NAME = "adg_sqlite"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 0

    def test_empty_config_with_no_gated_servers_passes(self, tmp_path):
        """Only fail-open servers in config → no gate constants needed → pass."""
        config = json.dumps({"mcpServers": {"GitKraken": {}, "enhanced_http": {}}})
        gate = ""
        assert self._run_with_files(config, gate, tmp_path) == 0

    def test_extra_gate_constant_not_in_config_fails(self, tmp_path):
        """Gate constant for a server removed from config → DEAD_GATE."""
        config = json.dumps({"mcpServers": {"adg_sqlite": {}, "GitKraken": {}, "enhanced_http": {}}})
        gate = dedent("""\
            ADG_SERVER_NAME = "adg_sqlite"
            STALE_SERVER_NAME = "removed_mcp"
        """)
        assert self._run_with_files(config, gate, tmp_path) == 1
