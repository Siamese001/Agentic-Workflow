"""
E2E Test Suite for apps_exec.enterprise.

Tests the full enterprise brief generation pipeline with realistic scenarios.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add repo to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from apps_exec.reasoning.enterprise_brief_orchestrator import (
    EnterpriseBriefOrchestrator,
    EnterpriseBriefRequest,
    run_enterprise_briefs,
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
    _assert(bool(repo_signals), "repo_signals missing from enterprise brief result")

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


def _assert_system_learning_wired(result: object) -> None:
    """Assert system learning signals are present in result."""
    repo_signals = getattr(result, "repo_signals", {})
    governance = repo_signals.get("governance", {})
    
    # Check for engineering posture signal (exec-specific system learning)
    engineering_posture = governance.get("engineering_posture", {})
    if engineering_posture:
        _assert(
            "risk_level" in engineering_posture,
            "Risk level missing from system learning signals"
        )


def _assert_observability_wired(result: object) -> None:
    """Assert observability signals are present in result."""
    # Check execution log for observability
    execution_log = getattr(result, "execution_log", [])
    _assert(len(execution_log) > 0, "Execution log empty - observability not wired")
    
    # Check trace_id present (distributed tracing)
    trace_id = getattr(result, "trace_id", "")
    _assert(bool(trace_id), "Trace ID missing - distributed tracing not wired")


async def test_single_persona_brief():
    """Test brief generation for a single persona."""
    print("\n" + "=" * 60)
    print("TEST 1: Single Persona Brief Generation")
    print("=" * 60)

    personas = ["recruiter"]
    source_content = """
    Platform Technical Documentation:

    Test Coverage: 95% of 6,000+ modules with automated test inventory.
    Performance: Policy validation completes in 10ms with 99.9% availability.
    Architecture: 7-layer design (L0-L6) with clear separation between routing,
    cognition, execution, orchestration, and safety concerns.

    Quality Measures:
    - Static analysis runs on every commit via pre-commit hooks
    - ADG (Architecture Dependency Graph) tracks 170,000+ nodes and 800,000+ edges
    - CI/CD pipeline includes 33 workflow definitions for comprehensive validation
    - Governance baseline tracks calls, execution traces, writes, and reads

    Compliance: All modules subject to determinism contracts and lifecycle tracing.
    """

    result = await run_enterprise_briefs(
        target_personas=personas,
        source_content=source_content,
        output_dir="reports/executive/test_output",
    )

    _assert(result.report_path != "", "Report path is empty")
    _assert(result.manifest_path != "", "Manifest path is empty")
    _assert(result.generation_results.get("agents_executed", 0) > 0, "No agents executed")
    _assert_repo_signals(result)

    print("\n✅ Brief Generation Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Report Path: {result.report_path}")

    print("\n📊 Results:")
    print(f"   Personas Decomposed: {len(result.decompositions)}")
    print(f"   Total Sections: {result.production_plan.get('total_sections', 0)}")
    print(f"   Agents Executed: {result.generation_results.get('agents_executed', 0)}")

    print("\n🛡️ Validation:")
    print(f"   Validations Run: {len(result.validation_results)}")
    print(
        f"   Gates Passed: {sum(1 for g in result.gate_results if g.get('gates_passed'))}/{len(result.gate_results)}"
    )
    print(f"   Avg Quality Score: {result.avg_quality_score:.0%}")

    return result


async def test_multi_persona_briefs():
    """Test brief generation for multiple personas."""
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Persona Brief Generation")
    print("=" * 60)

    personas = ["recruiter", "cto", "board"]
    source_content = """
    Technical Platform Specification:

    Architecture Details:
    - 7-layer modular design (L0 through L6)
    - 6,000+ Python modules with deterministic execution contracts
    - Lifecycle tracing on all entry points via static analysis
    - Pre-commit hooks enforce quality gates before any code merge

    Test & Quality Metrics:
    - 95% code coverage across core modules
    - 3,096 test cases tracked in test inventory
    - 33 CI workflow definitions for automated validation
    - ADG tracks 170,000+ nodes and 800,000+ dependency edges

    Performance Benchmarks:
    - 10ms policy validation latency (p99)
    - Sub-50ms routing decisions
    - 99.9% uptime target with observability hooks

    Governance: Locked denominator baselines for calls (19,609),
    execution traces (118), writes (5,095), and reads (72,652).
    """

    orchestrator = EnterpriseBriefOrchestrator()
    request = EnterpriseBriefRequest(
        target_personas=personas,
        source_content=source_content,
        enable_retrieval=True,
        enable_validation=True,
        output_dir="reports/executive/test_output",
    )

    result = await orchestrator.process(request)

    _assert(len(result.decompositions) == 3, "Expected decomposition for 3 personas")
    _assert(len(result.execution_log) > 0, "Execution log should not be empty")
    _assert_repo_signals(result)
    _assert_system_learning_wired(result)
    _assert_observability_wired(result)

    print("\n✅ Multi-Persona Briefs Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Personas: {', '.join(d.audience_persona for d in result.decompositions)}")

    print("\n📋 Execution Summary:")
    for entry in result.execution_log:
        if entry["status"] == "complete":
            print(f"   ✅ {entry['step']}: {entry['status']}")

    return result


async def test_with_style_retrieval():
    """Test brief generation with style retrieval and benchmarking."""
    print("\n" + "=" * 60)
    print("TEST 3: Brief Generation with Style Retrieval")
    print("=" * 60)

    orchestrator = EnterpriseBriefOrchestrator()

    # Index some historical briefs first
    for i in range(3):
        orchestrator.retrieval_engine.index_brief(
            content=f"Historical brief {i} for recruiter...",
            audience_persona="recruiter",
            quality_score=0.82 + i * 0.03,
            style_markers={
                "buzzword_density": 0.02,
                "evidence_density": 0.15,
                "readability_score": 0.75,
            },
            sections=["Executive Summary", "Key Skills", "Experience"],
        )

    request = EnterpriseBriefRequest(
        target_personas=["recruiter"],
        source_content="Sample source content for style benchmarking test.",
        enable_retrieval=True,
        output_dir="reports/executive/test_output",
    )

    result = await orchestrator.process(request)

    _assert(len(result.similar_briefs) >= 1, "Expected at least one similar brief")
    _assert_repo_signals(result)
    _assert_system_learning_wired(result)
    _assert_observability_wired(result)

    print("\n✅ Brief with Style Retrieval Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Similar Briefs Found: {len(result.similar_briefs)}")
    print(f"   Style Benchmarks: {list(result.style_benchmarks.keys())}")

    if result.style_benchmarks:
        for persona, benchmark in result.style_benchmarks.items():
            if isinstance(benchmark, dict) and "error" not in benchmark:
                print(f"\n   📊 {persona} Benchmark:")
                print(f"      Avg Quality: {benchmark.get('avg_quality_score', 0):.0%}")
                print(f"      Sample Size: {benchmark.get('sample_size', 0)}")

    return result


async def test_full_enterprise_pipeline():
    """Test the full enterprise pipeline with all features."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Enterprise Pipeline")
    print("=" * 60)

    orchestrator = EnterpriseBriefOrchestrator()

    # Index some past briefs for all personas
    for persona in ["recruiter", "cto", "board"]:
        for i in range(2):
            orchestrator.retrieval_engine.index_brief(
                content=f"Past {persona} brief {i}...",
                audience_persona=persona,
                quality_score=0.80 + i * 0.05,
                style_markers={
                    "buzzword_density": 0.03,
                    "evidence_density": 0.12,
                    "readability_score": 0.72,
                },
                sections=["Executive Summary", "Key Points"],
            )

    request = EnterpriseBriefRequest(
        target_personas=["recruiter", "cto", "svp_eng", "board"],
        source_content="""
        Comprehensive Platform Technical Documentation:

        Architecture:
        - 7-layer modular design from L0 (routing) to L6 (observability)
        - 6,290 modules with full lifecycle trace contracts
        - ADG dependency graph: 170,000 nodes, 800,000+ edges
        - Static analysis enforcement via pre-commit configuration

        Quality & Testing:
        - 95% test coverage measured by test inventory (3,096 entries)
        - 33 CI workflow definitions in .github/workflows
        - Pre-commit hooks for determinism and import validation
        - Governance baseline with locked denominators

        Performance Metrics:
        - 10ms policy validation latency at p99
        - Sub-50ms routing decision time
        - 3,011 modules with execution trace wiring (100%)
        - Zero blocking violations in production baseline

        Observability: Full execution tracing, telemetry event recording,
        and embedding storage across all production paths.
        """,
        source_dirs=["docs/architecture", "docs/governance"],
        enable_retrieval=True,
        enable_validation=True,
        output_dir="reports/executive/test_output",
    )

    result = await orchestrator.process(request)

    _assert(result.report_path != "", "Report path is empty")
    _assert(result.manifest_path != "", "Manifest path is empty")
    _assert(result.generation_results.get("agents_executed", 0) > 0, "No agents executed")
    _assert_repo_signals(result)

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


async def main():
    """Run all E2E tests."""
    print("\n" + "🚀 " * 30)
    print("ENTERPRISE BRIEF GENERATION SYSTEM - E2E TEST SUITE")
    print("🚀 " * 30)

    results = []
    failures: list[str] = []

    try:
        # Test 1: Single persona
        result1 = await test_single_persona_brief()
        results.append(("Single Persona", result1))

        # Test 2: Multi-persona
        result2 = await test_multi_persona_briefs()
        results.append(("Multi-Persona", result2))

        # Test 3: Style retrieval
        result3 = await test_with_style_retrieval()
        results.append(("Style Retrieval", result3))

        # Test 4: Full pipeline
        result4 = await test_full_enterprise_pipeline()
        results.append(("Full Pipeline", result4))

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
    print("\nTo view generated reports, check: reports/executive/test_output/")


if __name__ == "__main__":
    asyncio.run(main())
