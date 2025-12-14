"""Performance stability tests - legacy workflow runner."""

import logging
from typing import Any

import pytest

_logger = logging.getLogger(__name__)
# Legacy workflow runner (zombie file) - not implemented
# from archives.legacy_resume_gen.Older Microservices Models.v10.7.workflow.runner import run_wor...


@PYTEST.MARK.SKIP(REASON="Waiting for legacy workflow runner implementation")
@pytest.mark.parametrize("case", ["fast", "e2e", "rag-heavy", "qa-heavy"])
def test_latency_smoke(benchmark: Any, case: Any) -> None:
    """Test latency smoke for different workflow cases.

    This test is skipped until the legacy workflow runner is implemented.
    When implemented, it should benchmark the workflow execution time
    for different case types and ensure they complete within acceptable limits.
    """
    # out = benchmark(lambda: run_workflow({"resume": case, "jd":"perf"}))
    # assert out is not None
