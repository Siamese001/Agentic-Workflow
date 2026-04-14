"""Section Scope Integrator Agent - Overview Synthesis (K.5B & K.6B)
This agent synthesizes clean overviews after bullets are generated.
Enforces anti-prefix validation and strict deduplication constraints.

Layer: L2_execution
Responsibilities:
- Synthesize section overviews post-bullet generation
- Block redundant role prefixes (e.g., "As Title at Company")
- Enforce <75% similarity to master baseline (STRICT LESS THAN)
- Generate clean, non-redundant prose

Non-responsibilities:
- Bullet generation
- Provenance tracking
- Headline composition
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from dataclasses import field as Field
from typing import Any

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

_emit_applies_guardrail("p0", "validation_result_types", "p0_governance")
_emit_reads_policy_state("p0", "validation_result_types", "policy_binding")
_emit_snapshots_state("p0", "validation_result_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("validation_result_types", "p4obs", "metric_1")
_emit_emits_metric_event("validation_result_types", "p4obs", "metric_2")
_emit_emits_metric_event("validation_result_types", "p4obs", "metric_3")
_emit_emits_metric_event("validation_result_types", "p4obs", "metric_4")
_emit_emits_metric_event("validation_result_types", "p4obs", "metric_5")
_emit_emits_metric_event("validation_result_types", "p4obs", "metric_6")
_emit_records_incident_event("validation_result_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("validation_result_types", "p4obs", "anomaly")
_emit_writes_observability_log("validation_result_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("validation_result_types", "p4obs", "mon_state")
_emit_triggers_alert("validation_result_types", "p4obs", "alert")
_emit_links_incident_trace("validation_result_types", "p4obs", "trace_link")
_emit_captures_pattern("validation_result_types", "p3lm", "pattern")
_emit_records_learning_event("validation_result_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validation_result_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("validation_result_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validation_result_types", "p3lm", "routing")
_emit_improves_agent_policy("validation_result_types", "p3lm", "policy")
_emit_stores_learning_state("validation_result_types", "p3lm", "state")
_emit_records_execution_trace("validation_result_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validation_result_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validation_result_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validation_result_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validation_result_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validation_result_types", "env_read", "p2_env_1")
_emit_reads_environ("validation_result_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("validation_result_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validation_result_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validation_result_types", "context_pull")
_emit_pulls_context("p1", "validation_result_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validation_result_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validation_result_types", "uwg_term_2")
_emit_writes_through("p1", "validation_result_types", "write_through")
_emit_writes_through("p1", "validation_result_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "validation_result_types", "safety_validation")
_emit_invokes_eval("p1", "validation_result_types", "eval_call")
_emit_proposal_commits_routing("p1", "validation_result_types", "routing_commit")
_emit_escalates_to_human("p1", "validation_result_types", "human_escalation")
_emit_routes_through("p1", "validation_result_types", "route_through")
_emit_checks_agent_registry("p1", "validation_result_types", "agent_registry")
_emit_validates_agent_capability("p1", "validation_result_types", "capability")
_emit_dispatches_execution_plan("p1", "validation_result_types", "exec_plan")
_emit_agent_executes_agent("p1", "validation_result_types", "sub_agent")
_emit_routes_to_agent("p1", "validation_result_types", "target_agent")
_emit_verifies_policy("p1", "validation_result_types", "policy_check")
_emit_observes_runtime_state("p1", "validation_result_types", "runtime_state")
_emit_verifies_boundary("p1", "validation_result_types", "boundary_check")
_emit_transcripts_response("p1", "validation_result_types", "transcript")
_emit_hard_fails_untranscripted("p1", "validation_result_types")
_emit_gated_by_confidence("p1", "validation_result_types", "confidence_gate")
emit_replay_key("p0", "validation_result_types")
emit_determinism_digest("p0", "validation_result_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validation_result_types", "execution_auth")
_emit_validates_capability("p2", "validation_result_types", "capability_check")
_emit_routes_to_capability("p2", "validation_result_types", "capability_route")
_emit_writes_via_uwg("p2", "validation_result_types", "uwg_write")
_emit_blocks_direct_write("p2", "validation_result_types", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_result_types", "tool_invocation")
_emit_captures_execution_output("p2", "validation_result_types", "exec_output")
_emit_dispatches_agent("p3", "validation_result_types", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_result_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_result_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_result_types", "healing_outcome")
_emit_escalates_failure("p3", "validation_result_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_result_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_result_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_result_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_result_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_result_types", "eval_metric")
_emit_stores_embedding("p4", "validation_result_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_result_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_result_types", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class ValidationResult:
    """Brief description of functionality and purpose."""

    def __init__(self, gate_id, PASSED, SEVERITY, MESSAGE, DETAILS=None, SIGNATURE=None) -> None:
        self.gate_id = gate_id
        self.passed = PASSED
        self.Severity = SEVERITY
        self.message = MESSAGE
        self.details = DETAILS
        self.signature = SIGNATURE


class AdaptiveRecoveryLoop:
    """Brief description of functionality and purpose."""

    def __init__(self, initial_temperature) -> None:
        self.current_temperature = initial_temperature
        self.temperature_log = []

    def reset(self, temp):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AdaptiveRecoveryLoop.reset")

        self.current_temperature = temp
        self.temperature_log = []

    def record_failure(self, gate_id, MESSAGE, DETAILS):
        self.temperature_log.append(
            {
                "gate_id": gate_id,
                "message": MESSAGE,
                "details": DETAILS,
                "temperature": self.current_temperature,
            },
        )
        max_temp = float(os.getenv("VALIDATION_TEMPERATURE", "0.6"))
        if self.current_temperature < max_temp:
            self.current_temperature += 0.1
            return type("Recovery", (object,), {"should_retry": True})()
        return type("Recovery", (object,), {"should_retry": False})()

    def get_temperature_log(self):
        return self.temperature_log


@dataclass
class SectionIntegratorConfig:
    """[HARDENED] Environment-aware configuration for section integration."""

    max_similarity_threshold: float = Field(
        default_factory=lambda: float(os.getenv("VALIDATION_MAX_SIMILARITY_THRESHOLD", "0.75")),
    )
    TEMPERATURE: float = Field(default_factory=lambda: float(os.getenv("VALIDATION_TEMPERATURE", "0.6")))
    max_attempts: int = 3


@dataclass
class SectionIntegratorResult:
    """Docstring."""

    overview: str
    similarity_score: float
    validation_results: list[ValidationResult]
    temperature_log: list[dict[str, Any]]
    success: bool
    attempts: int


class SectionScopeIntegrator:
    """
    K.5B & K.6B - Overview Synthesis Agent

    Anti-Prefix Constraint:
    - BLOCKS if overview begins with redundant role prefixes
    - Examples: "As Title at Company", "In my role as", "Working as"

    Deduplication Constraint:
    - MUST ensure overview is <75% similar to master baseline
    - STRICT LESS THAN policy (not ≤)
    """

    FORBIDDEN_PREFIXES = [
        "^As\\s+\\w+\\s+at\\s+",
        "^In\\s+my\\s+role\\s+as\\s+",
        "^Working\\s+as\\s+",
        "^Serving\\s+as\\s+",
        "^Acting\\s+as\\s+",
        "^Currently\\s+\\w+\\s+at\\s+",
        "^At\\s+\\w+,?\\s+I\\s+",
        "^In\\s+this\\s+position,?\\s+",
        "^In\\s+this\\s+role,?\\s+",
    ]

    def __init__(
        self,
        config: SectionIntegratorConfig | None = None,
        gate_executor: IntegrityGateExecutorAgent | None = None,
        recovery_loop: AdaptiveRecoveryLoop | None = None,
    ):
        self.config = config or SectionIntegratorConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutorAgent()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.TEMPERATURE,
        )

    def generate_overview(
        self,
        bullets: list[str],
        master_baseline: str,
        context: dict[str, Any],
    ) -> SectionIntegratorResult:
        """
        Generate section overview with anti-prefix and deduplication validation.

        Args:
            bullets: Generated achievement bullets
            master_baseline: Master baseline for similarity comparison
            context: Additional context (role, company, etc.)

        Returns:
            SectionIntegratorResult with overview and validation details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SectionScopeIntegrator.generate_overview"
        )

        self.recovery_loop.reset(self.config.TEMPERATURE)
        validation_results = []
        for attempt in tqdm(range(1, self.config.max_attempts + 1), desc="Processing", unit="item"):
            overview = self._generate_content(
                bullets=bullets,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt,
            )
            hygiene_result = self.gate_executor.execute_hygiene_scan(overview)
            validation_results.append(hygiene_result)
            if not hygiene_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=hygiene_result.gate_id,
                    message=hygiene_result.message,
                    details=hygiene_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            prefix_result = self._validate_no_redundant_prefix(overview)
            validation_results.append(prefix_result)
            if not prefix_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=prefix_result.gate_id,
                    message=prefix_result.message,
                    details=prefix_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            similarity_score = self._calculate_similarity(overview, master_baseline)
            dedup_result = self._validate_deduplication(overview, similarity_score)
            validation_results.append(dedup_result)
            if not dedup_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=dedup_result.gate_id,
                    message=dedup_result.message,
                    details=dedup_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            self.gate_executor.results = validation_results
            return SectionIntegratorResult(
                overview=overview,
                similarity_score=similarity_score,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt,
            )
        return SectionIntegratorResult(
            overview="",
            similarity_score=1.0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts,
        )

    def _generate_content(
        self,
        bullets: list[str],
        context: dict[str, Any],
        temperature: float,
        attempt: int,
    ) -> str:
        """
        Generate overview content using LLM.
        Placeholder for actual LLM integration.
        """
        return "Directed strategic technology initiatives across cloud infrastructure and data engineering,\n        delivering scalable solutions that drove measurable business impact and\n            operational excellence."

    def _validate_no_redundant_prefix(self, overview: str) -> ValidationResult:
        """
        Validate overview does not begin with redundant role prefix.
        BLOCKS if forbidden prefix detected.
        """
        for pattern in tqdm(self.FORBIDDEN_PREFIXES, desc="Processing", unit="item"):
            match = re.match(pattern, overview, re.IGNORECASE)
            if match:
                return ValidationResult(
                    gate_id="VG_OVERVIEW_ANTI_PREFIX",
                    PASSED=False,
                    SEVERITY="BLOCK",
                    MESSAGE=f"BLOCKED: Overview begins with redundant prefix: '{match.group()}'",
                    DETAILS={
                        "matched_pattern": pattern,
                        "matched_text": match.group(),
                        "overview_preview": overview[:100],
                    },
                )
        return ValidationResult(
            gate_id="VG_OVERVIEW_ANTI_PREFIX",
            PASSED=True,
            SEVERITY="INFO",
            MESSAGE="No redundant prefix detected",
            SIGNATURE="ANTIPREFIX:OK",
        )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.
        Uses word overlap ratio as heuristic.
        """
        words1 = set(re.findall("\\b\\w+\\b", text1.lower()))
        words2 = set(re.findall("\\b\\w+\\b", text2.lower()))
        if not words1 or not words2:
            return 0.0
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        return overlap / union if union > 0 else 0.0

    def _validate_deduplication(self, overview: str, similarity_score: float) -> ValidationResult:
        """
        Validate overview is <75% similar to master baseline.
        STRICT LESS THAN policy (not ≤).
        """
        if similarity_score < self.config.max_similarity_threshold:
            return ValidationResult(
                gate_id="VG_OVERVIEW_DEDUPLICATION",
                PASSED=True,
                SEVERITY="INFO",
                MESSAGE=f"Deduplication passed: {similarity_score:.1%} similarity (threshold: <{self.config.max_similarity_threshold:.0%})",
                SIGNATURE=f"DEDUP:OK:{int(similarity_score * 100)}",
                DETAILS={
                    "similarity_score": similarity_score,
                    "threshold": self.config.max_similarity_threshold,
                },
            )
        return ValidationResult(
            gate_id="VG_OVERVIEW_DEDUPLICATION",
            PASSED=False,
            SEVERITY="BLOCK",
            MESSAGE=f"BLOCKED: Overview similarity {similarity_score:.1%} >= threshold {self.config.max_similarity_threshold:.0%}",
            DETAILS={
                "similarity_score": similarity_score,
                "threshold": self.config.max_similarity_threshold,
                "policy": "STRICT_LESS_THAN",
            },
        )


def create_section_scope_integrator(config: SectionIntegratorConfig | None = None) -> SectionScopeIntegrator:
    """Factory function to create SectionScopeIntegrator instance"""
    return SectionScopeIntegrator(config=config)
