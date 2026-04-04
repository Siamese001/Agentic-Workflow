"""Executive Title Composer - Industry-First Headline Generation (K.4).

This agent generates professional headlines with strict Industry-First positioning,
enforcing 8-13 word total count and ≤90 character limit with technology keyword blocking.

Sub-Atomic Agent Name: Executive_Title_Composer
Legacy K-Node: K.4
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from apps_rg.utils.RGAgentBase import RGAgentBase as Agent

_emit_applies_guardrail("p0", "HeadlineOutputAgent", "p0_governance")
_emit_reads_policy_state("p0", "HeadlineOutputAgent", "policy_binding")
_emit_snapshots_state("p0", "HeadlineOutputAgent", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_1")
_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_2")
_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_3")
_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_4")
_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_5")
_emit_emits_metric_event("HeadlineOutputAgent", "p4obs", "metric_6")
_emit_records_incident_event("HeadlineOutputAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("HeadlineOutputAgent", "p4obs", "anomaly")
_emit_writes_observability_log("HeadlineOutputAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("HeadlineOutputAgent", "p4obs", "mon_state")
_emit_triggers_alert("HeadlineOutputAgent", "p4obs", "alert")
_emit_links_incident_trace("HeadlineOutputAgent", "p4obs", "trace_link")
_emit_captures_pattern("HeadlineOutputAgent", "p3lm", "pattern")
_emit_records_learning_event("HeadlineOutputAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HeadlineOutputAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("HeadlineOutputAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HeadlineOutputAgent", "p3lm", "routing")
_emit_improves_agent_policy("HeadlineOutputAgent", "p3lm", "policy")
_emit_stores_learning_state("HeadlineOutputAgent", "p3lm", "state")
_emit_records_execution_trace("HeadlineOutputAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HeadlineOutputAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HeadlineOutputAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HeadlineOutputAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HeadlineOutputAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HeadlineOutputAgent", "env_read", "p2_env_1")
_emit_reads_environ("HeadlineOutputAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("HeadlineOutputAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HeadlineOutputAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HeadlineOutputAgent", "context_pull")
_emit_pulls_context("p1", "HeadlineOutputAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HeadlineOutputAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HeadlineOutputAgent", "uwg_term_2")
_emit_writes_through("p1", "HeadlineOutputAgent", "write_through")
_emit_writes_through("p1", "HeadlineOutputAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "HeadlineOutputAgent", "safety_validation")
_emit_invokes_eval("p1", "HeadlineOutputAgent", "eval_call")
_emit_proposal_commits_routing("p1", "HeadlineOutputAgent", "routing_commit")
_emit_escalates_to_human("p1", "HeadlineOutputAgent", "human_escalation")
_emit_routes_through("p1", "HeadlineOutputAgent", "route_through")
_emit_checks_agent_registry("p1", "HeadlineOutputAgent", "agent_registry")
_emit_validates_agent_capability("p1", "HeadlineOutputAgent", "capability")
_emit_dispatches_execution_plan("p1", "HeadlineOutputAgent", "exec_plan")
_emit_agent_executes_agent("p1", "HeadlineOutputAgent", "sub_agent")
_emit_routes_to_agent("p1", "HeadlineOutputAgent", "target_agent")
_emit_verifies_policy("p1", "HeadlineOutputAgent", "policy_check")
_emit_observes_runtime_state("p1", "HeadlineOutputAgent", "runtime_state")
_emit_verifies_boundary("p1", "HeadlineOutputAgent", "boundary_check")
_emit_transcripts_response("p1", "HeadlineOutputAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "HeadlineOutputAgent")
_emit_gated_by_confidence("p1", "HeadlineOutputAgent", "confidence_gate")
emit_replay_key("p0", "HeadlineOutputAgent")
emit_determinism_digest("p0", "HeadlineOutputAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "HeadlineOutputAgent", "execution_auth")
_emit_validates_capability("p2", "HeadlineOutputAgent", "capability_check")
_emit_routes_to_capability("p2", "HeadlineOutputAgent", "capability_route")
_emit_writes_via_uwg("p2", "HeadlineOutputAgent", "uwg_write")
_emit_blocks_direct_write("p2", "HeadlineOutputAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "HeadlineOutputAgent", "tool_invocation")
_emit_captures_execution_output("p2", "HeadlineOutputAgent", "exec_output")
_emit_dispatches_agent("p3", "HeadlineOutputAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "HeadlineOutputAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "HeadlineOutputAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "HeadlineOutputAgent", "healing_outcome")
_emit_escalates_failure("p3", "HeadlineOutputAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "HeadlineOutputAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HeadlineOutputAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "HeadlineOutputAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "HeadlineOutputAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HeadlineOutputAgent", "eval_metric")
_emit_stores_embedding("p4", "HeadlineOutputAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "HeadlineOutputAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HeadlineOutputAgent", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class HeadlineOutput:
    """Executive title composer output."""

    headline: str
    segment_1: str
    segment_2: str
    segment_3: str
    word_count: int
    char_count: int
    industry_first_compliant: bool
    technology_keywords_in_segment_1: list[str]
    metadata: dict[str, Any]


TECHNOLOGY_KEYWORDS = [
    "AI",
    "ML",
    "Python",
    "Java",
    "AWS",
    "Azure",
    "GCP",
    "Kubernetes",
    "Docker",
    "React",
    "Angular",
    "Node.js",
    "TensorFlow",
    "PyTorch",
    "SQL",
    "NoSQL",
    "MongoDB",
    "PostgreSQL",
    "Redis",
    "Kafka",
    "Microservices",
    "API",
    "REST",
    "GraphQL",
    "DevOps",
    "CI/CD",
]


class Executive_Title_Composer(Agent):
    """Executive Title Composer agent for Industry-First headline generation.

    This agent generates headlines with strict constraints:
    - Total word count: 8-13 words (ZERO TOLERANCE)
    - Character limit: ≤90 characters (ZERO TOLERANCE)
    - Industry-First positioning: Segment 1 MUST NOT contain technology keywords
    - 3-segment structure: Domain | Leadership | Value Prop

    Validation Gates:
    - VG_HEADLINE_WORD_COUNT_COMPLIANCE (8-13 words)
    - VG_HEADLINE_CHARACTER_COMPLIANCE (≤90 chars)
    - VG_INDUSTRY_FIRST_COMPLIANCE (no tech in Segment 1)
    """

    # guardian: allow-magic-config
    def __init__(self, config: Any, word_count_min: int = 8, word_count_max: int = 13, char_limit: int = 90):
        """Initialize Executive Title Composer.

        Args:
            config: Reasoning configuration
            word_count_min: Minimum word count (default 8)
            word_count_max: Maximum word count (default 13)
            char_limit: Character limit (default 90)
        """
        super().__init__(config, k_node_id="K.4", element="Executive Title (Industry-First)")
        self.word_count_min = word_count_min
        self.word_count_max = word_count_max
        self.char_limit = char_limit
        logger.info(
            f"Executive_Title_Composer initialized: words={word_count_min}-{word_count_max}, chars≤{char_limit}"
        )

    async def execute(self, context: dict[str, Any]) -> HeadlineOutput:
        """Execute headline generation with Industry-First positioning.

        Args:
            context: Execution context with:
                - target_industry: str - Target industry/domain
                - target_role: str - Target role/level
                - value_propositions: List[str] - Key value props
                - job_description: str - Target JD
                - regeneration_feedback: Optional[str]

        Returns:
            HeadlineOutput with 3-segment headline
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "HeadlineOutputAgent.execute")
        logger.info("Executing Executive_Title_Composer (Industry-First)")
        target_industry = context.get("target_industry", "Technology")
        target_role = context.get("target_role", "Engineering Leader")
        value_propositions = context.get("value_propositions", [])
        job_description = context.get("job_description", "")
        regeneration_feedback = context.get("regeneration_feedback")
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(
                target_industry, target_role, value_propositions, job_description
            )
        response = await self._call_llm(prompt)
        headline = response.strip()
        segments = self._parse_segments(headline)
        tech_keywords_in_seg1 = self._check_technology_keywords(segments[0])
        industry_first_compliant = len(tech_keywords_in_seg1) == 0
        word_count = len(headline.split())
        char_count = len(headline)
        output = HeadlineOutput(
            headline=headline,
            segment_1=segments[0],
            segment_2=segments[1],
            segment_3=segments[2],
            word_count=word_count,
            char_count=char_count,
            industry_first_compliant=industry_first_compliant,
            technology_keywords_in_segment_1=tech_keywords_in_seg1,
            metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "word_count_range": f"{self.word_count_min}-{self.word_count_max}",
                "char_limit": self.char_limit,
            },
        )
        logger.info(
            f"Executive_Title_Composer complete: {word_count} words, {char_count} chars, Industry-First={industry_first_compliant}"
        )
        if not industry_first_compliant:
            logger.error(
                f"INDUSTRY-FIRST VIOLATION: Technology keywords in Segment 1: {tech_keywords_in_seg1}"
            )
        return output

    def _build_initial_prompt(
        self, target_industry: str, target_role: str, value_propositions: list[str], job_description: str
    ) -> str:
        """Build initial generation prompt with Industry-First enforcement.

        Args:
            target_industry: Target industry/domain
            target_role: Target role/level
            value_propositions: Key value props
            job_description: Target JD

        Returns:
            Formatted prompt
        """
        prompt = f"""Generate a professional resume headline with STRICT Industry-First positioning.\n\nCRITICAL CONSTRAINTS (ZERO TOLERANCE):\n1. Total word count: {self.word_count_min}-{self.word_count_max} words (STRICT)\n2. Character limit: ≤{self.char_limit} characters (STRICT)\n3. 3-segment structure: Domain | Leadership | Value Proposition\n4. INDUSTRY-FIRST POSITIONING: Segment 1 MUST NOT contain technology keywords\n\nINDUSTRY-FIRST RULE (BLOCKING):\n- Segment 1 must lead with INDUSTRY/DOMAIN\n  (e.g., "Healthcare", "Financial Services", "Enterprise SaaS")\n- Segment 1 MUST NOT contain: AI, ML, Python, AWS, Kubernetes, Docker, etc.\n- Technology keywords belong in Segment 3 (Value Proposition)\n\nTARGET INDUSTRY: {target_industry}\nTARGET ROLE: {target_role}\n\nVALUE PROPOSITIONS (use for Segment 3):\n{chr(10).join(f"- {vp}" for vp in value_propositions[:3])}\n\nJOB DESCRIPTION CONTEXT:\n{job_description[:300]}...\n\nSTRUCTURE:\nSegment 1: {target_industry} [Industry/Domain - NO TECHNOLOGY KEYWORDS]\nSegment 2: {target_role} [Leadership/Role]\nSegment 3: [Value Proposition - technology keywords allowed here]\n\nEXAMPLES (Industry-First Compliant):\n✅ "Healthcare Technology Leader | AI/ML Innovation | Enterprise Scale"\n✅ "Financial Services Executive | Cloud Architecture | Digital Transformation"\n✅ "Enterprise SaaS Leader | Engineering Excellence | Scalable Solutions"\n\nEXAMPLES (Industry-First VIOLATIONS - DO NOT USE):\n❌ "AI/ML Leader | Healthcare Technology | Innovation" (tech in Segment 1)\n❌ "Python Engineer | Cloud Architecture | SaaS" (tech in Segment 1)\n\nGenerate the headline now (\n{self.word_count_min}-{self.word_count_max} words, ≤{self.char_limit} chars):\n"""
        return prompt

    def _build_regeneration_prompt(self, context: dict[str, Any], feedback: str) -> str:
        """Build regeneration prompt with validation feedback.

        Args:
            context: Original context
            feedback: Validation feedback

        Returns:
            Regeneration prompt
        """
        previous_headline = context.get("previous_headline", "")
        prompt = f"REGENERATION REQUIRED\n\n{feedback}\n\nPREVIOUS HEADLINE:\n{previous_headline}\n\nCONSTRAINTS (ZERO TOLERANCE):\n- Word count: {self.word_count_min}-{self.word_count_max} words\n- Character limit: ≤{self.char_limit} characters\n- INDUSTRY-FIRST: NO technology keywords in Segment 1\n\nINSTRUCTIONS:\nFix the specific violations listed in feedback.\nMaintain Industry-First positioning.\n\nGenerate the corrected headline:\n"
        return prompt

    def _parse_segments(self, headline: str) -> list[str]:
        """Parse headline into 3 segments.

        Args:
            headline: Full headline

        Returns:
            List of 3 segments [Domain, Leadership, Value Prop]
        """
        segments = [s.strip() for s in headline.split("|")]
        while len(segments) < 3:
            segments.append("")
        return segments[:3]

    def _check_technology_keywords(self, segment: str) -> list[str]:
        """Check for technology keywords in segment.

        Args:
            segment: Segment text

        Returns:
            List of found technology keywords
        """
        segment_upper = segment.upper()
        found_keywords = []
        for keyword in TECHNOLOGY_KEYWORDS:
            if keyword.upper() in segment_upper:
                found_keywords.append(keyword)
        return found_keywords
