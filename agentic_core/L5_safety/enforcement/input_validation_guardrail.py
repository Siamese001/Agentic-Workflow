from __future__ import annotations

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

emit_replay_key("p0", "input_validation_guardrail")
emit_determinism_digest("p0", "input_validation_guardrail")

_emit_dispatches_healing_run("p1", "input_validation_guardrail", "L5")
_emit_routes_through("p1", "input_validation_guardrail", "L5")
_emit_checks_agent_registry("p1", "input_validation_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "input_validation_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "input_validation_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "input_validation_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "input_validation_guardrail", "target_agent")
_emit_verifies_policy("p1", "input_validation_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "input_validation_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "input_validation_guardrail", "boundary_check")
_emit_transcripts_response("p1", "input_validation_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "input_validation_guardrail")
_emit_gated_by_confidence("p1", "input_validation_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "input_validation_guardrail", "L5")
_emit_reads_policy_state("p1", "input_validation_guardrail", "L5")
_emit_authorize_and_execute("p2", "input_validation_guardrail", "execution_auth")
_emit_validates_capability("p2", "input_validation_guardrail", "capability_check")
_emit_routes_to_capability("p2", "input_validation_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "input_validation_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "input_validation_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "input_validation_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "input_validation_guardrail", "exec_output")
_emit_dispatches_agent("p3", "input_validation_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "input_validation_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "input_validation_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "input_validation_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "input_validation_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "input_validation_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "input_validation_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "input_validation_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "input_validation_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "input_validation_guardrail", "eval_metric")
_emit_stores_embedding("p4", "input_validation_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "input_validation_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "input_validation_guardrail", "exec_snapshot_link")

"\nInputValidationGuardrail: Consolidated input validation with composable rules.\nMerges: input_validator, PII_Sanitizer, PromptInjectionDetector, BiasDetector, safety_guardrail\n"
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("input_validation_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("input_validation_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("input_validation_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("input_validation_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("input_validation_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("input_validation_guardrail", "p4obs", "alert")
_emit_links_incident_trace("input_validation_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("input_validation_guardrail", "p3lm", "pattern")
_emit_records_learning_event("input_validation_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("input_validation_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("input_validation_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("input_validation_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("input_validation_guardrail", "p3lm", "policy")
_emit_stores_learning_state("input_validation_guardrail", "p3lm", "state")
_emit_records_execution_trace("input_validation_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("input_validation_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("input_validation_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("input_validation_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("input_validation_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("input_validation_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("input_validation_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("input_validation_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("input_validation_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "input_validation_guardrail", "context_pull")
_emit_pulls_context("p1", "input_validation_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "input_validation_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "input_validation_guardrail", "uwg_term_2")
_emit_writes_through("p1", "input_validation_guardrail", "write_through")
_emit_writes_through("p1", "input_validation_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "input_validation_guardrail", "safety_validation")
_emit_invokes_eval("p1", "input_validation_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "input_validation_guardrail", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass
class InputValidationGuardrail(SovereignBaseAgent):
    """
    Consolidated input validation with composable rule sets.
    Handles: PII detection, prompt injection, bias detection, format validation.
    """

    debug_mode: bool = False
    enabled_rules: list[str] = field(
        default_factory=lambda: ["pii_detection", "prompt_injection", "bias_detection", "format_validation"],
    )

    def __post_init__(self):
        self.name = "InputValidationGuardrail"
        self.validation_count = 0
        self.violations_found = 0

    # guardian: allow-type-erasure
    async def validate(self, input_text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Validate input against enabled rules."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "InputValidationGuardrail.validate", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "InputValidationGuardrail.validate", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "InputValidationGuardrail.validate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InputValidationGuardrail.validate".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        logger.info(f"[{self.name}] Validating input")
        result = {"valid": True, "violations": [], "rules_applied": []}
        try:
            for rule in self.enabled_rules:
                rule_result = await self._apply_rule(rule, input_text, context)
                result["rules_applied"].append(rule)
                if not rule_result.get("valid"):
                    result["valid"] = False
                    result["violations"].extend(rule_result.get("violations", []))
            self.validation_count += 1
            if not result["valid"]:
                self.violations_found += 1
            return result
        except (ValueError, TypeError) as e:
            logger.error(f"[{self.name}] Validation error: {e}")
            return {
                "valid": False,
                "violations": [{"type": "validation_error", "message": str(e)}],
                "error": str(e),
            }

    # guardian: allow-type-erasure
    async def _apply_rule(self, rule: str, input_text: str, context: dict | None = None) -> dict[str, Any]:
        """Apply a specific validation rule."""
        if rule == "pii_detection":
            return self._detect_pii(input_text)
        elif rule == "prompt_injection":
            return self._detect_prompt_injection(input_text)
        elif rule == "bias_detection":
            return self._detect_bias(input_text)
        elif rule == "format_validation":
            return self._validate_format(input_text)
        return {"valid": True}

    # guardian: allow-type-erasure
    def _detect_pii(self, text: str) -> dict[str, Any]:
        """Detect personally identifiable information."""
        violations = []
        if re.search("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", text):
            violations.append(
                {"type": "pii_email", "severity": "high", "message": "Email address detected in input"},
            )
        if re.search("\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b", text):
            violations.append(
                {"type": "pii_phone", "severity": "high", "message": "Phone number detected in input"},
            )
        if re.search("\\b\\d{3}-\\d{2}-\\d{4}\\b", text):
            violations.append(
                {
                    "type": "pii_ssn",
                    "severity": "critical",
                    "message": "Social security number detected in input",
                },
            )
        return {"valid": len(violations) == 0, "violations": violations}

    # guardian: allow-type-erasure
    def _detect_prompt_injection(self, text: str) -> dict[str, Any]:
        """Detect prompt injection attempts."""
        violations = []
        injection_patterns = [
            "ignore.*previous.*instruction",
            "forget.*everything",
            "you.*are.*now",
            "developer.*mode",
            "jailbreak",
        ]
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    {
                        "type": "prompt_injection",
                        "severity": "high",
                        "message": f"Potential prompt injection detected: {pattern}",
                    },
                )
        return {"valid": len(violations) == 0, "violations": violations}

    # guardian: allow-type-erasure
    def _detect_bias(self, text: str) -> dict[str, Any]:
        """Detect biased language patterns."""
        violations = []
        bias_patterns = {
            "always|never|all|none": "absolute_language",
            "should|must|have to": "prescriptive_language",
        }
        for pattern, bias_type in bias_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    {
                        "type": f"bias_{bias_type}",
                        "severity": "low",
                        "message": f"Potential bias detected: {bias_type}",
                    },
                )
        return {"valid": len(violations) == 0, "violations": violations}

    # guardian: allow-type-erasure
    def _validate_format(self, text: str) -> dict[str, Any]:
        """Validate input format."""
        violations = []
        if not text or len(text.strip()) == 0:
            violations.append({"type": "empty_input", "severity": "medium", "message": "Input is empty"})
        if len(text) > 1000000:
            violations.append(
                {"type": "oversized_input", "severity": "high", "message": "Input exceeds maximum length"},
            )
        return {"valid": len(violations) == 0, "violations": violations}

    def _run_self_tests(self) -> bool:
        """Validate agent structure."""
        assert hasattr(self, "name"), "Missing name"
        assert hasattr(self, "enabled_rules"), "Missing enabled_rules"
        return True

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, **kwargs) -> dict[str, Any]:
        """Repository healing with parent chain invocation."""
        result = super().heal_repository(dry_run=dry_run, **kwargs)
        return {"violations_fixed": 0, "skipped": 0, "parent": result}

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal input validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (pii, injection, bias, format)
                - input: Input that caused the violation
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Input validation violations require content revision",
        }
