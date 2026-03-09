"""
Wave 1.4 Gate Test: Every ACTIVE agent in discovery must define heal().

Reads the freshest discovery JSON and asserts that no ACTIVE agent
is missing ``heal`` from its ``detected_methods`` list.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

DISCOVERY_JSON = (
    Path(__file__).resolve().parents[2] / "docs" / "reports" / "plans" / "v54_discovery_wave14.json"
)


@pytest.fixture(scope="module")
def active_agents() -> list[dict]:
    if not DISCOVERY_JSON.exists():
        pytest.fail(f"Discovery artifact not found: {DISCOVERY_JSON}")
    data = json.loads(DISCOVERY_JSON.read_text(encoding="utf-8"))
    return [a for a in data["agents"] if a.get("status") == "ACTIVE"]


class TestAllActiveAgentsHaveHeal:
    """Every ACTIVE agent must define heal()."""

    def test_no_active_agent_missing_heal(self, active_agents):
        missing = [a["identity"] for a in active_agents if "heal" not in a.get("detected_methods", [])]
        assert missing == [], f"ACTIVE agents missing heal(): {missing}"

    def test_active_agent_count_nonzero(self, active_agents):
        assert len(active_agents) > 0, "Discovery returned zero ACTIVE agents"
