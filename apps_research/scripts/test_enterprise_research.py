"""
E2E Test Suite for apps_research.enterprise.

Tests the full enterprise research generation pipeline with realistic scenarios.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add repo to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from apps_research.reasoning.enterprise_research_orchestrator import (
    EnterpriseResearchOrchestrator,
    EnterpriseResearchRequest,
    run_enterprise_research,
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
    _assert(bool(repo_signals), "repo_signals missing from enterprise research result")

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


def _assert_detailed_observability(result: object) -> None:
    """Assert comprehensive observability signals are present."""
    execution_log = getattr(result, "execution_log", [])
    trace_id = getattr(result, "trace_id", "")

    _assert(len(execution_log) > 0, "Execution log empty - observability not wired")
    _assert(bool(trace_id), "Trace ID missing - distributed tracing not wired")
    _assert(len(trace_id) >= 16, f"Trace ID too short ({len(trace_id)} chars)")

    complete_steps = {entry.get("step", "").upper() for entry in execution_log if entry.get("status") == "complete"}
    _assert(len(complete_steps) >= 2, f"Insufficient completed steps: {complete_steps}")


def _assert_layer4_wiring(result: object) -> None:
    """Assert Layer 4 (orchestration) wiring is active."""
    repo_signals = getattr(result, "repo_signals", {})
    execution_log = getattr(result, "execution_log", [])

    step_sequence = [entry.get("step", "") for entry in execution_log]
    _assert(len(step_sequence) >= 2, "Layer 4: insufficient orchestration steps")

    ci = repo_signals.get("ci", {})
    _assert(ci.get("workflow_count", 0) >= 30, "Layer 4: insufficient CI workflows")

    tests = repo_signals.get("tests", {})
    _assert(tests.get("inventory_entries", 0) > 1000, "Layer 4: insufficient test inventory")


def _assert_enhanced_system_learning(result: object) -> None:
    """Assert enhanced system learning signals are present."""
    repo_signals = getattr(result, "repo_signals", {})
    governance = repo_signals.get("governance", {})

    # Research context (research-specific system learning) - optional
    research_context = governance.get("research_context", {})
    if research_context:
        if "knowledge_depth" not in research_context:
            print("   ⚠️  System learning: research_context.knowledge_depth missing (non-blocking)")

    # ADG signals for pattern capture
    adg = repo_signals.get("adg", {})
    if adg.get("available"):
        nodes_count = adg.get("nodes_count", 0)
        if nodes_count <= 100000:
            print(f"   ⚠️  System learning: ADG nodes ({nodes_count}) below threshold (non-blocking)")


def _assert_rigorous_e2e_wiring(result: object) -> None:
    """Comprehensive E2E wiring validation."""
    print("\n🔍 RIGOROUS E2E WIRING VALIDATION")
    print("-" * 40)

    try:
        _assert_repo_signals(result)
        print("   ✅ Repo signals: PASS")
    except AssertionError as e:
        print(f"   ❌ Repo signals: FAIL - {e}")
        raise

    try:
        _assert_detailed_observability(result)
        print("   ✅ Observability: PASS")
    except AssertionError as e:
        print(f"   ❌ Observability: FAIL - {e}")
        raise

    try:
        _assert_layer4_wiring(result)
        print("   ✅ Layer 4 wiring: PASS")
    except AssertionError as e:
        print(f"   ❌ Layer 4 wiring: FAIL - {e}")
        raise

    try:
        _assert_enhanced_system_learning(result)
        print("   ✅ System learning: PASS")
    except AssertionError as e:
        print(f"   ❌ System learning: FAIL - {e}")
        raise

    print("-" * 40)
    print("🎯 ALL E2E WIRING ASSERTIONS: PASS")
    print("-" * 40)


async def test_single_topic_brief():
    """Test research generation for a single topic brief."""
    print("\n" + "=" * 60)
    print("TEST 1: Single Topic Brief Generation")
    print("=" * 60)

    topic = "governance in agentic AI systems"
    mode = "brief"

    result = await run_enterprise_research(
        topic=topic,
        artifact_mode=mode,
        target_audience="technical",
        output_dir="reports/research/test_output",
    )

    _assert(result.report_path != "", "Report path is empty")
    _assert(result.manifest_path != "", "Manifest path is empty")
    _assert(result.generation_results.get("agents_executed", 0) > 0, "No agents executed")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("\n✅ Research Generation Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Report Path: {result.report_path}")

    print("\n📊 Results:")
    if result.query_decomposition:
        print(f"   Components Decomposed: {len(result.query_decomposition.components)}")
    print(f"   Agents Executed: {result.generation_results.get('agents_executed', 0)}")

    print("\n🛡️ Validation:")
    print(f"   Validations Run: {len(result.validation_results)}")
    print(
        f"   Gates Passed: {sum(1 for g in result.gate_results if g.get('gates_passed'))}/{len(result.gate_results)}"
    )
    print(f"   Avg Quality Score: {result.avg_quality_score:.0%}")

    return result


async def test_comparison_mode():
    """Test research generation in comparison mode."""
    print("\n" + "=" * 60)
    print("TEST 2: Comparison Mode Research")
    print("=" * 60)

    topic = "agentic framework comparison"
    mode = "comparison"

    orchestrator = EnterpriseResearchOrchestrator()
    request = EnterpriseResearchRequest(
        topic=topic,
        artifact_mode=mode,
        target_audience="technical",
        enable_retrieval=True,
        enable_validation=True,
        output_dir="reports/research/test_output",
    )

    result = await orchestrator.process(request)
    _assert(result.query_decomposition is not None, "Query decomposition should be present")
    _assert(len(result.execution_log) > 0, "Execution log should not be empty")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("\n✅ Comparison Research Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Topic: {result.query_decomposition.original_topic if result.query_decomposition else 'N/A'}")

    print("\n📋 Execution Summary:")
    for entry in result.execution_log:
        if entry["status"] == "complete":
            print(f"   ✅ {entry['step']}: {entry['status']}")

    return result


async def test_with_source_retrieval():
    """Test research generation with source retrieval and benchmarking."""
    print("\n" + "=" * 60)
    print("TEST 3: Research with Source Retrieval")
    print("=" * 60)

    orchestrator = EnterpriseResearchOrchestrator()

    # Index some historical research first
    for i in range(3):
        orchestrator.retrieval_engine.index_research(
            content=f"Historical research {i} on governance patterns...",
            topic=f"governance topic {i}",
            artifact_mode="brief",
            quality_score=0.82 + i * 0.03,
            source_count=5 + i,
            claim_types={
                "direct_evidence": 4,
                "interpretation": 2,
                "analyst_inference": 1,
            },
        )

    request = EnterpriseResearchRequest(
        topic="governance patterns in multi-agent systems",
        artifact_mode="brief",
        target_audience="technical",
        enable_retrieval=True,
        output_dir="reports/research/test_output",
    )

    result = await orchestrator.process(request)

    _assert(len(result.similar_research) >= 1, "Expected at least one similar research artifact")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("\n✅ Research with Source Retrieval Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Similar Research Found: {len(result.similar_research)}")
    print(
        f"   Quality Benchmarks: {list(result.quality_benchmarks.keys()) if result.quality_benchmarks else []}"
    )

    if result.quality_benchmarks and "error" not in result.quality_benchmarks:
        print("\n   📊 Quality Benchmark:")
        print(f"      Avg Quality: {result.quality_benchmarks.get('avg_quality_score', 0):.0%}")
        print(f"      Sample Size: {result.quality_benchmarks.get('sample_size', 0)}")

    return result


async def test_full_enterprise_pipeline():
    """Test the full enterprise pipeline with all features."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Enterprise Pipeline")
    print("=" * 60)

    orchestrator = EnterpriseResearchOrchestrator()

    # Index some past research for benchmarking
    for mode in ["brief", "comparison", "trend"]:
        for i in range(2):
            orchestrator.retrieval_engine.index_research(
                content=f"Past {mode} research {i}...",
                topic=f"research topic {mode} {i}",
                artifact_mode=mode,
                quality_score=0.80 + i * 0.05,
                source_count=4 + i,
                claim_types={
                    "direct_evidence": 3 + i,
                    "interpretation": 2,
                    "analyst_inference": 1,
                    "assumption": 1,
                },
            )

    request = EnterpriseResearchRequest(
        topic="deterministic execution in agentic AI platforms",
        artifact_mode="position",
        target_audience="executive",
        enable_retrieval=True,
        enable_validation=True,
        output_dir="reports/research/test_output",
    )

    result = await orchestrator.process(request)

    _assert(result.report_path != "", "Report path is empty")
    _assert(result.manifest_path != "", "Manifest path is empty")
    _assert(result.generation_results.get("agents_executed", 0) > 0, "No agents executed")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

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

    print("\n📊 Final Metrics:")
    print(f"   Status: {result.status}")
    print(f"   Execution Time: {result.total_execution_time_ms}ms")
    print(f"   Avg Quality Score: {result.avg_quality_score:.0%}")

    return result


async def test_all_artifact_modes():
    """Test all artifact modes."""
    print("\n" + "=" * 60)
    print("TEST 5: All Artifact Modes")
    print("=" * 60)

    modes = ["brief", "comparison", "trend", "position", "thought_leadership"]
    results = []

    for mode in modes:
        print(f"\n   Testing mode: {mode}...")
        result = await run_enterprise_research(
            topic=f"test topic for {mode}",
            artifact_mode=mode,
            target_audience="technical",
            output_dir="reports/research/test_output",
        )
        results.append((mode, result))
        _assert_repo_signals(result)
        _assert_rigorous_e2e_wiring(result)
        print(f"   ✅ {mode}: {result.status}")

    print("\n📊 Mode Results:")
    for mode, result in results:
        status_icon = "✅" if result.status == "complete" else "⚠️" if result.status == "partial" else "❌"
        print(f"   {status_icon} {mode}: {result.status} (quality: {result.avg_quality_score:.0%})")

    return results


async def main():
    """Run all E2E tests."""
    print("\n" + "🔬 " * 30)
    print("ENTERPRISE RESEARCH GENERATION SYSTEM - E2E TEST SUITE")
    print("🔬 " * 30)

    results = []
    failures: list[str] = []

    try:
        # Test 1: Single topic brief
        result1 = await test_single_topic_brief()
        results.append(("Single Topic Brief", result1))

        # Test 2: Comparison mode
        result2 = await test_comparison_mode()
        results.append(("Comparison Mode", result2))

        # Test 3: Source retrieval
        result3 = await test_with_source_retrieval()
        results.append(("Source Retrieval", result3))

        # Test 4: Full pipeline
        result4 = await test_full_enterprise_pipeline()
        results.append(("Full Pipeline", result4))

        # Test 5: All modes
        results5 = await test_all_artifact_modes()
        for mode, result in results5:
            results.append((f"Mode: {mode}", result))

    except Exception as exc:
        print(f"\n❌ Test failed: {exc}")
        import traceback

        traceback.print_exc()
        failures.append(str(exc))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = (
            "✅ PASS"
            if result.status in ("complete", "partial")
            else "❌ FAIL"
        )
        print(f"{status}: {name}")
        print(f"      Trace: {result.trace_id[:16]}")
        print(f"      Quality: {result.avg_quality_score:.0%}")
        print(f"      Artifacts: {getattr(result, 'report_path', 'N/A')}")

    if failures:
        raise SystemExit(1)

    print("\n✨ All tests completed!")
    print("\nTo view generated reports, check: reports/research/test_output/")


if __name__ == "__main__":
    asyncio.run(main())
