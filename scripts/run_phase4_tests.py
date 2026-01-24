"""
Phase 4 Domain Expansion Test Runner.

Runs the Phase 4 tests directly, bypassing pytest configuration issues.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 4 domain expansion tests."""
    print("=" * 70)
    print("PHASE 4 DOMAIN EXPANSION TESTS")
    print("=" * 70)

    from apps_rg.engines.base.sovereign_context import SovereignContext
    from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine
    from apps_rg.engines.refinement.weight_adjustment_engine import WeightAdjustmentEngine
    from apps_rg.engines.refinement.content_optimizer_engine import ContentOptimizerEngine

    passed = 0
    failed = 0

    # Test 1: K9 Requires Upstream Data
    print("\n[TEST 1] test_k9_requires_upstream_data")
    try:
        async def run_test():
            ctx = SovereignContext()
            # Write only mission, missing enrichment
            ctx.buffer.write(
                "mission_input", {"job_description_keywords": ["python"]}, "SETUP"
            )

            engine = GapClosureEngine(ctx)
            try:
                await engine.execute()
                return False, "Expected ValueError"
            except ValueError as e:
                if "Buffer missing hop2_enrichment" not in str(e):
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

    # Test 2: K9 Writes to Buffer
    print("\n[TEST 2] test_k9_writes_to_buffer")
    try:
        async def run_test():
            ctx = SovereignContext()
            ctx.buffer.write(
                "mission_input", {"job_description_keywords": ["python"]}, "SETUP"
            )
            ctx.buffer.write("hop2_enrichment", {"skills": []}, "SETUP")

            engine = GapClosureEngine(ctx)
            await engine.execute()

            saved = ctx.buffer.read("k9_competencies")
            if saved is None:
                return False, "k9_competencies not written to buffer"
            if len(saved) != 6:
                return False, f"Expected 6 competencies, got {len(saved)}"
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

    # Test 3: Weight Adjustment Reads Signals
    print("\n[TEST 3] test_weight_adjustment_reads_signals")
    try:
        async def run_test():
            ctx = SovereignContext()
            ctx.add_signal("ATS_FAILURE")

            engine = WeightAdjustmentEngine(ctx)
            result = await engine.execute()

            if result.get("skills") != 1.25:
                return False, f"Expected skills=1.25, got {result.get('skills')}"
            if ctx.buffer.read("adjusted_weights") != result:
                return False, "Buffer doesn't match result"
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

    # Test 4: Optimizer Uses Weights
    print("\n[TEST 4] test_optimizer_uses_weights")
    try:
        async def run_test():
            ctx = SovereignContext()
            # Mock data
            ctx.buffer.write(
                "hop2_enrichment",
                {"experience_sections": [{"bullets": [{"quantified_metrics": True}]}]},
                "SETUP",
            )
            # Mock Weights
            ctx.buffer.write("adjusted_weights", {"experience": 2.0}, "SETUP")

            engine = ContentOptimizerEngine(ctx)
            await engine.execute()

            # Check if logic ran without error
            if ctx.buffer.read("optimized_content") is None:
                return False, "optimized_content not written to buffer"
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

    # Test 5: Optimizer Handles Missing Data Gracefully
    print("\n[TEST 5] test_optimizer_handles_missing_data")
    try:
        async def run_test():
            ctx = SovereignContext()
            # Don't write hop2_enrichment

            engine = ContentOptimizerEngine(ctx)
            result = await engine.execute()

            # Should return empty list, not crash
            if result != []:
                return False, f"Expected empty list, got {result}"
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

    # Test 6: Weight Adjustment with Multiple Signals
    print("\n[TEST 6] test_weight_adjustment_multiple_signals")
    try:
        async def run_test():
            ctx = SovereignContext()
            ctx.add_signal("ATS_FAILURE")
            ctx.add_signal("QUALITY_FAILURE")

            engine = WeightAdjustmentEngine(ctx)
            result = await engine.execute()

            if result.get("skills") != 1.25:
                return False, f"Expected skills=1.25, got {result.get('skills')}"
            if result.get("experience") != 1.30:
                return False, f"Expected experience=1.30, got {result.get('experience')}"
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
        print("\n🎉 ALL TESTS PASSED - Phase 4 Domain Expansion is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding to Phase 5")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
