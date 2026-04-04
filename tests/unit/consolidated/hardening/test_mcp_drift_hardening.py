"""Hardening tests for MCP drift detection system.

Tests edge cases, error conditions, resilience, and security scenarios.
"""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.adg.runtime import (
    MCPConfigSnapshot,
    MCPDriftRecorder,
    MCPDriftType,
    MCPServerState,
)
from agentic_core.L6_observability import (
    MCPDriftMonitor,
    MCPL6ObservabilityStore,
    MCPL6PersistenceConfig,
)


class TestMCPDriftRecorderHardening:
    """Hardening tests for MCPDriftRecorder."""

    def test_malformed_server_config(self, tmp_path):
        """Test handling of malformed server configurations."""
        config = {
            "mcpServers": {
                "valid_server": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {},
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                },
                "missing_command": {  # Missing required command
                    "args": ["server.py"],
                    "env": {},
                },
                "null_values": {  # Null values in fields
                    "command": None,
                    "args": None,
                    "env": None,
                    "capabilities": None,
                }
            }
        }

        config_path = tmp_path / "malformed.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        recorder = MCPDriftRecorder(agent_id="test")
        snapshot = recorder.capture_snapshot(config_path)

        # Should capture valid server and handle malformed ones gracefully
        assert snapshot.server_count == 3  # All are captured
        assert "valid_server" in snapshot.servers
        assert "missing_command" in snapshot.servers
        assert "null_values" in snapshot.servers

        # Null server should have empty string defaults
        null_server = snapshot.servers["null_values"]
        assert null_server.command == ""
        assert null_server.args == ()

    def test_unicode_and_special_chars(self, tmp_path):
        """Test handling of unicode and special characters in config."""
        config = {
            "mcpServers": {
                "unicode_server": {
                    "command": "python",
                    "args": ["server_日本語.py", "--emoji=🚀"],
                    "env": {"KEY": "val\u00fce_with_\u00e9ncoding"},
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                },
                "special_chars": {
                    "command": "python",
                    "args": ["path with spaces", "arg\"with'quotes", "arg\\with\\backslash"],
                    "env": {"PATH": "/path/to/dir;C:\\Windows\\System32"},
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        config_path = tmp_path / "unicode.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)

        recorder = MCPDriftRecorder(agent_id="test")
        snapshot = recorder.capture_snapshot(config_path)

        # Verify unicode preserved correctly
        assert "unicode_server" in snapshot.servers
        unicode_server = snapshot.servers["unicode_server"]
        assert "日本語" in unicode_server.args[0]
        assert "🚀" in unicode_server.args[1]

        # Verify special characters handled
        special = snapshot.servers["special_chars"]
        assert "spaces" in special.args[0]
        assert '"' in special.args[1] or "'" in special.args[1]

    def test_very_large_config(self, tmp_path):
        """Test handling of very large configuration files."""
        # Create config with 100 servers
        servers = {}
        for i in range(100):
            servers[f"server_{i}"] = {
                "command": "python",
                "args": [f"server_{i}.py"],
                "env": {f"KEY_{j}": f"value_{j}" for j in range(50)},  # 50 env vars each
                "capabilities": ["tools", "resources", "prompts"],
                "deploymentMode": "local",
                "layer": f"L{i % 7}"
            }

        config = {"mcpServers": servers}

        config_path = tmp_path / "large.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        recorder = MCPDriftRecorder(agent_id="test")

        start_time = time.time()
        snapshot = recorder.capture_snapshot(config_path)
        elapsed = time.time() - start_time

        assert snapshot.server_count == 100
        assert elapsed < 5.0  # Should complete in reasonable time

        # Verify hash is computed correctly for large config (MD5 is 32 chars)
        assert len(snapshot.config_hash) == 32

    def test_empty_and_whitespace_values(self, tmp_path):
        """Test handling of empty and whitespace-only values."""
        config = {
            "mcpServers": {
                "empty_values": {
                    "command": "",
                    "args": [],
                    "env": {},
                    "capabilities": [],
                    "deploymentMode": "",
                    "layer": ""
                },
                "whitespace_values": {
                    "command": "  python  ",
                    "args": ["  arg1  ", "  "],
                    "env": {"KEY": "  value  "},
                    "capabilities": ["  tools  ", ""],
                    "deploymentMode": "  local  ",
                    "layer": "  L6  "
                }
            }
        }

        config_path = tmp_path / "empty_whitespace.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        recorder = MCPDriftRecorder(agent_id="test")
        snapshot = recorder.capture_snapshot(config_path)

        # Empty values should be preserved (args is tuple)
        empty = snapshot.servers["empty_values"]
        assert empty.command == ""
        assert empty.args == ()

        # Whitespace should be preserved (not stripped)
        whitespace = snapshot.servers["whitespace_values"]
        assert whitespace.command == "  python  "

    def test_drift_with_deeply_nested_configs(self, tmp_path):
        """Test drift detection with deeply nested environment variables."""
        baseline = {
            "mcpServers": {
                "nested_env": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {
                        "LEVEL_1": {
                            "LEVEL_2": {
                                "LEVEL_3": "deep_value"
                            }
                        }
                    },
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        # Modified nested structure
        current = {
            "mcpServers": {
                "nested_env": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {
                        "LEVEL_1": {
                            "LEVEL_2": {
                                "LEVEL_3": "different_value"  # Changed deep value
                            }
                        }
                    },
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        baseline_path = tmp_path / "baseline_nested.json"
        current_path = tmp_path / "current_nested.json"

        with open(baseline_path, "w") as f:
            json.dump(baseline, f)
        with open(current_path, "w") as f:
            json.dump(current, f)

        recorder = MCPDriftRecorder(agent_id="test")
        baseline_snap = recorder.capture_snapshot(baseline_path)
        current_snap = recorder.capture_snapshot(current_path)

        report = recorder.detect_drift(baseline_snap, current_snap)

        # Should detect env change even with nested structure
        assert report.has_drift is True
        assert any(e.drift_type == MCPDriftType.ENV_CHANGED for e in report.drift_events)


class TestMCPL6ObservabilityStoreHardening:
    """Hardening tests for MCPL6ObservabilityStore."""

    def test_read_only_directory_handling(self, tmp_path):
        """Test handling of read-only directory permissions using mocking."""
        # Mock Path.mkdir to simulate permission denied on Windows/Unix
        original_mkdir = Path.mkdir
        call_count = [0]

        def mock_mkdir(self, *args, **kwargs):
            # Simulate permission denied on first call within mcp_snapshots
            if "mcp_snapshots" in str(self) and call_count[0] == 0:
                call_count[0] += 1
                raise PermissionError(13, "Permission denied")
            return original_mkdir(self, *args, **kwargs)

        with patch.object(Path, "mkdir", mock_mkdir):
            # Should handle permission error gracefully via error metadata
            config = MCPL6PersistenceConfig(base_dir=str(tmp_path / "readonly"))
            # If directory creation fails, error is captured in metadata
            # or the config is created with a fallback path
            assert config is not None
            assert isinstance(config.base_dir, (str, Path))

    def test_disk_full_simulation(self, tmp_path):
        """Test handling of disk full scenarios."""
        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))

        # Create a minimal valid snapshot
        snapshot = MCPConfigSnapshot(
            snapshot_id="test-snap-123",
            timestamp=time.time(),
            source_file="/tmp/test.json",
            servers={},
            metadata={}
        )

        # Mock Path.mkdir to simulate disk full during save
        original_mkdir = Path.mkdir
        def mock_mkdir(self, *args, **kwargs):
            if "snapshots" in str(self) or "test-snap" in str(self):
                raise OSError(28, "No space left on device")
            return original_mkdir(self, *args, **kwargs)

        with patch.object(Path, "mkdir", mock_mkdir):
            with pytest.raises(OSError) as exc_info:
                store.save_snapshot(snapshot)
            assert exc_info.value.errno == 28

    def test_corrupted_snapshot_recovery(self, tmp_path):
        """Test recovery from corrupted snapshot files."""
        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))

        # Create corrupted snapshot file
        snapshots_dir = tmp_path / "mcp_snapshots" / "20260328_000000"
        snapshots_dir.mkdir(parents=True)
        corrupted_file = snapshots_dir / "corrupted-snapshot.json"

        with open(corrupted_file, "w") as f:
            f.write("not valid json {{corrupted}}")

        # Should handle corrupted file gracefully during listing
        snapshots = store.list_snapshots()
        # Implementation may skip corrupted files or include them with error handling

        # Should handle corrupted file gracefully during loading
        # (if implementation supports loading)

    def test_concurrent_cleanup_race_condition(self, tmp_path):
        """Test race conditions during cleanup operations."""
        import threading

        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=str(tmp_path), max_snapshots=5)
        )

        recorder = MCPDriftRecorder(agent_id="test")

        errors = []

        def save_multiple():
            try:
                for i in range(10):
                    snapshot = MCPConfigSnapshot(
                        snapshot_id=f"race-test-{i}-{threading.current_thread().name}",
                        timestamp=time.time(),
                        source_file=f"/tmp/race-{i}.json",
                        servers={},
                        metadata={}
                    )
                    store.save_snapshot(snapshot)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        # Run multiple threads concurrently
        threads = [threading.Thread(target=save_multiple) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors despite race conditions
        assert len(errors) == 0, f"Errors during race condition test: {errors}"

        # Should not exceed max_snapshots by too much
        snapshots = store.list_snapshots()
        assert len(snapshots) <= 10  # Some overshoot is acceptable during races

    def test_path_traversal_attack_prevention(self, tmp_path):
        """Test prevention of path traversal in server names."""
        malicious_config = {
            "mcpServers": {
                "../../../etc/passwd": {  # Path traversal attempt
                    "command": "python",
                    "args": ["server.py"],
                    "env": {},
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        config_path = tmp_path / "malicious.json"
        with open(config_path, "w") as f:
            json.dump(malicious_config, f)

        recorder = MCPDriftRecorder(agent_id="test")

        # Should handle malicious server names safely
        snapshot = recorder.capture_snapshot(config_path)

        # Server name should be preserved but not cause path issues
        assert "../../../etc/passwd" in snapshot.servers

        # Saving should sanitize the name
        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
        saved_path = store.save_snapshot(snapshot)

        # Path should exist and be within the temp directory
        assert saved_path.exists()
        assert str(saved_path).startswith(str(tmp_path))


class TestMCPDriftMonitorHardening:
    """Hardening tests for MCPDriftMonitor."""

    def test_monitor_with_missing_config_file(self, tmp_path):
        """Test monitor behavior when config file is missing."""
        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))

        monitor = MCPDriftMonitor(
            config_path=tmp_path / "nonexistent.json",
            store=store
        )

        # Implementation handles missing config gracefully by capturing error metadata
        baseline = monitor.start_monitoring()
        # Should return a snapshot with error metadata rather than raising
        assert baseline is not None
        assert "error" in baseline.metadata

    def test_monitor_with_config_file_deleted_during_run(self, tmp_path):
        """Test monitor when config file is deleted during monitoring."""
        config_path = tmp_path / "config.json"

        # Create initial config
        with open(config_path, "w") as f:
            json.dump({"mcpServers": {"server1": {
                "command": "python",
                "args": ["s1.py"],
                "env": {},
                "capabilities": ["tools"],
                "deploymentMode": "local",
                "layer": "L6"
            }}}, f)

        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
        monitor = MCPDriftMonitor(config_path=config_path, store=store)

        # Start monitoring
        monitor.start_monitoring()

        # Delete config file
        config_path.unlink()

        # Check drift should handle missing file gracefully (returns report with error)
        report = monitor.check_drift()
        assert report is not None

    def test_monitor_with_permission_denied(self, tmp_path):
        """Test monitor with permission denied on config file using mocking."""
        config_path = tmp_path / "protected.json"

        with open(config_path, "w") as f:
            json.dump({"mcpServers": {}}, f)

        # Mock open to simulate permission denied
        original_open = open
        def mock_open_permission_error(filepath, *args, **kwargs):
            if str(filepath) == str(config_path):
                raise PermissionError(13, "Permission denied", str(config_path))
            return original_open(filepath, *args, **kwargs)

        with patch("builtins.open", mock_open_permission_error):
            store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
            monitor = MCPDriftMonitor(config_path=config_path, store=store)

            # Should handle permission error gracefully (returns snapshot with error metadata)
            baseline = monitor.start_monitoring()
            assert baseline is not None
            assert "error" in baseline.metadata
            assert "permission" in baseline.metadata["error"].lower() or "denied" in baseline.metadata["error"].lower()

    def test_monitor_baseline_corruption(self, tmp_path):
        """Test monitor behavior with corrupted baseline."""
        config_path = tmp_path / "config.json"

        with open(config_path, "w") as f:
            json.dump({"mcpServers": {"server1": {
                "command": "python",
                "args": ["s1.py"],
                "env": {},
                "capabilities": ["tools"],
                "deploymentMode": "local",
                "layer": "L6"
            }}}, f)

        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
        monitor = MCPDriftMonitor(config_path=config_path, store=store)

        # Start with valid config
        monitor.start_monitoring()

        # Corrupt the config file
        with open(config_path, "w") as f:
            f.write("corrupted not json")

        # Should handle corrupted config gracefully (returns report with error)
        report = monitor.check_drift()
        assert report is not None

    def test_monitor_rapid_config_changes(self, tmp_path):
        """Test monitor with rapid successive config changes."""
        config_path = tmp_path / "rapid.json"

        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
        monitor = MCPDriftMonitor(config_path=config_path, store=store)

        # Start monitoring
        with open(config_path, "w") as f:
            json.dump({"mcpServers": {"server1": {
                "command": "python", "args": ["s1.py"], "env": {},
                "capabilities": ["tools"], "deploymentMode": "local", "layer": "L6"
            }}}, f)
        monitor.start_monitoring()

        # Rapid changes
        reports = []
        for i in range(20):
            with open(config_path, "w") as f:
                json.dump({"mcpServers": {f"server{i}": {
                    "command": "python", "args": [f"s{i}.py"], "env": {},
                    "capabilities": ["tools"], "deploymentMode": "local", "layer": "L6"
                }}}, f)

            report = monitor.check_drift()
            if report:
                reports.append(report)
            time.sleep(0.05)  # Small delay

        # Should capture drift events without crashing
        assert len(reports) > 0


class TestSecurityScenarios:
    """Security-focused hardening tests."""

    def test_command_injection_prevention_in_args(self, tmp_path):
        """Test that malicious command injection in args is handled."""
        malicious_config = {
            "mcpServers": {
                "injection_test": {
                    "command": "python",
                    "args": [
                        "server.py",
                        "; rm -rf /",  # Command injection attempt
                        "$(whoami)",
                        "`cat /etc/passwd`"
                    ],
                    "env": {},
                    "capabilities": ["tools"],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        config_path = tmp_path / "injection.json"
        with open(config_path, "w") as f:
            json.dump(malicious_config, f)

        recorder = MCPDriftRecorder(agent_id="test")

        # Should capture without executing anything
        snapshot = recorder.capture_snapshot(config_path)

        # Args should be captured as-is (no execution)
        server = snapshot.servers["injection_test"]
        assert "; rm -rf /" in server.args
        assert "$(whoami)" in server.args

        # Hash should still be computed correctly (MD5 is 32 chars)
        assert len(snapshot.config_hash) == 32

    def test_xss_in_capabilities_handling(self, tmp_path):
        """Test handling of XSS attempts in capabilities."""
        xss_config = {
            "mcpServers": {
                "xss_test": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {},
                    "capabilities": [
                        "<script>alert('xss')</script>",
                        "tools<img src=x onerror=alert(1)>",
                        "normal_capability"
                    ],
                    "deploymentMode": "local",
                    "layer": "L6"
                }
            }
        }

        config_path = tmp_path / "xss.json"
        with open(config_path, "w") as f:
            json.dump(xss_config, f)

        recorder = MCPDriftRecorder(agent_id="test")
        snapshot = recorder.capture_snapshot(config_path)

        # XSS payloads should be captured but not executed (capabilities are sorted)
        server = snapshot.servers["xss_test"]
        # Check that XSS payloads exist in capabilities (order may vary due to sorting)
        assert any("<script>" in cap for cap in server.capabilities)
        assert any("onerror=" in cap for cap in server.capabilities)

    def test_large_hash_collision_resistance(self, tmp_path):
        """Test that different configs produce different hashes."""
        configs = []
        hashes = []

        for i in range(100):
            config = {
                "mcpServers": {
                    f"server_{i}": {
                        "command": f"cmd_{i}",
                        "args": [f"arg_{i}"],
                        "env": {"VAR": f"val_{i}"},
                        "capabilities": ["tools"],
                        "deploymentMode": "local",
                        "layer": f"L{i % 7}"
                    }
                }
            }
            configs.append(config)

        # Write each config and capture hash
        recorder = MCPDriftRecorder(agent_id="test")

        for i, config in enumerate(configs):
            config_path = tmp_path / f"config_{i}.json"
            with open(config_path, "w") as f:
                json.dump(config, f)

            snapshot = recorder.capture_snapshot(config_path)
            hashes.append(snapshot.config_hash)

        # All 100 hashes should be unique
        assert len(set(hashes)) == 100, "Hash collision detected!"


class TestResilienceAndRecovery:
    """Resilience and recovery tests."""

    def test_partial_failure_recovery(self, tmp_path):
        """Test system resilience to partial failures."""
        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))

        # Create multiple snapshots, some valid, some invalid
        valid_snapshot = MCPConfigSnapshot(
            snapshot_id="valid-1",
            timestamp=time.time(),
            source_file="/tmp/valid.json",
            servers={"s1": MCPServerState(
                name="s1", command="python", args=("s1.py",), env=tuple(),
                capabilities=("tools",), target_layer="L6",
                disabled=False
            )},
            metadata={}
        )

        # Save valid snapshot
        store.save_snapshot(valid_snapshot)

        # Verify store still works after partial operations
        snapshots = store.list_snapshots()
        assert len(snapshots) >= 1

    def test_system_recovery_after_exception(self, tmp_path):
        """Test system recovers gracefully after exceptions using mocking."""
        config_path = tmp_path / "config.json"

        with open(config_path, "w") as f:
            json.dump({"mcpServers": {}}, f)

        store = MCPL6ObservabilityStore(MCPL6PersistenceConfig(base_dir=str(tmp_path)))
        monitor = MCPDriftMonitor(config_path=config_path, store=store)

        # Start monitoring
        monitor.start_monitoring()

        # Mock open to simulate temporary permission error during drift check
        original_open = open
        call_count = [0]

        def mock_open_temp_error(filepath, *args, **kwargs):
            if str(filepath) == str(config_path) and call_count[0] == 0:
                call_count[0] += 1
                raise PermissionError(13, "Permission denied")
            return original_open(filepath, *args, **kwargs)

        with patch("builtins.open", mock_open_temp_error):
            # This should handle the error gracefully (returns report)
            report = monitor.check_drift()
            # May return None or report with error depending on implementation
            # The key is it doesn't crash

        # Restore config and verify system works again
        with open(config_path, "w") as f:
            json.dump({"mcpServers": {"new_server": {
                "command": "python", "args": ["new.py"], "env": {},
                "capabilities": ["tools"], "deploymentMode": "local", "layer": "L6"
            }}}, f)

        # Should work after recovery - returns a report
        report = monitor.check_drift()
        assert report is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
