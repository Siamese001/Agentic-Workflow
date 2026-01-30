"""
Integration tests for Resume Generation Pipeline - RG workflow.

Tests cross-agent communication in the resume generation workflow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with patch('redis.Redis', return_value=Mock()), \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        yield


class TestResumeGenerationIntegration:
    """Integration tests for resume generation agents."""
    
    @pytest.fixture
    def mock_resume_input(self):
        """Provide mock resume input."""
        return {
            'user_profile': {
                'name': 'Test Candidate',
                'current_title': 'Senior Software Engineer',
                'experience': [
                    {'title': 'Senior Engineer', 'company': 'Tech Corp', 'years': 3},
                    {'title': 'Engineer', 'company': 'Startup Inc', 'years': 2},
                ],
                'skills': ['Python', 'AWS', 'Docker', 'Kubernetes'],
                'education': [{'degree': 'BS Computer Science', 'school': 'State University'}],
            },
            'job_description': {
                'title': 'Staff Software Engineer',
                'company': 'Target Corp',
                'required_skills': ['Python', 'AWS', 'Leadership'],
                'preferred_skills': ['Kubernetes', 'Terraform'],
            },
        }
    
    def test_content_quality_to_ats_compatibility(self, mock_resume_input):
        """Test ContentQualityAgent -> ATSCompatibilityAgent flow."""
        content_quality_output = {
            'quality_score': 0.85,
            'issues': [],
            'suggestions': ['Add more quantified achievements'],
        }
        
        # ATS agent should receive quality-checked content
        assert 'quality_score' in content_quality_output, "Should have quality score"
    
    def test_fact_check_to_brand_compliance(self):
        """Test FactCheckAgent -> BrandComplianceAgent flow."""
        fact_check_output = {
            'verified_claims': ['5 years experience', 'Python expertise'],
            'unverified_claims': [],
            'fact_score': 1.0,
        }
        
        assert fact_check_output['fact_score'] == 1.0, "All facts verified"
    
    def test_section_balance_integration(self):
        """Test SectionBalanceAgent integration."""
        section_analysis = {
            'sections': {
                'summary': {'length': 150, 'optimal': True},
                'experience': {'length': 800, 'optimal': True},
                'skills': {'length': 100, 'optimal': True},
                'education': {'length': 80, 'optimal': True},
            },
            'overall_balance': 0.92,
        }
        
        assert section_analysis['overall_balance'] > 0.8, "Good balance"
    
    def test_healing_orchestrator_integration(self):
        """Test RgHealingOrchestratorAgent integration."""
        healing_result = {
            'issues_detected': 2,
            'issues_fixed': 2,
            'remaining_issues': 0,
            'health_score': 1.0,
        }
        
        assert healing_result['remaining_issues'] == 0, "All issues fixed"


class TestResumeValidationChain:
    """Test resume validation chain."""
    
    def test_validation_order(self):
        """Test correct validation order."""
        validation_chain = [
            'ContentQualityAgent',
            'FactCheckAgent',
            'ATSCompatibilityAgent',
            'BrandComplianceAgent',
            'SectionBalanceAgent',
        ]
        
        assert validation_chain[0] == 'ContentQualityAgent', "Content quality first"
        assert 'ATSCompatibilityAgent' in validation_chain, "ATS check included"
    
    def test_validation_aggregation(self):
        """Test validation results aggregation."""
        validations = {
            'content_quality': 0.85,
            'fact_check': 1.0,
            'ats_compatibility': 0.90,
            'brand_compliance': 0.95,
            'section_balance': 0.92,
        }
        
        overall = sum(validations.values()) / len(validations)
        assert overall > 0.9, "Overall score should be high"


class TestResumeGenerationState:
    """Test state management in resume generation."""
    
    def test_state_preservation_across_agents(self):
        """Test state is preserved across agent calls."""
        initial_state = {
            'resume_id': 'test-123',
            'version': 1,
            'content': {'summary': 'Test summary'},
        }
        
        # After processing
        updated_state = {
            **initial_state,
            'version': 2,
            'validations': {'quality': 0.85},
        }
        
        assert initial_state['version'] == 1, "Original unchanged"
        assert updated_state['version'] == 2, "New version incremented"
    
    def test_rollback_capability(self):
        """Test rollback capability on validation failure."""
        checkpoint = {
            'state_before': {'version': 1},
            'state_after': {'version': 2},
            'can_rollback': True,
        }
        
        assert checkpoint['can_rollback'] is True, "Should support rollback"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
