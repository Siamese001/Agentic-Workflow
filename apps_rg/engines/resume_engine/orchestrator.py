from __future__ import annotations
"""
Resume Engine Orchestrator - Self-Healing Mission Runner

This module provides the main orchestration loop for autonomous resume generation,
implementing self-healing cycles with strategic planning and signal-based routing.
"""
from typing import Any, Optional, Protocol, Dict, List


from typing import Any, Dict, List, Optional

from .agents import (
    ATSCompatibilityAgent,
    BrandComplianceAgent,
    ContentQualityAgent,
    FactCheckAgent,
    ReflectionAgent,
    SectionBalanceAgent,
    StrategicPlannerAgent,
    TemplateOptimizerAgent,
    TestPilot,
)
from .resume_base import ResumeAgent
from .context import ResumeEngineContext


async def run_resume_mission(
    JobDescription: str,
    master_resume: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]] = None,
    max_cycles: int = 5,
) -> Dict[str, Any]:
    """
    Run the autonomous resume generation mission.

    This is the main entry point for autonomous resume generation.
    It implements self-healing cycles with strategic planning.

    Args:
        JobDescription: Target job description
        master_resume: User's master resume data
        user_profile: Optional user profile for fact-checking
        max_cycles: Maximum healing cycles (default 5)

    Returns:
        Dictionary containing:
        - status: "success" or "failed"
        - resume: Final resume data
        - stats: Execution statistics
        - cycles_used: Number of cycles executed
    """
    print("\n" + "=" * 60)
    print("🚀 AUTONOMOUS RESUME GENERATION MISSION")
    print("=" * 60)

    # Initialize context
    ctx = ResumeEngineContext()
    ctx.JobDescription = JobDescription
    ctx.current_resume = master_resume.copy()
    ctx.user_profile = user_profile or {}
    ctx.max_cycles = max_cycles

    # Initialize all agents
    all_agents = [
        ContentQualityAgent(ctx),
        FactCheckAgent(ctx),
        BrandComplianceAgent(ctx),
        RgTemplateOptimizerAgent(ctx),
        SectionBalanceAgent(ctx),
        ATSCompatibilityAgent(ctx),
        TestPilot(ctx),
    ]

    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        ctx.signal_healing_cycle(cycle)
        print(f"\n{'=' * 40}")
        print(f"🧬 SELF-HEALING CYCLE {cycle}/{max_cycles}")
        print(f"{'=' * 40}")

        # Clear per-cycle tracking
        ctx.modified_sections.clear()
        ctx.impact_zone.clear()

        # Build agenda based on cycle and signals
        agenda: List[ResumeAgent] = []

        if cycle == 1:
            # Cycle 1: Full diagnostic - run all agents
            print("   📋 PLAN: Full system diagnostic")
            agenda = all_agents.copy()
        else:
            # Subsequent cycles: Strategic routing based on signals
            print(f"   🤔 STRATEGY: Analyzing {len(ctx.signals)} signals...")

            # Always run strategic planner first
            agenda.append(RgStrategicPlannerAgent(ctx))

            # Route based on signals
            if ctx.has_signal("QUALITY_FAILURE"):
                agenda.append(ContentQualityAgent(ctx))
                print("      → Priority: Content Quality")

            if ctx.has_signal("HALLUCINATION_DETECTED"):
                agenda.append(FactCheckAgent(ctx))
                print("      → Priority: Fact Checking")

            if ctx.has_signal("BRAND_VIOLATION"):
                agenda.append(BrandComplianceAgent(ctx))
                print("      → Priority: Brand Compliance")

            if ctx.has_signal("ATS_FAILURE"):
                agenda.append(ATSCompatibilityAgent(ctx))
                print("      → Priority: ATS Compatibility")

            if ctx.has_signal("BALANCE_ISSUE"):
                agenda.append(SectionBalanceAgent(ctx))
                print("      → Priority: Section Balance")

            if ctx.has_signal("TEST_FAILURE"):
                agenda.append(TestPilot(ctx))
                print("      → Priority: Test Validation")

            # If no specific signals, run TestPilot for verification
            if len(agenda) == 1:  # Only RgStrategicPlannerAgent
                agenda.append(TestPilot(ctx))
                print("      → Default: Verification")

        # Always add reflection at the end
        agenda.append(RgReflectionAgent(ctx))

        # Execute agenda
        print(f"\n   📋 Executing {len(agenda)} agents...")
        for agent in agenda:
            try:
                await agent.execute()
            except Exception as e:
                print(f"   ❌ Agent {agent.name} failed: {e}")
                ctx.record_result(agent.name, passed=False, details=str(e))

        # Check for critical regression and rollback
        if ctx.has_signal("TEST_FAILURE") and cycle > 1 and ctx.section_backups:
            print("   🚨 Critical regression detected. Rolling back...")
            ctx.rollback_all()
            ctx.remove_signal("TEST_FAILURE")

        # Check convergence
        if ctx.is_converged():
            print(f"\n✅ CONVERGED after {cycle} cycles")
            break

        # Budget check
        if not ctx.budget.check_budget():
            print(f"\n💸 Budget exhausted after {cycle} cycles")
            break

    # Final status
    success = ctx.is_converged()

    print("\n" + "=" * 60)
    print(f"{'✅ MISSION SUCCESS' if success else '⚠️ MISSION INCOMPLETE'}")
    print("=" * 60)

    stats = ctx.get_stats()
    print(f"   Cycles used: {cycle}/{max_cycles}")
    print(f"   Budget used: ${stats['budget_stats']['current_cost_usd']:.4f}")
    print(f"   Signals remaining: {len(ctx.signals)}")

    return {
        "status": "success" if success else "incomplete",
        "resume": ctx.current_resume,
        "stats": stats,
        "cycles_used": cycle,
        "converged": success,
    }


async def quick_validate(resume: Dict[str, Any], JobDescription: str = "") -> Dict[str, Any]:
    """
    Quick validation without full mission cycle.

    Runs all validation agents once and returns results.

    Args:
        resume: Resume data to validate
        JobDescription: Optional job description for ATS check

    Returns:
        Dictionary with validation results
    """
    ctx = ResumeEngineContext()
    ctx.current_resume = resume
    ctx.JobDescription = JobDescription

    agents = [
        ContentQualityAgent(ctx),
        FactCheckAgent(ctx),
        BrandComplianceAgent(ctx),
        SectionBalanceAgent(ctx),
        ATSCompatibilityAgent(ctx),
        TestPilot(ctx),
    ]

    for agent in agents:
        try:
            await agent.execute()
        except Exception as e:
            ctx.record_result(agent.name, passed=False, details=str(e))

    return {
        "valid": ctx.is_converged(),
        "results": ctx.results,
        "signals": list(ctx.signals),
    }
