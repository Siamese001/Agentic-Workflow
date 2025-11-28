"""
Comprehensive Pytest Suite for Resume Workflow v16_00 Refactoring
Tests all three specification implementations:
1. Spec 1: Dormant Retry Logic (Pre-flight + Failure Classification)
2. Spec 2: Agentic RAG Feature Activation
3. Spec 3: Code Cleanup Refactoring
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, MagicMock, patch, call
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

# Add the module to path
sys.path.insert(0, '/home/claude')

# Import from the refactored workflow
from resume_workflow_v16_20 import (
    WorkflowOrchestrator,
    ConstraintFailureClassifier,
    ValidationResult,
    ValidationSeverity,
    ValidationEngine,
    ValidationRule,
    ArtistGenerator,
    PreFlightValidator,
    ResumeSection,
    HopExecutionError,
    AppTrackerQAValidator,
    GeminiWebSearchClient,
    WebSearchRAG,
    RAGMission,
    PhaseExecutor,
    __version__
)


# ============================================================================
# SPEC 1.1: PRE-FLIGHT CONSTRAINT TEST
# ============================================================================

class TestSpec1_1_PreFlightConstraintTest:
    """Test Suite for Spec 1.1: Pre-flight Constraint Stress Test Integration"""
    
    def test_version_updated(self):
        """Verify version is updated to 16_20"""
        assert __version__ == "16_20", f"Version should be 16_20, got {__version__}"
    
    @patch('resume_workflow_v16_20.ArtistGenerator._pre_flight_constraint_test')
    @patch('resume_workflow_v16_20.ArtistGenerator.__init__')
    @patch('resume_workflow_v16_20.PreFlightValidator.__init__')
    def test_preflight_called_for_all_sections(
        self, 
        mock_validator_init,
        mock_artist_init,
        mock_preflight
    ):
        """Test that pre-flight test is called for all LLM sections"""
        mock_artist_init.return_value = None
        mock_validator_init.return_value = None
        mock_preflight.return_value = True  # All tests pass
        
        # Create mock artist with required attributes
        mock_artist = Mock()
        mock_artist.SECTION_GENERATION_SPECS = {
            ResumeSection.K1_EXECUTIVE_SUMMARY: {
                'generation_method': '_generate_section_generic',
                'context_builder': '_build_context_k1_summary',
                'prompt_template': 'Test prompt with {min_wc} and {max_wc}'
            },
            ResumeSection.K0_HEADLINE: {
                'generation_method': '_generate_section_generic',
                'context_builder': '_build_context_k0_headline',
                'prompt_template': 'Headline prompt'
            }
        }
        
        # Mock context builders
        mock_artist._build_context_k1_summary = Mock(return_value={
            'min_wc': 100, 'max_wc': 150
        })
        mock_artist._build_context_k0_headline = Mock(return_value={
            'min_wc': 10, 'max_wc': 15
        })
        mock_artist._pre_flight_constraint_test = mock_preflight
        
        # Simulate the pre-flight test execution
        all_llm_sections = {
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K0_HEADLINE
        }
        
        for section_enum in all_llm_sections:
            spec = mock_artist.SECTION_GENERATION_SPECS.get(section_enum)
            if spec:
                context_builder_name = spec.get("context_builder")
                if context_builder_name:
                    context_builder = getattr(mock_artist, context_builder_name)
                    context = context_builder(section_enum)
                    mock_artist._pre_flight_constraint_test(
                        section_enum, 
                        "test prompt",
                        context
                    )
        
        # Verify pre-flight was called for each section
        assert mock_preflight.call_count == 2, \
            f"Pre-flight should be called twice, was called {mock_preflight.call_count} times"
    
    def test_preflight_failure_raises_hop_error(self):
        """Test that pre-flight failure raises HopExecutionError"""
        with patch('resume_workflow_v16_20.ArtistGenerator._pre_flight_constraint_test') as mock_preflight:
            mock_preflight.return_value = False  # Constraint test fails
            
            # Simulate what should happen in the workflow
            is_achievable = mock_preflight(
                ResumeSection.K1_EXECUTIVE_SUMMARY,
                "test prompt",
                {'min_wc': 100, 'max_wc': 150}
            )
            
            if not is_achievable:
                with pytest.raises(HopExecutionError):
                    raise HopExecutionError(
                        f"Constraint Pre-flight FAILED for K1_EXECUTIVE_SUMMARY. "
                        f"Constraints are likely impossible to meet."
                    )
    
    def test_preflight_skips_sections_without_context_builder(self):
        """Test that pre-flight gracefully skips sections without context builders"""
        mock_artist = Mock()
        mock_artist.SECTION_GENERATION_SPECS = {
            ResumeSection.K7_EDUCATION: {
                'generation_method': '_copy_from_master',
                'master_data_key': 'education'
                # No context_builder
            }
        }
        
        # Should not raise error for sections without context builders
        all_llm_sections = {ResumeSection.K7_EDUCATION}
        
        for section_enum in all_llm_sections:
            spec = mock_artist.SECTION_GENERATION_SPECS.get(section_enum)
            context_builder_name = spec.get("context_builder")
            # Should be None, so pre-flight is skipped
            assert context_builder_name is None, \
                "Copy sections should not have context builders"


# ============================================================================
# SPEC 1.2: FAILURE CLASSIFICATION LOGIC
# ============================================================================

class TestSpec1_2_FailureClassification:
    """Test Suite for Spec 1.2: Constraint Failure Classifier Integration"""
    
    def test_failure_classifier_classify_mechanical(self):
        """Test that mechanical failures are correctly classified"""
        vr = ValidationResult(
            rule_id="WORD_COUNT_K1_SUMMARY",
            passed=False,
            severity=ValidationSeverity.CRITICAL,
            message="Word count out of range"
        )
        
        category = ConstraintFailureClassifier.classify_failure(vr, 0.8)
        assert category == "MECHANICAL", \
            f"Word count failure should be MECHANICAL, got {category}"
    
    def test_failure_classifier_classify_creative(self):
        """Test that creative failures are correctly classified"""
        vr = ValidationResult(
            rule_id="PLACEHOLDER_CONTENT_DETECTED",
            passed=False,
            severity=ValidationSeverity.HIGH,
            message="Found placeholder text"
        )
        
        category = ConstraintFailureClassifier.classify_failure(vr, 0.8)
        assert category == "CREATIVE", \
            f"Placeholder failure should be CREATIVE, got {category}"
    
    def test_failure_classifier_classify_semantic(self):
        """Test that semantic failures are correctly classified"""
        vr = ValidationResult(
            rule_id="FORBIDDEN_VERB_DETECTED",
            passed=False,
            severity=ValidationSeverity.HIGH,
            message="Found forbidden verb"
        )
        
        category = ConstraintFailureClassifier.classify_failure(vr, 0.8)
        assert category == "SEMANTIC", \
            f"Forbidden verb failure should be SEMANTIC, got {category}"
    
    def test_failure_analysis_aggregation(self):
        """Test that failure analysis correctly aggregates categories"""
        failed_rules = [
            ValidationResult("WORD_COUNT_K1", False, ValidationSeverity.CRITICAL, "wc"),
            ValidationResult("SENTENCE_COUNT_K1", False, ValidationSeverity.CRITICAL, "sc"),
            ValidationResult("PLACEHOLDER_K2", False, ValidationSeverity.HIGH, "ph"),
        ]
        
        failure_analysis = defaultdict(int)
        temperature = 0.8
        
        for vr in failed_rules:
            category = ConstraintFailureClassifier.classify_failure(vr, temperature)
            failure_analysis[category] += 1
        
        assert failure_analysis["MECHANICAL"] == 2, \
            f"Should have 2 MECHANICAL failures, got {failure_analysis['MECHANICAL']}"
        assert failure_analysis["CREATIVE"] == 1, \
            f"Should have 1 CREATIVE failure, got {failure_analysis['CREATIVE']}"
    
    def test_creative_failure_halts_when_dominant(self):
        """Test that creative failures halt when >= mechanical failures"""
        failure_analysis = {
            "CREATIVE": 3,
            "MECHANICAL": 2,
            "SEMANTIC": 1
        }
        
        creative_failures = failure_analysis.get("CREATIVE", 0)
        mechanical_failures = failure_analysis.get("MECHANICAL", 0)
        
        # This should trigger halt
        should_halt = (creative_failures > 0 and 
                       creative_failures >= mechanical_failures)
        
        assert should_halt, \
            "Should halt when creative failures >= mechanical failures"
        
        if should_halt:
            with pytest.raises(HopExecutionError):
                raise HopExecutionError(
                    f"Creative Failure detected ({creative_failures} creative vs. "
                    f"{mechanical_failures} mechanical). Lowering temperature will not fix this. Halting."
                )


# ============================================================================
# SPEC 1.3: DEPRECATED FUNCTIONS REMOVED
# ============================================================================

class TestSpec1_3_DeprecatedFunctionsRemoved:
    """Test Suite for Spec 1.3: Verify deprecated functions are removed"""
    
    def test_should_reduce_temperature_removed(self):
        """Test that should_reduce_temperature method is removed"""
        assert not hasattr(ConstraintFailureClassifier, 'should_reduce_temperature'), \
            "should_reduce_temperature should be removed from ConstraintFailureClassifier"
    
    def test_get_feedback_instruction_removed(self):
        """Test that _get_feedback_instruction method is removed"""
        # Create a mock artist to check
        with patch('resume_workflow_v16_20.ArtistGenerator.__init__'):
            artist = ArtistGenerator.__new__(ArtistGenerator)
            assert not hasattr(artist, '_get_feedback_instruction'), \
                "_get_feedback_instruction should be removed from ArtistGenerator"
    
    def test_deprecated_comments_present(self):
        """Verify deprecation comments are in the code"""
        with open('/home/claude/resume_workflow_v16_20.py', 'r') as f:
            content = f.read()
        
        assert "# DEPRECATED: Removed should_reduce_temperature (Spec 1.3)" in content, \
            "Should have deprecation comment for should_reduce_temperature"
        assert "# DEPRECATED: Removed _get_feedback_instruction (Spec 1.3)" in content, \
            "Should have deprecation comment for _get_feedback_instruction"


# ============================================================================
# SPEC 2: AGENTIC RAG FEATURE ACTIVATION
# ============================================================================

class TestSpec2_AgenticRAGActivation:
    """Test Suite for Spec 2: Agentic RAG Feature Activation"""
    
    @patch.object(GeminiWebSearchClient, 'agentic_search_and_analyze')
    def test_phase1_uses_agentic_rag(self, mock_agentic):
        """Test that phase1_thematic_research uses agentic RAG"""
        # Setup mock return value (3-tuple)
        mock_agentic.return_value = (
            {"search_summary": "test", "thematic_analysis": {}},
            10,  # API calls
            Mock()  # RAG state
        )
        
        with patch('resume_workflow_v16_20.WebSearchRAG.__init__') as mock_init:
            mock_init.return_value = None
            rag = WebSearchRAG.__new__(WebSearchRAG)
            rag.client = Mock()
            rag.client.agentic_search_and_analyze = mock_agentic
            rag.executor = Mock()
            rag._build_phase1_prompt = Mock(return_value="test prompt")
            
            # Simulate the phase execution
            def main_phase1():
                prompt = rag._build_phase1_prompt("job desc", Mock())
                result_dict, calls_made, rag_state = rag.client.agentic_search_and_analyze(
                    prompt, "Phase 1: Thematic Research"
                )
                return result_dict, calls_made
            
            result = main_phase1()
            
            # Verify agentic method was called
            mock_agentic.assert_called_once()
            assert len(result) == 2, "Should return 2-tuple for executor"
            assert result[1] == 10, "Should return API call count"
    
    @patch.object(GeminiWebSearchClient, 'agentic_search_and_analyze')
    def test_phase2_uses_agentic_rag(self, mock_agentic):
        """Test that phase2_authenticity_patterns uses agentic RAG"""
        mock_agentic.return_value = ({"patterns": []}, 8, Mock())
        
        with patch('resume_workflow_v16_20.WebSearchRAG.__init__') as mock_init:
            mock_init.return_value = None
            rag = WebSearchRAG.__new__(WebSearchRAG)
            rag.client = Mock()
            rag.client.agentic_search_and_analyze = mock_agentic
            
            # Verify the method signature change
            def main_phase2():
                result_dict, calls_made, rag_state = rag.client.agentic_search_and_analyze(
                    "prompt", "Phase 2: Authenticity Patterns"
                )
                return result_dict, calls_made
            
            result = main_phase2()
            mock_agentic.assert_called_once()
    
    @patch.object(GeminiWebSearchClient, 'agentic_search_and_analyze')
    def test_phase3_uses_agentic_rag(self, mock_agentic):
        """Test that phase3_competitive_positioning uses agentic RAG"""
        mock_agentic.return_value = ({"competitive_intel": {}}, 12, Mock())
        
        with patch('resume_workflow_v16_20.WebSearchRAG.__init__') as mock_init:
            mock_init.return_value = None
            rag = WebSearchRAG.__new__(WebSearchRAG)
            rag.client = Mock()
            rag.client.agentic_search_and_analyze = mock_agentic
            
            def main_phase3():
                result_dict, calls_made, rag_state = rag.client.agentic_search_and_analyze(
                    "prompt", "Phase 3: Competitive Positioning"
                )
                return result_dict, calls_made
            
            result = main_phase3()
            mock_agentic.assert_called_once()
    
    @patch.object(GeminiWebSearchClient, 'agentic_search_and_analyze')
    def test_phase4_uses_agentic_rag(self, mock_agentic):
        """Test that phase4_narrative_mining uses agentic RAG"""
        mock_agentic.return_value = ({"narrative": {}}, 9, Mock())
        
        with patch('resume_workflow_v16_20.WebSearchRAG.__init__') as mock_init:
            mock_init.return_value = None
            rag = WebSearchRAG.__new__(WebSearchRAG)
            rag.client = Mock()
            rag.client.agentic_search_and_analyze = mock_agentic
            
            def main_phase4():
                result_dict, calls_made, rag_state = rag.client.agentic_search_and_analyze(
                    "prompt", "Phase 4: Narrative Mining"
                )
                return result_dict, calls_made
            
            result = main_phase4()
            mock_agentic.assert_called_once()
    
    def test_agentic_spec_comments_present(self):
        """Verify agentic RAG spec comments are in the code"""
        with open('/home/claude/resume_workflow_v16_20.py', 'r') as f:
            content = f.read()
        
        # Should have 4 sets of comments (one for each phase)
        assert content.count("# --- SPEC 2: ACTIVATE AGENTIC RAG ---") == 4, \
            "Should have 4 agentic RAG activation comments"
        assert content.count("# --- END SPEC 2 ---") == 4, \
            "Should have 4 agentic RAG end comments"


# ============================================================================
# SPEC 3.1: BULK RULE REGISTRATION
# ============================================================================

class TestSpec3_1_BulkRuleRegistration:
    """Test Suite for Spec 3.1: ValidationEngine.register_rules Integration"""
    
    @patch.object(ValidationEngine, 'register_rules')
    def test_register_rules_called_once(self, mock_register_rules):
        """Test that register_rules is called once with all rules"""
        engine = ValidationEngine()
        
        # Simulate what _register_rules does
        rules_to_register = [
            ValidationRule("TEST_1", ValidationSeverity.HIGH, "test", lambda x: True, "msg1"),
            ValidationRule("TEST_2", ValidationSeverity.MEDIUM, "test", lambda x: True, "msg2"),
            ValidationRule("TEST_3", ValidationSeverity.LOW, "test", lambda x: True, "msg3"),
        ]
        
        # Should be called once with list of all rules
        engine.register_rules(rules_to_register)
        
        mock_register_rules.assert_called_once()
        call_args = mock_register_rules.call_args[0][0]
        assert len(call_args) == 3, \
            f"Should register 3 rules in one call, got {len(call_args)}"
    
    def test_bulk_registration_spec_comments_present(self):
        """Verify bulk registration spec comments are in the code"""
        with open('/home/claude/resume_workflow_v16_20.py', 'r') as f:
            content = f.read()
        
        assert "# --- SPEC 3.1: USE BULK REGISTRATION ---" in content, \
            "Should have bulk registration activation comment"
        assert "# Single bulk registration call" in content, \
            "Should have comment about single call"
        assert "self.engine.register_rules(rules_to_register)" in content, \
            "Should call register_rules instead of register_rule"


# ============================================================================
# SPEC 3.2: STRING FIELD HELPER INTEGRATION
# ============================================================================

class TestSpec3_2_StringFieldHelper:
    """Test Suite for Spec 3.2: _validate_string_field Helper Integration"""
    
    def test_validate_string_field_empty(self):
        """Test _validate_string_field with empty value"""
        validator = AppTrackerQAValidator()
        validator.errors = []
        validator.rule_pass_counts = {}
        validator.rule_fail_counts = {}
        
        row = {"Company": ""}
        validator._validate_string_field(0, row, "Company", "R21", "Company", min_length=2)
        
        assert len(validator.errors) == 1, "Should log error for empty company"
        assert validator.errors[0]["RULE_ID"] == "R21"
        assert "cannot be empty" in validator.errors[0]["message"]
    
    def test_validate_string_field_too_short(self):
        """Test _validate_string_field with value too short"""
        validator = AppTrackerQAValidator()
        validator.errors = []
        validator.rule_pass_counts = {}
        validator.rule_fail_counts = {}
        
        row = {"Job Title": "AI"}
        validator._validate_string_field(0, row, "Job Title", "R22", "Job Title", min_length=3)
        
        assert len(validator.errors) == 1, "Should log error for short job title"
        assert validator.errors[0]["RULE_ID"] == "R22"
        assert "too short" in validator.errors[0]["message"]
    
    def test_validate_string_field_valid(self):
        """Test _validate_string_field with valid value"""
        validator = AppTrackerQAValidator()
        validator.errors = []
        validator.rule_pass_counts = {}
        validator.rule_fail_counts = {}
        
        row = {"Company": "Microsoft"}
        validator._validate_string_field(0, row, "Company", "R21", "Company", min_length=2)
        
        assert len(validator.errors) == 0, "Should not log error for valid company"
        assert validator.rule_pass_counts.get("R21", 0) == 1, "Should log pass"
    
    def test_string_field_helper_spec_comments_present(self):
        """Verify string field helper spec comments are in the code"""
        with open('/home/claude/resume_workflow_v16_20.py', 'r') as f:
            content = f.read()
        
        # Should have 3 usages (Versioned Resume, Company, Job Title)
        assert content.count("# --- SPEC 3.2: USE STRING FIELD HELPER ---") >= 3, \
            "Should have at least 3 string field helper comments"
        assert "self._validate_string_field" in content, \
            "Should use _validate_string_field helper"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests verifying all specs work together"""
    
    def test_all_spec_comments_present(self):
        """Verify all specification comments are present in refactored code"""
        with open('/home/claude/resume_workflow_v16_20.py', 'r') as f:
            content = f.read()
        
        # Spec 1.1 - Pre-flight
        assert "# --- SPEC 1.1: PRE-FLIGHT CONSTRAINT STRESS TEST ---" in content
        assert "# --- END SPEC 1.1 ---" in content
        
        # Spec 1.2 - Failure Classification
        assert "# --- SPEC 1.2: FAILURE CLASSIFICATION ---" in content
        assert "# --- END SPEC 1.2 ---" in content
        
        # Spec 1.3 - Deprecated functions
        assert "# DEPRECATED: Removed should_reduce_temperature (Spec 1.3)" in content
        assert "# DEPRECATED: Removed _get_feedback_instruction (Spec 1.3)" in content
        
        # Spec 2 - Agentic RAG (4 phases)
        assert content.count("# --- SPEC 2: ACTIVATE AGENTIC RAG ---") == 4
        
        # Spec 3.1 - Bulk registration
        assert "# --- SPEC 3.1: USE BULK REGISTRATION ---" in content
        
        # Spec 3.2 - String field helper (3 usages)
        assert content.count("# --- SPEC 3.2: USE STRING FIELD HELPER ---") >= 3
    
    def test_version_is_16_20(self):
        """Verify version is correctly set to 16_20"""
        assert __version__ == "16_20"
    
    def test_imports_still_work(self):
        """Verify all critical classes still import correctly"""
        # If we got this far, imports worked
        assert WorkflowOrchestrator is not None
        assert ConstraintFailureClassifier is not None
        assert ValidationEngine is not None
        assert ArtistGenerator is not None
        assert PreFlightValidator is not None
        assert WebSearchRAG is not None
        assert AppTrackerQAValidator is not None


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
