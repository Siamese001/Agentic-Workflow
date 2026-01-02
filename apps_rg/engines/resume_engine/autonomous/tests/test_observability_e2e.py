from __future__ import annotations
"""
End-to-End Tests for Phase 5: Observability & Telemetry

Tests the complete observability workflow:
- Full mission with observability
- Report generation and export
- Integration with all previous phases
"""

import json

import pytest

from ..context import ResumeEngineContext
from ..gitops import Phase4OrchestratorAgent
from ..healing import HealingOrchestratorAgent, HealingResult, run_self_healing_mission
from ..learning import MemoryPersistence, ResumeLearningAgent
from ..observability import Phase5Orchestrator


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40%."
            },
            {
                "company": "StartupXYZ",
                "title": "Software Engineer",
                "description": "Built core platform features used by 100K+ customers."
            }
        ],
        "skills": ["Python", "JavaScript", "TypeScript", "AWS", "Docker", "Kubernetes"],
        "education": "BS Computer Science, MIT, 2010",
    }


@pytest.fixture
def JobDescription():
    """Sample job description."""
    return """
    Senior Software Engineer

    Requirements:
    - 5+ years of experience in software development
    - Strong Python and JavaScript skills
    - Experience with AWS and cloud infrastructure
    """


class TestFullMissionWithObservability:
    """Tests for full mission with observability."""

    @pytest.mark.asyncio
    async def test_mission_with_full_observability(self, valid_resume, JobDescription):
        """Test a complete mission with full observability."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase5 = Phase5Orchestrator(ctx)

        # Start mission
        trace_id = phase5.start_mission("e2e_mission_1")

        # Track healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )
        phase5.complete_agent(step_id, success=result.success)

        # Validate
        phase5.validate_resume(valid_resume)

        # End mission
        trace = phase5.end_mission(success=result.success)

        # Verify observability captured everything
        assert trace is not None
        assert trace.trace_id == trace_id
        assert len(trace.steps) >= 1

    @pytest.mark.asyncio
    async def test_mission_metrics_collection(self, valid_resume, JobDescription):
        """Test that mission collects proper metrics."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Run mission with metrics
        phase5.start_mission("metrics_mission")

        # Track various operations
        for i in range(3):
            step_id = phase5.track_agent(f"Agent{i}", "execute")
            phase5.metrics.timer(f"agent.{i}.duration", 100 * (i + 1))
            phase5.complete_agent(step_id, success=True)

        phase5.end_mission()

        # Verify metrics
        stats = phase5.metrics.get_stats()
        assert stats["total_metrics"] > 0


class TestReportGenerationAndExport:
    """Tests for report generation and export."""

    @pytest.mark.asyncio
    async def test_generate_comprehensive_report(self, valid_resume, JobDescription):
        """Test generating a comprehensive report."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Run mission
        phase5.start_mission("report_mission")

        # Simulate agent work
        for agent in ["ContentQualityAgent", "ATSOptimizer", "TestPilot"]:
            step_id = phase5.track_agent(agent, "execute")
            phase5.complete_agent(step_id, success=True)

        # Validate
        phase5.validate_resume(valid_resume)

        phase5.end_mission()

        # Generate report
        report = phase5.generate_report("report_mission")

        assert report.summary["total_traces"] == 1
        assert report.summary["total_steps"] == 3
        assert len(report.recommendations) > 0

    @pytest.mark.asyncio
    async def test_export_report_to_file(self, valid_resume, tmp_path):
        """Test exporting report to file."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Run mission
        phase5.start_mission("export_mission")
        phase5.track_agent("TestAgent", "test")
        phase5.validate_resume(valid_resume)
        phase5.end_mission()

        # Generate and export report
        report = phase5.generate_report("export_mission")

        json_path = tmp_path / "report.json"
        md_path = tmp_path / "report.md"

        phase5.reporter.export_report(report, str(json_path), format="json")
        phase5.reporter.export_report(report, str(md_path), format="markdown")

        assert json_path.exists()
        assert md_path.exists()

        # Verify content
        json_content = json.loads(json_path.read_text())
        assert "report_id" in json_content

        md_content = md_path.read_text()
        assert "# Audit Report" in md_content


class TestIntegrationWithAllPhases:
    """Tests for integration with all previous phases."""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_all_phases(self, valid_resume, JobDescription, tmp_path):
        """Test complete pipeline with all phases and observability."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Initialize all phase orchestrators
        phase5 = Phase5Orchestrator(ctx)
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False
        learning_agent = ResumeLearningAgent(ctx)
        memory = MemoryPersistence(memory_file=tmp_path / "memory.json")

        # Start observability
        phase5.start_mission("all_phases_mission")

        # Phase 3: Learning - Inject instructions
        step_id = phase5.track_agent("ResumeLearningAgent", "inject_instruction")
        learning_agent.inject_instruction("Focus on ATS compatibility", priority=10)
        phase5.complete_agent(step_id, success=True)

        # Phase 4: GitOps - Backup files
        test_file = tmp_path / "resume.py"
        test_file.write_text("def get_resume():\n    pass")

        step_id = phase5.track_agent("GitOpsManager", "backup_file")
        phase4.gitops.backup_file(str(test_file))
        phase5.complete_agent(step_id, success=True)

        # Phase 2: Healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )
        phase5.complete_agent(step_id, success=result.success)

        # Phase 3: Record learning
        step_id = phase5.track_agent("ResumeLearningAgent", "record_success")
        await learning_agent.record_success(
            TaskType="full_pipeline",
            input_context=str(valid_resume),
            output_result="Success",
            confidence=0.9,
        )
        phase5.complete_agent(step_id, success=True)

        # Validate final resume
        phase5.validate_resume(ctx.current_resume)

        # End mission
        trace = phase5.end_mission(success=result.success)

        # Generate comprehensive report
        report = phase5.generate_report("all_phases_mission")

        # Verify all phases were tracked
        assert trace.success is True
        assert len(trace.steps) >= 4
        assert report.summary["total_steps"] >= 4

    @pytest.mark.asyncio
    async def test_observability_with_healing_orchestrator(self, valid_resume, JobDescription):
        """Test observability integration with healing orchestrator."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase5 = Phase5Orchestrator(ctx)

        # Start observability
        phase5.start_mission("healing_observability")

        # Run healing with observability
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")

        healing = HealingOrchestratorAgent(ctx, max_cycles=3)
        result = await healing.run()

        phase5.complete_agent(step_id, success=result.success)

        # Record metrics
        phase5.metrics.gauge("healing.cycles", result.total_cycles)
        phase5.metrics.timer("healing.duration", result.total_duration_ms)

        # End mission
        trace = phase5.end_mission(success=result.success)

        # Verify
        assert trace.success is True
        assert phase5.metrics.get_gauge("healing.cycles") == result.total_cycles


class TestEdgeCases:
    """Tests for edge cases in observability."""

    @pytest.mark.asyncio
    async def test_empty_mission(self):
        """Test observability with empty mission."""
        ctx = ResumeEngineContext()
        phase5 = Phase5Orchestrator(ctx)

        phase5.start_mission("empty_mission")
        trace = phase5.end_mission()

        assert trace is not None
        assert len(trace.steps) == 0

    @pytest.mark.asyncio
    async def test_failed_mission(self, valid_resume):
        """Test observability with failed mission."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        phase5.start_mission("failed_mission")

        # Simulate failure
        step_id = phase5.track_agent("FailingAgent", "execute")
        phase5.complete_agent(step_id, success=False, error="Simulated failure")

        trace = phase5.end_mission(success=False)

        assert trace.success is False
        assert trace.steps[0].success is False
        assert trace.steps[0].error == "Simulated failure"

    @pytest.mark.asyncio
    async def test_validation_with_empty_resume(self):
        """Test validation with empty resume."""
        ctx = ResumeEngineContext()
        phase5 = Phase5Orchestrator(ctx)

        issues = phase5.validate_resume({})

        # Empty resume should have no issues (nothing to validate)
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_multiple_missions(self, valid_resume):
        """Test running multiple missions."""
        ctx = ResumeEngineContext()
        phase5 = Phase5Orchestrator(ctx)

        # Run multiple missions
        for i in range(3):
            phase5.start_mission(f"mission_{i}")
            phase5.track_agent("TestAgent", "execute")
            phase5.end_mission()

        traces = phase5.tracer.get_all_traces()

        assert len(traces) == 3


class TestComprehensiveWorkflow:
    """Tests for comprehensive end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_telemetry_export(self, valid_resume, JobDescription, tmp_path):
        """Test complete workflow with telemetry export."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase5 = Phase5Orchestrator(ctx)

        # Run complete workflow
        phase5.start_mission("telemetry_workflow")

        # Simulate work
        for agent in ["Agent1", "Agent2", "Agent3"]:
            step_id = phase5.track_agent(agent, "execute")
            phase5.metrics.increment("agent.invocations", tags={"agent": agent})
            phase5.complete_agent(step_id, success=True)

        # Validate
        phase5.validate_resume(valid_resume)

        phase5.end_mission()

        # Export telemetry
        telemetry = phase5.export_telemetry(format="json")

        # Save to files
        traces_path = tmp_path / "traces.json"
        metrics_path = tmp_path / "metrics.json"

        traces_path.write_text(telemetry["traces"])
        metrics_path.write_text(telemetry["metrics"])

        # Verify exports
        assert traces_path.exists()
        assert metrics_path.exists()

        traces_data = json.loads(traces_path.read_text())
        metrics_data = json.loads(metrics_path.read_text())

        assert len(traces_data) == 1
        assert len(metrics_data) > 0

    @pytest.mark.asyncio
    async def test_workflow_with_run_self_healing_mission(self, valid_resume, JobDescription):
        """Test workflow using the main entry point function."""
        ctx = ResumeEngineContext()
        phase5 = Phase5Orchestrator(ctx)

        # Start observability
        phase5.start_mission("self_healing_workflow")

        # Run self-healing mission
        step_id = phase5.track_agent("run_self_healing_mission", "execute")
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
            enable_reflection=True,
        )
        phase5.complete_agent(step_id, success=result.success)

        # End mission
        trace = phase5.end_mission(success=result.success)

        # Generate report
        report = phase5.generate_report("self_healing_workflow")

        assert isinstance(result, HealingResult)
        assert result.success is True
        assert trace.success is True
        assert report is not None

    @pytest.mark.asyncio
    async def test_comprehensive_stats(self, valid_resume, JobDescription):
        """Test getting comprehensive statistics."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase5 = Phase5Orchestrator(ctx)

        # Run some operations
        phase5.start_mission("stats_mission")
        phase5.track_agent("Agent1", "execute")
        phase5.metrics.increment("test.counter")
        phase5.metrics.gauge("test.gauge", 42)
        phase5.validate_resume(valid_resume)
        phase5.end_mission()
        phase5.generate_report("stats_mission")
        phase5.export_telemetry()

        # Get comprehensive stats
        stats = phase5.get_comprehensive_stats()

        assert "tracer" in stats
        assert "metrics" in stats
        assert "validator" in stats
        assert "reporter" in stats
        assert "exporter" in stats

        assert stats["tracer"]["total_traces"] == 1
        assert stats["metrics"]["total_metrics"] > 0
        assert stats["reporter"]["total_reports"] == 1
        assert stats["exporter"]["export_count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
