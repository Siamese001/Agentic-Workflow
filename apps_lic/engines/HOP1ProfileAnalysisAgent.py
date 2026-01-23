"""
HOP-1: Profile Analysis Agent (V2 Architecture).

Classifies recipient Archetype using deterministic heuristics from configuration.
Future-proofed for Hybrid (LLM) reasoning injection.
"""

from __future__ import annotations

from typing import Any

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class HOP1ProfileAnalysisAgent(V2AgentBase):
    """
    V2 Implementation of HOP-1.

    Architecture:
    - Base: V2AgentBase (Config, Tracing, Healing)
    - Input: 'recipient_profile' (Dict) from ImmutableStagingBuffer
    - Logic: Deterministic Keyword Matching (Fast Path)
    - Output: 'hop1_analysis' (Dict) to ImmutableStagingBuffer
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute profile analysis logic.

        1. Validates input.
        2. Applies heuristic classification (Fast Path).
        3. Checks for low confidence (Slow Path trigger).
        4. Writes immutable result.
        """
        # 1. Input Validation
        profile = buffer.read("recipient_profile")
        if not profile or not isinstance(profile, dict):
            registry.add_trace("DATA_ERROR", {"msg": "Missing or invalid recipient_profile"})
            raise ValueError("HOP-1 requires 'recipient_profile' in buffer")

        title = profile.get("title", "").lower()

        # 2. Fast Path: Heuristic Classification
        result = self._classify_heuristic(title)

        # 3. Slow Path: Reasoning Injection
        if result["needs_manual_override"] and self.toggles.use_cot and self.llm:
            registry.add_trace(
                "REASONING_ACTIVATED",
                {
                    "trigger": "low_confidence",
                    "threshold": self.config.profile_analysis_agent.manual_override_threshold,
                },
            )

            # Simulated LLM Call (In production, load prompt from config and await response)
            try:
                llm_response = self._execute_reasoning(title, result)

                # Hybrid Decision: Trust LLM if it is confident
                if llm_response["confidence"] > result["confidence"]:
                    registry.add_trace(
                        "DECISION_OVERRIDE",
                        {"old": result["archetype"], "new": llm_response["archetype"]},
                    )
                    result.update(llm_response)
                    result["needs_manual_override"] = False  # Resolved by AI
            except Exception as e:
                registry.add_trace("REASONING_ERROR", {"error": str(e)})

        # 4. Output Writing
        output_data = {
            "Archetype": result["archetype"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
            "key_indicators": result["key_indicators"],
            "needs_manual_override": result["needs_manual_override"],
            "recipient_title": title,
            "recipient_name": profile.get("name", ""),
            "recipient_company": profile.get("company", ""),
        }

        buffer.write_once("hop1_analysis", output_data)

        registry.add_trace(
            "DECISION_FINAL", {"archetype": result["archetype"], "confidence": result["confidence"]}
        )

    def _execute_reasoning(self, title: str, current_result: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the 'Slow Path' using the LLM.
        """
        # In a real implementation, this would:
        # 1. Load prompt template
        # 2. Format with title and current_result
        # 3. self.llm.generate(prompt)
        # 4. Parse JSON

        # For Phase 6 Prototype, we delegate to the injected MockLLM
        return self.llm.analyze(title, current_result)

    def _classify_heuristic(self, title: str) -> dict[str, Any]:
        """
        Apply deterministic keyword matching rules from AgentSpecs.
        """
        config = self.config.profile_analysis_agent

        best_match = {
            "archetype": config.default_archetype,
            "confidence": config.default_confidence,
            "reasoning": f"Default fallback for title: '{title}'",
            "key_indicators": [title],
            "needs_manual_override": True,
        }

        # Iterate defined archetypes in config
        for archetype_name, indicators in config.archetype_indicators.items():
            for keyword in indicators.keywords:
                if keyword in title:
                    # Match found
                    return {
                        "archetype": archetype_name,
                        "confidence": indicators.confidence,
                        "reasoning": f"Title '{title}' contains indicator '{keyword}'",
                        "key_indicators": [keyword],
                        "needs_manual_override": indicators.confidence
                        < config.manual_override_threshold,
                    }

        return best_match

    def heal_repository(self) -> None:
        """
        V2 Self-Healing.

        The base class handles Mixin logic. Here we add domain-specific checks.
        """
        super().heal_repository()
        self._run_profile_diagnostics()

    def _run_profile_diagnostics(self) -> None:
        """Run sanity checks on the configuration logic."""
        test_title = "Chief Executive Officer"
        result = self._classify_heuristic(test_title.lower())

        if result["archetype"] != "C_LEVEL":
            # Note: log_warning not available in current mixin implementation
            pass
        else:
            # Note: log_info not available in current mixin implementation
            pass
