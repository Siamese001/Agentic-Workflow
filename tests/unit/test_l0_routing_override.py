"""
Invariant test: L0_routing LAYER_OVERRIDES must encode Model A
(Core Logic & Routing + Control-Plane Core).

This test prevents semantic drift back to ambiguous "maintenance/tooling"
language.  Phase 1 of L0 Routing Scope Hardening.
"""

from __future__ import annotations

import re

from agentic_core.L5_safety.config.structure_blueprint import LAYER_OVERRIDES


class TestL0RoutingOverrideModelA:
    """Assert LAYER_OVERRIDES['L0_routing'] encodes Model A exactly."""

    # ------------------------------------------------------------------
    # Fixture: extract once
    # ------------------------------------------------------------------
    @staticmethod
    def _l0() -> dict:
        return dict(LAYER_OVERRIDES["L0_routing"])

    # ------------------------------------------------------------------
    # 1. Key existence
    # ------------------------------------------------------------------
    def test_layer_overrides_has_l0_routing(self):
        assert "L0_routing" in LAYER_OVERRIDES

    def test_purpose_key_exists(self):
        assert "purpose" in self._l0()

    def test_forbidden_capabilities_key_exists(self):
        assert "forbidden_capabilities" in self._l0()

    # ------------------------------------------------------------------
    # 2. Purpose: Model A positive assertions
    # ------------------------------------------------------------------
    def test_purpose_contains_core_logic_and_routing(self):
        purpose = self._l0()["purpose"]
        assert "Core Logic & Routing" in purpose

    def test_purpose_contains_control_plane_core(self):
        purpose = self._l0()["purpose"]
        assert "Control-Plane Core" in purpose

    def test_purpose_contains_at_least_one_control_plane_term(self):
        purpose = self._l0()["purpose"].lower()
        control_plane_terms = {"guardian", "ssot", "boot"}
        matches = {t for t in control_plane_terms if t in purpose}
        assert matches, (
            f"purpose must mention at least one of {control_plane_terms}; got: {self._l0()['purpose']!r}"
        )

    # ------------------------------------------------------------------
    # 3. Purpose: Model A negative assertions (no drift)
    # ------------------------------------------------------------------
    def test_purpose_does_not_contain_developer_tooling(self):
        purpose = self._l0()["purpose"]
        assert not re.search(r"developer\s+tooling", purpose, re.IGNORECASE), (
            "purpose must not contain 'developer tooling'"
        )

    def test_purpose_does_not_contain_fix_it(self):
        purpose = self._l0()["purpose"]
        assert not re.search(r"fix[\-\s]?it", purpose, re.IGNORECASE), "purpose must not contain 'fix-it'"

    # ------------------------------------------------------------------
    # 4. Forbidden capabilities: exact expected set
    # ------------------------------------------------------------------
    def test_forbidden_capabilities_exact(self):
        expected = {
            "debate",
            "synthesis",
            "complex_reasoning",
            "multi_agent_coordination",
        }
        actual = set(self._l0()["forbidden_capabilities"])
        assert actual == expected, f"forbidden_capabilities drift: expected {expected}, got {actual}"

    # ------------------------------------------------------------------
    # 5. Routing rules (schema-supported, added in Phase 1)
    # ------------------------------------------------------------------
    def test_routing_rules_key_exists(self):
        assert "routing_rules" in self._l0(), "L0_routing must declare routing_rules"

    def test_routing_rules_has_enforcement_patterns(self):
        rules = self._l0()["routing_rules"]
        enforcement_targets = [k for k, v in rules.items() if v == "enforcement"]
        assert len(enforcement_targets) >= 1, "routing_rules must route at least one pattern to enforcement"
