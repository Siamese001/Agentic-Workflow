"""ADG-driven tests for L0_routing/legacy_agent_name_allowlist.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.legacy_agent_name_allowlist import LEGACY_AGENT_NAME_ALLOWLIST


class TestLegacyAgentNameAllowlist:
    def test_is_dict(self):
        assert isinstance(LEGACY_AGENT_NAME_ALLOWLIST, dict)

    def test_non_empty(self):
        assert len(LEGACY_AGENT_NAME_ALLOWLIST) >= 1

    def test_values_are_strings(self):
        for key, val in LEGACY_AGENT_NAME_ALLOWLIST.items():
            assert isinstance(key, str)
            assert isinstance(val, str)

    def test_values_have_justification(self):
        for val in LEGACY_AGENT_NAME_ALLOWLIST.values():
            assert len(val) >= 12, f"Justification too short: {val!r}"
