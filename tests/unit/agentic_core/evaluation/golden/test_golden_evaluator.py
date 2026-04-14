"""Tests for GoldenDatasetEvaluator.

Per windsurf rules: test-first discipline, deterministic tests, no skips.
"""

import json
from pathlib import Path

import pytest

from agentic_core.evaluation.golden import (
    GoldenDatasetEvaluator,
    GoldenEvalResult,
    get_evaluator,
)


@pytest.fixture
def sample_test_cases(tmp_path: Path) -> Path:
    """Create a temporary test_cases.json."""
    data = {
        "version": "1.0.0",
        "test_cases": [
            {
                "id": "TC001",
                "name": "Simple Retrieval",
                "category": "happy_path",
                "mission": "Find the weather in San Francisco",
                "expected_output": {
                    "type": "weather_report",
                    "contains": ["temperature", "San Francisco"],
                    "min_length": 50,
                },
                "quality_criteria": {"accuracy": 0.9},
            },
            {
                "id": "TC002",
                "name": "Missing Content",
                "category": "edge_case",
                "mission": "Get stock price for AAPL",
                "expected_output": {
                    "type": "stock_info",
                    "contains": ["AAPL", "price", "market cap"],
                    "min_length": 30,
                },
                "quality_criteria": {"accuracy": 0.8},
            },
        ],
    }
    path = tmp_path / "test_cases.json"
    with open(path, "w") as f:
        json.dump(data, f)
    return path


@pytest.fixture
def sample_retrieval_ground_truth(tmp_path: Path) -> Path:
    """Create a temporary retrieval_ground_truth.jsonl."""
    records = [
        {
            "query_id": "RGT001",
            "query": "What is the UniversalWriteGateway?",
            "expected_document_ids": ["doc_001"],
            "expected_answer_spans": ["Single mutation authority", "write permissions"],
            "expected_top_k_rank": 1,
            "minimum_recall_at_3": 1.0,
        },
    ]
    path = tmp_path / "retrieval_ground_truth.jsonl"
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    return path


class TestGoldenDatasetEvaluator:
    """Test GoldenDatasetEvaluator core functionality."""

    def test_initialization(self, tmp_path: Path):
        """Test evaluator can be initialized with custom repo root."""
        evaluator = GoldenDatasetEvaluator(repo_root=tmp_path)
        assert evaluator.repo_root == tmp_path
        assert not evaluator._loaded

    def test_detect_repo_root(self):
        """Test repo root detection from module location."""
        evaluator = GoldenDatasetEvaluator()
        root = evaluator._detect_repo_root()
        assert root.exists()
        assert (root / "agentic_core").exists()

    def test_load_json_dataset(self, sample_test_cases: Path):
        """Test loading JSON dataset."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        # Override paths for testing
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        evaluator.load_datasets()

        assert "test_cases" in evaluator._datasets
        data = evaluator._datasets["test_cases"]
        assert data["version"] == "1.0.0"
        assert len(data["test_cases"]) == 2

    def test_load_jsonl_dataset(self, sample_retrieval_ground_truth: Path):
        """Test loading JSONL dataset."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_retrieval_ground_truth.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"retrieval_ground_truth": (Path("retrieval_ground_truth.jsonl"),)}

        evaluator.load_datasets()

        assert "retrieval_ground_truth" in evaluator._datasets
        records = evaluator._datasets["retrieval_ground_truth"]
        assert len(records) == 1
        assert records[0]["query_id"] == "RGT001"

    def test_evaluate_against_test_cases_pass(self, sample_test_cases: Path):
        """Test evaluation when output matches expected content."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        results = evaluator.evaluate_against_test_cases(
            query="Find the weather in San Francisco",
            actual_output="The temperature in San Francisco is 72 degrees.",
        )

        assert len(results) == 1
        result = results[0]
        assert result.case_id == "TC001"
        assert result.passed is True
        assert result.match_score == 1.0
        assert "temperature" in result.actual_contains
        assert "San Francisco" in result.actual_contains
        assert result.missing_spans == []

    def test_evaluate_against_test_cases_fail(self, sample_test_cases: Path):
        """Test evaluation when output missing expected content."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        results = evaluator.evaluate_against_test_cases(
            query="Get stock price for AAPL",
            actual_output="The AAPL stock price is $150.",  # Contains AAPL and price, missing market cap
        )

        assert len(results) == 1
        result = results[0]
        assert result.case_id == "TC002"
        assert result.passed is False  # Missing "market cap"
        assert result.match_score == 2 / 3  # 2 of 3 spans found
        assert "market cap" in result.missing_spans

    def test_evaluate_no_matching_query(self, sample_test_cases: Path):
        """Test evaluation when query doesn't match any test case."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        results = evaluator.evaluate_against_test_cases(
            query="Non-existent query",
            actual_output="Some output",
        )

        assert len(results) == 0

    def test_evaluate_retrieval_ground_truth(self, sample_retrieval_ground_truth: Path):
        """Test retrieval evaluation against ground truth."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_retrieval_ground_truth.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"retrieval_ground_truth": (Path("retrieval_ground_truth.jsonl"),)}

        results = evaluator.evaluate_retrieval_ground_truth(
            query="What is the UniversalWriteGateway?",
            retrieved_doc_ids=["doc_001", "doc_002"],
            generated_answer="The UniversalWriteGateway provides Single mutation authority and write permissions.",
        )

        assert len(results) == 1
        result = results[0]
        assert result.case_id == "RGT001"
        assert result.passed is True
        assert result.match_score == 1.0
        assert "Single mutation authority" in result.actual_contains
        assert "write permissions" in result.actual_contains

    def test_evaluate_retrieval_partial_match(self, sample_retrieval_ground_truth: Path):
        """Test retrieval with partial document match."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_retrieval_ground_truth.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"retrieval_ground_truth": (Path("retrieval_ground_truth.jsonl"),)}

        results = evaluator.evaluate_retrieval_ground_truth(
            query="What is the UniversalWriteGateway?",
            retrieved_doc_ids=["doc_999"],  # Wrong doc
            generated_answer="The UniversalWriteGateway enforces write permissions.",  # Missing one span
        )

        assert len(results) == 1
        result = results[0]
        assert result.passed is False
        # Match score = (0 doc recall + 0.5 span match) / 2 = 0.25
        assert result.match_score == 0.25
        assert "Single mutation authority" in result.missing_spans

    def test_get_dataset_summary(self, sample_test_cases: Path):
        """Test getting dataset summary."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        summary = evaluator.get_dataset_summary("test_cases")

        assert summary is not None
        assert summary.dataset_name == "test_cases"
        assert summary.total_cases == 2
        assert summary.pass_rate == 0.0  # No evaluations run yet

    def test_list_available_datasets(self, sample_test_cases: Path):
        """Test listing available datasets."""
        evaluator = GoldenDatasetEvaluator(repo_root=sample_test_cases.parent)
        evaluator.GOLDEN_DATASET_PATHS = {"test_cases": (Path("test_cases.json"),)}

        datasets = evaluator.list_available_datasets()

        assert "test_cases" in datasets

    def test_singleton_get_evaluator(self):
        """Test singleton pattern for get_evaluator."""
        e1 = get_evaluator()
        e2 = get_evaluator()
        assert e1 is e2

    def test_golden_eval_result_to_dict(self):
        """Test GoldenEvalResult serialization."""
        result = GoldenEvalResult(
            case_id="TC001",
            dataset_name="test_cases",
            query="Test query",
            passed=True,
            match_score=0.95,
            expected_contains=["a", "b"],
            actual_contains=["a"],
            missing_spans=["b"],
            extra_spans=[],
            eval_duration_ms=10.5,
        )

        d = result.to_dict()
        assert d["case_id"] == "TC001"
        assert d["passed"] is True
        assert d["match_score"] == 0.95
        assert d["eval_duration_ms"] == 10.5


class TestGoldenDatasetEvaluatorIntegration:
    """Integration tests with real repository datasets."""

    def test_load_real_datasets(self):
        """Test loading real golden datasets from repository."""
        evaluator = GoldenDatasetEvaluator()
        evaluator.load_datasets()

        datasets = evaluator.list_available_datasets()

        # Should find at least some of the canonical datasets
        assert len(datasets) > 0

    def test_real_test_cases_evaluation(self):
        """Test evaluation against real test_cases.json."""
        evaluator = GoldenDatasetEvaluator()

        # Use first test case mission
        results = evaluator.evaluate_against_test_cases(
            query="Find the current weather in San Francisco",
            actual_output="The current weather in San Francisco shows a temperature of 65°F with partly cloudy conditions.",
        )

        # Must match TC001 - assert results exist
        assert len(results) >= 1, "Expected at least one matching test case result"
        result = results[0]
        assert result.case_id == "TC001"
        assert result.dataset_name == "test_cases"
        assert result.passed is True, "Expected test case to pass with provided output"

    def test_real_retrieval_ground_truth(self):
        """Test evaluation against real retrieval_ground_truth.jsonl."""
        evaluator = GoldenDatasetEvaluator()

        results = evaluator.evaluate_retrieval_ground_truth(
            query="What is the UniversalWriteGateway and what does it enforce?",
            retrieved_doc_ids=["agentic_core/L2_execution/UniversalWriteGateway.py"],
            generated_answer="The UniversalWriteGateway enforces Single mutation authority, write permissions, and requires signed instruction packets.",
        )

        # Must match RGT001 - assert results exist
        assert len(results) >= 1, "Expected at least one matching retrieval ground truth result"
        result = results[0]
        assert result.case_id == "RGT001"
        assert result.passed is True, "Expected retrieval evaluation to pass"
