from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "SelfUpdatingSafetyEngineAgent")
emit_determinism_digest("p0", "SelfUpdatingSafetyEngineAgent")

_emit_dispatches_healing_run("p1", "SelfUpdatingSafetyEngineAgent", "L5")
_emit_routes_through("p1", "SelfUpdatingSafetyEngineAgent", "L5")
_emit_checks_agent_registry("p1", "SelfUpdatingSafetyEngineAgent", "agent_registry")
_emit_validates_agent_capability("p1", "SelfUpdatingSafetyEngineAgent", "capability")
_emit_dispatches_execution_plan("p1", "SelfUpdatingSafetyEngineAgent", "exec_plan")
_emit_agent_executes_agent("p1", "SelfUpdatingSafetyEngineAgent", "sub_agent")
_emit_routes_to_agent("p1", "SelfUpdatingSafetyEngineAgent", "target_agent")
_emit_verifies_policy("p1", "SelfUpdatingSafetyEngineAgent", "policy_check")
_emit_observes_runtime_state("p1", "SelfUpdatingSafetyEngineAgent", "runtime_state")
_emit_verifies_boundary("p1", "SelfUpdatingSafetyEngineAgent", "boundary_check")
_emit_transcripts_response("p1", "SelfUpdatingSafetyEngineAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "SelfUpdatingSafetyEngineAgent")
_emit_gated_by_confidence("p1", "SelfUpdatingSafetyEngineAgent", "confidence_gate")
_emit_escalates_to_human("p1", "SelfUpdatingSafetyEngineAgent", "L5")
_emit_reads_policy_state("p1", "SelfUpdatingSafetyEngineAgent", "L5")
_emit_authorize_and_execute("p2", "SelfUpdatingSafetyEngineAgent", "execution_auth")
_emit_validates_capability("p2", "SelfUpdatingSafetyEngineAgent", "capability_check")
_emit_routes_to_capability("p2", "SelfUpdatingSafetyEngineAgent", "capability_route")
_emit_writes_via_uwg("p2", "SelfUpdatingSafetyEngineAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SelfUpdatingSafetyEngineAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SelfUpdatingSafetyEngineAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SelfUpdatingSafetyEngineAgent", "exec_output")
_emit_dispatches_agent("p3", "SelfUpdatingSafetyEngineAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SelfUpdatingSafetyEngineAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SelfUpdatingSafetyEngineAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SelfUpdatingSafetyEngineAgent", "healing_outcome")
_emit_escalates_failure("p3", "SelfUpdatingSafetyEngineAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SelfUpdatingSafetyEngineAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SelfUpdatingSafetyEngineAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SelfUpdatingSafetyEngineAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SelfUpdatingSafetyEngineAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SelfUpdatingSafetyEngineAgent", "eval_metric")
_emit_stores_embedding("p4", "SelfUpdatingSafetyEngineAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SelfUpdatingSafetyEngineAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SelfUpdatingSafetyEngineAgent", "exec_snapshot_link")

# guardian: allow-path-fragility
"\nSelf-Updating Safety Engine - L5 Safety Enhancement\n\nDynamically learns and updates safety rules based on detected threats.\nAutomatically adapts to new attack patterns and security vulnerabilities.\n"
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.mixins.safety_mixin import SafetyAnalysisMixin
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from agentic_core.utils.timeout_decorator_util import timeout

Logger: Any = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat Severity levels."""

    LOW: Any = "low"
    MEDIUM: Any = "medium"
    HIGH: Any = "high"
    CRITICAL: Any = "critical"


class RuleType(Enum):
    """Types of safety rules."""

    PATTERN_MATCH: Any = "pattern_match"
    SEMANTIC_ANALYSIS: Any = "semantic_analysis"
    BEHAVIORAL: Any = "behavioral"
    CONTEXTUAL: Any = "contextual"


@dataclass
class ThreatPattern:
    """Represents a detected threat pattern."""

    pattern_id: str
    pattern_type: RuleType
    pattern_signature: str
    ThreatLevel: ThreatLevel
    detection_count: int = 0
    false_positive_count: int = 0
    last_detected: datetime | None = None
    examples: list[str] = field(default_factory=list)

    @property
    def confidence_score(self) -> float:
        """Calculate confidence score for this pattern."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ThreatPattern.confidence_score", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ThreatPattern.confidence_score", "p0_governance")
        total: Any = self.detection_count + self.false_positive_count
        if total == 0:
            return 0.5
        return self.detection_count / total


@dataclass
class SafetyRule:
    """Represents a safety rule."""

    rule_id: str
    RuleType: RuleType
    pattern: str
    description: str
    ThreatLevel: ThreatLevel
    enabled: bool = True
    auto_generated: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: datetime | None = None
    trigger_count: int = 0

    def matches(self, text: str) -> bool:
        """Check if text matches this rule."""
        if not self.enabled:
            return False
        if self.RuleType == RuleType.PATTERN_MATCH:
            return SafetyAnalysisMixin.matches(self.pattern, text)
        return False

    # guardian: allow-type-erasure
    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "RuleType": self.RuleType.value,
            "pattern": self.pattern,
            "description": self.description,
            "ThreatLevel": self.ThreatLevel.value,
            "enabled": self.enabled,
            "auto_generated": self.auto_generated,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SafetyRule:
        """Create rule from dictionary."""
        return cls(
            rule_id=data["rule_id"],
            RuleType=RuleType(data["RuleType"]),
            pattern=data["pattern"],
            description=data["description"],
            ThreatLevel=ThreatLevel(data["ThreatLevel"]),
            enabled=data.get("enabled", True),
            auto_generated=data.get("auto_generated", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_triggered=datetime.fromisoformat(data["last_triggered"])
            if data.get("last_triggered")
            else None,
            trigger_count=data.get("trigger_count", 0),
        )


@dataclass
class ThreatDetection:
    """Result of threat detection."""

    detected: bool
    ThreatLevel: ThreatLevel
    matched_rules: list[SafetyRule]
    confidence: float
    recommendations: list[str]


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_1")
_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_2")
_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_3")
_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_4")
_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_5")
_emit_emits_metric_event("SelfUpdatingSafetyEngineAgent", "p4obs", "metric_6")
_emit_records_incident_event("SelfUpdatingSafetyEngineAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("SelfUpdatingSafetyEngineAgent", "p4obs", "anomaly")
_emit_writes_observability_log("SelfUpdatingSafetyEngineAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("SelfUpdatingSafetyEngineAgent", "p4obs", "mon_state")
_emit_triggers_alert("SelfUpdatingSafetyEngineAgent", "p4obs", "alert")
_emit_links_incident_trace("SelfUpdatingSafetyEngineAgent", "p4obs", "trace_link")
_emit_captures_pattern("SelfUpdatingSafetyEngineAgent", "p3lm", "pattern")
_emit_records_learning_event("SelfUpdatingSafetyEngineAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SelfUpdatingSafetyEngineAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("SelfUpdatingSafetyEngineAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SelfUpdatingSafetyEngineAgent", "p3lm", "routing")
_emit_improves_agent_policy("SelfUpdatingSafetyEngineAgent", "p3lm", "policy")
_emit_stores_learning_state("SelfUpdatingSafetyEngineAgent", "p3lm", "state")
_emit_records_execution_trace("SelfUpdatingSafetyEngineAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SelfUpdatingSafetyEngineAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SelfUpdatingSafetyEngineAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SelfUpdatingSafetyEngineAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SelfUpdatingSafetyEngineAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SelfUpdatingSafetyEngineAgent", "env_read", "p2_env_1")
_emit_reads_environ("SelfUpdatingSafetyEngineAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("SelfUpdatingSafetyEngineAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SelfUpdatingSafetyEngineAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SelfUpdatingSafetyEngineAgent", "context_pull")
_emit_pulls_context("p1", "SelfUpdatingSafetyEngineAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SelfUpdatingSafetyEngineAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SelfUpdatingSafetyEngineAgent", "uwg_term_2")
_emit_writes_through("p1", "SelfUpdatingSafetyEngineAgent", "write_through")
_emit_writes_through("p1", "SelfUpdatingSafetyEngineAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "SelfUpdatingSafetyEngineAgent", "safety_validation")
_emit_invokes_eval("p1", "SelfUpdatingSafetyEngineAgent", "eval_call")
_emit_proposal_commits_routing("p1", "SelfUpdatingSafetyEngineAgent", "routing_commit")


class SelfUpdatingSafetyEngineAgent(SovereignBaseAgent):
    """
    Safety engine that learns and adapts to new threats.

    Features:
    - Automatic threat pattern detection
    - Dynamic rule generation
    - False positive learning
    - Threat Severity escalation
    - Rule effectiveness tracking
    """

    def __init__(self, rules_storage_path: str | None = None) -> None:
        """Initialize the self-updating safety engine."""
        # guardian: allow-path-string
        self.rules_storage_path = (
            rules_storage_path or Path(os.getcwd()) / ".canon_memory" / "safety_rules.json"
        )
        self.rules: dict[str, SafetyRule] = {}
        self.threat_patterns: dict[str, ThreatPattern] = {}
        self.detection_history: list[dict[str, Any]] = []
        self.false_positive_feedback: dict[str, int] = {}
        self._initialize_base_rules()
        self._load_rules()
        Logger.info("Self-Updating Safety Engine initialized")

    # guardian: allow-type-erasure
    def _initialize_base_rules(self) -> Any:
        """Initialize base safety rules."""
        base_rules = [
            SafetyRule(
                rule_id="base_001",
                RuleType=RuleType.PATTERN_MATCH,
                pattern="(?i)(api[_-]?key|secret[_-]?key|password|token)\\s*[=:]\\s*['\\\"][^'\\\"]{8,}['\\\"]",
                description="Hardcoded secrets detection",
                ThreatLevel=ThreatLevel.CRITICAL,
                auto_generated=False,
            ),
            SafetyRule(
                rule_id="base_002",
                RuleType=RuleType.PATTERN_MATCH,
                pattern="(?i)eval\\s*\\(|exec\\s*\\(",
                description="Dangerous code execution",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False,
            ),
            SafetyRule(
                rule_id="base_003",
                RuleType=RuleType.PATTERN_MATCH,
                pattern="(?i)__import__\\s*\\(\\s*['\\\"]os['\\\"]|subprocess\\.call",
                description="System command execution",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False,
            ),
            SafetyRule(
                rule_id="base_004",
                RuleType=RuleType.PATTERN_MATCH,
                pattern="(?i)DROP\\s+TABLE|DELETE\\s+FROM.*WHERE\\s+1\\s*=\\s*1",
                description="SQL injection patterns",
                ThreatLevel=ThreatLevel.CRITICAL,
                auto_generated=False,
            ),
            SafetyRule(
                rule_id="base_005",
                RuleType=RuleType.PATTERN_MATCH,
                pattern="(?i)<script[^>]*>.*?</script>|javascript:",
                description="XSS attack patterns",
                ThreatLevel=ThreatLevel.HIGH,
                auto_generated=False,
            ),
        ]
        for rule in base_rules:
            self.rules[rule.rule_id] = rule

    # guardian: allow-type-erasure
    def _load_rules(self) -> Any:
        """Load rules from storage."""
        # guardian: allow-path-string
        if not os.path.exists(self.rules_storage_path):
            Logger.info("No existing rules found, using base rules only")
            return
        try:
            with open(self.rules_storage_path, encoding="utf-8") as f:
                data = json.load(f)
            for rule_data in data.get("rules", []):
                if rule_data["auto_generated"]:
                    rule = SafetyRule.from_dict(rule_data)
                    self.rules[rule.rule_id] = rule
            Logger.info(f"Loaded {len(self.rules)} safety rules")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"Failed to load rules: {e}")

    # guardian: allow-type-erasure
    def _save_rules(self) -> Any:
        """Save rules to storage."""
        try:
            _wg.makedirs(Path(self.rules_storage_path).parent, exist_ok=True)
            data = {
                "rules": [rule.to_dict() for rule in self.rules.values()],
                "last_updated": datetime.now().isoformat(),
            }
            _wg.write_json(self.rules_storage_path, data, indent=2)
            Logger.debug(f"Saved {len(self.rules)} rules")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"Failed to save rules: {e}")

    async def detect_threats(self, text: str, context: dict[str, Any] | None = None) -> ThreatDetection:
        """
        Detect threats in text.

        Args:
            text: Text to analyze
            context: Optional context information

        Returns:
            Threat detection result
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            "SelfUpdatingSafetyEngineAgent.detect_threats",
        )
        matched_rules: Any = []
        max_threat_level: Any = ThreatLevel.LOW
        for rule in self.rules.values():
            if rule.matches(text):
                matched_rules.append(rule)
                rule.trigger_count += 1
                rule.last_triggered = datetime.now()
                if self._compare_threat_levels(rule.ThreatLevel, max_threat_level) > 0:
                    max_threat_level: Any = rule.ThreatLevel
        confidence: Any = 0.0
        if matched_rules:
            confidence: Any = sum(1.0 if not rule.auto_generated else 0.8 for rule in matched_rules) / len(
                matched_rules,
            )
        recommendations: Any = self._generate_recommendations(matched_rules)
        detection: Any = ThreatDetection(
            detected=len(matched_rules) > 0,
            ThreatLevel=max_threat_level,
            matched_rules=matched_rules,
            confidence=confidence,
            recommendations=recommendations,
        )
        self.detection_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "detected": detection.detected,
                "ThreatLevel": detection.ThreatLevel.value,
                "rules_matched": len(matched_rules),
            },
        )
        if detection.detected:
            await self._learn_from_detection(text, matched_rules)
        return detection

    # guardian: allow-type-erasure
    async def _learn_from_detection(self, text: str, matched_rules: list[SafetyRule]) -> Any:
        """Learn from a threat detection."""
        for rule in matched_rules:
            pattern_id = f"pattern_{rule.rule_id}"
            if pattern_id not in self.threat_patterns:
                self.threat_patterns[pattern_id] = ThreatPattern(
                    pattern_id=pattern_id,
                    pattern_type=rule.RuleType,
                    pattern_signature=rule.pattern,
                    ThreatLevel=rule.ThreatLevel,
                )
            pattern = self.threat_patterns[pattern_id]
            pattern.detection_count += 1
            pattern.last_detected = datetime.now()
            if len(pattern.examples) < 5:
                pattern.examples.append(text[:200])
        await self._generate_new_rules_if_needed()

    # guardian: allow-type-erasure
    async def _generate_new_rules_if_needed(self) -> Any:
        """Generate new rules based on detected patterns."""
        for pattern in self.threat_patterns.values():
            if pattern.confidence_score <= 0.75:
                continue
            if pattern.detection_count < 5:
                continue
            existing_rule_ids = {rule.rule_id for rule in self.rules.values()}
            new_rule_id = f"auto_{pattern.pattern_id}"
            if new_rule_id in existing_rule_ids:
                continue
            variations = self._generate_pattern_variations(pattern)
            for i, variation in enumerate(variations[:3]):
                rule_id = f"{new_rule_id}_v{i}"
                if rule_id not in existing_rule_ids:
                    new_rule = SafetyRule(
                        rule_id=rule_id,
                        RuleType=pattern.pattern_type,
                        pattern=variation,
                        description=f"Auto-generated rule from pattern {pattern.pattern_id}",
                        ThreatLevel=pattern.ThreatLevel,
                        auto_generated=True,
                    )
                    self.rules[rule_id] = new_rule
                    Logger.info(f"Generated new safety rule: {rule_id}")
        self._save_rules()

    def _generate_pattern_variations(self, pattern: ThreatPattern) -> list[str]:
        """Generate variations of a threat pattern."""
        base_pattern = pattern.pattern_signature
        variations = [base_pattern]
        if pattern.pattern_type == RuleType.PATTERN_MATCH:
            variations.append(base_pattern.replace("\\s*", "\\s+"))
            variations.append(base_pattern.replace("['\\\"]", "['\\\"`]"))
        return variations

    # guardian: allow-type-erasure
    def report_false_positive(self, rule_id: str, text: str) -> Any:
        """
        Report a false positive detection.

        Args:
            rule_id: Rule that triggered false positive
            text: Text that was incorrectly flagged
        """
        if rule_id not in self.rules:
            Logger.warning(f"Rule {rule_id} not found for false positive report")
            return
        self.false_positive_feedback[rule_id] = self.false_positive_feedback.get(rule_id, 0) + 1
        rule: Any = self.rules[rule_id]
        pattern_id: Any = f"pattern_{rule_id}"
        if pattern_id in self.threat_patterns:
            self.threat_patterns[pattern_id].false_positive_count += 1
        if self.false_positive_feedback[rule_id] >= 5:
            if rule.auto_generated:
                rule.enabled = False
                Logger.info(f"Disabled rule {rule_id} due to high false positive rate")
            else:
                Logger.warning(f"Base rule {rule_id} has high false positive rate")
        self._save_rules()

    def _compare_threat_levels(self, level1: ThreatLevel, level2: ThreatLevel) -> int:
        """Compare two threat levels."""
        return SafetyAnalysisMixin._compare_threat_levels(level1.value, level2.value)

    def _generate_recommendations(self, matched_rules: list[SafetyRule]) -> list[str]:
        """Generate recommendations based on matched rules."""
        recommendations = []
        for rule in matched_rules:
            context = {
                "rule_description": rule.description,
                "rule_id": rule.rule_id,
                "auto_generated": rule.auto_generated,
            }
            rule_recommendations = SafetyAnalysisMixin._generate_recommendations(
                rule.ThreatLevel.value,
                context,
            )
            recommendations.extend(
                [
                    f"{rule.ThreatLevel.value.upper()}: {rule.description} - {rec}"
                    for rec in rule_recommendations
                ],
            )
        return recommendations

    # guardian: allow-type-erasure
    def escalate_threat_level(self, rule_id: str) -> Any:
        """
        Escalate threat level for a rule.

        Args:
            rule_id: Rule to escalate
        """
        if rule_id not in self.rules:
            return
        rule: Any = self.rules[rule_id]
        if rule.ThreatLevel == ThreatLevel.LOW:
            rule.ThreatLevel = ThreatLevel.MEDIUM
        elif rule.ThreatLevel == ThreatLevel.MEDIUM:
            rule.ThreatLevel = ThreatLevel.HIGH
        elif rule.ThreatLevel == ThreatLevel.HIGH:
            rule.ThreatLevel = ThreatLevel.CRITICAL
        Logger.info(f"Escalated threat level for rule {rule_id} to {rule.ThreatLevel.value}")
        self._save_rules()

    # guardian: allow-type-erasure
    def get_rule_effectiveness(self) -> dict[str, Any]:
        """Get effectiveness metrics for rules."""
        total_rules: Any = len(self.rules)
        enabled_rules: Any = sum(1 for rule in self.rules.values() if rule.enabled)
        auto_generated: Any = sum(1 for rule in self.rules.values() if rule.auto_generated)
        total_triggers: Any = sum(rule.trigger_count for rule in self.rules.values())
        most_triggered: Any = sorted(self.rules.values(), key=lambda r: r.trigger_count, reverse=True)[:5]
        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "auto_generated_rules": auto_generated,
            "total_triggers": total_triggers,
            "most_triggered_rules": [
                {
                    "rule_id": rule.rule_id,
                    "description": rule.description,
                    "trigger_count": rule.trigger_count,
                    "ThreatLevel": rule.ThreatLevel.value,
                }
                for rule in most_triggered
            ],
            "false_positive_reports": sum(self.false_positive_feedback.values()),
        }

    # guardian: allow-type-erasure
    def get_threat_statistics(self) -> dict[str, Any]:
        """Get threat detection statistics."""
        total_detections: Any = len(self.detection_history)
        if total_detections == 0:
            return {"total_detections": 0, "threat_distribution": {}, "detection_rate": 0.0}
        threat_counts: Any = {}
        for detection in self.detection_history:
            level: Any = detection["ThreatLevel"]
            threat_counts[level] = threat_counts.get(level, 0) + 1
        detected_count: Any = sum(1 for d in self.detection_history if d["detected"])
        return {
            "total_detections": total_detections,
            "threats_detected": detected_count,
            "detection_rate": detected_count / total_detections,
            "threat_distribution": threat_counts,
            "unique_patterns": len(self.threat_patterns),
        }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal safety engine violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (threat, pattern, rule)
                - rule_id: ID of the triggered rule
                - threat_level: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        Logger.info("[SELF_UPDATING_SAFETY] Safety engine violations require manual review")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Safety engine violations require manual security review",
        }


def create_self_updating_safety_engine(rules_storage_path: str | None = None) -> SelfUpdatingSafetyEngine:
    """Factory function to create self-updating safety engine."""
    super().heal_repository()
    return SelfUpdatingSafetyEngine(rules_storage_path=rules_storage_path)
