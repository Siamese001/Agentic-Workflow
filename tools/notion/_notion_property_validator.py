#!/usr/bin/env python3
"""_notion_property_validator.py — Notion property schema validation helper.

Pure logic. No I/O at import. Safe to import from any hook, audit, or CI gate.

Provides pre-flight validation of Notion page/database properties before API
writes, preventing 400 errors from renamed/deleted properties.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Levenshtein distance for fuzzy property name matching
# ---------------------------------------------------------------------------

def _levenshtein(a: str, b: str) -> int:
    """Return edit distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    
    prev_row = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        curr_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def _suggest_property(missing: str, available: set[str]) -> str | None:
    """Find closest matching property name using Levenshtein distance."""
    if not available:
        return None
    
    scored = [(p, _levenshtein(missing.lower(), p.lower())) for p in available]
    scored.sort(key=lambda x: x[1])
    best, distance = scored[0]
    
    # Exact match - no suggestion needed (not a violation)
    if distance == 0:
        return None
    
    # Only suggest if reasonably close (distance <= 3 or 30% of length)
    threshold = min(3, max(1, len(missing) // 3))
    if distance <= threshold:
        return best
    return None


# ---------------------------------------------------------------------------
# Validation result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PropertyViolation:
    """A single property validation failure."""
    property_name: str
    violation_type: str  # 'missing', 'renamed', 'type_mismatch'
    suggestion: str | None = None
    message: str = ""


@dataclass
class ValidationResult:
    """Complete validation result for a page/database."""
    page_id: str
    valid: bool
    violations: list[PropertyViolation] = field(default_factory=list)
    available_properties: set[str] = field(default_factory=set)
    checked_at: float = field(default_factory=lambda: time.time())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "valid": self.valid,
            "violations": [
                {
                    "property": v.property_name,
                    "type": v.violation_type,
                    "suggestion": v.suggestion,
                    "message": v.message,
                }
                for v in self.violations
            ],
            "available_properties": sorted(self.available_properties),
            "checked_at": self.checked_at,
        }


# ---------------------------------------------------------------------------
# In-memory cache for property schemas (TTL = 5 minutes)
# ---------------------------------------------------------------------------

_SCHEMA_CACHE: dict[str, tuple[set[str], float]] = {}
_CACHE_TTL_SECONDS = 300


def _get_cached(page_id: str) -> set[str] | None:
    """Return cached properties if TTL not expired."""
    if page_id in _SCHEMA_CACHE:
        props, cached_at = _SCHEMA_CACHE[page_id]
        if time.time() - cached_at < _CACHE_TTL_SECONDS:
            return props
        del _SCHEMA_CACHE[page_id]
    return None


def _set_cached(page_id: str, properties: set[str]) -> None:
    """Cache properties with timestamp."""
    _SCHEMA_CACHE[page_id] = (properties, time.time())


def clear_cache() -> None:
    """Clear the schema cache. Useful for testing."""
    _SCHEMA_CACHE.clear()


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------

def validate_properties(
    page_id: str,
    expected_properties: set[str],
    actual_properties: set[str] | None = None,
) -> ValidationResult:
    """Validate that all expected properties exist on a Notion page/database.
    
    Args:
        page_id: The Notion page/database ID being validated
        expected_properties: Set of property names that must exist
        actual_properties: Optional pre-fetched set of actual property names.
                          If None, will attempt to fetch from Notion API.
    
    Returns:
        ValidationResult with violations and suggestions
    """
    violations: list[PropertyViolation] = []
    
    # If actual properties not provided, try to get from cache or return unknown
    if actual_properties is None:
        actual_properties = _get_cached(page_id)
        if actual_properties is None:
            # Cache miss - caller must fetch from Notion API
            return ValidationResult(
                page_id=page_id,
                valid=False,
                violations=[PropertyViolation(
                    property_name="*",
                    violation_type="cache_miss",
                    suggestion=None,
                    message=f"Property schema not cached for {page_id}. "
                            f"Call fetch_and_cache_properties() first.",
                )],
            )
    
    # Check each expected property
    missing = expected_properties - actual_properties
    for prop in missing:
        suggestion = _suggest_property(prop, actual_properties)
        if suggestion:
            violation_type = "renamed"
            message = f"Property '{prop}' not found. Did you mean '{suggestion}'?"
        else:
            violation_type = "missing"
            message = f"Property '{prop}' not found on page/database."
        
        violations.append(PropertyViolation(
            property_name=prop,
            violation_type=violation_type,
            suggestion=suggestion,
            message=message,
        ))
    
    return ValidationResult(
        page_id=page_id,
        valid=len(violations) == 0,
        violations=violations,
        available_properties=actual_properties,
    )


def fetch_and_cache_properties(page_id: str, properties: set[str]) -> None:
    """Cache a set of properties for a page ID.
    
    In production, this would be called with the result of a Notion API
    query to the database or page. For now, caller provides the property set.
    """
    _set_cached(page_id, properties)


# ---------------------------------------------------------------------------
# Canonical property sets for known databases
# ---------------------------------------------------------------------------

# Plans DB required properties (from notion-plans-taxonomy.md)
PLANS_DB_REQUIRED_PROPERTIES: set[str] = {
    "Slug",
    "Status",
    "Exists On Disk",
    "Plan File Path",
    "Summary",
    "AI Summary ",  # Note trailing space
    "Waiting For",
}

# Backlog Items DB required properties
BACKLOG_DB_REQUIRED_PROPERTIES: set[str] = {
    "Title",
    "Status",
    "Priority",
    "Plan",
    "Plan File",
    "Waiting For",
}


def validate_plans_db_properties(
    page_id: str,
    actual_properties: set[str] | None = None,
) -> ValidationResult:
    """Validate that a Plans DB row has all required properties."""
    return validate_properties(
        page_id=page_id,
        expected_properties=PLANS_DB_REQUIRED_PROPERTIES,
        actual_properties=actual_properties,
    )


def validate_backlog_db_properties(
    page_id: str,
    actual_properties: set[str] | None = None,
) -> ValidationResult:
    """Validate that a Backlog Items DB row has all required properties."""
    return validate_properties(
        page_id=page_id,
        expected_properties=BACKLOG_DB_REQUIRED_PROPERTIES,
        actual_properties=actual_properties,
    )
