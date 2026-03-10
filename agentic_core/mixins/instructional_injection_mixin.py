"""
InstructionalInjectionMixin — Canonical location.

Relocated from agentic_core/config/core/injection_layer_config.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import os
from dataclasses import field
from typing import Any

from agentic_core.config.core.injection_layer_config import (
    INSTRUCTIONAL_PATTERNS,
    InjectionLayer,
    InstructionalPattern,
)
from agentic_core.prompt_governance.security.utils.injection_scan_util import scan_untrusted_text


class InstructionalInjectionMixin:
    """
    Mixin providing all 30 instructional injection patterns to worker agents.

    Usage:
        class MyAgent(instructional_injection_mixin, HealerMixin, ...):
            def process(self, prompt):
                # Inject safety patterns
                prompt = self.inject_safety_layer(prompt)
                # Inject output patterns
                prompt = self.inject_output_layer(prompt, schema=my_schema)
                return self.llm_call(prompt)
    """

    _injection_patterns: dict[int, InstructionalPattern] = INSTRUCTIONAL_PATTERNS
    _enabled_layers: set = field(default_factory=lambda: set(InjectionLayer))

    def get_pattern(self, pattern_id: int) -> InstructionalPattern | None:
        """Get a specific instructional pattern by ID."""
        return self._injection_patterns.get(pattern_id)

    def get_patterns_by_layer(self, layer: InjectionLayer) -> list[InstructionalPattern]:
        """Get all patterns for a specific layer."""
        return [p for p in self._injection_patterns.values() if p.layer == layer and p.enabled]

    def inject_pattern(self, prompt: str, pattern_id: int, **kwargs) -> str:
        """Inject a specific pattern into a prompt."""
        pattern = self.get_pattern(pattern_id)
        if not pattern or not pattern.enabled:
            return prompt

        try:
            injection = pattern.template.format(**kwargs)
            return f"{injection}\n\n{prompt}"
        except KeyError:
            # Missing template variables - return prompt unchanged
            return prompt

    def inject_framing_layer(
        self,
        prompt: str,
        goal: str = "",
        criteria: str = "",
        mode: str = "analytical",
        boundaries: str = "",
        forbidden: str = "",
        target_tokens: int = 2000,
    ) -> str:
        """Inject all framing layer patterns (1-5)."""
        if goal:
            prompt = self.inject_pattern(prompt, 1, goal=goal)
        if criteria:
            prompt = self.inject_pattern(prompt, 2, criteria=criteria)
        prompt = self.inject_pattern(prompt, 3, mode=mode)
        if boundaries or forbidden:
            prompt = self.inject_pattern(prompt, 4, boundaries=boundaries, forbidden=forbidden)
        prompt = self.inject_pattern(prompt, 5, target_tokens=target_tokens)
        return prompt

    # guardian: allow-magic-config
    def inject_context_layer(
        self,
        prompt: str,
        user_data: str = "",
        max_tokens: int = 4000,
    ) -> str:
        """Inject context layer patterns (6-10)."""
        if user_data:
            prompt = self.inject_pattern(prompt, 6, user_data=user_data)
        prompt = self.inject_pattern(prompt, 7)
        prompt = self.inject_pattern(prompt, 8, max_tokens=max_tokens)
        prompt = self.inject_pattern(prompt, 9)
        prompt = self.inject_pattern(prompt, 10)
        return prompt

    def inject_reasoning_layer(
        self,
        prompt: str,
        n_branches: int = 3,
    ) -> str:
        """Inject reasoning layer patterns (11-15)."""
        prompt = self.inject_pattern(prompt, 11)
        prompt = self.inject_pattern(prompt, 12, n_branches=n_branches)
        prompt = self.inject_pattern(prompt, 13)
        prompt = self.inject_pattern(prompt, 14)
        prompt = self.inject_pattern(prompt, 15)
        return prompt

    def inject_tooling_layer(
        self,
        prompt: str,
        tool_output: str = "",
        source: str = "",
        priority_order: str = "RAG > QA > Draft",
        model: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
    ) -> str:
        """Inject tooling layer patterns (16-20)."""
        # §P1 — Canonical injection scan on tool_output before injection (fail-closed)
        if tool_output:
            scan_untrusted_text(tool_output, source="mixin_tool_output")
        if tool_output:
            prompt = self.inject_pattern(prompt, 16, tool_output=tool_output)
        if source:
            prompt = self.inject_pattern(prompt, 17, source=source)
        prompt = self.inject_pattern(prompt, 18, priority_order=priority_order)
        prompt = self.inject_pattern(prompt, 19)
        prompt = self.inject_pattern(prompt, 20, model=model)
        return prompt

    def inject_safety_layer(
        self,
        prompt: str,
        protected_decisions: str = "",
    ) -> str:
        """Inject safety layer patterns (21-25). CRITICAL for all agents."""
        prompt = self.inject_pattern(prompt, 21)
        prompt = self.inject_pattern(prompt, 22)
        prompt = self.inject_pattern(prompt, 23)
        if protected_decisions:
            prompt = self.inject_pattern(prompt, 24, protected_decisions=protected_decisions)
        prompt = self.inject_pattern(prompt, 25)
        return prompt

    # guardian: allow-magic-config
    def inject_output_layer(
        self,
        prompt: str,
        schema: str = "",
        example: str = "",
        max_tokens: int = 1000,
    ) -> str:
        """Inject output layer patterns (26-30)."""
        prompt = self.inject_pattern(prompt, 26)
        if schema:
            prompt = self.inject_pattern(prompt, 27, schema=schema, example=example or "{}")
        prompt = self.inject_pattern(prompt, 28)
        prompt = self.inject_pattern(prompt, 29)
        prompt = self.inject_pattern(prompt, 30, max_tokens=max_tokens)
        return prompt

    def inject_all_layers(
        self,
        prompt: str,
        goal: str = "",
        mode: str = "analytical",
        schema: str = "",
        **kwargs,
    ) -> str:
        """Inject all 30 patterns across all layers."""
        prompt = self.inject_framing_layer(prompt, goal=goal, mode=mode, **kwargs)
        prompt = self.inject_context_layer(prompt, **kwargs)
        prompt = self.inject_reasoning_layer(prompt, **kwargs)
        prompt = self.inject_tooling_layer(prompt, **kwargs)
        prompt = self.inject_safety_layer(prompt, **kwargs)
        prompt = self.inject_output_layer(prompt, schema=schema, **kwargs)
        return prompt

    def get_injection_summary(self) -> dict[str, Any]:
        """Get summary of available injection patterns."""
        return {
            "total_patterns": len(self._injection_patterns),
            "layers": {layer.value: len(self.get_patterns_by_layer(layer)) for layer in InjectionLayer},
            "enabled_count": sum(1 for p in self._injection_patterns.values() if p.enabled),
        }


# Backward compatibility alias
instructional_injection_mixin = InstructionalInjectionMixin


# Convenience function for standalone use
def get_instructional_injection_mixin() -> InstructionalInjectionMixin:
    """Get an instance of the instructional injection mixin."""
    return InstructionalInjectionMixin()
