"""Tests for BlastRadius - change impact analysis."""
import pytest
from unittest.mock import Mock
from agentic_core.L4_state.enforcement.blast_radius import BlastRadius


class TestBlastRadius:
    def test_init(self):
        br = BlastRadius()
        assert br is not None

    def test_compute_radius_for_node(self):
        br = BlastRadius()
        graph = Mock()
        graph.fanin.return_value = ["a", "b", "c"]
        br.set_graph(graph)
        radius = br.compute("target_node")
        assert len(radius) == 3

    def test_compute_radius_empty(self):
        br = BlastRadius()
        graph = Mock()
        graph.fanin.return_value = []
        br.set_graph(graph)
        assert br.compute("isolated") == []

    def test_compute_with_depth_limit(self):
        br = BlastRadius(max_depth=2)
        graph = Mock()
        graph.fanin.return_value = ["a"]
        br.set_graph(graph)
        radius = br.compute("target", max_depth=2)
        assert isinstance(radius, list)

    def test_classify_severity(self):
        br = BlastRadius()
        severity = br.classify_severity(impacted_count=100)
        assert severity in ("low", "medium", "high", "critical")

    def test_classify_severity_low(self):
        br = BlastRadius()
        severity = br.classify_severity(impacted_count=1)
        assert severity == "low"

    def test_get_summary(self):
        br = BlastRadius()
        graph = Mock()
        graph.fanin.return_value = ["a", "b"]
        br.set_graph(graph)
        summary = br.get_summary("node")
        assert "impacted_count" in summary
