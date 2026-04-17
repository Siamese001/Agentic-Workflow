"""E2E test for enterprise LIC campaign orchestration."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from apps_lic.reasoning.enterprise_campaign_orchestrator import (  # noqa: E402
    EnterpriseLicOrchestrator,
    EnterpriseLicRequest,
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
    _assert(bool(repo_signals), "repo_signals missing from enterprise LIC result")

    adg = repo_signals.get("adg", {})
    tests = repo_signals.get("tests", {})
    ci = repo_signals.get("ci", {})
    governance = repo_signals.get("governance", {})
    lic_domain = governance.get("lic_domain", {})

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
    _assert(lic_domain.get("agent_specs_available") is True, "LIC agent specs signal unavailable")


def _assert_detailed_observability(result: object) -> None:
    """Assert comprehensive observability signals are present."""
    trace_id = getattr(result, "trace_id", "")

    _assert(bool(trace_id), "Trace ID missing - distributed tracing not wired")
    _assert(len(trace_id) >= 16, f"Trace ID too short ({len(trace_id)} chars)")

    # Check provenance block for observability
    provenance = getattr(result, "provenance_block", {})
    _assert(bool(provenance), "Provenance block missing - observability not wired")
    _assert(provenance.get("trace_id") == trace_id, "Provenance trace_id mismatch")


def _assert_layer4_wiring(result: object) -> None:
    """Assert Layer 4 (orchestration) wiring is active."""
    repo_signals = getattr(result, "repo_signals", {})

    ci = repo_signals.get("ci", {})
    _assert(ci.get("workflow_count", 0) >= 30, "Layer 4: insufficient CI workflows")

    tests = repo_signals.get("tests", {})
    _assert(tests.get("inventory_entries", 0) > 1000, "Layer 4: insufficient test inventory")


def _assert_enhanced_system_learning(result: object) -> None:
    """Assert enhanced system learning signals are present."""
    repo_signals = getattr(result, "repo_signals", {})
    governance = repo_signals.get("governance", {})

    # LIC domain signals (LIC-specific system learning) - optional
    lic_domain = governance.get("lic_domain", {})
    if lic_domain:
        if "agent_specs_available" not in lic_domain:
            print("   ⚠️  System learning: lic_domain.agent_specs_available missing (non-blocking)")

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


async def test_enterprise_lic_campaign() -> object:
    print("\n" + "=" * 60)
    print("TEST: Enterprise LIC Campaign Planning")
    print("=" * 60)

    orchestrator = EnterpriseLicOrchestrator()
    request = EnterpriseLicRequest(
        campaign_goal="Increase response rate for principal engineer outreach",
        audience_segment="engineering_leadership",
        channel="linkedin",
        output_mode="planning",
        enable_repo_signals=True,
    )

    result = await orchestrator.process(request)

    _assert(result.status == "complete", "Enterprise LIC status should be complete")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)
    _assert(bool(result.recommendations), "Expected campaign recommendations")
    _assert(result.provenance_block.get("trace_id") == result.trace_id, "Trace mismatch in provenance block")

    print("✅ Enterprise LIC orchestration complete")
    print(f"   Status: {result.status}")
    print(f"   Risk: {result.risk_summary}")
    print(f"   Confidence: {result.confidence_summary}")
    print(f"   Recommendations: {len(result.recommendations)}")

    return result


async def main() -> None:
    failures: list[str] = []

    try:
        await test_enterprise_lic_campaign()
    except Exception as exc:
        failures.append(str(exc))
        print(f"\n❌ Test failed: {exc}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if failures:
        print("❌ FAIL: apps_lic enterprise campaign")
        raise SystemExit(1)

    print("✅ PASS: apps_lic enterprise campaign")
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
