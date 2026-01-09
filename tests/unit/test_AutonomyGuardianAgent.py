"""Unit tests for AutonomyGuardianAgent - L5 Safety Validator."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json


class TestAutonomyGuardianAgentImport:
    """Test suite for AutonomyGuardianAgent import and basic structure."""
    
    def test_agent_can_be_imported(self):
        """Test AutonomyGuardianAgent can be imported."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        assert AutonomyGuardianAgent is not None
    
    def test_agent_has_required_methods(self):
        """Test agent class has required methods defined."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        assert hasattr(AutonomyGuardianAgent, 'generate_compliance_report')
        assert hasattr(AutonomyGuardianAgent, 'heal_repository')
