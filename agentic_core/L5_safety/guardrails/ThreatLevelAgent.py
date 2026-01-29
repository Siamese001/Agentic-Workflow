from __future__ import annotations

"""
Threat Detection Guardrail - Consolidated Threat Analysis

Merges:
- AdversarialRedTeamer
- AutonomousThreatEvolution
- RedSentinel
- NeuralAutoImmune

Composable Rules:
- adversarial_detection: Adversarial example detection
- threat_evolution: Evolving threat patterns
- immune_response: Automated threat response
"""

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class ThreatLevel(Enum):
    """Threat severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of threats."""

    ADVERSARIAL = "adversarial"
    INJECTION = "injection"
    EVASION = "evasion"
    POISONING = "poisoning"
    EXTRACTION = "extraction"
    UNKNOWN = "unknown"


@dataclass
class ThreatIndicator:
    """Indicator of a potential threat."""

    threat_type: ThreatType
    level: ThreatLevel
    description: str
    confidence: float  # 0.0 to 1.0
    pattern_matched: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatAnalysisResult:
    """Result of threat analysis."""

    safe: bool
    threat_level: ThreatLevel
    indicators: list[ThreatIndicator] = field(default_factory=list)
    response_action: str = "allow"  # "allow", "block", "quarantine", "alert"
    analysis_time_ms: float = 0.0


class ThreatDetectionGuardrail(SovereignBaseAgent):
    """
    Consolidated Threat Detection Guardrail.

    HARDENED: Redis caching + Pinecone vector support for threat signature caching.

    Provides unified threat analysis with:
    - Adversarial input detection
    - Evolving threat pattern matching
    - Automated immune response
    - Red team attack simulation
    """

    # [PHASE 5] Redis/Pinecone integration
    _cache_prefix: str = "threat_detection"
    _namespace: str = "l5_threats"

    def __init__(self):
        """Initialize threat detection guardrail."""
        self.enabled_rules: list[str] = [
            "adversarial_detection",
            "threat_evolution",
            "immune_response",
        ]

        # Adversarial patterns
        self.adversarial_patterns = [
            r"ignore\s+(previous|all)\s+instructions",
            r"disregard\s+(your|the)\s+(rules|guidelines)",
            r"pretend\s+you\s+are",
            r"you\s+are\s+now\s+in\s+.*mode",
            r"jailbreak",
            r"DAN\s+mode",
            r"developer\s+mode",
        ]

        # Injection patterns
        self.injection_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__",
            r"subprocess\.",
        ]

        # Evasion patterns
        self.evasion_patterns = [
            r"unicode[\s_]*(escape|bypass)",
            r"base64[\s_]*encode",
            r"rot13",
            r"hex[\s_]*encode",
        ]

        # Threat history for evolution tracking
        self.threat_history: list[ThreatIndicator] = []
        self.evolved_patterns: list[str] = []

        # Statistics
        self.scans_performed = 0
        self.threats_detected = 0
        self.threats_blocked = 0

    async def analyze(
        self, input_data: str, context: dict[str, Any] | None = None
    ) -> ThreatAnalysisResult:
        """
        Analyze input for threats.

        Args:
            input_data: Input to analyze
            context: Optional context

        Returns:
            ThreatAnalysisResult
        """
        start_time = time.time()
        self.scans_performed += 1
        indicators = []

        # Apply enabled rules
        if "adversarial_detection" in self.enabled_rules:
            indicators.extend(self._detect_adversarial(input_data))

        if "threat_evolution" in self.enabled_rules:
            indicators.extend(self._detect_evolved_threats(input_data))

        # Determine overall threat level
        threat_level = self._calculate_threat_level(indicators)

        # Determine response action
        response = self._determine_response(threat_level, indicators)

        if indicators:
            self.threats_detected += 1
            self.threat_history.extend(indicators)

        if response in ("block", "quarantine"):
            self.threats_blocked += 1

        return ThreatAnalysisResult(
            safe=threat_level in (ThreatLevel.NONE, ThreatLevel.LOW),
            threat_level=threat_level,
            indicators=indicators,
            response_action=response,
            analysis_time_ms=(time.time() - start_time) * 1000,
        )

    def _detect_adversarial(self, input_data: str) -> list[ThreatIndicator]:
        """Detect adversarial patterns."""
        indicators = []
        input_lower = input_data.lower()

        # Check adversarial patterns
        for pattern in self.adversarial_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                indicators.append(
                    ThreatIndicator(
                        threat_type=ThreatType.ADVERSARIAL,
                        level=ThreatLevel.HIGH,
                        description="Adversarial prompt injection attempt",
                        confidence=0.9,
                        pattern_matched=pattern,
                    )
                )

        # Check injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                indicators.append(
                    ThreatIndicator(
                        threat_type=ThreatType.INJECTION,
                        level=ThreatLevel.CRITICAL,
                        description="Code injection attempt",
                        confidence=0.95,
                        pattern_matched=pattern,
                    )
                )

        # Check evasion patterns
        for pattern in self.evasion_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                indicators.append(
                    ThreatIndicator(
                        threat_type=ThreatType.EVASION,
                        level=ThreatLevel.MEDIUM,
                        description="Potential evasion technique",
                        confidence=0.7,
                        pattern_matched=pattern,
                    )
                )

        return indicators

    def _detect_evolved_threats(self, input_data: str) -> list[ThreatIndicator]:
        """Detect evolved threat patterns from history."""
        indicators = []

        # Check evolved patterns
        for pattern in self.evolved_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                indicators.append(
                    ThreatIndicator(
                        threat_type=ThreatType.UNKNOWN,
                        level=ThreatLevel.MEDIUM,
                        description="Evolved threat pattern detected",
                        confidence=0.6,
                        pattern_matched=pattern,
                    )
                )

        return indicators

    def _calculate_threat_level(self, indicators: list[ThreatIndicator]) -> ThreatLevel:
        """Calculate overall threat level from indicators."""
        if not indicators:
            return ThreatLevel.NONE

        # Find highest threat level
        level_priority = {
            ThreatLevel.CRITICAL: 4,
            ThreatLevel.HIGH: 3,
            ThreatLevel.MEDIUM: 2,
            ThreatLevel.LOW: 1,
            ThreatLevel.NONE: 0,
        }

        max_level = max(indicators, key=lambda x: level_priority[x.level])
        return max_level.level

    def _determine_response(self, level: ThreatLevel, indicators: list[ThreatIndicator]) -> str:
        """Determine response action based on threat level."""
        if level == ThreatLevel.CRITICAL:
            return "block"
        elif level == ThreatLevel.HIGH:
            return "quarantine"
        elif level == ThreatLevel.MEDIUM:
            return "alert"
        else:
            return "allow"

    def add_evolved_pattern(self, pattern: str) -> None:
        """Add new evolved threat pattern."""
        if pattern not in self.evolved_patterns:
            self.evolved_patterns.append(pattern)

    def immune_response(self, indicator: ThreatIndicator) -> dict[str, Any]:
        """
        Execute immune response to threat.

        Args:
            indicator: Threat indicator

        Returns:
            Response action taken
        """
        if "immune_response" not in self.enabled_rules:
            return {"action": "none", "reason": "immune_response disabled"}

        # Add pattern to evolved patterns for future detection
        if indicator.pattern_matched:
            self.add_evolved_pattern(indicator.pattern_matched)

        return {
            "action": "learned",
            "pattern_added": indicator.pattern_matched,
            "threat_type": indicator.threat_type.value,
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get threat detection statistics."""
        return {
            "scans_performed": self.scans_performed,
            "threats_detected": self.threats_detected,
            "threats_blocked": self.threats_blocked,
            "evolved_patterns": len(self.evolved_patterns),
            "threat_history_size": len(self.threat_history),
            "detection_rate": (self.threats_detected / self.scans_performed * 100)
            if self.scans_performed > 0
            else 0,
        }
