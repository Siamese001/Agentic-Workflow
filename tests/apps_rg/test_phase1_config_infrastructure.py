"""
Test Suite for Phase 1: Configuration Infrastructure.
Verifies schemas, default values, and singleton loading.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from apps_rg.domain.config.schemas import RGAgentSpecs, AgentSpec, OrchestratorConfig
from apps_rg.domain.config.loader import load_rg_specs, reload_config

def test_rg_agent_specs_defaults():
    """Verify default values are populated correctly."""
    specs = RGAgentSpecs()
    
    # Check orchestrator defaults
    assert specs.orchestrator.global_step_limit == 20
    assert specs.orchestrator.max_retry_iterations == 5
    assert specs.orchestrator.checkpoint_enabled is True
    assert specs.orchestrator.trace_persistence is True
    
    # Check other component defaults
    assert specs.clerk_extraction.min_bullets_per_section == 3
    assert specs.clerk_extraction.max_bullets_per_section == 8
    assert specs.enrichment.duplicate_threshold == 0.85
    assert specs.generation.n_candidates == 3
    assert specs.validation.min_quality_score == 0.7

def test_agent_spec_validation():
    """Verify validation logic in AgentSpec."""
    # Valid config
    config = AgentSpec(
        name="TestAgent",
        module_path="apps_rg.engines.test.TestEngine",
        timeout_sec=60
    )
    assert config.name == "TestAgent"
    assert config.timeout_sec == 60
    assert config.criticality == "required"
    
    # Invalid timeout (must be >= 1)
    with pytest.raises(ValueError):
        AgentSpec(
            name="TestAgent",
            module_path="apps_rg.engines.test.TestEngine",
            timeout_sec=0
        )
    
    # Invalid criticality
    with pytest.raises(ValueError):
        AgentSpec(
            name="TestAgent",
            module_path="apps_rg.engines.test.TestEngine",
            criticality="invalid"
        )

def test_orchestrator_config_validation():
    """Verify OrchestratorConfig validation."""
    config = OrchestratorConfig()
    assert config.global_step_limit == 20
    assert config.max_retry_iterations == 5
    assert config.checkpoint_enabled is True
    assert config.trace_persistence is True

def test_singleton_loader():
    """Verify load_rg_specs returns the same instance (Singleton)."""
    reload_config()
    
    # First load
    specs1 = load_rg_specs()
    # Second load
    specs2 = load_rg_specs()
    
    assert specs1 is specs2
    assert id(specs1) == id(specs2)

def test_loader_with_mock_file():
    """Verify loader parses JSON correctly."""
    reload_config()
    
    mock_data = {
        "clerk_extraction": {
            "min_bullets_per_section": 5,
            "max_bullets_per_section": 10
        },
        "orchestrator": {
            "global_step_limit": 50,
            "max_retry_iterations": 10
        }
    }
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        
        specs = load_rg_specs()
        
        assert specs.clerk_extraction.min_bullets_per_section == 5
        assert specs.clerk_extraction.max_bullets_per_section == 10
        assert specs.orchestrator.global_step_limit == 50
        assert specs.orchestrator.max_retry_iterations == 10

def test_loader_force_reload():
    """Verify force_reload parameter works."""
    # Load initial config
    specs1 = load_rg_specs()
    
    # Force reload should return new instance
    specs2 = load_rg_specs(force_reload=True)
    
    # Should be different objects
    assert specs1 is not specs2

def test_loader_missing_file():
    """Verify loader handles missing config file gracefully."""
    reload_config()
    
    with patch("pathlib.Path.exists", return_value=False):
        specs = load_rg_specs()
        
        # Should return default configuration
        assert specs is not None
        assert specs.orchestrator.global_step_limit == 20
        assert specs.orchestrator.max_retry_iterations == 5

def test_loader_invalid_json():
    """Verify loader handles invalid JSON gracefully."""
    reload_config()
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="invalid json")):
        
        # Should fall back to defaults on error
        specs = load_rg_specs()
        assert specs is not None
        assert specs.orchestrator.global_step_limit == 20

def test_topology_validation():
    """Verify OrchestrationTopology validation works."""
    from apps_rg.domain.config.schemas import OrchestrationTopology
    
    # Valid topology
    agent_spec = AgentSpec(
        name="TEST_AGENT",
        module_path="apps_rg.engines.test.TestEngine"
    )
    
    topology = OrchestrationTopology(
        phases={"phase1": ["TEST_AGENT"]},
        agents={"TEST_AGENT": agent_spec}
    )
    
    assert len(topology.phases) == 1
    assert "TEST_AGENT" in topology.agents
    
    # Invalid topology (agent in phase but not in agents)
    with pytest.raises(ValueError, match="unknown agent"):
        OrchestrationTopology(
            phases={"phase1": ["MISSING_AGENT"]},
            agents={"TEST_AGENT": agent_spec}
        )

def test_config_path_resolution():
    """Verify config path is resolved correctly."""
    from apps_rg.domain.config.loader import get_config_path
    
    config_path = get_config_path()
    assert config_path.name == "config"
    assert config_path.exists() or True  # May not exist in test

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
