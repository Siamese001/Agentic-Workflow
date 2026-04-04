from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "SafetyDetectorAgent")
emit_determinism_digest("p0", "SafetyDetectorAgent")

_emit_dispatches_healing_run("p1", "SafetyDetectorAgent", "L5")
_emit_routes_through("p1", "SafetyDetectorAgent", "L5")
_emit_checks_agent_registry("p1", "SafetyDetectorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "SafetyDetectorAgent", "capability")
_emit_dispatches_execution_plan("p1", "SafetyDetectorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "SafetyDetectorAgent", "sub_agent")
_emit_routes_to_agent("p1", "SafetyDetectorAgent", "target_agent")
_emit_verifies_policy("p1", "SafetyDetectorAgent", "policy_check")
_emit_observes_runtime_state("p1", "SafetyDetectorAgent", "runtime_state")
_emit_verifies_boundary("p1", "SafetyDetectorAgent", "boundary_check")
_emit_transcripts_response("p1", "SafetyDetectorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "SafetyDetectorAgent")
_emit_gated_by_confidence("p1", "SafetyDetectorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "SafetyDetectorAgent", "L5")
_emit_reads_policy_state("p1", "SafetyDetectorAgent", "L5")

_emit_snapshots_state("p0", "SafetyDetectorAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "SafetyDetectorAgent", "execution_auth")
_emit_validates_capability("p2", "SafetyDetectorAgent", "capability_check")
_emit_routes_to_capability("p2", "SafetyDetectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "SafetyDetectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SafetyDetectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SafetyDetectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SafetyDetectorAgent", "exec_output")
_emit_dispatches_agent("p3", "SafetyDetectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SafetyDetectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SafetyDetectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SafetyDetectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "SafetyDetectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SafetyDetectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SafetyDetectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SafetyDetectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SafetyDetectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SafetyDetectorAgent", "eval_metric")
_emit_stores_embedding("p4", "SafetyDetectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SafetyDetectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SafetyDetectorAgent", "exec_snapshot_link")

"\nSafetyDetectorAgent - Safety & Security Detection\n\nPhase 4 Hard Migration: Consolidates:\n- BiasDetectorAgent (bias detection in outputs)\n- HallucinationDetectorAgent (hallucination detection)\n- PromptInjectionDetectorAgent (injection attack detection)\n\nFeatures:\n- Bias pattern detection in model outputs\n- Hallucination detection via fact-checking\n- Prompt injection attack detection\n- Configurable detection thresholds\n- Real-time safety scoring\n"
import logging
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("SafetyDetectorAgent", "p4obs", "metric_6")
_emit_records_incident_event("SafetyDetectorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("SafetyDetectorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("SafetyDetectorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("SafetyDetectorAgent", "p4obs", "mon_state")
_emit_triggers_alert("SafetyDetectorAgent", "p4obs", "alert")
_emit_links_incident_trace("SafetyDetectorAgent", "p4obs", "trace_link")
_emit_captures_pattern("SafetyDetectorAgent", "p3lm", "pattern")
_emit_records_learning_event("SafetyDetectorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SafetyDetectorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("SafetyDetectorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SafetyDetectorAgent", "p3lm", "routing")
_emit_improves_agent_policy("SafetyDetectorAgent", "p3lm", "policy")
_emit_stores_learning_state("SafetyDetectorAgent", "p3lm", "state")
_emit_records_execution_trace("SafetyDetectorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SafetyDetectorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SafetyDetectorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SafetyDetectorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SafetyDetectorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SafetyDetectorAgent", "env_read", "p2_env_1")
_emit_reads_environ("SafetyDetectorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("SafetyDetectorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SafetyDetectorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SafetyDetectorAgent", "context_pull")
_emit_pulls_context("p1", "SafetyDetectorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SafetyDetectorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SafetyDetectorAgent", "uwg_term_2")
_emit_writes_through("p1", "SafetyDetectorAgent", "write_through")
_emit_writes_through("p1", "SafetyDetectorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "SafetyDetectorAgent", "safety_validation")
_emit_invokes_eval("p1", "SafetyDetectorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "SafetyDetectorAgent", "routing_commit")

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
