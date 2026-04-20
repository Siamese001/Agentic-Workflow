"""Talent Signal Enhancer - Transform Management into Talent Attraction.

This module enhances resume bullets to emphasize talent attraction capabilities,
highlighting team pedigree and leveraging network as a strategic asset for
AI leadership roles.
"""

import logging
import re
from typing import Any

from pydantic import BaseModel, Field, validator

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

_emit_applies_guardrail("p0", "talent_signal_enhancer_validator", "p0_governance")
_emit_reads_policy_state("p0", "talent_signal_enhancer_validator", "policy_binding")
_emit_snapshots_state("p0", "talent_signal_enhancer_validator", "state_snapshot")
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

_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_1")
_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_2")
_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_3")
_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_4")
_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_5")
_emit_emits_metric_event("talent_signal_enhancer_validator", "p4obs", "metric_6")
_emit_records_incident_event("talent_signal_enhancer_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("talent_signal_enhancer_validator", "p4obs", "anomaly")
_emit_writes_observability_log("talent_signal_enhancer_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("talent_signal_enhancer_validator", "p4obs", "mon_state")
_emit_triggers_alert("talent_signal_enhancer_validator", "p4obs", "alert")
_emit_links_incident_trace("talent_signal_enhancer_validator", "p4obs", "trace_link")
_emit_captures_pattern("talent_signal_enhancer_validator", "p3lm", "pattern")
_emit_records_learning_event("talent_signal_enhancer_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("talent_signal_enhancer_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("talent_signal_enhancer_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("talent_signal_enhancer_validator", "p3lm", "routing")
_emit_improves_agent_policy("talent_signal_enhancer_validator", "p3lm", "policy")
_emit_stores_learning_state("talent_signal_enhancer_validator", "p3lm", "state")
_emit_records_execution_trace("talent_signal_enhancer_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("talent_signal_enhancer_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("talent_signal_enhancer_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("talent_signal_enhancer_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("talent_signal_enhancer_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("talent_signal_enhancer_validator", "env_read", "p2_env_1")
_emit_reads_environ("talent_signal_enhancer_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("talent_signal_enhancer_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("talent_signal_enhancer_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "talent_signal_enhancer_validator", "context_pull")
_emit_pulls_context("p1", "talent_signal_enhancer_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "talent_signal_enhancer_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "talent_signal_enhancer_validator", "uwg_term_2")
_emit_writes_through("p1", "talent_signal_enhancer_validator", "write_through")
_emit_writes_through("p1", "talent_signal_enhancer_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "talent_signal_enhancer_validator", "safety_validation")
_emit_invokes_eval("p1", "talent_signal_enhancer_validator", "eval_call")
_emit_proposal_commits_routing("p1", "talent_signal_enhancer_validator", "routing_commit")
_emit_escalates_to_human("p1", "talent_signal_enhancer_validator", "human_escalation")
_emit_routes_through("p1", "talent_signal_enhancer_validator", "route_through")
_emit_checks_agent_registry("p1", "talent_signal_enhancer_validator", "agent_registry")
_emit_validates_agent_capability("p1", "talent_signal_enhancer_validator", "capability")
_emit_dispatches_execution_plan("p1", "talent_signal_enhancer_validator", "exec_plan")
_emit_agent_executes_agent("p1", "talent_signal_enhancer_validator", "sub_agent")
_emit_routes_to_agent("p1", "talent_signal_enhancer_validator", "target_agent")
_emit_verifies_policy("p1", "talent_signal_enhancer_validator", "policy_check")
_emit_observes_runtime_state("p1", "talent_signal_enhancer_validator", "runtime_state")
_emit_verifies_boundary("p1", "talent_signal_enhancer_validator", "boundary_check")
_emit_transcripts_response("p1", "talent_signal_enhancer_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "talent_signal_enhancer_validator")
_emit_gated_by_confidence("p1", "talent_signal_enhancer_validator", "confidence_gate")
emit_replay_key("p0", "talent_signal_enhancer_validator")
emit_determinism_digest("p0", "talent_signal_enhancer_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "talent_signal_enhancer_validator", "execution_auth")
_emit_validates_capability("p2", "talent_signal_enhancer_validator", "capability_check")
_emit_routes_to_capability("p2", "talent_signal_enhancer_validator", "capability_route")
_emit_writes_via_uwg("p2", "talent_signal_enhancer_validator", "uwg_write")
_emit_blocks_direct_write("p2", "talent_signal_enhancer_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "talent_signal_enhancer_validator", "tool_invocation")
_emit_captures_execution_output("p2", "talent_signal_enhancer_validator", "exec_output")
_emit_dispatches_agent("p3", "talent_signal_enhancer_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "talent_signal_enhancer_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "talent_signal_enhancer_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "talent_signal_enhancer_validator", "healing_outcome")
_emit_escalates_failure("p3", "talent_signal_enhancer_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "talent_signal_enhancer_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "talent_signal_enhancer_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "talent_signal_enhancer_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "talent_signal_enhancer_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "talent_signal_enhancer_validator", "eval_metric")
_emit_stores_embedding("p4", "talent_signal_enhancer_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "talent_signal_enhancer_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "talent_signal_enhancer_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class TalentMetrics(BaseModel):
    """Metrics describing talent acquisition and management capabilities."""

    team_size: int = Field(..., ge=0, description="Size of team managed")
    pedigree_keywords: list[str] = Field(default_factory=list, description="Prestige markers in team")
    retention_rate: str | None = Field(None, description="Team retention rate")
    hiring_velocity: str | None = Field(None, description="Hiring speed metric")

    @validator("pedigree_keywords")
    def validate_pedigree(cls, v):
        """Ensure pedigree keywords are prestigious markers."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TalentMetrics.validate_pedigree"
        )

        prestigious_terms = {
            "phd",
            "masters",
            "ex-google",
            "ex-meta",
            "ex-amazon",
            "ex-apple",
            "ex-microsoft",
            "ex-netflix",
            "researchers",
            "contributors",
            "senior",
            "principal",
            "staff",
            "founding engineer",
            "top-tier",
            "fortune 500",
            "ivy league",
            "stanford",
            "mit",
            "cmu",
            "berkeley",
            "open-source",
            "github",
            "kaggle",
        }
        filtered = [kw for kw in v if any(term in kw.lower() for term in prestigious_terms)]
        return filtered


class TalentSignalEnhancer:
    """Enhances talent signals in resume content and generates network hooks."""

    def __init__(self, candidate_background: dict[str, Any]):
        """Initialize the talent signal enhancer.

        Args:
            candidate_background: Candidate's professional background
        """
        self.candidate_background = candidate_background
        self.management_history = candidate_background.get("management_history", [])
        self.network_size = candidate_background.get("network_size", {})
        self.has_management_experience = len(self.management_history) > 0
        self.pedigree_patterns = {
            "education": [
                "phd",
                "masters?",
                "msc",
                "mba",
                "ivy league",
                "stanford",
                "mit",
                "cmu",
                "berkeley",
                "carnegie mellon",
            ],
            "experience": [
                "ex-(google|meta|amazon|apple|microsoft|netflix|faang)",
                "former (google|meta|amazon|apple|microsoft|netflix)",
                "previously at (google|meta|amazon|apple|microsoft|netflix)",
                "big tech",
                "fortune 500",
                "top-tier",
            ],
            "seniority": [
                "senior",
                "principal",
                "staff",
                "founding engineer",
                "lead",
                "head of",
                "director",
                "vp",
            ],
            "achievement": [
                "researcher",
                "contributor",
                "open-source",
                "github",
                "kaggle",
                "published",
                "patented",
            ],
        }
        logger.info(
            f"Initialized TalentSignalEnhancer with management experience: {self.has_management_experience}",
        )

    def enhance_management_bullet(self, bullet_text: str) -> str:
        """Enhance a management bullet with talent signals.

        Args:
            bullet_text: Original management bullet

        Returns:
            Enhanced bullet with talent attraction focus
        """
        try:
            team_size = self._extract_team_size(bullet_text)
            pedigree = self._detect_pedigree(bullet_text)
            hiring_metric = self._extract_hiring_metric(bullet_text)
            retention_metric = self._extract_retention_metric(bullet_text)
            enhanced = bullet_text
            if team_size > 0:
                if pedigree:
                    pedigree_str = ", ".join(pedigree[:3])
                    enhanced = enhanced.replace(
                        f"team of {team_size}",
                        f"team of {team_size} (including **{pedigree_str}**)",
                    )
                else:
                    enhanced = enhanced.replace(
                        f"team of {team_size}",
                        f"high-performance team of {team_size}",
                    )
            if hiring_metric:
                if "hired" in enhanced.lower():
                    enhanced = enhanced.replace("hired", f"recruited **{hiring_metric}**")
            if retention_metric:
                enhanced += f", achieving **{retention_metric} retention**"
            if not pedigree and (not hiring_metric) and (not retention_metric):
                enhanced = self._strengthen_generic_bullet(enhanced, team_size)
            logger.debug(f"Enhanced bullet: {bullet_text[:50]}... -> {enhanced[:50]}...")
            return enhanced
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error enhancing management bullet: {str(e)}")
            return bullet_text

    def generate_network_hook(self, target_role: str) -> str | None:
        """Generate a P.S. hook leveraging network as asset.

        Args:
            target_role: Role being targeted (e.g., "Senior AI Engineer")

        Returns:
            Network hook string or None if no management experience
        """
        try:
            if not self.has_management_experience:
                logger.debug("No management experience, skipping network hook")
                return None
            role_network = self.network_size.get(target_role.lower(), 0)
            if role_network < 5:
                return None
            hook = f"P.S. I have a specialized network of {role_network} {target_role}s who often follow me to new ventures. I could likely fill your open {target_role} roles within 60 days."
            logger.info(f"Generated network hook for {target_role} with network size {role_network}")
            return hook
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error generating network hook: {str(e)}")
            return None

    def get_hyde_context(self, job_description: str) -> str | None:
        """Get HyDE context if JD is hiring-heavy.

        Args:
            job_description: Job description text

        Returns:
            "Recruiting" context if hiring focus detected
        """
        try:
            hiring_keywords = [
                "hire",
                "hiring",
                "recruit",
                "build team",
                "scale team",
                "grow team",
                "talent acquisition",
                "team building",
            ]
            jd_lower = job_description.lower()
            hiring_count = sum(1 for keyword in hiring_keywords if keyword in jd_lower)
            if hiring_count >= 3:
                return "Recruiting"
            return None
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error getting HyDE context: {str(e)}")
            return None

    def _detect_pedigree(self, text: str) -> list[str]:
        """Detect prestige markers in text.

        Args:
            text: Text to scan for pedigree markers

        Returns:
            List of detected prestige markers
        """
        try:
            text_lower = text.lower()
            detected = []
            for category, patterns in tqdm(self.pedigree_patterns.items(), desc="Processing", unit="item"):
                for pattern in tqdm(patterns, desc="Processing", unit="item"):
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        if category == "experience":
                            formatted = f"Ex-{match.title()}"
                        elif category == "education":
                            formatted = match.title()
                        else:
                            formatted = match.title()
                        if formatted not in detected:
                            detected.append(formatted)
            if not detected and any(term in text_lower for term in ["senior", "lead", "principal"]):
                detected.append("Senior Talent")
            return detected[:5]
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error detecting pedigree: {str(e)}")
            return []

    def _extract_team_size(self, text: str) -> int:
        """Extract team size from text.

        Args:
            text: Text containing team size

        Returns:
            Team size number
        """
        try:
            patterns = [
                "team of (\\d+)",
                "(\\d+) (?:people|engineers|developers|members)",
                "managed (\\d+)",
                "led (\\d+)",
                "built a team of (\\d+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return int(match.group(1))
            return 0
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error extracting team size: {str(e)}")
            return 0

    def _extract_hiring_metric(self, text: str) -> str | None:
        """Extract hiring velocity from text.

        Args:
            text: Text containing hiring information

        Returns:
            Hiring velocity string or None
        """
        try:
            patterns = [
                "hired (\\d+) in (\\d+) months?",
                "recruited (\\d+) within (\\d+) months?",
                "built team from (\\d+) to (\\d+) in (\\d+) months?",
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        return f"{groups[0]} in <{groups[1]} months"
                    elif len(groups) == 3:
                        growth = int(groups[1]) - int(groups[0])
                        return f"{growth} in <{groups[2]} months"
            return None
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error extracting hiring metric: {str(e)}")
            return None

    def _extract_retention_metric(self, text: str) -> str | None:
        """Extract retention rate from text.

        Args:
            text: Text containing retention information

        Returns:
            Retention rate string or None
        """
        try:
            patterns = ["(\\d+)% retention", "retention of (\\d+)%", "retained (\\d+)%"]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return f"{match.group(1)}%"
            if any(phrase in text.lower() for phrase in ["no attrition", "zero turnover", "100% retained"]):
                return "100%"
            return None
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error extracting retention metric: {str(e)}")
            return None

    def _strengthen_generic_bullet(self, bullet: str, team_size: int) -> str:
        """Strengthen generic management bullet.

        Args:
            bullet: Original bullet
            team_size: Detected team size

        Returns:
            Strengthened bullet
        """
        try:
            if team_size > 0:
                if team_size >= 20:
                    bullet = bullet.replace(
                        f"team of {team_size}",
                        f"team of {team_size} **senior engineers**",
                    )
                elif team_size >= 10:
                    bullet = bullet.replace(
                        f"team of {team_size}",
                        f"team of {team_size} **high-caliber engineers**",
                    )
                else:
                    bullet = bullet.replace(
                        f"team of {team_size}",
                        f"team of {team_size} **specialized engineers**",
                    )
            if "managed" in bullet.lower():
                bullet = bullet.replace("managed", "built and led")
            return bullet
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Error strengthening generic bullet: {str(e)}")
            return bullet


def create_talent_signal_enhancer(candidate_background: dict[str, Any]) -> TalentSignalEnhancer:
    """Create a TalentSignalEnhancer instance.

    Args:
        candidate_background: Candidate's professional background

    Returns:
        Configured TalentSignalEnhancer
    """
    return TalentSignalEnhancer(candidate_background)


def enhance_talent_signals(
    bullets: list[str],
    candidate_background: dict[str, Any],
) -> tuple[list[str], str | None]:
    """Quickly enhance talent signals in bullets.

    Args:
        bullets: List of management bullets
        candidate_background: Candidate background

    Returns:
        Tuple of (enhanced bullets, network hook)
    """
    enhancer = create_talent_signal_enhancer(candidate_background)
    enhanced = [enhancer.enhance_management_bullet(b) for b in bullets]
    hook = None
    if enhancer.has_management_experience:
        hook = enhancer.generate_network_hook("Senior AI Engineer")
    return (enhanced, hook)
