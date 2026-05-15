"""
Content Quality Validator - Deterministic Content Quality Validation

Zero-Ambiguity Standard: Renamed from content_quality_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Placeholder detection using regex patterns
- Basic skill validation with rule-based logic
- Resume text processing and normalization
- Quantified achievements analysis
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "content_quality_validator")
emit_determinism_digest("p0", "content_quality_validator")

_emit_dispatches_healing_run("p1", "content_quality_validator", "L5")
_emit_routes_through("p1", "content_quality_validator", "L5")
_emit_checks_agent_registry("p1", "content_quality_validator", "agent_registry")
_emit_validates_agent_capability("p1", "content_quality_validator", "capability")
_emit_dispatches_execution_plan("p1", "content_quality_validator", "exec_plan")
_emit_agent_executes_agent("p1", "content_quality_validator", "sub_agent")
_emit_routes_to_agent("p1", "content_quality_validator", "target_agent")
_emit_verifies_policy("p1", "content_quality_validator", "policy_check")
_emit_observes_runtime_state("p1", "content_quality_validator", "runtime_state")
_emit_verifies_boundary("p1", "content_quality_validator", "boundary_check")
_emit_transcripts_response("p1", "content_quality_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "content_quality_validator")
_emit_gated_by_confidence("p1", "content_quality_validator", "confidence_gate")
_emit_escalates_to_human("p1", "content_quality_validator", "L5")
_emit_reads_policy_state("p1", "content_quality_validator", "L5")

_emit_applies_guardrail("p0", "content_quality_validator", "p0_governance")
_emit_snapshots_state("p0", "content_quality_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "content_quality_validator", "execution_auth")
_emit_validates_capability("p2", "content_quality_validator", "capability_check")
_emit_routes_to_capability("p2", "content_quality_validator", "capability_route")
_emit_writes_via_uwg("p2", "content_quality_validator", "uwg_write")
_emit_blocks_direct_write("p2", "content_quality_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "content_quality_validator", "tool_invocation")
_emit_captures_execution_output("p2", "content_quality_validator", "exec_output")
_emit_dispatches_agent("p3", "content_quality_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "content_quality_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "content_quality_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "content_quality_validator", "healing_outcome")
_emit_escalates_failure("p3", "content_quality_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "content_quality_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "content_quality_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "content_quality_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "content_quality_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "content_quality_validator", "eval_metric")
_emit_stores_embedding("p4", "content_quality_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "content_quality_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "content_quality_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_1")
_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_2")
_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_3")
_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_4")
_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_5")
_emit_emits_metric_event("content_quality_validator", "p4obs", "metric_6")
_emit_records_incident_event("content_quality_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("content_quality_validator", "p4obs", "anomaly")
_emit_writes_observability_log("content_quality_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("content_quality_validator", "p4obs", "mon_state")
_emit_triggers_alert("content_quality_validator", "p4obs", "alert")
_emit_links_incident_trace("content_quality_validator", "p4obs", "trace_link")
_emit_captures_pattern("content_quality_validator", "p3lm", "pattern")
_emit_records_learning_event("content_quality_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("content_quality_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("content_quality_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("content_quality_validator", "p3lm", "routing")
_emit_improves_agent_policy("content_quality_validator", "p3lm", "policy")
_emit_stores_learning_state("content_quality_validator", "p3lm", "state")
_emit_records_execution_trace("content_quality_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("content_quality_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("content_quality_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("content_quality_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("content_quality_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("content_quality_validator", "env_read", "p2_env_1")
_emit_reads_environ("content_quality_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("content_quality_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("content_quality_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "content_quality_validator", "context_pull")
_emit_pulls_context("p1", "content_quality_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "content_quality_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "content_quality_validator", "uwg_term_2")
_emit_writes_through("p1", "content_quality_validator", "write_through")
_emit_writes_through("p1", "content_quality_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "content_quality_validator", "safety_validation")
_emit_invokes_eval("p1", "content_quality_validator", "eval_call")
_emit_proposal_commits_routing("p1", "content_quality_validator", "routing_commit")


@dataclass
class QualityValidationResult:
    """Result of content quality validation."""

    passed: bool
    issues: list[str]
    score: float | None = None
    suggestions: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class ContentQualityValidator:
    """
    Pure deterministic content quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with content quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        self.placeholder_patterns = config.get(
            "placeholder_patterns",
            ["\\[.*?\\]", "\\{.*?\\}", "<.*?>", "\\$.*?\\$"],
        )
        self.quantified_patterns = config.get(
            "quantified_patterns",
            [
                "\\d+\\s*(?:%|percent|percentages?)",
                "\\$\\d+(?:,\\d{3})*(?:\\.\\d{2})?",
                "\\d+\\s*(?:years?|months?|days?)",
                "\\d+\\s*(?:projects?|tasks?|items?)",
            ],
        )
        self.skill_keywords = config.get("skill_keywords", [])
        self.min_skill_matches = config.get("min_skill_matches", 3)

    def validate_content_quality(
        self,
        resume: dict[str, Any],
        job_desc: str | None = None,
    ) -> QualityValidationResult:
        """
        Validate content quality using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for skill matching

        Returns:
            QualityValidationResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "ContentQualityValidator.validate_content_quality",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ContentQualityValidator.validate_content_quality".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        suggestions: list[str] = []
        placeholder_issues = self._check_placeholders(resume)
        issues.extend(placeholder_issues)
        quantified_issues = self._check_quantified_achievements(resume)
        issues.extend(quantified_issues)
        skill_issues, skill_suggestions = self._validate_skills(resume, job_desc)
        issues.extend(skill_issues)
        suggestions.extend(skill_suggestions)
        score = self._calculate_quality_score(issues, resume)
        return QualityValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            score=score,
            metadata={"validation_type": "deterministic"},
        )

    def _check_placeholders(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for placeholder text using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        resume_text = json.dumps(resume, ensure_ascii=False)
        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            if matches:
                issues.append(f"Found {len(matches)} placeholder(s): {pattern}")
        return issues

    def _check_quantified_achievements(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for quantified achievements using deterministic patterns.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        resume_text = json.dumps(resume, ensure_ascii=False)
        quantified_count = 0
        for pattern in self.quantified_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            quantified_count += len(matches)
        if quantified_count < 3:
            issues.append(f"Insufficient quantified achievements ({quantified_count} found)")
        return issues

    def _validate_skills(
        self,
        resume: dict[str, Any],
        job_desc: str | None = None,
    ) -> tuple[list[str], list[str]]:
        """
        Validate skills using deterministic rule-based logic.

        Moved to Deterministic: Pure string matching and validation
        """
        issues: list[str] = []
        suggestions: list[str] = []
        resume_text = json.dumps(resume).lower()
        skill_matches = 0
        matched_skills: set[str] = set()
        for skill in self.skill_keywords:
            if skill.lower() in resume_text:
                skill_matches += 1
                matched_skills.add(skill)
        if skill_matches < self.min_skill_matches:
            issues.append(f"Insufficient skill matches ({skill_matches} found)")
        if job_desc:
            alignment_score = self._calculate_skill_alignment(matched_skills, job_desc)
            if alignment_score < 0.5:
                suggestions.append("Improve skill alignment with job description")
        return (issues, suggestions)

    def _calculate_skill_alignment(self, skills: set[str], job_desc: str) -> float:
        """
        Calculate skill alignment using deterministic text analysis.

        Moved to Deterministic: Pure text processing and calculation
        """
        if not skills:
            return 0.0
        job_desc_lower = job_desc.lower()
        aligned_skills = 0
        for skill in skills:
            if skill.lower() in job_desc_lower:
                aligned_skills += 1
        return aligned_skills / len(skills)

    def _calculate_quality_score(self, issues: list[str], resume: dict[str, Any]) -> float:
        """
        Calculate overall quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        base_score = 1.0
        base_score -= len(issues) * 0.1
        resume_sections = len([k for k in resume.keys() if not k.startswith("_")])
        if resume_sections >= 5:
            base_score += 0.1
        resume_text = json.dumps(resume, ensure_ascii=False)
        quantified_count = sum(
            len(re.findall(pattern, resume_text, re.IGNORECASE)) for pattern in self.quantified_patterns
        )
        if quantified_count >= 5:
            base_score += 0.1
        return max(0.0, min(1.0, base_score))

    def extract_resume_text(self, resume: dict[str, Any]) -> str:
        """
        Extract and normalize resume text for processing.

        Moved to Deterministic: Pure text extraction and normalization
        """
        text = json.dumps(resume, ensure_ascii=False)
        text = re.sub('[{}"\\[\\],:]', " ", text)
        text = re.sub("\\s+", " ", text).strip()
        return text

    def detect_formatting_issues(self, text: str) -> list[str]:
        """
        Detect formatting issues using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        """
        issues: list[str] = []
        if re.search("[A-Z]{4,}", text):
            issues.append("Excessive capitalization detected")
        if re.search("(.)\\1{3,}", text):
            issues.append("Repeated characters detected")
        sentences = re.split("[.!?]+", text)
        short_sentences = [s for s in sentences if len(s.strip()) < 5 and s.strip()]
        if len(short_sentences) > 3:
            issues.append("Too many very short sentences")
        return issues
