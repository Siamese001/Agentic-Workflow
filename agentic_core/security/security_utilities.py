#!/usr/bin/env python3
"""
Consolidated Security Utilities for Agentic Workflow
Implements P3 (Prompt Firewall) and P4 (Fact Checker) on L1

This module centralizes security protocols previously distributed
across the system, providing unified access to:
- P3: Prompt injection detection and prevention
- P4: Fact checking and truth anchor validation
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Set

# Configure logging
logger = logging.getLogger(__name__)


class SecurityStatus(Enum):
    """Status codes for security checks."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"


@dataclass
class SecurityResult:
    """Result from a security check."""
    status: SecurityStatus
    reason: str
    details: Dict[str, Any] = None
    confidence: float = 0.0


class PromptFirewall:
    """P3: Prompt Firewall for injection detection and prevention."""

    # Known injection patterns
    INJECTION_PATTERNS = [
        r'(?i)(ignore|forget|disregard).*previous.*instruction',
        r'(?i)(system|developer|admin|root).*prompt',
        r'(?i)(jailbreak|bypass|override).*restriction',
        r'(?i)(new.*role|act.*as|pretend.*you)',
        r'(?i)(translate|decode|reveal).*hidden',
        r'(?i)(<\|.*?\|>|<\|.*?\|>)',  # Special token patterns
        r'(?i)(###.*instruction|```.*prompt)',
        r'(?i)(summarize|repeat|echo).*above',
    ]

    # Suspicious keywords
    SUSPICIOUS_KEYWORDS = {
        'injection', 'bypass', 'override', 'ignore', 'forget',
        'disregard', 'jailbreak', 'root', 'admin', 'system',
        'developer', 'prompt', 'instruction', 'roleplay',
        'pretend', 'act as', 'translate', 'decode'
    }

    def __init__(self):
        self.patterns = [re.compile(p) for p in self.INJECTION_PATTERNS]

    def scan_input(self, input_text: str) -> SecurityResult:
        """
        Scan input text for prompt injection attempts.

        Args:
            input_text: Text to scan for injections

        Returns:
            SecurityResult with PASS/FAIL status
        """
        if not input_text:
            return SecurityResult(
                status=SecurityStatus.WARNING,
                reason="Empty input provided"
            )

        # Check for injection patterns
        for pattern in self.patterns:
            if pattern.search(input_text):
                logger.warning(f"P3_INJECTION_DETECTED: {pattern.pattern}")
                return SecurityResult(
                    status=SecurityStatus.FAIL,
                    reason=f"Injection pattern detected: {pattern.pattern}",
                    details={'pattern': pattern.pattern, 'confidence': 0.95}
                )

        # Check for suspicious keyword density
        words = input_text.lower().split()
        suspicious_count = sum(1 for word in words if word in self.SUSPICIOUS_KEYWORDS)
        suspicious_ratio = suspicious_count / len(words) if words else 0

        if suspicious_ratio > 0.1:  # More than 10% suspicious keywords
            logger.warning(f"P3_SUSPICIOUS_KEYWORDS: {suspicious_ratio:.2%}")
            return SecurityResult(
                status=SecurityStatus.WARNING,
                reason=f"High suspicious keyword density: {suspicious_ratio:.2%}",
                details={'ratio': suspicious_ratio, 'count': suspicious_count}
            )

        logger.info("P3_SCAN_PASS: No injection detected")
        return SecurityResult(
            status=SecurityStatus.PASS,
            reason="Input passed security scan",
            confidence=0.9
        )

    def sanitize_input(self, input_text: str) -> str:
        """
        Sanitize input by removing or escaping suspicious content.

        Args:
            input_text: Text to sanitize

        Returns:
            Sanitized text
        """
        # Remove special token patterns
        sanitized = re.sub(r'<\|.*?\|>', '', input_text)

        # Escape code blocks
        sanitized = re.sub(r'```', '```', sanitized)

        # Limit length to prevent overflow attacks
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000] + "...[truncated]"

        return sanitized


class FactChecker:
    """P4: Fact Checker for truth anchor validation."""

    def __init__(self, golden_record_path: Optional[str] = None):
        """
        Initialize Fact Checker with golden record data.

        Args:
            golden_record_path: Path to JSON file with truth anchors
        """
        self.golden_record_path = golden_record_path or "config/golden_record.json"
        self.truth_anchors = self._load_golden_record()

    def _load_golden_record(self) -> Dict[str, Any]:
        """Load truth anchors from golden record file."""
        try:
            path = Path(self.golden_record_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Golden record not found at {self.golden_record_path}")
                return self._create_default_record()
        except Exception as e:
            logger.error(f"Failed to load golden record: {e}")
            return self._create_default_record()

    def _create_default_record(self) -> Dict[str, Any]:
        """Create default truth anchors if file doesn't exist."""
        return {
            "skills": {
                "python": {"level": "expert", "verified": True},
                "javascript": {"level": "advanced", "verified": True},
                "react": {"level": "intermediate", "verified": True},
                "docker": {"level": "intermediate", "verified": True},
                "aws": {"level": "beginner", "verified": True}
            },
            "experience": {
                "years_total": 5,
                "companies": ["TechCorp", "StartupXYZ"],
                "positions": ["Senior Developer", "Lead Engineer"]
            },
            "education": {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "university": "State University"
            }
        }

    def validate_skills(self, draft: str) -> SecurityResult:
        """
        Validate skills mentioned in draft against truth anchors.

        Args:
            draft: Generated draft text to validate

        Returns:
            SecurityResult with validation outcome
        """
        if not draft:
            return SecurityResult(
                status=SecurityStatus.FAIL,
                reason="Empty draft provided for validation"
            )

        # Extract skills from draft
        mentioned_skills = self._extract_skills(draft)
        violations = []

        for skill in mentioned_skills:
            if skill.lower() in self.truth_anchors.get("skills", {}):
                anchor = self.truth_anchors["skills"][skill.lower()]
                if not anchor.get("verified", False):
                    violations.append(f"Skill '{skill}' not verified")
            else:
                violations.append(f"Skill '{skill}' not found in truth anchors")

        if violations:
            logger.warning(f"P4_VALIDATION_FAIL: {len(violations)} violations")
            return SecurityResult(
                status=SecurityStatus.FAIL,
                reason=f"Skill validation failed: {'; '.join(violations)}",
                details={'violations': violations, 'mentioned_skills': mentioned_skills}
            )

        logger.info("P4_VALIDATION_PASS: All skills verified")
        return SecurityResult(
            status=SecurityStatus.PASS,
            reason="All skills validated against truth anchors",
            details={'verified_skills': mentioned_skills}
        )

    def _extract_skills(self, text: str) -> Set[str]:
        """Extract skill keywords from text."""
        # Common skill keywords to look for
        skill_keywords = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular',
            'vue', 'node', 'django', 'flask', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'sql', 'nosql', 'mongodb', 'postgresql',
            'git', 'ci/cd', 'devops', 'microservices', 'rest', 'graphql',
            'machine learning', 'ai', 'data science', 'analytics'
        }

        text_lower = text.lower()
        found_skills = set()

        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.add(skill)

        return found_skills

    def validate_experience(self, draft: str) -> SecurityResult:
        """
        Validate experience claims in draft.

        Args:
            draft: Generated draft text

        Returns:
            SecurityResult with validation outcome
        """
        # Extract years of experience
        years_pattern = r'(\d+)\s*(?:years?|yrs?)'
        matches = re.findall(years_pattern, draft.lower())

        if matches:
            max_years = max(int(year) for year in matches)
            anchor_years = self.truth_anchors.get("experience", {}).get("years_total", 0)

            if max_years > anchor_years + 2:  # Allow 2 years grace
                return SecurityResult(
                    status=SecurityStatus.WARNING,
                    reason=f"Experience claim ({max_years} years) exceeds anchor ({anchor_years} years)"
                )

        return SecurityResult(
            status=SecurityStatus.PASS,
            reason="Experience validation passed"
        )


# Singleton instances for easy access
_prompt_firewall = None
_fact_checker = None


def get_prompt_firewall() -> PromptFirewall:
    """Get singleton instance of PromptFirewall."""
    global _prompt_firewall
    if _prompt_firewall is None:
        _prompt_firewall = PromptFirewall()
    return _prompt_firewall


def get_fact_checker(golden_record_path: Optional[str] = None) -> FactChecker:
    """Get singleton instance of FactChecker."""
    global _fact_checker
    if _fact_checker is None or golden_record_path:
        _fact_checker = FactChecker(golden_record_path)
    return _fact_checker


# Convenience functions
def scan_for_injection(input_text: str) -> SecurityResult:
    """Convenience function to scan input for injections."""
    return get_prompt_firewall().scan_input(input_text)


def validate_facts(draft: str) -> SecurityResult:
    """Convenience function to validate facts in draft."""
    return get_fact_checker().validate_skills(draft)
