"""
Test Suite for Resume_Generation_v15_64.py
Tests HOP-3 "No Cost/Time Tradeoffs" Enhancement

Focus Areas:
1. Enhanced temperature progression (1.0 -> 0.8 -> 0.6 -> 0.4 -> 0.2)
2. ConstraintFailureClassifier functionality
3. Progressive constraint reinforcement
4. Mechanical word count fixes (zero-cost)
5. Pre-flight constraint testing
6. Retry logic for HIGH/CRITICAL QA rules (5 attempts)
7. Word count validation with multiple attempts
8. Error handling and logging
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, List, Tuple
import sys
import os

# Mock genai before import
sys.modules['google.generativeai'] = MagicMock()

# Import after mocking
from Resume_Generation_v15_64 import (
    ArtistGenerator, TextUtils, ReasoningConfig, BulletProvenance,
    HopExecutionError, text_utils, ConstraintFailureClassifier,
    ValidationResult, ValidationSeverity, ResumeSection
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_master_resume():
    """Mock master resume data"""
    return {
        "experience": [
            {
                "company": "TechCorp",
                "role": "Senior Engineer",
                "bullets": ["Sample bullet point"]
            }
        ]
    }

@pytest.fixture
def mock_enriched_scaffold():
    """Mock enriched scaffold"""
    return {
        "K2_UNIFY_BULLETS": {
            "selected_bullets": []
        }
    }

@pytest.fixture
def mock_thematic_analysis():
    """Mock thematic analysis"""
    return Mock()

@pytest.fixture
def mock_artist_specs():
    """Mock artist specs"""
    return {
        "K2_UNIFY_BULLETS": {
            "reasoning_config": "DEFAULT",
            "system_prompt": "Test prompt"
        }
    }

@pytest.fixture
def artist(mock_master_resume, mock_enriched_scaffold, mock_thematic_analysis, mock_artist_specs):
    """Create an ArtistGenerator instance for testing"""
    with patch('Resume_Generation_v15_64.ReasoningConfig.DEFAULT', Mock()):
        return ArtistGenerator(
            master_resume=mock_master_resume,
            enriched_scaffold=mock_enriched_scaffold,
            job_description="Test job description",
            thematic_analysis=mock_thematic_analysis,
            artist_specs=mock_artist_specs
        )

@pytest.fixture
def sample_bullets():
    """Sample bullet data for testing"""
    return [
        {
            "text": "Led cross-functional team of 15 engineers to deliver cloud migration project 3 months ahead of schedule, reducing infrastructure costs by 40% while improving system reliability to 99.99% uptime.",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 28
        },
        {
            "text": "Short bullet with only ten words here.",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 7
        },
        {
            "text": "This is an extremely long bullet point that exceeds the maximum word count threshold and should trigger a rewrite operation to bring it down to an acceptable range for resume formatting standards and best practices.",
            "provenance": BulletProvenance.Synthetic.value,
            "word_count": 38
        }
    ]

@pytest.fixture
def mock_api_response():
    """Create a mock API response"""
    mock_response = Mock()
    mock_response.text = "Revised bullet point with exactly thirty words to meet the target range while maintaining the core message and preserving all key metrics for professional resume standards."
    mock_response.candidates = [Mock()]
    mock_response.candidates[0].finish_reason = 1  # STOP
    mock_response.candidates[0].content.parts = [Mock()]
    mock_response.candidates[0].content.parts[0].text = mock_response.text
    return mock_response

# ============================================================================
# TEST: ConstraintFailureClassifier (NEW in v15_64)
# ============================================================================

class TestConstraintFailureClassifier:
    """Test the new ConstraintFailureClassifier functionality"""
    
    def test_classify_mechanical_failure(self):
        """Test classification of mechanical failures"""
        result = ValidationResult(
            rule_id="H3_GLOBAL_BULLET_WORD_COUNT_RANGE",
            passed=False,
            severity=ValidationSeverity.HIGH,
            message="Word count out of range"
        )
        
        category = ConstraintFailureClassifier.classify_failure(result, 1.0)
        assert category == "MECHANICAL"
    
    def test_classify_creative_failure(self):
        """Test classification of creative failures"""
        result = ValidationResult(
            rule_id="H3_CONTENT_NO_PLACEHOLDER_TEXT",
            passed=False,
            severity=ValidationSeverity.CRITICAL,
            message="Contains placeholder"
        )
        
        category = ConstraintFailureClassifier.classify_failure(result, 1.0)
        assert category == "CREATIVE"
    
    def test_classify_semantic_failure(self):
        """Test classification of semantic failures"""
        result = ValidationResult(
            rule_id="H3_GLOBAL_CONTENT_NO_FORBIDDEN_VERBS",
            passed=False,
            severity=ValidationSeverity.HIGH,
            message="Contains forbidden verb"
        )
        
        category = ConstraintFailureClassifier.classify_failure(result, 1.0)
        assert category == "SEMANTIC"
    
    def test_classify_conflict_failure(self):
        """Test classification of impossible constraint conflicts"""
        result = ValidationResult(
            rule_id="SOME_CUSTOM_RULE",
            passed=False,
            severity=ValidationSeverity.CRITICAL,
            message="Failed at low temperature"
        )
        
        # At low temperature (0.3), persistent failure indicates conflict
        category = ConstraintFailureClassifier.classify_failure(result, 0.3)
        assert category == "CONFLICT"
    
    def test_should_reduce_temperature_mechanical(self):
        """Test that mechanical failures suggest temperature reduction"""
        failure_counts = {
            "MECHANICAL": 5,
            "CREATIVE": 1,
            "SEMANTIC": 1
        }
        
        assert ConstraintFailureClassifier.should_reduce_temperature(failure_counts) is True
    
    def test_should_not_reduce_temperature_creative(self):
        """Test that creative failures suggest keeping temperature high"""
        failure_counts = {
            "MECHANICAL": 1,
            "CREATIVE": 5,
            "SEMANTIC": 1
        }
        
        assert ConstraintFailureClassifier.should_reduce_temperature(failure_counts) is False

# ============================================================================
# TEST: Enhanced Temperature Schedule (v15_64)
# ============================================================================

class TestEnhancedTemperatureSchedule:
    """Test the enhanced 5-attempt temperature schedule"""
    
    def test_temperature_schedule_default(self, artist):
        """Test that temperature schedule is [1.0, 0.8, 0.6, 0.4, 0.2] by default"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            # Simulate failures until last attempt
            mock_api.side_effect = [
                ("Twenty five word bullet that fails validation check here now", 7),  # Too short
                ("Still too short at twenty words only", 8),  # Too short
                ("Getting closer with twenty five words here", 9),  # Too short
                ("Almost there with twenty eight words now", 10),  # Too short
                ("Finally a bullet with exactly thirty words to meet target range while preserving metrics and maintaining professional tone for resume standards excellence.", 20)  # Success
            ]
            
            original_bullet = "Original bullet text here."
            target_range = (28, 38)
            
            # Mock mechanical fix to return original (no fix)
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = original_bullet
                
                result, calls = artist._rewrite_bullet_for_word_count(
                    original_bullet, target_range, "TEST_SECTION", max_retries=5
                )
            
            # Verify 5 attempts were made
            assert mock_api.call_count == 5
            
            # Extract temperature from each call
            temps_used = [call_args.kwargs.get('temperature_override') 
                         for call_args in mock_api.call_args_list]
            
            # Verify enhanced temperature progression: 1.0 -> 0.8 -> 0.6 -> 0.4 -> 0.2
            assert temps_used == [1.0, 0.8, 0.6, 0.4, 0.2]
    
    def test_temperature_schedule_with_override(self, artist):
        """Test temperature schedule when override is provided"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Short", 1),  # Fail
                ("Still short", 2),  # Fail
                ("Led cross-functional team of engineers to deliver cloud migration project ahead of schedule reducing infrastructure costs by percentage while improving system reliability uptime metrics overall.", 25)  # Success
            ]
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Short"
                
                result, calls = artist._rewrite_bullet_for_word_count(
                    "Original bullet", (28, 38), "TEST", 
                    temperature_override=0.9, max_retries=5
                )
            
            # With override=0.9, schedule should start at 0.9
            temps_used = [call_args.kwargs.get('temperature_override') 
                         for call_args in mock_api.call_args_list]
            assert temps_used[0] == 0.9
            assert temps_used[1] == 0.8  # Then continue with standard schedule

# ============================================================================
# TEST: Mechanical Word Count Fix (NEW in v15_64)
# ============================================================================

class TestMechanicalWordCountFix:
    """Test zero-cost mechanical word count fixes"""
    
    def test_mechanical_fix_expansion(self, artist):
        """Test mechanical expansion for short text"""
        text = "Led team w/ 10 engineers & delivered project."
        result = artist._mechanical_word_count_fix(text, 10, 20)
        
        # Should expand "w/" to "with" and "&" to "and"
        assert "with" in result
        assert "and" in result
        assert "w/" not in result
        assert "&" not in result
    
    def test_mechanical_fix_contraction(self, artist):
        """Test mechanical contraction for long text"""
        text = "Led very really quite actually basically team effectively."
        result = artist._mechanical_word_count_fix(text, 1, 5)
        
        # Should remove filler words
        original_count = text_utils.count_words_ms_word_style(text)
        result_count = text_utils.count_words_ms_word_style(result)
        assert result_count < original_count
    
    def test_mechanical_fix_already_compliant(self, artist):
        """Test that compliant text is not modified"""
        text = "This text has exactly ten words here now today."
        word_count = text_utils.count_words_ms_word_style(text)
        result = artist._mechanical_word_count_fix(text, word_count, word_count)
        
        # Should return unchanged
        assert result == text
    
    def test_mechanical_fix_returns_original_if_cant_fix(self, artist):
        """Test that original is returned if mechanical fix is insufficient"""
        text = "Short"
        result = artist._mechanical_word_count_fix(text, 20, 30)
        
        # Can't mechanically fix this, should return original
        assert result == text
    
    def test_rewrite_uses_mechanical_fix_first(self, artist):
        """Test that mechanical fix is attempted before LLM calls"""
        original_bullet = "Led team w/ engineers & delivered project successfully overall."
        target_range = (8, 12)
        
        with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
            # Mock mechanical fix succeeding
            mock_mech.return_value = "Led team with engineers and delivered project successfully overall."
            
            with patch.object(artist, '_call_gemini_api') as mock_api:
                result, calls = artist._rewrite_bullet_for_word_count(
                    original_bullet, target_range, "TEST", max_retries=5
                )
                
                # Should have tried mechanical fix
                assert mock_mech.call_count == 1
                
                # If mechanical fix succeeded, no API calls should be made
                if text_utils.count_words_ms_word_style(result) in range(target_range[0], target_range[1] + 1):
                    assert calls == 0

# ============================================================================
# TEST: Progressive Constraint Reinforcement (NEW in v15_64)
# ============================================================================

class TestProgressiveConstraintReinforcement:
    """Test progressive constraint reinforcement across attempts"""
    
    def test_constraint_prompt_attempt_1(self, artist):
        """Test attempt 1 uses permissive constraint language"""
        base_prompt = "Generate bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        enhanced = artist._build_generation_prompt_with_reinforced_constraints(
            base_prompt, constraints, attempt_number=1
        )
        
        # Should contain basic constraints
        assert "CONSTRAINTS" in enhanced
        assert "28-38 words" in enhanced
        assert "verify before output" in enhanced
    
    def test_constraint_prompt_attempt_2(self, artist):
        """Test attempt 2 uses adversarial emphasis"""
        base_prompt = "Generate bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        enhanced = artist._build_generation_prompt_with_reinforced_constraints(
            base_prompt, constraints, attempt_number=2
        )
        
        # Should contain adversarial language
        assert "AUTOMATIC REJECTION" in enhanced
        assert "❌" in enhanced
        assert "✓" in enhanced
    
    def test_constraint_prompt_attempt_3(self, artist):
        """Test attempt 3 uses mechanical checklist"""
        base_prompt = "Generate bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        enhanced = artist._build_generation_prompt_with_reinforced_constraints(
            base_prompt, constraints, attempt_number=3
        )
        
        # Should contain checklist
        assert "VALIDATION CHECKLIST" in enhanced
        assert "[ ]" in enhanced
        assert "REGENERATE" in enhanced
    
    def test_constraint_prompt_attempt_4_plus(self, artist):
        """Test attempt 4+ uses algorithmic instructions"""
        base_prompt = "Generate bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        for attempt in [4, 5, 6]:
            enhanced = artist._build_generation_prompt_with_reinforced_constraints(
                base_prompt, constraints, attempt_number=attempt
            )
            
            # Should contain algorithmic steps
            assert "ALGORITHMIC" in enhanced
            assert "STEP 1" in enhanced
            assert "STEP 7" in enhanced

# ============================================================================
# TEST: Pre-flight Constraint Testing (NEW in v15_64)
# ============================================================================

class TestPreFlightConstraintTest:
    """Test constraint feasibility testing"""
    
    def test_preflight_test_feasible_constraints(self, artist):
        """Test that feasible constraints return True"""
        prompt = "Generate a bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.return_value = ("YES", 1)
            
            result = artist._pre_flight_constraint_test(
                ResumeSection.K2_UNIFY_BULLETS, prompt, constraints
            )
            
            assert result is True
    
    def test_preflight_test_infeasible_constraints(self, artist):
        """Test that infeasible constraints return False"""
        prompt = "Generate a bullet point."
        constraints = {"min_wc": 5, "max_wc": 10, "forbidden": "everything"}
        
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.return_value = ("NO: Word count too restrictive", 1)
            
            result = artist._pre_flight_constraint_test(
                ResumeSection.K2_UNIFY_BULLETS, prompt, constraints
            )
            
            assert result is False
    
    def test_preflight_test_error_handling(self, artist):
        """Test that pre-flight errors don't block generation"""
        prompt = "Generate a bullet point."
        constraints = {"min_wc": 28, "max_wc": 38}
        
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = Exception("API Error")
            
            # Should return True (don't block on test failure)
            result = artist._pre_flight_constraint_test(
                ResumeSection.K2_UNIFY_BULLETS, prompt, constraints
            )
            
            assert result is True

# ============================================================================
# TEST: TextUtils Word Counting
# ============================================================================

class TestTextUtils:
    """Test TextUtils word counting functionality"""
    
    def test_count_words_basic(self):
        """Test basic word counting"""
        assert text_utils.count_words_ms_word_style("Hello world") == 2
        assert text_utils.count_words_ms_word_style("One two three four five") == 5
    
    def test_count_words_with_punctuation(self):
        """Test word counting with punctuation"""
        text = "Led team of 10, delivered project 25% faster."
        assert text_utils.count_words_ms_word_style(text) == 8
    
    def test_count_words_empty(self):
        """Test word counting with empty string"""
        assert text_utils.count_words_ms_word_style("") == 0
        assert text_utils.count_words_ms_word_style(None) == 0
    
    def test_count_words_multiple_spaces(self):
        """Test word counting with multiple spaces"""
        text = "Word  with   multiple    spaces"
        assert text_utils.count_words_ms_word_style(text) == 4
    
    def test_count_sentences(self):
        """Test sentence counting"""
        text = "First sentence. Second sentence! Third sentence?"
        assert text_utils.count_sentences(text) == 3

# ============================================================================
# TEST: Enhanced Retry Logic
# ============================================================================

class TestEnhancedRetryLogic:
    """Test the enhanced retry mechanism with 5 attempts"""
    
    def test_success_on_first_attempt(self, artist):
        """Test that retry stops when first attempt succeeds"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.return_value = (
                "Led team of fifteen engineers delivering cloud migration project ahead schedule reducing costs forty percent improving reliability ninety nine uptime metrics.", 
                5
            )
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Original"  # Mechanical fix doesn't help
                
                result, calls = artist._rewrite_bullet_for_word_count(
                    "Original bullet", (28, 38), "TEST", max_retries=5
                )
            
            # Should only call API once
            assert mock_api.call_count == 1
            assert calls == 5
    
    def test_success_on_third_attempt(self, artist):
        """Test that retry stops when third attempt succeeds"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Too short bullet here", 4),  # Fail attempt 1
                ("Still short bullet", 5),  # Fail attempt 2
                ("Led cross-functional engineering team delivering cloud migration ahead schedule reducing infrastructure costs forty percent while improving system reliability metrics to ninety nine uptime.", 28)  # Success attempt 3
            ]
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Original"
                
                result, calls = artist._rewrite_bullet_for_word_count(
                    "Original", (28, 38), "TEST", max_retries=5
                )
            
            # Should call API three times
            assert mock_api.call_count == 3
            assert calls == 4 + 5 + 28
    
    def test_failure_after_all_attempts(self, artist):
        """Test that HopExecutionError is raised after exhausting all 5 attempts"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            # All attempts return too-short bullets
            mock_api.side_effect = [
                ("Short", 2),
                ("Short", 3),
                ("Short", 4),
                ("Short", 5),
                ("Short", 6)
            ]
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Short"
                
                with pytest.raises(HopExecutionError) as exc_info:
                    artist._rewrite_bullet_for_word_count(
                        "Original", (28, 38), "TEST", max_retries=5
                    )
            
            assert "failed after 5 attempts" in str(exc_info.value)
            assert mock_api.call_count == 5

# ============================================================================
# TEST: Validation and Rewrite Integration
# ============================================================================

class TestValidationRewriteIntegration:
    """Test _validate_and_potentially_rewrite_bullets with v15_64 enhancements"""
    
    def test_validate_calls_rewrite_with_max_retries_5(self, artist):
        """Test that validation calls rewrite with max_retries=5"""
        bullets = [{
            "text": "Short bullet",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 2
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (" ".join(["word"] * 30), 15)
            
            result, calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST"
            )
            
            # Verify max_retries=5 was passed
            mock_rewrite.assert_called_once()
            call_kwargs = mock_rewrite.call_args[1]
            assert call_kwargs.get('max_retries') == 5
    
    def test_validate_logs_enhanced_temperature_schedule(self, artist, caplog):
        """Test that validation logs mention enhanced temperature schedule"""
        bullets = [{
            "text": "Short",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 1
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (" ".join(["word"] * 30), 15)
            
            with caplog.at_level(logging.WARNING):
                artist._validate_and_potentially_rewrite_bullets(
                    bullets, 28, 38, "TEST"
                )
            
            # Check for enhanced schedule in logs
            assert any("1.0→0.8→0.6→0.4→0.2" in record.message for record in caplog.records)

# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_word_count_at_minimum_boundary(self, artist):
        """Test bullet exactly at minimum word count"""
        bullets = [{
            "text": " ".join(["word"] * 28),  # Exactly 28 words
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 28
        }]
        
        result, calls = artist._validate_and_potentially_rewrite_bullets(
            bullets, 28, 38, "TEST_MIN"
        )
        
        assert len(result) == 1
        assert calls == 0  # No rewrite needed
    
    def test_word_count_at_maximum_boundary(self, artist):
        """Test bullet exactly at maximum word count"""
        bullets = [{
            "text": " ".join(["word"] * 38),  # Exactly 38 words
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 38
        }]
        
        result, calls = artist._validate_and_potentially_rewrite_bullets(
            bullets, 28, 38, "TEST_MAX"
        )
        
        assert len(result) == 1
        assert calls == 0  # No rewrite needed
    
    def test_mechanical_fix_success_zero_api_calls(self, artist):
        """Test that successful mechanical fix results in zero API calls"""
        bullets = [{
            "text": "Led team w/ engineers & delivered project.",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 6
        }]
        
        with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
            # Mock successful mechanical fix
            fixed_text = " ".join(["word"] * 30)
            mock_mech.return_value = fixed_text
            
            with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
                # Ensure the mock returns the mechanically fixed text with 0 calls
                mock_rewrite.return_value = (fixed_text, 0)
                
                result, calls = artist._validate_and_potentially_rewrite_bullets(
                    bullets, 28, 38, "TEST"
                )
                
                # Mechanical fix was attempted
                assert mock_mech.call_count >= 1

# ============================================================================
# TEST: Logging Verification
# ============================================================================

class TestLogging:
    """Test that proper logging occurs"""
    
    def test_logging_mechanical_fix_attempt(self, artist, caplog):
        """Test that mechanical fix attempts are logged"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.return_value = (" ".join(["word"] * 30), 5)
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Original"
                
                with caplog.at_level(logging.INFO):
                    artist._rewrite_bullet_for_word_count(
                        "Original", (28, 38), "TEST_LOG", max_retries=5
                    )
        
        # Check that mechanical fix was logged
        assert any("mechanical" in record.message.lower() for record in caplog.records)
    
    def test_logging_enhanced_temperature_info(self, artist, caplog):
        """Test that enhanced temperature information is logged"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Short", 2),
                ("Short", 3),
                ("Led engineering team delivering cloud migration ahead schedule reducing costs significantly while improving reliability metrics overall performance uptime standards excellence effectively.", 5)
            ]
            
            with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
                mock_mech.return_value = "Short"
                
                with caplog.at_level(logging.INFO):
                    artist._rewrite_bullet_for_word_count(
                        "Original", (28, 38), "TEST_LOG", max_retries=5
                    )
        
        # Check for all temperature values in logs
        log_text = " ".join(record.message for record in caplog.records)
        assert "Temp: 1.0" in log_text
        assert "Temp: 0.8" in log_text

# ============================================================================
# TEST: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic end-to-end scenarios"""
    
    def test_realistic_resume_bullet_batch_with_mechanical_fixes(self, artist):
        """Test processing a realistic batch with mechanical fixes"""
        bullets = [
            {"text": " ".join(["word"] * 30), "provenance": "Verbatim", "word_count": 30},
            {"text": "Led team w/ engineers & delivered.", "provenance": "Verbatim", "word_count": 5},
            {"text": " ".join(["word"] * 35), "provenance": "Synthetic", "word_count": 35},
        ]
        
        with patch.object(artist, '_mechanical_word_count_fix') as mock_mech:
            # First call: no fix needed
            # Second call: successful mechanical fix
            # Third call: no fix needed
            mock_mech.side_effect = [
                " ".join(["word"] * 30),  # Already compliant
                " ".join(["word"] * 29),  # Mechanically fixed
                " ".join(["word"] * 35),  # Already compliant
            ]
            
            with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
                mock_rewrite.return_value = (" ".join(["word"] * 32), 8)
                
                result, total_calls = artist._validate_and_potentially_rewrite_bullets(
                    bullets, 28, 38, "INTEGRATION_TEST"
                )
        
        assert len(result) == 3

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
