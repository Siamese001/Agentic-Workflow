"""E2E test for enterprise LIC campaign orchestration."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
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
