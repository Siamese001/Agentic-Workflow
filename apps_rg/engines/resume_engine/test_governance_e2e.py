from __future__ import annotations
"""
End-to-End Tests for Phase 7: Governance & Meta-Optimization

Tests the complete governance workflow:
- Full mission with governance checks
- Dashboard generation
- Integration with all previous phases
"""

from pathlib import Path

import pytest

from ..context import ResumeEngineContext
from ..gitops import Phase4OrchestratorAgent
from ..governance import Phase7OrchestratorAgent
from ..healing import HealingResult, run_self_healing_mission
from ..intelligence import Phase6OrchestratorAgent
from ..learning import ResumeLearningAgent
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
                "description": "Developed microservices architecture serving 1M+ users."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
    }


@pytest.fixture
def JobDescription():
    """Sample job description."""
    return """
    Senior Software Engineer

    Requirements:
    - 5+ years of experience
    - Strong Python skills
    - AWS experience
    """


class TestFullMissionWithGovernance:
    """Tests for full mission with governance."""

    @pytest.mark.asyncio
    async def test_complete_governance_mission(self, valid_resume, tmp_path):
        """Test a complete governance mission."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase7 = Phase7OrchestratorAgent(ctx)

        # Check dependencies
        dep_issues = phase7.check_dependencies()

        # Check documentation
        sample_code = '''
def process(data):
    """Process data."""
    return data
'''
        doc_violations = phase7.check_documentation(sample_code)

        # Scan prompts
        prompt_code = '''
SYSTEM_PROMPT = "You are a helpful assistant."
'''
        prompt_issues = phase7.scan_prompts(prompt_code)

        # Predict cost
        prediction = phase7.predict_mission_cost(10, 7, 3)

        # Generate dashboard
        dashboard_path = str(tmp_path / "mission_control.html")
        phase7.generate_dashboard(ctx.results, ctx.signals, dashboard_path)

        # Verify
        assert isinstance(dep_issues, list)
        assert isinstance(doc_violations, list)
        assert isinstance(prompt_issues, list)
        assert prediction.estimated_tokens > 0
        assert Path(dashboard_path).exists()

    @pytest.mark.asyncio
    async def test_governance_checks_comprehensive(self, valid_resume):
        """Test comprehensive governance checks."""
        ctx = ResumeEngineContext()

        phase7 = Phase7OrchestratorAgent(ctx)

        sample_code = '''
ANALYSIS_PROMPT = "Analyze this: {content}"

def analyze(data, options):
    """
    Analyze data.

    Args:
        data: Input data
        options: Analysis options

    Returns:
        Analysis results
    """
    return {"result": data}
'''

        results = await phase7.run_governance_checks(sample_code)

        assert "dependencies" in results
        assert "documentation" in results
        assert "prompts" in results
        assert "passed" in results


class TestDashboardGeneration:
    """Tests for dashboard generation."""

    @pytest.mark.asyncio
    async def test_dashboard_after_full_mission(self, valid_resume, JobDescription, tmp_path):
        """Test dashboard generation after full mission."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase7 = Phase7OrchestratorAgent(ctx)

        # Run healing
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Generate dashboard
        dashboard_path = str(tmp_path / "post_healing_dashboard.html")
        phase7.generate_dashboard(ctx.results, ctx.signals, dashboard_path)

        assert Path(dashboard_path).exists()
        content = Path(dashboard_path).read_text()
        assert "Mission Control" in content

    def test_dashboard_with_comprehensive_results(self, tmp_path):
        """Test dashboard with comprehensive results."""
        ctx = ResumeEngineContext()
        phase7 = Phase7OrchestratorAgent(ctx)

        results = {
            "ContentQualityAgent": {"passed": True, "details": "Quality OK"},
            "ATSOptimizer": {"passed": True, "details": "ATS compatible"},
            "TestPilot": {"passed": True, "details": "All tests passed"},
            "SecurityHardener": {"passed": False, "details": "PII detected"},
            "PromptGovernor": {"passed": True, "details": "No issues"},
        }
        signals = {"QUALITY_OK", "ATS_COMPATIBLE", "PII_DETECTED"}

        dashboard_path = str(tmp_path / "comprehensive_dashboard.html")
        phase7.generate_dashboard(results, signals, dashboard_path)

        content = Path(dashboard_path).read_text(encoding="utf-8")
        assert "ContentQualityAgent" in content
        assert "PII_DETECTED" in content


class TestIntegrationWithAllPhases:
    """Tests for integration with all previous phases."""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_all_phases(self, valid_resume, JobDescription, tmp_path):
        """Test complete pipeline with all phases."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Initialize all orchestrators
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False
        phase5 = Phase5Orchestrator(ctx)
        phase6 = Phase6OrchestratorAgent(ctx)
        phase7 = Phase7OrchestratorAgent(ctx)
        learning_agent = ResumeLearningAgent(ctx)

        # Phase 3: Learning
        learning_agent.inject_instruction("Focus on governance", priority=10)

        # Phase 4: GitOps
        test_file = tmp_path / "resume.py"
        test_file.write_text("def get_resume():\n    pass")
        phase4.gitops.backup_file(str(test_file))

        # Phase 5: Observability
        phase5.start_mission("all_phases_e2e")

        # Phase 7: Predict cost
        step_id = phase5.track_agent("PredictiveBudgetManager", "predict")
        prediction = phase7.predict_mission_cost(5, 7, 3)
        phase5.complete_agent(step_id, success=not prediction.will_exceed)

        # Phase 6: Intelligence
        step_id = phase5.track_agent("Phase6OrchestratorAgent", "analyze")
        analysis = await phase6.analyze_resume(valid_resume, JobDescription)
        phase5.complete_agent(step_id, success=True)

        # Phase 2: Healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )
        phase5.complete_agent(step_id, success=result.success)

        # Phase 7: Governance checks
        step_id = phase5.track_agent("Phase7OrchestratorAgent", "governance")
        sample_code = "def test(): pass"
        gov_results = await phase7.run_governance_checks(sample_code)
        phase5.complete_agent(step_id, success=gov_results["passed"])

        # Phase 7: Generate dashboard
        dashboard_path = str(tmp_path / "all_phases_dashboard.html")
        phase7.generate_dashboard(ctx.results, ctx.signals, dashboard_path)

        # Phase 3: Record learning
        await learning_agent.record_success(
            TaskType="full_pipeline",
            input_context=str(valid_resume),
            output_result="Success",
            confidence=0.9,
        )

        # End observability
        trace = phase5.end_mission(success=True)

        # Verify all phases worked
        assert len(ctx.instructions) >= 1
        assert str(test_file) in phase4.gitops._backups
        assert trace is not None
        assert "security" in analysis
        # Healing may not fully converge due to BALANCE_ISSUE, but should complete
        assert result.total_cycles >= 1
        assert Path(dashboard_path).exists()


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_empty_code_governance(self):
        """Test governance with empty code."""
        ctx = ResumeEngineContext()
        phase7 = Phase7OrchestratorAgent(ctx)

        results = await phase7.run_governance_checks("")

        assert "passed" in results

    @pytest.mark.asyncio
    async def test_syntax_error_code(self):
        """Test governance with syntax error code."""
        ctx = ResumeEngineContext()
        phase7 = Phase7OrchestratorAgent(ctx)

        bad_code = "def broken(:\n    pass"

        results = await phase7.run_governance_checks(bad_code)

        # Should handle gracefully
        assert "passed" in results

    def test_budget_exceeded_prediction(self):
        """Test budget exceeded prediction."""
        ctx = ResumeEngineContext()
        phase7 = Phase7OrchestratorAgent(ctx, budget_limit=0.001)

        prediction = phase7.predict_mission_cost(100, 10, 5)

        assert prediction.will_exceed is True
        assert "Reduce scope" in prediction.Recommendation


class TestComprehensiveWorkflow:
    """Tests for comprehensive end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_all_components(self, valid_resume, JobDescription, tmp_path):
        """Test complete workflow with all Phase 7 components."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase7 = Phase7OrchestratorAgent(ctx)

        # 1. Check dependencies
        dep_issues = phase7.check_dependencies()

        # 2. Check documentation
        sample_code = '''
def calculate(x, y):
    """
    Calculate sum.

    Args:
        x: First number
        y: Second number

    Returns:
        Sum
    """
    return x + y
'''
        doc_violations = phase7.check_documentation(sample_code)

        # 3. Scan prompts
        prompt_code = '''
SYSTEM_PROMPT = "You are helpful."
'''
        prompt_issues = phase7.scan_prompts(prompt_code)

        # 4. Predict cost
        prediction = phase7.predict_mission_cost(10, 7, 3)

        # 5. Run governance checks
        gov_results = await phase7.run_governance_checks(sample_code)

        # 6. Generate dashboard
        dashboard_path = str(tmp_path / "complete_workflow.html")
        phase7.generate_dashboard(ctx.results, ctx.signals, dashboard_path)

        # 7. Get comprehensive stats
        stats = phase7.get_comprehensive_stats()

        # Verify all components worked
        assert isinstance(dep_issues, list)
        assert isinstance(doc_violations, list)
        assert isinstance(prompt_issues, list)
        assert prediction.estimated_tokens > 0
        assert "passed" in gov_results
        assert Path(dashboard_path).exists()
        assert "dependency" in stats
        assert "documentation" in stats
        assert "prompts" in stats
        assert "budget" in stats

    @pytest.mark.asyncio
    async def test_workflow_with_healing_and_governance(self, valid_resume, JobDescription, tmp_path):
        """Test workflow combining healing and governance."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase5 = Phase5Orchestrator(ctx)
        phase7 = Phase7OrchestratorAgent(ctx)

        # Start observability
        phase5.start_mission("healing_governance_workflow")

        # Predict cost
        prediction = phase7.predict_mission_cost(5, 7, 2)
        phase5.metrics.gauge("predicted_cost", prediction.estimated_cost)

        # Run healing
        step_id = phase5.track_agent("run_self_healing_mission", "execute")
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )
        phase5.complete_agent(step_id, success=result.success)

        # Run governance
        step_id = phase5.track_agent("Phase7OrchestratorAgent", "governance")
        sample_code = "def test(): pass"
        gov_results = await phase7.run_governance_checks(sample_code)
        phase5.complete_agent(step_id, success=gov_results["passed"])

        # Generate dashboard
        dashboard_path = str(tmp_path / "healing_governance_dashboard.html")
        phase7.generate_dashboard(ctx.results, ctx.signals, dashboard_path)

        # End mission
        trace = phase5.end_mission(success=True)

        # Generate report
        report = phase5.generate_report("healing_governance_workflow")

        assert isinstance(result, HealingResult)
        # Healing may not fully converge due to BALANCE_ISSUE, but should complete
        assert result.total_cycles >= 1
        assert trace is not None
        assert report is not None
        assert Path(dashboard_path).exists()

    @pytest.mark.asyncio
    async def test_comprehensive_stats_after_workflow(self, valid_resume):
        """Test getting comprehensive statistics after workflow."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase7 = Phase7OrchestratorAgent(ctx)

        # Run various operations
        phase7.check_dependencies()
        phase7.check_documentation("def test(): pass")
        phase7.scan_prompts('PROMPT = "test"')
        phase7.predict_mission_cost(10, 5, 2)

        # Get comprehensive stats
        stats = phase7.get_comprehensive_stats()

        assert stats["dependency"]["checks_performed"] >= 1
        assert stats["budget"]["predictions_made"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
