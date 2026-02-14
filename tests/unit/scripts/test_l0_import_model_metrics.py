"""Regression tests for L0-targeting upward import metric.

Validates that count_l0_targeting_edges correctly identifies edges
whose imported module resides in L0_routing, using synthetic data only.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure ops_scripts is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ops_scripts.general.l0_import_model import count_l0_targeting_edges


class TestCountL0TargetingEdges:
    """Synthetic tests for the L0-targeting counting function."""

    def test_edge_targeting_l0_routing_is_counted(self):
        """An edge whose target_module starts with agentic_core.L0_routing MUST be counted."""
        edges = [
            {
                "source": "agentic_core/L5_safety/utils/guard_util.py",
                "source_layer": "L5_safety",
                "source_rank": 5,
                "target_module": "agentic_core.L0_routing.scripts.full_agent_discovery",
                "target_layer": "L0_routing",
                "target_rank": 0,
                "lineno": 15,
            },
        ]
        assert count_l0_targeting_edges(edges) == 1

    def test_edge_not_targeting_l0_is_not_counted(self):
        """An edge targeting a non-L0 module MUST NOT be counted."""
        edges = [
            {
                "source": "agentic_core/L6_observability/dashboards/core/config.py",
                "source_layer": "L6_observability",
                "source_rank": 6,
                "target_module": "agentic_core.L5_safety.config.structure_blueprint_config",
                "target_layer": "L5_safety",
                "target_rank": 5,
                "lineno": 13,
            },
        ]
        assert count_l0_targeting_edges(edges) == 0

    def test_mixed_edges_counts_only_l0(self):
        """Only edges targeting L0_routing are counted in a mixed set."""
        edges = [
            {
                "source": "agentic_core/L5_safety/utils/a.py",
                "target_module": "agentic_core.L0_routing.types.v15_p2_types",
                "lineno": 10,
            },
            {
                "source": "agentic_core/L6_observability/utils/b.py",
                "target_module": "agentic_core.L5_safety.enforcement.registry",
                "lineno": 20,
            },
            {
                "source": "agentic_core/L6_observability/utils/c.py",
                "target_module": "agentic_core.L0_routing.scripts.execute_ssot",
                "lineno": 30,
            },
        ]
        assert count_l0_targeting_edges(edges) == 2

    def test_empty_edges_returns_zero(self):
        """An empty edge list returns 0."""
        assert count_l0_targeting_edges([]) == 0

    def test_target_layer_field_is_irrelevant(self):
        """The count must NOT depend on the target_layer field value.

        This is the regression guard: even if target_layer is wrong or missing,
        the count must be correct because it checks target_module.
        """
        edges = [
            {
                "source": "agentic_core/L5_safety/utils/x.py",
                "target_module": "agentic_core.L0_routing.scripts.discovery",
                "target_layer": "WRONG_VALUE",
                "lineno": 1,
            },
            {
                "source": "agentic_core/L5_safety/utils/y.py",
                "target_module": "agentic_core.L0_routing.types.contract",
                "lineno": 2,
            },
        ]
        assert count_l0_targeting_edges(edges) == 2

    def test_partial_prefix_not_counted(self):
        """A module like agentic_core.L0_routingXYZ must NOT match."""
        edges = [
            {
                "source": "agentic_core/L5_safety/utils/z.py",
                "target_module": "agentic_core.L0_routingXYZ.fake",
                "lineno": 1,
            },
        ]
        assert count_l0_targeting_edges(edges) == 0
