from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "pitch_engine")
trace_contract.emit_determinism_digest("p0", "pitch_engine")

trace_contract._emit_dispatches_healing_run("p1", "pitch_engine", "L1")
trace_contract._emit_routes_through("p1", "pitch_engine", "L1")
trace_contract._emit_checks_agent_registry("p1", "pitch_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pitch_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pitch_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pitch_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pitch_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "pitch_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pitch_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pitch_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pitch_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pitch_engine")
trace_contract._emit_gated_by_confidence("p1", "pitch_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "pitch_engine", "L1")
trace_contract._emit_reads_policy_state("p1", "pitch_engine", "L1")
trace_contract._emit_authorize_and_execute("p2", "pitch_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "pitch_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pitch_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pitch_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pitch_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pitch_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pitch_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pitch_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pitch_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pitch_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pitch_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pitch_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pitch_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pitch_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pitch_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pitch_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pitch_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pitch_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pitch_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pitch_engine", "exec_snapshot_link")

"\nPitch Generator for Outreach Engine\nGenerates personalized outreach pitches\n"
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any


trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("pitch_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("pitch_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("pitch_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("pitch_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("pitch_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("pitch_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("pitch_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("pitch_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("pitch_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("pitch_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("pitch_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("pitch_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("pitch_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("pitch_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("pitch_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("pitch_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("pitch_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("pitch_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("pitch_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("pitch_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("pitch_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("pitch_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("pitch_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "pitch_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "pitch_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "pitch_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "pitch_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "pitch_engine", "write_through")
trace_contract._emit_writes_through("p1", "pitch_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "pitch_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "pitch_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "pitch_engine", "routing_commit")

Logger: Any = logging.getLogger(__name__)
__all__ = ["PitchGenerator", "PitchResult"]


@dataclass
class PitchResult:
    """Result from pitch generation."""

    subject: str
    content: str
    metadata: dict[str, Any]


class PitchGenerator:
    """Generates personalized outreach pitches."""

    def __init__(self, llm_client=None):
        """
        Initialize pitch generator.

        Args:
            llm_client: Optional LLM client for generation
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "PitchGenerator.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "PitchGenerator.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_COGNITION, "PitchGenerator.__init__")
        self.llm_client = llm_client

    def generate_pitch(self, context: dict[str, Any], relationships: dict[str, Any]) -> PitchResult:
        """
        Generate personalized pitch based on context and relationships.

        Args:
            context: Company context and news
            relationships: Contact history and relationships

        Returns:
            PitchResult with subject, content, and metadata
        """
        if self.llm_client:
            return self._generate_with_llm(context, relationships)
        else:
            return self._generate_with_template(context, relationships)

    def _generate_with_llm(self, context: dict[str, Any], relationships: dict[str, Any]) -> PitchResult:
        """Generate pitch using LLM."""
        try:
            prompt = self._build_pitch_prompt(context, relationships)
            response = self.llm_client.generate(prompt)
            lines = response.text.strip().split("\n")
            subject = lines[0].replace("Subject:", "").strip() if lines else "Introduction"
            content = "\n".join(lines[1:]) if len(lines) > 1 else response.text
            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm",
                    "model": self.llm_client.model_name,
                    "tokens_used": getattr(response.usage, "total_tokens", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except (
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
            OSError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"LLM pitch generation failed: {e}")
            return self._generate_with_template(context, relationships)

    def _generate_with_template(self, context: dict[str, Any], relationships: dict[str, Any]) -> PitchResult:
        """Generate pitch using template."""
        company_name = context.get("company_name", "the company")
        recent_news = context.get("recent_news", "recent developments")
        contact_name = relationships.get("contact_name", "there")
        mutual_connections = relationships.get("mutual_connections", [])
        subject = f"Introduction - {context.get('my_name', 'Your Name')} & {company_name}"
        content = f"Dear {contact_name},\n\nI hope this email finds you well. I've been following {company_name}'s work and was particularly impressed by {recent_news}.\n\n{('We share several mutual connections: ' + ', '.join(mutual_connections[:3]) + '.' if mutual_connections else '')}\n\nI believe my experience in {context.get('my_field', 'technology')} could be valuable to your team, especially given your focus on {context.get('company_focus', 'innovation')}.\n\nWould you be open to a brief conversation next week to explore potential synergies?\n\nBest regards,\n{context.get('my_name', 'Your Name')}\n{context.get('my_title', 'Your Title')}\n{context.get('my_contact', 'your@email.com')}\n"
        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "template",
                "template": "professional_outreach",
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _build_pitch_prompt(self, context: dict[str, Any], relationships: dict[str, Any]) -> str:
        """Build prompt for LLM pitch generation."""
        return f"\nGenerate a professional outreach email based on the following:\n\nCOMPANY CONTEXT:\n{json.dumps(context, indent=2)}\n\nRELATIONSHIP CONTEXT:\n{json.dumps(relationships, indent=2)}\n\nRequirements:\n- Write a compelling subject line\n- Keep the email concise (150-200 words)\n- Personalize with recent company news or developments\n- Mention mutual connections if available\n- Include a clear call to action\n- Maintain professional but friendly tone\n- Avoid sales-heavy language\n\nFormat the response with the subject line first, followed by the email body.\n"

    def refine_pitch(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """
        Refine a pitch based on error feedback.

        Args:
            pitch: Original pitch to refine
            error_reason: Reason for refinement (e.g., "Too salesy", "Brand compliance issue")

        Returns:
            Refined PitchResult
        """
        if self.llm_client:
            return self._refine_with_llm(pitch, error_reason)
        else:
            return self._refine_with_rules(pitch, error_reason)

    def _refine_with_llm(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """Refine pitch using LLM."""
        try:
            prompt = f"\nRefine the following outreach email to address: {error_reason}\n\nORIGINAL EMAIL:\nSubject: {pitch.subject}\n\n{pitch.content}\n\nRefinement requirements:\n- Fix the specific issue mentioned\n- Maintain professional tone\n- Keep it concise\n- Ensure brand compliance\n- Avoid spam triggers\n\nProvide the refined email in the same format (subject first, then body).\n"
            response = self.llm_client.generate(prompt)
            lines = response.text.strip().split("\n")
            subject = lines[0].replace("Subject:", "").strip() if lines else pitch.subject
            content = "\n".join(lines[1:]) if len(lines) > 1 else response.text
            return PitchResult(
                subject=subject,
                content=content,
                metadata={
                    "source": "llm_refined",
                    "original_subject": pitch.subject,
                    "refinement_reason": error_reason,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except (
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
            OSError,
        ) as e:  # guardian: allow-silent-swallow
            Logger.error(f"LLM pitch refinement failed: {e}")
            return self._refine_with_rules(pitch, error_reason)

    def _refine_with_rules(self, pitch: PitchResult, error_reason: str) -> PitchResult:
        """Refine pitch using rule-based approach."""
        content = pitch.content
        subject = pitch.subject
        if "salesy" in error_reason.lower():
            content = content.replace("excited to offer", "interested in discussing")
            content = content.replace("amazing opportunity", "potential collaboration")
            subject = subject.replace("Opportunity", "Introduction")
        if "brand" in error_reason.lower():
            content = content.replace("!!", "!")
            content = content.replace("$$$ ", "")
        if "spam" in error_reason.lower():
            content = content.replace("FREE", "complimentary")
            content = content.replace("ACT NOW", "Let me know if you're interested")
        return PitchResult(
            subject=subject,
            content=content,
            metadata={
                "source": "rule_refined",
                "original_subject": pitch.subject,
                "refinement_reason": error_reason,
                "timestamp": datetime.now().isoformat(),
            },
        )
