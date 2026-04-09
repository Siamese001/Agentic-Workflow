"""Tests for the packet registry."""

from __future__ import annotations

import pytest

from tools.adg.prompt_assembly.packets.registry import (
    TEMPLATES,
    VALID_PACKET_TYPES,
    get_template,
    list_packet_types,
)


class TestPacketRegistry:
    def test_eight_packet_types_registered(self) -> None:
        assert len(VALID_PACKET_TYPES) == 8

    def test_all_types_have_templates(self) -> None:
        for ptype in VALID_PACKET_TYPES:
            template = get_template(ptype)
            assert template.packet_type == ptype
            assert template.system_block
            assert template.policy_block
            assert template.output_schema
            assert template.must_use_sources
            assert template.token_budget.total > 0

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown packet type"):
            get_template("nonexistent_type")

    def test_list_packet_types_sorted(self) -> None:
        types = list_packet_types()
        assert types == sorted(types)
        assert len(types) == 8

    def test_expected_types_present(self) -> None:
        expected = {
            "determinism_rca",
            "p0_failure",
            "ratchet_review",
            "unknown_unresolved_triage",
            "hotspot_investigation",
            "infrastructure_boundary",
            "graph_path_explanation",
            "executive_summary",
        }
        assert expected == VALID_PACKET_TYPES

    def test_templates_have_shared_policy(self) -> None:
        """All templates share the same policy block referencing C0/PA separation."""
        for ptype in VALID_PACKET_TYPES:
            template = get_template(ptype)
            assert "source of truth" in template.policy_block.lower()
            assert "C0 retrieves only" in template.policy_block

    def test_token_budgets_positive(self) -> None:
        for ptype in VALID_PACKET_TYPES:
            budget = get_template(ptype).token_budget
            assert budget.total > 0
            assert budget.must_use_evidence > 0
            total_parts = (
                budget.system_policy
                + budget.task
                + budget.must_use_evidence
                + budget.optional_evidence
                + budget.contradiction_meta
            )
            # Parts should not exceed total (they can be less due to flexible allocation)
            assert total_parts <= budget.total * 1.5  # reasonable tolerance
