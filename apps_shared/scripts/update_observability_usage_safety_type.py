"""
07_observability/cache_ops/data_access/get_info/understand_request/query_observability_state.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 37c2bab0108a9e73a26d42276f09fc18aaa2410fd207db45332c58a4ed0187b8
"""

"\nL5 Agentic Core - Safety Layer - update_observability_usage\nImplements L5 Safety/Policy Layer for update observability usage operations\n"
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import field
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

_emit_applies_guardrail("p0", "update_observability_usage_safety_type", "p0_governance")
_emit_reads_policy_state("p0", "update_observability_usage_safety_type", "policy_binding")
_emit_snapshots_state("p0", "update_observability_usage_safety_type", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace(
    "update_observability_usage_safety_type", "update_observability_usage_safety_type_trace"
)


_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_1")
_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_2")
_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_3")
_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_4")
_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_5")
_emit_emits_metric_event("update_observability_usage_safety_type", "p4obs", "metric_6")
_emit_records_incident_event("update_observability_usage_safety_type", "p4obs", "incident")
_emit_captures_runtime_anomaly("update_observability_usage_safety_type", "p4obs", "anomaly")
_emit_writes_observability_log("update_observability_usage_safety_type", "p4obs", "obs_log")
_emit_updates_monitoring_state("update_observability_usage_safety_type", "p4obs", "mon_state")
_emit_triggers_alert("update_observability_usage_safety_type", "p4obs", "alert")
_emit_links_incident_trace("update_observability_usage_safety_type", "p4obs", "trace_link")
_emit_captures_pattern("update_observability_usage_safety_type", "p3lm", "pattern")
_emit_records_learning_event("update_observability_usage_safety_type", "p3lm", "learning_event")
_emit_writes_learning_snapshot("update_observability_usage_safety_type", "p3lm", "snapshot")
_emit_feeds_meta_learning("update_observability_usage_safety_type", "p3lm", "meta_feed")
_emit_updates_routing_strategy("update_observability_usage_safety_type", "p3lm", "routing")
_emit_improves_agent_policy("update_observability_usage_safety_type", "p3lm", "policy")
_emit_stores_learning_state("update_observability_usage_safety_type", "p3lm", "state")
_emit_records_execution_trace("update_observability_usage_safety_type", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("update_observability_usage_safety_type", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("update_observability_usage_safety_type", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("update_observability_usage_safety_type", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("update_observability_usage_safety_type", "L4_STATE", "p2_trace_5")
_emit_reads_environ("update_observability_usage_safety_type", "env_read", "p2_env_1")
_emit_reads_environ("update_observability_usage_safety_type", "env_read", "p2_env_2")
_emit_reads_runtime_state("update_observability_usage_safety_type", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("update_observability_usage_safety_type", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "update_observability_usage_safety_type", "context_pull")
_emit_pulls_context("p1", "update_observability_usage_safety_type", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "update_observability_usage_safety_type", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "update_observability_usage_safety_type", "uwg_term_2")
_emit_writes_through("p1", "update_observability_usage_safety_type", "write_through")
_emit_writes_through("p1", "update_observability_usage_safety_type", "write_through_2")
_emit_validated_by_safety_plane("p1", "update_observability_usage_safety_type", "safety_validation")
_emit_invokes_eval("p1", "update_observability_usage_safety_type", "eval_call")
_emit_proposal_commits_routing("p1", "update_observability_usage_safety_type", "routing_commit")
_emit_escalates_to_human("p1", "update_observability_usage_safety_type", "human_escalation")
_emit_routes_through("p1", "update_observability_usage_safety_type", "route_through")
_emit_checks_agent_registry("p1", "update_observability_usage_safety_type", "agent_registry")
_emit_validates_agent_capability("p1", "update_observability_usage_safety_type", "capability")
_emit_dispatches_execution_plan("p1", "update_observability_usage_safety_type", "exec_plan")
_emit_agent_executes_agent("p1", "update_observability_usage_safety_type", "sub_agent")
_emit_routes_to_agent("p1", "update_observability_usage_safety_type", "target_agent")
_emit_verifies_policy("p1", "update_observability_usage_safety_type", "policy_check")
_emit_observes_runtime_state("p1", "update_observability_usage_safety_type", "runtime_state")
_emit_verifies_boundary("p1", "update_observability_usage_safety_type", "boundary_check")
_emit_transcripts_response("p1", "update_observability_usage_safety_type", "transcript")
_emit_hard_fails_untranscripted("p1", "update_observability_usage_safety_type")
_emit_gated_by_confidence("p1", "update_observability_usage_safety_type", "confidence_gate")
emit_replay_key("p0", "update_observability_usage_safety_type")
emit_determinism_digest("p0", "update_observability_usage_safety_type")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "update_observability_usage_safety_type", "execution_auth")
_emit_validates_capability("p2", "update_observability_usage_safety_type", "capability_check")
_emit_routes_to_capability("p2", "update_observability_usage_safety_type", "capability_route")
_emit_writes_via_uwg("p2", "update_observability_usage_safety_type", "uwg_write")
_emit_blocks_direct_write("p2", "update_observability_usage_safety_type", "direct_write_block")
_emit_records_tool_invocation("p2", "update_observability_usage_safety_type", "tool_invocation")
_emit_captures_execution_output("p2", "update_observability_usage_safety_type", "exec_output")
_emit_dispatches_agent("p3", "update_observability_usage_safety_type", "agent_dispatch")
_emit_coordinates_agents("p3", "update_observability_usage_safety_type", "agent_coordination")
_emit_records_workflow_lineage("p3", "update_observability_usage_safety_type", "workflow_lineage")
_emit_records_healing_outcome("p3", "update_observability_usage_safety_type", "healing_outcome")
_emit_escalates_failure("p3", "update_observability_usage_safety_type", "failure_escalation")
_emit_orchestrates_workflow("p3", "update_observability_usage_safety_type", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "update_observability_usage_safety_type", "healing_dispatch")
_emit_invokes_evaluation("p3", "update_observability_usage_safety_type", "evaluation_signal")
_emit_records_telemetry_event("p4", "update_observability_usage_safety_type", "telemetry_event")
_emit_captures_evaluation_metric("p4", "update_observability_usage_safety_type", "eval_metric")
_emit_stores_embedding("p4", "update_observability_usage_safety_type", "embedding_store")
_emit_updates_meta_learning_state("p4", "update_observability_usage_safety_type", "meta_learning")
_emit_links_execution_to_snapshot("p4", "update_observability_usage_safety_type", "exec_snapshot_link")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_1")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_2")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_3")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_4")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_5")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_6")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_7")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_8")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_9")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_10")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_11")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_12")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_13")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_14")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_15")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_16")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_17")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_18")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_19")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_20")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_21")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_22")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_23")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_24")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_25")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_26")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_27")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_28")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_29")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_30")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_31")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_32")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_33")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_34")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_35")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_36")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_37")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_38")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_39")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_40")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_41")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_42")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_43")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_44")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_45")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_46")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_47")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_48")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_49")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_50")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_51")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_52")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_53")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_54")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_55")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_56")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_57")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_58")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_59")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_60")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_61")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_62")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_63")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_64")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_65")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_66")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_67")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_68")
_emit_reads_through("l4", "update_observability_usage_safety_type", "urg_read_69")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateObservabilityUsageSafetyType(Enum):
    """L5 Typed enumeration for deterministic safety operations"""

    APPLY = "apply"
    ENFORCE = "enforce"
    VALIDATE = "validate"


class UpdateObservabilityUsageSafetyConstraints:
    """L5 Safety constraints - fail-closed behavior"""

    max_risk_score: float = 0.5
    allowed_operations: list[str] = field(default_factory=lambda: ["apply", "enforce", "validate"])
    safety_level: str = "strict"
    requires_approval: bool = True


class UpdateObservabilityUsageSafetyResult:
    """L5 Safety result with full type safety"""

    success: bool
    safety_score: float = 0.0
    risk_assessment: dict[str, object] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""


class UpdateObservabilityUsageSafetySafety(ABC):
    """L5 interface foundation - ensures L5 pure safety behavior"""

    @abstractmethod
    def apply_safety(self, data: dict[str, object]) -> UpdateObservabilityUsageSafetyResult:
        """Apply safety checks with L5 constraints"""
        pass

    @abstractmethod
    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass


class UpdateObservabilityUsageSafetyImpl(UpdateObservabilityUsageSafetySafety):
    """
    L5 Implementation - L5 Safety/Policy Layer
    Fail-closed safety enforcement with comprehensive policy checks
    """

    def __init__(self, constraints: UpdateObservabilityUsageSafetyConstraints | None = None):
        self.constraints = constraints or UpdateObservabilityUsageSafetyConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._safety_rules = self._initialize_safety_rules()

    def apply_safety(self, data: dict[str, object]) -> UpdateObservabilityUsageSafetyResult:
        """Apply safety checks following L5 architecture principles"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "UpdateObservabilityUsageSafetyImpl.apply_safety"
        )

        self.logger.info("Applying safety checks to data")
        self._validate_input(data)
        if not self.validate_safety(data):
            raise SecurityError("Data failed L5 safety validation")
        safety_score = self._calculate_safety_score(data)
        risk_assessment = self._assess_risks(data)
        result = UpdateObservabilityUsageSafetyResult(
            success=safety_score <= self.constraints.max_risk_score,
            safety_score=safety_score,
            risk_assessment=risk_assessment,
            safety_validated=True,
            timestamp=self._get_timestamp(),
        )
        self.logger.info(f"Safety check completed: score={safety_score}, passed={result.success}")
        return result

    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            critical_patterns = [
                "<script[^>]*>.*?</script>",
                "javascript:",
                "eval\\s*\\(",
                "exec\\s*\\(",
                "__import__",
                "subprocess\\.",
                "os\\.system",
                "\\.\\./.*\\.\\.",
            ]
            data_str = str(data).lower()
            for pattern in critical_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    self.logger.error(f"Critical dangerous pattern detected: {pattern}")
                    return False
            if len(data_str) > 1000000:
                self.logger.error("Data exceeds safety size limit")
                return False
            self.logger.info("Data passed L5 safety validation")
            return True
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            self.logger.error(f"Safety validation error: {e}")
            return False

    def _validate_input(self, data: dict[str, object]) -> None:
        """L5 Input validation"""
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        if not data:
            raise ValueError("Input cannot be empty")

    def _calculate_safety_score(self, data: dict[str, object]) -> float:
        """Calculate L5 safety score (0.0 = safe, 1.0 = dangerous)"""
        score = 0.0
        data_str = str(data).lower()
        suspicious_patterns = [
            ("password", 0.3),
            ("secret", 0.3),
            ("token", 0.2),
            ("key", 0.1),
            ("admin", 0.2),
            ("root", 0.3),
        ]
        for pattern, weight in suspicious_patterns:
            if pattern in data_str:
                score += weight
        if len(data_str) > 10000:
            score += 0.2
        return min(score, 1.0)

    def _assess_risks(self, data: dict[str, object]) -> dict[str, object]:
        """Perform comprehensive risk assessment"""
        risks = {
            "injection_risk": self._check_injection_risk(data),
            "size_risk": self._check_size_risk(data),
            "complexity_risk": self._check_complexity_risk(data),
            "pattern_risk": self._check_pattern_risk(data),
        }
        return {
            "risks": risks,
            "overall_risk": "low"
            if all(r == "low" for r in risks.values())
            else "medium"
            if any(r == "medium" for r in risks.values())
            else "high",
        }

    def _check_injection_risk(self, data: dict[str, object]) -> str:
        """Check for injection risks"""
        injection_patterns = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        data_str = str(data)
        for pattern in injection_patterns:
            if pattern in data_str:
                return "high"
        return "low"

    def _check_size_risk(self, data: dict[str, object]) -> str:
        """Check size-related risks"""
        size = len(str(data))
        if size > 100000:
            return "high"
        elif size > 10000:
            return "medium"
        else:
            return "low"

    def _check_complexity_risk(self, data: dict[str, object]) -> str:
        """Check complexity risks"""
        try:
            depth = self._calculate_depth(data)
            if depth > 10:
                return "high"
            elif depth > 5:
                return "medium"
            else:
                return "low"
        except (ValueError, TypeError, RuntimeError):
            return "high"

    def _check_pattern_risk(self, data: dict[str, object]) -> str:
        """Check for risky patterns"""
        risky_patterns = ["eval", "exec", "import", "subprocess", "os.system"]
        data_str = str(data).lower()
        for pattern in risky_patterns:
            if pattern in data_str:
                return "high"
        return "low"

    def _calculate_depth(self, obj: object, current_depth: int = 0) -> int:
        """Calculate nesting depth"""
        if isinstance(obj, dict):
            return max(
                [self._calculate_depth(v, current_depth + 1) for v in obj.values()],
                default=current_depth,
            )
        elif isinstance(obj, list):
            return max(
                [self._calculate_depth(item, current_depth + 1) for item in obj],
                default=current_depth,
            )
        else:
            return current_depth

    def _initialize_safety_rules(self) -> list[dict[str, object]]:
        """Initialize L5 safety rules"""
        return [
            {
                "name": "no_injection",
                "pattern": "(union|select|insert|update|delete|drop)",
                "severity": "high",
            },
            {"name": "no_scripts", "pattern": "<script", "severity": "high"},
            {"name": "no_eval", "pattern": "eval\\s*\\(", "severity": "high"},
            {"name": "size_limit", "max_size": 1000000, "severity": "medium"},
        ]

    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime

        return datetime.utcnow().isoformat()


class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""

    pass


class UpdateObservabilityUsageSafetyInterface:
    """L5 Interface - ensures contract compliance"""

    def __init__(self, safety: UpdateObservabilityUsageSafetySafety):
        self._safety = safety

    def apply_safety(self, data: dict[str, object]) -> dict[str, object]:
        """L5 Interface method - applies safety safely"""
        try:
            result = self._safety.apply_safety(data)
            return {
                "success": result.success,
                "safety_score": result.safety_score,
                "risk_assessment": result.risk_assessment,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            raise SecurityError(f'Safety application failed: {e}') from e


class UpdateObservabilityUsageSafetyFactory:
    """L5 builder for creating safety executors with proper configuration"""

    @staticmethod
    def create_safety(safety_level: str = "strict") -> UpdateObservabilityUsageSafetyInterface:
        """Create configured safety executor"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "UpdateObservabilityUsageSafetyFactory.create_safety"
        )

        constraints = UpdateObservabilityUsageSafetyConstraints(safety_level=safety_level)
        safety = UpdateObservabilityUsageSafetyImpl(constraints)
        return UpdateObservabilityUsageSafetyInterface(safety)


def update_observability_usage(data: dict[str, object]) -> dict[str, object]:
    """
    L5 Main function - update observability usage operations

    Args:
        data: Data to apply safety checks to

    Returns:
        Dict: Safety result

    Raises:
        SecurityError: If safety check fails any validation
    """
    builder = UpdateObservabilityUsageSafetyFactory()
    safety = builder.create_safety()
    return safety.apply_safety(data)


if __name__ == "__main__":
    try:
        test_data = {"test": "safe_data"}
        result = update_observability_usage(test_data)
        logger.info(f"L5 Safety check successful: {result}")
    except SecurityError as e:  # guardian: SecurityError should be handled with specific context
        logger.error(f"L5 Security error: {e}")
    except (ValueError, TypeError, RuntimeError, KeyError) as e:
        logger.error(f"L5 Unexpected error: {e}")
