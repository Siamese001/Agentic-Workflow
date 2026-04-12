#!/usr/bin/env python3
"""Tests for post_write_mcp_config_sync.py hook."""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Import the module under test
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".windsurf" / "scripts"))
from post_write_mcp_config_sync import _validate_ssot, main


class TestPostWriteMcpConfigSync(unittest.TestCase):
    """Validate MCP config sync hook behavior."""

    def setUp(self):
        """Set up temporary fixtures."""
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.ssot = self.tmp_dir / "mcp_config.json"
        self.global_cfg = self.tmp_dir / "global" / "mcp_config.json"

    def tearDown(self):
        """Clean up temporary fixtures."""
        import shutil

        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_validate_ssot_happy_path(self):
        """Happy path: valid config with _note and proper servers."""
        valid_config = {
            "_note": "VERSION-CONTROLLED REFERENCE ONLY",
            "mcpServers": {
                "test-server": {"command": "python", "args": ["-m", "test"], "env": {"TEST_VAR": "value"}}
            },
        }
        self.ssot.write_text(json.dumps(valid_config), encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertEqual([], issues)

    def test_validate_ssot_missing_mcp_servers(self):
        """Failure path: missing top-level mcpServers key."""
        invalid_config = {"_note": "test"}
        self.ssot.write_text(json.dumps(invalid_config), encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertIn("Missing top-level 'mcpServers' key", issues)

    def test_validate_ssot_server_without_command_or_url(self):
        """Failure path: server has neither command nor url."""
        invalid_config = {"mcpServers": {"bad-server": {}}}
        self.ssot.write_text(json.dumps(invalid_config), encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertIn("Server 'bad-server' has neither 'command' nor 'url'", issues)

    def test_validate_ssot_hardcoded_secret_detected(self):
        """Failure path: hardcoded secret in env (non-localhost)."""
        invalid_config = {
            "mcpServers": {"secret-server": {"command": "python", "env": {"API_KEY": "sk-1234567890abcdef"}}}
        }
        self.ssot.write_text(json.dumps(invalid_config), encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertTrue(any("hardcoded secret" in issue for issue in issues))

    def test_validate_ssot_localhost_value_not_flagged(self):
        """Edge case: env value containing 'localhost' is NOT flagged as a hardcoded secret."""
        valid_config = {
            "mcpServers": {
                "local-server": {"command": "python", "env": {"API_KEY": "http://localhost:8080/key"}}
            }
        }
        self.ssot.write_text(json.dumps(valid_config), encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertEqual([], issues, "localhost value should not be flagged as hardcoded secret")

    def test_validate_ssot_json_parse_error(self):
        """Failure path: malformed JSON."""
        self.ssot.write_text("{invalid json", encoding="utf-8")
        issues = _validate_ssot(self.ssot)
        self.assertTrue(any("JSON parse error" in issue for issue in issues))

    @patch("post_write_mcp_config_sync.GLOBAL")
    @patch("post_write_mcp_config_sync.SSOT")
    def test_main_sync_success(self, mock_ssot, _mock_global):
        """Happy path: successful sync to global config."""
        mock_ssot.exists.return_value = True
        mock_ssot.read_text.return_value = json.dumps({"mcpServers": {"test": {"command": "python"}}})
        _mock_global.parent.mkdir.return_value = None

        result = main()
        self.assertEqual(0, result)

    @patch("post_write_mcp_config_sync.SSOT")
    def test_main_ssot_not_found(self, mock_ssot):
        """Edge case: SSOT file missing should not fail."""
        mock_ssot.exists.return_value = False
        result = main()
        self.assertEqual(0, result)  # advisory only

    @patch("post_write_mcp_config_sync.GLOBAL")
    @patch("post_write_mcp_config_sync.SSOT")
    def test_main_validation_failure(self, mock_ssot, mock_global):
        """Failure path: validation failures prevent sync."""
        mock_ssot.exists.return_value = True
        mock_ssot.read_text.return_value = json.dumps({"invalid": "config"})

        result = main()
        self.assertEqual(0, result)  # advisory only, never blocks

    def test_main_argv_non_mcp_path_skips(self):
        """Filter: non-mcp_config.json argv path causes immediate 0 return without touching SSOT."""
        with patch("sys.argv", ["post_write_mcp_config_sync.py", "/some/other/file.py"]):
            with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                mock_ssot.exists.return_value = True
                result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_not_called()

    def test_main_argv_mcp_config_path_proceeds(self):
        """Filter: mcp_config.json in argv proceeds to sync (SSOT checked)."""
        with patch("sys.argv", ["post_write_mcp_config_sync.py", "/repo/.windsurf/mcp_config.json"]):
            with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                mock_ssot.exists.return_value = False
                result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_called_once()

    def test_main_argv_windows_backslash_path_proceeds(self):
        """Filter: Windows backslash path ending in mcp_config.json is accepted."""
        with patch("sys.argv", ["post_write_mcp_config_sync.py", r"C:\repo\.windsurf\mcp_config.json"]):
            with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                mock_ssot.exists.return_value = False
                result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_called_once()

    def test_main_stdin_non_mcp_payload_skips(self):
        """Filter: stdin JSON with non-mcp file_path causes immediate 0 return."""
        payload = json.dumps({"file_path": "/some/other.py"})
        with patch("sys.argv", ["post_write_mcp_config_sync.py"]):
            with patch("sys.stdin", io.StringIO(payload)):
                with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                    mock_ssot.exists.return_value = True
                    result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_not_called()

    def test_main_stdin_mcp_config_payload_proceeds(self):
        """Filter: stdin JSON with mcp_config.json file_path proceeds to sync."""
        payload = json.dumps({"file_path": "/repo/.windsurf/mcp_config.json"})
        with patch("sys.argv", ["post_write_mcp_config_sync.py"]):
            with patch("sys.stdin", io.StringIO(payload)):
                with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                    mock_ssot.exists.return_value = False
                    result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_called_once()

    def test_main_stdin_empty_proceeds(self):
        """Edge: empty stdin with no argv falls through to SSOT check."""
        with patch("sys.argv", ["post_write_mcp_config_sync.py"]):
            with patch("sys.stdin", io.StringIO("")):
                with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                    mock_ssot.exists.return_value = False
                    result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_called_once()

    def test_main_stdin_malformed_json_proceeds(self):
        """Edge: malformed stdin JSON falls through to SSOT check (no crash)."""
        with patch("sys.argv", ["post_write_mcp_config_sync.py"]):
            with patch("sys.stdin", io.StringIO("{bad json")):
                with patch("post_write_mcp_config_sync.SSOT") as mock_ssot:
                    mock_ssot.exists.return_value = False
                    result = main()
        self.assertEqual(0, result)
        mock_ssot.exists.assert_called_once()


if __name__ == "__main__":
    unittest.main()
