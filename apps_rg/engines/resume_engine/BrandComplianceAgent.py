from typing import Any
from dataclasses import dataclass
"""
BrandComplianceAgent - Extracted for one-class-per-file pattern.

Originally from: ContentQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin

@dataclass
class BrandComplianceAgent(SubatomicTestingMixin, ResumeAgent, MCPHardenedMixin):
    """
    Ensures brand voice and professional tone.

    Checks for:
    - Professional language
    - No informal/slang terms
    - Consistent voice (first/third person)
    - No forbidden phrases
    """

    FORBIDDEN_PHRASES = [
        "i am", "i'm", "my name is",  # First person in summary
        "responsible for",  # Weak phrasing
        "duties included",  # Passive
        "helped with",  # Vague
        "worked on",  # Vague
        "etc.",  # Unprofessional
        "stuff",  # Informal
        "things",  # Vague
        "very",  # Weak intensifier
        "really",  # Weak intensifier
    ]

    POWER_VERBS = [
        "achieved", "delivered", "drove", "led", "managed",
        "developed", "created", "implemented", "optimized", "increased",
        "reduced", "improved", "launched", "designed", "built",
    ]

    async def execute(self) -> None:
        """Execute execute operation."""
        self.log("Checking brand compliance...")

        resume = self.ctx.current_resume
        if not resume:
            self.record_fail("No resume to check")
            self.add_signal("BRAND_VIOLATION")
            return

        issues = []
        suggestions = []

        for section_name, content in resume.items():
            if section_name.startswith("_"):
                continue

            content_str = self._to_string(content).lower()

            # Check forbidden phrases
            for phrase in self.FORBIDDEN_PHRASES:
                if phrase in content_str:
                    issues.append(f"Forbidden phrase '{phrase}' in {section_name}")

            # Check for power verbs in experience
            if section_name == "experience":
                has_power_verb = any(verb in content_str for verb in self.POWER_VERBS)
                if not has_power_verb:
                    suggestions.append("Experience section could use more action verbs")

        if issues:
            self.record_fail(f"Brand violations: {len(issues)}", data={"issues": issues, "suggestions": suggestions})
            self.add_signal("BRAND_VIOLATION")
        else:
            self.record_pass("Brand compliant", data={"suggestions": suggestions})
            self.remove_signal("BRAND_VIOLATION")

    def _to_string(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join(str(item) for item in content)
        elif isinstance(content, dict):
            return json.dumps(content)
        return str(content)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
