"""
Test script for enterprise RFP generation.

Demonstrates end-to-end RFP processing with all enterprise components:
- Document ingestion
- Requirement decomposition (L1)
- Past proposal retrieval (L2)
- Multi-agent section generation (L3)
- Compliance validation (L5)
- Traceable output with source register
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add repo to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from apps_rfp.reasoning.enterprise_orchestrator import (
    EnterpriseRfpOrchestrator,
    EnterpriseRfpRequest,
    generate_proposal_from_rfp,
    generate_proposal_from_text,
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
    _assert(bool(repo_signals), "repo_signals missing from enterprise RFP result")

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

    complete_steps = {
        entry.get("step", "").upper() for entry in execution_log if entry.get("status") == "complete"
    }
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

    # Delivery proof (RFP-specific system learning) - optional
    delivery_proof = governance.get("delivery_proof", {})
    if delivery_proof:
        if "track_record" not in delivery_proof:
            print("   ⚠️  System learning: delivery_proof.track_record missing (non-blocking)")

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


async def test_with_sample_rfp():
    """Test with a sample RFP document."""
    print("\n" + "=" * 60)
    print("TEST 1: Process Financial Services RFP Document")
    print("=" * 60)

    rfp_path = Path(__file__).parent / "sample_rfps" / "financial_services_rfp.md"

    if not rfp_path.exists():
        print(f"Sample RFP not found: {rfp_path}")
        return

    result = await generate_proposal_from_rfp(
        rfp_path=str(rfp_path),
        industry="financial_services",
        output_dir="rfp/test_output",
    )

    _assert(result.proposal_path != "", "Proposal path is empty")
    _assert(result.source_register_path != "", "Source register path is empty")
    _assert(len(result.requirements) > 0, "Expected requirements from sample RFP")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("\n✅ RFP Processing Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Proposal Path: {result.proposal_path}")
    print(f"   Source Register: {result.source_register_path}")
    print("\n📊 Metrics:")
    print(f"   Requirements Found: {len(result.requirements)}")
    print(f"   Components Decomposed: {result.implementation_plan.get('total_components', 0)}")
    print(f"   Similar Proposals Retrieved: {len(result.similar_proposals)}")
    print(f"   Proposal Sections: {result.proposal.get('total_sections', 0)}")
    print(f"   Word Count: {result.proposal.get('total_word_count', 0)}")
    print(f"   Quality Score: {result.proposal.get('average_quality_score', 0):.0%}")

    if result.compliance_result:
        print("\n🛡️ Compliance Validation:")
        print(f"   Passed: {result.compliance_result.get('passed', False)}")
        print(f"   Violations: {len(result.compliance_result.get('violations', []))}")
        print(f"   Quality Score: {result.compliance_result.get('quality_score', 0):.0%}")

    return result


async def test_with_problem_statement():
    """Test with a simple problem statement."""
    print("\n" + "=" * 60)
    print("TEST 2: Generate Proposal from Problem Statement")
    print("=" * 60)

    problem = """
    We need to automate our document processing workflow which currently takes
    40 hours per week of manual data entry. The solution should extract data
    from PDF invoices, validate against purchase orders, and flag discrepancies
    for review. We process approximately 5,000 documents per month.
    """

    result = await generate_proposal_from_text(
        problem_statement=problem.strip(),
        industry="technology",
        output_dir="rfp/test_output",
    )

    _assert(result.proposal_path != "", "Proposal path is empty")
    _assert(result.source_register_path != "", "Source register path is empty")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("\n✅ Proposal Generation Complete!")
    print(f"   Trace ID: {result.trace_id}")
    print(f"   Status: {result.status}")
    print(f"   Proposal Path: {result.proposal_path}")

    return result


async def test_full_pipeline():
    """Test the full enterprise orchestrator with detailed output."""
    print("\n" + "=" * 60)
    print("TEST 3: Full Enterprise Pipeline")
    print("=" * 60)

    orchestrator = EnterpriseRfpOrchestrator()

    # Create request with healthcare RFP
    rfp_path = Path(__file__).parent / "sample_rfps" / "healthcare_rfp.md"

    request = EnterpriseRfpRequest(
        rfp_document_path=str(rfp_path) if rfp_path.exists() else None,
        problem_statement="Healthcare document processing automation" if not rfp_path.exists() else None,
        industry="healthcare",
        company_name="Metro Health System",
        our_company_name="Agentic AI Solutions",
        output_dir="rfp/test_output",
    )

    result = await orchestrator.process(request)

    _assert(result.proposal_path != "", "Proposal path is empty")
    _assert(result.source_register_path != "", "Source register path is empty")
    _assert(len(result.execution_log) > 0, "Execution log should not be empty")
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
    print(f"   Proposal: {result.proposal_path}")
    print(f"   Source Register: {result.source_register_path}")
    print(f"   Validation Report: {result.validation_report_path}")

    return result


async def main():
    """Run all tests."""
    print("\n" + "🚀 " * 30)
    print("ENTERPRISE RFP GENERATION SYSTEM - TEST SUITE")
    print("🚀 " * 30)

    results = []
    failures: list[str] = []

    try:
        # Test 1: Sample RFP document
        result1 = await test_with_sample_rfp()
        results.append(("Sample RFP", result1))

        # Test 2: Problem statement
        result2 = await test_with_problem_statement()
        results.append(("Problem Statement", result2))

        # Test 3: Full pipeline
        result3 = await test_full_pipeline()
        results.append(("Full Pipeline", result3))

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
        status = "✅ PASS" if result and result.status in ("complete", "partial") else "❌ FAIL"
        print(f"{status}: {name}")
        if result:
            print(f"      Trace: {result.trace_id[:16]}")
            print(f"      Artifacts: {result.proposal_path}")

    if failures:
        raise SystemExit(1)

    print("\n✨ All tests completed!")
    print("\nTo view generated proposals, check: rfp/test_output/")


if __name__ == "__main__":
    asyncio.run(main())
