"""
tests/unit/agentic_core/L6_observability/evaluation/test_evaluation_provenance.py

Unit tests for Wave 1.5: Evaluation Provenance Capture

Tests:
- Provenance capture and storage
- Provenance queries by various filters
- Trace and evaluator indexing
- FIFO enforcement
- Statistics tracking
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.evaluation_provenance import (
    EvaluationProvenance,
    EvaluationProvenanceStore,
    ProvenanceQuery,
    get_provenance_store,
    reset_provenance_store,
)


class TestEvaluationProvenance:
    """Test EvaluationProvenance dataclass."""

    def test_provenance_creation(self):
        """Test creating a provenance record."""
        provenance = EvaluationProvenance(
            provenance_id="prov-001",
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="FaithfulnessEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="faithfulness",
            timestamp_utc=1700000000.0,
            input_data={"query": "test query"},
            output_data={"answer": "test answer"},
            context_data={"context": ["doc1", "doc2"]},
            score=0.85,
            verdict="PASS",
            confidence=0.95,
            metadata={"source": "test"},
        )

        assert provenance.provenance_id == "prov-001"
        assert provenance.evaluation_id == "eval-001"
        assert provenance.trace_id == "trace-001"
        assert provenance.evaluator_name == "FaithfulnessEvaluator"
        assert provenance.score == 0.85
        assert provenance.verdict == "PASS"


class TestEvaluationProvenanceStore:
    """Test suite for EvaluationProvenanceStore."""

    def test_capture_provenance(self):
        """Test capturing provenance."""
        store = EvaluationProvenanceStore()

        provenance = store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="FaithfulnessEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="faithfulness",
            input_data={"query": "test"},
            output_data={"answer": "test"},
            context_data={"context": []},
            score=0.85,
            verdict="PASS",
        )

        assert isinstance(provenance, EvaluationProvenance)
        assert provenance.evaluation_id == "eval-001"
        assert provenance.trace_id == "trace-001"
        assert provenance.score == 0.85

    def test_get_provenance_by_id(self):
        """Test retrieving provenance by ID."""
        store = EvaluationProvenanceStore()

        provenance = store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="FaithfulnessEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="faithfulness",
            input_data={},
            output_data={},
            context_data={},
            score=0.85,
            verdict="PASS",
        )

        retrieved = store.get_provenance(provenance.provenance_id)
        assert retrieved is not None
        assert retrieved.provenance_id == provenance.provenance_id

    def test_get_trace_provenance(self):
        """Test retrieving all provenance for a trace."""
        store = EvaluationProvenanceStore()

        # Add multiple evaluations for same trace
        for i in range(3):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id="trace-001",
                evaluator_name=f"Evaluator{i}",
                evaluator_version="1.0.0",
                evaluation_type="test",
                input_data={},
                output_data={},
                context_data={},
                score=0.8 + i * 0.05,
                verdict="PASS",
            )

        trace_provenance = store.get_trace_provenance("trace-001")
        assert len(trace_provenance) == 3

    def test_get_evaluator_provenance(self):
        """Test retrieving all provenance for an evaluator."""
        store = EvaluationProvenanceStore()

        # Add multiple evaluations from same evaluator
        for i in range(3):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id=f"trace-{i:03d}",
                evaluator_name="FaithfulnessEvaluator",
                evaluator_version="1.0.0",
                evaluation_type="faithfulness",
                input_data={},
                output_data={},
                context_data={},
                score=0.8 + i * 0.05,
                verdict="PASS",
            )

        evaluator_provenance = store.get_evaluator_provenance("FaithfulnessEvaluator")
        assert len(evaluator_provenance) == 3

    def test_query_by_evaluation_type(self):
        """Test querying provenance by evaluation type."""
        store = EvaluationProvenanceStore()

        # Add different evaluation types
        store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="FaithfulnessEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="faithfulness",
            input_data={},
            output_data={},
            context_data={},
            score=0.85,
            verdict="PASS",
        )

        store.capture_provenance(
            evaluation_id="eval-002",
            trace_id="trace-002",
            evaluator_name="GroundednessEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="groundedness",
            input_data={},
            output_data={},
            context_data={},
            score=0.90,
            verdict="PASS",
        )

        query = ProvenanceQuery(evaluation_type="faithfulness")
        results = store.query_provenance(query)

        assert len(results) == 1
        assert results[0].evaluation_type == "faithfulness"

    def test_query_by_score_range(self):
        """Test querying provenance by score range."""
        store = EvaluationProvenanceStore()

        # Add evaluations with different scores
        for i in range(5):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id=f"trace-{i:03d}",
                evaluator_name="TestEvaluator",
                evaluator_version="1.0.0",
                evaluation_type="test",
                input_data={},
                output_data={},
                context_data={},
                score=0.5 + i * 0.1,
                verdict="PASS",
            )

        query = ProvenanceQuery(min_score=0.7, max_score=0.9)
        results = store.query_provenance(query)

        assert len(results) == 3  # Scores 0.7, 0.8, 0.9
        assert all(0.7 <= r.score <= 0.9 for r in results)

    def test_query_by_time_range(self):
        """Test querying provenance by time range."""
        store = EvaluationProvenanceStore()
        current_time = time.time()

        # Add evaluations at different times
        store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="TestEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="test",
            input_data={},
            output_data={},
            context_data={},
            score=0.85,
            verdict="PASS",
        )

        time.sleep(0.01)  # Small delay

        store.capture_provenance(
            evaluation_id="eval-002",
            trace_id="trace-002",
            evaluator_name="TestEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="test",
            input_data={},
            output_data={},
            context_data={},
            score=0.90,
            verdict="PASS",
        )

        # Query for records after current_time
        query = ProvenanceQuery(start_time_utc=current_time)
        results = store.query_provenance(query)

        assert len(results) == 2

    def test_query_limit(self):
        """Test query limit enforcement."""
        store = EvaluationProvenanceStore()

        # Add 10 evaluations
        for i in range(10):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id=f"trace-{i:03d}",
                evaluator_name="TestEvaluator",
                evaluator_version="1.0.0",
                evaluation_type="test",
                input_data={},
                output_data={},
                context_data={},
                score=0.85,
                verdict="PASS",
            )

        query = ProvenanceQuery(limit=5)
        results = store.query_provenance(query)

        assert len(results) == 5

    def test_fifo_enforcement(self):
        """Test FIFO enforcement of max records."""
        store = EvaluationProvenanceStore(max_records=5)

        # Add 10 records
        for i in range(10):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id=f"trace-{i:03d}",
                evaluator_name="TestEvaluator",
                evaluator_version="1.0.0",
                evaluation_type="test",
                input_data={},
                output_data={},
                context_data={},
                score=0.85,
                verdict="PASS",
            )

        stats = store.get_stats()
        assert stats["total_records"] == 5  # Only last 5 kept

    def test_statistics(self):
        """Test provenance store statistics."""
        store = EvaluationProvenanceStore()

        # Add evaluations from different evaluators and traces
        store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="Evaluator1",
            evaluator_version="1.0.0",
            evaluation_type="test",
            input_data={},
            output_data={},
            context_data={},
            score=0.85,
            verdict="PASS",
        )

        store.capture_provenance(
            evaluation_id="eval-002",
            trace_id="trace-002",
            evaluator_name="Evaluator2",
            evaluator_version="1.0.0",
            evaluation_type="test",
            input_data={},
            output_data={},
            context_data={},
            score=0.90,
            verdict="PASS",
        )

        stats = store.get_stats()
        assert stats["total_records"] == 2
        assert stats["unique_traces"] == 2
        assert stats["unique_evaluators"] == 2
        assert "Evaluator1" in stats["evaluators"]
        assert "Evaluator2" in stats["evaluators"]

    def test_clear(self):
        """Test clearing all provenance records."""
        store = EvaluationProvenanceStore()

        store.capture_provenance(
            evaluation_id="eval-001",
            trace_id="trace-001",
            evaluator_name="TestEvaluator",
            evaluator_version="1.0.0",
            evaluation_type="test",
            input_data={},
            output_data={},
            context_data={},
            score=0.85,
            verdict="PASS",
        )

        store.clear()

        stats = store.get_stats()
        assert stats["total_records"] == 0


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test provenance store singleton pattern."""
        reset_provenance_store()

        store1 = get_provenance_store()
        store2 = get_provenance_store()

        assert store1 is store2

        reset_provenance_store()
        store3 = get_provenance_store()

        assert store3 is not store1


class TestIntegration:
    """Integration tests for provenance capture."""

    def test_full_evaluation_provenance_workflow(self):
        """Test complete provenance capture workflow."""
        store = EvaluationProvenanceStore()

        # Capture provenance for multiple evaluations
        evaluations = [
            ("FaithfulnessEvaluator", "faithfulness", 0.85),
            ("GroundednessEvaluator", "groundedness", 0.90),
            ("RelevancyEvaluator", "relevancy", 0.88),
        ]

        trace_id = "trace-001"
        for i, (evaluator, eval_type, score) in enumerate(evaluations):
            store.capture_provenance(
                evaluation_id=f"eval-{i:03d}",
                trace_id=trace_id,
                evaluator_name=evaluator,
                evaluator_version="1.0.0",
                evaluation_type=eval_type,
                input_data={"query": "test query"},
                output_data={"answer": "test answer"},
                context_data={"context": ["doc1", "doc2"]},
                score=score,
                verdict="PASS",
                confidence=0.95,
                metadata={"source": "integration_test"},
            )

        # Query all provenance for trace
        trace_provenance = store.get_trace_provenance(trace_id)
        assert len(trace_provenance) == 3

        # Query by score range
        query = ProvenanceQuery(min_score=0.88)
        high_score_provenance = store.query_provenance(query)
        assert len(high_score_provenance) == 2  # 0.90 and 0.88

        # Verify metadata preservation
        for prov in trace_provenance:
            assert prov.input_data["query"] == "test query"
            assert prov.metadata["source"] == "integration_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
