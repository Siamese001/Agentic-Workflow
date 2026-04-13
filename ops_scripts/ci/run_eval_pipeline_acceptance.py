"""
ops_scripts/ci/run_eval_pipeline_acceptance.py

CI acceptance runner for the evaluation pipeline test suite.

Usage:
    python ops_scripts/ci/run_eval_pipeline_acceptance.py [--verbose]

Exit codes:
    0 — all eval_pipeline tests pass
    1 — one or more eval_pipeline tests fail

Known pre-existing failures excluded from acceptance (unrelated to eval pipeline):
    tests/unit/agentic_core/L6_observability/utils/evaluation/test_learning_signal_enrichment.py
      - test_statistics_tracking
      - test_low_quality_filtering
      - test_trend_analysis_degrading
    These are failures in LearningSignalEnricher, not in the canonical eval pipeline.
    Do NOT include these in the eval_pipeline suite.

Eval pipeline test targets (all carry @pytest.mark.eval_pipeline):
    tests/unit/agentic_core/L6_observability/utils/evaluation/test_pipeline_integration.py
    tests/unit/agentic_core/L6_observability/utils/evaluation/test_async_future_run_slice.py
    tests/unit/agentic_core/L6_observability/utils/evaluation/test_promotion_approval_slice.py
    tests/unit/agentic_core/L6_observability/utils/evaluation/test_queue_health.py
    tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_eval_bridge_adoption.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

_EVAL_PIPELINE_TESTS = [
    "tests/unit/agentic_core/L6_observability/utils/evaluation/test_pipeline_integration.py",
    "tests/unit/agentic_core/L6_observability/utils/evaluation/test_async_future_run_slice.py",
    "tests/unit/agentic_core/L6_observability/utils/evaluation/test_promotion_approval_slice.py",
    "tests/unit/agentic_core/L6_observability/utils/evaluation/test_queue_health.py",
    "tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_eval_bridge_adoption.py",
]

_KNOWN_EXCLUDED = [
    "tests/unit/agentic_core/L6_observability/utils/evaluation/"
    "test_learning_signal_enrichment.py::TestLearningSignalEnricher::test_statistics_tracking",
    "tests/unit/agentic_core/L6_observability/utils/evaluation/"
    "test_learning_signal_enrichment.py::TestLearningSignalEnricher::test_low_quality_filtering",
    "tests/unit/agentic_core/L6_observability/utils/evaluation/"
    "test_learning_signal_enrichment.py::TestLearningSignalEnricher::test_trend_analysis_degrading",
]


def main(verbose: bool = False) -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *_EVAL_PIPELINE_TESTS,
        "--tb=short",
        "-q" if not verbose else "-v",
        "--strict-markers",
        "--timeout=60",
    ]

    print("=" * 70)
    print("Eval pipeline acceptance run")
    print(f"Targets: {len(_EVAL_PIPELINE_TESTS)} test files")
    print(f"Known excluded (pre-existing, unrelated): {len(_KNOWN_EXCLUDED)}")
    print("=" * 70)

    try:
        result = subprocess.run(
            cmd,
            shell=False,
            timeout=180,
            check=False,
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"\n[FAIL] Eval pipeline acceptance timed out after {exc.timeout}s.")
        if exc.stdout:
            print(exc.stdout)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"\n[FAIL] Could not launch pytest: {exc}", file=sys.stderr)
        return 2

    if verbose or result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")

    if result.returncode == 0:
        print("\n[PASS] All eval_pipeline tests passed.")
    else:
        print("\n[FAIL] One or more eval_pipeline tests failed.")
        print("NOTE: The following are KNOWN pre-existing failures excluded from acceptance:")
        for path in _KNOWN_EXCLUDED:
            print(f"  {path}")

    return result.returncode


if __name__ == "__main__":
    _cli_verbose = "--verbose" in sys.argv or "-v" in sys.argv
    sys.exit(main(verbose=_cli_verbose))
