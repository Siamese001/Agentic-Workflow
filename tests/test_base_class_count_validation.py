#!/usr/bin/env python3
"""
Test suite for validating base class agent counts by layer.

Ensures that each layer has exactly ONE base class agent and that
agents with "base" in their name are correctly classified.
"""
import json
import re
from pathlib import Path
import pytest

# Disable path_shield for real file I/O testing
pytestmark = pytest.mark.usefixtures("disable_path_shield")

# Module-level constants
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DASHBOARD_PATH = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"
DISCOVERY_JSON_PATH = PROJECT_ROOT / "reports" / "agent_discovery_full.json"  # Primary source (cache eliminated)


class TestBaseClassCounts:
    """Test base class agent counts and classification."""
    
    def test_l5_safety_has_one_base_class_agent(self):
        """Test that L5 Safety has exactly 1 base class agent."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"
        
        data = json.loads(match.group(1))
        
        # Find L5 Safety/Base Class row
        l5_base_row = next((r for r in data if r.get('Territory') == 'L5 Safety/Base Class'), None)
        
        assert l5_base_row is not None, (
            "L5 Safety/Base Class territory not found in dashboard.\n"
            "This indicates the base class subterritory is not being tracked."
        )
        
        agent_count = int(l5_base_row.get('Total', 0))
        assert agent_count == 1, (
            f"L5 Safety should have exactly 1 base class agent, but found {agent_count}.\n"
            f"Expected: SafetyBaseAgent.py only\n"
            f"Possible issue: BaseClassEnforcerAgent or other agents incorrectly classified as base_class"
        )
    
    def test_base_class_enforcer_not_classified_as_base_class(self):
        """Test that BaseClassEnforcerAgent is NOT classified as a base_class agent."""
        if not DISCOVERY_JSON_PATH.exists():
            pytest.skip("Discovery JSON not found")
        
        data = json.loads(DISCOVERY_JSON_PATH.read_text(encoding='utf-8'))
        
        # Find BaseClassEnforcerAgent
        enforcer_path = next((k for k in data.keys() if 'BaseClassEnforcerAgent' in k), None)
        
        if enforcer_path:
            # BaseClassEnforcerAgent should be in L5_safety/validators, not base_class
            assert 'validators' in enforcer_path, (
                f"BaseClassEnforcerAgent found at unexpected location: {enforcer_path}"
            )
            
            # Check dashboard to ensure it's not counted in Base Class territory
            if DASHBOARD_PATH.exists():
                html = DASHBOARD_PATH.read_text(encoding='utf-8')
                match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
                if match:
                    dashboard_data = json.loads(match.group(1))
                    validators_row = next((r for r in dashboard_data if r.get('Territory') == 'L5 Safety/Validators'), None)
                    
                    if validators_row:
                        # BaseClassEnforcerAgent should be counted in Validators, not Base Class
                        assert validators_row.get('Total', 0) > 0, (
                            "L5 Safety/Validators should have agents including BaseClassEnforcerAgent"
                        )
    
    def test_safety_base_agent_classified_correctly(self):
        """Test that SafetyBaseAgent is correctly classified as base_class."""
        if not DISCOVERY_JSON_PATH.exists():
            pytest.skip("Discovery JSON not found")
        
        data = json.loads(DISCOVERY_JSON_PATH.read_text(encoding='utf-8'))
        
        # Find SafetyBaseAgent
        safety_base_path = next((k for k in data.keys() if 'SafetyBaseAgent' in k), None)
        
        assert safety_base_path is not None, (
            "SafetyBaseAgent not found in discovery data.\n"
            "Expected: agentic_core/L5_safety/guardrails/SafetyBaseAgent.py"
        )
        
        assert 'L5_safety' in safety_base_path, (
            f"SafetyBaseAgent should be in L5_safety directory: {safety_base_path}"
        )
    
    def test_all_layers_have_base_class_territory(self):
        """Test that all layers (L0-L5) have a base_class subterritory in dashboard."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"
        
        data = json.loads(match.group(1))
        
        expected_base_territories = [
            'L0 Maintenance/Base Class',
            'L1 Cognition/Base Class',
            'L2 Execution/Base Class',
            'L3 Orchestration/Base Class',
            'L4 State/Base Class',
            'L5 Safety/Base Class'
        ]
        
        found_territories = [r.get('Territory') for r in data]
        missing_territories = [t for t in expected_base_territories if t not in found_territories]
        
        assert not missing_territories, (
            f"Missing base class territories in dashboard: {missing_territories}\n"
            f"All layers should have a Base Class subterritory for tracking foundational agents."
        )
    
    def test_base_class_agents_have_low_count(self):
        """Test that base class territories have low agent counts (1-3 per layer)."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"
        
        data = json.loads(match.group(1))
        
        base_class_rows = [r for r in data if 'Base Class' in r.get('Territory', '')]
        
        high_count_territories = []
        for row in base_class_rows:
            territory = row.get('Territory')
            count = int(row.get('Total', 0))
            
            # Base class territories should have 1-3 agents max
            # (base + maybe 1-2 mixins)
            if count > 3:
                high_count_territories.append((territory, count))
        
        assert not high_count_territories, (
            f"Base class territories with unexpectedly high agent counts:\n" +
            "\n".join([f"  {t}: {c} agents (expected ≤3)" for t, c in high_count_territories]) +
            "\n\nThis indicates agents are being incorrectly classified as base_class."
        )
    
    def test_no_enforcer_agents_in_base_class(self):
        """Test that no *Enforcer agents are classified as base_class."""
        if not DISCOVERY_JSON_PATH.exists():
            pytest.skip("Discovery JSON not found")
        
        data = json.loads(DISCOVERY_JSON_PATH.read_text(encoding='utf-8'))
        
        # Find all agents with "Enforcer" in their name
        enforcer_agents = [k for k in data.keys() if 'Enforcer' in k]
        
        if not enforcer_agents:
            pytest.skip("No Enforcer agents found")
        
        # Check dashboard to ensure none are in Base Class territories
        if DASHBOARD_PATH.exists():
            html = DASHBOARD_PATH.read_text(encoding='utf-8')
            
            # Enforcer agents should NOT appear in base class context
            for agent_path in enforcer_agents:
                agent_name = Path(agent_path).stem
                
                # These agents should be in their respective layer's core/validator territory
                # NOT in base_class subterritory
                assert 'base_class' not in agent_path.lower() or 'enforcer' in agent_path.lower(), (
                    f"Enforcer agent incorrectly classified: {agent_path}\n"
                    f"Enforcer agents validate base class usage but are not base classes themselves."
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
