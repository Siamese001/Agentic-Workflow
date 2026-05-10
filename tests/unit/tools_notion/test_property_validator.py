#!/usr/bin/env python3
"""test_property_validator.py — Unit tests for _notion_property_validator."""
import pytest

from tools.notion._notion_property_validator import (
    PropertyViolation,
    ValidationResult,
    _levenshtein,
    _suggest_property,
    clear_cache,
    fetch_and_cache_properties,
    validate_properties,
    validate_plans_db_properties,
    PLANS_DB_REQUIRED_PROPERTIES,
)


class TestLevenshtein:
    """Tests for the Levenshtein distance function."""
    
    def test_same_string_zero_distance(self):
        assert _levenshtein("hello", "hello") == 0
    
    def test_empty_string(self):
        assert _levenshtein("hello", "") == 5
        assert _levenshtein("", "hello") == 5
    
    def test_single_substitution(self):
        assert _levenshtein("hello", "hallo") == 1
    
    def test_single_deletion(self):
        assert _levenshtein("hello", "hell") == 1
    
    def test_single_insertion(self):
        assert _levenshtein("hell", "hello") == 1
    
    def test_case_insensitive_sensitivity(self):
        # Levenshtein is case-sensitive
        assert _levenshtein("Hello", "hello") == 1


class TestSuggestProperty:
    """Tests for property name suggestion logic."""
    
    def test_exact_match_returns_none(self):
        # Exact match shouldn't suggest (not a violation)
        available = {"Status", "Summary", "Slug"}
        assert _suggest_property("Status", available) is None
    
    def test_typo_suggestion(self):
        # "Stats" is close to "Status"
        available = {"Status", "Summary", "Slug"}
        suggestion = _suggest_property("Stats", available)
        assert suggestion == "Status"
    
    def test_case_insensitive_typo(self):
        # "stats" should still suggest "Status"
        available = {"Status", "Summary", "Slug"}
        suggestion = _suggest_property("stats", available)
        assert suggestion == "Status"
    
    def test_no_suggestion_for_different_word(self):
        # "CompletelyDifferent" shouldn't suggest anything
        available = {"Status", "Summary", "Slug"}
        assert _suggest_property("CompletelyDifferent", available) is None
    
    def test_trailing_space_suggestion(self):
        # "AI Summary" should suggest "AI Summary " (with trailing space)
        available = {"AI Summary ", "Status", "Slug"}
        suggestion = _suggest_property("AI Summary", available)
        assert suggestion == "AI Summary "


class TestValidateProperties:
    """Tests for the main validate_properties function."""
    
    def setup_method(self):
        clear_cache()
    
    def teardown_method(self):
        clear_cache()
    
    def test_all_properties_present(self):
        expected = {"Status", "Summary", "Slug"}
        actual = {"Status", "Summary", "Slug", "Extra"}
        
        result = validate_properties("page-123", expected, actual)
        
        assert result.valid is True
        assert len(result.violations) == 0
        assert result.page_id == "page-123"
    
    def test_missing_property(self):
        expected = {"Status", "Summary", "Missing"}
        actual = {"Status", "Summary"}
        
        result = validate_properties("page-123", expected, actual)
        
        assert result.valid is False
        assert len(result.violations) == 1
        assert result.violations[0].property_name == "Missing"
        assert result.violations[0].violation_type == "missing"
    
    def test_renamed_property_suggestion(self):
        # "Stats" should be detected as renamed "Status"
        expected = {"Status"}
        actual = {"Stats"}  # Typo
        
        result = validate_properties("page-123", expected, actual)
        
        # "Status" is missing from actual
        assert result.valid is False
        assert len(result.violations) == 1
        assert result.violations[0].property_name == "Status"
    
    def test_cache_miss_returns_error(self):
        expected = {"Status"}
        
        # Don't cache anything - should return cache_miss error
        result = validate_properties("unknown-page", expected, None)
        
        assert result.valid is False
        assert len(result.violations) == 1
        assert result.violations[0].violation_type == "cache_miss"
    
    def test_cache_hit_uses_cached_properties(self):
        expected = {"Status", "Summary"}
        actual = {"Status", "Summary"}
        
        # Pre-populate cache
        fetch_and_cache_properties("cached-page", actual)
        
        # Don't pass actual - should use cache
        result = validate_properties("cached-page", expected, None)
        
        assert result.valid is True
        assert len(result.violations) == 0


class TestPlansDBValidation:
    """Tests for Plans DB specific validation."""
    
    def setup_method(self):
        clear_cache()
    
    def teardown_method(self):
        clear_cache()
    
    def test_plans_db_required_properties_count(self):
        # Should have the expected number of required properties
        assert len(PLANS_DB_REQUIRED_PROPERTIES) >= 7
        assert "Slug" in PLANS_DB_REQUIRED_PROPERTIES
        assert "Status" in PLANS_DB_REQUIRED_PROPERTIES
        assert "AI Summary " in PLANS_DB_REQUIRED_PROPERTIES
    
    def test_plans_db_validation_with_all_properties(self):
        # All required properties present
        all_props = PLANS_DB_REQUIRED_PROPERTIES | {"ExtraProperty"}
        fetch_and_cache_properties("plans-page", all_props)
        
        result = validate_plans_db_properties("plans-page")
        
        assert result.valid is True


class TestCacheOperations:
    """Tests for cache operations."""
    
    def setup_method(self):
        clear_cache()
    
    def teardown_method(self):
        clear_cache()
    
    def test_fetch_and_cache(self):
        props = {"Status", "Summary"}
        fetch_and_cache_properties("page-1", props)
        
        # Validation should use cached value
        result = validate_properties("page-1", {"Status"}, None)
        assert result.valid is True
    
    def test_clear_cache_removes_entries(self):
        fetch_and_cache_properties("page-1", {"Status"})
        clear_cache()
        
        # After clear, should get cache miss
        result = validate_properties("page-1", {"Status"}, None)
        assert result.violations[0].violation_type == "cache_miss"


class TestValidationResult:
    """Tests for ValidationResult data class."""
    
    def test_to_dict_with_violations(self):
        vio = PropertyViolation(
            property_name="MissingProp",
            violation_type="missing",
            suggestion="CorrectProp",
            message="Property not found",
        )
        result = ValidationResult(
            page_id="page-123",
            valid=False,
            violations=[vio],
            available_properties={"OtherProp"},
        )
        
        d = result.to_dict()
        assert d["page_id"] == "page-123"
        assert d["valid"] is False
        assert len(d["violations"]) == 1
        assert d["violations"][0]["property"] == "MissingProp"
        assert d["available_properties"] == ["OtherProp"]
    
    def test_to_dict_without_violations(self):
        result = ValidationResult(
            page_id="page-123",
            valid=True,
            violations=[],
            available_properties={"Status", "Summary"},
        )
        
        d = result.to_dict()
        assert d["valid"] is True
        assert len(d["violations"]) == 0
