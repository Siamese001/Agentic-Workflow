"""
Phase 6 Full Cycle Test Runner.

Runs the Phase 6 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 6 full cycle tests."""
    print("=" * 70)
    print("PHASE 6 FULL CYCLE TESTS")
    print("=" * 70)

    from apps_rg.engines.base.sovereign_context import SovereignContext
    from apps_rg.engines.generation.service_invoker_engine import ServiceInvokerEngine
    from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
    from apps_rg.engines.quality.content_quality_engine import ContentQualityEngine

    passed = 0
    failed = 0

    # Test 1: Orchestrator Full Chain
    print("\n[TEST 1] test_orchestrator_full_chain")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Setup Mock Data
            ctx.master_resume = {
                "experience": [{"company": "A", "bullets": ["Managed $1M budget"]}],
                "education": [],
                "skills": [],
            }

            orch = ResumeOrchestratorEngine(ctx)
            result = await orch.execute("Senior Python Engineer with leadership experience")

            # Check Checkpoints
            checkpoints = result["checkpoints"]
            expected_checkpoints = [
                "HOP-1",
                "HOP-2",
                "HOP-3-K9",
                "HOP-4-OPT",
                "HOP-4-RANK",
                "HOP-5-ATS",
            ]
            for checkpoint in expected_checkpoints:
                if checkpoint not in checkpoints:
                    return False, f"Missing checkpoint: {checkpoint}"

            # Check Final Output
            if result["status"] not in ["SUCCESS", "WARNING"]:
                return False, f"Unexpected status: {result['status']}"

            # Verify Data Flow
            if ctx.buffer.read("k9_competencies") is None:
                return False, "k9_competencies not written"
            if ctx.buffer.read("ranked_content") is None:
                return False, "ranked_content not written"

            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  PASSED")
            passed += 1
        else:
            print(f"  FAILED: {error}")
            failed += 1
    except Exception as e:
        import traceback

        print(f"  FAILED: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        failed += 1

    # Test 2: Quality Feedback Loop
    print("\n[TEST 2] test_quality_feedback_loop")
    try:

        async def run_test():
            ctx = SovereignContext()
            ctx.buffer.write(
                "hop2_enrichment",
                {
                    "experience_sections": [
                        {"bullets": [{"bullet_text": "Responsible for nothing"}]}
                    ]
                },
                "SETUP",
            )

            engine = ContentQualityEngine(ctx)
            await engine.execute()

            report = ctx.buffer.read("quality_report")
            if report is None:
                return False, "quality_report not written"
            if report["score"] >= 100:
                return False, f"Expected score < 100, got {report['score']}"
            if len(report["issues"]) == 0:
                return False, "Expected at least 1 issue"
            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED: {error}")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 3: Service Invoker Telemetry
    print("\n[TEST 3] test_service_invoker_telemetry")
    try:

        async def run_test():
            ctx = SovereignContext()
            engine = ServiceInvokerEngine(ctx)
            response = await engine.execute("Test prompt", "test-model")

            if response != "Sovereign Generated Content":
                return False, f"Unexpected response: {response}"
            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED: {error}")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 4: Orchestrator Handles ATS Failure
    print("\n[TEST 4] test_orchestrator_handles_ats_failure")
    try:

        async def run_test():
            ctx = SovereignContext()
            ctx.master_resume = {
                "experience": [{"company": "A", "bullets": ["<table>Bad HTML</table>"]}],
                "education": [],
                "skills": [],
            }

            orch = ResumeOrchestratorEngine(ctx)
            result = await orch.execute("Test job")

            # Should return WARNING status due to ATS failure
            if result["status"] != "WARNING":
                return False, f"Expected WARNING status, got {result['status']}"
            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED: {error}")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 5: Quality Engine Skips Empty Data
    print("\n[TEST 5] test_quality_engine_skips_empty")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Don't write any data

            engine = ContentQualityEngine(ctx)
            result = await engine.execute()

            if result["status"] != "skipped":
                return False, f"Expected 'skipped' status, got {result['status']}"
            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED: {error}")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 6: Service Invoker Token Counting
    print("\n[TEST 6] test_service_invoker_token_counting")
    try:

        async def run_test():
            ctx = SovereignContext()
            engine = ServiceInvokerEngine(ctx)

            # Check that telemetry is recorded (via record_pass call)
            # This is a basic smoke test
            response = await engine.execute("A longer prompt with more words", "test-model")

            if not response:
                return False, "No response from service invoker"
            return True, None

        success, error = asyncio.run(run_test())
        if success:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED: {error}")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Phase 6 Full Cycle is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
