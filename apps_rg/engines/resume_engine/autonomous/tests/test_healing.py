from __future__ import annotations
"""
Unit Tests for Phase 2: Self-Healing Components

Tests the core self-healing functionality:
- SignalRouterAgent
- AgentFactory
- HealingCycle
- HealingOrchestratorAgent
- ConvergenceDetectorAgent
- AutomaticRollback
"""

import pytest

from ..context import ResumeEngineContext
from ..healing import (
    AgentFactory,
    AutomaticRollback,
    ConvergenceDetectorAgent,
    CycleResult,
    HealingCycle,
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


class TestSignalRouter:
    """Tests for SignalRouterAgent class."""

    def test_get_agents_for_quality_failure(self):
        """Test agent routing for QUALITY_FAILURE signal."""
        signals = {"QUALITY_FAILURE"}
        agents = SignalRouterAgent.get_agents_for_signals(signals)

        assert "ContentQualityAgent" in agents
        assert "FactCheckAgent" in agents

    def test_get_agents_for_multiple_signals(self):
        """Test agent routing for multiple signals."""
        signals = {"QUALITY_FAILURE", "BRAND_VIOLATION"}
        agents = SignalRouterAgent.get_agents_for_signals(signals)

        assert "ContentQualityAgent" in agents
        assert "BrandComplianceAgent" in agents

    def test_get_agents_for_unknown_signal(self):
        """Test agent routing for unknown signal."""
        signals = {"UNKNOWN_SIGNAL"}
        agents = SignalRouterAgent.get_agents_for_signals(signals)

        assert agents == []

    def test_has_critical_signal_true(self):
        """Test critical signal detection - positive case."""
        signals = {"QUALITY_FAILURE", "CRITICAL_FAILURE"}
        assert SignalRouterAgent.has_critical_signal(signals) is True

    def test_has_critical_signal_false(self):
        """Test critical signal detection - negative case."""
        signals = {"QUALITY_FAILURE", "BRAND_VIOLATION"}
        assert SignalRouterAgent.has_critical_signal(signals) is False

    def test_determine_strategy_cycle_1(self):
        """Test strategy determination for cycle 1."""
        strategy = SignalRouterAgent.determine_strategy(1, set(), set())
        assert strategy == HealingStrategy.FULL_DIAGNOSTIC

    def test_determine_strategy_no_signals(self):
        """Test strategy determination with no signals."""
        strategy = SignalRouterAgent.determine_strategy(2, set(), set())
        assert strategy == HealingStrategy.VERIFICATION_ONLY

    def test_determine_strategy_quality_focus(self):
        """Test strategy determination for quality signals."""
        signals = {"QUALITY_FAILURE"}
        strategy = SignalRouterAgent.determine_strategy(2, signals, set())
        assert strategy == HealingStrategy.QUALITY_FOCUS

    def test_determine_strategy_compliance_focus(self):
        """Test strategy determination for compliance signals."""
        signals = {"BRAND_VIOLATION"}
        strategy = SignalRouterAgent.determine_strategy(2, signals, set())
        assert strategy == HealingStrategy.COMPLIANCE_FOCUS

    def test_determine_strategy_surgical_strike(self):
        """Test strategy determination for mixed signals."""
        signals = {"QUALITY_FAILURE", "BRAND_VIOLATION"}
        strategy = SignalRouterAgent.determine_strategy(2, signals, set())
        assert strategy == HealingStrategy.SURGICAL_STRIKE


class TestAgentFactory:
    """Tests for AgentFactory class."""

    def test_create_all_agents(self, ctx):
        """Test creating all agents."""
        agents = AgentFactory.create_all_agents(ctx)

        assert len(agents) == 7
        agent_names = [a.name for a in agents]
        assert "ContentQualityAgent" in agent_names
        assert "TestPilot" in agent_names

    def test_create_agents_by_name(self, ctx):
        """Test creating specific agents by name."""
        names = ["ContentQualityAgent", "TestPilot"]
        agents = AgentFactory.create_agents_by_name(ctx, names)

        assert len(agents) == 2
        assert agents[0].name == "ContentQualityAgent"
        assert agents[1].name == "TestPilot"

    def test_create_agents_by_name_unknown(self, ctx):
        """Test creating agents with unknown name."""
        names = ["UnknownAgent", "ContentQualityAgent"]
        agents = AgentFactory.create_agents_by_name(ctx, names)

        assert len(agents) == 1
        assert agents[0].name == "ContentQualityAgent"

    def test_create_quality_agents(self, ctx):
        """Test creating quality-focused agents."""
        agents = AgentFactory.create_quality_agents(ctx)

        assert len(agents) == 3
        agent_names = [a.name for a in agents]
        assert "ContentQualityAgent" in agent_names
        assert "FactCheckAgent" in agent_names
        assert "TestPilot" in agent_names

    def test_create_compliance_agents(self, ctx):
        """Test creating compliance-focused agents."""
        agents = AgentFactory.create_compliance_agents(ctx)

        assert len(agents) == 4
        agent_names = [a.name for a in agents]
        assert "BrandComplianceAgent" in agent_names
        assert "ATSCompatibilityAgent" in agent_names


class TestHealingCycle:
    """Tests for HealingCycle class."""

    @pytest.mark.asyncio
    async def test_execute_full_diagnostic(self, ctx, valid_resume):
        """Test executing a full diagnostic cycle."""
        ctx.current_resume = valid_resume

        cycle = HealingCycle(ctx, cycle_number=1)
        result = await cycle.execute(HealingStrategy.FULL_DIAGNOSTIC)

        assert result.cycle_number == 1
        assert result.strategy == HealingStrategy.FULL_DIAGNOSTIC
        assert len(result.agents_executed) == 7
        assert result.duration_ms > 0

    @pytest.mark.asyncio
    async def test_execute_verification_only(self, ctx, valid_resume):
        """Test executing verification-only cycle."""
        ctx.current_resume = valid_resume

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        assert result.strategy == HealingStrategy.VERIFICATION_ONLY
        assert "TestPilot" in result.agents_executed
        assert len(result.agents_executed) == 1

    @pytest.mark.asyncio
    async def test_execute_quality_focus(self, ctx, valid_resume):
        """Test executing quality-focused cycle."""
        ctx.current_resume = valid_resume

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(HealingStrategy.QUALITY_FOCUS)

        assert result.strategy == HealingStrategy.QUALITY_FOCUS
        assert "ContentQualityAgent" in result.agents_executed
        assert "FactCheckAgent" in result.agents_executed

    @pytest.mark.asyncio
    async def test_execute_surgical_strike(self, ctx, valid_resume):
        """Test executing surgical strike cycle."""
        ctx.current_resume = valid_resume
        ctx.add_signal("QUALITY_FAILURE")

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(HealingStrategy.SURGICAL_STRIKE)

        assert result.strategy == HealingStrategy.SURGICAL_STRIKE
        assert "ContentQualityAgent" in result.agents_executed or "FactCheckAgent" in result.agents_executed

    @pytest.mark.asyncio
    async def test_rollback_on_critical_signal(self, ctx, valid_resume):
        """Test rollback triggered by critical signal."""
        ctx.current_resume = valid_resume.copy()
        ctx.update_section("summary", "Modified summary")
        ctx.add_signal("CRITICAL_FAILURE")

        cycle = HealingCycle(ctx, cycle_number=2)
        result = await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        assert result.rollback_triggered is True
        assert "CRITICAL_FAILURE" not in ctx.signals

    @pytest.mark.asyncio
    async def test_convergence_detection(self, ctx, valid_resume):
        """Test convergence detection in cycle result."""
        ctx.current_resume = valid_resume

        cycle = HealingCycle(ctx, cycle_number=1)
        result = await cycle.execute(HealingStrategy.FULL_DIAGNOSTIC)

        # Valid resume should converge
        assert result.converged is True


class TestConvergenceDetector:
    """Tests for ConvergenceDetectorAgent class."""

    def test_is_converged_true(self, ctx, valid_resume):
        """Test convergence detection - converged case."""
        ctx.current_resume = valid_resume
        ctx.record_result("Agent1", passed=True)

        detector = ConvergenceDetectorAgent(ctx)
        assert detector.is_converged() is True

    def test_is_converged_false(self, ctx, valid_resume):
        """Test convergence detection - not converged case."""
        ctx.current_resume = valid_resume
        ctx.add_signal("QUALITY_FAILURE")

        detector = ConvergenceDetectorAgent(ctx)
        assert detector.is_converged() is False

    def test_record_state(self, ctx):
        """Test state recording."""
        ctx.add_signal("SIGNAL_A")

        detector = ConvergenceDetectorAgent(ctx)
        detector.record_state()

        assert len(detector.history) == 1
        assert "SIGNAL_A" in detector.history[0]

    def test_is_oscillating_false(self, ctx):
        """Test oscillation detection - not oscillating."""
        detector = ConvergenceDetectorAgent(ctx)

        # Not enough history
        assert detector.is_oscillating() is False

    def test_get_stuck_signals(self, ctx):
        """Test stuck signal detection."""
        detector = ConvergenceDetectorAgent(ctx)

        ctx.signals = {"SIGNAL_A", "SIGNAL_B"}
        detector.record_state()

        ctx.signals = {"SIGNAL_A"}  # SIGNAL_A persists
        detector.record_state()

        stuck = detector.get_stuck_signals()
        assert "SIGNAL_A" in stuck


class TestAutomaticRollback:
    """Tests for AutomaticRollback class."""

    def test_should_rollback_true(self, ctx):
        """Test rollback decision - should rollback."""
        ctx.add_signal("CRITICAL_FAILURE")

        rollback = AutomaticRollback(ctx)
        assert rollback.should_rollback() is True

    def test_should_rollback_false(self, ctx):
        """Test rollback decision - should not rollback."""
        ctx.add_signal("QUALITY_FAILURE")

        rollback = AutomaticRollback(ctx)
        assert rollback.should_rollback() is False

    def test_execute_rollback(self, ctx, valid_resume):
        """Test rollback execution."""
        ctx.current_resume = valid_resume.copy()
        ctx.update_section("summary", "Modified")
        ctx.add_signal("CRITICAL_FAILURE")

        rollback = AutomaticRollback(ctx)
        result = rollback.execute_rollback()

        assert result is True
        assert rollback.rollback_count == 1
        assert "CRITICAL_FAILURE" not in ctx.signals
        assert ctx.current_resume["summary"] == valid_resume["summary"]

    def test_max_rollbacks_limit(self, ctx):
        """Test max rollbacks limit."""
        ctx.add_signal("CRITICAL_FAILURE")

        rollback = AutomaticRollback(ctx)
        rollback.rollback_count = 3  # At max

        assert rollback.should_rollback() is False

    def test_reset(self, ctx):
        """Test rollback counter reset."""
        rollback = AutomaticRollback(ctx)
        rollback.rollback_count = 2

        rollback.reset()

        assert rollback.rollback_count == 0


class TestCycleResult:
    """Tests for CycleResult dataclass."""

    def test_cycle_result_creation(self):
        """Test CycleResult creation."""
        result = CycleResult(
            cycle_number=1,
            strategy=HealingStrategy.FULL_DIAGNOSTIC,
            agents_executed=["Agent1", "Agent2"],
            signals_before={"SIGNAL_A"},
            signals_after=set(),
            passed_agents=["Agent1", "Agent2"],
            failed_agents=[],
            rollback_triggered=False,
            converged=True,
            duration_ms=100.0,
        )

        assert result.cycle_number == 1
        assert result.strategy == HealingStrategy.FULL_DIAGNOSTIC
        assert len(result.agents_executed) == 2
        assert result.converged is True


class TestHealingStrategy:
    """Tests for HealingStrategy enum."""

    def test_strategy_values(self):
        """Test strategy enum values."""
        assert HealingStrategy.FULL_DIAGNOSTIC.value == "full_diagnostic"
        assert HealingStrategy.SURGICAL_STRIKE.value == "surgical_strike"
        assert HealingStrategy.VERIFICATION_ONLY.value == "verification_only"
        assert HealingStrategy.QUALITY_FOCUS.value == "quality_focus"
        assert HealingStrategy.COMPLIANCE_FOCUS.value == "compliance_focus"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
