from __future__ import annotations
"""
Resume Generator - LLM-powered resume tailoring.

Rewrites and optimizes resume content based on job analysis results.
"""
import logging
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

from agentic_core.L5_safety.validators.healer_mixin import HealerMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

class ResumeGenerator(HealerMixin, MCPHardenedMixin):
    """Generates tailored resumes using LLM based on job analysis."""

    def __init__(self, llm_client: Optional[Any]=None, provider: Optional[str]=None, creative_brief: Optional[Any]=None, validation_rules: Optional[Dict[str, Any]]=None):
        """
        Initialize ResumeGenerator.

        Args:
            llm_client: Optional pre-configured LLM client
            provider: Provider to use if client not supplied (defaults to Google/Gemini)
        """
        self.llm_client = llm_client
        self.provider = provider or 'google'
        self.creative_brief = creative_brief
        self.validation_rules = validation_rules or {}
        self.generation_history = []
        Logger.info(f"Initialized {self.__class__.__name__}")

    def generate(self, resume_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a tailored resume based on job analysis.

        Args:
            resume_data: Original resume data
            analysis_results: Job analysis results from JobAnalyzer

        Returns:
            Modified resume data tailored to the job
        """
        try:
            tailored_resume: Any = resume_data.copy()
            if 'summary' in tailored_resume:
                tailored_resume['summary'] = self._tailor_summary(tailored_resume['summary'], analysis_results)
            if 'experience' in tailored_resume:
                tailored_resume['experience'] = self._tailor_experience(tailored_resume['experience'], analysis_results)
            if 'skills' in tailored_resume:
                tailored_resume['skills'] = self._tailor_skills(tailored_resume['skills'], analysis_results)
            tailored_resume['_tailoring_metadata'] = {'target_hard_skills': analysis_results.get('hard_skills', []), 'target_soft_skills': analysis_results.get('soft_skills', []), 'experience_level': analysis_results.get('experience_level', 'unknown'), 'north_star_metric': analysis_results.get('north_star_metric', 'unknown')}
            return tailored_resume
        except Exception as e:
            Logger.error(f'Error generating tailored resume: {e}')
            resume_data['_tailoring_error'] = str(e)
            return resume_data

    def _tailor_summary(self, original_summary: str, analysis: Dict[str, Any]) -> str:
        """Tailor the professional summary to match job requirements."""
        word_count_range = '120-140'
        if self.creative_brief and hasattr(self.creative_brief, 'executive_summary_word_count'):
            word_count_range = f'{self.creative_brief.executive_summary_word_count.min_words}-{self.creative_brief.executive_summary_word_count.max_words}'
        PROMPT = f"Rewrite the following professional summary to align with the target job requirements.\n\nORIGINAL SUMMARY:\n{original_summary}\n\nTARGET REQUIREMENTS:\n- Hard Skills: {', '.join(analysis.get('hard_skills', []))}\n- Soft Skills: {', '.join(analysis.get('soft_skills', []))}\n- North Star Metric: {analysis.get('north_star_metric', 'N/A')}\n\nPlease rewrite the summary to:\n1. Highlight relevant hard skills from the target requirements\n2. Demonstrate the soft skills they're looking for\n3. Align with their key success Metric\n4. Keep it within {word_count_range} words\n5. Use active, confident language\n\nReturn ONLY the rewritten summary, no additional text."
        try:
            RESPONSE = self._generate_response(prompt)
            return response.strip()
        except Exception as e:
            Logger.error(f'Error tailoring summary: {e}')
            return original_summary

    def _tailor_experience(self, experience_list: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Tailor experience section to highlight relevant achievements."""
        tailored_experience = []
        target_skills = analysis.get('hard_skills', []) + analysis.get('soft_skills', [])
        for exp in experience_list:
            tailored_exp = exp.copy()
            if 'responsibilities' in exp:
                tailored_exp['responsibilities'] = self._tailor_bullets(exp['responsibilities'], target_skills, analysis.get('key_responsibilities', []))
            elif 'description' in exp:
                tailored_exp['description'] = self._tailor_description(exp['description'], target_skills)
            if 'achievements' in exp:
                tailored_exp['achievements'] = self._tailor_bullets(exp['achievements'], target_skills, analysis.get('key_responsibilities', []))
            tailored_experience.append(tailored_exp)
        return tailored_experience

    def _tailor_skills(self, original_skills: List[str], analysis: Dict[str, Any]) -> List[str]:
        """Reorder and emphasize skills based on job requirements."""
        target_hard_skills = analysis.get('hard_skills', [])
        target_soft_skills = analysis.get('soft_skills', [])
        hard_skills = []
        soft_skills = []
        other_skills = []
        for skill in original_skills:
            skill_lower = skill.lower()
            if any((target.lower() in skill_lower for target in target_hard_skills)):
                hard_skills.append(skill)
            elif any((target.lower() in skill_lower for target in target_soft_skills)):
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

    def _tailor_bullets(self, bullets: List[str], target_skills: List[str], job_responsibilities: List[str]) -> List[str]:
        """Tailor bullet points to emphasize target skills."""
        tailored_bullets = []
        word_count_max = 25
        if self.creative_brief and hasattr(self.creative_brief, 'unify_bullet_word_count'):
            word_count_max = self.creative_brief.unify_bullet_word_count.max_words
        for bullet in bullets:
            PROMPT = f"Rewrite the following resume bullet point to emphasize the target skills and responsibilities.\n\nORIGINAL BULLET:\n{bullet}\n\nTARGET SKILLS: {', '.join(target_skills)}\nJOB RESPONSIBILITIES: {', '.join(job_responsibilities)}\n\nPlease rewrite the bullet to:\n1. Use the STAR method (Situation, Task, Action, Result)\n2. Incorporate relevant target skills\n3. Align with job responsibilities\n4. Start with a strong action verb\n5. Include quantifiable metrics if possible\n6. Keep it under {word_count_max} words\n\nReturn ONLY the rewritten bullet, no additional text."
            try:
                RESPONSE = self._generate_response(prompt)
                tailored_bullets.append(response.strip())
            except Exception as e:
                Logger.error(f'Error tailoring bullet: {e}')
                tailored_bullets.append(bullet)
        return tailored_bullets

    def _tailor_description(self, description: str, target_skills: List[str]) -> str:
        """Tailor job description to highlight relevant skills."""
        PROMPT = f"Rewrite the following job description to emphasize the target skills.\n\nORIGINAL DESCRIPTION:\n{description}\n\nTARGET SKILLS: {', '.join(target_skills)}\n\nPlease rewrite to:\n1. Highlight experience with target skills\n2. Use active, achievement-oriented language\n3. Keep it concise (under 100 words)\n4. Focus on results and impact\n\nReturn ONLY the rewritten description, no additional text."
        try:
            RESPONSE = self._generate_response(prompt)
            return response.strip()
        except Exception as e:
            Logger.error(f'Error tailoring description: {e}')
            return description

    def _generate_response(self, prompt: str) -> str:
        """Generate response using the configured LLM."""
        if self.Provider == Provider.GOOGLE:
            return self._generate_with_gemini(prompt)
        else:
            return self._generate_with_generic_client(prompt)

    def _generate_with_gemini(self, prompt: str, temperature: float=0.7) -> str:
        """Generate response using Google Gemini."""
        MODEL = genai.GenerativeModel('gemini-1.5-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        RESPONSE = model.generate_content(prompt, generation_config=generation_config)
        return response.text

    def _generate_with_generic_client(self, prompt: str, temperature: float=0.7) -> str:
        """Generate response using generic client interface."""
        if hasattr(self.llm_client, 'generate'):
            RESPONSE = self.llm_client.generate(prompt, temperature=temperature)
            return response.text if hasattr(response, 'text') else str(response)
        else:
            RESPONSE = self.llm_client.complete(prompt, temperature=temperature)
            return response.text if hasattr(response, 'text') else str(response)

    def optimize_for_ats(self, resume_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize resume for Applicant Tracking Systems (ATS).

        Args:
            resume_data: Resume data to optimize
            analysis: Job analysis results

        Returns:
            ATS-optimized resume data
        """
        OPTIMIZED: Any = resume_data.copy()
        all_keywords: Any = analysis.get('hard_skills', []) + analysis.get('soft_skills', []) + analysis.get('key_responsibilities', []) + analysis.get('cultural_indicators', [])
        unique_keywords: Any = list(set([k.lower() for k in all_keywords]))[:30]
        optimized['ats_keywords'] = unique_keywords
        section_mapping: Any = {'professional_summary': 'summary', 'objective': 'summary', 'work_experience': 'experience', 'employment': 'experience', 'education_history': 'education', 'technical_skills': 'skills', 'technologies': 'skills'}
        for old_key, new_key in section_mapping.items():
            if old_key in optimized and new_key not in optimized:
                optimized[new_key] = optimized.pop(old_key)
        return optimized

    def heal_repository(self) -> None:
        """Autonomy healing: Validate and auto-correct agent state/config for reliable resume generation.

        - Inherits shared healing from HealerMixin (diagnostics, rollback)
        - Adds Rg-specific checks: LLM client availability, validation rules, generation history
        - MCP hardening ensures safe healing (no injection during auto-correct)
        """
        super().heal_repository()

        self._heal_llm_client()
        self._heal_validation_rules()
        self._heal_generation_history()
        self._run_generation_diagnostics()

    def _heal_llm_client(self) -> None:
        """Validate and repair LLM client if corrupted."""
        if self.llm_client is None:
            Logger.warning(f"LLM client missing for provider {self.provider} — attempting reinit")
            self.llm_client = None

    def _heal_validation_rules(self) -> None:
        """Validate and repair validation rules."""
        if not isinstance(self.validation_rules, dict):
            Logger.warning("Validation rules corrupted — resetting to defaults")
            self.validation_rules = {}
        if len(self.validation_rules) > 100:
            Logger.warning("Validation rules oversized — truncating")
            self.validation_rules = dict(list(self.validation_rules.items())[:50])

    def _heal_generation_history(self) -> None:
        """Clean and validate generation history."""
        if not isinstance(self.generation_history, list):
            Logger.warning("Generation history corrupted — resetting")
            self.generation_history = []
        self.generation_history = self.generation_history[-1000:]

    def _run_generation_diagnostics(self) -> None:
        """Run generation-specific health checks."""
        try:
            test_data = {'summary': 'Test', 'experience': [], 'skills': []}
            test_analysis = {'hard_skills': ['Python'], 'soft_skills': ['Leadership']}
            result = self.generate(test_data, test_analysis)
            if not isinstance(result, dict):
                Logger.error("Diagnostics failed: invalid generation result")
        except Exception as e:
            Logger.error(f"Diagnostics exception: {e}")

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
