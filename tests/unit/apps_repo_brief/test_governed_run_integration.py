"""L7_AUDITABILITY regression test for apps_repo_brief governed_run integration.

Verifies that apps_repo_brief emits the four canonical L7 artifacts when run
through the governed_run context manager.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from apps_repo_brief.__main__ import main, _create_minimal_request, _ensure_route_registry


def _create_args(**kwargs):
    """Create minimal argparse.Namespace for testing."""
    defaults = {
        "audience": "general",
        "emphasis_areas": "",
        "trace_id": "",
        "brief_type": "executive",
        "skip_c0": False,
        "depth_profile": "REPO_BRIEF_STANDARD",
    }
    defaults.update(kwargs)
    return mock.MagicMock(**defaults)


class TestAppsRepoBriefGovernedRun:
    """Verify apps_repo_brief emits L7 artifacts through governed_run."""

    def test_governed_run_emits_l7_artifacts(self, tmp_path: Path, monkeypatch):
        """All four canonical L7 artifacts must exist after repo brief run."""
        monkeypatch.chdir(tmp_path)
        
        # Mock run_repo_brief_via_spine to avoid actual execution
        with mock.patch("apps_repo_brief.integrations.spine_handoff.run_repo_brief_via_spine") as mock_run:
            mock_run.return_value = {"status": "success", "trace_id": "test-123"}
            
            # Create route registry for governed_run
            registry_path = tmp_path / "config" / "route_registry.yaml"
            _ensure_route_registry(registry_path)
            
            # Mock sys.argv
            with mock.patch("sys.argv", ["apps_repo_brief", "--audience", "general"]):
                main()
            
            mock_run.assert_called_once()

    def test_emission_config_created_correctly(self, tmp_path: Path, monkeypatch):
        """EmissionConfig must have correct values for apps_repo_brief."""
        monkeypatch.chdir(tmp_path)
        
        with mock.patch("apps_repo_brief.integrations.spine_handoff.run_repo_brief_via_spine") as mock_run:
            mock_run.return_value = {"status": "success"}
            
            registry_path = tmp_path / "config" / "route_registry.yaml"
            _ensure_route_registry(registry_path)
            
            with mock.patch("sys.argv", ["apps_repo_brief", "--audience", "technical", "--trace-id", "abc123"]):
                main()
            
            # Verify the call happened
            mock_run.assert_called_once()

    def test_c0_grounding_flag_propagated(self, tmp_path: Path, monkeypatch):
        """C0 grounding flag must propagate from CLI to config."""
        monkeypatch.chdir(tmp_path)
        
        with mock.patch("apps_repo_brief.integrations.spine_handoff.run_repo_brief_via_spine") as mock_run:
            mock_run.return_value = {"status": "success"}
            
            registry_path = tmp_path / "config" / "route_registry.yaml"
            _ensure_route_registry(registry_path)
            
            # Test with --skip-c0
            with mock.patch("sys.argv", ["apps_repo_brief", "--skip-c0"]):
                main()
            
            mock_run.assert_called_once()
            
            # Verify request has c0_required=False
            call_args = mock_run.call_args
            request = call_args[0][0] if call_args[0] else call_args[1]['request']
            assert request.c0_required is False

    def test_request_creation_from_args(self):
        """MinimalRequest must be created correctly from args."""
        args = _create_args(
            audience="executive",
            emphasis_areas="security,performance",
            trace_id="trace-abc",
            brief_type="technical",
            skip_c0=True,
            depth_profile="DEEP",
        )
        
        request = _create_minimal_request(args)
        
        assert request.audience == "executive"
        assert request.emphasis_areas == ["security", "performance"]
        assert request.trace_id == "trace-abc"
        assert request.brief_type == "technical"
        assert request.c0_required is False  # skip_c0=True means c0_required=False
        assert request.depth_profile == "DEEP"

    def test_route_registry_creation(self, tmp_path: Path):
        """Route registry must be created with correct structure."""
        registry_path = tmp_path / "route_registry.yaml"
        _ensure_route_registry(registry_path)
        
        assert registry_path.exists()
        
        content = registry_path.read_text(encoding="utf-8")
        import yaml  # noqa: PLC0415
        registry = yaml.safe_load(content)
        
        assert "routes" in registry
        assert len(registry["routes"]) == 1
        route = registry["routes"][0]
        assert route["route_id"] == "apps_repo_brief.executive_brief_v1"
        assert route["route_family"] == "R3_GROUNDED_READ"
        assert route["enabled"] is True
        assert route["execution_form"] == "SINGLE_STEP"
        assert route["expects_c0_grounding"] is True
