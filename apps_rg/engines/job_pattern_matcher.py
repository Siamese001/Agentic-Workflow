"""
Job Pattern Matcher - JD pattern recognition
Refactored from match_job_patterns.py
"""

from __future__ import annotations

import logging
import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "job_pattern_matcher", "execution_auth")
_emit_validates_capability("p2", "job_pattern_matcher", "capability_check")
_emit_routes_to_capability("p2", "job_pattern_matcher", "capability_route")
_emit_writes_via_uwg("p2", "job_pattern_matcher", "uwg_write")
_emit_blocks_direct_write("p2", "job_pattern_matcher", "direct_write_block")
_emit_records_tool_invocation("p2", "job_pattern_matcher", "tool_invocation")
_emit_captures_execution_output("p2", "job_pattern_matcher", "exec_output")
_emit_dispatches_agent("p3", "job_pattern_matcher", "agent_dispatch")
_emit_coordinates_agents("p3", "job_pattern_matcher", "agent_coordination")
_emit_records_workflow_lineage("p3", "job_pattern_matcher", "workflow_lineage")
_emit_records_healing_outcome("p3", "job_pattern_matcher", "healing_outcome")
_emit_escalates_failure("p3", "job_pattern_matcher", "failure_escalation")
_emit_orchestrates_workflow("p3", "job_pattern_matcher", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "job_pattern_matcher", "healing_dispatch")
_emit_invokes_evaluation("p3", "job_pattern_matcher", "evaluation_signal")
_emit_records_telemetry_event("p4", "job_pattern_matcher", "telemetry_event")
_emit_captures_evaluation_metric("p4", "job_pattern_matcher", "eval_metric")
_emit_stores_embedding("p4", "job_pattern_matcher", "embedding_store")
_emit_updates_meta_learning_state("p4", "job_pattern_matcher", "meta_learning")
_emit_links_execution_to_snapshot("p4", "job_pattern_matcher", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "job_pattern_matcher", "p0_governance")
_emit_reads_policy_state("p0", "job_pattern_matcher", "policy_binding")
_emit_snapshots_state("p0", "job_pattern_matcher", "state_snapshot")
emit_replay_key("p0", "job_pattern_matcher")
emit_determinism_digest("p0", "job_pattern_matcher")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class JobPatternMatcher(BaseRGEngine):
    """
    Pattern recognition for job descriptions.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.PATTERN_MATCHER")

    async def execute(self, job_description: str) -> dict[str, Any]:
        """
        Extract patterns from job description.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "JobPatternMatcher.execute")

        self._mcp_audit("pattern_matching_start")
        patterns = {
            "technical_skills": self._extract_technical_skills(job_description),
            "soft_skills": self._extract_soft_skills(job_description),
            "experience_level": self._extract_experience_level(job_description),
            "certifications": self._extract_certifications(job_description),
        }
        self.record_pass("Pattern matching complete", data=patterns)
        return patterns

    def _extract_technical_skills(self, text: str) -> list[str]:
        """Extract technical skill mentions."""
        tech_patterns = [
            "\\b(Python|Java|JavaScript|C\\+\\+|Go|Rust)\\b",
            "\\b(AWS|Azure|GCP|Docker|Kubernetes)\\b",
            "\\b(SQL|NoSQL|PostgreSQL|MongoDB)\\b",
        ]
        skills = []
        for pattern in tech_patterns:
            skills.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(skills))

    def _extract_soft_skills(self, text: str) -> list[str]:
        """Extract soft skill mentions."""
        soft_keywords = ["leadership", "communication", "collaboration", "problem-solving"]
        return [kw for kw in soft_keywords if kw in text.lower()]

    def _extract_experience_level(self, text: str) -> str:
        """Determine required experience level."""
        if re.search("\\b(\\d+)\\+?\\s*years?\\b", text):
            match = re.search("\\b(\\d+)\\+?\\s*years?\\b", text)
            years = int(match.group(1))
            if years >= 10:
                return "senior"
            elif years >= 5:
                return "mid"
            else:
                return "junior"
        return "unknown"

    def _extract_certifications(self, text: str) -> list[str]:
        """Extract certification mentions."""
        cert_patterns = ["\\b(AWS Certified|Azure Certified|PMP|CISSP)\\b"]
        certs = []
        for pattern in cert_patterns:
            certs.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(certs))
