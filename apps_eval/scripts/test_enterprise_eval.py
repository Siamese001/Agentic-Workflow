"""
E2E Test Suite for apps_eval.enterprise.

Tests the full enterprise evaluation pipeline with realistic scenarios.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add repo to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from apps_eval.reasoning.enterprise_eval_orchestrator import (
    EnterpriseEvalOrchestrator,
    EnterpriseEvalRequest,
    run_enterprise_evaluation,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_repo_signals(result: object) -> None:
    repo_signals = getattr(result, "repo_signals", {})
    _assert(bool(repo_signals), "repo_signals missing from enterprise result")

    adg = repo_signals.get("adg", {})
    tests = repo_signals.get("tests", {})
    ci = repo_signals.get("ci", {})
    governance = repo_signals.get("governance", {})

    _assert(adg.get("available") is True, "ADG signal unavailable")
    _assert(ci.get("workflow_count", 0) > 0, "No workflow definitions discovered")
    _assert(
        tests.get("inventory_available") or tests.get("surface_available"),
        "Neither test inventory nor test surface artifact is available",
    )
    _assert(
        governance.get("denominator_baseline_available") is True,
        "Governance denominator baseline not detected",
    )


async def test_basic_evaluation():
    """Test basic evaluation flow."""
    print("\n" + "="*60)
    print("TEST 1: Basic Enterprise Evaluation")
    print("="*60)

    suite_ids = [
        "routing_enforcement",
        "determinism_contracts",
        "orchestration_hop",
    ]

    criteria_items = [
        {
            "criteria_id": "C001",
            "text": "All routing decisions must validate policy hashes within 10ms",
            "dimension": "governance",
            "weight": 2.5,
        },
        {
            "criteria_id": "C002",
            "text": "Determinism contracts must detect time-dependent calls with 100% accuracy",
            "dimension": "determinism",
            "weight": 3.0,
        },
        {
            "criteria_id": "C003",
            "text": "Multi-hop orchestration must complete within 5 seconds",
            "dimension": "latency",
            "weight": 1.5,
        },
    ]

    result = await run_enterprise_evaluation(
        suite_ids=suite_ids,
        criteria_items=criteria_items,
        output_dir="eval/test_output",
    )

    _assert(result.report_path != "", "Report path is empty")
    _assert(result.manifest_path != "", "Manifest path is empty")
    _assert(result.evaluation_results.get("agents_executed", 0) > 0, "No agents executed")
    _assert_repo_signals(result)

    print("\n✅ Evaluation Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Report Path: {result.report_path}")

    print("\n📊 Results:")
    print(f"   Components Decomposed: {result.test_plan.get('total_components', 0)}")
    print(f"   Agents Executed: {result.evaluation_results.get('agents_executed', 0)}")
    print(f"   Overall Score: {result.evaluation_results.get('overall_score', 0):.0%}")

    print("\n🛡️ Validation:")
    print(f"   Validation Passed: {result.validation_result.get('passed', False)}")
    print(f"   Gates Passed: {result.gate_result.get('gates_passed', False)}")
    print(f"   Quality Score: {result.validation_result.get('quality_score', 0):.0%}")

    return result


async def test_with_trend_analysis():
    """Test evaluation with trend analysis."""
    print("\n" + "="*60)
    print("TEST 2: Evaluation with Trend Analysis")
    print("="*60)

    orchestrator = EnterpriseEvalOrchestrator()

    # Index some historical evaluations first
    for i in range(3):
        mock_result = {
            "overall_score": 0.75 + i * 0.05,
            "dimension_scores": {
                "correctness": 0.80 + i * 0.02,
                "determinism": 0.85,
                "governance": 0.70 + i * 0.03,
            },
        }
        orchestrator.retrieval_engine.index_evaluation(
            result=mock_result,
            suite_ids=["routing_enforcement"],
            trace_id=f"historical_{i}",
        )

    request = EnterpriseEvalRequest(
        suite_ids=["routing_enforcement", "determinism_contracts"],
        criteria_items=[
            {
                "criteria_id": "C001",
                "text": "Policy hash validation must complete within SLA",
                "dimension": "governance",
                "weight": 2.0,
            },
        ],
        enable_retrieval=True,
        output_dir="eval/test_output",
    )

    result = await orchestrator.process(request)

    _assert(len(result.similar_evaluations) >= 1, "Expected at least one similar evaluation")
    _assert_repo_signals(result)

    print("\n✅ Evaluation with Trends Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Similar Evaluations Found: {len(result.similar_evaluations)}")
    print(f"   Trends Analyzed: {len(result.trend_analysis)}")

    if result.trend_analysis:
        print("\n📈 Trends:")
        for dim, trend in result.trend_analysis.items():
            print(f"   {dim}: {trend['direction']} (slope: {trend['slope']:.3f})")

    return result


async def test_full_pipeline():
    """Test the full enterprise pipeline with all features."""
    print("\n" + "="*60)
    print("TEST 3: Full Enterprise Pipeline")
    print("="*60)

    orchestrator = EnterpriseEvalOrchestrator()

    request = EnterpriseEvalRequest(
        suite_ids=[
            "routing_enforcement",
            "determinism_contracts",
            "orchestration_hop",
            "output_contracts",
            "exec_brief_generation",
        ],
        criteria_items=[
            {
                "criteria_id": "C001",
                "text": "L0 routing must enforce policy hashes with sub-10ms latency",
                "dimension": "governance",
                "weight": 2.5,
            },
            {
                "criteria_id": "C002",
                "text": "Determinism checks must detect non-deterministic calls (time, random, uuid)",
                "dimension": "determinism",
                "weight": 3.0,
            },
            {
                "criteria_id": "C003",
                "text": "Multi-hop orchestration must handle gate failures gracefully",
                "dimension": "correctness",
                "weight": 3.0,
            },
            {
                "criteria_id": "C004",
                "text": "Output contracts must be signed and tamper-evident",
                "dimension": "correctness",
                "weight": 2.0,
            },
            {
                "criteria_id": "C005",
                "text": "Executive brief generation must produce persona-targeted outputs",
                "dimension": "output_richness",
                "weight": 1.0,
            },
        ],
        enable_retrieval=True,
        enable_validation=True,
        output_dir="eval/test_output",
    )

    result = await orchestrator.process(request)

    print("\n📋 Execution Log:")
    for entry in result.execution_log:
        status_icon = "✅" if entry["status"] == "complete" else "⏳" if entry["status"] == "start" else "⚠️"
        print(f"   {status_icon} {entry['step']}: {entry['status']}")
        if entry.get("details"):
            for key, value in entry["details"].items():
                print(f"      - {key}: {value}")

    print("\n📁 Generated Artifacts:")
    print(f"   Report: {result.report_path}")
    print(f"   Manifest: {result.manifest_path}")

    return result


async def test_regression_detection():
    """Test regression detection capabilities."""
    print("\n" + "="*60)
    print("TEST 4: Regression Detection")
    print("="*60)

    orchestrator = EnterpriseEvalOrchestrator()

    # Create baseline
    baseline = {"overall_score": 0.85, "dimension_scores": {"correctness": 0.90}}

    # Index some past evaluations
    for score in [0.82, 0.84, 0.83, 0.85]:
        orchestrator.retrieval_engine.index_evaluation(
            result={"overall_score": score, "dimension_scores": {"correctness": score}},
            suite_ids=["determinism_contracts"],
            trace_id=f"past_{score}",
        )

    # Current evaluation with lower score (simulating regression)
    current = {"overall_score": 0.78, "dimension_scores": {"correctness": 0.75}}

    signals = orchestrator.retrieval_engine.detect_regression_signals(
        current_result=current,
        threshold=0.05,
    )

    _assert(len(signals) >= 1, "Expected regression signals for reduced score sample")

    print("\n✅ Regression Analysis Complete!")
    print(f"   Baseline Score: {baseline['overall_score']:.0%}")
    print(f"   Current Score: {current['overall_score']:.0%}")
    print(f"   Delta: {current['overall_score'] - baseline['overall_score']:.0%}")

    if signals:
        print("\n⚠️  Regression Signals Detected:")
        for sig in signals:
            print(f"   - {sig['type']}: {sig['dimension']} ({sig['severity']})")
    else:
        print("\n✅ No regression signals detected")

    return {"signals": signals, "regression_detected": len(signals) > 0}


async def main():
    """Run all E2E tests."""
    print("\n" + "🚀 "*30)
    print("ENTERPRISE EVALUATION SYSTEM - E2E TEST SUITE")
    print("🚀 "*30)

    results = []
    failures: list[str] = []

    try:
        # Test 1: Basic evaluation
        result1 = await test_basic_evaluation()
        results.append(("Basic Evaluation", result1))

        # Test 2: Trend analysis
        result2 = await test_with_trend_analysis()
        results.append(("Trend Analysis", result2))

        # Test 3: Full pipeline
        result3 = await test_full_pipeline()
        results.append(("Full Pipeline", result3))

        # Test 4: Regression detection
        result4 = await test_regression_detection()
        results.append(("Regression Detection", result4))

    except Exception as exc:
        print(f"\n❌ Test failed: {exc}")
        import traceback
        traceback.print_exc()
        failures.append(str(exc))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, result in results:
        if hasattr(result, 'status'):
            status = "✅ PASS" if result.status == "complete" else "⚠️ PARTIAL" if result.status == "partial" else "❌ FAIL"
            print(f"{status}: {name}")
            print(f"      Trace: {result.trace_id[:16]}")
            print(f"      Artifacts: {getattr(result, 'report_path', 'N/A')}")
        else:
            status = "✅ PASS" if result.get('regression_detected') else "✅ PASS"
            print(f"{status}: {name}")

    if failures:
        raise SystemExit(1)

    print("\n✨ All tests completed!")
    print("\nTo view generated reports, check: eval/test_output/")


if __name__ == "__main__":
    asyncio.run(main())
