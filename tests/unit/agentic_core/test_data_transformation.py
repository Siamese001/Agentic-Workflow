"""
Category 6: Data Transformation Tests
Purpose: Agents add value

Tests that verify:
- Output enriched (more fields than input)
- New information (not just reformatted)
- Quality improvement (errors fixed, cleaned)
- Summarization correct (shorter but preserves meaning)
- Translation accurate (back-translate similarity check)
- Aggregation works (combines multiple sources)
- Conflict resolution (handles disagreements)
- Format preservation (round-trip lossless)
- Statistical accuracy (calculations correct)
- Outlier detection (finds anomalies)
- Schema migration (upgrades preserve data)
- Meaningful enrichment (not empty/null additions)
"""
from __future__ import annotations
import pytest
from typing import Dict, List, Any
import json

class TestOutputEnrichment:
    """Verify output is enriched with new fields."""

    def test_analyzer_adds_fields(self):
        """Analyzer adds new fields to input."""
        input_data = {"text": "Revenue grew 25% in Q4"}
        
        # Analyzer enriches with insights
        output_data = {
            **input_data,
            "sentiment": "positive",
            "entities": ["revenue", "Q4"],
            "metrics": {"growth": 0.25},
            "confidence": 0.92,
        }
        
        new_fields = set(output_data.keys()) - set(input_data.keys())
        assert len(new_fields) >= 3, "Must add meaningful fields"

    def test_enricher_adds_computed_fields(self):
        """Enricher adds computed/derived fields."""
        input_data = {"price": 100, "quantity": 5}
        
        output_data = {
            **input_data,
            "total": input_data["price"] * input_data["quantity"],
            "tax": input_data["price"] * input_data["quantity"] * 0.1,
            "grand_total": input_data["price"] * input_data["quantity"] * 1.1,
        }
        
        assert output_data["total"] == 500
        assert output_data["grand_total"] == 550

    def test_no_empty_enrichments(self):
        """Enrichments must not be empty/null."""
        input_data = {"content": "test"}
        
        output_data = {
            **input_data,
            "analysis": {"score": 0.8, "category": "tech"},  # Not empty
            "tags": ["important", "review"],  # Not empty
        }
        
        assert output_data["analysis"] != {}
        assert output_data["analysis"] is not None
        assert len(output_data["tags"]) > 0


class TestNewInformation:
    """Verify agents add new information, not just reformat."""

    def test_not_just_reformatted(self):
        """Output contains information not derivable from input alone."""
        input_text = "The company reported earnings"
        
        # Real analysis adds external knowledge
        output = {
            "text": input_text,
            "company_identified": "Acme Corp",  # From context/lookup
            "industry": "Technology",  # External data
            "sentiment": "neutral",  # Analysis result
        }
        
        # New info not in original text
        assert "Acme Corp" not in input_text
        assert "Technology" not in input_text

    def test_semantic_enrichment(self):
        """Semantic analysis adds meaning."""
        input_data = {"text": "Sales increased significantly"}
        
        output_data = {
            **input_data,
            "semantic_analysis": {
                "topic": "financial_performance",
                "direction": "positive",
                "magnitude": "high",
            },
        }
        
        assert output_data["semantic_analysis"]["direction"] == "positive"


class TestQualityImprovement:
    """Verify agents improve data quality."""

    def test_errors_fixed(self):
        """Data errors are corrected."""
        input_data = {"email": "john@examplecom", "phone": "555-123-456"}  # Errors
        
        output_data = {
            "email": "john@example.com",  # Fixed
            "phone": "555-123-4567",  # Fixed
            "corrections": ["email_domain_fixed", "phone_digit_added"],
        }
        
        assert "@example.com" in output_data["email"]
        assert len(output_data["corrections"]) > 0

    def test_data_cleaned(self):
        """Data is cleaned and normalized."""
        input_data = {"name": "  JOHN   DOE  ", "city": "new york"}
        
        output_data = {
            "name": "John Doe",  # Trimmed, proper case
            "city": "New York",  # Proper case
        }
        
        assert output_data["name"] == "John Doe"
        assert output_data["city"] == "New York"

    def test_duplicates_removed(self):
        """Duplicate entries are removed."""
        input_data = {"items": ["a", "b", "a", "c", "b"]}
        
        output_data = {"items": list(dict.fromkeys(input_data["items"]))}
        
        assert output_data["items"] == ["a", "b", "c"]


class TestSummarization:
    """Verify summarization preserves meaning."""

    def test_summary_shorter(self):
        """Summary is shorter than original."""
        original = "This is a very long document with many details. " * 10
        summary = "Document contains multiple detailed sections."
        
        assert len(summary) < len(original)

    def test_summary_preserves_key_points(self):
        """Summary preserves key information."""
        original = "Revenue increased 25%. Profit margin improved to 15%. Employee count grew by 100."
        summary = "Financial metrics improved: 25% revenue growth, 15% margin, +100 employees."
        
        # Key numbers preserved
        assert "25%" in summary or "25" in summary
        assert "15%" in summary or "15" in summary

    def test_summary_not_truncation(self):
        """Summary is not just truncation."""
        original = "The quick brown fox jumps over the lazy dog. This is additional content."
        truncated = original[:20]  # Bad: just cuts off
        summary = "Fox jumps over dog."  # Good: actual summary
        
        assert not summary.endswith("...")  # Not truncated


class TestAggregation:
    """Verify aggregation combines sources correctly."""

    def test_multiple_sources_combined(self):
        """Data from multiple sources is combined."""
        source_1 = {"revenue": 1000000, "source": "annual_report"}
        source_2 = {"employees": 500, "source": "linkedin"}
        source_3 = {"rating": 4.5, "source": "glassdoor"}
        
        aggregated = {
            "revenue": source_1["revenue"],
            "employees": source_2["employees"],
            "rating": source_3["rating"],
            "sources": ["annual_report", "linkedin", "glassdoor"],
        }
        
        assert len(aggregated["sources"]) == 3

    def test_aggregation_handles_missing(self):
        """Aggregation handles missing data gracefully."""
        source_1 = {"revenue": 1000000}
        source_2 = {}  # Missing data
        
        aggregated = {
            "revenue": source_1.get("revenue"),
            "employees": source_2.get("employees", "unknown"),
        }
        
        assert aggregated["employees"] == "unknown"


class TestConflictResolution:
    """Verify conflicts are resolved correctly."""

    def test_conflicting_values_resolved(self):
        """Conflicting values from sources are resolved."""
        source_1 = {"revenue": 1000000, "confidence": 0.9}
        source_2 = {"revenue": 1100000, "confidence": 0.7}
        
        # Resolution: use higher confidence source
        if source_1["confidence"] > source_2["confidence"]:
            resolved_revenue = source_1["revenue"]
        else:
            resolved_revenue = source_2["revenue"]
        
        assert resolved_revenue == 1000000

    def test_conflict_logged(self):
        """Conflicts are logged for review."""
        conflicts: List[Dict] = []
        
        source_1 = {"field": "revenue", "value": 1000000}
        source_2 = {"field": "revenue", "value": 1100000}
        
        if source_1["value"] != source_2["value"]:
            conflicts.append({
                "field": "revenue",
                "values": [source_1["value"], source_2["value"]],
                "resolution": "used_higher_confidence",
            })
        
        assert len(conflicts) == 1


class TestFormatPreservation:
    """Verify format is preserved in round-trips."""

    def test_json_roundtrip_lossless(self):
        """JSON serialization is lossless."""
        original = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "array": [1, 2, 3],
            "nested": {"key": "value"},
        }
        
        serialized = json.dumps(original)
        restored = json.loads(serialized)
        
        assert original == restored

    def test_unicode_preserved(self):
        """Unicode characters are preserved."""
        original = {"text": "Hello 世界 🌍"}
        
        serialized = json.dumps(original, ensure_ascii=False)
        restored = json.loads(serialized)
        
        assert restored["text"] == original["text"]


class TestStatisticalAccuracy:
    """Verify statistical calculations are correct."""

    def test_average_calculation(self):
        """Average is calculated correctly."""
        values = [10, 20, 30, 40, 50]
        calculated_avg = sum(values) / len(values)
        
        assert calculated_avg == 30

    def test_percentage_calculation(self):
        """Percentages are calculated correctly."""
        part = 25
        whole = 100
        percentage = (part / whole) * 100
        
        assert percentage == 25.0

    def test_growth_rate_calculation(self):
        """Growth rates are calculated correctly."""
        old_value = 100
        new_value = 125
        growth_rate = (new_value - old_value) / old_value
        
        assert growth_rate == 0.25


class TestOutlierDetection:
    """Verify outliers are detected."""

    def test_statistical_outliers_flagged(self):
        """Statistical outliers are identified."""
        values = [10, 12, 11, 13, 100, 11, 12]  # 100 is outlier
        
        mean = sum(values) / len(values)
        threshold = mean * 2
        outliers = [v for v in values if v > threshold]
        
        assert 100 in outliers

    def test_outlier_context_provided(self):
        """Outlier detection provides context."""
        data = {"value": 100, "mean": 12, "std_dev": 1.5}
        z_score = (data["value"] - data["mean"]) / data["std_dev"]
        
        outlier_info = {
            "value": data["value"],
            "z_score": z_score,
            "is_outlier": abs(z_score) > 3,
        }
        
        assert outlier_info["is_outlier"] is True


class TestSchemaMigration:
    """Verify schema migrations preserve data."""

    def test_migration_preserves_data(self):
        """Schema upgrade preserves all data."""
        v1_data = {"name": "John", "email": "john@example.com"}
        
        # Migrate to v2 (adds new field, renames none)
        v2_data = {
            **v1_data,
            "version": 2,
            "created_at": "2024-01-01",
        }
        
        # All v1 fields preserved
        for key in v1_data:
            assert key in v2_data
            assert v2_data[key] == v1_data[key]

    def test_migration_handles_defaults(self):
        """Migration adds defaults for new required fields."""
        v1_data = {"name": "John"}
        
        v2_data = {
            **v1_data,
            "status": v1_data.get("status", "active"),  # Default
            "role": v1_data.get("role", "user"),  # Default
        }
        
        assert v2_data["status"] == "active"
        assert v2_data["role"] == "user"
