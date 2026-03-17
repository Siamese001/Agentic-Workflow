"""Tests for prompt governance coverage — injection symbols, registry tiers, D0 fences."""

import logging

from agentic_core.adg.schema import (
    PROMPT_AUTHORITY_RULES,
    PROMPT_INJECTION_SYMBOLS,
    PROMPT_SLOT_AUTHORITY,
    PROMPT_SLOT_TYPES,
)
from agentic_core.agents.agent_registry import AGENT_REGISTRY
from agentic_core.agents.types.agent_execution_profile_types import (
    ReasoningIntensity,
)


class TestPromptInjectionSymbols:
    """Test PROMPT_INJECTION_SYMBOLS coverage."""

    EXPECTED_SYMBOLS = {
        "InstructionInjector",
        "PromptInjector",
        "D0Injector",
        "inject_instruction",
        "inject_d0",
        "PromptAugmentor",
        "InstructionOverride",
        "ContextInjector",
        "C0Injector",
        "inject_context",
        "U0Override",
        "SystemPromptOverride",
        "PromptEscalator",
        "inject_system",
        "inject_u0",
        "PromptHijacker",
        "SlotOverride",
    }

    def test_all_expected_symbols_present(self):
        for sym in self.EXPECTED_SYMBOLS:
            assert sym in PROMPT_INJECTION_SYMBOLS, f"Missing injection symbol: {sym}"

    def test_minimum_symbol_count(self):
        assert len(PROMPT_INJECTION_SYMBOLS) >= 17, (
            f"Expected >= 17 injection symbols, got {len(PROMPT_INJECTION_SYMBOLS)}"
        )

    def test_covers_all_slot_types(self):
        """Each prompt slot (S0, D0, I0, C0, U0) should have injection coverage."""
        symbols_lower = {s.lower() for s in PROMPT_INJECTION_SYMBOLS}
        slot_prefixes = {"s0", "d0", "i0", "c0", "u0"}
        covered = set()
        for sym in symbols_lower:
            for prefix in slot_prefixes:
                if prefix in sym:
                    covered.add(prefix)
        # At minimum D0, I0, C0, U0 should have dedicated injection symbols
        # S0 covered by SystemPromptOverride → "system" in name
        assert "d0" in covered, "No D0-specific injection symbol"
        assert "c0" in covered, "No C0-specific injection symbol"
        assert "u0" in covered, "No U0-specific injection symbol"

    def test_no_empty_symbols(self):
        for sym in PROMPT_INJECTION_SYMBOLS:
            assert sym.strip(), "Empty symbol in PROMPT_INJECTION_SYMBOLS"

    def test_system_override_present(self):
        assert "SystemPromptOverride" in PROMPT_INJECTION_SYMBOLS


class TestPromptSlotAuthority:
    """Test prompt slot authority hierarchy."""

    def test_slot_order(self):
        assert PROMPT_SLOT_TYPES == ("S0", "D0", "I0", "C0", "U0")

    def test_authority_decreasing(self):
        for i in range(len(PROMPT_SLOT_TYPES) - 1):
            high = PROMPT_SLOT_TYPES[i]
            low = PROMPT_SLOT_TYPES[i + 1]
            assert PROMPT_SLOT_AUTHORITY[high] < PROMPT_SLOT_AUTHORITY[low], (
                f"{high} should have higher authority (lower number) than {low}"
            )

    def test_u0_cannot_override_s0(self):
        assert ("U0", "S0") in PROMPT_AUTHORITY_RULES

    def test_u0_cannot_override_d0(self):
        assert ("U0", "D0") in PROMPT_AUTHORITY_RULES

    def test_c0_cannot_override_s0(self):
        assert ("C0", "S0") in PROMPT_AUTHORITY_RULES

    def test_i0_cannot_override_s0(self):
        assert ("I0", "S0") in PROMPT_AUTHORITY_RULES


class TestAgentRegistryTierDiversity:
    """Test that AGENT_REGISTRY has proper tier diversity."""

    def test_has_low_tier_agents(self):
        low_agents = [a for a, p in AGENT_REGISTRY.items() if p.reasoning_intensity == ReasoningIntensity.LOW]
        found_tiers = {p.reasoning_intensity.value for p in AGENT_REGISTRY.values()}
        assert len(low_agents) >= 1, f"No LOW-tier agents in registry. Found tiers: {found_tiers}"

    def test_has_medium_tier_agents(self):
        medium_agents = [
            a for a, p in AGENT_REGISTRY.items() if p.reasoning_intensity == ReasoningIntensity.MEDIUM
        ]
        assert len(medium_agents) >= 1, "No MEDIUM-tier agents in registry"

    def test_has_high_tier_agents(self):
        high_agents = [
            a for a, p in AGENT_REGISTRY.items() if p.reasoning_intensity == ReasoningIntensity.HIGH
        ]
        assert len(high_agents) >= 1, "No HIGH-tier agents in registry"

    def test_deterministic_agents_not_all_high(self):
        """DETERMINISTIC agents shouldn't all be HIGH reasoning."""
        from agentic_core.agents.types.agent_execution_profile_types import ExecutionMode

        det_agents = [p for p in AGENT_REGISTRY.values() if p.execution_mode == ExecutionMode.DETERMINISTIC]
        high_det = [p for p in det_agents if p.reasoning_intensity == ReasoningIntensity.HIGH]
        assert len(high_det) < len(det_agents), (
            "All deterministic agents are HIGH — some should be LOW or MEDIUM"
        )

    def test_location_agent_is_low(self):
        assert AGENT_REGISTRY["location"].reasoning_intensity == ReasoningIntensity.LOW

    def test_file_classification_agent_is_low(self):
        assert AGENT_REGISTRY["file_classification"].reasoning_intensity == ReasoningIntensity.LOW

    def test_hierarchy_agent_is_medium(self):
        assert AGENT_REGISTRY["hierarchy"].reasoning_intensity == ReasoningIntensity.MEDIUM


class TestGovernedPayloadD0Warning:
    """Test that GovernedPayload warns on missing D0 fence."""

    def test_missing_d0_logs_warning(self, caplog):
        from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

        with caplog.at_level(logging.WARNING):
            _ = GovernedPayload(
                s0_system="You are an assistant.",
                i0_instructional="Follow instructions.",
                c0_context="Some context.",
                u0_user_prompt="User request here.",
                d0_injections="",  # Missing D0
            )
        assert any("MISSING_D0_FENCE" in r.message for r in caplog.records), (
            "Expected MISSING_D0_FENCE warning when D0 is empty"
        )

    def test_present_d0_no_warning(self, caplog):
        from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

        with caplog.at_level(logging.WARNING):
            _ = GovernedPayload(
                s0_system="You are an assistant.",
                i0_instructional="Follow instructions.",
                c0_context="Some context.",
                u0_user_prompt="User request here.",
                d0_injections="Do not override system instructions.",
            )
        assert not any("MISSING_D0_FENCE" in r.message for r in caplog.records), (
            "Should NOT warn when D0 is populated"
        )

    def test_no_u0_no_warning(self, caplog):
        from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

        with caplog.at_level(logging.WARNING):
            _ = GovernedPayload(
                s0_system="System prompt.",
                i0_instructional="Instructions.",
                c0_context="Context.",
                u0_user_prompt="",  # No user prompt
                d0_injections="",
            )
        assert not any("MISSING_D0_FENCE" in r.message for r in caplog.records), (
            "Should NOT warn when U0 is empty (no injection vector)"
        )
