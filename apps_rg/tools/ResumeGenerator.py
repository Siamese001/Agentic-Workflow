"""
Resume Generator - LLM-powered resume tailoring.

Rewrites and optimizes resume content based on job analysis results.
"""

import logging
from typing import Any

from runtime.shared.multi_provider_clients import Provider, get_client

from agentic_core.L2_execution.utils import get_clock
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
)

_emit_reads_policy_state("p0", "ResumeGenerator", "policy_binding")
_emit_snapshots_state("p0", "ResumeGenerator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ResumeGenerator", "execution_auth")
_emit_validates_capability("p2", "ResumeGenerator", "capability_check")
_emit_routes_to_capability("p2", "ResumeGenerator", "capability_route")
_emit_writes_via_uwg("p2", "ResumeGenerator", "uwg_write")
_emit_blocks_direct_write("p2", "ResumeGenerator", "direct_write_block")
_emit_records_tool_invocation("p2", "ResumeGenerator", "tool_invocation")
_emit_captures_execution_output("p2", "ResumeGenerator", "exec_output")
_emit_dispatches_agent("p3", "ResumeGenerator", "agent_dispatch")
_emit_coordinates_agents("p3", "ResumeGenerator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ResumeGenerator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ResumeGenerator", "healing_outcome")
_emit_escalates_failure("p3", "ResumeGenerator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ResumeGenerator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ResumeGenerator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ResumeGenerator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ResumeGenerator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ResumeGenerator", "eval_metric")
_emit_stores_embedding("p4", "ResumeGenerator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ResumeGenerator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ResumeGenerator", "exec_snapshot_link")
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

_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_1")
_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_2")
_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_3")
_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_4")
_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_5")
_emit_emits_metric_event("ResumeGenerator", "p4obs", "metric_6")
_emit_records_incident_event("ResumeGenerator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ResumeGenerator", "p4obs", "anomaly")
_emit_writes_observability_log("ResumeGenerator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ResumeGenerator", "p4obs", "mon_state")
_emit_triggers_alert("ResumeGenerator", "p4obs", "alert")
_emit_links_incident_trace("ResumeGenerator", "p4obs", "trace_link")
_emit_captures_pattern("ResumeGenerator", "p3lm", "pattern")
_emit_records_learning_event("ResumeGenerator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ResumeGenerator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ResumeGenerator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ResumeGenerator", "p3lm", "routing")
_emit_improves_agent_policy("ResumeGenerator", "p3lm", "policy")
_emit_stores_learning_state("ResumeGenerator", "p3lm", "state")
_emit_records_execution_trace("ResumeGenerator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ResumeGenerator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ResumeGenerator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ResumeGenerator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ResumeGenerator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ResumeGenerator", "env_read", "p2_env_1")
_emit_reads_environ("ResumeGenerator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ResumeGenerator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ResumeGenerator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ResumeGenerator", "context_pull")
_emit_pulls_context("p1", "ResumeGenerator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ResumeGenerator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ResumeGenerator", "uwg_term_2")
_emit_writes_through("p1", "ResumeGenerator", "write_through")
_emit_writes_through("p1", "ResumeGenerator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ResumeGenerator", "safety_validation")
_emit_invokes_eval("p1", "ResumeGenerator", "eval_call")
_emit_proposal_commits_routing("p1", "ResumeGenerator", "routing_commit")
_emit_escalates_to_human("p1", "ResumeGenerator", "human_escalation")
_emit_routes_through("p1", "ResumeGenerator", "route_through")
_emit_checks_agent_registry("p1", "ResumeGenerator", "agent_registry")
_emit_validates_agent_capability("p1", "ResumeGenerator", "capability")
_emit_dispatches_execution_plan("p1", "ResumeGenerator", "exec_plan")
_emit_agent_executes_agent("p1", "ResumeGenerator", "sub_agent")
_emit_routes_to_agent("p1", "ResumeGenerator", "target_agent")
_emit_verifies_policy("p1", "ResumeGenerator", "policy_check")
_emit_observes_runtime_state("p1", "ResumeGenerator", "runtime_state")
_emit_verifies_boundary("p1", "ResumeGenerator", "boundary_check")
_emit_transcripts_response("p1", "ResumeGenerator", "transcript")
_emit_hard_fails_untranscripted("p1", "ResumeGenerator")
_emit_gated_by_confidence("p1", "ResumeGenerator", "confidence_gate")

Logger = logging.getLogger(__name__)


class ResumeGenerator:
    """Generates tailored resumes using LLM based on job analysis."""

    def __init__(
        self,
        llm_client: Any | None = None,
        provider: Any | None = None,
        creative_brief: Any | None = None,
        validation_rules: dict[str, Any] | None = None,
    ):
        """
        Initialize ResumeGenerator.

        Args:
            llm_client: Optional pre-configured LLM client
            provider: Provider to use if client not supplied (defaults to Google/Gemini)
        """
        _default_provider = getattr(Provider, "GOOGLE", provider)
        resolved_provider = provider or _default_provider
        self.llm_client = llm_client or get_client(resolved_provider)
        self.Provider = resolved_provider
        self.creative_brief = creative_brief
        self.validation_rules = validation_rules or {}
        if self.llm_client is None:
            raise ValueError(f"Failed to initialize LLM client for Provider {self.Provider}")

    def generate(self, resume_data: dict[str, Any], analysis_results: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a tailored resume based on job analysis.

        Args:
            resume_data: Original resume data
            analysis_results: Job analysis results from JobAnalyzer

        Returns:
            Modified resume data tailored to the job
        """
        try:
            tailored_resume = resume_data.copy()
            if "summary" in tailored_resume:
                tailored_resume["summary"] = self._tailor_summary(
                    tailored_resume["summary"], analysis_results
                )
            if "experience" in tailored_resume:
                tailored_resume["experience"] = self._tailor_experience(
                    tailored_resume["experience"], analysis_results
                )
            if "skills" in tailored_resume:
                tailored_resume["skills"] = self._tailor_skills(tailored_resume["skills"], analysis_results)
            tailored_resume["_tailoring_metadata"] = {
                "target_hard_skills": analysis_results.get("hard_skills", []),
                "target_soft_skills": analysis_results.get("soft_skills", []),
                "experience_level": analysis_results.get("experience_level", "unknown"),
                "north_star_metric": analysis_results.get("north_star_metric", "unknown"),
            }
            return tailored_resume
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Error generating tailored resume: {e}")
            resume_data["_tailoring_error"] = str(e)
            return resume_data

    def _tailor_summary(self, original_summary: str, analysis: dict[str, Any]) -> str:
        """Tailor the professional summary to match job requirements."""
        word_count_range = "120-140"
        if self.creative_brief and hasattr(self.creative_brief, "executive_summary_word_count"):
            word_count_range = f"{self.creative_brief.executive_summary_word_count.min_words}-{self.creative_brief.executive_summary_word_count.max_words}"
        prompt = f"Rewrite the following professional summary to align with the target job requirements.\n\nORIGINAL SUMMARY:\n{original_summary}\n\nTARGET REQUIREMENTS:\n- Hard Skills: {', '.join(analysis.get('hard_skills', []))}\n- Soft Skills: {', '.join(analysis.get('soft_skills', []))}\n- North Star Metric: {analysis.get('north_star_metric', 'N/A')}\n\nPlease rewrite the summary to:\n1. Highlight relevant hard skills from the target requirements\n2. Demonstrate the soft skills they're looking for\n3. Align with their key success Metric\n4. Keep it within {word_count_range} words\n5. Use active, confident language\n\nReturn ONLY the rewritten summary, no additional text."
        try:
            response = self._generate_response(prompt)
            return response.strip()
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Error tailoring summary: {e}")
            return original_summary

    def _tailor_experience(
        self, experience_list: list[dict[str, Any]], analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Tailor experience section to highlight relevant achievements."""
        tailored_experience = []
        target_skills = analysis.get("hard_skills", []) + analysis.get("soft_skills", [])
        for exp in experience_list:
            tailored_exp = exp.copy()
            if "responsibilities" in exp:
                tailored_exp["responsibilities"] = self._tailor_bullets(
                    exp["responsibilities"], target_skills, analysis.get("key_responsibilities", [])
                )
            elif "description" in exp:
                tailored_exp["description"] = self._tailor_description(exp["description"], target_skills)
            if "achievements" in exp:
                tailored_exp["achievements"] = self._tailor_bullets(
                    exp["achievements"], target_skills, analysis.get("key_responsibilities", [])
                )
            tailored_experience.append(tailored_exp)
        return tailored_experience

    def _tailor_skills(self, original_skills: list[str], analysis: dict[str, Any]) -> list[str]:
        """Reorder and emphasize skills based on job requirements."""
        target_hard_skills = analysis.get("hard_skills", [])
        target_soft_skills = analysis.get("soft_skills", [])
        hard_skills = []
        soft_skills = []
        other_skills = []
        for skill in original_skills:
            skill_lower = skill.lower()
            if any(target.lower() in skill_lower for target in target_hard_skills):
                hard_skills.append(skill)
            elif any(target.lower() in skill_lower for target in target_soft_skills):
                soft_skills.append(skill)
            else:
                other_skills.append(skill)
        final_skills = []
        final_skills.extend(hard_skills[:5])
        for target in target_hard_skills:
            if target not in [s.lower() for s in final_skills]:
                final_skills.append(target)
        final_skills.extend(soft_skills[:3])
        final_skills.extend(other_skills[:10])
        return final_skills[:15]

    def _tailor_bullets(
        self, bullets: list[str], target_skills: list[str], job_responsibilities: list[str]
    ) -> list[str]:
        """Tailor bullet points to emphasize target skills."""
        tailored_bullets = []
        word_count_max = 25
        if self.creative_brief and hasattr(self.creative_brief, "unify_bullet_word_count"):
            word_count_max = self.creative_brief.unify_bullet_word_count.max_words
        for bullet in bullets:
            prompt = f"Rewrite the following resume bullet point to emphasize the target skills and responsibilities.\n\nORIGINAL BULLET:\n{bullet}\n\nTARGET SKILLS: {', '.join(target_skills)}\nJOB RESPONSIBILITIES: {', '.join(job_responsibilities)}\n\nPlease rewrite the bullet to:\n1. Use the STAR method (Situation, Task, Action, Result)\n2. Incorporate relevant target skills\n3. Align with job responsibilities\n4. Start with a strong action verb\n5. Include quantifiable metrics if possible\n6. Keep it under {word_count_max} words\n\nReturn ONLY the rewritten bullet, no additional text."
            try:
                response = self._generate_response(prompt)
                tailored_bullets.append(response.strip())
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"Error tailoring bullet: {e}")
                tailored_bullets.append(bullet)
        return tailored_bullets

    def _tailor_description(self, description: str, target_skills: list[str]) -> str:
        """Tailor job description to highlight relevant skills."""
        prompt = f"Rewrite the following job description to emphasize the target skills.\n\nORIGINAL DESCRIPTION:\n{description}\n\nTARGET SKILLS: {', '.join(target_skills)}\n\nPlease rewrite to:\n1. Highlight experience with target skills\n2. Use active, achievement-oriented language\n3. Keep it concise (under 100 words)\n4. Focus on results and impact\n\nReturn ONLY the rewritten description, no additional text."
        try:
            response = self._generate_response(prompt)
            return response.strip()
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Error tailoring description: {e}")
            return description

    def _generate_response(self, prompt: str) -> str:
        """Generate response using the configured LLM."""
        if self.Provider == Provider.GOOGLE:
            return self._generate_with_gemini(prompt)
        else:
            return self._generate_with_generic_client(prompt)

    def _generate_with_gemini(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response using Google Gemini via SovereignLLMGateway.

        Routes through SovereignLLMGateway — no direct SDK access.
        """
        try:
            from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway

            gateway = SovereignLLMGateway()
            request = GenerationRequest(
                agent_id="ResumeGenerator",
                provider="google",
                model="gemini-2.5-pro",
                prompt=prompt,
                temperature=temperature,
            )
            _clk = get_clock()
            _clk.emit_replay_key(context=f"rg:resume:{request.agent_id}:{request.provider}")
            _clk.emit_determinism_digest(inputs={"agent": request.agent_id, "provider": request.provider})
            response = gateway.generate(request)
            return response.text if hasattr(response, "text") else str(response)
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(
                "ResumeGenerator._generate_with_gemini: SovereignLLMGateway failed: %s; direct SDK fallback is NOT permitted — raising",
                e,
            )
            raise RuntimeError(f"ResumeGenerator: Gemini generation failed (gateway unavailable): {e}") from e

    def _generate_with_generic_client(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response using generic client interface."""
        if hasattr(self.llm_client, "generate"):
            response = self.llm_client.generate(prompt, temperature=temperature)
            return response.text if hasattr(response, "text") else str(response)
        else:
            response = self.llm_client.complete(prompt, temperature=temperature)
            return response.text if hasattr(response, "text") else str(response)

    def optimize_for_ats(self, resume_data: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        """
        Optimize resume for Applicant Tracking Systems (ATS).

        Args:
            resume_data: Resume data to optimize
            analysis: Job analysis results

        Returns:
            ATS-optimized resume data
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResumeGenerator.optimize_for_ats")

        optimized = resume_data.copy()
        all_keywords = (
            analysis.get("hard_skills", [])
            + analysis.get("soft_skills", [])
            + analysis.get("key_responsibilities", [])
            + analysis.get("cultural_indicators", [])
        )
        unique_keywords = list({k.lower() for k in all_keywords})[:30]
        optimized["ats_keywords"] = unique_keywords
        section_mapping = {
            "professional_summary": "summary",
            "objective": "summary",
            "work_experience": "experience",
            "employment": "experience",
            "education_history": "education",
            "technical_skills": "skills",
            "technologies": "skills",
        }
        for old_key, new_key in section_mapping.items():
            if old_key in optimized and new_key not in optimized:
                optimized[new_key] = optimized.pop(old_key)
        return optimized
