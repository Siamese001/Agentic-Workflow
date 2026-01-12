from __future__ import annotations
"""
Integration Tests for Phase 6: Intelligence & Strategic Analysis

Tests the integration of intelligence components:
- SecurityHardener with resume processing
- SemanticAnalyzer with healing cycles
- StrategicAdvisor with optimization
- OmniContext with search
- UnifiedOrchestratorAgent with full pipeline
"""

import pytest

from ..context import ResumeEngineContext
from ..gitops import Phase4OrchestratorAgent
from ..healing import HealingCycle, HealingOrchestratorAgent, HealingStrategy
from ..intelligence import (
    OmniContext,
    Phase6OrchestratorAgent,
    SecurityHardener,
    SemanticAnalyzer,
    StrategicAdvisor,
    UnifiedOrchestratorAgent,
)
from ..learning import ResumeLearningAgent
from ..observability import Phase5Orchestrator


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
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40%."
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
    - 5+ years of experience in software development
    - Strong Python and JavaScript skills
    - Experience with AWS and cloud infrastructure
    """


class TestSecurityWithResumeProcessing:
    """Integration tests for SecurityHardener with resume processing."""

    def test_security_scan_during_healing(self, ctx, valid_resume):
        """Test security scanning during healing process."""
        ctx.current_resume = valid_resume

        hardener = SecurityHardener(ctx)

        # Scan resume
        hardener.scan_resume(valid_resume)

        # Valid resume should have minimal issues
        high_issues = hardener.get_issues_by_severity("high")
        assert len(high_issues) == 0

    def test_security_scan_with_pii(self, ctx, valid_resume):
        """Test security scanning with PII."""
        resume_with_pii = valid_resume.copy()
        resume_with_pii["contact"] = {
            "email": "test@example.com",
            "phone": "555-123-4567",
        }

        hardener = SecurityHardener(ctx)
        issues = hardener.scan_resume(resume_with_pii)

        # Should detect PII
        assert len(issues) >= 1


class TestSemanticWithHealingCycles:
    """Integration tests for SemanticAnalyzer with healing cycles."""

    @pytest.mark.asyncio
    async def test_semantic_analysis_before_healing(self, ctx, valid_resume):
        """Test semantic analysis before healing."""
        ctx.current_resume = valid_resume

        analyzer = SemanticAnalyzer(ctx)

        # Analyze before healing
        result_before = analyzer.analyze_resume(valid_resume)

        # Run healing
        cycle = HealingCycle(ctx, cycle_number=1)
        await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        # Score should be reasonable
        assert result_before["overall_score"] >= 0

    def test_semantic_tracks_quality_improvements(self, ctx, valid_resume):
        """Test that semantic analyzer tracks quality."""
        analyzer = SemanticAnalyzer(ctx)

        # Analyze weak content
        weak_content = "Helped with tasks and assisted team."
        weak_result = analyzer.analyze_content(weak_content)

        # Analyze strong content
        strong_content = "Led team of 10 engineers, delivered 5 projects, increased revenue by 40%."
        strong_result = analyzer.analyze_content(strong_content)

        # Strong should score higher
        assert strong_result["metrics"]["quality_score"] > weak_result["metrics"]["quality_score"]


class TestStrategicWithOptimization:
    """Integration tests for StrategicAdvisor with optimization."""

    def test_strategic_proposals_for_improvement(self, ctx, valid_resume):
        """Test strategic proposals for resume improvement."""
        advisor = StrategicAdvisor(ctx)

        # Get proposals
        advisor.analyze_structure(valid_resume)

        # Get ATS recommendations
        recs = advisor.get_ats_recommendations(valid_resume)

        # Should have some recommendations
        assert len(recs) > 0

    def test_strategic_with_job_matching(self, ctx, valid_resume, JobDescription):
        """Test strategic analysis with job matching."""
        advisor = StrategicAdvisor(ctx)

        recs = advisor.get_ats_recommendations(valid_resume, JobDescription)

        # Should provide job-specific recommendations
        assert isinstance(recs, list)


class TestOmniContextWithSearch:
    """Integration tests for OmniContext with search."""

    def test_omni_context_search_integration(self, ctx, valid_resume):
        """Test OmniContext search integration."""
        omni = OmniContext(ctx)

        # Build context
        omni.build_context(valid_resume)

        # Search for relevant content
        matches = omni.search("engineer software")

        # Should find matches
        assert len(matches) > 0

    def test_omni_context_section_retrieval(self, ctx, valid_resume):
        """Test OmniContext section retrieval."""
        omni = OmniContext(ctx)
        omni.build_context(valid_resume)

        # Get specific sections
        summary = omni.get_section("summary")
        experience = omni.get_section("experience")

        assert summary is not None
        assert experience is not None


class TestUnifiedOrchestratorWithPipeline:
    """Integration tests for UnifiedOrchestratorAgent with full pipeline."""

    @pytest.mark.asyncio
    async def test_unified_mission_execution(self, ctx, valid_resume):
        """Test unified mission execution."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        result = await orchestrator.run_mission(valid_resume)

        assert result["cycles"] >= 1
        assert len(result["phases"]) >= 4

    @pytest.mark.asyncio
    async def test_unified_with_job_description(self, ctx, valid_resume, JobDescription):
        """Test unified orchestrator with job description."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        result = await orchestrator.run_mission(valid_resume, JobDescription)

        assert "success" in result


class TestPhase6WithPreviousPhases:
    """Integration tests for Phase 6 with previous phases."""

    @pytest.mark.asyncio
    async def test_phase6_with_phase5_observability(self, ctx, valid_resume):
        """Test Phase 6 integration with Phase 5 observability."""
        phase6 = Phase6OrchestratorAgent(ctx)
        phase5 = Phase5Orchestrator(ctx)

        # Start observability
        phase5.start_mission("phase6_integration")

        # Run Phase 6 analysis
        step_id = phase5.track_agent("Phase6OrchestratorAgent", "analyze_resume")
        result = await phase6.analyze_resume(valid_resume)
        phase5.complete_agent(step_id, success=True)

        # End observability
        trace = phase5.end_mission(success=True)

        assert trace is not None
        assert "security" in result

    @pytest.mark.asyncio
    async def test_phase6_with_learning_agent(self, ctx, valid_resume):
        """Test Phase 6 integration with Phase 3 learning."""
        phase6 = Phase6OrchestratorAgent(ctx)
        learning_agent = ResumeLearningAgent(ctx)

        # Inject instruction
        learning_agent.inject_instruction("Focus on ATS optimization", priority=10)

        # Run analysis
        result = await phase6.analyze_resume(valid_resume)

        # Record learning
        await learning_agent.record_success(
            TaskType="phase6_analysis",
            input_context=str(valid_resume),
            output_result=str(result),
            confidence=0.9,
        )

        assert len(ctx.instructions) > 0

    @pytest.mark.asyncio
    async def test_phase6_with_healing(self, ctx, valid_resume, JobDescription):
        """Test Phase 6 with healing orchestrator."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase6 = Phase6OrchestratorAgent(ctx)

        # Analyze before healing
        analysis_before = await phase6.analyze_resume(valid_resume)

        # Run healing
        healing = RgHealingOrchestratorAgent(ctx, max_cycles=2)
        healing_result = await healing.run()

        # Verify both worked
        assert "security" in analysis_before
        assert healing_result.total_cycles >= 1


class TestCrossComponentIntegration:
    """Tests for integration across multiple Phase 6 components."""

    @pytest.mark.asyncio
    async def test_full_phase6_workflow(self, ctx, valid_resume, JobDescription):
        """Test complete Phase 6 workflow."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase6 = Phase6OrchestratorAgent(ctx)

        # 1. Security scan
        security_issues = phase6.security.scan_resume(valid_resume)

        # 2. Build context
        phase6.omni.build_context(valid_resume)

        # 3. Semantic analysis
        semantic_result = phase6.semantic.analyze_resume(valid_resume)

        # 4. Strategic analysis
        proposals = phase6.strategic.analyze_structure(valid_resume)
        ats_recs = phase6.strategic.get_ats_recommendations(valid_resume, JobDescription)

        # 5. Run full mission
        MissionResult = await phase6.run_full_mission(valid_resume, JobDescription)

        # Verify all components worked
        assert isinstance(security_issues, list)
        assert "overall_score" in semantic_result
        assert isinstance(proposals, list)
        assert isinstance(ats_recs, list)
        assert "success" in MissionResult

    @pytest.mark.asyncio
    async def test_all_phases_integration(self, ctx, valid_resume, JobDescription, tmp_path):
        """Test integration of all phases."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Initialize all phase orchestrators
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False
        phase5 = Phase5Orchestrator(ctx)
        phase6 = Phase6OrchestratorAgent(ctx)
        learning_agent = ResumeLearningAgent(ctx)

        # Phase 3: Learning
        learning_agent.inject_instruction("Optimize for ATS", priority=10)

        # Phase 4: GitOps (backup)
        test_file = tmp_path / "resume.py"
        test_file.write_text("def get_resume():\n    pass")
        phase4.gitops.backup_file(str(test_file))

        # Phase 5: Observability
        phase5.start_mission("all_phases_test")

        # Phase 6: Intelligence
        step_id = phase5.track_agent("Phase6OrchestratorAgent", "analyze")
        analysis = await phase6.analyze_resume(valid_resume, JobDescription)
        phase5.complete_agent(step_id, success=True)

        # Phase 2: Healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        healing = RgHealingOrchestratorAgent(ctx, max_cycles=2)
        healing_result = await healing.run()
        phase5.complete_agent(step_id, success=True)

        # End observability
        trace = phase5.end_mission(success=True)

        # Verify all phases worked
        assert len(ctx.instructions) > 0
        assert str(test_file) in phase4.gitops._backups
        assert trace is not None
        assert "security" in analysis
        assert healing_result.total_cycles >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
