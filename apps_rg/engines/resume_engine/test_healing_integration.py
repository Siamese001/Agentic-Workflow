from __future__ import annotations
"""
Integration Tests for Phase 2: Self-Healing

Tests the integration of self-healing components:
- HealingOrchestratorAgent with multiple cycles
- Signal-based routing across cycles
- Rollback integration
- Convergence across cycles
"""
import re


import pytest

from ..context import ResumeEngineContext
from ..healing import (
    ConvergenceDetectorAgent,
    HealingCycle,
    HealingOrchestratorAgent,
    HealingStrategy,
    SignalRouterAgent,
)


@pytest.fixture
def ctx():
    """Create a fresh context for each test."""
    return ResumeEngineContext()


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40% through optimization."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
        "education": "BS Computer Science, MIT, 2010",
    }


@pytest.fixture
def problematic_resume():
    """Create a resume with multiple issues."""
    return {
        "summary": "I am a developer.",
        "experience": "Worked on stuff",
        "skills": "",
    }


class TestHealingOrchestratorIntegration:
    """Integration tests for HealingOrchestratorAgent."""

    @pytest.mark.asyncio
    async def test_orchestrator_valid_resume_converges(self, ctx, valid_resume):
        """Test orchestrator converges with valid resume."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Software Engineer"

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=3)
        result = await orchestrator.run()

        assert result.success is True
        assert result.convergence_cycle is not None
        assert result.convergence_cycle <= 2  # Should converge quickly
        assert len(result.cycle_results) <= 3

    @pytest.mark.asyncio
    async def test_orchestrator_problematic_resume(self, ctx, problematic_resume):
        """Test orchestrator with problematic resume."""
        ctx.current_resume = problematic_resume
        ctx.JobDescription = "Software Engineer"

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # May not converge due to issues
        assert result.total_cycles <= 2
        assert len(result.final_signals) > 0 or not result.success

    @pytest.mark.asyncio
    async def test_orchestrator_respects_max_cycles(self, ctx, problematic_resume):
        """Test orchestrator respects max_cycles limit."""
        ctx.current_resume = problematic_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=1)
        result = await orchestrator.run()

        assert result.total_cycles == 1

    @pytest.mark.asyncio
    async def test_orchestrator_tracks_cycle_results(self, ctx, valid_resume):
        """Test orchestrator tracks all cycle results."""
        ctx.current_resume = valid_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=3)
        result = await orchestrator.run()

        assert len(result.cycle_results) > 0
        assert all(isinstance(cr, type(result.cycle_results[0])) for cr in result.cycle_results)

        # First cycle should be FULL_DIAGNOSTIC
        assert result.cycle_results[0].strategy == HealingStrategy.FULL_DIAGNOSTIC

    @pytest.mark.asyncio
    async def test_orchestrator_with_reflection(self, ctx, valid_resume):
        """Test orchestrator runs reflection agent."""
        ctx.current_resume = valid_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2, enable_reflection=True)
        await orchestrator.run()

        # Reflection should have recorded insights
        assert "reflection" in ctx.results or "ReflectionAgent" in ctx.results

    @pytest.mark.asyncio
    async def test_orchestrator_without_reflection(self, ctx, valid_resume):
        """Test orchestrator without reflection agent."""
        ctx.current_resume = valid_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2, enable_reflection=False)
        result = await orchestrator.run()

        assert result.success is True


class TestMultiCycleHealing:
    """Tests for multi-cycle healing behavior."""

    @pytest.mark.asyncio
    async def test_strategy_changes_across_cycles(self, ctx, valid_resume):
        """Test that strategy changes based on signals."""
        ctx.current_resume = valid_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=3)
        result = await orchestrator.run()

        # First cycle is always FULL_DIAGNOSTIC
        assert result.cycle_results[0].strategy == HealingStrategy.FULL_DIAGNOSTIC

        # Subsequent cycles should adapt
        if len(result.cycle_results) > 1:
            assert result.cycle_results[1].strategy != HealingStrategy.FULL_DIAGNOSTIC

    @pytest.mark.asyncio
    async def test_signals_propagate_between_cycles(self, ctx, problematic_resume):
        """Test that signals propagate between cycles."""
        ctx.current_resume = problematic_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # First cycle should detect issues
        first_cycle = result.cycle_results[0]
        assert len(first_cycle.signals_after) > 0

    @pytest.mark.asyncio
    async def test_convergence_stops_cycles(self, ctx, valid_resume):
        """Test that convergence stops further cycles."""
        ctx.current_resume = valid_resume

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=5)
        result = await orchestrator.run()

        # Should converge before max cycles
        assert result.total_cycles < 5
        assert result.success is True


class TestRollbackIntegration:
    """Tests for rollback integration with healing cycles."""

    @pytest.mark.asyncio
    async def test_rollback_on_critical_failure(self, ctx, valid_resume):
        """Test rollback triggered by critical failure."""
        ctx.current_resume = valid_resume.copy()
        original_summary = valid_resume["summary"]

        # Modify and add critical signal
        ctx.update_section("summary", "Bad summary")
        ctx.add_signal("CRITICAL_FAILURE")

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        assert result.rollback_triggered is True
        assert ctx.current_resume["summary"] == original_summary

    @pytest.mark.asyncio
    async def test_rollback_clears_critical_signals(self, ctx, valid_resume):
        """Test that rollback clears critical signals."""
        ctx.current_resume = valid_resume.copy()
        ctx.update_section("summary", "Modified")
        ctx.add_signal("CRITICAL_FAILURE")
        ctx.add_signal("QUALITY_FAILURE")  # Non-critical

        cycle = HealingCycle(ctx, cycle_number=2)
        await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        assert "CRITICAL_FAILURE" not in ctx.signals
        # Non-critical signals may still be present


class TestSignalRoutingIntegration:
    """Tests for signal-based routing integration."""

    @pytest.mark.asyncio
    async def test_quality_signals_route_to_quality_agents(self, ctx, valid_resume):
        """Test quality signals Route to quality agents."""
        ctx.current_resume = valid_resume
        ctx.add_signal("QUALITY_FAILURE")

        strategy = SignalRouterAgent.determine_strategy(2, ctx.signals, set())
        assert strategy == HealingStrategy.QUALITY_FOCUS

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(strategy)

        assert "ContentQualityAgent" in result.agents_executed or "FactCheckAgent" in result.agents_executed

    @pytest.mark.asyncio
    async def test_compliance_signals_route_to_compliance_agents(self, ctx, valid_resume):
        """Test compliance signals Route to compliance agents."""
        ctx.current_resume = valid_resume
        ctx.add_signal("BRAND_VIOLATION")

        strategy = SignalRouterAgent.determine_strategy(2, ctx.signals, set())
        assert strategy == HealingStrategy.COMPLIANCE_FOCUS

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(strategy)

        assert "BrandComplianceAgent" in result.agents_executed


class TestConvergenceIntegration:
    """Tests for convergence detection integration."""

    @pytest.mark.asyncio
    async def test_convergence_detector_with_orchestrator(self, ctx, valid_resume):
        """Test convergence detector works with orchestrator."""
        ctx.current_resume = valid_resume

        detector = ConvergenceDetectorAgent(ctx)

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=3)
        await orchestrator.run()

        # After successful run, should be converged
        assert detector.is_converged() is True

    @pytest.mark.asyncio
    async def test_convergence_with_problematic_resume(self, ctx, problematic_resume):
        """Test convergence detection with problematic resume."""
        ctx.current_resume = problematic_resume

        detector = ConvergenceDetectorAgent(ctx)

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # May not converge
        if not result.success:
            assert not detector.is_converged()


class TestBudgetIntegration:
    """Tests for budget management integration."""

    @pytest.mark.asyncio
    async def test_budget_tracked_across_cycles(self, ctx, valid_resume):
        """Test budget is tracked across healing cycles."""
        ctx.current_resume = valid_resume

        initial_cost = ctx.budget.current_cost

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Budget should be tracked (even if no LLM calls)
        assert ctx.budget.current_cost >= initial_cost
        assert not result.budget_exhausted

    @pytest.mark.asyncio
    async def test_budget_exhaustion_stops_cycles(self, ctx, problematic_resume):
        """Test that budget exhaustion stops healing cycles."""
        ctx.current_resume = problematic_resume  # Use problematic to prevent early convergence
        ctx.budget.max_cost = 0.0  # Exhaust budget immediately
        ctx.budget.current_cost = 0.001

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=5)
        result = await orchestrator.run()

        # Either budget exhausted OR converged in cycle 1
        # Budget check happens after cycle, so if it converges first, budget_exhausted is False
        assert result.total_cycles == 1  # Should stop after first cycle
        # With problematic resume, should hit budget limit
        if not result.success:
            assert result.budget_exhausted is True


class TestHealingResultIntegration:
    """Tests for HealingResult integration."""

    @pytest.mark.asyncio
    async def test_healing_result_completeness(self, ctx, valid_resume):
        """Test HealingResult contains all expected data."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Software Engineer"

        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=3)
        result = await orchestrator.run()

        # Check all fields are populated
        assert isinstance(result.success, bool)
        assert isinstance(result.total_cycles, int)
        assert isinstance(result.final_signals, set)
        assert isinstance(result.cycle_results, list)
        assert isinstance(result.total_duration_ms, float)
        assert isinstance(result.final_resume, dict)

        # Check resume is preserved
        assert "summary" in result.final_resume
        assert "experience" in result.final_resume


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
