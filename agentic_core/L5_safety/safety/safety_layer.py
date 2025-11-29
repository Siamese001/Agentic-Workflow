"""
Safety layer for L5 - provides comprehensive safety checks for outbound content and mutating actions.
Implements PII filtering, hallucination detection, and injection detection.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SafetyResult:
    """Result of safety check."""
    is_safe: bool
    confidence: float
    detected_issues: List[str]
    sanitized_content: Optional[str] = None
    risk_level: str = "low"  # low, medium, high, critical

class PIIDetector:
    """Detects and handles Personally Identifiable Information."""
    
    def __init__(self):
        # Regex patterns for PII detection
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.credit_card_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        self.address_pattern = re.compile(r'\b\d+\s+[\w\s]+\b(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|way|place|pl)\b', re.IGNORECASE)
        
    def detect_pii(self, text: str) -> Tuple[bool, List[str]]:
        """Detect PII in text and return (has_pii, detected_types)."""
        detected_types = []
        
        if self.email_pattern.search(text):
            detected_types.append("email")
        if self.phone_pattern.search(text):
            detected_types.append("phone")
        if self.ssn_pattern.search(text):
            detected_types.append("ssn")
        if self.credit_card_pattern.search(text):
            detected_types.append("credit_card")
        if self.address_pattern.search(text):
            detected_types.append("address")
        
        return len(detected_types) > 0, detected_types
    
    def sanitize_pii(self, text: str) -> str:
        """Remove or mask PII from text."""
        sanitized = text
        sanitized = self.email_pattern.sub('[EMAIL]', sanitized)
        sanitized = self.phone_pattern.sub('[PHONE]', sanitized)
        sanitized = self.ssn_pattern.sub('[SSN]', sanitized)
        sanitized = self.credit_card_pattern.sub('[CREDIT_CARD]', sanitized)
        sanitized = self.address_pattern.sub('[ADDRESS]', sanitized)
        return sanitized

class HallucinationDetector:
    """Detects potential hallucinations in generated content."""
    
    def __init__(self):
        # Keywords that might indicate hallucinations
        self.hallucination_indicators = [
            "I am not sure", "I don't have information", "I cannot confirm",
            "this might not be accurate", "I may be wrong", "speculation",
            "uncertain", "unverified", "not factual", "potentially incorrect"
        ]
        
        # Factual claims that should be verified
        self.factual_patterns = [
            r'\b\d{4}\b',  # Years
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Money amounts
            r'\b\d+%?\b',  # Percentages
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b'  # Dates
        ]
    
    def detect_hallucination(self, text: str) -> Tuple[bool, float, List[str]]:
        """Detect hallucinations and return (has_hallucination, confidence, indicators)."""
        indicators = []
        confidence = 0.0
        
        # Check for uncertainty indicators
        for indicator in self.hallucination_indicators:
            if indicator.lower() in text.lower():
                indicators.append(f"Uncertainty: {indicator}")
                confidence += 0.3
        
        # Check for unverified factual claims
        for pattern in self.factual_patterns:
            matches = re.findall(pattern, text)
            if matches:
                indicators.append(f"Unverified claim: {pattern}")
                confidence += 0.1
        
        # Normalize confidence
        confidence = min(confidence, 1.0)
        
        return confidence > 0.5, confidence, indicators

class InjectionDetector:
    """Detects potential injection attacks in prompts and inputs."""
    
    def __init__(self):
        # Common injection patterns
        self.injection_patterns = [
            r'(?i)(ignore|forget|disregard).*(previous|above|earlier).*(instruction|prompt|direction)',
            r'(?i)(system|developer|admin).*(mode|override|bypass)',
            r'(?i)(new|change|modify).*(instruction|prompt|role)',
            r'(?i)(act|behave|pretend).*(as|like).*(different|another)',
            r'(?i)(jailbreak|escape|break).*(restriction|limit|filter)',
            r'(?i)(tell|show|reveal).*(secret|hidden|private).*(information|data)',
            r'(?i)\bDAN\b',  # Do Anything Now
            r'(?i)(hypothetical|imagine|fictional).*(scenario|situation)'
        ]
        
        self.compiled_patterns = [re.compile(pattern) for pattern in self.injection_patterns]
    
    def detect_injection(self, text: str) -> Tuple[bool, float, List[str]]:
        """Detect injection attempts and return (has_injection, confidence, patterns)."""
        detected_patterns = []
        confidence = 0.0
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                detected_patterns.append(f"Injection pattern {i+1}")
                confidence += 0.4
        
        # Normalize confidence
        confidence = min(confidence, 1.0)
        
        return confidence > 0.3, confidence, detected_patterns

class SafetyLayer:
    """Main safety layer that coordinates all safety checks."""
    
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.hallucination_detector = HallucinationDetector()
        self.injection_detector = InjectionDetector()
        self.logger = logging.getLogger(__name__)
    
    def check_outbound_content_safety(self, content: str) -> SafetyResult:
        """Check safety of outbound content (responses, generated text)."""
        detected_issues = []
        risk_level = "low"
        sanitized_content = content
        
        # PII Detection
        has_pii, pii_types = self.pii_detector.detect_pii(content)
        if has_pii:
            detected_issues.extend([f"PII detected: {', '.join(pii_types)}"])
            risk_level = "high"
            sanitized_content = self.pii_detector.sanitize_pii(content)
        
        # Hallucination Detection
        has_hallucination, hallu_confidence, hallu_indicators = self.hallucination_detector.detect_hallucination(content)
        if has_hallucination:
            detected_issues.extend([f"Hallucination risk: {', '.join(hallu_indicators)}"])
            risk_level = "medium" if risk_level == "low" else "high"
        
        # Injection Detection
        has_injection, inj_confidence, inj_patterns = self.injection_detector.detect_injection(content)
        if has_injection:
            detected_issues.extend([f"Injection attempt: {', '.join(inj_patterns)}"])
            risk_level = "critical"
        
        # Calculate overall confidence
        confidence = 1.0 - (len(detected_issues) * 0.2)
        confidence = max(confidence, 0.0)
        
        is_safe = len(detected_issues) == 0
        
        result = SafetyResult(
            is_safe=is_safe,
            confidence=confidence,
            detected_issues=detected_issues,
            sanitized_content=sanitized_content if has_pii else None,
            risk_level=risk_level
        )
        
        self.logger.info(f"Content safety check: {'SAFE' if is_safe else 'UNSAFE'} (Risk: {risk_level})")
        return result
    
    def check_mutating_action_safety(self, action: Dict[str, Any]) -> SafetyResult:
        """Check safety of mutating actions (file operations, API calls, etc.)."""
        detected_issues = []
        risk_level = "low"
        
        action_type = action.get("type", "").lower()
        action_target = action.get("target", "")
        action_params = action.get("parameters", {})
        
        # Dangerous action types
        dangerous_actions = ["delete", "remove", "format", "destroy", "drop", "truncate"]
        if action_type in dangerous_actions:
            detected_issues.append(f"Dangerous action type: {action_type}")
            risk_level = "high"
        
        # System-level operations
        system_patterns = [r"system\(", r"exec\(", r"eval\(", r"__import__", r"subprocess\.call"]
        for pattern in system_patterns:
            if re.search(pattern, str(action_params)):
                detected_issues.append(f"System operation detected: {pattern}")
                risk_level = "critical"
        
        # File system operations on sensitive paths
        sensitive_paths = ["/etc", "/boot", "/sys", "/proc", "C:\\Windows", "C:\\System32"]
        for path in sensitive_paths:
            if path.lower() in action_target.lower():
                detected_issues.append(f"Sensitive path access: {path}")
                risk_level = "critical"
        
        # Network operations to untrusted destinations
        if action_type in ["http_request", "api_call", "network"]:
            url = action_params.get("url", "")
            if not url.startswith(("https://", "http://localhost", "http://127.0.0.1")):
                detected_issues.append(f"Untrusted network destination: {url}")
                risk_level = "medium" if risk_level == "low" else "high"
        
        # Calculate confidence
        confidence = 1.0 - (len(detected_issues) * 0.25)
        confidence = max(confidence, 0.0)
        
        is_safe = len(detected_issues) == 0
        
        result = SafetyResult(
            is_safe=is_safe,
            confidence=confidence,
            detected_issues=detected_issues,
            risk_level=risk_level
        )
        
        self.logger.info(f"Action safety check: {'SAFE' if is_safe else 'UNSAFE'} (Action: {action_type}, Risk: {risk_level})")
        return result

# Global safety layer instance
safety_layer = SafetyLayer()

# Public API functions
def check_outbound_content_safety(content: str) -> SafetyResult:
    """Check safety of outbound content."""
    return safety_layer.check_outbound_content_safety(content)

def check_mutating_action_safety(action: Dict[str, Any]) -> SafetyResult:
    """Check safety of mutating actions."""
    return safety_layer.check_mutating_action_safety(action)

if __name__ == "__main__":
    # Test examples
    safe_content = "This is a safe message about the weather."
    unsafe_content = "Contact me at john.doe@example.com or call 555-123-4567."
    
    print("=== Content Safety Tests ===")
    result1 = check_outbound_content_safety(safe_content)
    print(f"Safe content: {result1}")
    
    result2 = check_outbound_content_safety(unsafe_content)
    print(f"Unsafe content: {result2}")
    
    # Action safety tests
    safe_action = {"type": "read", "target": "data.txt"}
    unsafe_action = {"type": "delete", "target": "/etc/passwd"}
    
    print("\n=== Action Safety Tests ===")
    result3 = check_mutating_action_safety(safe_action)
    print(f"Safe action: {result3}")
    
    result4 = check_mutating_action_safety(unsafe_action)
    print(f"Unsafe action: {result4}")
