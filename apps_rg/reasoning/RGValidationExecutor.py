"""RGValidationExecutor — Canonical parameterized RG validation agent.

Consolidates: ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
Updated: 2026-03-11 (P3-A: now subclasses ParameterizedValidator)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from apps_shared.reasoning.ParameterizedValidator import ParameterizedValidator

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Domain-specific collect_issues implementations stored as module-level registry
_RULE_REGISTRY: dict[str, Callable] = {}


def register_rule(name: str):
    """Decorator to register a collect_issues implementation."""

    def decorator(func):
        _RULE_REGISTRY[name] = func
        return func

    return decorator


@register_rule("ats_compatibility")
def _ats_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """ATS compatibility validation logic."""
    issues = []
    if not resume_data.get("skills"):
        issues.append(
            {"type": "ats_missing_skills", "severity": "high", "message": "No skills section found"},
        )
    if not resume_data.get("experience"):
        issues.append(
            {"type": "ats_missing_experience", "severity": "high", "message": "No experience section"},
        )
    keywords = resume_data.get("keywords", [])
    if job_data:
        required = set(job_data.get("required_keywords", []))
        found = set(keywords)
        missing = required - found
        for kw in missing:
            issues.append(
                {"type": "ats_missing_keyword", "severity": "medium", "message": f"Missing keyword: {kw}"},
            )
    return issues


@register_rule("brand_compliance")
def _brand_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Brand compliance validation logic."""
    issues = []
    tone = resume_data.get("tone", "")
    if tone and tone.lower() not in ("professional", "confident", "balanced"):
        issues.append(
            {"type": "brand_tone_mismatch", "severity": "medium", "message": f"Tone '{tone}' not aligned"},
        )
    if resume_data.get("contains_superlatives", False):
        issues.append({"type": "brand_superlatives", "severity": "low", "message": "Contains superlatives"})
    return issues


@register_rule("fact_check")
def _fact_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Fact-check validation logic."""
    issues = []
    claims = resume_data.get("quantified_claims", [])
    for claim in claims:
        if not claim.get("source"):
            issues.append(
                {
                    "type": "fact_unsourced_claim",
                    "severity": "high",
                    "message": f"Unsourced: {claim.get('text', '')}",
                },
            )
        if claim.get("value") and not claim.get("context"):
            issues.append(
                {
                    "type": "fact_no_context",
                    "severity": "medium",
                    "message": f"No context for metric: {claim.get('text', '')}",
                },
            )
    dates = resume_data.get("dates", [])
    for i in range(len(dates) - 1):
        if dates[i].get("end") and dates[i + 1].get("start"):
            if dates[i]["end"] > dates[i + 1]["start"]:
                issues.append(
                    {"type": "fact_date_overlap", "severity": "high", "message": "Overlapping date ranges"},
                )
    return issues


@register_rule("section_balance")
def _section_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Section balance validation logic."""
    issues = []
    sections = resume_data.get("sections", {})
    total_len = sum(len(str(v)) for v in sections.values()) or 1
    for name, content in sections.items():
        ratio = len(str(content)) / total_len
        if ratio > 0.6:
            issues.append(
                {
                    "type": "section_oversized",
                    "severity": "medium",
                    "message": f"Section '{name}' is {ratio:.0%} of total",
                },
            )
        if ratio < 0.05 and name not in ("objective", "summary"):
            issues.append(
                {
                    "type": "section_undersized",
                    "severity": "low",
                    "message": f"Section '{name}' is only {ratio:.0%} of total",
                },
            )
    return issues


@dataclass
class RGValidationExecutor(ParameterizedValidator):
    """Parameterized RG validation agent.

    Usage:
        validator = RGValidationExecutor(rule_set="ats_compatibility")

    Inherits execute(), collect_issues() skeleton, and _RULE_REGISTRY dispatch
    from ParameterizedValidator (P3-A). Rule functions registered via @register_rule above.
    """

    rule_set: str = "generic"

    def execute(self, resume_data: dict, job_data: dict | None = None, **kwargs) -> dict:
        """Execute validation and return results."""
        issues = self.collect_issues(resume_data, job_data)
        return {
            "rule_set": self.rule_set,
            "issues": issues,
            "issue_count": len(issues),
            "passed": len(issues) == 0,
        }

    def collect_issues(self, resume_data: dict, job_data: dict | None = None, **kwargs) -> list[dict]:
        """Dispatch to registered rule implementation."""
        handler = _RULE_REGISTRY.get(self.rule_set)
        if handler is None:
            return [
                {
                    "type": "unknown_rule_set",
                    "severity": "high",
                    "message": f"No handler for rule_set={self.rule_set}",
                },
            ]
        return handler(self, resume_data, job_data)
