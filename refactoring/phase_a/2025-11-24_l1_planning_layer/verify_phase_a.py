#!/usr/bin/env python
"""Quick verification script for Phase A completion."""

from pathlib import Path
import sys

# Add project root to path
# This file is in refactoring/phase_a/2025-11-24_l1_planning_layer/
# Project root is three levels up
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import sys

def verify_phase_a():
    """Verify Phase A L1 planning layer is complete and functional."""
    
    print("\n" + "="*70)
    print("PHASE A: L1 PLANNING LAYER VERIFICATION")
    print("="*70 + "\n")
    
    checks = []
    
    # Check 1: L1 imports
    try:
        import l1
        assert hasattr(l1, 'plan_strategy')
        assert hasattr(l1, 'plan_draft')
        assert hasattr(l1, 'plan_rag_reasoning')
        assert hasattr(l1, 'plan_hyde_query')
        assert hasattr(l1, 'plan_semantic_qa')
        assert hasattr(l1, 'plan_safety_review')
        checks.append(("L1 Planning Layer", True, "All planning functions available"))
    except Exception as e:
        checks.append(("L1 Planning Layer", False, str(e)))
    
    # Check 2: L2 imports
    try:
        import l2
        assert hasattr(l2, 'run_l2')
        assert hasattr(l2, 'execute_workflow_plans')
        checks.append(("L2 Execution Layer", True, "All execution functions available"))
    except Exception as e:
        checks.append(("L2 Execution Layer", False, str(e)))
    
    # Check 3: Cognitive agents
    try:
        from core.cognitive_agents import (
            StrategyLLMAgent,
            DraftingGuild,
            SemanticQAAgent,
            ConstitutionalSafetyAgent,
            HYDEQueryAgent,
            QACouncilAgent,
        )
        checks.append(("Cognitive Agents", True, "All agents available"))
    except Exception as e:
        checks.append(("Cognitive Agents", False, str(e)))
    
    # Check 4: Core models
    try:
        from core.models.models import (
            ExecutionContext,
            WorkflowPlanBundle,
            StrategyResult,
            RAGResult,
            DraftingResult,
            QAResult,
            SafetyResult,
        )
        checks.append(("Core Models", True, "All models available"))
    except Exception as e:
        checks.append(("Core Models", False, str(e)))
    
    # Check 5: No circular dependencies
    try:
        from core.models import models
        import l1
        from core import cognitive_agents
        import l2
        checks.append(("No Circular Dependencies", True, "Import order verified"))
    except Exception as e:
        checks.append(("No Circular Dependencies", False, str(e)))
    
    # Check 6: L1 plan dataclasses
    try:
        from l1 import (
            StrategyPlan,
            DraftPlan,
            LatentThinkingPlan,
            RAGReasoningPlan,
            HydePlan,
            SemanticQAPlan,
            CouncilPlan,
            SafetyPlan,
        )
        checks.append(("L1 Plan Dataclasses", True, "All plan types available"))
    except Exception as e:
        checks.append(("L1 Plan Dataclasses", False, str(e)))
    
    # Print results
    passed = 0
    failed = 0
    
    for name, success, message in checks:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name}")
        if not success:
            print(f"         Error: {message}")
        else:
            print(f"         {message}")
        print()
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("="*70)
    print(f"SUMMARY: {passed}/{len(checks)} checks passed")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 PHASE A: COMPLETE - All verification checks passed!\n")
        return 0
    else:
        print(f"\n⚠️  PHASE A: INCOMPLETE - {failed} check(s) failed\n")
        return 1

if __name__ == "__main__":
    sys.exit(verify_phase_a())
