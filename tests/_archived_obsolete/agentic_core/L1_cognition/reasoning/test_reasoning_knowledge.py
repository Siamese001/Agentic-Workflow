"""Tests for reasoning_knowledge - knowledge graph for reasoning."""
import pytest
from agentic_core.L1_cognition.reasoning.reasoning_knowledge import ReasoningKnowledge


class TestReasoningKnowledge:
    def test_init(self):
        k = ReasoningKnowledge()
        assert k is not None

    def test_add_fact(self):
        k = ReasoningKnowledge()
        k.add_fact(subject="x", predicate="is", obj="y")
        assert k.fact_count() == 1

    def test_query_facts(self):
        k = ReasoningKnowledge()
        k.add_fact("x", "is", "y")
        results = k.query(subject="x")
        assert len(results) == 1

    def test_remove_fact(self):
        k = ReasoningKnowledge()
        k.add_fact("x", "is", "y")
        k.remove_fact("x", "is", "y")
        assert k.fact_count() == 0

    def test_infer(self):
        k = ReasoningKnowledge()
        k.add_fact("x", "is", "y")
        k.add_fact("y", "is", "z")
        inferred = k.infer_transitive("x", "is")
        assert "z" in inferred

    def test_serialize(self):
        k = ReasoningKnowledge()
        k.add_fact("x", "is", "y")
        data = k.to_dict()
        assert isinstance(data, dict)

    def test_clear(self):
        k = ReasoningKnowledge()
        k.add_fact("x", "is", "y")
        k.clear()
        assert k.fact_count() == 0
