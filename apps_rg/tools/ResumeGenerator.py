"""
Resume Generator - LLM-powered resume tailoring.

Rewrites and optimizes resume content based on job analysis results.
"""

import logging
from typing import Any

from runtime.shared.multi_provider_clients import Provider, get_client

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_reads_policy_state("p0", "ResumeGenerator", "policy_binding")
_emit_snapshots_state("p0", "ResumeGenerator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
