"""
Intelligence Query Validator - Deterministic Query Validation

Zero-Ambiguity Standard: Renamed from intelligence_librarian_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Query validation (string validation)
- Filter validation (schema validation)
- Cache key generation (deterministic hashing)
- Result filtering (deterministic filtering)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


@dataclass
class IntelligenceQueryResult:
    """Result of intelligence query validation."""

    valid: bool
    issues: list[str]
    cache_key: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class IntelligenceQueryValidator:
    """
    Pure deterministic intelligence query validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize with intelligence librarian configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.min_query_length = config.get("min_query_length", 3)
        self.max_query_length = config.get("max_query_length", 500)
        self.allowed_filter_keys = config.get(
            "allowed_filter_keys", ["industry", "date_range", "source", "relevance_threshold"]
        )
        self.cache_ttl = config.get("cache_ttl", 3600)

    def validate_query(self, query: str, filters: dict[str, Any] | None = None) -> IntelligenceQueryResult:
        """
        Validate intelligence query using purely deterministic logic.

        Args:
            query: Query string to validate
            filters: Optional filters dictionary

        Returns:
            IntelligenceQueryResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "IntelligenceQueryValidator.validate_query")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:IntelligenceQueryValidator.validate_query".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        query_issues = self._validate_query_string(query)
        issues.extend(query_issues)
        if filters:
            filter_issues = self._validate_filters(filters)
            issues.extend(filter_issues)
        cache_key = self._generate_cache_key(query, filters) if not issues else None
        return IntelligenceQueryResult(
            valid=len(issues) == 0,
            issues=issues,
            cache_key=cache_key,
            metadata={"validation_type": "deterministic"},
        )

    def _validate_query_string(self, query: str) -> list[str]:
        """
        Validate query string using deterministic rules.

        Moved to Deterministic: Pure string validation
        """
        issues: list[str] = []
        if not query:
            issues.append("Query cannot be empty")
            return issues
        if len(query) < self.min_query_length:
            issues.append(f"Query too short (min {self.min_query_length} characters)")
        if len(query) > self.max_query_length:
            issues.append(f"Query too long (max {self.max_query_length} characters)")
        if re.search("[<>{}]", query):
            issues.append("Query contains invalid characters")
        return issues

    def _validate_filters(self, filters: dict[str, Any]) -> list[str]:
        """
        Validate filters using deterministic schema validation.

        Moved to Deterministic: Pure schema validation
        """
        issues: list[str] = []
        for key in filters.keys():
            if key not in self.allowed_filter_keys:
                issues.append(f"Unknown filter key: {key}")
        if "relevance_threshold" in filters:
            threshold = filters["relevance_threshold"]
            if not isinstance(threshold, int | float) or not 0 <= threshold <= 1:
                issues.append("relevance_threshold must be between 0 and 1")
        if "date_range" in filters:
            date_range = filters["date_range"]
            if not isinstance(date_range, dict) or "start" not in date_range:
                issues.append("date_range must have 'start' field")
        return issues

    def _generate_cache_key(self, query: str, filters: dict[str, Any] | None) -> str:
        """
        Generate cache key using deterministic hashing.

        Moved to Deterministic: Pure hash generation
        """
        filter_str = str(sorted(filters.items())) if filters else ""
        combined = f"{query}:{filter_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    def normalize_query(self, query: str) -> str:
        """
        Normalize query string using deterministic rules.

        Moved to Deterministic: Pure string normalization
        """
        query = re.sub("\\s+", " ", query.strip())
        query = query.lower()
        return query

    def filter_results(self, results: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Filter results using deterministic filtering logic.

        Moved to Deterministic: Pure filtering logic
        """
        filtered = results.copy()
        if "relevance_threshold" in filters:
            threshold = filters["relevance_threshold"]
            filtered = [r for r in filtered if r.get("relevance", 0) >= threshold]
        if "industry" in filters:
            industry = filters["industry"]
            filtered = [r for r in filtered if r.get("industry") == industry]
        if "source" in filters:
            source = filters["source"]
            filtered = [r for r in filtered if r.get("source") == source]
        return filtered

    def calculate_query_complexity(self, query: str) -> dict[str, Any]:
        """
        Calculate query complexity using deterministic analysis.

        Returns complexity metrics for query optimization.
        """
        words = query.split()
        word_count = len(words)
        operator_count = sum(1 for word in words if word.upper() in ["AND", "OR", "NOT"])
        quoted_phrases = len(re.findall('"[^"]*"', query))
        complexity_score = word_count + operator_count * 2 + quoted_phrases * 3
        complexity_level = (
            "simple" if complexity_score < 5 else "moderate" if complexity_score < 15 else "complex"
        )
        return {
            "word_count": word_count,
            "operator_count": operator_count,
            "quoted_phrases": quoted_phrases,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
        }
