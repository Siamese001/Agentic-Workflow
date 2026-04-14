"""Invariant tests for L0 routing scope hardening."""

from __future__ import annotations

import re

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def l0_override():
    blueprint_module = pytest.importorskip("agentic_core.L5_safety.config.structure_blueprint")
    layer_overrides = blueprint_module.LAYER_OVERRIDES
    assert "L0_routing" in layer_overrides
    return dict(layer_overrides["L0_routing"])


class TestL0RoutingOverrideModelA:
    def test_purpose_key_exists(self, l0_override):
        assert "purpose" in l0_override

    def test_forbidden_capabilities_key_exists(self, l0_override):
        assert "forbidden_capabilities" in l0_override

    @pytest.mark.parametrize(
        "fragment",
        [
            "Core Logic & Routing",
            "Control-Plane Core",
        ],
    )
    def test_purpose_contains_required_phrases(self, l0_override, fragment):
        assert fragment in l0_override["purpose"]

    def test_purpose_contains_at_least_one_control_plane_term(self, l0_override):
        purpose = l0_override["purpose"].lower()
        control_plane_terms = {"guardian", "ssot", "boot"}
        matches = {term for term in control_plane_terms if term in purpose}

        assert matches, (
            f"purpose must mention at least one of {control_plane_terms}; got: {l0_override['purpose']!r}"
        )

    @pytest.mark.parametrize(
        "pattern",
        [
            r"developer\s+tooling",
            r"fix[\-\s]?it",
        ],
    )
    def test_purpose_does_not_contain_drift_terms(self, l0_override, pattern):
        assert not re.search(pattern, l0_override["purpose"], re.IGNORECASE)

    def test_forbidden_capabilities_exact(self, l0_override):
        expected = {
            "debate",
            "synthesis",
            "complex_reasoning",
            "multi_agent_coordination",
        }

        assert set(l0_override["forbidden_capabilities"]) == expected

    def test_routing_rules_key_exists(self, l0_override):
        assert "routing_rules" in l0_override

    def test_routing_rules_has_enforcement_patterns(self, l0_override):
        enforcement_targets = [
            key for key, value in l0_override["routing_rules"].items() if value == "enforcement"
        ]

        assert enforcement_targets, "routing_rules must route at least one pattern to enforcement"
