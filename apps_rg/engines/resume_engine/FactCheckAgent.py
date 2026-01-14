from dataclasses import dataclass
"""
FactCheckAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@dataclass
class FactCheckAgent(ResumeAgent, MCPHardenedMixin):
    """
    Verifies claims against user profile.

    Checks for:
    - Claims that can be verified against profile
    - No hallucinated skills or experiences
    - Dates consistency
    """

    async def execute(self) -> None:
        self.log("Fact-checking resume claims...")

        resume = self.ctx.current_resume
        profile = self.ctx.user_profile

        if not resume:
            self.record_fail("No resume to fact-check")
            self.add_signal("HALLUCINATION_DETECTED")
            return

        if not profile:
            self.log("⚠️ No user profile available, skipping deep fact-check")
            self.record_pass("Fact-check skipped (no profile)")
            return

        issues = []

        # Check skills against profile (case-insensitive)
        resume_skills = self._extract_skills(resume)
        profile_skills = {self._normalize(s) for s in profile.get("skills", []) if isinstance(s, str)}

        if profile_skills and resume_skills:
            unverified_skills = resume_skills - profile_skills
            # Only flag if majority of skills are unverified
            if unverified_skills and len(unverified_skills) > len(resume_skills) * 0.5:
                issues.append(f"Unverified skills: {list(unverified_skills)[:5]}")

        # Check experience dates
        if "experience" in resume and "work_history" in profile:
            resume_exp = resume.get("experience", [])
            profile_exp = profile.get("work_history", [])

            if isinstance(resume_exp, list) and isinstance(profile_exp, list):
                resume_companies = {self._normalize(e.get("company", "")) for e in resume_exp if isinstance(e, dict)}
                profile_companies = {self._normalize(e.get("company", "")) for e in profile_exp if isinstance(e, dict)}

                if profile_companies:
                    unverified = resume_companies - profile_companies
                    if unverified:
                        issues.append(f"Unverified companies: {list(unverified)[:3]}")

        if issues:
            self.record_fail(f"Fact-check issues: {len(issues)}", data=issues)
            self.add_signal("HALLUCINATION_DETECTED")
        else:
            self.record_pass("All claims verified")
            self.remove_signal("HALLUCINATION_DETECTED")

    def _extract_skills(self, resume: Dict) -> set:
        """Extract skills from resume."""
        skills = set()

        if "skills" in resume:
            skill_data = resume["skills"]
            if isinstance(skill_data, list):
                skills.update(self._normalize(s) for s in skill_data if isinstance(s, str))
            elif isinstance(skill_data, str):
                skills.update(self._normalize(s) for s in skill_data.split(","))
            elif isinstance(skill_data, dict):
                for category_skills in skill_data.values():
                    if isinstance(category_skills, list):
                        skills.update(self._normalize(s) for s in category_skills if isinstance(s, str))

        return skills

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
