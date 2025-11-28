#!/usr/bin/env python
"""Quick verification script for OpenAI-style reorganization completion."""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def verify_reorganization():
    """Verify OpenAI-style reorganization is complete and functional."""
    
    print("\n" + "="*70)
    print("OPENAI-STYLE REORGANIZATION VERIFICATION")
    print("="*70 + "\n")
    
    checks = []
    
    # Check 1: New structure imports
    try:
        import agents
        import orchestration
        import infrastructure
        import prompts
        import tools
        import safety
        import state
        # Use imports to avoid unused warnings
        _ = [agents, orchestration, infrastructure, prompts, tools, safety, state]
        checks.append(("New Structure", True, "All capability directories available"))
    except Exception as e:
        checks.append(("New Structure", False, str(e)))
    
    # Check 2: Agents subdirectories
    try:
        from agents import planning, execution
        # Use imports to avoid unused warnings
        _ = [planning, execution]
        checks.append(("Agents Structure", True, "Planning and execution subdirectories available"))
    except Exception as e:
        checks.append(("Agents Structure", False, str(e)))
    
    # Check 3: Core models available
    try:
        from core.models.models import (
            AgentCard,
            DraftingResult,
            QAResult,
            SafetyResult,
        )
        # Use imports to avoid unused warnings
        _ = [AgentCard, DraftingResult, QAResult, SafetyResult]
        checks.append(("Core Models", True, "All models available"))
    except Exception as e:
        checks.append(("Core Models", False, str(e)))
    
    # Check 4: No circular dependencies
    try:
        from l2.agents import StrategyLLMAgent
        from l1.strategy_planning import plan_strategy
        # Use imports to avoid unused warnings
        _ = [StrategyLLMAgent, plan_strategy]
        checks.append(("No Circular Dependencies", True, "Import order verified"))
    except Exception as e:
        checks.append(("No Circular Dependencies", False, str(e)))
    
    # Check 5: Execution agents available
    try:
        from l2.agents import (
            StrategyLLMAgent,
            DraftingGuild,
            SemanticQAAgent,
            ConstitutionalSafetyAgent,
        )
        # Use imports to avoid unused warnings
        _ = [StrategyLLMAgent, DraftingGuild, SemanticQAAgent, ConstitutionalSafetyAgent]
        checks.append(("Execution Agents", True, "All execution agents available"))
    except Exception as e:
        checks.append(("Execution Agents", False, str(e)))
    
    # Check 6: Planning agents available
    try:
        from l1.strategy_planning import plan_strategy
        from l1.drafting_planning import plan_drafting
        # Use imports to avoid unused warnings
        _ = [plan_strategy, plan_drafting]
        checks.append(("Planning Agents", True, "Planning functions available"))
    except Exception as e:
        checks.append(("Planning Agents", False, str(e)))
    
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
        print("\n🎉 REORGANIZATION: COMPLETE - All verification checks passed!\n")
        return 0
    else:
        print(f"\n⚠️  REORGANIZATION: INCOMPLETE - {failed} check(s) failed\n")
        return 1

if __name__ == "__main__":
    sys.exit(verify_reorganization())






