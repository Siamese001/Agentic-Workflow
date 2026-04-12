"""Test TestDiscoveryService functionality."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTestDiscoveryService:
    """Test TestDiscoveryService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        config = {"max_tests": 1000}
        service = TestDiscoveryService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        assert service.config == {}
        assert service._discovered_tests == []

    @patch("apps_eval.services.test_discovery_service.emit_replay_key")
    @patch("apps_eval.services.test_discovery_service.emit_determinism_digest")
    @patch("apps_eval.services.test_discovery_service._emit_applies_guardrail")
    @patch("apps_eval.services.test_discovery_service._emit_snapshots_state")
    def test_init_emits_lifecycle_events(self, mock_state, mock_guardrail, mock_digest, mock_replay):
        """Test that initialization emits all lifecycle events."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        mock_replay.assert_called_once_with("test_discovery", "init")
        mock_digest.assert_called_once_with("test_discovery", "init")
        mock_guardrail.assert_called_once_with("p0", "test_discovery", "service_init")
        mock_state.assert_called_once_with("p0", "test_discovery", "service_state")

    def test_discover_from_adg_default_params(self):
        """Test discovering tests from ADG with default parameters."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        tests = service.discover_from_adg()

        assert len(tests) == 5
        assert tests[0]["test_id"] == "test_0"
        assert tests[0]["module"] == "tests/**/*test*.py"
        assert tests[0]["layer"] == "unknown"
        assert len(service._discovered_tests) == 5

    def test_discover_from_adg_custom_pattern(self):
        """Test discovering tests from ADG with custom pattern."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        tests = service.discover_from_adg(module_pattern="custom/**/*.py")

        assert len(tests) == 5
        assert tests[0]["module"] == "custom/**/*.py"

    def test_discover_from_adg_with_target_layer(self):
        """Test discovering tests from ADG with target layer filter."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        tests = service.discover_from_adg(target_layer="L2")

        assert len(tests) == 5
        assert tests[0]["layer"] == "L2"

    def test_discover_from_adg_error_handling(self):
        """Test ADG discovery error handling."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()

        with patch(
            "apps_eval.services.test_discovery_service._emit_records_execution_trace",
            side_effect=Exception("ADG error"),
        ):
            with pytest.raises(Exception, match="ADG error"):
                service.discover_from_adg()

    def test_discover_from_codebase_single_dir(self):
        """Test discovering tests from a single directory."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "test_example.py").write_text("# test file")
            (Path(tmpdir) / "example_test.py").write_text("# test file")

            service = TestDiscoveryService()
            tests = service.discover_from_codebase([tmpdir])

            assert len(tests) == 2
            assert any("test_example" in t["test_id"] for t in tests)
            assert any("example_test" in t["test_id"] for t in tests)

    def test_discover_from_codebase_multiple_dirs(self):
        """Test discovering tests from multiple directories."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            (dir1 / "test_file1.py").write_text("# test")
            (dir2 / "test_file2.py").write_text("# test")

            service = TestDiscoveryService()
            tests = service.discover_from_codebase([str(dir1), str(dir2)])

            assert len(tests) == 2

    def test_discover_from_codebase_nonexistent_dir(self):
        """Test discovering tests from non-existent directory logs warning."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        tests = service.discover_from_codebase(["/nonexistent/directory"])

        assert len(tests) == 0

    def test_discover_from_codebase_custom_patterns(self):
        """Test discovering tests with custom patterns."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "custom_test.py").write_text("# test")
            (Path(tmpdir) / "test_custom.py").write_text("# test")
            (Path(tmpdir) / "other.py").write_text("# not test")

            service = TestDiscoveryService()
            tests = service.discover_from_codebase([tmpdir], test_patterns=["custom_*.py"])

            assert len(tests) == 1
            assert "custom_test" in tests[0]["test_id"]

    def test_discover_from_codebase_default_patterns(self):
        """Test discovering tests with default patterns."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test_foo.py").write_text("# test")
            (Path(tmpdir) / "foo_test.py").write_text("# test")
            (Path(tmpdir) / "bar.py").write_text("# not test")

            service = TestDiscoveryService()
            tests = service.discover_from_codebase([tmpdir])

            assert len(tests) == 2

    def test_discover_from_codebase_empty_directory(self):
        """Test discovering tests from empty directory."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            service = TestDiscoveryService()
            tests = service.discover_from_codebase([tmpdir])

            assert len(tests) == 0

    def test_discover_from_codebase_nested_directories(self):
        """Test discovering tests from nested directory structure."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        with TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "subdir" / "nested"
            nested.mkdir(parents=True)
            (nested / "test_nested.py").write_text("# test")

            service = TestDiscoveryService()
            tests = service.discover_from_codebase([tmpdir])

            assert len(tests) == 1
            assert "test_nested" in tests[0]["test_id"]

    def test_get_catalog(self):
        """Test getting the full catalog of discovered tests."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        service.discover_from_adg()

        catalog = service.get_catalog()
        assert len(catalog) == 5
        # Verify it's a copy, not the original list
        assert catalog is not service._discovered_tests

    def test_get_catalog_empty(self):
        """Test getting catalog when no tests discovered."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        catalog = service.get_catalog()
        assert catalog == []

    def test_clear_catalog(self):
        """Test clearing the test catalog."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        service.discover_from_adg()
        assert len(service._discovered_tests) == 5

        service.clear_catalog()
        assert len(service._discovered_tests) == 0

    @patch("apps_eval.services.test_discovery_service._emit_records_telemetry_event")
    def test_clear_catalog_emits_telemetry(self, mock_emit):
        """Test that clearing catalog emits telemetry event."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        service.clear_catalog()
        mock_emit.assert_called_once_with("p4", "test_discovery", "catalog_cleared")

    def test_multiple_discoveries_accumulate(self):
        """Test that multiple discoveries accumulate in catalog."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        service.discover_from_adg()
        assert len(service._discovered_tests) == 5

        service.discover_from_adg()
        assert len(service._discovered_tests) == 10

    def test_discover_from_codebase_with_empty_source_dirs(self):
        """Test discovering tests with empty source dirs list."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        tests = service.discover_from_codebase([])
        assert len(tests) == 0

    @patch("apps_eval.services.test_discovery_service._emit_records_execution_trace")
    @patch("apps_eval.services.test_discovery_service._emit_routes_to_capability")
    @patch("apps_eval.services.test_discovery_service._emit_validates_capability")
    @patch("apps_eval.services.test_discovery_service._emit_records_telemetry_event")
    def test_discover_from_adg_emits_all_events(self, mock_telemetry, mock_validate, mock_route, mock_trace):
        """Test that ADG discovery emits all required events."""
        from apps_eval.services.test_discovery_service import TestDiscoveryService

        service = TestDiscoveryService()
        service.discover_from_adg()

        mock_trace.assert_called()
        mock_route.assert_called_once()
        mock_validate.assert_called_once()
        assert mock_telemetry.call_count >= 2  # start and complete
