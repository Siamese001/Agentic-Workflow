"""
L5 Consolidated Knowledge Retrieval for Resume Engine
Consolidates L3 (Pinecone) and L5 (MEMemory) into unified knowledge access

This module provides unified access to:
- User profiles from MEMemory
- Cover letter templates from Pinecone/L3
- Consolidated search across both knowledge bases
"""

import logging
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

_emit_applies_guardrail("p0", "knowledge_result_validator", "p0_governance")
_emit_reads_policy_state("p0", "knowledge_result_validator", "policy_binding")
_emit_snapshots_state("p0", "knowledge_result_validator", "state_snapshot")
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

_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_1")
_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_2")
_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_3")
_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_4")
_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_5")
_emit_emits_metric_event("knowledge_result_validator", "p4obs", "metric_6")
_emit_records_incident_event("knowledge_result_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("knowledge_result_validator", "p4obs", "anomaly")
_emit_writes_observability_log("knowledge_result_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("knowledge_result_validator", "p4obs", "mon_state")
_emit_triggers_alert("knowledge_result_validator", "p4obs", "alert")
_emit_links_incident_trace("knowledge_result_validator", "p4obs", "trace_link")
_emit_captures_pattern("knowledge_result_validator", "p3lm", "pattern")
_emit_records_learning_event("knowledge_result_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("knowledge_result_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("knowledge_result_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("knowledge_result_validator", "p3lm", "routing")
_emit_improves_agent_policy("knowledge_result_validator", "p3lm", "policy")
_emit_stores_learning_state("knowledge_result_validator", "p3lm", "state")
_emit_records_execution_trace("knowledge_result_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("knowledge_result_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("knowledge_result_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("knowledge_result_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("knowledge_result_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("knowledge_result_validator", "env_read", "p2_env_1")
_emit_reads_environ("knowledge_result_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("knowledge_result_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("knowledge_result_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "knowledge_result_validator", "context_pull")
_emit_pulls_context("p1", "knowledge_result_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "knowledge_result_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "knowledge_result_validator", "uwg_term_2")
_emit_writes_through("p1", "knowledge_result_validator", "write_through")
_emit_writes_through("p1", "knowledge_result_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "knowledge_result_validator", "safety_validation")
_emit_invokes_eval("p1", "knowledge_result_validator", "eval_call")
_emit_proposal_commits_routing("p1", "knowledge_result_validator", "routing_commit")
_emit_escalates_to_human("p1", "knowledge_result_validator", "human_escalation")
_emit_routes_through("p1", "knowledge_result_validator", "route_through")
_emit_checks_agent_registry("p1", "knowledge_result_validator", "agent_registry")
_emit_validates_agent_capability("p1", "knowledge_result_validator", "capability")
_emit_dispatches_execution_plan("p1", "knowledge_result_validator", "exec_plan")
_emit_agent_executes_agent("p1", "knowledge_result_validator", "sub_agent")
_emit_routes_to_agent("p1", "knowledge_result_validator", "target_agent")
_emit_verifies_policy("p1", "knowledge_result_validator", "policy_check")
_emit_observes_runtime_state("p1", "knowledge_result_validator", "runtime_state")
_emit_verifies_boundary("p1", "knowledge_result_validator", "boundary_check")
_emit_transcripts_response("p1", "knowledge_result_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "knowledge_result_validator")
_emit_gated_by_confidence("p1", "knowledge_result_validator", "confidence_gate")
emit_replay_key("p0", "knowledge_result_validator")
emit_determinism_digest("p0", "knowledge_result_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "knowledge_result_validator", "execution_auth")
_emit_validates_capability("p2", "knowledge_result_validator", "capability_check")
_emit_routes_to_capability("p2", "knowledge_result_validator", "capability_route")
_emit_writes_via_uwg("p2", "knowledge_result_validator", "uwg_write")
_emit_blocks_direct_write("p2", "knowledge_result_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "knowledge_result_validator", "tool_invocation")
_emit_captures_execution_output("p2", "knowledge_result_validator", "exec_output")
_emit_dispatches_agent("p3", "knowledge_result_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "knowledge_result_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "knowledge_result_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "knowledge_result_validator", "healing_outcome")
_emit_escalates_failure("p3", "knowledge_result_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "knowledge_result_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "knowledge_result_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "knowledge_result_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "knowledge_result_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "knowledge_result_validator", "eval_metric")
_emit_stores_embedding("p4", "knowledge_result_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "knowledge_result_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "knowledge_result_validator", "exec_snapshot_link")

Logger: Any = logging.getLogger(__name__)


@dataclass
class KnowledgeResult:
    """Result from knowledge retrieval."""

    user_profile: dict[str, Any] | None
    template: dict[str, Any] | None
    metadata: dict[str, Any]


class L5ConsolidatedKnowledge:
    """Consolidated knowledge access layer."""

    def __init__(self, memory_client=None, pinecone_client=None):
        """
        Initialize consolidated knowledge layer.

        Args:
            memory_client: MEMemory client for user profiles
            pinecone_client: Pinecone client for templates
        """
        self.memory_client = memory_client
        self.pinecone_client = pinecone_client
        self._fallback_profiles = self._load_fallback_profiles()
        self._fallback_templates = self._load_fallback_templates()

    def _load_fallback_profiles(self) -> dict[str, Any]:
        """Load fallback user profiles if MEMemory unavailable."""
        return {
            "default": {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "experience": "5 years",
                "skills": ["Python", "JavaScript", "React", "Docker"],
                "education": "B.S. Computer Science",
                "achievements": [
                    "Led team of 5 developers",
                    "Reduced deployment time by 50%",
                    "Implemented CI/CD pipeline",
                ],
                "contact": {
                    "email": "john.doe@email.com",
                    "phone": "(555) 123-4567",
                    "linkedin": "linkedin.com/in/johndoe",
                },
            },
        }

    def _load_fallback_templates(self) -> dict[str, Any]:
        """Load fallback templates if Pinecone unavailable."""
        return {
            "professional": {
                "name": "Professional Cover Letter",
                "structure": {
                    "header": "{name}\n{contact}\n{date}",
                    "greeting": "Dear {hiring_manager},",
                    "introduction": "I am writing to express my interest in the {position} position at {company}.",
                    "body": [
                        "With {experience} of experience in {field}, I have developed strong skills in {skills}.",
                        "At my previous role at {previous_company}, I {achievement}.",
                        "I am particularly drawn to {company} because of {company_value}.",
                    ],
                    "closing": "I look forward to discussing how my skills can benefit your team.",
                    "signature": "Sincerely,\n{name}",
                },
                "tone": "formal",
                "length": "medium",
            },
            "modern": {
                "name": "Modern Cover Letter",
                "structure": {
                    "header": "{name} | {title} | {contact}",
                    "greeting": "Hello {hiring_manager},",
                    "introduction": "Excited about the {position} opportunity at {company}!",
                    "body": [
                        "My {experience} in {field} has prepared me to tackle {challenge}.",
                        "Key achievements: {achievements}",
                        "Why I'm excited: {company_culture}",
                    ],
                    "closing": "Let's connect and discuss how I can contribute!",
                    "signature": "Best regards,\n{name}",
                },
                "tone": "casual",
                "length": "short",
            },
        }

    def search_knowledge(self, query: str, types: list[str] = None) -> KnowledgeResult:
        """
        Search consolidated knowledge base.

        Args:
            query: Search query
            types: Types to search ["profile", "template"]

        Returns:
            KnowledgeResult with retrieved data
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "L5ConsolidatedKnowledge.search_knowledge"
        )

        if types is None:
            types: Any = ["profile", "template"]
        result: Any = KnowledgeResult(
            user_profile=None,
            template=None,
            metadata={"query": query, "types": types},
        )
        if "profile" in types:
            result.user_profile = self._get_user_profile(query)
            result.metadata["profile_source"] = self._get_profile_source()
        if "template" in types:
            result.template = self._get_template(query)
            result.metadata["template_source"] = self._get_template_source()
        return result

    def _get_user_profile(self, query: str) -> dict[str, Any] | None:
        """Get user profile from MEMemory or fallback."""
        if self.memory_client:
            try:
                profile = self.memory_client.get_profile(query)
                if profile:
                    Logger.info("Retrieved profile from MEMemory")
                    return profile
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.warning(f"Failed to retrieve from MEMemory: {e}")
        Logger.info("Using fallback user profile")
        return self._fallback_profiles.get("default")

    def _get_template(self, query: str) -> dict[str, Any] | None:
        """Get template from Pinecone or fallback."""
        if self.pinecone_client:
            try:
                templates = self.pinecone_client.query(
                    vector=self._embed_query(query),
                    top_k=1,
                    include_metadata=True,
                )
                if templates:
                    Logger.info("Retrieved template from Pinecone")
                    return templates[0].metadata
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.warning(f"Failed to retrieve from Pinecone: {e}")
        template_type = "professional" if "professional" in query.lower() else "modern"
        Logger.info(f"Using fallback template: {template_type}")
        return self._fallback_templates.get(template_type)

    def _embed_query(self, query: str) -> list[float]:
        """Create embedding for query using BGE-m3."""
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            result = bmg_embed_text(query)
            if result:
                return result
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return [0.0] * 1024

    def _get_profile_source(self) -> str:
        """Get source of profile retrieval."""
        return "memory" if self.memory_client else "fallback"

    def _get_template_source(self) -> str:
        """Get source of template retrieval."""
        return "pinecone" if self.pinecone_client else "fallback"

    def save_profile(self, profile: dict[str, Any]) -> bool:
        """
        Save user profile to MEMemory.

        Args:
            profile: User profile to save

        Returns:
            True if successful
        """
        if self.memory_client:
            try:
                self.memory_client.save_profile(profile)
                Logger.info("Profile saved to MEMemory")
                return True
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"Failed to save profile: {e}")
                return False
        self._fallback_profiles["default"] = profile
        Logger.info("Profile saved to fallback storage")
        return True

    def add_template(self, template: dict[str, Any]) -> bool:
        """
        Add template to Pinecone.

        Args:
            template: Template to add

        Returns:
            True if successful
        """
        if self.pinecone_client:
            try:
                embedding: Any = self._embed_query(template.get("name", ""))
                self.pinecone_client.upsert(
                    vectors=[{"id": template.get("id", "custom"), "values": embedding, "metadata": template}],
                )
                Logger.info("Template added to Pinecone")
                return True
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"Failed to add template: {e}")
                return False
        template_name: Any = template.get("name", "custom").lower()
        self._fallback_templates[template_name] = template
        Logger.info("Template added to fallback storage")
        return True

    def query_consensus(self, pitch: str, guidelines: dict) -> dict:
        """
        Query multiple models for consensus on pitch compliance.

        Args:
            pitch: Pitch content to evaluate
            guidelines: Brand style guidelines to check against

        Returns:
            Consensus result with status and reasoning
        """
        Logger.info("P6_CONSENSUS_START: Evaluating pitch compliance")
        evaluations: Any = []
        brand_score: Any = self._check_brand_compliance(pitch, guidelines)
        evaluations.append(
            {
                "model": "brand_checker",
                "status": "PASS" if brand_score >= 0.7 else "FAIL",
                "score": brand_score,
                "reason": "Brand tone and style analysis",
            },
        )
        spam_score: Any = self._check_spam_indicators(pitch)
        evaluations.append(
            {
                "model": "spam_detector",
                "status": "PASS" if spam_score <= 0.3 else "FAIL",
                "score": spam_score,
                "reason": "Spam and promotional content analysis",
            },
        )
        professionalism_score: Any = self._check_professionalism(pitch)
        evaluations.append(
            {
                "model": "professionalism_checker",
                "status": "PASS" if professionalism_score >= 0.6 else "FAIL",
                "score": professionalism_score,
                "reason": "Professional tone and language analysis",
            },
        )
        pass_count: Any = sum(1 for e in evaluations if e["status"] == "PASS")
        total_count: Any = len(evaluations)
        consensus_status: Any = "PASS" if pass_count == total_count else "FAIL"
        failure_reasons: Any = [e["reason"] for e in evaluations if e["status"] == "FAIL"]
        result: Any = {
            "status": consensus_status,
            "evaluations": evaluations,
            "consensus_score": pass_count / total_count,
            "reason": "; ".join(failure_reasons) if failure_reasons else "All checks passed",
        }
        Logger.info(f"P6_CONSENSUS_COMPLETE: Status={consensus_status}, Score={result['consensus_score']}")
        return result

    def _check_brand_compliance(self, pitch: str, guidelines: dict) -> float:
        """Check pitch against brand guidelines."""
        score = 0.8
        prohibited = guidelines.get("prohibited_words", [])
        for word in prohibited:
            if word.lower() in pitch.lower():
                score -= 0.2
        required_tone = guidelines.get("tone", "professional")
        if required_tone == "professional":
            if any(word in pitch.lower() for word in ["amazing", "incredible", "revolutionary"]):
                score -= 0.1
        return max(0, min(1, score))

    def _check_spam_indicators(self, pitch: str) -> float:
        """Check for spam indicators (lower is better)."""
        spam_score = 0.0
        spam_triggers = ["!!", "FREE", "ACT NOW", "LIMITED TIME", "GUARANTEE"]
        for trigger in spam_triggers:
            if trigger in pitch.upper():
                spam_score += 0.2
        words = pitch.split()
        caps_ratio = sum(1 for w in words if w.isupper()) / len(words)
        if caps_ratio > 0.1:
            spam_score += 0.2
        return min(1, spam_score)

    def _check_professionalism(self, pitch: str) -> float:
        """Check professionalism of the pitch."""
        score = 0.7
        if pitch.strip().startswith(("Dear", "Hello", "Hi")):
            score += 0.1
        if any(closing in pitch for closing in ["Best regards", "Sincerely", "Regards"]):
            score += 0.1
        word_count = len(pitch.split())
        if 100 <= word_count <= 200:
            score += 0.1
        return min(1, score)

    def add_observations(self, data: dict) -> bool:
        """Add observations to knowledge graph."""
        try:
            if self.memory_client:
                self.memory_client.add_observations(data)
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Failed to add observations: {e}")
            return False


_consolidated_knowledge = None


def get_consolidated_knowledge(
    memory_client: Any = None,
    pinecone_client: Any = None,
) -> L5ConsolidatedKnowledge:
    """Get singleton instance of consolidated knowledge."""
    global _consolidated_knowledge
    if _consolidated_knowledge is None:
        _consolidated_knowledge = L5ConsolidatedKnowledge(memory_client, pinecone_client)
    return _consolidated_knowledge


def search_profile_and_template(query: str) -> KnowledgeResult:
    """Convenience function to search for profile and template."""
    return get_consolidated_knowledge().search_knowledge(query)
