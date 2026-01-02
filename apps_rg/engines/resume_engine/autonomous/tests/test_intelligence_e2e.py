from __future__ import annotations
"""
End-to-End Tests for Phase 6: Intelligence & Strategic Analysis

Tests the complete intelligence workflow:
- Full mission with all intelligence components
- Integration with all previous phases
- Comprehensive analysis and optimization
"""

import pytest

from ..context import ResumeEngineContext
from ..gitops import Phase4OrchestratorAgent
from ..healing import HealingResult, run_self_healing_mission
from ..intelligence import Phase6OrchestratorAgent
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
    - Leadership experience preferred
    """


class TestFullMissionWithIntelligence:
    """Tests for full mission with intelligence components."""

    @pytest.mark.asyncio
    async def test_complete_intelligence_mission(self, valid_resume, JobDescription):
        """Test a complete intelligence mission."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase6 = Phase6OrchestratorAgent(ctx)

        # Run full mission
        result = await phase6.run_full_mission(valid_resume, JobDescription)

        assert "success" in result
        assert "cycles" in result
        assert "phases" in result
        assert result["cycles"] >= 1

    @pytest.mark.asyncio
    async def test_intelligence_analysis_comprehensive(self, valid_resume, JobDescription):
        """Test comprehensive intelligence analysis."""
        ctx = ResumeEngineContext()

        phase6 = Phase6OrchestratorAgent(ctx)

        result = await phase6.analyze_resume(valid_resume, JobDescription)

        assert "security" in result
        assert "semantic" in result
        assert "strategic" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0


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
        learning_agent = ResumeLearningAgent(ctx)
        memory = MemoryPersistence(memory_file=tmp_path / "memory.json")

        # Phase 3: Learning - Inject instructions
        learning_agent.inject_instruction("Focus on ATS compatibility", priority=10)
        learning_agent.inject_instruction("Emphasize leadership", priority=8)

        # Phase 4: GitOps - Backup files
        test_file = tmp_path / "resume.py"
        test_file.write_text("def get_resume():\n    pass")
        phase4.gitops.backup_file(str(test_file))

        # Phase 5: Observability - Start mission
        phase5.start_mission("full_pipeline_e2e")

        # Phase 6: Intelligence - Analyze
        step_id = phase5.track_agent("Phase6OrchestratorAgent", "analyze_resume")
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

        # Phase 3: Record learning
        step_id = phase5.track_agent("ResumeLearningAgent", "record_success")
        await learning_agent.record_success(
            TaskType="full_pipeline",
            input_context=str(valid_resume),
            output_result="Success",
            confidence=0.9,
        )
        phase5.complete_agent(step_id, success=True)

        # Record section validations
        for section in ["summary", "experience", "skills"]:
            memory.record_validation(section, str(valid_resume.get(section, "")), passed=True)

        # End observability
        trace = phase5.end_mission(success=True)

        # Generate report
        report = phase5.generate_report("full_pipeline_e2e")

        # Verify all phases worked
        assert len(ctx.instructions) >= 2
        assert str(test_file) in phase4.gitops._backups
        assert trace is not None
        assert trace.success is True
        assert "security" in analysis
        assert result.success is True
        assert report is not None

    @pytest.mark.asyncio
    async def test_intelligence_with_healing_loop(self, valid_resume, JobDescription):
        """Test intelligence analysis within healing loop."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase6 = Phase6OrchestratorAgent(ctx)

        # Analyze before healing
        analysis_before = await phase6.analyze_resume(valid_resume, JobDescription)

        # Run healing
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Analyze after healing
        analysis_after = await phase6.analyze_resume(ctx.current_resume, JobDescription)

        # Both analyses should complete
        assert "security" in analysis_before
        assert "security" in analysis_after
        assert result.success is True


class TestEdgeCases:
    """Tests for edge cases in Phase 6."""

    @pytest.mark.asyncio
    async def test_empty_resume(self):
        """Test handling empty resume."""
        ctx = ResumeEngineContext()
        phase6 = Phase6OrchestratorAgent(ctx)

        result = await phase6.analyze_resume({})

        assert "security" in result
        assert result["security"]["issues"] == 0

    @pytest.mark.asyncio
    async def test_resume_with_pii(self, valid_resume):
        """Test handling resume with PII."""
        ctx = ResumeEngineContext()
        phase6 = Phase6OrchestratorAgent(ctx)

        resume_with_pii = valid_resume.copy()
        resume_with_pii["contact"] = {
            "email": "test@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
        }

        result = await phase6.analyze_resume(resume_with_pii)

        # Should detect PII
        assert result["security"]["issues"] >= 1

    @pytest.mark.asyncio
    async def test_weak_resume_analysis(self):
        """Test analyzing a weak resume."""
        ctx = ResumeEngineContext()
        phase6 = Phase6OrchestratorAgent(ctx)

        weak_resume = {
            "summary": "I helped with tasks and assisted the team.",
            "experience": [
                {
                    "company": "Company",
                    "title": "Developer",
                    "description": "Worked on things.",
                }
            ],
            "skills": ["Python"],
        }

        result = await phase6.analyze_resume(weak_resume)

        # Weak resume should have recommendations for improvement
        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_no_job_description(self, valid_resume):
        """Test analysis without job description."""
        ctx = ResumeEngineContext()
        phase6 = Phase6OrchestratorAgent(ctx)

        result = await phase6.analyze_resume(valid_resume)

        # Should still work without JD
        assert "security" in result
        assert "recommendations" in result


class TestComprehensiveWorkflow:
    """Tests for comprehensive end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_all_components(self, valid_resume, JobDescription, tmp_path):
        """Test complete workflow with all Phase 6 components."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase6 = Phase6OrchestratorAgent(ctx)

        # 1. Security scan
        security_issues = phase6.security.scan_resume(valid_resume)

        # 2. Build context
        context_buffer = phase6.omni.build_context(valid_resume)

        # 3. Search context
        matches = phase6.omni.search("engineer leadership")

        # 4. Semantic analysis
        semantic_result = phase6.semantic.analyze_resume(valid_resume)

        # 5. Strategic analysis
        proposals = phase6.strategic.analyze_structure(valid_resume)
        ats_recs = phase6.strategic.get_ats_recommendations(valid_resume, JobDescription)

        # 6. Full analysis
        full_analysis = await phase6.analyze_resume(valid_resume, JobDescription)

        # 7. Full mission
        MissionResult = await phase6.run_full_mission(valid_resume, JobDescription)

        # 8. Get comprehensive stats
        stats = phase6.get_comprehensive_stats()

        # Verify all components worked
        assert isinstance(security_issues, list)
        assert len(context_buffer) > 0
        assert isinstance(matches, list)
        assert "overall_score" in semantic_result
        assert isinstance(proposals, list)
        assert isinstance(ats_recs, list)
        assert "security" in full_analysis
        assert "success" in MissionResult
        assert "security" in stats
        assert "semantic" in stats
        assert "strategic" in stats
        assert "omni" in stats

    @pytest.mark.asyncio
    async def test_workflow_with_run_self_healing_mission(self, valid_resume, JobDescription):
        """Test workflow using the main entry point function."""
        ctx = ResumeEngineContext()
        phase6 = Phase6OrchestratorAgent(ctx)

        # Analyze resume
        analysis = await phase6.analyze_resume(valid_resume, JobDescription)

        # Run self-healing mission
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
            enable_reflection=True,
        )

        assert isinstance(result, HealingResult)
        assert result.success is True
        assert "security" in analysis

    @pytest.mark.asyncio
    async def test_comprehensive_stats_after_workflow(self, valid_resume, JobDescription):
        """Test getting comprehensive statistics after workflow."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        phase6 = Phase6OrchestratorAgent(ctx)

        # Run various operations
        phase6.security.scan_resume(valid_resume)
        phase6.omni.build_context(valid_resume)
        phase6.omni.search("test query")
        phase6.semantic.analyze_resume(valid_resume)
        phase6.strategic.analyze_structure(valid_resume)
        await phase6.run_full_mission(valid_resume, JobDescription)

        # Get comprehensive stats
        stats = phase6.get_comprehensive_stats()

        assert stats["security"]["scans_performed"] >= 1
        assert stats["omni"]["queries_performed"] >= 1
        assert stats["semantic"]["total_analyses"] >= 1
        assert stats["unified"]["orchestrator"]["cycles"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
