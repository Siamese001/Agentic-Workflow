#!/usr/bin/env python3
"""Comprehensive tests for MRO Auditor"""
import pytest
from agentic_core.utils.testing.mro_auditor import MROAuditor
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from dataclasses import dataclass


class TestMROAuditorStaticChecks:
    """Test static MRO order checks."""
    
    def test_audit_valid_agent(self):
        """Test auditing a valid agent passes."""
        @dataclass
        class ValidAgent(SovereignBaseAgent):
            name: str = "ValidAgent"
        
        auditor = MROAuditor()
        errors = auditor.audit_class_hierarchy(ValidAgent)
        assert len(errors) == 0
    
    def test_audit_detects_missing_sovereign(self):
        """Test auditor detects missing SovereignBaseAgent."""
        class BadAgent:
            pass
        
        auditor = MROAuditor()
        errors = auditor.audit_class_hierarchy(BadAgent)
        assert len(errors) > 0
        assert "does not inherit from SovereignBaseAgent" in errors[0]


class TestMROAuditorDynamicChecks:
    """Test dynamic propagation checks."""
    
    def test_verify_propagation_success(self):
        """Test propagation verification succeeds for valid agent."""
        @dataclass
        class ValidAgent(SovereignBaseAgent):
            name: str = "ValidAgent"
        
        agent = ValidAgent()
        auditor = MROAuditor()
        success, error = auditor.verify_initialization_propagation(agent)
        assert success is True
        assert error is None
    
    def test_verify_propagation_failure(self):
        """Test propagation verification detects broken chain."""
        class BrokenAgent:
            pass
        
        agent = BrokenAgent()
        auditor = MROAuditor()
        success, error = auditor.verify_initialization_propagation(agent)
        assert success is False
        assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
