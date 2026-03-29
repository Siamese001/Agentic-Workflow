"""E2E test suite for apps_rg enterprise workflow context."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator

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
