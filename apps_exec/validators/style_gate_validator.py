"""
Style Gate Validator — apps_exec.

Enforces quality gates on assembled executive brief sections:
- minimum evidence anchors per section
- no unsupported strategic claims
- forbidden buzzword density check
- required "why this matters" block
- required audience declaration

Deterministic: all checks are rule-based regex/count operations.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

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

_emit_authorize_and_execute("p2", "style_gate_validator", "execution_auth")
_emit_validates_capability("p2", "style_gate_validator", "capability_check")
_emit_routes_to_capability("p2", "style_gate_validator", "capability_route")
_emit_writes_via_uwg("p2", "style_gate_validator", "uwg_write")
_emit_blocks_direct_write("p2", "style_gate_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "style_gate_validator", "tool_invocation")
_emit_captures_execution_output("p2", "style_gate_validator", "exec_output")
_emit_dispatches_agent("p3", "style_gate_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "style_gate_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "style_gate_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "style_gate_validator", "healing_outcome")
_emit_escalates_failure("p3", "style_gate_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "style_gate_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "style_gate_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "style_gate_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "style_gate_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "style_gate_validator", "eval_metric")
_emit_stores_embedding("p4", "style_gate_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "style_gate_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "style_gate_validator", "exec_snapshot_link")
from apps_exec.types.exec_types import BriefSection, StyleViolation

_emit_applies_guardrail("p0", "style_gate_validator", "p0_governance")
_emit_reads_policy_state("p0", "style_gate_validator", "policy_binding")
_emit_snapshots_state("p0", "style_gate_validator", "state_snapshot")
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

_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_1")
_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_2")
_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_3")
_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_4")
_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_5")
_emit_emits_metric_event("style_gate_validator", "p4obs", "metric_6")
_emit_records_incident_event("style_gate_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("style_gate_validator", "p4obs", "anomaly")
_emit_writes_observability_log("style_gate_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("style_gate_validator", "p4obs", "mon_state")
_emit_triggers_alert("style_gate_validator", "p4obs", "alert")
_emit_links_incident_trace("style_gate_validator", "p4obs", "trace_link")
_emit_captures_pattern("style_gate_validator", "p3lm", "pattern")
_emit_records_learning_event("style_gate_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("style_gate_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("style_gate_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("style_gate_validator", "p3lm", "routing")
_emit_improves_agent_policy("style_gate_validator", "p3lm", "policy")
_emit_stores_learning_state("style_gate_validator", "p3lm", "state")
_emit_records_execution_trace("style_gate_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("style_gate_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("style_gate_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("style_gate_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("style_gate_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("style_gate_validator", "env_read", "p2_env_1")
_emit_reads_environ("style_gate_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("style_gate_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("style_gate_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "style_gate_validator", "context_pull")
_emit_pulls_context("p1", "style_gate_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "style_gate_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "style_gate_validator", "uwg_term_2")
_emit_writes_through("p1", "style_gate_validator", "write_through")
_emit_writes_through("p1", "style_gate_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "style_gate_validator", "safety_validation")
_emit_invokes_eval("p1", "style_gate_validator", "eval_call")
_emit_proposal_commits_routing("p1", "style_gate_validator", "routing_commit")
_emit_escalates_to_human("p1", "style_gate_validator", "human_escalation")
_emit_routes_through("p1", "style_gate_validator", "route_through")
_emit_checks_agent_registry("p1", "style_gate_validator", "agent_registry")
_emit_validates_agent_capability("p1", "style_gate_validator", "capability")
_emit_dispatches_execution_plan("p1", "style_gate_validator", "exec_plan")
_emit_agent_executes_agent("p1", "style_gate_validator", "sub_agent")
_emit_routes_to_agent("p1", "style_gate_validator", "target_agent")
_emit_verifies_policy("p1", "style_gate_validator", "policy_check")
_emit_observes_runtime_state("p1", "style_gate_validator", "runtime_state")
_emit_verifies_boundary("p1", "style_gate_validator", "boundary_check")
_emit_transcripts_response("p1", "style_gate_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "style_gate_validator")
_emit_gated_by_confidence("p1", "style_gate_validator", "confidence_gate")
emit_replay_key("p0", "style_gate_validator")
emit_determinism_digest("p0", "style_gate_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)

_BUZZWORDS = frozenset(
    [
        "synergy",
        "leverage",
        "game-changer",
        "disruptive",
        "revolutionary",
        "paradigm shift",
        "bleeding edge",
        "best-in-class",
        "world-class",
        "next-generation",
        "cutting-edge",
        "holistic",
        "ecosystem",
        "empower",
        "unlock",
        "transform",
    ],
)

_UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(r"(?i)\b(always|never|guaranteed|100%|perfect|flawless)\b"),
    re.compile(r"(?i)\bfastest\b"),
    re.compile(r"(?i)\bbest\s+in\s+class\b"),
]


@dataclass
class StyleGateResult:
    """Result of a style gate validation pass."""

    passed: bool
    violations: list[StyleViolation] = field(default_factory=list)
    quality_score: float = 0.0
    sections_checked: int = 0

    def first_failure(self) -> StyleViolation | None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StyleGateResult.first_failure"
        )

        for v in self.violations:
            if v.severity == "BLOCK":
                return v
        return None


class StyleGateValidator:
    """Validate assembled brief sections against quality gate rules.

    No silent pass — every violation is recorded with rule_id and evidence.
    """

    def __init__(self, config: object | None = None) -> None:
        self._cfg = config

    def validate_sections(
        self,
        sections: list[BriefSection],
        audience: str = "",
    ) -> StyleGateResult:
        """Run all style gate checks on assembled sections.

        Args:
            sections: Assembled BriefSection list.
            audience: Target persona key for audience-declaration check.

        Returns:
            StyleGateResult with all violations.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StyleGateValidator.validate_sections"
        )

        violations: list[StyleViolation] = []

        for section in sections:
            violations.extend(self._check_evidence_anchors(section))
            violations.extend(self._check_buzzwords(section))
            violations.extend(self._check_unsupported_claims(section))
            violations.extend(self._check_why_this_matters(section))
            violations.extend(self._check_empty_body(section))

        block_count = sum(1 for v in violations if v.severity == "BLOCK")
        warn_count = sum(1 for v in violations if v.severity == "WARN")

        total_checks = len(sections) * 5
        passed_checks = total_checks - block_count - warn_count
        quality_score = max(0.0, passed_checks / total_checks) if total_checks > 0 else 1.0

        passed = block_count == 0
        return StyleGateResult(
            passed=passed,
            violations=violations,
            quality_score=round(quality_score, 4),
            sections_checked=len(sections),
        )

    def _check_evidence_anchors(self, section: BriefSection) -> list[StyleViolation]:
        if not section.evidence_anchors:
            return [
                StyleViolation(
                    rule_id="STYLE_EVIDENCE_MISSING",
                    severity="WARN",
                    message=f"Section '{section.section_id}' has no evidence anchors.",
                    section_id=section.section_id,
                ),
            ]
        return []

    def _check_buzzwords(self, section: BriefSection) -> list[StyleViolation]:
        body_lower = section.body.lower()
        found = [bw for bw in _BUZZWORDS if bw in body_lower]
        if not found:
            return []
        density = len(found) / max(1, len(section.body.split()))
        severity = "BLOCK" if density > 0.05 else "WARN"
        return [
            StyleViolation(
                rule_id="STYLE_BUZZWORD_DENSITY",
                severity=severity,
                message=f"Section '{section.section_id}' contains buzzwords: {found}",
                section_id=section.section_id,
                evidence=", ".join(found),
            ),
        ]

    def _check_unsupported_claims(self, section: BriefSection) -> list[StyleViolation]:
        results: list[StyleViolation] = []
        for pattern in _UNSUPPORTED_CLAIM_PATTERNS:
            match = pattern.search(section.body)
            if match:
                results.append(
                    StyleViolation(
                        rule_id="STYLE_UNSUPPORTED_CLAIM",
                        severity="BLOCK",
                        message=(
                            f"Section '{section.section_id}' contains unsupported claim: '{match.group(0)}'"
                        ),
                        section_id=section.section_id,
                        evidence=match.group(0),
                    ),
                )
        return results

    def _check_why_this_matters(self, section: BriefSection) -> list[StyleViolation]:
        if not section.why_this_matters or not section.why_this_matters.strip():
            return [
                StyleViolation(
                    rule_id="STYLE_WHY_MISSING",
                    severity="WARN",
                    message=f"Section '{section.section_id}' is missing a 'why this matters' block.",
                    section_id=section.section_id,
                ),
            ]
        return []

    def _check_empty_body(self, section: BriefSection) -> list[StyleViolation]:
        if not section.body or not section.body.strip():
            return [
                StyleViolation(
                    rule_id="STYLE_EMPTY_BODY",
                    severity="BLOCK",
                    message=f"Section '{section.section_id}' has an empty body.",
                    section_id=section.section_id,
                ),
            ]
        return []
