"""
Wave 1.2 Evidence Test: Discovery sovereign classification is MRO-based.

Asserts:
1. ``is_sovereign`` is derived from ``"SovereignBaseAgent" in mro_chain``.
2. ``DiscoveredAgent`` is NOT emitted as an ACTIVE agent.
3. Known non-sovereign agents remain correctly classified.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_OUTPUT = PROJECT_ROOT / "docs" / "reports" / "plans" / "v54_discovery_wave12.json"


@pytest.fixture(scope="module")
def discovery_agents() -> list[dict]:
    """Load the v5.4 discovery output produced by forensic_discovery_prep."""
    if not DISCOVERY_OUTPUT.exists():
        pytest.skip(f"Discovery output not found: {DISCOVERY_OUTPUT}")
    with open(DISCOVERY_OUTPUT, encoding="utf-8") as f:
        data = json.load(f)
    return data["agents"]


class TestSovereignClassification:
    """Sovereign flag must be consistent with mro_chain content."""

    def test_sovereign_iff_sovereign_base_in_mro(self, discovery_agents):
        """Every agent's is_sovereign must equal 'SovereignBaseAgent' in mro_chain."""
        mismatches = []
        for agent in discovery_agents:
            mro = agent.get("mro_chain", [])
            expected = "SovereignBaseAgent" in mro
            actual = agent.get("is_sovereign", False)
            if actual != expected:
                mismatches.append(
                    f"{agent['identity']}: is_sovereign={actual}, "
                    f"'SovereignBaseAgent' in mro={expected}, mro={mro[:5]}",
                )
        assert not mismatches, "Sovereign flag / MRO mismatches:\n" + "\n".join(mismatches)

    def test_non_sovereign_agents_are_expected(self, discovery_agents):
        """Only DuplicateCodeDetectorAgent and ReportLocationAgent should be non-sovereign."""
        non_sov = sorted(a["identity"] for a in discovery_agents if not a.get("is_sovereign"))
        assert non_sov == ["DuplicateCodeDetectorAgent", "ReportLocationAgent"]


class TestPhantomAgentRemoval:
    """DiscoveredAgent must not appear as an ACTIVE discovery agent."""

    def test_discovered_agent_not_in_active(self, discovery_agents):
        active_ids = {a["identity"] for a in discovery_agents}
        assert "DiscoveredAgent" not in active_ids, "Phantom DiscoveredAgent still emitted as ACTIVE"
