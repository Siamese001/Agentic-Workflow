"""PII Policy V1 Enforcer - Enforces old PII policy for backward compatibility.

This module enforces the old, looser PII policy for backward compatibility tests,
ensuring legacy systems continue to work with the new security framework.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Pattern
import logging
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of PII in legacy system."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"


class PIIAction(Enum):
    """Actions for PII detection."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    MASK = "mask"
    REDACT = "redact"


@dataclass
class PIIPattern:
    """Legacy PII pattern definition."""
    pii_type: PIIType
    pattern: str
    description: str
    confidence: float = 0.8
    action: PIIAction = PIIAction.WARN


@dataclass
class PIIPolicy:
    """Legacy PII policy."""
    policy_name: str
    version: str
    patterns: List[PIIPattern] = field(default_factory=list)
    strict_mode: bool = False
    allow_list: List[str] = field(default_factory=list)
    block_list: List[str] = field(default_factory=list)


@dataclass
class PIIResult:
    """Result of PII detection."""
    detected: bool
    pii_type: Optional[PIIType] = None
    matches: List[Dict[str, Any]] = field(default_factory=list)
    action_taken: Optional[PIIAction] = None
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)


class PIIPolicyV1Enforcer:
    """Enforcer for legacy PII policy v1."""
    
    def __init__(self, policy: Optional[PIIPolicy] = None):
        self.policy = policy or self._create_default_policy()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._compiled_patterns: Dict[PIIType, List[Pattern]] = {}
        self._compile_patterns()
    
    def check_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> PIIResult:
        """Check text for PII using legacy policy.
        
        Args:
            text: Text to check
            context: Optional context information
            
        Returns:
            PIIResult: PII detection result
        """
        self.logger.debug(f"Checking text for PII using v1 policy")
        
        result = PIIResult(detected=False)
        
        # Check each pattern
        for pii_pattern in self.policy.patterns:
            matches = self._check_pattern(text, pii_pattern)
            
            if matches:
                result.detected = True
                result.pii_type = pii_pattern.pii_type
                result.matches.extend(matches)
                result.confidence = max(result.confidence, pii_pattern.confidence)
                
                # Determine action
                if self.policy.strict_mode:
                    result.action_taken = PIIAction.BLOCK
                else:
                    result.action_taken = pii_pattern.action
                
                # Add warning
                if result.action_taken in [PIIAction.WARN, PIIAction.BLOCK]:
                    result.warnings.append(
                        f"PII detected: {pii_pattern.pii_type.value} - {pii_pattern.description}"
                    )
        
        return result
    
    def check_data(self, data: Any, context: Optional[Dict[str, Any]] = None) -> PIIResult:
        """Check data structure for PII.
        
        Args:
            data: Data to check
            context: Optional context information
            
        Returns:
            PIIResult: PII detection result
        """
        result = PIIResult(detected=False)
        
        if isinstance(data, str):
            return self.check_text(data, context)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    sub_result = self.check_text(value, context)
                    if sub_result.detected:
                        result.detected = True
                        result.matches.extend(sub_result.matches)
                        result.confidence = max(result.confidence, sub_result.confidence)
                        result.warnings.extend(sub_result.warnings)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    sub_result = self.check_text(item, context)
                    if sub_result.detected:
                        result.detected = True
                        result.matches.extend(sub_result.matches)
                        result.confidence = max(result.confidence, sub_result.confidence)
                        result.warnings.extend(sub_result.warnings)
        
        return result
    
    def sanitize_text(self, text: str, action: Optional[PIIAction] = None) -> str:
        """Sanitize text by applying PII action.
        
        Args:
            text: Text to sanitize
            action: Action to apply (uses policy default if not provided)
            
        Returns:
            str: Sanitized text
        """
        if not action:
            # Check what PII is present
            result = self.check_text(text)
            action = result.action_taken or PIIAction.WARN
        
        if action == PIIAction.ALLOW:
            return text
        elif action == PIIAction.MASK:
            return self._mask_pii(text)
        elif action == PIIAction.REDACT:
            return self._redact_pii(text)
        else:
            return text
    
    def update_policy(self, policy: PIIPolicy) -> None:
        """Update the PII policy.
        
        Args:
            policy: New PII policy
        """
        self.policy = policy
        self._compile_patterns()
        self.logger.info(f"Updated PII policy to: {policy.policy_name} v{policy.version}")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self._compiled_patterns.clear()
        
        for pii_pattern in self.policy.patterns:
            if pii_pattern.pii_type not in self._compiled_patterns:
                self._compiled_patterns[pii_pattern.pii_type] = []
            
            try:
                compiled = re.compile(pii_pattern.pattern, re.IGNORECASE)
                self._compiled_patterns[pii_pattern.pii_type].append(compiled)
            except re.error as e:
                self.logger.error(f"Failed to compile pattern {pii_pattern.pattern}: {e}")
    
    def _check_pattern(self, text: str, pattern: PIIPattern) -> List[Dict[str, Any]]:
        """Check text for specific PII pattern.
        
        Args:
            text: Text to check
            pattern: PII pattern to check
            
        Returns:
            List[Dict]: List of matches
        """
        matches = []
        compiled_patterns = self._compiled_patterns.get(pattern.pii_type, [])
        
        for compiled in compiled_patterns:
            for match in compiled.finditer(text):
                matches.append({
                    "type": pattern.pii_type.value,
                    "pattern": pattern.pattern,
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": pattern.confidence
                })
        
        return matches
    
    def _mask_pii(self, text: str) -> str:
        """Mask PII in text.
        
        Args:
            text: Text to mask
            
        Returns:
            str: Masked text
        """
        masked_text = text
        
        for pii_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                # Replace with masked version
                masked_text = pattern.sub(lambda m: self._mask_match(m.group()), masked_text)
        
        return masked_text
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII in text.
        
        Args:
            text: Text to redact
            
        Returns:
            str: Redacted text
        """
        redacted_text = text
        
        for pii_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                # Replace with redaction marker
                redacted_text = pattern.sub("[REDACTED]", redacted_text)
        
        return redacted_text
    
    def _mask_match(self, match: str) -> str:
        """Mask a matched PII value.
        
        Args:
            match: Matched value
            
        Returns:
            str: Masked value
        """
        if len(match) <= 4:
            return "*" * len(match)
        else:
            return match[:2] + "*" * (len(match) - 4) + match[-2:]
    
    def _create_default_policy(self) -> PIIPolicy:
        """Create default legacy PII policy."""
        patterns = [
            PIIPattern(
                pii_type=PIIType.EMAIL,
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                description="Email address",
                confidence=0.9,
                action=PIIAction.WARN
            ),
            PIIPattern(
                pii_type=PIIType.PHONE,
                pattern=r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
                description="Phone number",
                confidence=0.8,
                action=PIIAction.WARN
            ),
            PIIPattern(
                pii_type=PIIType.SSN,
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                description="Social Security Number",
                confidence=0.95,
                action=PIIAction.BLOCK
            ),
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                description="Credit card number",
                confidence=0.9,
                action=PIIAction.BLOCK
            ),
            PIIPattern(
                pii_type=PIIType.IP_ADDRESS,
                pattern=r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                description="IP address",
                confidence=0.7,
                action=PIIAction.WARN
            )
        ]
        
        return PIIPolicy(
            policy_name="legacy_pii_policy_v1",
            version="1.0",
            patterns=patterns,
            strict_mode=False
        )


# Factory function for easy instantiation
def create_pii_v1_enforcer(strict_mode: bool = False, **kwargs) -> PIIPolicyV1Enforcer:
    """Create a configured PII v1 enforcer."""
    policy = PIIPolicy(
        policy_name="legacy_pii_policy_v1",
        version="1.0",
        strict_mode=strict_mode,
        **kwargs
    )
    return PIIPolicyV1Enforcer(policy)


# Global enforcer instance
_global_enforcer = create_pii_v1_enforcer()


def check_text_for_pii(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Check text for PII using legacy v1 policy.
    
    Args:
        text: Text to check
        context: Optional context
        
    Returns:
        Dict: PII check result
    """
    result = _global_enforcer.check_text(text, context)
    
    return {
        "detected": result.detected,
        "pii_type": result.pii_type.value if result.pii_type else None,
        "matches": result.matches,
        "action_taken": result.action_taken.value if result.action_taken else None,
        "confidence": result.confidence,
        "warnings": result.warnings
    }


def sanitize_pii_text(text: str, action: str = "warn") -> str:
    """Sanitize text containing PII.
    
    Args:
        text: Text to sanitize
        action: Action to take
        
    Returns:
        str: Sanitized text
    """
    return _global_enforcer.sanitize_text(text, PIIAction(action))
