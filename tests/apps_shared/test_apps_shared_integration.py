"""
End-to-End Integration Tests — apps_shared

Validates full integration with agentic_core and all apps_* folders.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from apps_shared.config.operational_config import (
    is_allowed_duplicate,
    is_excluded_path,
    should_scan_directory,
)
from apps_shared.services import (
    ConfigLoaderService,
    EnvironmentValidatorService,
    OperationalScannerService,
)


class TestAppsSharedIntegration:
    """Integration tests for apps_shared."""

    def test_environment_config_import(self) -> None:
        """Test that environment config imports with lifecycle traces."""
        from apps_shared.config import environment_config

        assert hasattr(environment_config, "_emit_applies_guardrail")
        assert hasattr(environment_config, "EnvironmentConfig")

    def test_operational_config_import(self) -> None:
        """Test that operational config imports with lifecycle traces."""
        from apps_shared.config import operational_config

        assert hasattr(operational_config, "_emit_applies_guardrail")
        assert hasattr(operational_config, "is_excluded_path")

    def test_config_loader_service_init(self) -> None:
        """Test ConfigLoaderService initialization."""
        service = ConfigLoaderService()
        assert service is not None
        assert hasattr(service, "load_json_config")
        assert hasattr(service, "clear_cache")

    def test_config_loader_service_load(self, tmp_path: Any) -> None:
        """Test ConfigLoaderService can load JSON config."""
        service = ConfigLoaderService()

        # Create a test config file
        config_file = tmp_path / "test_config.json"
        test_config = {"key": "value", "nested": {"a": 1}}
        config_file.write_text(json.dumps(test_config))

        # Load the config
        loaded = service.load_json_config(str(config_file))
        assert loaded == test_config

    def test_environment_validator_service_init(self) -> None:
        """Test EnvironmentValidatorService initialization."""
        service = EnvironmentValidatorService()
        assert service is not None
        assert hasattr(service, "validate_environment")

    def test_operational_scanner_service_init(self) -> None:
        """Test OperationalScannerService initialization."""
        service = OperationalScannerService()
        assert service is not None
        assert hasattr(service, "scan_directory")

    def test_operational_exclusion_check(self) -> None:
        """Test operational path exclusion logic."""
        # Should exclude .git paths
        assert is_excluded_path("/some/path/.git/config") is True
        # Should not exclude normal paths
        assert is_excluded_path("/some/path/module.py") is False

    def test_duplicate_allowlist_check(self) -> None:
        """Test duplicate file allowlist logic."""
        # Should allow conftest.py
        assert is_allowed_duplicate("conftest.py") is True
        # Should not allow random files
        assert is_allowed_duplicate("random_module.py") is False

    def test_scan_directory_check(self) -> None:
        """Test scan directory logic."""
        # Should scan agentic_core
        assert should_scan_directory("agentic_core") is True
        # Should not scan random directories
        assert should_scan_directory("random_dir") is False

    def test_integration_with_apps_eval(self) -> None:
        """Test apps_shared integration with apps_eval."""
        # apps_eval should be able to import apps_shared services
        from apps_eval.config.agent_spec_config import EvalAgentSpecs

        assert EvalAgentSpecs is not None

    def test_integration_with_apps_exec(self) -> None:
        """Test apps_shared integration with apps_exec."""
        from apps_exec.config.agent_spec_config import ExecAgentSpecs

        assert ExecAgentSpecs is not None

    def test_integration_with_apps_research(self) -> None:
        """Test apps_shared integration with apps_research."""
        from apps_research.config.agent_spec_config import ResearchAgentSpecs

        assert ResearchAgentSpecs is not None

    def test_adg_lifecycle_imports_available(self) -> None:
        """Verify ADG lifecycle trace imports are available."""
        from agentic_core.runtime.contracts.lifecycle_trace_contract import (
            LayerSegment,
            _emit_records_execution_trace,
            _emit_records_telemetry_event,
            emit_determinism_digest,
            emit_replay_key,
        )

        assert LayerSegment is not None
        assert _emit_records_execution_trace is not None
        assert _emit_records_telemetry_event is not None
        assert emit_determinism_digest is not None
        assert emit_replay_key is not None
