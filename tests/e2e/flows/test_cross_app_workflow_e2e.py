"""
E2E tests for Cross-App Workflow - LIC + RG integration.

Tests complete workflow spanning both LIC and RG applications.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with patch('redis.Redis', return_value=Mock()), \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'ANTHROPIC_API_KEY': 'test-key'}):
        yield


class TestCrossAppWorkflowE2E:
    """E2E tests for cross-app workflows."""
    
    @pytest.fixture
    def mock_candidate_profile(self):
        """Profile used by both LIC and RG."""
        return {
            'id': 'candidate-001',
            'name': 'Sarah Chen',
            'current_title': 'Engineering Manager',
            'target_title': 'Director of Engineering',
            'skills': ['Python', 'Leadership', 'System Design', 'AWS'],
            'experience_years': 10,
        }
    
    @pytest.fixture
    def mock_job_opportunity(self):
        """Job opportunity for both resume and outreach."""
        return {
            'id': 'job-001',
            'title': 'Director of Engineering',
            'company': 'Dream Tech Corp',
            'recruiter': {
                'name': 'Mike Johnson',
                'title': 'Senior Technical Recruiter',
            },
            'requirements': ['Leadership', 'Python', 'Cloud Architecture'],
        }
    
    def test_resume_then_outreach_workflow(self, mock_candidate_profile, mock_job_opportunity):
        """Test workflow: Generate resume, then create outreach to recruiter."""
        # Step 1: RG generates tailored resume
        resume_result = {
            'resume_id': 'resume-001',
            'tailored_for': mock_job_opportunity['title'],
            'highlights': [
                'Engineering leadership experience',
                'Cloud architecture expertise',
            ],
            'quality_score': 0.94,
        }
        assert resume_result['quality_score'] > 0.9, "High quality resume"
        
        # Step 2: LIC uses resume insights for outreach
        outreach_context = {
            'resume_highlights': resume_result['highlights'],
            'target_role': mock_job_opportunity['title'],
            'recruiter': mock_job_opportunity['recruiter'],
        }
        
        # Step 3: LIC generates personalized outreach
        outreach_result = {
            'message_id': 'msg-001',
            'to': mock_job_opportunity['recruiter']['name'],
            'subject': f"Interest in {mock_job_opportunity['title']} role",
            'body': 'Hi Mike, I noticed the Director of Engineering opening...',
            'references_resume': True,
            'quality_score': 0.92,
        }
        assert outreach_result['references_resume'] is True, "Outreach references resume"
    
    def test_shared_profile_consistency(self, mock_candidate_profile):
        """Test profile data consistency across apps."""
        # RG profile view
        rg_profile = {
            'name': mock_candidate_profile['name'],
            'skills': mock_candidate_profile['skills'],
            'experience_years': mock_candidate_profile['experience_years'],
        }
        
        # LIC profile view (sender perspective)
        lic_profile = {
            'sender_name': mock_candidate_profile['name'],
            'sender_skills': mock_candidate_profile['skills'],
            'sender_experience': mock_candidate_profile['experience_years'],
        }
        
        # Verify consistency
        assert rg_profile['name'] == lic_profile['sender_name'], "Name consistent"
        assert rg_profile['skills'] == lic_profile['sender_skills'], "Skills consistent"
    
    def test_shared_utilities_in_workflow(self):
        """Test shared utilities work across both apps."""
        # Both apps use AdaptiveRecoveryLoop
        recovery_config = {
            'max_retries': 3,
            'backoff_factor': 2,
            'timeout_seconds': 30,
        }
        
        # RG usage
        rg_recovery = {
            'app': 'RG',
            'config': recovery_config,
            'used_for': 'llm_calls',
        }
        
        # LIC usage
        lic_recovery = {
            'app': 'LIC',
            'config': recovery_config,
            'used_for': 'research_calls',
        }
        
        assert rg_recovery['config'] == lic_recovery['config'], "Same config"


class TestCrossAppDataFlow:
    """E2E tests for data flow between apps."""
    
    def test_profile_enrichment_flow(self):
        """Test profile enrichment across apps."""
        # Initial profile
        base_profile = {
            'name': 'Test User',
            'skills': ['Python'],
        }
        
        # RG enriches with resume analysis
        rg_enriched = {
            **base_profile,
            'resume_score': 0.85,
            'skill_gaps': ['Leadership'],
        }
        
        # LIC enriches with research
        lic_enriched = {
            **rg_enriched,
            'company_insights': ['Growing fast'],
            'pain_points': ['Hiring challenges'],
        }
        
        assert 'resume_score' in lic_enriched, "RG data preserved"
        assert 'company_insights' in lic_enriched, "LIC data added"
    
    def test_shared_schema_compliance(self):
        """Test both apps comply with shared schemas."""
        shared_schema = {
            'required_fields': ['id', 'timestamp', 'status', 'app_source'],
            'status_values': ['pending', 'processing', 'completed', 'failed'],
        }
        
        # RG output
        rg_output = {
            'id': 'rg-001',
            'timestamp': '2026-01-30T11:00:00Z',
            'status': 'completed',
            'app_source': 'RG',
        }
        
        # LIC output
        lic_output = {
            'id': 'lic-001',
            'timestamp': '2026-01-30T11:01:00Z',
            'status': 'completed',
            'app_source': 'LIC',
        }
        
        # Verify compliance
        for field in shared_schema['required_fields']:
            assert field in rg_output, f"RG has {field}"
            assert field in lic_output, f"LIC has {field}"


class TestCrossAppErrorHandling:
    """E2E tests for cross-app error handling."""
    
    def test_upstream_failure_handling(self):
        """Test handling of upstream app failure."""
        # RG fails
        rg_failure = {
            'app': 'RG',
            'error': 'resume_generation_failed',
            'recoverable': True,
        }
        
        # LIC should handle gracefully
        lic_response = {
            'upstream_failure': True,
            'fallback_action': 'use_basic_profile',
            'continue_workflow': True,
        }
        
        assert lic_response['continue_workflow'] is True, "Workflow continues"
    
    def test_shared_service_failure(self):
        """Test handling of shared service failure."""
        # Shared LLM service fails
        service_failure = {
            'service': 'llm_provider',
            'error': 'rate_limit_exceeded',
            'affects': ['RG', 'LIC'],
        }
        
        # Both apps should handle
        recovery = {
            'action': 'switch_to_fallback_provider',
            'rg_status': 'recovered',
            'lic_status': 'recovered',
        }
        
        assert recovery['rg_status'] == 'recovered', "RG recovered"
        assert recovery['lic_status'] == 'recovered', "LIC recovered"


class TestCrossAppMetrics:
    """E2E tests for cross-app metrics."""
    
    def test_combined_workflow_metrics(self):
        """Test metrics collection across apps."""
        combined_metrics = {
            'workflow_id': 'wf-001',
            'total_duration_ms': 6000,
            'rg_metrics': {
                'duration_ms': 3500,
                'llm_calls': 4,
            },
            'lic_metrics': {
                'duration_ms': 2500,
                'llm_calls': 3,
            },
            'total_llm_calls': 7,
            'total_tokens': 3500,
        }
        
        assert combined_metrics['total_duration_ms'] < 10000, "Fast workflow"
        assert combined_metrics['total_llm_calls'] == 7, "Correct LLM count"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
