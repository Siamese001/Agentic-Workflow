"""
TemplateOptimizerAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class TemplateOptimizerAgent(OutreachAgent, MCPHardenedMixin):
    """Optimizes message templates for engagement."""

    async def execute(self) -> None:
        print(f"   [{self.name}] Optimizing templates...")

        messages = self.ctx.messages

        if not messages:
            self.record_result(True, "No templates to optimize")
            return

        optimizations = []

        for i, message in enumerate(messages):
            content = message.get("content", "")
            subject = message.get("subject", "")

            # Check subject line length
            if len(subject) > 60:
                optimizations.append(f"Message {i}: Subject too long")
            elif len(subject) < 10:
                optimizations.append(f"Message {i}: Subject too short")

            # Check personalization
            if "{name}" not in content and "{company}" not in content:
                optimizations.append(f"Message {i}: Missing personalization")

            # Check call to action
            cta_words = ["schedule", "call", "meet", "discuss", "connect"]
            has_cta = any(word in content.lower() for word in cta_words)
            if not has_cta:
                optimizations.append(f"Message {i}: Missing call to action")

        if optimizations:
            self.add_signal("TEMPLATE_NEEDS_OPTIMIZATION")
            self.record_result(False, f"Optimizations needed: {len(optimizations)}")
            print(f"   [{self.name}] ⚠️ Optimizations needed: {len(optimizations)}")
        else:
            self.record_result(True, "Templates optimized")
            print(f"   [{self.name}] ✅ Templates optimized")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
