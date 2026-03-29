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


async def test_single_persona_brief():
    """Test brief generation for a single persona."""
    print("\n" + "="*60)
    print("TEST 1: Single Persona Brief Generation")
    print("="*60)

    personas = ["recruiter"]
    source_content = """
    This is a sample source document describing an AI platform with:
    - Multi-agent orchestration capabilities
    - Deterministic execution guarantees
    - Layered architecture (L0-L6)
    - Comprehensive test coverage (95%)
    - Low latency performance (10ms for policy validation)
    - Governance-first design with static analysis enforcement
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

    print(f"\n✅ Brief Generation Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Report Path: {result.report_path}")

    print(f"\n📊 Results:")
    print(f"   Personas Decomposed: {len(result.decompositions)}")
    print(f"   Total Sections: {result.production_plan.get('total_sections', 0)}")
    print(f"   Agents Executed: {result.generation_results.get('agents_executed', 0)}")

    print(f"\n🛡️ Validation:")
    print(f"   Validations Run: {len(result.validation_results)}")
    print(f"   Gates Passed: {sum(1 for g in result.gate_results if g.get('gates_passed'))}/{len(result.gate_results)}")
    print(f"   Avg Quality Score: {result.avg_quality_score:.0%}")

    return result


async def test_multi_persona_briefs():
    """Test brief generation for multiple personas."""
    print("\n" + "="*60)
    print("TEST 2: Multi-Persona Brief Generation")
    print("="*60)

    personas = ["recruiter", "cto", "board"]
    source_content = """
    Enterprise AI Platform with the following characteristics:
    
    Architecture:
    - Layered agentic architecture (L0-L6)
    - Deterministic execution via lifecycle contracts
    - Static analysis enforcement (pre-commit hooks)
    - Quality gates across 5 dimensions
    
    Capabilities:
    - Multi-agent orchestration with dependency management
    - Evidence-grounded brief generation
    - Full traceability and auditability
    - Enterprise-grade governance
    
    Performance:
    - 10ms policy validation latency
    - 95% test coverage
    - 6,000+ modules
    - 100% determinism compliance
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

    print(f"\n✅ Multi-Persona Briefs Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Personas: {', '.join(d.audience_persona for d in result.decompositions)}")

    print(f"\n📋 Execution Summary:")
    for entry in result.execution_log:
        if entry["status"] == "complete":
            print(f"   ✅ {entry['step']}: {entry['status']}")

    return result


async def test_with_style_retrieval():
    """Test brief generation with style retrieval and benchmarking."""
    print("\n" + "="*60)
    print("TEST 3: Brief Generation with Style Retrieval")
    print("="*60)

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

    print(f"\n✅ Brief with Style Retrieval Complete!")
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
    print("\n" + "="*60)
    print("TEST 4: Full Enterprise Pipeline")
    print("="*60)

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
        Comprehensive platform documentation including:
        
        Technical Architecture:
        - Layered design with 7 layers (L0-L6)
        - Clear separation of concerns
        - Deterministic execution model
        - Full observability and traceability
        
        Governance & Quality:
        - Static analysis at commit time
        - 5-dimensional quality scorecard
        - Automated regression detection
        - Compliance validation (L5)
        
        Performance Metrics:
        - 10ms policy validation
        - 95% test coverage
        - 100% determinism compliance
        - Zero blocking violations in production
        """,
        source_dirs=["docs/architecture", "docs/governance"],
        enable_retrieval=True,
        enable_validation=True,
        output_dir="reports/executive/test_output",
    )

    result = await orchestrator.process(request)

    print(f"\n📋 Execution Log:")
    for entry in result.execution_log:
        status_icon = "✅" if entry["status"] == "complete" else "⏳" if entry["status"] == "start" else "⚠️"
        print(f"   {status_icon} {entry['step']}: {entry['status']}")
        if entry.get("details"):
            for key, value in entry["details"].items():
                print(f"      - {key}: {value}")

    print(f"\n📁 Generated Artifacts:")
    print(f"   Report: {result.report_path}")
    print(f"   Manifest: {result.manifest_path}")

    print(f"\n📊 Final Metrics:")
    print(f"   Status: {result.status}")
    print(f"   Execution Time: {result.total_execution_time_ms}ms")
    print(f"   Avg Quality Score: {result.avg_quality_score:.0%}")

    return result


async def main():
    """Run all E2E tests."""
    print("\n" + "🚀 "*30)
    print("ENTERPRISE BRIEF GENERATION SYSTEM - E2E TEST SUITE")
    print("🚀 "*30)

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
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, result in results:
        status = "✅ PASS" if result.status == "complete" else "⚠️ PARTIAL" if result.status == "partial" else "❌ FAIL"
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
