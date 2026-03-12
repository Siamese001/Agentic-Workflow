"""ADG-driven tests for L2_execution/enforcement/network_egress_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.network_egress_guard import (
    COMPILED_PATTERNS,
    LLM_ENDPOINT_PATTERNS,
)


class TestNetworkEgressGuardConstants:
    def test_llm_endpoint_patterns_is_list(self):
        assert isinstance(LLM_ENDPOINT_PATTERNS, list)
        assert len(LLM_ENDPOINT_PATTERNS) > 0

    def test_all_patterns_are_strings(self):
        for p in LLM_ENDPOINT_PATTERNS:
            assert isinstance(p, str)

    def test_compiled_patterns_length_matches(self):
        assert len(COMPILED_PATTERNS) == len(LLM_ENDPOINT_PATTERNS)

    def test_openai_pattern_present(self):
        raw = " ".join(LLM_ENDPOINT_PATTERNS)
        assert "openai" in raw.lower()

    def test_anthropic_pattern_present(self):
        raw = " ".join(LLM_ENDPOINT_PATTERNS)
        assert "anthropic" in raw.lower()
