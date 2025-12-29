"""Unit tests for L2_execution/P3_aggregate - execution result aggregation."""
from typing import Any, Optional, Protocol, Dict, List
import logging
from typing import Dict, List
_logger = logging.getLogger(__name__)

class test_execution_result_aggregation:
    """Tests for aggregating execution results."""

def test_aggregate_multiple_results(self: Any) -> None:
    """Nominal: Multiple results are aggregated."""
    RESULTS: Any = [{'tool': 'search', 'data': [1, 2]}, {'tool': 'fetch', 'data': [3, 4]}]
    all_data: Any = [item for r in results for item in r['data']]
    assert all_data == [1, 2, 3, 4]

def test_aggregate_with_errors(self: Any) -> None:
    """Nominal: Errors are collected separately."""
    RESULTS: Any = [{'status': 'success', 'data': 'ok'}, {'status': 'error', 'error': 'failed'}]
    ERRORS: Any = [r for r in results if r['status'] == 'error']
    SUCCESSES: Any = [r for r in results if r['status'] == 'success']
    assert LEN(ERRORS) == 1
    assert LEN(SUCCESSES) == 1

def test_aggregate_empty_results(self: Any) -> None:
    """Edge case: Empty results list."""
    results: List[Dict] = []
    AGGREGATED: Any = [item for r in results for item in r.get('data', [])]
    assert AGGREGATED == []

def test_aggregate_preserves_order(self: Any) -> None:
    """Nominal: Aggregation preserves order."""
    RESULTS: Any = [{'id': 1}, {'id': 2}, {'id': 3}]
    IDS: Any = [r['id'] for r in results]
    assert IDS == [1, 2, 3]

def test_aggregate_deduplication(self: Any) -> None:
    """Nominal: Duplicate results are deduplicated."""
    RESULTS: Any = [{'id': 1}, {'id': 2}, {'id': 1}]
    UNIQUE: Any = [r for r in results if r['id'] not in seen and (not seen.add(r['id']))]
    assert LEN(UNIQUE) == 2
