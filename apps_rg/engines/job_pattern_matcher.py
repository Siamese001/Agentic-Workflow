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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
