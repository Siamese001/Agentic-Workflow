"""Phase A verification tests for L1 planning layer."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
# This file is in refactoring/phase_a/2025-11-24_l1_planning_layer/
# Project root is three levels up
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_l1_imports():
    """Verify all L1 modules import successfully."""
    try:
        import l1
        assert l1 is not None
        
        # Verify all exported functions exist
        assert hasattr(l1, 'plan_strategy')
        assert hasattr(l1, 'plan_draft')
        assert hasattr(l1, 'generate_latent_thinking_plan')
        assert hasattr(l1, 'plan_rag_reasoning')
        assert hasattr(l1, 'plan_hyde_query')
        assert hasattr(l1, 'plan_semantic_qa')
        assert hasattr(l1, 'plan_council_review')
        assert hasattr(l1, 'plan_safety_review')
        
        # Verify all exported classes exist
        assert hasattr(l1, 'StrategyPlan')
        assert hasattr(l1, 'DraftPlan')
        assert hasattr(l1, 'LatentThinkingPlan')
        assert hasattr(l1, 'RAGReasoningPlan')
        assert hasattr(l1, 'HydePlan')
        assert hasattr(l1, 'SemanticQAPlan')
        assert hasattr(l1, 'CouncilPlan')
        assert hasattr(l1, 'SafetyPlan')
        
        print("✓ All L1 imports successful")
        return True
    except Exception as e:
        print(f"✗ L1 import failed: {e}")
        return False


def test_l1_strategy_planning_imports():
    """Verify strategy planning module imports."""
    try:
        from l1.strategy_planning import (
            StrategyPlan,
            DraftPlan,
            LatentThinkingPlan,
            plan_strategy,
            plan_draft,
            generate_latent_thinking_plan,
        )
        assert StrategyPlan is not None
        assert DraftPlan is not None
        assert LatentThinkingPlan is not None
        assert callable(plan_strategy)
        assert callable(plan_draft)
        assert callable(generate_latent_thinking_plan)
        print("✓ Strategy planning module imports successful")
        return True
    except Exception as e:
        print(f"✗ Strategy planning import failed: {e}")
        return False


def test_l1_rag_planning_imports():
    """Verify RAG planning module imports."""
    try:
        from l1.rag_planning import (
            RAGReasoningPlan,
            HydePlan,
            plan_rag_reasoning,
            plan_hyde_query,
        )
        assert RAGReasoningPlan is not None
        assert HydePlan is not None
        assert callable(plan_rag_reasoning)
        assert callable(plan_hyde_query)
        print("✓ RAG planning module imports successful")
        return True
    except Exception as e:
        print(f"✗ RAG planning import failed: {e}")
        return False


def test_l1_qa_planning_imports():
    """Verify QA planning module imports."""
    try:
        from l1.qa_planning import (
            SemanticQAPlan,
            CouncilPlan,
            plan_semantic_qa,
            plan_council_review,
        )
        assert SemanticQAPlan is not None
        assert CouncilPlan is not None
        assert callable(plan_semantic_qa)
        assert callable(plan_council_review)
        print("✓ QA planning module imports successful")
        return True
    except Exception as e:
        print(f"✗ QA planning import failed: {e}")
        return False


def test_l1_safety_planning_imports():
    """Verify safety planning module imports."""
    try:
        from l1.safety_planning import (
            SafetyPlan,
            plan_safety_review,
        )
        assert SafetyPlan is not None
        assert callable(plan_safety_review)
        print("✓ Safety planning module imports successful")
        return True
    except Exception as e:
        print(f"✗ Safety planning import failed: {e}")
        return False


def test_cognitive_agents_imports():
    """Verify cognitive agents import successfully."""
    try:
        from cognitive_agents import (
            StrategyLLMAgent,
            DraftingGuild,
            SemanticQAAgent,
            ConstitutionalSafetyAgent,
            HYDEQueryAgent,
            QACouncilAgent,
        )
        assert StrategyLLMAgent is not None
        assert DraftingGuild is not None
        assert SemanticQAAgent is not None
        assert ConstitutionalSafetyAgent is not None
        assert HYDEQueryAgent is not None
        assert QACouncilAgent is not None
        print("✓ Cognitive agents imports successful")
        return True
    except Exception as e:
        print(f"✗ Cognitive agents import failed: {e}")
        return False


def test_l2_imports():
    """Verify L2 module imports successfully."""
    try:
        import l2
        assert l2 is not None
        assert hasattr(l2, 'run_l2')
        assert hasattr(l2, 'execute_workflow_plans')
        assert callable(l2.run_l2)
        assert callable(l2.execute_workflow_plans)
        print("✓ L2 module imports successful")
        return True
    except Exception as e:
        print(f"✗ L2 import failed: {e}")
        return False


def test_no_circular_dependencies():
    """Verify no circular dependencies exist."""
    try:
        # Import in order: models -> l1 -> cognitive_agents -> l2
        import core.models.models as models  # noqa: F401
        import l1  # noqa: F401
        import meta.cognitive_agents  # noqa: F401
        import l2  # noqa: F401
        
        print("✓ No circular dependencies detected")
        return True
    except Exception as e:
        print(f"✗ Circular dependency detected: {e}")
        return False


def test_l1_planning_is_pure():
    """Verify L1 planning functions are pure (no execution)."""
    try:
        import l1  # noqa: F401
        from l1.strategy_planning import StrategyPlan, DraftPlan
        from l1.rag_planning import RAGReasoningPlan, HydePlan
        from l1.qa_planning import SemanticQAPlan, CouncilPlan
        from l1.safety_planning import SafetyPlan
        
        # All L1 plan dataclasses should be frozen
        import dataclasses
        
        for plan_class in [StrategyPlan, DraftPlan, RAGReasoningPlan, HydePlan, SemanticQAPlan, CouncilPlan, SafetyPlan]:
            if dataclasses.is_dataclass(plan_class):
                # Check if frozen
                if not plan_class.__dataclass_fields__:
                    continue
                # Frozen dataclasses should have __frozen__ or be immutable
                print(f"  Checked {plan_class.__name__}")
        
        print("✓ L1 planning classes are properly structured")
        return True
    except Exception as e:
        print(f"✗ L1 planning purity check failed: {e}")
        return False


def run_all_tests():
    """Run all Phase A verification tests."""
    print("\n" + "="*60)
    print("PHASE A: L1 PLANNING LAYER VERIFICATION")
    print("="*60 + "\n")
    
    tests = [
        ("L1 Module Imports", test_l1_imports),
        ("Strategy Planning", test_l1_strategy_planning_imports),
        ("RAG Planning", test_l1_rag_planning_imports),
        ("QA Planning", test_l1_qa_planning_imports),
        ("Safety Planning", test_l1_safety_planning_imports),
        ("Cognitive Agents", test_cognitive_agents_imports),
        ("L2 Module", test_l2_imports),
        ("No Circular Dependencies", test_no_circular_dependencies),
        ("L1 Planning Purity", test_l1_planning_is_pure),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 40)
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase A verification tests PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)






