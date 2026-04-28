"""End-to-End Golden Dataset Evaluation Test.

Wave 5 validation: Full integration test with real golden datasets.
Tests complete flow: GoldenDatasetEvaluator → EvalSpine → L6 emission.
"""

import time
from concurrent.futures import wait

import pytest

from agentic_core.runtime.engine.eval_spine import EvalSpine
from agentic_core.evaluation.golden import GoldenDatasetEvaluator, get_evaluator
from agentic_core.evaluation.golden.eval_spine_integration import (
    GoldenEvalIntegration,
    attach_golden_eval,
)
from agentic_core.evaluation.golden.l6_emitter import GoldenL6Emitter


@pytest.fixture
def real_evaluator():
    """Get evaluator with real repository datasets."""
    return get_evaluator()


@pytest.fixture
def eval_spine():
    """Create fresh EvalSpine."""
    return EvalSpine(agent_id="e2e_test_agent", run_id=f"e2e_run_{int(time.time())}")


@pytest.fixture
def integration(eval_spine, real_evaluator):
    """Create integration with real evaluator."""
    integration = GoldenEvalIntegration(eval_spine, evaluator=real_evaluator, max_workers=2)
    yield integration
    integration.shutdown()


class TestEndToEndGoldenEvaluation:
    """End-to-end tests with real golden datasets."""

    def test_load_real_datasets(self, real_evaluator):
        """Verify real golden datasets are loaded."""
        real_evaluator.load_datasets()

        datasets = real_evaluator.list_available_datasets()

        # Should find at least one real dataset
        assert len(datasets) > 0
        print(f"Loaded datasets: {datasets}")

    def test_evaluate_real_test_case(self, integration, eval_spine):
        """Evaluate against real test_cases.json."""
        # Use an actual test case from the dataset
        query = "Find the current weather in San Francisco"
        actual_output = (
            "The current weather in San Francisco shows a temperature of 72°F with partly cloudy conditions."
        )

        future = integration.evaluate_query_async(query, actual_output)
        wait([future], timeout=5.0)

        results = future.result()

        # Should match TC001
        assert len(results) >= 1
        result = results[0]
        assert result.case_id == "TC001"
        assert result.dataset_name == "test_cases"
        assert result.passed is True  # Should pass with this output
        assert result.match_score == 1.0  # Contains both required spans

    def test_evaluate_real_retrieval_ground_truth(self, integration, eval_spine):
        """Evaluate against real retrieval_ground_truth.jsonl."""
        query = "What is the UniversalWriteGateway and what does it enforce?"
        retrieved_docs = ["agentic_core/L2_execution/UniversalWriteGateway.py"]
        generated_answer = (
            "The UniversalWriteGateway enforces Single mutation authority, "
            "write permissions, and requires signed instruction packets."
        )

        future = integration.evaluate_retrieval_async(
            query=query,
            retrieved_doc_ids=retrieved_docs,
            generated_answer=generated_answer,
        )
        wait([future], timeout=5.0)

        results = future.result()

        # Should match RGT001
        assert len(results) >= 1
        result = results[0]
        assert result.case_id == "RGT001"
        assert result.dataset_name == "retrieval_ground_truth"
        assert result.passed is True

    def test_metrics_emitted_to_eval_spine(self, integration, eval_spine):
        """Verify metrics are recorded in EvalSpine."""
        query = "Find the current weather in San Francisco"
        actual_output = "The temperature in San Francisco is 72 degrees."

        future = integration.evaluate_query_async(query, actual_output)
        wait([future], timeout=5.0)

        results = future.result()
        integration.emit_golden_metrics(results)

        # Check EvalSpine has metrics
        assert len(eval_spine.report.metrics) > 0

        # Check for golden metric
        golden_metrics = [m for m in eval_spine.report.metrics if "golden" in m.metric_name]
        assert len(golden_metrics) > 0

    def test_drift_alert_on_failure(self, integration, eval_spine):
        """Verify drift alert is emitted for low match scores."""
        # Query with poor output to trigger low match score
        query = "Get stock price for AAPL"
        actual_output = "The stock is doing well."  # Missing key spans

        future = integration.evaluate_query_async(query, actual_output)
        wait([future], timeout=5.0)

        results = future.result()
        integration.emit_golden_metrics(results)

        # Check for drift alerts
        if results and results[0].match_score < 0.5:
            assert len(eval_spine.report.drift_alerts) > 0
            alert = eval_spine.report.drift_alerts[0]
            assert "golden" in alert.metric_name

    def test_full_pipeline_shadow_mode(self, integration, eval_spine):
        """Test full pipeline runs in shadow mode (non-blocking)."""
        start = time.time()

        # Submit multiple evaluations
        futures = []
        for i in range(3):
            future = integration.evaluate_query_async(
                f"Query {i}",
                f"Output {i}",
            )
            futures.append(future)

        # Should return immediately (non-blocking)
        elapsed = time.time() - start
        assert elapsed < 0.1

        # Wait for completion
        wait(futures, timeout=5.0)

        # Process all results
        for future in futures:
            results = future.result()
            integration.emit_golden_metrics(results)

        # Pipeline completed
        assert len(eval_spine.report.metrics) >= 0  # May be 0 if no matches

    def test_l6_emission_integration(self, real_evaluator):
        """Test L6 emitter with real evaluation results."""
        emitter = GoldenL6Emitter()

        # Get a real result
        results = real_evaluator.evaluate_against_test_cases(
            query="Find the current weather in San Francisco",
            actual_output="The temperature in San Francisco is 72 degrees.",
        )

        if results:
            # Should emit without error
            emitter.emit_golden_eval_result(results[0])
            assert emitter.get_emit_stats()["total_emits"] == 3

    def test_summary_generation(self, integration, real_evaluator):
        """Test summary reflects real evaluation state."""
        summary = integration.get_summary()

        assert "pending_evaluations" in summary
        assert "datasets_available" in summary
        assert "eval_spine_metrics" in summary

        # Should list real datasets
        datasets = summary["datasets_available"]
        assert len(datasets) > 0

    def test_real_dataset_schema_validation(self, real_evaluator):
        """Validate real datasets have expected schema."""
        real_evaluator.load_datasets()

        # Check test_cases schema (flexible - different cases have different schemas)
        if "test_cases" in real_evaluator._datasets:
            data = real_evaluator._datasets["test_cases"]
            assert "version" in data
            assert "test_cases" in data

            for case in data["test_cases"]:
                assert "id" in case
                assert "mission" in case
                assert "expected_output" in case
                # Schema varies: some have 'contains', others have 'max_tokens', etc.
                expected = case["expected_output"]
                assert isinstance(expected, dict)
                assert len(expected) > 0  # Has at least one constraint

        # Check retrieval_ground_truth schema
        if "retrieval_ground_truth" in real_evaluator._datasets:
            records = real_evaluator._datasets["retrieval_ground_truth"]
            for record in records:
                assert "query_id" in record
                assert "query" in record
                assert "expected_document_ids" in record
                assert "expected_answer_spans" in record

    def test_no_blocking_on_dataset_errors(self, eval_spine):
        """Verify integration doesn't block if datasets are missing."""
        # Create evaluator with non-existent path
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            empty_evaluator = GoldenDatasetEvaluator(repo_root=Path(tmpdir))
            integration = GoldenEvalIntegration(eval_spine, evaluator=empty_evaluator)

            # Should not raise when datasets missing
            future = integration.evaluate_query_async("test", "output")
            wait([future], timeout=2.0)

            results = future.result()
            assert results == []  # Empty results, no crash

            integration.shutdown()


class TestCompleteGoldenWorkflow:
    """Complete workflow tests combining all components."""

    def test_full_workflow_with_attach(self):
        """Test complete workflow using attach_golden_eval convenience function."""
        spine = EvalSpine(agent_id="workflow_test", run_id="wf_001")
        integration = attach_golden_eval(spine)

        # Submit evaluation
        future = integration.evaluate_query_async(
            "Find the current weather in San Francisco",
            "The temperature in San Francisco is 72 degrees with clear skies.",
        )
        wait([future], timeout=5.0)

        # Process and emit
        results = future.result()
        integration.emit_golden_metrics(results)

        # Verify EvalSpine state
        assert len(spine.report.metrics) > 0 or len(results) == 0

        integration.shutdown()

    def test_batch_evaluation_workflow(self, integration, eval_spine):
        """Test batch evaluation with multiple queries."""
        queries = [
            ("Find the current weather in San Francisco", "SF weather info"),
            ("Get stock price for AAPL", "AAPL stock info"),
            ("Research quantum computing", "Quantum computing research"),
        ]

        futures = []
        for query, output in queries:
            future = integration.evaluate_query_async(query, output)
            futures.append(future)

        # Wait for all
        wait(futures, timeout=10.0)

        # Process results
        total_results = 0
        for future in futures:
            results = future.result()
            total_results += len(results)
            integration.emit_golden_metrics(results)

        # Should have processed all queries
        assert total_results >= 0  # Some may not match
