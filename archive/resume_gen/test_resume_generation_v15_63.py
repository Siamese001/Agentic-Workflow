"""
Test Suite for Resume_Generation_v15_63.py
Tests the critical fix: Temperature-based retry for bullet word count validation

Focus Areas:
1. Temperature progression (1.0 -> 0.7 -> 0.4)
2. Retry logic for HIGH/CRITICAL QA rules
3. Word count validation with multiple attempts
4. Error handling and logging
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
from Resume_Generation_v15_63 import (
    Artist, TextUtils, ReasoningConfig, BulletProvenance,
    HopExecutionError, text_utils
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def artist():
    """Create an Artist instance for testing"""
    return Artist(workflow_id="test_workflow_123")

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
# TEST: Temperature-Based Retry Logic
# ============================================================================

class TestTemperatureRetry:
    """Test the core temperature-based retry mechanism"""
    
    def test_temperature_schedule_default(self, artist):
        """Test that temperature schedule is [1.0, 0.7, 0.4] by default"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            # Simulate failures on attempts 1 and 2, success on attempt 3
            mock_api.side_effect = [
                ("Twenty five word bullet that fails validation check", 7),  # Too short
                ("Still too short at fifteen words only here", 8),  # Too short
                ("Finally a bullet with exactly thirty words to meet target range while preserving metrics and maintaining professional tone for resume standards.", 20)  # Success
            ]
            
            original_bullet = "Original bullet text here."
            target_range = (28, 38)
            
            result, calls = artist._rewrite_bullet_for_word_count(
                original_bullet, target_range, "TEST_SECTION", max_retries=3
            )
            
            # Verify 3 attempts were made
            assert mock_api.call_count == 3
            
            # Extract temperature from each call
            temps_used = [call_args.kwargs.get('temperature_override') 
                         for call_args in mock_api.call_args_list]
            
            # Verify temperature progression: 1.0 -> 0.7 -> 0.4
            assert temps_used == [1.0, 0.7, 0.4]
    
    def test_temperature_schedule_with_override(self, artist):
        """Test temperature schedule when override is provided"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Short", 1),  # Fail
                ("Still short", 2),  # Fail
                ("Led cross-functional team of engineers to deliver cloud migration project ahead of schedule reducing infrastructure costs by percentage while improving system reliability uptime metrics overall performance.", 25)  # Success
            ]
            
            result, calls = artist._rewrite_bullet_for_word_count(
                "Original bullet", (28, 38), "TEST", 
                temperature_override=0.8, max_retries=3
            )
            
            # With override=0.8, schedule should be [0.8, 0.7, 0.4]
            temps_used = [call_args.kwargs.get('temperature_override') 
                         for call_args in mock_api.call_args_list]
            assert temps_used == [0.8, 0.7, 0.4]
    
    def test_success_on_first_attempt(self, artist):
        """Test that retry stops when first attempt succeeds"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            # Return valid bullet on first attempt
            mock_api.return_value = (
                "Led team of fifteen engineers delivering cloud migration project ahead schedule reducing costs forty percent improving reliability ninety nine uptime metrics.", 
                5
            )
            
            result, calls = artist._rewrite_bullet_for_word_count(
                "Original bullet", (28, 38), "TEST", max_retries=3
            )
            
            # Should only call API once
            assert mock_api.call_count == 1
            assert calls == 5  # API made 5 internal calls
    
    def test_success_on_second_attempt(self, artist):
        """Test that retry stops when second attempt succeeds"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Too short bullet here", 4),  # Fail attempt 1
                ("Led cross-functional engineering team delivering cloud migration ahead schedule reducing infrastructure costs forty percent while improving system reliability metrics to ninety nine point nine nine uptime.", 28)  # Success attempt 2
            ]
            
            result, calls = artist._rewrite_bullet_for_word_count(
                "Original", (28, 38), "TEST", max_retries=3
            )
            
            # Should call API twice
            assert mock_api.call_count == 2
            assert calls == 4 + 28  # Sum of both call counts
    
    def test_all_attempts_fail(self, artist):
        """Test that HopExecutionError is raised when all attempts fail"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            # All attempts return bullets that are too short
            mock_api.side_effect = [
                ("Short", 2),
                ("Still short", 3),
                ("Way too short", 4)
            ]
            
            with pytest.raises(HopExecutionError) as exc_info:
                artist._rewrite_bullet_for_word_count(
                    "Original", (28, 38), "TEST_FAIL", max_retries=3
                )
            
            # Verify error message contains details
            assert "failed after 3 attempts" in str(exc_info.value)
            assert "Temperature schedule" in str(exc_info.value)
            assert mock_api.call_count == 3

# ============================================================================
# TEST: Word Count Validation
# ============================================================================

class TestWordCountValidation:
    """Test word count validation and rewrite logic"""
    
    def test_validate_bullets_all_valid(self, artist, sample_bullets):
        """Test validation when all bullets are within range"""
        # First bullet is 28 words (valid for 28-38 range)
        bullets = [sample_bullets[0]]
        
        result, calls = artist._validate_and_potentially_rewrite_bullets(
            bullets, 28, 38, "TEST_VALID"
        )
        
        assert len(result) == 1
        assert result[0]["text"] == bullets[0]["text"]
        assert calls == 0  # No rewrite calls needed
    
    def test_validate_bullets_one_needs_rewrite(self, artist, sample_bullets):
        """Test validation when one bullet needs rewriting"""
        # Second bullet is 7 words (too short for 28-38 range)
        bullets = [sample_bullets[0], sample_bullets[1]]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (
                "Led diverse engineering team delivering cloud infrastructure migration ahead of schedule reducing costs significantly while improving reliability metrics performance uptime standards excellence.", 
                10  # 10 API calls made
            )
            
            result, calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_REWRITE"
            )
            
            assert len(result) == 2
            # First bullet should be unchanged
            assert result[0]["text"] == bullets[0]["text"]
            # Second bullet should be rewritten
            assert result[1]["text"] != bullets[1]["text"]
            assert calls == 10  # Rewrite made 10 calls
    
    def test_validate_bullets_multiple_need_rewrite(self, artist, sample_bullets):
        """Test validation when multiple bullets need rewriting"""
        # Use bullets that are outside the 28-38 word range
        bullets = [sample_bullets[1], sample_bullets[2]]  # 7 words and 38 words
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            # Return different rewrites for each bullet
            mock_rewrite.side_effect = [
                ("First rewritten bullet with thirty words meeting target range preserving metrics maintaining professional tone for resume standards while demonstrating achievements clearly effectively.", 8),
                ("Second rewritten bullet with thirty words meeting target range preserving metrics maintaining professional tone for resume standards while demonstrating achievements clearly effectively.", 12)
            ]
            
            result, calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_MULTIPLE"
            )
            
            assert len(result) == 2
            assert mock_rewrite.call_count == 2
            assert calls == 8 + 12  # Total calls from both rewrites
    
    def test_validate_bullets_rewrite_fails(self, artist, sample_bullets):
        """Test that HopExecutionError is raised when rewrite fails"""
        bullets = [sample_bullets[1]]  # 7 words, too short
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.side_effect = HopExecutionError("Rewrite failed after 3 attempts")
            
            with pytest.raises(HopExecutionError) as exc_info:
                artist._validate_and_potentially_rewrite_bullets(
                    bullets, 28, 38, "TEST_FAIL"
                )
            
            assert "Bullet WC correction failed" in str(exc_info.value)
    
    def test_validate_bullets_empty_text(self, artist):
        """Test that empty bullet text raises error"""
        bullets = [{"text": "", "provenance": "Verbatim", "word_count": 0}]
        
        with pytest.raises(HopExecutionError) as exc_info:
            artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_EMPTY"
            )
        
        assert "Empty bullet" in str(exc_info.value)
    
    def test_validate_bullets_invalid_structure(self, artist):
        """Test that invalid bullet structure raises error"""
        bullets = ["not a dict"]
        
        with pytest.raises(HopExecutionError) as exc_info:
            artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_INVALID"
            )
        
        assert "Invalid item in bullet list" in str(exc_info.value)

# ============================================================================
# TEST: Provenance Tracking
# ============================================================================

class TestProvenanceTracking:
    """Test bullet provenance tracking through rewrites"""
    
    def test_verbatim_becomes_customized_after_rewrite(self, artist):
        """Test that Verbatim bullets become Customized after rewrite"""
        bullets = [{
            "text": "Short",
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 1
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (
                "Led engineering team delivering cloud migration ahead schedule reducing costs significantly while improving reliability metrics overall performance uptime standards excellence effectively.", 
                5
            )
            
            result, _ = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_PROV"
            )
            
            assert result[0]["provenance"] == BulletProvenance.Customized.value
            assert "original_text_if_rewritten" in result[0]
    
    def test_synthetic_stays_synthetic_after_rewrite(self, artist):
        """Test that Synthetic bullets stay Synthetic after rewrite"""
        bullets = [{
            "text": "Short",
            "provenance": BulletProvenance.Synthetic.value,
            "word_count": 1
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (
                "Led engineering team delivering cloud migration ahead schedule reducing costs significantly while improving reliability metrics overall performance uptime standards excellence effectively.", 
                5
            )
            
            result, _ = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_PROV"
            )
            
            assert result[0]["provenance"] == BulletProvenance.Synthetic.value
    
    def test_customized_stays_customized_after_rewrite(self, artist):
        """Test that Customized bullets stay Customized after rewrite"""
        bullets = [{
            "text": "Short",
            "provenance": BulletProvenance.Customized.value,
            "word_count": 1
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (
                "Led engineering team delivering cloud migration ahead schedule reducing costs significantly while improving reliability metrics overall performance uptime standards excellence effectively.", 
                5
            )
            
            result, _ = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_PROV"
            )
            
            assert result[0]["provenance"] == BulletProvenance.Customized.value

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
    
    def test_word_count_one_below_minimum(self, artist):
        """Test bullet one word below minimum"""
        bullets = [{
            "text": " ".join(["word"] * 27),  # 27 words (1 below min)
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 27
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (" ".join(["word"] * 28), 5)
            
            result, calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_BELOW"
            )
            
            assert mock_rewrite.call_count == 1  # Should trigger rewrite
    
    def test_word_count_one_above_maximum(self, artist):
        """Test bullet one word above maximum"""
        bullets = [{
            "text": " ".join(["word"] * 39),  # 39 words (1 above max)
            "provenance": BulletProvenance.Verbatim.value,
            "word_count": 39
        }]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (" ".join(["word"] * 38), 5)
            
            result, calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "TEST_ABOVE"
            )
            
            assert mock_rewrite.call_count == 1  # Should trigger rewrite
    
    def test_max_retries_parameter(self, artist):
        """Test that max_retries parameter is respected"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Short", 2),
                ("Short", 3),
                ("Short", 4),
                ("Short", 5),
                ("Short", 6)
            ]
            
            # Test with max_retries=5
            with pytest.raises(HopExecutionError):
                artist._rewrite_bullet_for_word_count(
                    "Original", (28, 38), "TEST", max_retries=5
                )
            
            assert mock_api.call_count == 5

# ============================================================================
# TEST: Logging Verification
# ============================================================================

class TestLogging:
    """Test that proper logging occurs"""
    
    def test_logging_temperature_info(self, artist, caplog):
        """Test that temperature information is logged"""
        with patch.object(artist, '_call_gemini_api') as mock_api:
            mock_api.side_effect = [
                ("Short", 2),
                ("Led engineering team delivering cloud migration ahead schedule reducing costs significantly while improving reliability metrics overall performance uptime standards excellence effectively.", 5)
            ]
            
            with caplog.at_level(logging.INFO):
                artist._rewrite_bullet_for_word_count(
                    "Original", (28, 38), "TEST_LOG", max_retries=3
                )
            
            # Check that temperature info was logged
            assert any("Temp: 1.0" in record.message for record in caplog.records)
            assert any("Temp: 0.7" in record.message for record in caplog.records)
    
    def test_logging_rewrite_success(self, artist, caplog):
        """Test that successful rewrites are logged"""
        bullets = [{"text": "Short", "provenance": "Verbatim", "word_count": 1}]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.return_value = (" ".join(["word"] * 30), 5)
            
            with caplog.at_level(logging.INFO):
                artist._validate_and_potentially_rewrite_bullets(
                    bullets, 28, 38, "TEST_LOG"
                )
            
            assert any("Rewrite SUCCESS" in record.message for record in caplog.records)
    
    def test_logging_rewrite_failure(self, artist, caplog):
        """Test that failed rewrites are logged"""
        bullets = [{"text": "Short", "provenance": "Verbatim", "word_count": 1}]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            mock_rewrite.side_effect = HopExecutionError("Failed")
            
            with caplog.at_level(logging.ERROR):
                with pytest.raises(HopExecutionError):
                    artist._validate_and_potentially_rewrite_bullets(
                        bullets, 28, 38, "TEST_LOG"
                    )
            
            assert any("Rewrite FAILED" in record.message for record in caplog.records)

# ============================================================================
# TEST: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic end-to-end scenarios"""
    
    def test_realistic_resume_bullet_batch(self, artist):
        """Test processing a realistic batch of resume bullets"""
        bullets = [
            {"text": " ".join(["word"] * 30), "provenance": "Verbatim", "word_count": 30},
            {"text": " ".join(["word"] * 10), "provenance": "Verbatim", "word_count": 10},
            {"text": " ".join(["word"] * 35), "provenance": "Synthetic", "word_count": 35},
            {"text": " ".join(["word"] * 50), "provenance": "Customized", "word_count": 50},
        ]
        
        with patch.object(artist, '_rewrite_bullet_for_word_count') as mock_rewrite:
            # Return valid bullets for rewrites
            mock_rewrite.return_value = (" ".join(["word"] * 32), 8)
            
            result, total_calls = artist._validate_and_potentially_rewrite_bullets(
                bullets, 28, 38, "INTEGRATION_TEST"
            )
            
            assert len(result) == 4
            # First bullet is valid, should not be rewritten
            assert result[0]["word_count"] == 30
            # Second bullet is too short, should be rewritten
            assert result[1]["word_count"] == 32
            # Third bullet is valid, should not be rewritten
            assert result[2]["word_count"] == 35
            # Fourth bullet is too long, should be rewritten
            assert result[3]["word_count"] == 32
            
            # Should have called rewrite twice (for bullets 2 and 4)
            assert mock_rewrite.call_count == 2
            assert total_calls == 16  # 8 calls × 2 rewrites

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
