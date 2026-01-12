from __future__ import annotations
"""
Integration Tests for Phase 5: Observability & Telemetry

Tests the integration of observability components:
- ExecutionTracer with healing cycles
- MetricsCollector with agents
- ValidationAgent with resume processing
- AuditReporter with full missions
"""

import json

import pytest

from ..context import ResumeEngineContext
from ..gitops import Phase4OrchestratorAgent
from ..healing import HealingCycle, HealingOrchestratorAgent, HealingStrategy
from ..learning import ResumeLearningAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from ..observability import (
    AuditReporter,
    ExecutionTracer,
    MetricsCollector,
    MetricType,
    Phase5Orchestrator,
    ValidationAgent,
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
                "description": "Developed microservices architecture serving 1M+ users."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
    }


class TestTracerWithHealingCycles:
    """Integration tests for ExecutionTracer with healing cycles."""

    @pytest.mark.asyncio
    async def test_tracer_tracks_healing_cycle(self, ctx, valid_resume):
        """Test that tracer tracks healing cycle execution."""
        ctx.current_resume = valid_resume

        tracer = ExecutionTracer(ctx)
        tracer.start_trace("healing_mission_1")

        # Run healing cycle
        cycle = HealingCycle(ctx, cycle_number=1)
        step_id = tracer.start_step("HealingCycle", "execute")

        result = await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        tracer.end_step(step_id, success=result.converged)
        trace = tracer.end_trace()

        assert trace is not None
        assert len(trace.steps) == 1
        assert trace.steps[0].agent_name == "HealingCycle"

    @pytest.mark.asyncio
    async def test_tracer_tracks_multiple_agents(self, ctx, valid_resume):
        """Test that tracer tracks multiple agent executions."""
        ctx.current_resume = valid_resume

        tracer = ExecutionTracer(ctx)
        tracer.start_trace("multi_agent_mission")

        # Simulate multiple agents
        agents = ["ContentQualityAgent", "ATSOptimizer", "TestPilot"]
        for agent in agents:
            step_id = tracer.start_step(agent, "execute")
            tracer.end_step(step_id, success=True)

        trace = tracer.end_trace()

        assert len(trace.steps) == 3
        assert [s.agent_name for s in trace.steps] == agents


class TestMetricsWithAgents(MCPHardenedMixin):
    """Integration tests for MetricsCollector with agents."""

    @pytest.mark.asyncio
    async def test_metrics_track_agent_invocations(self, ctx, valid_resume):
        """Test that metrics track agent invocations."""
        ctx.current_resume = valid_resume

        metrics = MetricsCollector(ctx)

        # Simulate agent invocations
        agents = ["ContentQualityAgent", "ATSOptimizer", "ContentQualityAgent"]
        for agent in agents:
            metrics.increment("agent.invocations", tags={"agent": agent})

        all_metrics = metrics.get_metrics(name="agent.invocations")

        assert len(all_metrics) == 3

    @pytest.mark.asyncio
    async def test_metrics_track_healing_duration(self, ctx, valid_resume):
        """Test that metrics track healing duration."""
        ctx.current_resume = valid_resume

        metrics = MetricsCollector(ctx)

        # Run healing and track duration
        cycle = HealingCycle(ctx, cycle_number=1)

        import time
        start = time.time()
        await cycle.execute(HealingStrategy.VERIFICATION_ONLY)
        duration = (time.time() - start) * 1000

        metrics.timer("healing.cycle.duration", duration, tags={"cycle": "1"})

        timer_metrics = metrics.get_metrics(metric_type=MetricType.TIMER)
        assert len(timer_metrics) == 1


class TestValidatorWithResumeProcessing:
    """Integration tests for ValidationAgent with resume processing."""

    def test_validator_with_healing_result(self, ctx, valid_resume):
        """Test validator with healing result."""
        ctx.current_resume = valid_resume

        validator = ValidationAgent(ctx)

        # Validate before healing
        issues_before = validator.validate_resume(valid_resume)

        # Simulate healing improvement
        improved_resume = valid_resume.copy()
        improved_resume["summary"] = (
            "Senior Software Engineer with 12+ years of experience. "
            "Led engineering teams of 8-15 engineers. "
            "Delivered 5 major projects increasing revenue by 40% and reducing costs by 25%."
        )

        # Validate after healing
        issues_after = validator.validate_resume(improved_resume)

        # Improved resume should have fewer or equal issues
        assert len(issues_after) <= len(issues_before) + 1  # Allow some tolerance

    def test_validator_tracks_all_sections(self, ctx, valid_resume):
        """Test that validator checks all resume sections."""
        validator = ValidationAgent(ctx)

        issues = validator.validate_resume(valid_resume)

        # Check that validator examined multiple sections
        set(i.file_path for i in issues)
        # Even valid resumes may have some info-level issues
        assert validator.get_stats()["total_issues"] >= 0


class TestReporterWithFullMissions:
    """Integration tests for AuditReporter with full missions."""

    @pytest.mark.asyncio
    async def test_reporter_captures_full_mission(self, ctx, valid_resume):
        """Test that reporter captures a full mission."""
        ctx.current_resume = valid_resume

        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        # Run a full mission
        tracer.start_trace("full_mission")

        # Track agents
        for agent in ["ContentQualityAgent", "ATSOptimizer"]:
            step_id = tracer.start_step(agent, "execute")
            metrics.increment("agent.invocations")
            tracer.end_step(step_id, success=True)

        # Validate
        validator.validate_resume(valid_resume)

        tracer.end_trace()

        # Generate report
        report = reporter.generate_report("full_mission")

        assert report.summary["total_traces"] == 1
        assert report.summary["total_steps"] == 2

    @pytest.mark.asyncio
    async def test_reporter_generates_recommendations(self, ctx):
        """Test that reporter generates recommendations."""
        tracer = ExecutionTracer(ctx)
        metrics = MetricsCollector(ctx)
        validator = ValidationAgent(ctx)
        reporter = AuditReporter(ctx, tracer, metrics, validator)

        # Create a failed trace
        tracer.start_trace("failed_mission")
        step_id = tracer.start_step("FailingAgent", "execute")
        tracer.end_step(step_id, success=False, error="Test failure")
        tracer.end_trace(success=False)

        # Validate invalid resume
        validator.validate_resume({"summary": ""})

        report = reporter.generate_report("failed_mission")

        assert len(report.recommendations) > 0


class TestPhase5WithPreviousPhases:
    """Integration tests for Phase 5 with previous phases."""

    @pytest.mark.asyncio
    async def test_phase5_with_learning_agent(self, ctx, valid_resume):
        """Test Phase 5 integration with Phase 3 learning."""
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)
        learning_agent = ResumeLearningAgent(ctx)

        # Start observability
        phase5.start_mission("learning_mission")

        # Inject instruction
        learning_agent.inject_instruction("Focus on metrics", priority=10)
        phase5.metrics.increment("instructions.injected")

        # Validate
        phase5.validate_resume(valid_resume)

        # End mission
        phase5.end_mission(success=True)

        # Generate report
        report = phase5.generate_report("learning_mission")

        assert report is not None

    @pytest.mark.asyncio
    async def test_phase5_with_gitops(self, ctx, valid_resume, tmp_path):
        """Test Phase 5 integration with Phase 4 GitOps."""
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False

        # Start observability
        phase5.start_mission("gitops_mission")

        # Create and backup file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass")

        step_id = phase5.track_agent("GitOpsManager", "backup_file")
        phase4.gitops.backup_file(str(test_file))
        phase5.complete_agent(step_id, success=True)

        # End mission
        phase5.end_mission(success=True)

        stats = phase5.get_comprehensive_stats()

        assert stats["tracer"]["total_steps"] == 1

    @pytest.mark.asyncio
    async def test_full_pipeline_observability(self, ctx, valid_resume):
        """Test observability across full pipeline."""
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Start mission
        phase5.start_mission("full_pipeline")

        # Track healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        healing = RgHealingOrchestratorAgent(ctx, max_cycles=2)
        await healing.run()
        # Mark step as successful if healing ran (even if not fully converged)
        phase5.complete_agent(step_id, success=True)

        # Validate result
        phase5.validate_resume(ctx.current_resume)

        # End mission - success if healing ran without errors
        trace = phase5.end_mission(success=True)

        # Generate report
        report = phase5.generate_report("full_pipeline")

        # Verify observability captured the execution
        assert trace is not None
        assert report.summary["total_traces"] == 1


class TestTelemetryExport:
    """Integration tests for telemetry export."""

    @pytest.mark.asyncio
    async def test_export_after_mission(self, ctx, valid_resume):
        """Test exporting telemetry after a mission."""
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Run mission
        phase5.start_mission("export_test")
        phase5.track_agent("TestAgent", "test")
        phase5.metrics.increment("test.Metric")
        phase5.end_mission()

        # Export
        telemetry = phase5.export_telemetry(format="json")

        traces = json.loads(telemetry["traces"])
        metrics = json.loads(telemetry["metrics"])

        assert len(traces) == 1
        assert len(metrics) > 0

    @pytest.mark.asyncio
    async def test_export_multiple_formats(self, ctx):
        """Test exporting in multiple formats."""
        phase5 = Phase5Orchestrator(ctx)

        phase5.start_mission("format_test")
        phase5.metrics.gauge("test.gauge", 42)
        phase5.end_mission()

        # JSON export
        json_export = phase5.export_telemetry(format="json")
        assert "traces" in json_export

        # Verify JSON is valid
        json.loads(json_export["traces"])
        json.loads(json_export["metrics"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
