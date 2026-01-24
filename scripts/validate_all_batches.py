#!/usr/bin/env python3
"""
Direct validation of all 6 batches without pytest import issues
"""

import sys
from pathlib import Path
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import all engines
from apps_rg.engines.base.base_resume_engine import BaseRGEngine
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
from apps_rg.engines.hops.hop2_enrichment_engine import EnrichmentEngine
from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine, CompetencyItem
from apps_rg.engines.generation.service_invoker_engine import ServiceInvokerEngine
from apps_rg.engines.refinement.weight_adjustment_engine import WeightAdjustmentEngine
from apps_rg.engines.refinement.content_optimizer_engine import ContentOptimizerEngine
from apps_rg.engines.refinement.section_ranker_engine import SectionRankerEngine
from apps_rg.engines.refinement.template_optimizer_engine import TemplateOptimizerEngine
from apps_rg.engines.safety.void_compliance_engine import VoidComplianceEngine
from apps_rg.engines.safety.ats_compatibility_engine import ATSCompatibilityEngine
from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT


def mock_ctx():
    """Create mock context."""
    ctx = MagicMock()
    ctx.signals = set()
    ctx.get_failed_results = MagicMock(return_value={})
    ctx.master_resume = {"experience": []}
    ctx.add_signal = MagicMock()
    return ctx


async def test_batch_1():
    """Test Batch 1: Foundation & Command."""
    print("\n" + "="*60)
    print("BATCH 1: Foundation & Command")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Base engine config hydration
    tests_total += 1
    try:
        class TestEngine(BaseRGEngine):
            async def execute(self): 
                pass
        
        engine = TestEngine(mock_ctx(), node_id="K.9")
        assert engine.config.id == "K.9"
        assert "count" in engine.thresholds
        print("✅ Base engine config hydration")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Base engine config hydration: {e}")
    
    # Test 2: Orchestrator HOP tracking
    tests_total += 1
    try:
        orch = ResumeOrchestratorEngine(mock_ctx())
        # Provide a longer JD to pass validation
        long_jd = "Software Engineer position requiring Python, AWS, Docker, and Kubernetes experience. Must have 5+ years of experience."
        result = await orch.execute(long_jd)
        assert len(orch.hop_checkpoints) >= 2
        assert result["status"] == "success"
        print("✅ Orchestrator HOP tracking")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Orchestrator HOP tracking: {e}")
    
    # Test 3: Frozen prompt access
    tests_total += 1
    try:
        engine = TestEngine(mock_ctx(), node_id="K.9")
        prompt = engine.get_frozen_prompt("k1_hyde_generation")
        assert "{company_name}" in prompt
        print("✅ Frozen prompt access")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Frozen prompt access: {e}")
    
    return tests_passed, tests_total


async def test_batch_2():
    """Test Batch 2: HOP Domain."""
    print("\n" + "="*60)
    print("BATCH 2: HOP Domain")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Clerk metrics extraction
    tests_total += 1
    try:
        engine = ClerkExtractionEngine(mock_ctx())
        text = "Managed a $50M+ budget and increased efficiency by 20% across 1,200 employees."
        metrics = engine._extract_metrics(text)
        assert "$50M+" in metrics
        assert "20%" in metrics
        print("✅ Clerk metrics extraction")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Clerk metrics extraction: {e}")
    
    # Test 2: Enrichment forbidden verbs
    tests_total += 1
    try:
        engine = EnrichmentEngine(mock_ctx())
        violations = engine._check_forbidden("I was responsible for managing")
        assert "responsible for" in violations
        print("✅ Enrichment forbidden verb detection")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Enrichment forbidden verb detection: {e}")
    
    return tests_passed, tests_total


async def test_batch_3():
    """Test Batch 3: Generation Domain."""
    print("\n" + "="*60)
    print("BATCH 3: Generation Domain")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: K9 word count validation
    tests_total += 1
    try:
        engine = GapClosureEngine(mock_ctx())
        items = [
            CompetencyItem("Good", "Balanced description", 25),
            CompetencyItem("Too Short", "Brief", 2),
        ]
        issues = engine._validate_word_counts(items)
        assert len(issues) == 1
        print("✅ K9 word count validation")
        tests_passed += 1
    except Exception as e:
        print(f"❌ K9 word count validation: {e}")
    
    # Test 2: Service invoker telemetry
    tests_total += 1
    try:
        engine = ServiceInvokerEngine(mock_ctx())
        engine.call_llm = AsyncMock(return_value="Success")
        result = await engine.execute("test", {"prompt": "test"})
        assert result["success"] is True
        assert "duration_ms" in result
        print("✅ Service invoker telemetry")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Service invoker telemetry: {e}")
    
    return tests_passed, tests_total


async def test_batch_4():
    """Test Batch 4: Refinement Part 1."""
    print("\n" + "="*60)
    print("BATCH 4: Refinement Part 1")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Weight adjustment with signals
    tests_total += 1
    try:
        ctx = mock_ctx()
        ctx.signals = {"ATS_FAILURE"}
        engine = WeightAdjustmentEngine(ctx)
        data = {"skills": "Python", "education": "BS"}
        result = await engine.execute(data)
        assert result["skills"]["applied_weight"] == 1.25
        print("✅ Weight adjustment with signals")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Weight adjustment with signals: {e}")
    
    # Test 2: Content optimizer impact scoring
    tests_total += 1
    try:
        engine = ContentOptimizerEngine(mock_ctx())
        bullets = [
            {"bullet_text": "Managed team", "quantified_metrics": []},
            {"bullet_text": "Increased by 50%", "quantified_metrics": ["50%"]},
        ]
        section = {"bullets": bullets}
        optimized = await engine.execute([section])
        assert "50%" in optimized[0]["bullets"][0]["bullet_text"]
        print("✅ Content optimizer impact scoring")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Content optimizer impact scoring: {e}")
    
    return tests_passed, tests_total


async def test_batch_5():
    """Test Batch 5: Refinement Part 2."""
    print("\n" + "="*60)
    print("BATCH 5: Refinement Part 2")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Section ranker ordering
    tests_total += 1
    try:
        ctx = mock_ctx()
        engine = SectionRankerEngine(ctx)
        engine.strategies = {"technical": ["skills", "experience", "education"], "default": ["experience", "education", "skills"]}
        resume = {"education": "BS", "experience": "Dev", "skills": "Python"}
        ordered = await engine.execute(resume, role_type="technical")
        keys = list(ordered.keys())
        assert keys[0] == "skills"
        print("✅ Section ranker ordering")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Section ranker ordering: {e}")
    
    # Test 2: Template optimizer detection
    tests_total += 1
    try:
        ctx = mock_ctx()
        engine = TemplateOptimizerEngine(ctx)
        # Use more explicit executive keywords
        job_type = engine._detect_job_type("Looking for a Vice President to lead the division as Chief Strategy Officer")
        assert job_type == "executive", f"Expected 'executive' but got '{job_type}'"
        print("✅ Template optimizer detection")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Template optimizer detection: {e}")
    
    return tests_passed, tests_total


async def test_batch_6():
    """Test Batch 6: Safety Domain."""
    print("\n" + "="*60)
    print("BATCH 6: Safety Domain")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: ATS clean pass
    tests_total += 1
    try:
        engine = ATSCompatibilityEngine(mock_ctx())
        clean_resume = {
            "experience": [{"company": "A"}],
            "education": "University"
        }
        result = await engine.execute(clean_resume)
        assert result["compatible"] is True
        print("✅ ATS clean pass")
        tests_passed += 1
    except Exception as e:
        print(f"❌ ATS clean pass: {e}")
    
    # Test 2: Void compliance forbidden check
    tests_total += 1
    try:
        engine = VoidComplianceEngine(mock_ctx())
        is_forbidden = engine._is_forbidden("archives.legacy")
        assert is_forbidden is True
        print("✅ Void compliance forbidden check")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Void compliance forbidden check: {e}")
    
    return tests_passed, tests_total


async def main():
    """Run all batch tests."""
    print("\n🛡️ SOVEREIGN V2.5 - 6-BATCH VALIDATION")
    
    all_results = []
    
    all_results.append(await test_batch_1())
    all_results.append(await test_batch_2())
    all_results.append(await test_batch_3())
    all_results.append(await test_batch_4())
    all_results.append(await test_batch_5())
    all_results.append(await test_batch_6())
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    total_passed = sum(r[0] for r in all_results)
    total_tests = sum(r[1] for r in all_results)
    
    for i, (passed, total) in enumerate(all_results, 1):
        status = "✅" if passed == total else "⚠️"
        print(f"{status} Batch {i}: {passed}/{total} passed")
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed ({100*total_passed/total_tests:.0f}%)")
    
    if total_passed == total_tests:
        print("\n🎉 ALL BATCH TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - total_passed} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
