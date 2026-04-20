"""Golden Dataset Evaluator - Shadow-mode evaluation against fixed baselines.

Implements G16 gap closure: wiring golden datasets into runtime evaluation flow.
- Loads immutable golden datasets (versioned JSON)
- Evaluates agent outputs against expected values
- Runs in shadow mode (non-blocking, no L2 routing impact)
- Emits metrics to L6 observability
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class GoldenEvalResult:
    """Result of evaluating against a single golden test case."""

    case_id: str
    dataset_name: str
    query: str
    passed: bool
    match_score: float  # 0.0-1.0
    expected_contains: list[str]
    actual_contains: list[str]
    missing_spans: list[str]
    extra_spans: list[str]
    eval_duration_ms: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "dataset_name": self.dataset_name,
            "query": self.query,
            "passed": self.passed,
            "match_score": self.match_score,
            "expected_contains": self.expected_contains,
            "actual_contains": self.actual_contains,
            "missing_spans": self.missing_spans,
            "extra_spans": self.extra_spans,
            "eval_duration_ms": self.eval_duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class GoldenDatasetSummary:
    """Aggregated summary of golden dataset evaluation."""

    dataset_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    avg_match_score: float
    eval_duration_ms: float
    results: list[GoldenEvalResult]
    timestamp: float = field(default_factory=time.time)

    @property
    def pass_rate(self) -> float:
        return self.passed_cases / self.total_cases if self.total_cases > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "avg_match_score": self.avg_match_score,
            "eval_duration_ms": self.eval_duration_ms,
            "timestamp": self.timestamp,
            "results": [r.to_dict() for r in self.results],
        }


class GoldenDatasetEvaluator:
    """Evaluates agent outputs against golden datasets in shadow mode.

    Design constraints:
    - Read-only access to golden datasets (immutable)
    - Shadow mode only (no L2 routing impact)
    - Non-blocking evaluation
    - L6 observability emission
    """

    # Canonical golden dataset paths. Each entry is ordered by preference.
    GOLDEN_DATASET_PATHS = {
        "test_cases": (Path("data/golden_state/datasets/test_cases.json"),),
        "retrieval_ground_truth": (Path("data/golden_state/datasets/retrieval_ground_truth.jsonl"),),
        "classification": (
            Path("agentic_core/evaluation/datasets/classification_eval_set.json"),
            Path("evaluation/datasets/classification_eval_set.json"),
            Path("datasets/classification_eval_set.json"),
        ),
        "rag": (
            Path("agentic_core/evaluation/datasets/rag_eval_set.json"),
            Path("evaluation/datasets/rag_eval_set.json"),
            Path("datasets/rag_eval_set.json"),
        ),
        "groundedness": (
            Path("agentic_core/evaluation/datasets/groundedness_eval_set.json"),
            Path("evaluation/datasets/groundedness_eval_set.json"),
            Path("datasets/groundedness_eval_set.json"),
        ),
    }

    def __init__(self, repo_root: Path | None = None):
        """Initialize evaluator.

        Args:
            repo_root: Repository root path (default: detected from __file__)
        """
        self.repo_root = repo_root or self._detect_repo_root()
        self._datasets: dict[str, Any] = {}
        self._loaded = False

    def _detect_repo_root(self) -> Path:
        """Detect repository root from module location."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "agentic_core/evaluation/datasets").exists():
                return parent
        return current.parent.parent.parent.parent

    def _resolve_dataset_path(self, candidates: tuple[Path, ...]) -> Path | None:
        """Resolve the first available dataset path from an ordered candidate list."""
        for rel_path in candidates:
            full_path = self.repo_root / rel_path
            if full_path.exists():
                return full_path
        return None

    def load_datasets(self) -> None:
        """Load all golden datasets into memory (immutable)."""
        if self._loaded:
            return

        for name, candidate_paths in self.GOLDEN_DATASET_PATHS.items():  # progress_bar: load golden datasets
            full_path = self._resolve_dataset_path(candidate_paths)
            if full_path is None:
                Logger.warning("Golden dataset not found for %s in %s", name, self.repo_root)
                continue

            try:
                if full_path.suffix == ".jsonl":
                    data: Any = self._load_jsonl(full_path)
                else:
                    data = self._load_json(full_path)
                self._datasets[name] = data
                record_count = (
                    len(data)
                    if isinstance(data, list)
                    else len(data.get("test_cases", data.get("examples", [])))
                )
                Logger.info("Loaded golden dataset: %s (%s records)", name, record_count)
            except (OSError, ValueError, json.JSONDecodeError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                Logger.error("Failed to load %s from %s: %s", name, full_path, exc)

        self._loaded = True

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON dataset."""
        with path.open(encoding="utf-8") as handle:
            result: dict[str, Any] = json.load(handle)
            return result

    def _load_jsonl(self, path: Path) -> list[dict]:
        """Load JSONL dataset."""
        records: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
        return records

    def evaluate_against_test_cases(
        self,
        query: str,
        actual_output: str,
        actual_actions: list[dict] | None = None,
    ) -> list[GoldenEvalResult]:
        """Evaluate a query/output against golden test cases.

        Args:
            query: The input query/mission
            actual_output: The actual output produced
            actual_actions: Optional list of actual actions taken

        Returns:
            List of evaluation results (one per matching test case)
        """
        if not self._loaded:
            self.load_datasets()

        results = []
        dataset = self._datasets.get("test_cases", {})
        test_cases = dataset.get("test_cases", [])

        for case in test_cases:
            # Match by query similarity (exact match for now)
            if case.get("mission") != query:
                continue

            start = time.perf_counter()
            result = self._evaluate_single_case(case, actual_output, actual_actions)
            result.eval_duration_ms = (time.perf_counter() - start) * 1000
            results.append(result)

        return results

    def _evaluate_single_case(
        self,
        case: dict,
        actual_output: str,
        actual_actions: list[dict] | None,  # Reserved for future action validation
    ) -> GoldenEvalResult:
        """Evaluate a single test case."""
        expected = case.get("expected_output", {})
        expected_contains = expected.get("contains", [])

        # Check contains matches
        actual_contains = []
        missing_spans = []
        for span in expected_contains:
            if span.lower() in actual_output.lower():
                actual_contains.append(span)
            else:
                missing_spans.append(span)

        # Calculate match score
        if expected_contains:
            match_score = len(actual_contains) / len(expected_contains)
        else:
            match_score = 1.0 if actual_output else 0.0

        passed = match_score >= case.get("quality_criteria", {}).get("accuracy", 0.8)

        return GoldenEvalResult(
            case_id=case.get("id", "unknown"),
            dataset_name="test_cases",
            query=case.get("mission", ""),
            passed=passed,
            match_score=match_score,
            expected_contains=expected_contains,
            actual_contains=actual_contains,
            missing_spans=missing_spans,
            extra_spans=[],  # Not tracked for now
            eval_duration_ms=0.0,  # Set by caller
        )

    def evaluate_retrieval_ground_truth(
        self,
        query: str,
        retrieved_doc_ids: list[str],
        generated_answer: str,
    ) -> list[GoldenEvalResult]:
        """Evaluate retrieval against ground truth.

        Args:
            query: The search query
            retrieved_doc_ids: List of document IDs retrieved
            generated_answer: The answer generated from retrieved docs

        Returns:
            List of evaluation results
        """
        if not self._loaded:
            self.load_datasets()

        results = []
        records = self._datasets.get("retrieval_ground_truth", [])

        for record in records:
            if record.get("query") != query:
                continue

            start = time.perf_counter()
            result = self._evaluate_retrieval_record(record, retrieved_doc_ids, generated_answer)
            result.eval_duration_ms = (time.perf_counter() - start) * 1000
            results.append(result)

        return results

    def _evaluate_retrieval_record(
        self,
        record: dict,
        retrieved_doc_ids: list[str],
        generated_answer: str,
    ) -> GoldenEvalResult:
        """Evaluate a single retrieval ground truth record."""
        expected_docs = record.get("expected_document_ids", [])
        expected_spans = record.get("expected_answer_spans", [])

        # Check document recall
        retrieved_set = set(retrieved_doc_ids)
        expected_set = set(expected_docs)
        docs_found = len(retrieved_set & expected_set)
        doc_recall = docs_found / len(expected_set) if expected_set else 1.0

        # Check answer span containment
        spans_found = []
        missing_spans = []
        for span in expected_spans:
            if span.lower() in generated_answer.lower():
                spans_found.append(span)
            else:
                missing_spans.append(span)

        span_score = len(spans_found) / len(expected_spans) if expected_spans else 1.0

        # Combined score: 50% doc recall, 50% span match
        match_score = (doc_recall + span_score) / 2

        min_recall = record.get("minimum_recall_at_3", 1.0)
        passed = doc_recall >= min_recall and span_score >= 0.5

        return GoldenEvalResult(
            case_id=record.get("query_id", "unknown"),
            dataset_name="retrieval_ground_truth",
            query=record.get("query", ""),
            passed=passed,
            match_score=match_score,
            expected_contains=expected_spans,
            actual_contains=spans_found,
            missing_spans=missing_spans,
            extra_spans=[],
            eval_duration_ms=0.0,
        )

    def get_dataset_summary(self, dataset_name: str) -> GoldenDatasetSummary | None:
        """Get summary of a loaded dataset."""
        if not self._loaded:
            self.load_datasets()

        if dataset_name not in self._datasets:
            return None

        data = self._datasets[dataset_name]
        if isinstance(data, dict):
            cases = data.get("test_cases", data.get("examples", []))
        else:
            cases = data

        return GoldenDatasetSummary(
            dataset_name=dataset_name,
            total_cases=len(cases),
            passed_cases=0,  # Would need full evaluation
            failed_cases=0,
            avg_match_score=0.0,
            eval_duration_ms=0.0,
            results=[],
        )

    def list_available_datasets(self) -> list[str]:
        """List available golden dataset names."""
        if not self._loaded:
            self.load_datasets()
        return list(self._datasets.keys())


# Module-level singleton for convenience
_evaluator: GoldenDatasetEvaluator | None = None


def get_evaluator(repo_root: Path | None = None) -> GoldenDatasetEvaluator:
    """Get or create singleton evaluator."""
    global _evaluator
    if _evaluator is None:
        _evaluator = GoldenDatasetEvaluator(repo_root)
    return _evaluator
