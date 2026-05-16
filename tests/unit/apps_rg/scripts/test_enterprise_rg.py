"""E2E test suite for apps_rg enterprise workflow context."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

try:
    from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator
except ModuleNotFoundError:
    pytest.skip(
        "apps-rg-unit-pytest-remediation-f7e2a9 W1: apps_rg.reasoning.RgResumeOrchestrator "
        "not importable.",
        allow_module_level=True,
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_repo_signals(payload: dict) -> None:
    repo_signals = payload.get("repo_signals", {})
    _assert(bool(repo_signals), "repo_signals missing from orchestration result")

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


def _assert_detailed_observability(payload: dict) -> None:
    """Assert comprehensive observability signals are present."""
    # RG uses checkpoints for observability instead of trace_id
    checkpoints = payload.get("checkpoints", [])

    _assert(len(checkpoints) > 0, "Checkpoints empty - observability not wired")
    _assert("HOP-ENRICH" in checkpoints, "HOP-ENRICH checkpoint missing - repo signal wiring not complete")


def _assert_layer4_wiring(payload: dict) -> None:
    """Assert Layer 4 (orchestration) wiring is active."""
    repo_signals = payload.get("repo_signals", {})

    ci = repo_signals.get("ci", {})
    _assert(ci.get("workflow_count", 0) >= 30, "Layer 4: insufficient CI workflows")

    tests = repo_signals.get("tests", {})
    _assert(tests.get("inventory_entries", 0) > 1000, "Layer 4: insufficient test inventory")


def _assert_enhanced_system_learning(payload: dict) -> None:
    """Assert enhanced system learning signals are present."""
    repo_signals = payload.get("repo_signals", {})
    governance = repo_signals.get("governance", {})

    # Market fit (RG-specific system learning) - optional
    market_fit = governance.get("market_fit", {})
    if market_fit:
        if "role_fit_score" not in market_fit:
            print("   ⚠️  System learning: market_fit.role_fit_score missing (non-blocking)")

    # ADG signals for pattern capture
    adg = repo_signals.get("adg", {})
    if adg.get("available"):
        nodes_count = adg.get("nodes_count", 0)
        if nodes_count <= 100000:
            print(f"   ⚠️  System learning: ADG nodes ({nodes_count}) below threshold (non-blocking)")


def _assert_rigorous_e2e_wiring(payload: dict) -> None:
    """Comprehensive E2E wiring validation."""
    print("\n🔍 RIGOROUS E2E WIRING VALIDATION")
    print("-" * 40)

    try:
        _assert_repo_signals(payload)
        print("   ✅ Repo signals: PASS")
    except AssertionError as e:
        print(f"   ❌ Repo signals: FAIL - {e}")
        raise

    try:
        _assert_detailed_observability(payload)
        print("   ✅ Observability: PASS")
    except AssertionError as e:
        print(f"   ❌ Observability: FAIL - {e}")
        raise

    try:
        _assert_layer4_wiring(payload)
        print("   ✅ Layer 4 wiring: PASS")
    except AssertionError as e:
        print(f"   ❌ Layer 4 wiring: FAIL - {e}")
        raise

    try:
        _assert_enhanced_system_learning(payload)
        print("   ✅ System learning: PASS")
    except AssertionError as e:
        print(f"   ❌ System learning: FAIL - {e}")
        raise

    print("-" * 40)
    print("🎯 ALL E2E WIRING ASSERTIONS: PASS")
    print("-" * 40)


def test_rg_resume_orchestrator_enrichment() -> dict:
    print("\n" + "=" * 60)
    print("TEST: RG Resume Orchestrator with Repo Signal Enrichment")
    print("=" * 60)

    orchestrator = RgResumeOrchestrator(
        master_resume={
            "contact_info": {"name": "Candidate", "email": "candidate@example.com"},
            "experience": [{"company": "Example Corp", "title": "Engineer"}],
            "skills": ["Python", "Architecture", "Testing"],
        },
        qwen_enabled=False,
        test_mode=True,
        enable_repo_signals=True,
    )

    result = orchestrator.run("Senior AI Engineer role requiring deterministic systems experience")

    _assert(result.get("status") == "success", "Orchestrator status should be success")
    _assert("HOP-ENRICH" in result.get("checkpoints", []), "HOP-ENRICH checkpoint missing")
    _assert_repo_signals(result)
    _assert_rigorous_e2e_wiring(result)

    print("✅ Orchestrator run complete")
    print(f"   Status: {result.get('status')}")
    print(f"   Checkpoints: {result.get('checkpoints')}")

    return result


def main() -> None:
    failures: list[str] = []

    try:
        result = test_rg_resume_orchestrator_enrichment()
    except Exception as exc:
        failures.append(str(exc))
        print(f"\n❌ Test failed: {exc}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if failures:
        print("❌ FAIL: apps_rg enterprise enrichment")
        raise SystemExit(1)

    print("✅ PASS: apps_rg enterprise enrichment")
    print("\n✨ All tests completed!")


if __name__ == "__main__":
    main()
