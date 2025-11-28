"""LIC Validation Toolkit - L5 reusable rule-check helpers for safety/validation.

Implements nuclear prompt requirements for deterministic validation helpers:
- Provide reusable, deterministic rule-check helpers for LIC safety/validation
- L5 only: no LLM, no RAG, pure rules
- Helpers for placeholders, CTA alignment, tone/persona, factual markers
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SafetyViolation:
    """Individual safety violation found during validation."""
    violation_type: str                  # type of violation
    severity: str                        # "LOW", "MEDIUM", "HIGH"
    description: str                     # human-readable description
    position: Optional[int] = None       # character position in message
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICValidationToolkit:
    """L5 toolkit for deterministic LIC message validation.
    
    Provides pure rule-based validation helpers for safety,
    persona consistency, and factual accuracy checking.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC validation toolkit."""
        self.telemetry_bus = telemetry_bus
        
        # Placeholder patterns to detect
        self.placeholder_patterns = [
            r'\[.*?\]',                    # [placeholder] format
            r'\{.*?\}',                    # {placeholder} format
            r'<.*?>',                      # <placeholder> format
            r'PLACEHOLDER[_\s]*\w+',       # PLACEHOLDER_text format
            r'XXX+',                       # XXX, XXXX, etc.
            r'\.\.\.',                     # ... (incomplete)
            r'__.*__',                     # __placeholder__ format
        ]
        
        # Aggressive CTA patterns by archetype
        self.aggressive_cta_patterns = {
            "EXECUTIVE": [
                r'call\s+me\s+now', r'urgent', r'immediately', 
                r'right\s+away', r'don\'t\s+delay', r'critical'
            ],
            "SENIOR_TA": [
                r'buy\s+now', r'purchase', r'payment', 
                r'credit\s+card', r'money\s+back'
            ],
            "RECRUITER": [
                r'harass', r'spam', r'annoy', 
                r'bother', r'pester'
            ],
        }
        
        # Tone mismatch indicators by archetype
        self.tone_mismatch_patterns = {
            "EXECUTIVE": [
                r'lol', r'haha', r'omg', r'awesome!', 
                r'cool!', r'wow!', r'!!!{2,}'
            ],
            "SENIOR_TA": [
                r'synergy', r'paradigm', r'leverage', 
                r'circle\s+back', r'touch\s+base'
            ],
            "RECRUITER": [
                r'quantum', r'blockchain', r'cryptocurrency',
                r'enterprise\s+architecture', r'scalability'
            ],
        }
        
        # Factual marker patterns
        self.factual_patterns = [
            r'\d+%$',                     # percentages
            r'\$\d+[kmb]?',               # dollar amounts
            r'\d+x\s+(increase|growth|improvement)',  # multipliers
            r'\d+\s+years?',              # time periods
            r'\d+\s+(people|employees|team members)',  # team sizes
        ]
    
    def check_placeholders(self, message: str) -> List[SafetyViolation]:
        """Check for placeholder tokens in message.
        
        Args:
            message: The message to validate
            
        Returns:
            List of placeholder violations found
        """
        violations = []
        
        for pattern in self.placeholder_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="placeholder_token",
                    severity="HIGH",
                    description=f"Placeholder token detected: '{match.group()}'",
                    position=match.start(),
                    metadata={"pattern": pattern, "matched_text": match.group()},
                )
                violations.append(violation)
        
        return violations
    
    def check_cta_alignment(self, message: str, archetype: str, cta_style: str) -> List[SafetyViolation]:
        """Check if CTA is too aggressive for the archetype.
        
        Args:
            message: The message to validate
            archetype: Target archetype ("EXECUTIVE", "SENIOR_TA", "RECRUITER")
            cta_style: Intended CTA style ("light_touch", "exploratory_call", "direct")
            
        Returns:
            List of CTA alignment violations found
        """
        violations = []
        archetype_upper = archetype.upper()
        
        # Check for aggressive patterns that don't match archetype
        if archetype_upper in self.aggressive_cta_patterns:
            aggressive_patterns = self.aggressive_cta_patterns[archetype_upper]
            
            for pattern in aggressive_patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    severity = "HIGH" if archetype_upper == "EXECUTIVE" else "MEDIUM"
                    
                    violation = SafetyViolation(
                        violation_type="cta_too_aggressive",
                        severity=severity,
                        description=f"CTA too aggressive for {archetype}: '{match.group()}'",
                        position=match.start(),
                        metadata={
                            "archetype": archetype,
                            "cta_style": cta_style,
                            "pattern": pattern,
                            "matched_text": match.group(),
                        },
                    )
                    violations.append(violation)
        
        # Check CTA style consistency
        cta_violations = self._check_cta_style_consistency(message, archetype, cta_style)
        violations.extend(cta_violations)
        
        return violations
    
    def _check_cta_style_consistency(self, message: str, archetype: str, cta_style: str) -> List[SafetyViolation]:
        """Check if CTA style matches the intended style."""
        violations = []
        
        # Define patterns for each CTA style
        style_patterns = {
            "light_touch": [
                r'if\s+you\'re\s+interested', r'when\s+you\s+have\s+a\s+moment',
                r'no\s+pressure', r'at\s+your\s+convenience'
            ],
            "exploratory_call": [
                r'brief\s+call', r'quick\s+chat', r'15\s+minutes',
                r'exploratory\s+discussion', r'initial\s+conversation'
            ],
            "direct": [
                r'call\s+me', r'schedule\s+meeting', r'let\'s\s+connect',
                r'reach\s+out\s+directly', r'contact\s+me'
            ],
        }
        
        # Check if message contains patterns from other styles (inconsistency)
        if cta_style in style_patterns:
            intended_patterns = style_patterns[cta_style]
            
            # Look for patterns from other styles
            for other_style, other_patterns in style_patterns.items():
                if other_style == cta_style:
                    continue
                
                for pattern in other_patterns:
                    matches = re.finditer(pattern, message, re.IGNORECASE)
                    for match in matches:
                        violation = SafetyViolation(
                            violation_type="cta_style_inconsistency",
                            severity="MEDIUM",
                            description=f"CTA style inconsistency: using {other_style} pattern with {cta_style} style",
                            position=match.start(),
                            metadata={
                                "intended_style": cta_style,
                                "detected_style": other_style,
                                "pattern": pattern,
                                "matched_text": match.group(),
                            },
                        )
                        violations.append(violation)
        
        return violations
    
    def check_tone_and_persona(self, message: str, archetype: str) -> List[SafetyViolation]:
        """Check for tone and persona mismatches.
        
        Args:
            message: The message to validate
            archetype: Target archetype ("EXECUTIVE", "SENIOR_TA", "RECRUITER")
            
        Returns:
            List of tone/persona violations found
        """
        violations = []
        archetype_upper = archetype.upper()
        
        # Check for tone mismatch patterns
        if archetype_upper in self.tone_mismatch_patterns:
            mismatch_patterns = self.tone_mismatch_patterns[archetype_upper]
            
            for pattern in mismatch_patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    violation = SafetyViolation(
                        violation_type="tone_mismatch",
                        severity="MEDIUM",
                        description=f"Tone mismatch for {archetype}: '{match.group()}'",
                        position=match.start(),
                        metadata={
                            "archetype": archetype,
                            "pattern": pattern,
                            "matched_text": match.group(),
                        },
                    )
                    violations.append(violation)
        
        # Additional tone checks
        violations.extend(self._check_message_length_tone(message, archetype))
        violations.extend(self._check_formality_level(message, archetype))
        
        return violations
    
    def _check_message_length_tone(self, message: str, archetype: str) -> List[SafetyViolation]:
        """Check if message length is appropriate for archetype."""
        violations = []
        word_count = len(message.split())
        
        # Length guidelines by archetype
        length_guidelines = {
            "EXECUTIVE": {"min": 50, "max": 200},
            "SENIOR_TA": {"min": 100, "max": 400},
            "RECRUITER": {"min": 75, "max": 300},
        }
        
        if archetype.upper() in length_guidelines:
            guidelines = length_guidelines[archetype.upper()]
            
            if word_count < guidelines["min"]:
                violation = SafetyViolation(
                    violation_type="message_too_short",
                    severity="LOW",
                    description=f"Message too short for {archetype}: {word_count} words (min: {guidelines['min']})",
                    metadata={
                        "archetype": archetype,
                        "word_count": word_count,
                        "min_expected": guidelines["min"],
                    },
                )
                violations.append(violation)
            
            elif word_count > guidelines["max"]:
                violation = SafetyViolation(
                    violation_type="message_too_long",
                    severity="MEDIUM",
                    description=f"Message too long for {archetype}: {word_count} words (max: {guidelines['max']})",
                    metadata={
                        "archetype": archetype,
                        "word_count": word_count,
                        "max_expected": guidelines["max"],
                    },
                )
                violations.append(violation)
        
        return violations
    
    def _check_formality_level(self, message: str, archetype: str) -> List[SafetyViolation]:
        """Check formality level appropriateness."""
        violations = []
        
        # Informal indicators
        informal_patterns = [
            r'hey\s+\w+', r'what\'s\s+up', r'yo', 
            r'gonna', r'wanna', r'gotta'
        ]
        
        # Overly formal indicators
        formal_patterns = [
            r'dear\s+sir\s+or\s+madam', r'to\s+whom\s+it\s+may\s+concern',
            r'respectfully\s+yours', r'your\s+humble\s+servant'
        ]
        
        # Check based on archetype expectations
        if archetype.upper() == "EXECUTIVE":
            # Executives expect formal but not overly formal
            for pattern in informal_patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    violation = SafetyViolation(
                        violation_type="informal_language",
                        severity="MEDIUM",
                        description=f"Too informal for executive: '{match.group()}'",
                        position=match.start(),
                        metadata={
                            "archetype": archetype,
                            "pattern": pattern,
                            "matched_text": match.group(),
                        },
                    )
                    violations.append(violation)
        
        # Check for overly formal language (generally inappropriate)
        for pattern in formal_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="overly_formal_language",
                    severity="LOW",
                    description=f"Overly formal language: '{match.group()}'",
                    position=match.start(),
                    metadata={
                        "pattern": pattern,
                        "matched_text": match.group(),
                    },
                )
                violations.append(violation)
        
        return violations
    
    def check_factual_markers(self, message: str, signals: List[Dict[str, Any]]) -> List[SafetyViolation]:
        """Check for factual markers and verify against signals.
        
        Args:
            message: The message to validate
            signals: List of research signals for fact verification
            
        Returns:
            List of factual accuracy violations found
        """
        violations = []
        
        # Extract factual claims from message
        factual_claims = self._extract_factual_claims(message)
        
        # Verify each claim against available signals
        for claim in factual_claims:
            verification_result = self._verify_claim_against_signals(claim, signals)
            
            if not verification_result["verified"]:
                violation = SafetyViolation(
                    violation_type="unverified_factual_claim",
                    severity="HIGH" if claim["confidence"] > 0.8 else "MEDIUM",
                    description=f"Unverified factual claim: '{claim['text']}'",
                    position=claim["position"],
                    metadata={
                        "claim_text": claim["text"],
                        "claim_type": claim["type"],
                        "confidence": claim["confidence"],
                        "verification_details": verification_result,
                    },
                )
                violations.append(violation)
        
        return violations
    
    def _extract_factual_claims(self, message: str) -> List[Dict[str, Any]]:
        """Extract factual claims from message."""
        claims = []
        
        # Find factual markers
        for pattern in self.factual_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                # Extract context around the factual marker
                start = max(0, match.start() - 50)
                end = min(len(message), match.end() + 50)
                context = message[start:end].strip()
                
                claim = {
                    "text": match.group(),
                    "type": self._classify_factual_claim_type(match.group()),
                    "position": match.start(),
                    "context": context,
                    "confidence": self._estimate_claim_confidence(match.group()),
                }
                claims.append(claim)
        
        return claims
    
    def _classify_factual_claim_type(self, claim_text: str) -> str:
        """Classify the type of factual claim."""
        if "%" in claim_text:
            return "percentage"
        elif "$" in claim_text:
            return "financial"
        elif "x" in claim_text.lower() and ("increase" in claim_text.lower() or "growth" in claim_text.lower()):
            return "multiplier"
        elif "year" in claim_text.lower():
            return "time_period"
        elif any(word in claim_text.lower() for word in ["people", "employees", "team"]):
            return "team_size"
        else:
            return "general"
    
    def _estimate_claim_confidence(self, claim_text: str) -> float:
        """Estimate confidence level of a factual claim."""
        # Higher confidence for specific numbers
        if re.match(r'^\d+%$', claim_text):
            return 0.9
        elif re.match(r'^\$\d+[kmb]?$', claim_text):
            return 0.8
        elif re.match(r'^\d+x\s+', claim_text):
            return 0.7
        else:
            return 0.6
    
    def _verify_claim_against_signals(self, claim: Dict[str, Any], signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify a claim against available research signals."""
        if not signals:
            return {"verified": False, "reason": "No signals available for verification"}
        
        claim_text = claim["text"].lower()
        claim_type = claim["type"]
        
        # Look for matching information in signals
        for signal in signals:
            if isinstance(signal, dict):
                signal_text = signal.get("text", "").lower()
                
                # Check for direct matches or close variants
                if claim_text in signal_text or signal_text in claim_text:
                    return {"verified": True, "signal_id": signal.get("id")}
                
                # Check for type-specific verification
                if claim_type == "percentage" and "%" in signal_text:
                    if any(char in signal_text for char in claim_text if char.isdigit()):
                        return {"verified": True, "signal_id": signal.get("id")}
                
                elif claim_type == "financial" and "$" in signal_text:
                    if any(char in signal_text for char in claim_text if char.isdigit()):
                        return {"verified": True, "signal_id": signal.get("id")}
        
        return {"verified": False, "reason": "No matching signal found"}
    
    def validate_message(self, message: str, archetype: str, cta_style: str, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive message validation.
        
        Args:
            message: The message to validate
            archetype: Target archetype
            cta_style: Intended CTA style
            signals: Research signals for fact verification
            
        Returns:
            Comprehensive validation results
        """
        all_violations = []
        
        # Run all validation checks
        all_violations.extend(self.check_placeholders(message))
        all_violations.extend(self.check_cta_alignment(message, archetype, cta_style))
        all_violations.extend(self.check_tone_and_persona(message, archetype))
        all_violations.extend(self.check_factual_markers(message, signals))
        
        # Count violations by severity
        severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for violation in all_violations:
            severity = violation.severity.upper()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Determine overall validation status
        is_valid = severity_counts["HIGH"] == 0 and severity_counts["MEDIUM"] <= 2
        
        # Record telemetry (best-effort)
        self._safe_record_telemetry(message, all_violations, is_valid)
        
        return {
            "is_valid": is_valid,
            "violations": all_violations,
            "severity_counts": severity_counts,
            "total_violations": len(all_violations),
        }
    
    def _safe_record_telemetry(self, message: str, violations: List[SafetyViolation], is_valid: bool) -> None:
        """Record telemetry event safely without breaking validation."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_message_validation_completed",
                layer="L5",
                payload={
                    "message_length": len(message),
                    "total_violations": len(violations),
                    "is_valid": is_valid,
                    "violation_types": list(set(v.violation_type for v in violations)),
                },
            )
        except Exception:
            # Telemetry failures should never break validation logic
            logger.debug("Failed to record telemetry for LIC message validation")
