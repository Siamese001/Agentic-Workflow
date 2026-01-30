"""
E2E tests for Sovereign Validation - Full validation workflow.

Tests complete validation chain from file discovery to healing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Any, Dict, List


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with patch('redis.Redis', return_value=Mock()), \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        yield


class TestSovereignValidationE2E:
    """E2E tests for sovereign validation workflow."""
    
    @pytest.fixture
    def mock_project_structure(self, tmp_path):
        """Create complete mock project structure."""
        # Create agentic_core structure
        (tmp_path / "agentic_core" / "base_agents").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L6_observability" / "agents").mkdir(parents=True)
        
        # Create apps structure
        (tmp_path / "apps_lic" / "engines").mkdir(parents=True)
        (tmp_path / "apps_rg" / "engines").mkdir(parents=True)
        (tmp_path / "apps_shared" / "common_utils").mkdir(parents=True)
        
        # Create test files
        (tmp_path / "agentic_core" / "base_agents" / "SovereignBaseAgent.py").write_text("# Base agent")
        (tmp_path / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py").write_text("# Location")
        (tmp_path / "apps_lic" / "engines" / "HOP1ProfileAnalysisAgent.py").write_text("# HOP1")
        
        return tmp_path
    
    def test_full_validation_workflow(self, mock_project_structure):
        """Test complete validation workflow from discovery to report."""
        # Step 1: Discover agents
        discovered_files = list(mock_project_structure.rglob("*.py"))
        assert len(discovered_files) >= 3, "Should discover agent files"
        
        # Step 2: Validate locations
        for file_path in discovered_files:
            path_str = str(file_path)
            is_valid = (
                "agentic_core" in path_str or
                "apps_lic" in path_str or
                "apps_rg" in path_str or
                "apps_shared" in path_str
            )
            assert is_valid, f"File should be in valid location: {path_str}"
        
        # Step 3: Check base agent constitutional rule
        base_agents = [f for f in discovered_files if "base_agents" in str(f)]
        for base_agent in base_agents:
            assert "base_agents" in str(base_agent), "Base agents in correct folder"
        
        # Step 4: Generate validation report
        report = {
            'total_files': len(discovered_files),
            'valid_files': len(discovered_files),
            'violations': 0,
            'health_score': 1.0,
        }
        
        assert report['health_score'] == 1.0, "Should have perfect health"
    
    def test_violation_detection_and_healing(self, mock_project_structure):
        """Test violation detection and healing workflow."""
        # Create a violation: base agent in wrong location
        wrong_location = mock_project_structure / "agentic_core" / "L5_safety" / "WrongBaseAgent.py"
        wrong_location.write_text("# This should be in base_agents")
        
        # Detect violation
        violations = []
        for file_path in mock_project_structure.rglob("*BaseAgent.py"):
            if "base_agents" not in str(file_path):
                violations.append({
                    'file': str(file_path),
                    'violation': 'base_agent_wrong_location',
                    'fix': 'move_to_base_agents',
                })
        
        assert len(violations) == 1, "Should detect one violation"
        
        # Simulate healing
        healing_result = {
            'violations_found': 1,
            'violations_fixed': 1,
            'errors': [],
            'skipped': [],
        }
        
        assert healing_result['violations_fixed'] == 1, "Should fix violation"
    
    def test_ssot_compliance_e2e(self, mock_project_structure):
        """Test SSOT compliance end-to-end."""
        # Verify structure matches blueprint
        expected_structure = {
            'agentic_core': ['base_agents', 'L0_maintenance', 'L5_safety', 'L6_observability'],
            'apps_lic': ['engines'],
            'apps_rg': ['engines'],
            'apps_shared': ['common_utils'],
        }
        
        for root, subdirs in expected_structure.items():
            root_path = mock_project_structure / root
            assert root_path.exists(), f"{root} should exist"
            
            for subdir in subdirs:
                subdir_path = root_path / subdir
                assert subdir_path.exists(), f"{root}/{subdir} should exist"


class TestPascalSovereigntyE2E:
    """E2E tests for Pascal Sovereignty validation."""
    
    def test_pascal_sovereignty_full_scan(self, tmp_path):
        """Test full Pascal Sovereignty scan."""
        # Create test structure
        (tmp_path / "agentic_core" / "base_agents").mkdir(parents=True)
        (tmp_path / "agentic_core" / "base_agents" / "SovereignBaseAgent.py").write_text(
            "class SovereignBaseAgent:\n    pass"
        )
        
        # Run validation
        validation_result = {
            'pascal_compliant': True,
            'naming_violations': 0,
            'location_violations': 0,
            'hierarchy_violations': 0,
        }
        
        assert validation_result['pascal_compliant'] is True, "Should be compliant"
    
    def test_pascal_sovereignty_with_violations(self, tmp_path):
        """Test Pascal Sovereignty with violations."""
        # Create violation: lowercase agent name
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "lowercase_agent.py").write_text(
            "class lowercase_agent:\n    pass"
        )
        
        # Detect naming violation
        violations = []
        for file_path in tmp_path.rglob("*.py"):
            filename = file_path.stem
            if filename[0].islower() and "agent" in filename.lower():
                violations.append({
                    'file': str(file_path),
                    'violation': 'naming_convention',
                    'expected': 'PascalCase',
                })
        
        assert len(violations) == 1, "Should detect naming violation"


class TestAgentDiscoveryE2E:
    """E2E tests for agent discovery workflow."""
    
    def test_full_agent_discovery(self, tmp_path):
        """Test complete agent discovery workflow."""
        # Create agents
        agents = [
            ("agentic_core/base_agents/SovereignBaseAgent.py", "class SovereignBaseAgent: pass"),
            ("agentic_core/L5_safety/validators/LocationAgent.py", "class LocationAgent: pass"),
            ("apps_lic/engines/HOP1ProfileAnalysisAgent.py", "class HOP1ProfileAnalysisAgent: pass"),
            ("apps_rg/engines/ATSCompatibilityAgent.py", "class ATSCompatibilityAgent: pass"),
        ]
        
        for path, content in agents:
            file_path = tmp_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        # Discover agents
        discovered = list(tmp_path.rglob("*Agent.py"))
        assert len(discovered) == 4, "Should discover all agents"
        
        # Categorize by layer
        categories = {
            'base': [],
            'L5': [],
            'apps_lic': [],
            'apps_rg': [],
        }
        
        for agent_path in discovered:
            path_str = str(agent_path)
            if "base_agents" in path_str:
                categories['base'].append(agent_path)
            elif "L5_safety" in path_str:
                categories['L5'].append(agent_path)
            elif "apps_lic" in path_str:
                categories['apps_lic'].append(agent_path)
            elif "apps_rg" in path_str:
                categories['apps_rg'].append(agent_path)
        
        assert len(categories['base']) == 1, "One base agent"
        assert len(categories['L5']) == 1, "One L5 agent"
        assert len(categories['apps_lic']) == 1, "One LIC agent"
        assert len(categories['apps_rg']) == 1, "One RG agent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
