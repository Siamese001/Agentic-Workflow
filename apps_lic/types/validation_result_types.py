"""
Stateless validation tools for apps_lic.

Moved from k-series agents to promote modularity and reusability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validator execution."""

    passed: bool
    reasons: tuple[str, ...]
    final_draft: str
    attempts: int
    qa_result: dict[str, Any]


@dataclass(frozen=True)
class Draft:
    """Simple draft container."""

    subject: str
    body: str

    def render(self) -> str:
        return f"Subject: {self.subject}\n\n{self.body}"


@dataclass(frozen=True)
class DraftPackage:
    """Container describing the composed draft and supporting evidence."""

    draft: str
    artifacts: dict[str, str]
    total_latency_ms: int = 0

    def with_draft(self, new_draft: str) -> DraftPackage:
        return DraftPackage(new_draft, dict(self.artifacts), self.total_latency_ms)


def score_quality(draft: str, reflexion: bool) -> int:
    """Return a simple heuristic quality score."""
    base = 5 if "value" in draft.lower() else 3
    return base + (2 if reflexion else 0)


def validate_schema_policy(data: dict[str, Any], schema: dict[str, Any]) -> ValidationResult:
    """
    Stateless schema validation utility.

    Args:
        data: Data to validate
        schema: Schema definition

    Returns:
        ValidationResult with validation outcome
    """
    required_fields = schema.get("required", [])
    missing_fields = [field for field in required_fields if field not in data]
    passed = len(missing_fields) == 0
    reasons = tuple(missing_fields) if not passed else ()
    return ValidationResult(
        passed=passed,
        reasons=reasons,
        final_draft=str(data),
        attempts=1,
        qa_result={"validation": "schema_check"},
    )


def check_content_compliance(content: str, prohibited_terms: list[str]) -> ValidationResult:
    """
    Stateless content compliance check.

    Args:
        content: Content to check
        prohibited_terms: List of prohibited terms

    Returns:
        ValidationResult with compliance outcome
    """
    violations = [term for term in prohibited_terms if term.lower() in content.lower()]
    passed = len(violations) == 0
    reasons = tuple(violations) if not passed else ()
    return ValidationResult(
        passed=passed,
        reasons=reasons,
        final_draft=content,
        attempts=1,
        qa_result={"validation": "compliance_check"},
    )
