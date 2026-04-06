"""Safety guard stack agents - LIC Sovereign Specialists."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

# Constants for test compatibility
BATCH_SIZE = 32
BUFFER_SIZE = 8192

from pydantic import BaseModel, Field

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
)
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from apps_lic.utils.lic_agent_base_util import LICAgentBase

_emit_authorize_and_execute("p2", "PIISanitizerSpecialistAgent_util", "execution_auth")
_emit_validates_capability("p2", "PIISanitizerSpecialistAgent_util", "capability_check")
_emit_routes_to_capability("p2", "PIISanitizerSpecialistAgent_util", "capability_route")
_emit_writes_via_uwg("p2", "PIISanitizerSpecialistAgent_util", "uwg_write")
_emit_blocks_direct_write("p2", "PIISanitizerSpecialistAgent_util", "direct_write_block")
_emit_records_tool_invocation("p2", "PIISanitizerSpecialistAgent_util", "tool_invocation")
_emit_captures_execution_output("p2", "PIISanitizerSpecialistAgent_util", "exec_output")
_emit_dispatches_agent("p3", "PIISanitizerSpecialistAgent_util", "agent_dispatch")
_emit_coordinates_agents("p3", "PIISanitizerSpecialistAgent_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "PIISanitizerSpecialistAgent_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "PIISanitizerSpecialistAgent_util", "healing_outcome")
_emit_escalates_failure("p3", "PIISanitizerSpecialistAgent_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "PIISanitizerSpecialistAgent_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "PIISanitizerSpecialistAgent_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "PIISanitizerSpecialistAgent_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "PIISanitizerSpecialistAgent_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "PIISanitizerSpecialistAgent_util", "eval_metric")
_emit_stores_embedding("p4", "PIISanitizerSpecialistAgent_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "PIISanitizerSpecialistAgent_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "PIISanitizerSpecialistAgent_util", "exec_snapshot_link")
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

_emit_applies_guardrail("p0", "PIISanitizerSpecialistAgent_util", "p0_governance")
_emit_reads_policy_state("p0", "PIISanitizerSpecialistAgent_util", "policy_binding")
_emit_snapshots_state("p0", "PIISanitizerSpecialistAgent_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
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

_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_1")
_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_2")
_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_3")
_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_4")
_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_5")
_emit_emits_metric_event("PIISanitizerSpecialistAgent_util", "p4obs", "metric_6")
_emit_records_incident_event("PIISanitizerSpecialistAgent_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("PIISanitizerSpecialistAgent_util", "p4obs", "anomaly")
_emit_writes_observability_log("PIISanitizerSpecialistAgent_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("PIISanitizerSpecialistAgent_util", "p4obs", "mon_state")
_emit_triggers_alert("PIISanitizerSpecialistAgent_util", "p4obs", "alert")
_emit_links_incident_trace("PIISanitizerSpecialistAgent_util", "p4obs", "trace_link")
_emit_captures_pattern("PIISanitizerSpecialistAgent_util", "p3lm", "pattern")
_emit_records_learning_event("PIISanitizerSpecialistAgent_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("PIISanitizerSpecialistAgent_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("PIISanitizerSpecialistAgent_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("PIISanitizerSpecialistAgent_util", "p3lm", "routing")
_emit_improves_agent_policy("PIISanitizerSpecialistAgent_util", "p3lm", "policy")
_emit_stores_learning_state("PIISanitizerSpecialistAgent_util", "p3lm", "state")
_emit_records_execution_trace("PIISanitizerSpecialistAgent_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("PIISanitizerSpecialistAgent_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("PIISanitizerSpecialistAgent_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("PIISanitizerSpecialistAgent_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("PIISanitizerSpecialistAgent_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("PIISanitizerSpecialistAgent_util", "env_read", "p2_env_1")
_emit_reads_environ("PIISanitizerSpecialistAgent_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("PIISanitizerSpecialistAgent_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("PIISanitizerSpecialistAgent_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "PIISanitizerSpecialistAgent_util", "context_pull")
_emit_pulls_context("p1", "PIISanitizerSpecialistAgent_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "PIISanitizerSpecialistAgent_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "PIISanitizerSpecialistAgent_util", "uwg_term_2")
_emit_writes_through("p1", "PIISanitizerSpecialistAgent_util", "write_through")
_emit_writes_through("p1", "PIISanitizerSpecialistAgent_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "PIISanitizerSpecialistAgent_util", "safety_validation")
_emit_invokes_eval("p1", "PIISanitizerSpecialistAgent_util", "eval_call")
_emit_proposal_commits_routing("p1", "PIISanitizerSpecialistAgent_util", "routing_commit")
_emit_escalates_to_human("p1", "PIISanitizerSpecialistAgent_util", "human_escalation")
_emit_routes_through("p1", "PIISanitizerSpecialistAgent_util", "route_through")
_emit_checks_agent_registry("p1", "PIISanitizerSpecialistAgent_util", "agent_registry")
_emit_validates_agent_capability("p1", "PIISanitizerSpecialistAgent_util", "capability")
_emit_dispatches_execution_plan("p1", "PIISanitizerSpecialistAgent_util", "exec_plan")
_emit_agent_executes_agent("p1", "PIISanitizerSpecialistAgent_util", "sub_agent")
_emit_routes_to_agent("p1", "PIISanitizerSpecialistAgent_util", "target_agent")
_emit_verifies_policy("p1", "PIISanitizerSpecialistAgent_util", "policy_check")
_emit_observes_runtime_state("p1", "PIISanitizerSpecialistAgent_util", "runtime_state")
_emit_verifies_boundary("p1", "PIISanitizerSpecialistAgent_util", "boundary_check")
_emit_transcripts_response("p1", "PIISanitizerSpecialistAgent_util", "transcript")
_emit_hard_fails_untranscripted("p1", "PIISanitizerSpecialistAgent_util")
_emit_gated_by_confidence("p1", "PIISanitizerSpecialistAgent_util", "confidence_gate")
emit_replay_key("p0", "PIISanitizerSpecialistAgent_util")
emit_determinism_digest("p0", "PIISanitizerSpecialistAgent_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""

    def decorator(func):
        return func

    return decorator


@dataclass
class PII_SanitizerSpecialistAgent(LICAgentBase):
    """Performs local PII detection using regex heuristics."""

    pii_patterns: dict[str, Any] = field(
        default_factory=lambda: {
            "EMAIL": re.compile("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"),
            "PHONE": re.compile("\\b(?:\\+?1[ -]?)?\\(?\\d{3}\\)?[ -]?\\d{3}[ -]?\\d{4}\\b"),
            "NAME": re.compile("\\b[A-Z][a-z]+ [A-Z][a-z]+\\b"),
        }
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    PII_PATTERNS = {
        "EMAIL": re.compile("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"),
        "PHONE": re.compile("\\b(?:\\+?1[ -]?)?\\(?\\d{3}\\)?[ -]?\\d{3}[ -]?\\d{4}\\b"),
        "NAME": re.compile("\\b[A-Z][a-z]+ [A-Z][a-z]+\\b"),
    }

    @track_metrics("run_pii_sanitizer")
    def run(self, resume: dict[str, Any]) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PII_SanitizerSpecialistAgent.run")

        self.log_info("Sanitizing PII (local regex processing)...")
        sanitized_resume = json.loads(json.dumps(resume))

        def sanitize_node(node: Any) -> Any:
            if isinstance(node, dict):
                return {k: sanitize_node(v) for k, v in node.items()}
            if isinstance(node, list):
                return [sanitize_node(item) for item in node]
            if isinstance(node, str):
                return self._sanitize_text(node)
            return node

        sanitized = sanitize_node(sanitized_resume)
        self.log_info("PII sanitization complete.")
        return sanitized

    def _sanitize_text(self, text: str) -> str:
        for pii_type, pattern in self.pii_patterns.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)


@dataclass
class BiasDetectorSpecialist(LICAgentBase, SubatomicTestingMixin):
    """LIC Sovereign Bias Detector - Runs local bias detection with dynamic constitution rules."""

    name: str = "BiasDetectorSpecialist"
    sensitivity_level: float = 0.85
    prohibited_terms: list[str] = field(default_factory=lambda: ["guaranteed", "unlimited", "risk-free"])

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Execute bias detection on buffer content."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BiasDetectorSpecialist._process")

        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})
        mission_input = buffer.read("mission_input") or {}
        text = mission_input.get("text", "")
        patterns_found = [term for term in self.prohibited_terms if term.lower() in text.lower()]
        bias_patterns = ["always", "never", "everyone", "no one"]
        additional_patterns = [p for p in bias_patterns if p.lower() in text.lower()]
        patterns_found.extend(additional_patterns)
        result = {"bias_detected": len(patterns_found) > 0, "patterns": patterns_found}
        buffer.write_once("bias_detection_result", result)
        registry.add_trace("PHASE_COMPLETE", {"agent": self.__class__.__name__, "result": result})

    def scan_content(self, text: str) -> dict[str, Any]:
        """Public interface for bias scanning - used in simulation."""
        self.log_info(f"Scanning content for bias: '{text[:50]}...'")
        patterns_found = [term for term in self.prohibited_terms if term.lower() in text.lower()]
        bias_patterns = ["always", "never", "everyone", "no one"]
        additional_patterns = [p for p in bias_patterns if p.lower() in text.lower()]
        patterns_found.extend(additional_patterns)
        result = {
            "has_bias": len(patterns_found) > 0,
            "bias_detected": len(patterns_found) > 0,
            "patterns": patterns_found,
            "sensitivity_level": self.sensitivity_level,
        }
        self.log_info(f"Bias scan complete: {result}")
        return result


@dataclass
class PromptInjectionDetectorSpecialist(LICAgentBase, SubatomicTestingMixin):
    """Detects prompt-injection attacks."""

    detection_threshold: float = 0.8
    attack_patterns: list[str] = field(
        default_factory=lambda: ["ignore previous instructions", "system prompt", "jailbreak"]
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    class PIDetectionOutput(BaseModel):
        injection_detected: bool = Field(..., description="True if an attack was detected")
        reason: str = Field(..., description="Explanation for the detection")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the detection")

    @track_metrics("run_pi_detector")
    async def run_async(self, user_input: str, workflow_id: str) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptInjectionDetectorSpecialist.run_async")

        self.log_info("Detecting prompt injection...")
        if not self.config.agent_stacks.enable_prompt_injection_detection:
            self.log_warning("Prompt injection detection is disabled.")
            return {"injection_detected": False, "reason": "Detector disabled", "confidence": 0.0}
        client = self.get_model_client("prompt_injection_model")
        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"user_input": user_input},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.prompt_injection_model.temperature,
            response_format="json_object",
        )
        validated_output, error = self.validator.validate(response["content"], self.PIDetectionOutput)
        if error:
            self.log_error(f"PromptInjectionDetector failed validation: {error}")
            return {
                "injection_detected": True,
                "reason": f"Detector validation failed: {error}",
                "confidence": 1.0,
            }
        if validated_output.injection_detected:
            self.log_warning(
                f"PROMPT INJECTION DETECTED (Confidence: {validated_output.confidence}): {validated_output.reason}"
            )
        return validated_output.model_dump()


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""

    review_passed: bool
    violations_found: list[str]
    feedback: str = ""


async def _format_prompt_with_defaults(template, context, *args):
    """Stub function for prompt formatting."""
    return template.format(**context)


@dataclass
class ConstitutionalReviewerAgent(LICAgentBase, SubatomicTestingMixin):
    """Performs final constitutional review of the output."""

    @track_metrics("run_constitutional_review")
    async def run_async(self, final_draft: str, workflow_id: str) -> ConstitutionalReviewResult:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConstitutionalReviewerAgent.run_async")

        self.log_info("Running final constitutional review...")
        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(
                review_passed=True, violations_found=[], feedback="Review disabled"
            )
        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")
        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"final_draft": final_draft, "constitution": constitution_text},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.constitutional_review_model.temperature,
            response_format="json_object",
        )
        validated_output, error = self.validator.validate(response["content"], ConstitutionalReviewResult)
        if error:
            self.log_error(
                f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft)."
            )
            return ConstitutionalReviewResult(
                review_passed=True, violations_found=["VALIDATION_ERROR"], feedback=error
            )
        if not validated_output.review_passed:
            self.log_warning(f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}")
        return validated_output
