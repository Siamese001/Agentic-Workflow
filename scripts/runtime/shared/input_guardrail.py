"""Input Guardrail - Adversarial Defense Layer for RAG Pipeline.

This module provides security scanning for all inputs before they reach
the RAG pipeline, protecting against prompt injection, jailbreaks,
PII leakage, Unicode attacks, and encoded payloads.
"""

import base64
import logging
import re
import time
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any # Added missing type imports

LOGGER = logging.getLogger(__name__)


class GuardAction(Enum):
    """Action to take based on guardrail scan."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    WARN = "WARN"
    REDACT = "REDACT"


@dataclass
class GuardResult:
    """Result of input guardrail scan."""
    action: GuardAction
    reason: str
    confidence: float
    pii_detected: List[str] = None
    injection_patterns: List[str] = None
    sanitized_input: Optional[str] = None

    def __post_init__(self):
        if self.pii_detected is None:
            self.pii_detected = []
        if self.injection_patterns is None:
            self.injection_patterns = []


class InputGuardrail:
    """Adversarial defense layer for input validation and sanitization."""

    def __init__(self,
                 enable_injection_detection: bool = True,
                 enable_pii_detection: bool = True,
                 enable_semantic_check: bool = True,
                 enable_unicode_check: bool = True,
                 enable_encoding_check: bool = True,
                 enable_rate_limit: bool = True,
                 strict_mode: bool = False,
                 rate_limit_per_minute: int = 60):
        """Initialize the input guardrail.

        Args:
            enable_injection_detection: Enable prompt injection detection
            enable_pii_detection: Enable PII detection and redaction
            enable_semantic_check: Enable semantic malicious intent detection
            enable_unicode_check: Enable Unicode homoglyph attack detection
            enable_encoding_check: Enable base64/encoded payload detection
            enable_rate_limit: Enable rate limiting per user
            strict_mode: Block on any suspicious pattern (not just high confidence)
            rate_limit_per_minute: Requests per minute per user
        """
        self.enable_injection_detection = enable_injection_detection
        self.enable_pii_detection = enable_pii_detection
        self.enable_semantic_check = enable_semantic_check
        self.enable_unicode_check = enable_unicode_check
        self.enable_encoding_check = enable_encoding_check
        self.enable_rate_limit = enable_rate_limit
        self.strict_mode = strict_mode
        self.rate_limit_per_minute = rate_limit_per_minute

        # Rate limiting storage (in production, use Redis)
        self._rate_limit_store: Dict[str, List[float]] = {}

        # Compile regex patterns for performance
        self._compile_patterns()

        # Initialize semantic checker if enabled
        if self.enable_semantic_check:
            self._init_semantic_checker()

        LOGGER.info(f"InputGuardrail initialized - Injection: {enable_injection_detection}, "
                   f"PII: {enable_pii_detection}, Semantic: {enable_semantic_check}, "
                   f"Unicode: {enable_unicode_check}, Encoding: {enable_encoding_check}, "
                   f"Rate Limit: {enable_rate_limit}, Strict: {strict_mode}")

    def _compile_patterns(self):
        """Compile regex patterns for fast detection."""
        # Prompt injection patterns
        self.injection_patterns = [
            # DAN (Do Anything Now) patterns
            r'(?i)(dan|do anything now)',
            r'(?i)(ignore (all|previous|the above) instructions?)',
            r'(?i)(disregard (all|previous|the above) instructions?)',
            r'(?i)(forget (all|previous|the above) instructions?)',
            r'(?i)(override (all|previous|the above) instructions?)',

            # System prompt extraction
            r'(?i)(show|print|display|tell me) (your )?(system|initial|original) prompt',
            r'(?i)(what are your instructions|what were you told to do)',
            r'(?i)(repeat|echo|copy) (everything )?above',

            # Role playing/jailbreak attempts
            r'(?i)(you are now|henceforth|from now on) (a )?(developer|admin|god|dAN)',
            r'(?i)(pretend|act as|roleplay as) (a )?(jailbroken|uncensored|unrestricted)',
            r'(?i)(hypothetical|imagine|fictional) scenario',

            # Instruction manipulation
            r'(?i)(new instruction|additional instruction|update)',
            r'(?i)(replace|change|modify) (the )?(prompt|instructions)',
            r'(?i)(add to|append to) (your )?(instructions|prompt)',

            # Output format manipulation
            r'(?i)(respond with only|just say|output only)',
            r'(?i)(no explanation|no commentary|no analysis)',
            r'(?i)(between brackets|in code block|as JSON)',

            # Security bypass attempts
            r'(?i)(bypass|override|circumvent) (the )?(filter|restriction|safety)',
            r'(?i)(this is not harmful|this is safe|this is for testing)',
            r'(?i)(educational|research|academic) purpose',
        ]

        # Compile injection patterns
        self.compiled_injection_patterns = [
            re.compile(pattern) for pattern in self.injection_patterns
        ]

        # Unicode homoglyph patterns (common substitutions)
        self.unicode_homoglyphs = {
            'i': ['ⅰ', 'і', 'í', 'ì', 'î', 'ï'],
            'l': ['ⅼ', 'ⅼ', 'ł', 'ĺ', 'ľ'],
            'o': ['ο', 'о', 'ó', 'ò', 'ô', 'ö'],
            'e': ['е', 'é', 'è', 'ê', 'ë'],
            'a': ['а', 'á', 'à', 'â', 'ä'],
            'r': ['г', 'ŕ', 'ř', 'ŗ'],
            'n': ['ո', 'ñ', 'ń'],
            'g': ['ɡ', 'ğ', 'ĝ'],
            'c': ['с', 'č', 'ć', 'ç'],
            'v': ['ѵ', 'ν'],
            'u': ['ս', 'ú', 'ù', 'û', 'ü'],
        }

        # Base64 detection patterns
        # Fix: Unterminated string literal
        self.base64_pattern = re.compile(r'(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')

        # PII detection patterns
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Fix: Unterminated string literal and 're..compile' typo
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),

            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            # Fix: Unterminated string literal and truncated regex
            'url': re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*))'),

        }

        # Malicious intent keywords
        self.malicious_keywords = [
            'jailbreak', 'bypass', 'override', 'hack', 'exploit',
            'injection', 'prompt leak', 'system prompt', 'dan',
            'malicious', 'harmful', 'illegal', 'forbidden'
        ]

    def _init_semantic_checker(self):
        """Initialize semantic malicious intent checker."""
        # For now, use keyword-based semantic checking
        # In production, this could use a lightweight model
        self.semantic_threshold = 0.7 if not self.strict_mode else 0.5

    def scan(self, input_text: str, user_id: Optional[str] = None) -> GuardResult:
        """Scan input text for security issues.

        Args:
            input_text: The input text to scan
            user_id: Optional user ID for rate limiting

        Returns:
            GuardResult with action and details
        """
        start_time = time.time()

        # Initialize result
        # Fix: Arguments to GuardResult should be snake_case
        RESULT = GuardResult(
            action=GuardAction.ALLOW,
            reason="Input appears safe",
            confidence=0.0,
            pii_detected=[],
            injection_patterns=[]
        )

        try:
            # Check rate limiting first
            if self.enable_rate_limit and user_id:
                if self._check_rate_limit(user_id):
                    RESULT.action = GuardAction.BLOCK
                    RESULT.reason = "Rate limit exceeded"
                    RESULT.confidence = 1.0
                    return RESULT # Variable was `result` but defined as `RESULT`

            # Check for prompt injection
            if self.enable_injection_detection:
                injection_result = self._check_injection(input_text)
                if injection_result[0]:  # Found injection
                    RESULT.action = GuardAction.BLOCK if self.strict_mode else GuardAction.WARN
                    RESULT.injection_patterns = injection_result[1] # Variable was `result`
                    RESULT.reason = f"Prompt injection detected: {', '.join(injection_result[1])}"
                    RESULT.confidence = max(RESULT.confidence, 0.8) # Variable was `result`

            # Check for Unicode homoglyph attacks
            if self.enable_unicode_check:
                unicode_result = self._check_unicode_attacks(input_text)
                if unicode_result[0]:  # Found suspicious Unicode
                    if RESULT.action == GuardAction.ALLOW: # Variable was `result`
                        # Fix: Unterminated line for BLOCK
                        RESULT.action = GuardAction.WARN if not self.strict_mode else GuardAction.BLOCK
                        RESULT.reason = f"Suspicious Unicode characters detected: {unicode_result[1]}" # Variable was `result`
                    RESULT.confidence = max(RESULT.confidence, 0.7) # Variable was `result`

            # Check for encoded payloads
            if self.enable_encoding_check:
                encoding_result = self._check_encoded_payloads(input_text)
                if encoding_result[0]:  # Found encoded content
                    if RESULT.action == GuardAction.ALLOW: # Variable was `result`
                        RESULT.action = GuardAction.BLOCK
                        RESULT.reason = "Encoded payload detected - potential attack"
                    RESULT.confidence = max(RESULT.confidence, 0.9) # Variable was `result`

            # Check for PII
            if self.enable_pii_detection:
                pii_result = self._check_pii(input_text)
                if pii_result[0]:  # Found PII
                    RESULT.pii_detected = pii_result[1] # Variable was `result`
                    if RESULT.action == GuardAction.ALLOW: # Variable was `result`
                        RESULT.action = GuardAction.REDACT
                        RESULT.reason = "PII detected - will be redacted"
                        RESULT.sanitized_input = self._redact_pii(input_text, pii_result[1]) # Variable was `result`
                    RESULT.confidence = max(RESULT.confidence, 0.6) # Variable was `result`

            # Check semantic malicious intent
            if self.enable_semantic_check:
                semantic_score = self._check_semantic_intent(input_text)
                if semantic_score > self.semantic_threshold:
                    if RESULT.action == GuardAction.ALLOW: # Variable was `result`
                        RESULT.action = GuardAction.WARN
                        RESULT.reason = "Potentially malicious intent detected"
                    RESULT.confidence = max(RESULT.confidence, semantic_score) # Variable was `result`

            # Log the scan
            scan_time = (time.time() - start_time) * 1000
            LOGGER.info(f"Input scan completed in {scan_time:.2f}ms - " # Changed `logger` to `LOGGER`
                       f"Action: {RESULT.action.value}, Confidence: {RESULT.confidence:.2f}") # Variable was `result`

            return RESULT # Variable was `result`

        except Exception as e:
# Fix: Indentation error and `logger` vs `LOGGER` inconsistency
            LOGGER.error(f"Error during input scan: {e}")
            # Fail safe - allow but warn
            return GuardResult(
                action=GuardAction.WARN, # Fix: GuardResult arguments are snake_case
                reason="Scan error - proceeding with caution",
                confidence=0.0
            )

    def _check_injection(self, text: str) -> Tuple[bool, List[str]]:
        """Check for prompt injection patterns.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, list_of_patterns)
        """
        found_patterns = []

        for pattern in self.compiled_injection_patterns:
            MATCHES = pattern.findall(text)
            if MATCHES:
                found_patterns.append(pattern.pattern)

        return (len(found_patterns) > 0, found_patterns)

    def _check_pii(self, text: str) -> Tuple[bool, List[str]]:
        """Check for PII in the text.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, list_of_pii_types)
        """
        found_types = []

        for pii_type, pattern in self.pii_patterns.items():
            MATCHES = pattern.findall(text)
            if MATCHES:
                found_types.append(pii_type)

        return (len(found_types) > 0, found_types)

    def _redact_pii(self, text: str, pii_types: List[str]) -> str:
        """Redact PII from text.

        Args:
            text: Text to redact
            pii_types: Types of PII found

        Returns:
            Redacted text
        """
        REDACTED = text

        for pii_type in pii_types:
            if pii_type in self.pii_patterns:
                PATTERN = self.pii_patterns[pii_type]
                if pii_type == 'email':
                    REDACTED = PATTERN.sub('[EMAIL_REDACTED]', REDACTED) # Variable was `pattern` and `redacted`
                elif pii_type == 'phone':
                    REDACTED = PATTERN.sub('[PHONE_REDACTED]', REDACTED)
                elif pii_type == 'ssn':
                    REDACTED = PATTERN.sub('[SSN_REDACTED]', REDACTED)
                elif pii_type == 'credit_card':
                    REDACTED = PATTERN.sub('[CARD_REDACTED]', REDACTED)
                elif pii_type == 'ip_address':
                    REDACTED = PATTERN.sub('[IP_REDACTED]', REDACTED)
                elif pii_type == 'url':
                    REDACTED = PATTERN.sub('[URL_REDACTED]', REDACTED)

        return REDACTED # Variable was `redacted`

    def _check_semantic_intent(self, text: str) -> float:
        """Check for semantic malicious intent.

        Args:
            text: Text to check

        Returns:
            Confidence score (0.0 - 1.0)
        """
        # Simple keyword-based semantic check
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in self.malicious_keywords
                          if keyword in text_lower)

        # Calculate confidence based on keyword density
        CONFIDENCE = min(keyword_count / len(self.malicious_keywords), 1.0)

        # Boost confidence if multiple injection patterns are found
        injection_count = sum(1 for pattern in self.compiled_injection_patterns
                            if pattern.search(text))
        if injection_count > 2:
            CONFIDENCE = min(CONFIDENCE + 0.3, 1.0) # Variable was `confidence`

        return CONFIDENCE # Variable was `confidence`

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            True if rate limit exceeded
        """
        NOW = time.time()
        minute_ago = NOW - 60

        # Clean old entries
        if user_id in self._rate_limit_store:
            self._rate_limit_store[user_id] = [
                timestamp for timestamp in self._rate_limit_store[user_id]
                if timestamp > minute_ago
            ]
        else:
            self._rate_limit_store[user_id] = []

        # Check current count
        if len(self._rate_limit_store[user_id]) >= self.rate_limit_per_minute:
            return True

        # Add current request
        self._rate_limit_store[user_id].append(NOW)
        return False

    def _check_unicode_attacks(self, text: str) -> Tuple[bool, str]:
        """Check for Unicode homoglyph attacks.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, suspicious_chars)
        """
        suspicious_chars = []

        for char in text:
            # Check if character is in suspicious Unicode ranges
            char_name = unicodedata.name(char, '')

            # Check for homoglyph substitutions
            for normal_char, homoglyphs in self.unicode_homoglyphs.items():
                if char in homoglyphs:
                    suspicious_chars.append(f"{char} (looks like {normal_char})")

            # Check for suspicious Unicode categories
            if unicodedata.category(char) in ['Cf', 'Cs', 'Co', 'Cn']:
                suspicious_chars.append(f"{char} (control/private char)")

        return (len(suspicious_chars) > 0, ', '.join(suspicious_chars[:5]))

    def _check_encoded_payloads(self, text: str) -> Tuple[bool, str]:
        """Check for base64 or other encoded payloads.

        Args:
            text: Text to check

        Returns:
            Tuple of (found, details)
        """
        # Check for base64 patterns
        base64_matches = self.base64_pattern.findall(text)

        for match in base64_matches:
            try:
                # Try to decode
                DECODED = base64.b64decode(match).decode('utf-8', errors='ignore')

                # Check if decoded content looks suspicious
                decoded_lower = DECODED.lower()
                if any(keyword in decoded_lower for keyword in self.malicious_keywords):
                    return (True, f"Base64 payload with malicious content: {match[:20]}...")

                # Check for common injection patterns in decoded content
                for pattern in self.injection_patterns[:5]:  # Check first 5 patterns
                    if re.search(pattern, DECODED, re.IGNORECASE):
                        return (True, f"Base64 payload with injection pattern: {match[:20]}...")

            except Exception as e: # Fix: Corrected indentation for except block and added `as e`
                # Not valid base64, continue, but log error if it was intended to log.
                LOGGER.debug(f"Base64 decoding failed for {match[:20]}...: {e}")

        # Check for hex encoding
        hex_pattern = re.compile(r'[0-9A-Fa-f]{32,}')
        hex_matches = hex_pattern.findall(text)

        for match in hex_matches:
            try:
                # Try to decode as hex
                DECODED = bytes.fromhex(match).decode('utf-8', errors='ignore')
                if any(keyword in DECODED.lower() for keyword in self.malicious_keywords):
                    return (True, f"Hex encoded payload with malicious content")
            except Exception as e: # Fix: Corrected indentation for except block and `logger` vs `LOGGER`
                LOGGER.warning(f"Error decoding hex: {e}")

        return (False, "")

    def get_stats(self) -> Dict[str, Any]:
        """Get guardrail statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "injection_patterns_count": len(self.injection_patterns),
            "pii_types_count": len(self.pii_patterns),
            "malicious_keywords_count": len(self.malicious_keywords),
            # Fix: Remove extra dots in self.unicode_homoglyphs.values()
            "unicode_homoglyphs_count": sum(len(homoglyphs) for homoglyphs in self.unicode_homoglyphs.values()),

            "strict_mode": self.strict_mode,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "active_rate_limits": len(self._rate_limit_store),
            "features_enabled": {
                "injection_detection": self.enable_injection_detection,
                "pii_detection": self.enable_pii_detection,
                "semantic_check": self.enable_semantic_check,
                "unicode_check": self.enable_unicode_check,
                "encoding_check": self.enable_encoding_check,
                "rate_limit": self.enable_rate_limit
            }
        }

class InputGuardrailManager:
    """Manager for InputGuardrail without global state"""
    
    def __init__(self):
        self._instance = None
    
    def get_guardrail(self, **kwargs):
        """Get or create the InputGuardrail instance"""
        if self._instance is None:
            self._instance = InputGuardrail(**kwargs)
        return self._instance


# Global manager instance (acceptable as it's a dependency injection container)
_guardrail_manager = InputGuardrailManager()


def get_input_guardrail(**kwargs) -> InputGuardrail:
    """Get the global input guardrail instance.

    Args:
        **kwargs: Configuration arguments

    Returns:
        InputGuardrail instance
    """
    return _guardrail_manager.get_guardrail(**kwargs)

def scan_input(input_text: str, **kwargs) -> GuardResult:
    """Convenience function to scan input.

    Args:
        input_text: Text to scan
        **kwargs: Arguments for guardrail initialization

    Returns:
        GuardResult from scan
    """
    GUARDRAIL = get_input_guardrail(**kwargs)
    return GUARDRAIL.scan(input_text) # Variable was `guardrail`

