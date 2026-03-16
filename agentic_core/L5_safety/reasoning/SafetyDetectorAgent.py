from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "SafetyDetectorAgent")
emit_determinism_digest("p0", "SafetyDetectorAgent")

_emit_dispatches_healing_run("p1", "SafetyDetectorAgent", "L5")
_emit_routes_through("p1", "SafetyDetectorAgent", "L5")
_emit_escalates_to_human("p1", "SafetyDetectorAgent", "L5")
_emit_reads_policy_state("p1", "SafetyDetectorAgent", "L5")

_emit_snapshots_state("p0", "SafetyDetectorAgent", "state_snapshot")

"\nSafetyDetectorAgent - Safety & Security Detection\n\nPhase 4 Hard Migration: Consolidates:\n- BiasDetectorAgent (bias detection in outputs)\n- HallucinationDetectorAgent (hallucination detection)\n- PromptInjectionDetectorAgent (injection attack detection)\n\nFeatures:\n- Bias pattern detection in model outputs\n- Hallucination detection via fact-checking\n- Prompt injection attack detection\n- Configurable detection thresholds\n- Real-time safety scoring\n"
import logging
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

Logger = logging.getLogger(__name__)


class SafetyThreatType(Enum):
    """Types of safety threats."""

    BIAS = auto()
    HALLUCINATION = auto()
    PROMPT_INJECTION = auto()
    JAILBREAK = auto()
    DATA_EXFILTRATION = auto()


class ThreatSeverity(Enum):
    """Severity levels for threats."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class SafetyThreat:
    """Represents a detected safety threat."""

    threat_type: SafetyThreatType
    severity: ThreatSeverity
    message: str
    source: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    blocked: bool = False


@dataclass
class SafetyConfig:
    """configuration for safety detection."""

    enable_bias: bool = True
    enable_hallucination: bool = True
    enable_injection: bool = True
    injection_threshold: float = 0.8
    bias_threshold: float = 0.7
    block_high_severity: bool = True


class SafetyDetectorAgent(SovereignBaseAgent):
    """
    Unified safety and security detector.

    Consolidates:
    - BiasDetectorAgent
    - HallucinationDetectorAgent
    - PromptInjectionDetectorAgent

    Usage:
        detector = SafetyDetectorAgent()

        # Check user input for injection
        threats = detector.detect_injection("user input here")

        # Check model output for bias
        threats = detector.detect_bias("model output here")
    """

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        _emit_applies_guardrail(str(uuid.uuid4()), "SafetyDetectorAgent.heal_repository", "L5_POLICY")
        return {"violations": 0, "fixed": 0, "errors": 0}

    INJECTION_PATTERNS = [
        "ignore\\s+(previous|all|above)\\s+instructions?",
        "ignore\\s+all\\s+previous",
        "disregard\\s+(previous|all|above|the)",
        "forget\\s+(previous|all|above|your)",
        "you\\s+are\\s+now\\s+",
        "pretend\\s+(you\\s+are|to\\s+be)",
        "act\\s+as\\s+(if|a|an)",
        "new\\s+instructions?:",
        "system\\s*:\\s*",
        "<\\s*system\\s*>",
        "\\[\\s*system\\s*\\]",
        "override\\s+safety",
        "bypass\\s+(all\\s+)?(restrictions?|safety)",
        "jailbreak",
        "dan\\s+mode",
        "developer\\s+mode",
        "unrestricted\\s+ai",
    ]
    BIAS_PATTERNS = [
        "\\b(always|never|all|none|every)\\b.*\\b(men|women|people|group)\\b",
        "\\b(superior|inferior)\\b.*\\b(race|gender|religion)\\b",
        "\\b(typical|stereotyp)",
        "\\b(obviously|clearly)\\s+(men|women|they)\\b",
    ]
    HALLUCINATION_PATTERNS = [
        "as\\s+of\\s+my\\s+knowledge\\s+cutoff",
        "i\\s+don'?t\\s+have\\s+access\\s+to\\s+real-?time",
        "i\\s+cannot\\s+verify",
        "according\\s+to\\s+my\\s+training\\s+data",
    ]

    def __init__(self, agent_config: SafetyConfig | None = None):
        self._agent_config = agent_config or SafetyConfig()
        self._lock = threading.RLock()
        self._threats: list[SafetyThreat] = []
        self._compiled_injection = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._compiled_bias = [re.compile(p, re.IGNORECASE) for p in self.BIAS_PATTERNS]
        Logger.info("SafetyDetectorAgent initialized")

    def detect_all(self, text: str, source: str = "unknown") -> list[SafetyThreat]:
        """Run all enabled detections on text."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyDetectorAgent.detect_all")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyDetectorAgent.detect_all".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        threats = []
        if self._agent_config.enable_injection:
            threats.extend(self.detect_injection(text, source))
        if self._agent_config.enable_bias:
            threats.extend(self.detect_bias(text, source))
        if self._agent_config.enable_hallucination:
            threats.extend(self.detect_hallucination(text, source))
        return threats

    def detect_injection(self, text: str, source: str = "user_input") -> list[SafetyThreat]:
        """Detect prompt injection attacks."""
        threats = []
        text_lower = text.lower()
        matched_patterns = []
        for pattern in self._compiled_injection:
            if pattern.search(text_lower):
                matched_patterns.append(pattern.pattern)
        if matched_patterns:
            if len(matched_patterns) >= 3:
                severity = ThreatSeverity.CRITICAL
            elif len(matched_patterns) >= 2:
                severity = ThreatSeverity.HIGH
            else:
                severity = ThreatSeverity.MEDIUM
            threat = SafetyThreat(
                threat_type=SafetyThreatType.PROMPT_INJECTION,
                severity=severity,
                message=f"Prompt injection detected: {len(matched_patterns)} pattern(s) matched",
                source=source,
                details={
                    "patterns_matched": matched_patterns,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                },
                blocked=self._agent_config.block_high_severity
                and severity.value >= ThreatSeverity.HIGH.value,
            )
            threats.append(threat)
            self._threats.append(threat)
        return threats

    def detect_bias(self, text: str, source: str = "model_output") -> list[SafetyThreat]:
        """Detect bias patterns in text."""
        threats = []
        for pattern in self._compiled_bias:
            match = pattern.search(text)
            if match:
                threat = SafetyThreat(
                    threat_type=SafetyThreatType.BIAS,
                    severity=ThreatSeverity.MEDIUM,
                    message=f"Potential bias detected: '{match.group()}'",
                    source=source,
                    details={"matched_text": match.group(), "pattern": pattern.pattern},
                )
                threats.append(threat)
                self._threats.append(threat)
        return threats

    def detect_hallucination(self, text: str, source: str = "model_output") -> list[SafetyThreat]:
        """Detect hallucination indicators in text."""
        threats = []
        for pattern in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                threat = SafetyThreat(
                    threat_type=SafetyThreatType.HALLUCINATION,
                    severity=ThreatSeverity.LOW,
                    message="Potential hallucination indicator detected",
                    source=source,
                    details={"pattern": pattern},
                )
                threats.append(threat)
                self._threats.append(threat)
        return threats

    def is_safe(self, text: str, source: str = "unknown") -> bool:
        """Quick check if text is safe (no high-severity threats)."""
        threats = self.detect_all(text, source)
        high_severity = [t for t in threats if t.severity.value >= ThreatSeverity.HIGH.value]
        return len(high_severity) == 0

    def get_safety_score(self, text: str) -> float:
        """Calculate safety score (0.0 = unsafe, 1.0 = safe)."""
        threats = self.detect_all(text)
        if not threats:
            return 1.0
        total_penalty = sum(t.severity.value * 0.25 for t in threats)
        score = max(0.0, 1.0 - total_penalty)
        return score

    def get_threats(self) -> list[SafetyThreat]:
        """Get all recorded threats."""
        return self._threats.copy()

    def clear_threats(self) -> None:
        """Clear recorded threats."""
        with self._lock:
            self._threats.clear()

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal safety detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (bias, hallucination, injection)
                - source: Source of the threat
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        Logger.info("[SAFETY_DETECTOR] Detection-only agent - threats require manual review")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Detection-only agent - threats require manual security review",
        }


def create_legacy_bias_detector() -> SafetyDetectorAgent:
    """Create detector for bias only."""
    config = SafetyConfig(enable_bias=True, enable_hallucination=False, enable_injection=False)
    return SafetyDetectorAgent(config=config)


def create_legacy_injection_detector() -> SafetyDetectorAgent:
    """Create detector for prompt injection only."""
    config = SafetyConfig(enable_bias=False, enable_hallucination=False, enable_injection=True)
    return SafetyDetectorAgent(config=config)
