"""
Phase 5 Governance Test Runner.

Runs the Phase 5 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 5 governance tests."""
    print("=" * 70)
    print("PHASE 5 GOVERNANCE TESTS")
    print("=" * 70)

    from apps_rg.engines.base.sovereign_context import SovereignContext
    from apps_rg.engines.refinement.section_ranker_engine import SectionRankerEngine
    from apps_rg.engines.refinement.template_optimizer_engine import TemplateOptimizerEngine
    from apps_rg.engines.safety.ats_compatibility_engine import ATSCompatibilityEngine
    from apps_rg.engines.safety.void_compliance_engine import VoidComplianceEngine

    passed = 0
    failed = 0

    # Test 1: Ranker Reorders Content
    print("\n[TEST 1] test_ranker_reorders_content")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Mock data - use dict with keys that match strategy order
            ctx.buffer.write("optimized_content", {"education": {}, "skills": {}}, "SETUP")
            ctx.buffer.write("mission_input", {"role_type": "technical"}, "SETUP")

            engine = SectionRankerEngine(ctx)
            # Inject strategy for test - must include 'default' as fallback
            engine.strategies = {
                "technical": ["skills", "education"],
                "default": ["skills", "education"],
            }

            await engine.execute()

            ranked = ctx.buffer.read("ranked_content")
            if ranked is None:
                return False, "ranked_content not written"
            keys = list(ranked.keys())
            if len(keys) < 2:
                return False, f"Expected at least 2 keys, got {keys}"
            if keys[0] != "skills":
                return False, f"Expected 'skills' first, got {keys[0]}"
            if keys[1] != "education":
                return False, f"Expected 'education' second, got {keys[1]}"
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

    # Test 2: ATS Signals Failure
    print("\n[TEST 2] test_ats_signals_failure")
    try:

        async def run_test():
            ctx = SovereignContext()
            ctx.buffer.write("ranked_content", {"summary": "<table>bad</table>"}, "SETUP")

            engine = ATSCompatibilityEngine(ctx)
            await engine.execute()

            if "ATS_FAILURE" not in ctx.signals:
                return False, "ATS_FAILURE signal not triggered"
            report = ctx.buffer.read("ats_report")
            if report["valid"] is not False:
                return False, f"Expected valid=False, got {report['valid']}"
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

    # Test 3: Template Optimizer Reads JD
    print("\n[TEST 3] test_template_optimizer_reads_jd")
    try:

        async def run_test():
            ctx = SovereignContext()
            ctx.buffer.write("mission_input", {"job_description": "Senior Manager role"}, "SETUP")

            engine = TemplateOptimizerEngine(ctx)
            result = await engine.execute()

            if result.get("job_type") != "executive":
                return False, f"Expected 'executive', got {result.get('job_type')}"
            if ctx.buffer.read("template_strategy") is None:
                return False, "template_strategy not written to buffer"
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

    # Test 4: ATS Passes Clean Content
    print("\n[TEST 4] test_ats_passes_clean_content")
    try:

        async def run_test():
            ctx = SovereignContext()
            ctx.buffer.write("ranked_content", {"summary": "Clean text content"}, "SETUP")

            engine = ATSCompatibilityEngine(ctx)
            result = await engine.execute()

            if result["valid"] is not True:
                return False, f"Expected valid=True, got {result['valid']}"
            if "ATS_FAILURE" in ctx.signals:
                return False, "ATS_FAILURE signal should not be triggered"
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

    # Test 5: Void Compliance Writes Report
    print("\n[TEST 5] test_void_compliance_writes_report")
    try:

        async def run_test():
            ctx = SovereignContext()

            engine = VoidComplianceEngine(ctx)
            result = await engine.execute()

            if ctx.buffer.read("compliance_audit") is None:
                return False, "compliance_audit not written to buffer"
            # Should be clean (no archives imports in our codebase)
            if result.get("clean") is not True:
                return False, f"Expected clean=True, got {result.get('clean')}"
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

    # Test 6: Ranker Falls Back to Enrichment
    print("\n[TEST 6] test_ranker_fallback_to_enrichment")
    try:

        async def run_test():
            ctx = SovereignContext()
            # Don't write optimized_content, only hop2_enrichment
            ctx.buffer.write("hop2_enrichment", {"skills": {}, "experience": {}}, "SETUP")

            engine = SectionRankerEngine(ctx)
            await engine.execute()

            ranked = ctx.buffer.read("ranked_content")
            if ranked is None:
                return False, "ranked_content not written"
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
        print("\n🎉 ALL TESTS PASSED - Phase 5 Governance is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
