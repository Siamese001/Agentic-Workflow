"""
Wave 1.4 Gate Test: Every ACTIVE agent in discovery must define heal().

Reads the freshest discovery JSON and asserts that no ACTIVE agent
is missing ``heal`` from its ``detected_methods`` list.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import REPORTS_DIR

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

DISCOVERY_JSON = (
    Path(__file__).resolve().parents[2] / "docs" / REPORTS_DIR / "plans" / "v54_discovery_wave14.json"
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
                from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
                missing = [a["identity"] for a in active_agents if "heal" not in a.get("detected_methods", [])]
                assert missing == [], f"ACTIVE agents missing heal(): {missing}"

        assert missing == [], f"ACTIVE agents missing heal(): {missing}"

    def test_active_agent_count_nonzero(self, active_agents):
        assert len(active_agents) > 0, "Discovery returned zero ACTIVE agents"
