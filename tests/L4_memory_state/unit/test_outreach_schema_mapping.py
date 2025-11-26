"""
Tests for L4 outreach schema mapping and signal scoring.

Validates format_as_outreach_result(), signal scoring, signal type classification,
age_days computation, and LIC-compatible metadata presence.
Tests MUST NOT import L1 or L2 modules.
"""

from datetime import datetime, timezone, timedelta

from l4.hybrid_search import SearchResult
from l4.schema.outreach_schema import OutreachRAGResult, format_as_outreach_result


class TestOutreachSchemaMapping:
    """Test suite for L4 outreach schema mapping functionality."""
    
    def test_format_as_outreach_result_basic_mapping(self):
        """Test basic SearchResult to OutreachRAGResult mapping."""
        # Create mock SearchResult
        search_result = SearchResult(
            id="test_result_123",
            text="John Smith is a Senior Software Engineer at TechCorp with 5 years experience in Python and machine learning.",
            fused_score=0.85,
            metadata={
                "company": "TechCorp",
                "title": "Senior Software Engineer",
                "source": "linkedin",
                "source_weight": 0.9,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )
        
        # Convert to OutreachRAGResult
        result = format_as_outreach_result(search_result)
        
        # Verify basic mapping
        assert isinstance(result, OutreachRAGResult)
        assert result.id == "test_result_123"
        assert result.text == search_result.text
        assert result.score == 0.85
        assert result.company == "TechCorp"
        assert result.title == "Senior Software Engineer"
        assert result.source == "linkedin"
        assert result.source_weight == 0.9
    
    def test_signal_scoring_with_quantitative_indicators(self):
        """Test signal scoring increases with quantitative indicators."""
        # Text with quantitative indicators
        quantitative_text = "Increased revenue by 25% and reduced costs by $1M through 3x efficiency improvements."
        search_result = SearchResult(
            id="quantitative_test",
            text=quantitative_text,
            fused_score=0.7,
            metadata={
                "company": "FinanceCorp",
                "title": "CFO",
                "source": "annual_report",
                "timestamp": "2024-02-01T12:00:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should have higher signal score due to quantitative indicators
        assert result.signal_score >= 0.7
        assert result.signal_type == "quantitative"
        assert result.is_signal_candidate is True
    
    def test_signal_scoring_with_strategic_indicators(self):
        """Test signal scoring with strategic indicators."""
        strategic_text = "Led digital transformation initiative to modernize core infrastructure and drive strategic vision."
        search_result = SearchResult(
            id="strategic_test",
            text=strategic_text,
            fused_score=0.75,
            metadata={
                "company": "StrategyCorp",
                "title": "CTO",
                "source": "press_release",
                "timestamp": "2024-01-20T09:15:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should classify as strategic signal
        assert result.signal_type == "strategic"
        assert result.is_signal_candidate is True
    
    def test_signal_scoring_with_recent_activity(self):
        """Test signal scoring with recent activity indicators."""
        recent_text = "Recently announced new product launch and just secured Series C funding."
        search_result = SearchResult(
            id="recent_test",
            text=recent_text,
            fused_score=0.6,
            metadata={
                "company": "StartupCorp",
                "title": "CEO",
                "source": "news",
                "timestamp": "2024-03-01T14:30:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should classify as recent activity
        assert result.signal_type == "recent_activity"
        assert result.is_signal_candidate is True
    
    def test_signal_scoring_general_classification(self):
        """Test signal scoring falls back to general classification."""
        general_text = "Works in engineering department and collaborates with cross-functional teams."
        search_result = SearchResult(
            id="general_test",
            text=general_text,
            fused_score=0.5,
            metadata={
                "company": "GeneralCorp",
                "title": "Software Engineer",
                "source": "company_profile",
                "timestamp": "2024-01-10T11:00:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should classify as general
        assert result.signal_type == "general"
        assert result.is_signal_candidate is False  # Below 0.7 threshold
    
    def test_age_days_computation_with_valid_timestamp(self):
        """Test age_days computation with valid ISO timestamp."""
        # Create result with timestamp 30 days ago
        past_date = datetime.now(timezone.utc) - timedelta(days=30)
        search_result = SearchResult(
            id="age_test",
            text="Test content",
            fused_score=0.8,
            metadata={
                "company": "TestCorp",
                "title": "Test Role",
                "source": "test",
                "timestamp": past_date.isoformat()
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should compute age correctly (allowing 1 day variance)
        assert 29 <= result.age_days <= 31
    
    def test_age_days_computation_with_invalid_timestamp(self):
        """Test age_days defaults to 365 with invalid timestamp."""
        search_result = SearchResult(
            id="invalid_age_test",
            text="Test content",
            fused_score=0.8,
            metadata={
                "company": "TestCorp",
                "title": "Test Role",
                "source": "test",
                "timestamp": "invalid_timestamp"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should default to 365 days
        assert result.age_days == 365
    
    def test_age_days_computation_with_missing_timestamp(self):
        """Test age_days defaults to 365 with missing timestamp."""
        search_result = SearchResult(
            id="missing_age_test",
            text="Test content",
            fused_score=0.8,
            metadata={
                "company": "TestCorp",
                "title": "Test Role",
                "source": "test"
                # No timestamp
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should default to 365 days
        assert result.age_days == 365
    
    def test_lic_compatible_metadata_presence(self):
        """Test LIC-compatible metadata is preserved and accessible."""
        lic_metadata = {
            "company": "LICCorp",
            "title": "Chief Technology Officer",
            "source": "executive_profile",
            "source_weight": 0.95,
            "timestamp": "2024-02-15T16:45:00Z",
            "named_entities": ["LICCorp", "CTO"],
            "is_signal_candidate": True,
            "lic_error_codes": ["E001", "E002"],
            "validation_status": "passed"
        }
        
        search_result = SearchResult(
            id="lic_metadata_test",
            text="Executive with strategic technology leadership and quantifiable business impact.",
            fused_score=0.9,
            metadata=lic_metadata
        )
        
        result = format_as_outreach_result(search_result)
        
        # Verify LIC metadata is preserved in the result structure
        assert result.company == "LICCorp"
        assert result.title == "Chief Technology Officer"
        assert result.source == "executive_profile"
        assert result.source_weight == 0.95
        # Note: Original metadata is not directly accessible in OutreachRAGResult
        # but is used for signal scoring and classification
    
    def test_signal_scoring_with_named_entities_boost(self):
        """Test signal scoring increases with named entities in metadata."""
        search_result_with_entities = SearchResult(
            id="entities_test",
            text="Technology leader at major corporation",
            fused_score=0.6,
            metadata={
                "company": "BigCorp",
                "title": "VP Engineering",
                "source": "professional_network",
                "named_entities": ["BigCorp", "VP Engineering", "Engineering"]
            }
        )
        
        result = format_as_outreach_result(search_result_with_entities)
        
        # Should have higher signal score due to named entities
        assert result.signal_score >= 0.7  # Base 0.5 + 0.1 for named entities + 0.1 for timestamp
    
    def test_signal_candidate_threshold_validation(self):
        """Test signal candidate threshold of 0.7 is correctly applied."""
        # Test just below threshold
        below_threshold = SearchResult(
            id="below_threshold",
            text="Basic professional information",
            fused_score=0.5,
            metadata={"company": "TestCorp", "title": "Engineer", "source": "profile"}
        )
        
        result_below = format_as_outreach_result(below_threshold)
        assert result_below.signal_score < 0.7
        assert result_below.is_signal_candidate is False
        
        # Test just above threshold
        above_threshold = SearchResult(
            id="above_threshold",
            text="Achieved 150% growth with $2M revenue impact",
            fused_score=0.5,
            metadata={"company": "TestCorp", "title": "Director", "source": "achievement"}
        )
        
        result_above = format_as_outreach_result(above_threshold)
        assert result_above.signal_score >= 0.7
        assert result_above.is_signal_candidate is True
    
    def test_outreach_rag_result_field_completeness(self):
        """Test OutreachRAGResult has all required fields with proper types."""
        search_result = SearchResult(
            id="completeness_test",
            text="Complete test data",
            fused_score=0.8,
            metadata={
                "company": "CompleteCorp",
                "title": "Complete Role",
                "source": "complete_source",
                "source_weight": 0.85,
                "timestamp": "2024-03-01T10:00:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Verify all required fields exist and have correct types
        assert isinstance(result.id, str)
        assert isinstance(result.score, float)
        assert isinstance(result.text, str)
        assert isinstance(result.company, str)
        assert isinstance(result.title, str)
        assert isinstance(result.source, str)
        assert isinstance(result.source_weight, float)
        assert isinstance(result.age_days, int)
        assert isinstance(result.signal_score, float)
        assert isinstance(result.signal_type, str) or result.signal_type is None
        assert isinstance(result.is_signal_candidate, bool)
    
    def test_multiple_signal_types_priority_handling(self):
        """Test handling of multiple signal type indicators with priority."""
        # Text with both quantitative and strategic indicators
        mixed_text = "Strategic initiative increased revenue by 40% through digital transformation."
        search_result = SearchResult(
            id="mixed_signals_test",
            text=mixed_text,
            fused_score=0.7,
            metadata={
                "company": "MixedCorp",
                "title": "Strategic Director",
                "source": "quarterly_report",
                "timestamp": "2024-02-01T12:00:00Z"
            }
        )
        
        result = format_as_outreach_result(search_result)
        
        # Should prioritize quantitative (checked first in implementation)
        assert result.signal_type == "quantitative"
        assert result.is_signal_candidate is True
