"""
Unit tests for Configuration Infrastructure.
Ensures schemas define correct types and loader handles caching/validation.
"""
import pytest
import json
from pathlib import Path
from pydantic import ValidationError
from apps_lic.domain.config.loader import load_agent_specs, get_config_path
from apps_lic.domain.config.schemas import AgentSpecs

class TestConfigInfrastructure:
    
    def test_load_valid_specs(self):
        """Test successful loading and parsing of the default JSON."""
        specs = load_agent_specs(force_reload=True)
        assert isinstance(specs, AgentSpecs)
        
        # Verify nested access
        assert "C_LEVEL" in specs.profile_analysis_agent.archetype_indicators
        assert specs.profile_analysis_agent.archetype_indicators["C_LEVEL"].confidence == 0.95
        assert specs.research_agent.fallback_rag_params["timeout_seconds"] == 30

    def test_caching_mechanism(self):
        """Test that the loader caches results."""
        specs1 = load_agent_specs(force_reload=True)
        specs2 = load_agent_specs(force_reload=False)
        assert specs1 is specs2  # Same object reference
        
        specs3 = load_agent_specs(force_reload=True)
        assert specs1 is not specs3  # New object reference

    def test_validation_error(self, tmp_path, monkeypatch):
        """Test that invalid JSON raises ValidationError."""
        # Create invalid config (confidence > 1.0)
        invalid_data = {
            "profile_analysis_agent": {
                "archetype_indicators": {
                    "BAD": {"keywords": ["test"], "confidence": 1.5} 
                },
                "default_archetype": "TEST",
                "default_confidence": 0.5,
                "manual_override_threshold": 0.6
            },
            "research_agent": {
                "vector_store_query_params": {"top_k": 10.0, "similarity_threshold": 0.7},
                "fallback_rag_params": {"max_results": 5, "timeout_seconds": 30}
            }
        }
        
        # Mock get_config_path to point to tmp_path
        d = tmp_path / "subdir"
        d.mkdir()
        p = d / "agent_specs.json"
        p.write_text(json.dumps(invalid_data), encoding="utf-8")
        
        monkeypatch.setattr("apps_lic.domain.config.loader.get_config_path", lambda: d)
        
        with pytest.raises(ValidationError):
            load_agent_specs(force_reload=True)

    def test_missing_file_error(self, tmp_path, monkeypatch):
        """Test that missing file raises FileNotFoundError."""
        d = tmp_path / "empty_dir"
        d.mkdir()
        monkeypatch.setattr("apps_lic.domain.config.loader.get_config_path", lambda: d)
        
        with pytest.raises(FileNotFoundError):
            load_agent_specs(force_reload=True)
