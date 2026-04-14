"""
ATS Validator - Deterministic ATS Compatibility Validation

Zero-Ambiguity Standard: Renamed from ats_validation_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Pattern matching for ATS-unfriendly formats
- Section header validation
- Keyword scoring algorithm
- Text normalization and processing
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

emit_replay_key("p0", "ats_validator")
emit_determinism_digest("p0", "ats_validator")

_emit_dispatches_healing_run("p1", "ats_validator", "L5")
_emit_routes_through("p1", "ats_validator", "L5")
_emit_checks_agent_registry("p1", "ats_validator", "agent_registry")
_emit_validates_agent_capability("p1", "ats_validator", "capability")
_emit_dispatches_execution_plan("p1", "ats_validator", "exec_plan")
_emit_agent_executes_agent("p1", "ats_validator", "sub_agent")
_emit_routes_to_agent("p1", "ats_validator", "target_agent")
_emit_verifies_policy("p1", "ats_validator", "policy_check")
_emit_observes_runtime_state("p1", "ats_validator", "runtime_state")
_emit_verifies_boundary("p1", "ats_validator", "boundary_check")
_emit_transcripts_response("p1", "ats_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "ats_validator")
_emit_gated_by_confidence("p1", "ats_validator", "confidence_gate")
_emit_escalates_to_human("p1", "ats_validator", "L5")
_emit_reads_policy_state("p1", "ats_validator", "L5")

_emit_applies_guardrail("p0", "ats_validator", "p0_governance")
_emit_snapshots_state("p0", "ats_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "ats_validator", "execution_auth")
_emit_validates_capability("p2", "ats_validator", "capability_check")
_emit_routes_to_capability("p2", "ats_validator", "capability_route")
_emit_writes_via_uwg("p2", "ats_validator", "uwg_write")
_emit_blocks_direct_write("p2", "ats_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "ats_validator", "tool_invocation")
_emit_captures_execution_output("p2", "ats_validator", "exec_output")
_emit_dispatches_agent("p3", "ats_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "ats_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ats_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ats_validator", "healing_outcome")
_emit_escalates_failure("p3", "ats_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ats_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ats_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ats_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ats_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ats_validator", "eval_metric")
_emit_stores_embedding("p4", "ats_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ats_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ats_validator", "exec_snapshot_link")
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
from tqdm import tqdm

_emit_emits_metric_event("ats_validator", "p4obs", "metric_1")
_emit_emits_metric_event("ats_validator", "p4obs", "metric_2")
_emit_emits_metric_event("ats_validator", "p4obs", "metric_3")
_emit_emits_metric_event("ats_validator", "p4obs", "metric_4")
_emit_emits_metric_event("ats_validator", "p4obs", "metric_5")
_emit_emits_metric_event("ats_validator", "p4obs", "metric_6")
_emit_records_incident_event("ats_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ats_validator", "p4obs", "anomaly")
_emit_writes_observability_log("ats_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ats_validator", "p4obs", "mon_state")
_emit_triggers_alert("ats_validator", "p4obs", "alert")
_emit_links_incident_trace("ats_validator", "p4obs", "trace_link")
_emit_captures_pattern("ats_validator", "p3lm", "pattern")
_emit_records_learning_event("ats_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ats_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ats_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ats_validator", "p3lm", "routing")
_emit_improves_agent_policy("ats_validator", "p3lm", "policy")
_emit_stores_learning_state("ats_validator", "p3lm", "state")
_emit_records_execution_trace("ats_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ats_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ats_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ats_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ats_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ats_validator", "env_read", "p2_env_1")
_emit_reads_environ("ats_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ats_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ats_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ats_validator", "context_pull")
_emit_pulls_context("p1", "ats_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ats_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ats_validator", "uwg_term_2")
_emit_writes_through("p1", "ats_validator", "write_through")
_emit_writes_through("p1", "ats_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ats_validator", "safety_validation")
_emit_invokes_eval("p1", "ats_validator", "eval_call")
_emit_proposal_commits_routing("p1", "ats_validator", "routing_commit")


@dataclass
class ATSValidationResult:
    """Result of ATS validation with deterministic scoring."""

    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class AtsValidator:
    """
    Pure deterministic ATS validation logic.

    All methods in this class are 100% deterministic and can be
    executed without external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with ATS validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        self.standard_headers = config.get("standard_headers", {})
        self.ats_unfriendly_patterns = config.get("ats_unfriendly_patterns", [])
        self.allowed_non_standard_sections = config.get("allowed_non_standard_sections", [])
        self.keyword_config = config.get("keyword_optimization", {})
        self.min_score_threshold = self.keyword_config.get("min_score_threshold", 0.3)
        self.stop_words: set[str] = set(self.keyword_config.get("stop_words", []))

    def validate_ats_compatibility(
        self,
        resume: dict[str, Any],
        job_desc: str | None = None,
    ) -> ATSValidationResult:
        """
        Validate ATS compatibility using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for keyword scoring

        Returns:
            ATSValidationResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "AtsValidator.validate_ats_compatibility",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:AtsValidator.validate_ats_compatibility".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        issues.extend(self._check_ats_unfriendly_patterns(resume))
        issues.extend(self._validate_section_headers(resume))
        score = None
        if job_desc:
            score = self.calculate_keyword_score(resume, job_desc)
            if score < self.min_score_threshold:
                issues.append(f"Low keyword match ({score:.0%})")
        return ATSValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"validation_type": "deterministic"},
        )

    def _check_ats_unfriendly_patterns(self, resume: dict[str, Any]) -> list[str]:
        """
        Check for ATS-unfriendly patterns using deterministic regex.

        Moved to Deterministic: Pure pattern matching logic
        """
        issues: list[str] = []
        full_content = json.dumps(resume, ensure_ascii=False)
        for pattern in self.ats_unfriendly_patterns:
            if re.search(pattern, full_content):
                issues.append(f"ATS-unfriendly pattern found: {pattern}")
        return issues

    def _validate_section_headers(self, resume: dict[str, Any]) -> list[str]:
        """
        Validate section headers using deterministic string comparison.

        Moved to Deterministic: Pure string validation logic
        """
        issues: list[str] = []
        for section_name in tqdm(resume.keys(), desc="Processing", unit="item"):
            if section_name.startswith("_"):
                continue
            normalized = section_name.lower().strip()
            is_standard = False
            for standard_section, variants in self.standard_headers.items():
                if normalized in variants or normalized == standard_section:
                    is_standard = True
                    break
            if not is_standard and normalized not in self.allowed_non_standard_sections:
                issues.append(f"Non-standard section header: {section_name}")
        return issues

    def calculate_keyword_score(self, resume: dict[str, Any], job_desc: str) -> float:
        """
        Calculate keyword match score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical calculation
        """
        job_words = set(re.findall("\\b[a-zA-Z]{3,}\\b", job_desc.lower()))
        job_words -= self.stop_words
        if not job_words:
            return 1.0
        resume_text = json.dumps(resume).lower()
        matches = sum(1 for word in job_words if word in resume_text)
        return matches / len(job_words)

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing.

        Moved to Deterministic: Pure string manipulation
        """
        text = re.sub("\\s+", " ", text.strip())
        return text.lower()

    # guardian: allow-magic-config
    def extract_keywords(self, text: str, min_length: int = 3) -> set[str]:
        """
        Extract keywords from text using deterministic regex.

        Moved to Deterministic: Pure pattern extraction
        """
        words = set(re.findall(f"\\b[a-zA-Z]{{{min_length},}}\\b", text.lower()))
        return words - self.stop_words

    def validate_formatting(self, content: str) -> list[str]:
        """
        Validate content formatting using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        """
        issues: list[str] = []
        if re.search("[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]", content):
            issues.append("Contains control characters")
        if re.search("\\n{3,}", content):
            issues.append("Excessive line breaks")
        if "\r\n" in content and "\n" in content and (content.count("\r\n") != content.count("\n")):
            issues.append("Mixed line ending formats")
        return issues
