"""
Resume Engine Injection Detection Module

Corollary to outreach_engine/l5/injection_detection.py
Specialized for resume-specific injection patterns and PII protection.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InjectionType(Enum):
    """Types of resume-specific injection attacks."""
    PII_INJECTION = "pii_injection"
    FAKE_CREDENTIALS = "fake_credentials"
    TEMPLATE_MANIPULATION = "template_manipulation"
    MALICIOUS_LINKS = "malicious_links"
    SKILL_INFLATION = "skill_inflation"
    EXPERIENCE_FABRICATION = "experience_fabrication"
    PROMPT_INJECTION = "prompt_injection"
    XSS_ATTEMPTS = "xss_attempts"


@dataclass
class InjectionResult:
    """Result of injection detection analysis."""
    is_injected: bool
    injection_type: Optional[InjectionType]
    confidence: float
    detected_patterns: List[str]
    risk_level: str  # "low", "medium", "high", "critical"
    sanitized_content: Optional[str] = None


class ResumeInjectionDetector:
    """Detects and prevents resume-specific injection attacks."""
    
    def __init__(self):
        self.pii_patterns = self._init_pii_patterns()
        self.credential_patterns = self._init_credential_patterns()
        self.template_patterns = self._init_template_patterns()
        self.malicious_patterns = self._init_malicious_patterns()
        self.skill_inflation_patterns = self._init_skill_inflation_patterns()
    
    def _init_pii_patterns(self) -> List[re.Pattern]:
        """Initialize PII injection detection patterns."""
        return [
            # Social Security Numbers
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            re.compile(r'\b\d{3}\s\d{2}\s\d{4}\b'),
            # Credit Card Numbers
            re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            # Phone Numbers with suspicious patterns
            re.compile(r'\+1-\d{3}-\d{3}-\d{4}'),
            # Email patterns that look like injection attempts
            re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            # Address patterns
            re.compile(r'\d+\s+[\w\s]+,\s+[A-Z]{2}\s+\d{5}'),
        ]
    
    def _init_credential_patterns(self) -> List[re.Pattern]:
        """Initialize fake credential detection patterns."""
        return [
            # Fake university patterns
            re.compile(r'University of [A-Z]+', re.IGNORECASE),
            re.compile(r'[A-Z]+ University', re.IGNORECASE),
            # Fake certification patterns
            re.compile(r'Certified [A-Z]+ [A-Z]+', re.IGNORECASE),
            re.compile(r'[A-Z]+ Certified [A-Z]+', re.IGNORECASE),
            # Suspicious degree patterns
            re.compile(r'PhD in [A-Z]+ [A-Z]+', re.IGNORECASE),
            re.compile(r'Master of [A-Z]+ [A-Z]+', re.IGNORECASE),
        ]
    
    def _init_template_patterns(self) -> List[re.Pattern]:
        """Initialize template manipulation detection patterns."""
        return [
            # Template injection attempts
            re.compile(r'\{\{.*\}\}'),
            re.compile(r'\{%.*%\}'),
            re.compile(r'\{\#.*\#\}'),
            # System command attempts
            re.compile(r'\$\(.*\)'),
            re.compile(r'`.*`'),
            re.compile(r'\|\|.*\|\|'),
            # Format string attacks
            re.compile(r'%s.*%s'),
            re.compile(r'%d.*%d'),
            re.compile(r'%x.*%x'),
        ]
    
    def _init_malicious_patterns(self) -> List[re.Pattern]:
        """Initialize malicious content detection patterns."""
        return [
            # XSS attempts
            re.compile(r'<script.*?>.*?</script>', re.IGNORECASE),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            # SQL injection patterns
            re.compile(r'union\s+select', re.IGNORECASE),
            re.compile(r'drop\s+table', re.IGNORECASE),
            re.compile(r'insert\s+into', re.IGNORECASE),
            # Command injection
            re.compile(r';\s*(rm|del|format)', re.IGNORECASE),
            re.compile(r'\|\s*(cat|type|dir)', re.IGNORECASE),
        ]
    
    def _init_skill_inflation_patterns(self) -> List[re.Pattern]:
        """Initialize skill inflation detection patterns."""
        return [
            # Expertise level inflation
            re.compile(r'Expert in [A-Z]+ [A-Z]+', re.IGNORECASE),
            re.compile(r'Master of [A-Z]+ [A-Z]+', re.IGNORECASE),
            re.compile(r'Ninja [A-Z]+ [A-Z]+', re.IGNORECASE),
            re.compile(r'Guru [A-Z]+ [A-Z]+', re.IGNORECASE),
            # Unrealistic experience claims
            re.compile(r'\d+\+ years? of experience', re.IGNORECASE),
            re.compile(r'Since \d{4}.*present', re.IGNORECASE),
        ]
    
    def detect_injection(self, content: str) -> InjectionResult:
        """
        Detect injection attempts in resume content.
        
        Args:
            content: Resume content to analyze
            
        Returns:
            InjectionResult with detection details
        """
        detected_patterns = []
        injection_types = []
        max_confidence = 0.0
        
        # Check PII injection
        for pattern in self.pii_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_patterns.extend([f"PII: {match}" for match in matches])
                injection_types.append(InjectionType.PII_INJECTION)
                max_confidence = max(max_confidence, 0.8)
        
        # Check credential injection
        for pattern in self.credential_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_patterns.extend([f"Credential: {match}" for match in matches])
                injection_types.append(InjectionType.FAKE_CREDENTIALS)
                max_confidence = max(max_confidence, 0.7)
        
        # Check template manipulation
        for pattern in self.template_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_patterns.extend([f"Template: {match}" for match in matches])
                injection_types.append(InjectionType.TEMPLATE_MANIPULATION)
                max_confidence = max(max_confidence, 0.9)
        
        # Check malicious content
        for pattern in self.malicious_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_patterns.extend([f"Malicious: {match}" for match in matches])
                injection_types.extend([InjectionType.MALICIOUS_LINKS, InjectionType.XSS_ATTEMPTS])
                max_confidence = max(max_confidence, 0.95)
        
        # Check skill inflation
        for pattern in self.skill_inflation_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_patterns.extend([f"Skill Inflation: {match}" for match in matches])
                injection_types.append(InjectionType.SKILL_INFLATION)
                max_confidence = max(max_confidence, 0.6)
        
        # Determine risk level
        risk_level = self._calculate_risk_level(max_confidence, injection_types)
        
        # Sanitize content if injection detected
        sanitized_content = None
        if detected_patterns:
            sanitized_content = self._sanitize_content(content, detected_patterns)
        
        return InjectionResult(
            is_injected=len(detected_patterns) > 0,
            injection_type=injection_types[0] if injection_types else None,
            confidence=max_confidence,
            detected_patterns=detected_patterns,
            risk_level=risk_level,
            sanitized_content=sanitized_content
        )
    
    def _calculate_risk_level(self, confidence: float, injection_types: List[InjectionType]) -> str:
        """Calculate risk level based on confidence and injection types."""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _sanitize_content(self, content: str, detected_patterns: List[str]) -> str:
        """Sanitize content by removing detected injection patterns."""
        sanitized = content
        
        # Remove PII patterns
        for pattern in self.pii_patterns:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        # Remove template patterns
        for pattern in self.template_patterns:
            sanitized = pattern.sub('[SANITIZED]', sanitized)
        
        # Remove malicious patterns
        for pattern in self.malicious_patterns:
            sanitized = pattern.sub('[REMOVED]', sanitized)
        
        return sanitized
    
    def validate_resume_section(self, section_name: str, content: str) -> Tuple[bool, List[str]]:
        """
        Validate a specific resume section for injection attempts.
        
        Args:
            section_name: Name of the resume section
            content: Section content to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        result = self.detect_injection(content)
        
        if result.is_injected:
            issues = [
                f"Injection detected in {section_name}",
                f"Type: {result.injection_type.value if result.injection_type else 'unknown'}",
                f"Risk Level: {result.risk_level}",
                f"Patterns: {', '.join(result.detected_patterns[:3])}"  # Show first 3 patterns
            ]
            return False, issues
        else:
            return True, []
    
    def batch_validate_sections(self, sections: Dict[str, str]) -> Dict[str, InjectionResult]:
        """
        Validate multiple resume sections for injection attempts.
        
        Args:
            sections: Dictionary of section_name -> content
            
        Returns:
            Dictionary of section_name -> InjectionResult
        """
        results = {}
        
        for section_name, content in sections.items():
            results[section_name] = self.detect_injection(content)
        
        return results


# Convenience functions for backward compatibility
def detect_resume_injection(content: str) -> InjectionResult:
    """Convenience function to detect injection in resume content."""
    detector = ResumeInjectionDetector()
    return detector.detect_injection(content)


def validate_resume_sections(sections: Dict[str, str]) -> Dict[str, InjectionResult]:
    """Convenience function to validate multiple resume sections."""
    detector = ResumeInjectionDetector()
    return detector.batch_validate_sections(sections)





