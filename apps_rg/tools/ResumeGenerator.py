"""
Resume Generator - LLM-powered resume tailoring.

Rewrites and optimizes resume content based on job analysis results.
"""

import logging
from typing import Any

from runtime.shared.multi_provider_clients import Provider, get_client

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
        self.creative_brief = creative_brief  # Store creative brief configuration
        self.validation_rules = validation_rules or {}  # Store validation rules

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
            # Create a copy to avoid modifying original
            tailored_resume = resume_data.copy()

            # Tailor each section
            if "summary" in tailored_resume:
                tailored_resume["summary"] = self._tailor_summary(
                    tailored_resume["summary"],
                    analysis_results,
                )

            if "experience" in tailored_resume:
                tailored_resume["experience"] = self._tailor_experience(
                    tailored_resume["experience"],
                    analysis_results,
                )

            if "skills" in tailored_resume:
                tailored_resume["skills"] = self._tailor_skills(tailored_resume["skills"], analysis_results)

            # Add metadata about tailoring
            tailored_resume["_tailoring_metadata"] = {
                "target_hard_skills": analysis_results.get("hard_skills", []),
                "target_soft_skills": analysis_results.get("soft_skills", []),
                "experience_level": analysis_results.get("experience_level", "unknown"),
                "north_star_metric": analysis_results.get("north_star_metric", "unknown"),
            }

            return tailored_resume

        except Exception as e:
            Logger.error(f"Error generating tailored resume: {e}")
            # Return original with error note
            resume_data["_tailoring_error"] = str(e)
            return resume_data

    def _tailor_summary(self, original_summary: str, analysis: dict[str, Any]) -> str:
        """Tailor the professional summary to match job requirements."""
        # Use creative brief word count constraints if available
        word_count_range = "120-140"
        if self.creative_brief and hasattr(self.creative_brief, "executive_summary_word_count"):
            word_count_range = f"{self.creative_brief.executive_summary_word_count.min_words}-{self.creative_brief.executive_summary_word_count.max_words}"

        prompt = f"""Rewrite the following professional summary to align with the target job requirements.

ORIGINAL SUMMARY:
{original_summary}

TARGET REQUIREMENTS:
- Hard Skills: {", ".join(analysis.get("hard_skills", []))}
- Soft Skills: {", ".join(analysis.get("soft_skills", []))}
- North Star Metric: {analysis.get("north_star_metric", "N/A")}

Please rewrite the summary to:
1. Highlight relevant hard skills from the target requirements
2. Demonstrate the soft skills they're looking for
3. Align with their key success Metric
4. Keep it within {word_count_range} words
5. Use active, confident language

Return ONLY the rewritten summary, no additional text."""

        try:
            response = self._generate_response(prompt)
            return response.strip()
        except Exception as e:
            Logger.error(f"Error tailoring summary: {e}")
            return original_summary

    def _tailor_experience(
        self,
        experience_list: list[dict[str, Any]],
        analysis: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Tailor experience section to highlight relevant achievements."""
        tailored_experience = []

        target_skills = analysis.get("hard_skills", []) + analysis.get("soft_skills", [])

        for exp in experience_list:
            tailored_exp = exp.copy()

            # Tailor responsibilities/description
            if "responsibilities" in exp:
                tailored_exp["responsibilities"] = self._tailor_bullets(
                    exp["responsibilities"],
                    target_skills,
                    analysis.get("key_responsibilities", []),
                )
            elif "description" in exp:
                tailored_exp["description"] = self._tailor_description(exp["description"], target_skills)

            # Tailor achievements if present
            if "achievements" in exp:
                tailored_exp["achievements"] = self._tailor_bullets(
                    exp["achievements"],
                    target_skills,
                    analysis.get("key_responsibilities", []),
                )

            tailored_experience.append(tailored_exp)

        return tailored_experience

    def _tailor_skills(self, original_skills: list[str], analysis: dict[str, Any]) -> list[str]:
        """Reorder and emphasize skills based on job requirements."""
        target_hard_skills = analysis.get("hard_skills", [])
        target_soft_skills = analysis.get("soft_skills", [])

        # Separate hard and soft skills
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

        # Combine with target skills first
        final_skills = []

        # Add matching hard skills first
        final_skills.extend(hard_skills[:5])

        # Add any Missing target hard skills
        for target in target_hard_skills:
            if target not in [s.lower() for s in final_skills]:
                final_skills.append(target)

        # Add matching soft skills
        final_skills.extend(soft_skills[:3])

        # Add remaining skills
        final_skills.extend(other_skills[:10])

        return final_skills[:15]  # Limit to 15 skills

    def _tailor_bullets(
        self,
        bullets: list[str],
        target_skills: list[str],
        job_responsibilities: list[str],
    ) -> list[str]:
        """Tailor bullet points to emphasize target skills."""
        tailored_bullets = []

        # Use creative brief word count constraints if available
        word_count_max = 25
        if self.creative_brief and hasattr(self.creative_brief, "unify_bullet_word_count"):
            word_count_max = self.creative_brief.unify_bullet_word_count.max_words

        for bullet in bullets:
            prompt = f"""Rewrite the following resume bullet point to emphasize the target skills and responsibilities.

ORIGINAL BULLET:
{bullet}

TARGET SKILLS: {", ".join(target_skills)}
JOB RESPONSIBILITIES: {", ".join(job_responsibilities)}

Please rewrite the bullet to:
1. Use the STAR method (Situation, Task, Action, Result)
2. Incorporate relevant target skills
3. Align with job responsibilities
4. Start with a strong action verb
5. Include quantifiable metrics if possible
6. Keep it under {word_count_max} words

Return ONLY the rewritten bullet, no additional text."""

            try:
                response = self._generate_response(prompt)
                tailored_bullets.append(response.strip())
            except Exception as e:
                Logger.error(f"Error tailoring bullet: {e}")
                tailored_bullets.append(bullet)

        return tailored_bullets

    def _tailor_description(self, description: str, target_skills: list[str]) -> str:
        """Tailor job description to highlight relevant skills."""
        prompt = f"""Rewrite the following job description to emphasize the target skills.

ORIGINAL DESCRIPTION:
{description}

TARGET SKILLS: {", ".join(target_skills)}

Please rewrite to:
1. Highlight experience with target skills
2. Use active, achievement-oriented language
3. Keep it concise (under 100 words)
4. Focus on results and impact

Return ONLY the rewritten description, no additional text."""

        try:
            response = self._generate_response(prompt)
            return response.strip()
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
            response = gateway.generate(request)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            Logger.error(
                "ResumeGenerator._generate_with_gemini: SovereignLLMGateway failed: %s; "
                "direct SDK fallback is NOT permitted — raising",
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
        optimized = resume_data.copy()

        # Add keywords section for ATS
        all_keywords = (
            analysis.get("hard_skills", [])
            + analysis.get("soft_skills", [])
            + analysis.get("key_responsibilities", [])
            + analysis.get("cultural_indicators", [])
        )

        # Remove duplicates and limit
        unique_keywords = list({k.lower() for k in all_keywords})[:30]

        optimized["ats_keywords"] = unique_keywords

        # Ensure standard section names
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
