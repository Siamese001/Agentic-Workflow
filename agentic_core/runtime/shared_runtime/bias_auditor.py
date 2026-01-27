from __future__ import annotations

"""
Bias Auditor - Shim layer for UnifiedSafetyDetectorAgent
Phase 5 Migration: Migrated from BiasAuditorAgent to UnifiedSafetyDetectorAgent
"""

from dataclasses import dataclass
from enum import Enum

from agentic_core.L5_safety.unified.UnifiedSafetyDetectorAgent import (
    UnifiedSafetyDetectorAgent,
    SafetyThreat,
    SafetyThreatType,
    ThreatSeverity,
)


# Legacy compatibility types
class BiasType(Enum):
    """Types of bias to detect (legacy compatibility)."""
    GENDER = "gender"
    AGE = "age"
    RACE = "race"
    DISABILITY = "disability"
    AFFILIATION = "affiliation"
    SOCIOECONOMIC = "socioeconomic"
    APPEARANCE = "appearance"


@dataclass
class BiasMatch:
    """Single bias detection match (legacy compatibility)."""
    BiasType: BiasType
    phrase: str
    context: str
    Severity: float


@dataclass
class BiasResult:
    """Bias detection result (legacy compatibility)."""
    has_bias: bool
    bias_types: list[BiasType]
    flagged_phrases: list[str]
    matches: list[BiasMatch]
    confidence_score: float
    recommendations: list[str]

    def get_critical_biases(self) -> list[BiasMatch]:
        """Get high-Severity bias matches."""
        return [m for m in self.matches if m.Severity > 0.7]


# Compatibility wrapper class
class BiasAuditorAgent:
    """Legacy compatibility wrapper for UnifiedSafetyDetectorAgent."""
    
    def __init__(self, enable_logging: bool = True):
        """Initialize bias auditor using UnifiedSafetyDetectorAgent."""
        self._detector = UnifiedSafetyDetectorAgent()
        self.enable_logging = enable_logging
    
    def audit_content(self, content: str) -> BiasResult:
        """Check for biased language patterns using UnifiedSafetyDetectorAgent."""
        if not content:
            return BiasResult(
                has_bias=False,
                bias_types=[],
                flagged_phrases=[],
                matches=[],
                confidence_score=0.0,
                recommendations=["Content appears neutral and inclusive"],
            )
        
        # Use UnifiedSafetyDetectorAgent to detect bias
        threats = self._detector.detect_bias(content)
        
        # Convert SafetyThreat list to legacy BiasResult format
        has_bias = len(threats) > 0
        flagged_phrases = [t.details.get("matched_text", "") for t in threats]
        confidence_score = min(len(threats) / 10.0, 1.0)
        
        # Map to legacy BiasMatch format
        matches = []
        for threat in threats:
            matches.append(BiasMatch(
                BiasType=BiasType.GENDER,  # Default, as UnifiedSafetyDetectorAgent doesn't categorize
                phrase=threat.details.get("matched_text", ""),
                context=threat.details.get("text_preview", ""),
                Severity=0.5 if threat.severity == ThreatSeverity.MEDIUM else 0.8,
            ))
        
        recommendations = [
            "Consider using more inclusive language",
            "Review flagged phrases for potential bias",
        ] if has_bias else ["Content appears neutral and inclusive"]
        
        return BiasResult(
            has_bias=has_bias,
            bias_types=[BiasType.GENDER] if has_bias else [],
            flagged_phrases=flagged_phrases,
            matches=matches,
            confidence_score=confidence_score,
            recommendations=recommendations,
        )


def audit_bias(content: str) -> BiasResult:
    """Convenience function to audit content for bias."""
    auditor = BiasAuditorAgent()
    return auditor.audit_content(content)


# Factory function for compatibility
def create_bias_auditor() -> BiasAuditorAgent:
    """Factory function to create bias auditor."""
    return BiasAuditorAgent()


__all__ = [
    "BiasType",
    "BiasMatch",
    "BiasResult",
    "BiasAuditorAgent",
    "audit_bias",
    "create_bias_auditor",
]
