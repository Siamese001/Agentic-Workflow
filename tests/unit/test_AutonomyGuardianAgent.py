"""Unit tests for AutonomyGuardianAgent - L5 Safety Validator."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json


class TestAutonomyGuardianAgent:
    """Test suite for AutonomyGuardianAgent compliance dashboard generation."""
    
    @pytest.fixture
    def agent(self):
        """Create AutonomyGuardianAgent instance."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        return AutonomyGuardianAgent(project_root=Path('.'))
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes."""
        assert agent.project_root is not None
        assert hasattr(agent, 'generate_compliance_report')
        assert hasattr(agent, 'heal_repository')
    
    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method is defined."""
        assert callable(getattr(agent, 'heal_repository', None))
    
    def test_heal_repository_returns_dict(self, agent):
        """Test heal_repository returns proper dict structure."""
        result = agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)
    
    def test_detect_mcp_hardening(self, agent):
        """Test MCP hardening detection logic."""
        # Test with MCPHardenedMixin
        content_with_mixin = "class TestAgent():\n    pass"
        result = agent._detect_mcp_hardening(None, content_with_mixin)
        assert result == 1
        
        # Test with MCPShield
        content_with_shield = "class TestAgent(MCPShield):\n    pass"
        result = agent._detect_mcp_hardening(None, content_with_shield)
        assert result == 1
        
        # Test without MCP hardening
        content_without = "class TestAgent:\n    pass"
        result = agent._detect_mcp_hardening(None, content_without)
        assert result == 0
    
    def test_detect_healing_invocation(self, agent):
        """Test healing invocation detection logic."""
        # Test with super().heal_repository()
        content_with_super = "def heal_repository(self):\n    super().heal_repository()"
        result = agent._detect_healing_invocation(None, content_with_super)
        assert result == 1
        
        # Test without super call
        content_without = "def heal_repository(self):\n    return {}"
        result = agent._detect_healing_invocation(None, content_without)
        assert result == 0
    
    def test_detect_healing_capability(self, agent):
        """Test healing capability detection logic."""
        # Test with HealerMixin
        content_with_mixin = "class TestAgent(HealerMixin):\n    pass"
        result = agent._detect_healing_capability(None, content_with_mixin)
        assert result == 1
        
        # Test with heal_repository method
        content_with_method = "def heal_repository(self):\n    pass"
        result = agent._detect_healing_capability(None, content_with_method)
        assert result == 1
        
        # Test without healing capability
        content_without = "class TestAgent:\n    pass"
        result = agent._detect_healing_capability(None, content_without)
        assert result == 0


class TestAutonomyGuardianAgentMetrics:
    """Test metrics calculation in AutonomyGuardianAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create AutonomyGuardianAgent instance."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        return AutonomyGuardianAgent(project_root=Path('.'))
    
    def test_get_all_agent_paths_deduplication(self, agent):
        """Test that agent paths are deduplicated."""
        paths = agent._get_all_agent_paths()
        # Check no duplicates
        assert len(paths) == len(set(str(p) for p in paths))
    
    def test_sparkline_generation(self, agent):
        """Test sparkline SVG generation."""
        data = [10, 20, 30, 40, 50]
        sparkline = agent._generate_sparkline(data)
        assert '<svg' in sparkline
        assert '</svg>' in sparkline


class TestAutonomyGuardianAgentIntegration:
    """Integration tests for AutonomyGuardianAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create AutonomyGuardianAgent instance."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        return AutonomyGuardianAgent(project_root=Path('.'))
    
    @pytest.mark.slow
    def test_generate_compliance_report(self, agent):
        """Test full compliance report generation."""
        # This is a slow test - only run when needed
        agent.generate_compliance_report()
        
        # Check output files exist
        assert Path('reports/autonomy_dashboard.html').exists()
        assert Path('reports/autonomy_compliance_report.md').exists()
        assert Path('reports/autonomy_compliance_data.csv').exists()
