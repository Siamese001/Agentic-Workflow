"""
Phase 3 Data Flow Test Runner.

Runs the Phase 3 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 3 data flow tests."""
    print("=" * 70)
    print("PHASE 3 DATA FLOW TESTS")
    print("=" * 70)

    from apps_rg.engines.base.sovereign_context import SovereignContext
    from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
    from apps_rg.engines.hops.hop2_enrichment_engine import DataEnrichmentEngine
    from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine

    passed = 0
    failed = 0

    # Test 1: HOP1 Reads From Buffer
    print("\n[TEST 1] test_hop1_reads_from_buffer")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Don't write mission_input yet

            clerk = ClerkExtractionEngine(ctx)
            try:
                await clerk.execute()
                return False, "Expected ValueError"
            except ValueError as e:
                if "Buffer missing mission_input" not in str(e):
                    return False, f"Wrong error message: {e}"

            # Now write input
            mock_resume = {"experience": []}
            ctx.buffer.write("mission_input", {"master_resume": mock_resume}, "TEST_SETUP")

            result = await clerk.execute()
            if "experience_sections" not in result:
                return False, "Missing experience_sections in result"

            # Verify Write
            saved = ctx.buffer.read("hop1_extraction")
            if saved is None:
                return False, "hop1_extraction not written to buffer"

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

    # Test 2: HOP2 Chaining
    print("\n[TEST 2] test_hop2_chaining")
    try:

        async def run_test():
            ctx = SovereignContext()

            # Simulate HOP1 output existing
            hop1_out = {"experience_sections": [{"bullets": [{"bullet_text": "Managed stuff"}]}]}
            ctx.buffer.write("hop1_extraction", hop1_out, "HOP1_MOCK")

            enricher = DataEnrichmentEngine(ctx)
            result = await enricher.execute()

            if "enrichment_metadata" not in result:
                return False, "Missing enrichment_metadata"
            if ctx.buffer.read("hop2_enrichment") is None:
                return False, "hop2_enrichment not written to buffer"

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

    # Test 3: Orchestrator End-to-End Flow
    print("\n[TEST 3] test_orchestrator_end_to_end_flow")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Inject master resume into context wrapper as expected by Orchestrator init
            ctx.master_resume = {"experience": [{"company": "A", "bullets": ["Did A"]}]}

            orch = ResumeOrchestratorEngine(ctx)
            result = await orch.execute("Job Description")

            if result["status"] != "success":
                return False, f"Status not success: {result['status']}"
            if "HOP-1" not in result["checkpoints"]:
                return False, "HOP-1 not in checkpoints"
            if "HOP-2" not in result["checkpoints"]:
                return False, "HOP-2 not in checkpoints"

            # Verify Trace
            summary = ctx.trace.get_summary()
            if summary["completed"] < 2:
                return False, f"Expected at least 2 completed spans, got {summary['completed']}"

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

    # Test 4: HOP2 Fails Without HOP1 Output
    print("\n[TEST 4] test_hop2_fails_without_hop1")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Don't write hop1_extraction

            enricher = DataEnrichmentEngine(ctx)
            try:
                await enricher.execute()
                return False, "Expected ValueError"
            except ValueError as e:
                if "Buffer missing hop1_extraction" not in str(e):
                    return False, f"Wrong error message: {e}"

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

    # Test 5: Buffer Immutability in Data Flow
    print("\n[TEST 5] test_buffer_immutability_in_dataflow")
    try:

        async def run_test():
            ctx = SovereignContext()

            # Write mission_input
            mock_resume = {"experience": [{"company": "Test", "bullets": ["Did stuff"]}]}
            ctx.buffer.write("mission_input", {"master_resume": mock_resume}, "TEST")

            # Run HOP1
            clerk = ClerkExtractionEngine(ctx)
            await clerk.execute()

            # Try to overwrite hop1_extraction (should fail)
            try:
                ctx.buffer.write("hop1_extraction", {"fake": "data"}, "ATTACKER")
                return False, "Should not allow overwriting hop1_extraction"
            except PermissionError:
                pass  # Expected

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
        print("\n🎉 ALL TESTS PASSED - Phase 3 Data Flow is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding to Phase 4")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
