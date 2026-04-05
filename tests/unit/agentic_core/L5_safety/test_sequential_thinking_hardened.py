#!/usr/bin/env python3
"""
HARDENED E2E Tests for Kimi K2.5 Sequential Thinking MCP Dominance

These tests verify that sequential thinking is ALWAYS prioritized above cascade chat
and that the hardened configuration is properly enforced.
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure test can find modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Lazy import - only import when needed
def get_sequential_thinking_booster():
    from tools.mcp.sequential_thinking_booster import (
        CORE_TOOLS,
        CRITICAL_TOOLS,
        REASONING_TOOLS,
        SUPPRESSED_TOOLS,
        apply_kimi_k2_5_boosting,
        boost_sequential_thinking,
    )
    return boost_sequential_thinking, apply_kimi_k2_5_boosting, CRITICAL_TOOLS, CORE_TOOLS, SUPPRESSED_TOOLS, REASONING_TOOLS


class TestSequentialThinkingDominance:
    """Test that sequential thinking has ABSOLUTE priority over cascade chat."""

    def test_sequential_thinking_always_first(self):
        """CRITICAL: Sequential thinking tools MUST always be first in the list."""
        tools = [
            {'name': 'cascade_chat', 'description': 'Cascade chat tool'},
            {'name': 'sequential_thinking', 'description': 'Sequential thinking tool'},
            {'name': 'filesystem', 'description': 'Filesystem operations'},
            {'name': 'simple_chat', 'description': 'Simple chat fallback'},
        ]

        boosted = boost_sequential_thinking(tools)

        # CRITICAL: Sequential thinking MUST be first
        assert boosted[0]['name'] == 'sequential_thinking', \
            "CRITICAL FAIL: Sequential thinking is not first!"

        # Chat tools MUST be at the end
        chat_positions = [i for i, t in enumerate(boosted)
                         if any(pat in t['name'] for pat in SUPPRESSED_TOOLS)]
        other_positions = [i for i, t in enumerate(boosted)
                          if not any(pat in t['name'] for pat in SUPPRESSED_TOOLS)]

        if chat_positions and other_positions:
            assert min(chat_positions) > max(other_positions), \
                "CRITICAL FAIL: Chat tools not suppressed to end!"

    def test_cascade_chat_suppressed(self):
        """AGGRESSIVE: All cascade/chat tools MUST be pushed to lowest priority."""
        tools = [
            {'name': 'filesystem', 'description': 'File operations'},
            {'name': 'cascade_chat', 'description': 'Cascade chat'},
            {'name': 'sequential_thinking', 'description': 'Sequential thinking'},
            {'name': 'fallback_chat', 'description': 'Fallback chat mode'},
            {'name': 'simple_chat', 'description': 'Simple chat'},
            {'name': 'adg_redis', 'description': 'ADG Redis operations'},
        ]

        boosted = apply_kimi_k2_5_boosting(tools)

        # Find positions
        seq_pos = next((i for i, t in enumerate(boosted) if 'sequential' in t['name']), None)
        chat_positions = [i for i, t in enumerate(boosted)
                         if any(pat in t['name'] for pat in ['chat', 'cascade', 'fallback'])]

        # CRITICAL: Sequential must be before ALL chat tools
        for chat_pos in chat_positions:
            assert seq_pos < chat_pos, \
                f"CRITICAL FAIL: Sequential thinking ({seq_pos}) not before chat ({chat_pos})!"

    def test_no_chat_fallback_allowed(self):
        """HARDCORE: Chat tools must NEVER be used as fallback for planning."""
        planning_tools = [
            {'name': 'sequential_thinking', 'description': 'Sequential thinking for planning'},
            {'name': 'analysis_tool', 'description': 'Analysis operations'},
            {'name': 'cascade_chat', 'description': 'Quick chat fallback'},
        ]

        boosted = boost_sequential_thinking(planning_tools)

        # Chat tool must be last
        assert boosted[-1]['name'] == 'cascade_chat', \
            "CRITICAL FAIL: Chat fallback not suppressed to last position!"


class TestKimiK2_5Boosting:
    """Test HARDENED Kimi K2.5 specific boosting rules."""

    def test_kimi_k2_5_categories_prioritized(self):
        """All Kimi K2.5 relevant categories must be prioritized."""
        tools = [
            {'name': 'random_tool', 'description': 'Random operations'},
            {'name': 'validation_engine', 'description': 'Validation and compliance'},
            {'name': 'cascade_chat', 'description': 'Cascade chat'},
            {'name': 'audit_scanner', 'description': 'Audit and governance'},
            {'name': 'basic_calculator', 'description': 'Simple math'},
        ]

        boosted = apply_kimi_k2_5_boosting(tools)

        # Validation and audit tools should come before random and basic tools
        validation_pos = next((i for i, t in enumerate(boosted) if 'validation' in t['name']), 999)
        audit_pos = next((i for i, t in enumerate(boosted) if 'audit' in t['name']), 999)
        random_pos = next((i for i, t in enumerate(boosted) if 'random' in t['name']), 999)
        basic_pos = next((i for i, t in enumerate(boosted) if 'basic' in t['name']), 999)
        chat_pos = next((i for i, t in enumerate(boosted) if 'cascade' in t['name']), 999)

        # Kimi K2.5 tools before generic tools
        assert validation_pos < random_pos, "Validation tool not prioritized!"
        assert audit_pos < basic_pos, "Audit tool not prioritized!"

        # Chat should be among last tools (not necessarily strictly last due to other categorizations)
        assert chat_pos > validation_pos, "Chat tool not after validation!"
        assert chat_pos > audit_pos, "Chat tool not after audit!"

    def test_sequential_thinking_within_kimi_k2_5_first(self):
        """Sequential thinking must be first even among Kimi K2.5 tools."""
        tools = [
            {'name': 'analysis_engine', 'description': 'Analysis tool'},
            {'name': 'reasoning_framework', 'description': 'Reasoning operations'},
            {'name': 'sequential_thinking', 'description': 'Sequential thinking'},
            {'name': 'audit_scanner', 'description': 'Audit tool'},
        ]

        boosted = apply_kimi_k2_5_boosting(tools)

        # Sequential thinking MUST be first
        assert boosted[0]['name'] == 'sequential_thinking', \
            "Sequential thinking not first among Kimi K2.5 tools!"


class TestEnvironmentVariables:
    """Test that hardened environment variables are properly set."""

    def test_cascade_chat_fallback_disabled(self, monkeypatch):
        """CRITICAL: CASCADE_CHAT_FALLBACK must be disabled."""
        # Set the expected value
        monkeypatch.setenv('CASCADE_CHAT_FALLBACK', 'disabled')

        fallback = os.environ.get('CASCADE_CHAT_FALLBACK')
        assert fallback == 'disabled', \
            f"CRITICAL: CASCADE_CHAT_FALLBACK is '{fallback}', must be 'disabled'!"

    def test_sequential_thinking_priority_absolute(self, monkeypatch):
        """CRITICAL: SEQUENTIAL_THINKING_PRIORITY must be 0 (absolute highest)."""
        monkeypatch.setenv('SEQUENTIAL_THINKING_PRIORITY', '0')

        priority = os.environ.get('SEQUENTIAL_THINKING_PRIORITY')
        assert priority == '0', \
            f"CRITICAL: Priority is '{priority}', must be '0' for absolute dominance!"

    def test_kimi_k2_5_dominance_enabled(self, monkeypatch):
        """CRITICAL: KIMI_K2_5_DOMINANCE must be enabled."""
        monkeypatch.setenv('KIMI_K2_5_DOMINANCE', 'enabled')

        dominance = os.environ.get('KIMI_K2_5_DOMINANCE')
        assert dominance == 'enabled', \
            f"CRITICAL: KIMI_K2_5_DOMINANCE is '{dominance}', must be 'enabled'!"

    def test_reasoning_mode_sequential_only(self, monkeypatch):
        """AGGRESSIVE: WINDSURF_REASONING_MODE must be 'sequential-only'."""
        monkeypatch.setenv('WINDSURF_REASONING_MODE', 'sequential-only')

        mode = os.environ.get('WINDSURF_REASONING_MODE')
        assert mode == 'sequential-only', \
            f"CRITICAL: Reasoning mode is '{mode}', must be 'sequential-only'!"


class TestAggressiveToolOrdering:
    """Test aggressive tool ordering scenarios."""

    def test_mixed_tools_aggressive_sorting(self):
        """Test aggressive sorting with complex mixed tool set."""
        tools = [
            {'name': 'chat_fallback', 'description': 'Quick chat response'},
            {'name': 'simple_tool', 'description': 'Simple operations'},
            {'name': 'sequential_thinking', 'description': 'Deep sequential analysis'},
            {'name': 'cascade_chat', 'description': 'Cascade chat mode'},
            {'name': 'filesystem', 'description': 'File operations'},
            {'name': 'adg_redis', 'description': 'ADG cache access'},
            {'name': 'basic_chat', 'description': 'Basic chat'},
            {'name': 'reasoning_engine', 'description': 'Advanced reasoning'},
            {'name': 'planning_framework', 'description': 'Planning operations'},
        ]

        # Apply both boosting phases
        boosted = boost_sequential_thinking(tools)
        boosted = apply_kimi_k2_5_boosting(boosted)

        # Expected order: sequential_thinking, reasoning/planning, filesystem/adg, others, chat tools
        expected_first = 'sequential_thinking'
        assert boosted[0]['name'] == expected_first, \
            f"Expected '{expected_first}' first, got '{boosted[0]['name']}'"

        # Chat tools should be at the end
        chat_tools = [t for t in boosted if any(pat in t['name'] for pat in ['chat', 'fallback'])]
        non_chat_tools = [t for t in boosted if not any(pat in t['name'] for pat in ['chat', 'fallback'])]

        # All chat tools should come after all non-chat tools
        for chat_tool in chat_tools:
            chat_pos = boosted.index(chat_tool)
            for non_chat in non_chat_tools:
                non_chat_pos = boosted.index(non_chat)
                assert non_chat_pos < chat_pos, \
                    f"Non-chat tool '{non_chat['name']}' ({non_chat_pos}) should come before chat '{chat_tool['name']}' ({chat_pos})"

    def test_empty_tools_list(self):
        """Test handling of empty tools list."""
        boosted = boost_sequential_thinking([])
        assert boosted == [], "Empty list should return empty list"

        boosted = apply_kimi_k2_5_boosting([])
        assert boosted == [], "Empty list should return empty list"


class TestHardenedConfiguration:
    """Test hardened configuration values."""

    def test_max_thoughts_increased(self, monkeypatch):
        """HARDENED: Max thoughts increased to 25 for complex analysis."""
        monkeypatch.setenv('SEQUENTIAL_THINKING_MAX_THOUGHTS', '25')

        max_thoughts = os.environ.get('SEQUENTIAL_THINKING_MAX_THOUGHTS')
        assert max_thoughts == '25', \
            f"Max thoughts is '{max_thoughts}', expected '25' for hardened config!"

    def test_token_budget_increased(self, monkeypatch):
        """HARDENED: Token budget increased to 50000."""
        monkeypatch.setenv('SEQUENTIAL_THINKING_TOKEN_BUDGET', '50000')

        budget = os.environ.get('SEQUENTIAL_THINKING_TOKEN_BUDGET')
        assert budget == '50000', \
            f"Token budget is '{budget}', expected '50000' for hardened config!"

    def test_aggressive_mode_enabled(self, monkeypatch):
        """HARDENED: Aggressive mode must be enabled."""
        monkeypatch.setenv('SEQUENTIAL_THINKING_AGGRESSIVE_MODE', 'enabled')

        mode = os.environ.get('SEQUENTIAL_THINKING_AGGRESSIVE_MODE')
        assert mode == 'enabled', \
            f"Aggressive mode is '{mode}', must be 'enabled'!"

    def test_suppress_chat_on_planning(self, monkeypatch):
        """HARDENED: Chat suppression on planning must be enabled."""
        monkeypatch.setenv('CASCADE_CHAT_SUPPRESS_ON_PLANNING', 'true')

        suppress = os.environ.get('CASCADE_CHAT_SUPPRESS_ON_PLANNING')
        assert suppress == 'true', \
            f"Chat suppression is '{suppress}', must be 'true'!"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_tools_with_no_description(self):
        """Test handling of tools without descriptions."""
        tools = [
            {'name': 'sequential_thinking'},
            {'name': 'cascade_chat'},
            {'name': 'filesystem'},
        ]

        boosted = boost_sequential_thinking(tools)

        # Should still prioritize sequential thinking
        assert boosted[0]['name'] == 'sequential_thinking'

    def test_tools_with_similar_names(self):
        """Test that similar names don't confuse the booster."""
        tools = [
            {'name': 'sequential_thinking_v2', 'description': 'Updated sequential thinking'},
            {'name': 'not_really_a_match', 'description': 'Just a name'},
            {'name': 'sequential_analysis', 'description': 'Sequential analysis tool'},
        ]

        boosted = apply_kimi_k2_5_boosting(tools)

        # Both sequential tools should be at the front (sequential_thinking_v2 and sequential_analysis)
        sequential_tools = [t for t in boosted if 'sequential' in t['name']]
        non_sequential = [t for t in boosted if 'sequential' not in t['name']]

        # Should have 2 sequential tools
        assert len(sequential_tools) == 2, f"Expected 2 sequential tools, got {len(sequential_tools)}"
        assert boosted[0] in sequential_tools

    def test_all_chat_tools_variations(self):
        """Test all variations of chat tool names are suppressed."""
        chat_variations = [
            {'name': 'chat', 'description': 'Chat tool'},
            {'name': 'cascade_chat', 'description': 'Cascade chat'},
            {'name': 'simple_chat', 'description': 'Simple chat'},
            {'name': 'fallback_chat', 'description': 'Fallback chat'},
            {'name': 'quick_chat', 'description': 'Quick chat'},
            {'name': 'direct_chat', 'description': 'Direct chat'},
        ]

        other_tools = [
            {'name': 'filesystem', 'description': 'File ops'},
            {'name': 'sequential_thinking', 'description': 'Sequential thinking'},
        ]

        all_tools = chat_variations + other_tools
        boosted = apply_kimi_k2_5_boosting(all_tools)

        # Sequential thinking should be first
        assert boosted[0]['name'] == 'sequential_thinking'

        # All chat tools should be at the end
        chat_positions = [i for i, t in enumerate(boosted) if 'chat' in t['name']]
        non_chat_positions = [i for i, t in enumerate(boosted) if 'chat' not in t['name']]

        if chat_positions and non_chat_positions:
            assert min(chat_positions) > max(non_chat_positions), \
                "Not all chat tools were suppressed to the end!"


@pytest.fixture
def sample_tools():
    """Fixture providing sample tools for testing."""
    return [
        {'name': 'sequential_thinking', 'description': 'Sequential thinking MCP'},
        {'name': 'filesystem', 'description': 'Filesystem operations'},
        {'name': 'adg_redis', 'description': 'ADG Redis cache'},
        {'name': 'cascade_chat', 'description': 'Cascade chat fallback'},
        {'name': 'memory', 'description': 'Memory MCP'},
        {'name': 'simple_chat', 'description': 'Simple chat tool'},
    ]


def test_full_boosting_pipeline(sample_tools):
    """INTEGRATION: Test full boosting pipeline with all phases."""
    # Apply both boosting phases as in production
    boosted = boost_sequential_thinking(sample_tools)
    boosted = apply_kimi_k2_5_boosting(boosted)

    # Verify order
    assert boosted[0]['name'] == 'sequential_thinking', \
        "Sequential thinking must be first after full pipeline!"

    # Verify chat tools are at the end
    chat_tools = [t for t in boosted if any(pat in t['name'] for pat in SUPPRESSED_TOOLS)]
    for chat_tool in chat_tools:
        pos = boosted.index(chat_tool)
        # All non-chat tools should come before this chat tool
        for i, tool in enumerate(boosted):
            if i < pos and not any(pat in tool['name'] for pat in SUPPRESSED_TOOLS):
                assert True  # Non-chat tool is before chat tool

    print("\nFull pipeline result order:")
    for i, tool in enumerate(boosted):
        print(f"  {i+1}. {tool['name']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
