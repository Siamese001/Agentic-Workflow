from __future__ import annotations
"""
Unit Tests for Phase 6: Intelligence & Strategic Analysis Components

Tests the core intelligence functionality:
- SecurityHardener
- SemanticAnalyzer
- StrategicAdvisor
- OmniContext
- UnifiedOrchestratorAgent
- Phase6OrchestratorAgent
"""
import re


import pytest

from ..context import ResumeEngineContext
from ..intelligence import (
    AnalysisType,
    OmniContext,
    Phase6OrchestratorAgent,
    RefactorProposal,
    RefactorType,
    SecurityHardener,
    SecurityIssue,
    SecurityLevel,
    SemanticAnalyzer,
    SemanticMatch,
    StrategicAdvisor,
    UnifiedOrchestratorAgent,
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
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40%."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
    }


@pytest.fixture
def weak_resume():
    """Create a resume with weak language."""
    return {
        "summary": "I helped with various projects and assisted the team with tasks. Worked on different things.",
        "experience": [
            {
                "company": "Some Company",
                "title": "Developer",
                "description": "Responsible for helping with code and participating in meetings."
            }
        ],
        "skills": ["Python"],
    }


class TestSecurityLevel:
    """Tests for SecurityLevel enum."""

    def test_security_levels(self):
        """Test security level values."""
        assert SecurityLevel.BASIC.value == "basic"
        assert SecurityLevel.STANDARD.value == "standard"
        assert SecurityLevel.STRICT.value == "strict"
        assert SecurityLevel.PARANOID.value == "paranoid"


class TestAnalysisType:
    """Tests for AnalysisType enum."""

    def test_analysis_types(self):
        """Test analysis type values."""
        assert AnalysisType.DOCSTRING.value == "docstring"
        assert AnalysisType.CONTENT.value == "content"
        assert AnalysisType.STRUCTURE.value == "structure"
        assert AnalysisType.QUALITY.value == "quality"


class TestRefactorType:
    """Tests for RefactorType enum."""

    def test_refactor_types(self):
        """Test refactor type values."""
        assert RefactorType.EXTRACT_METHOD.value == "extract_method"
        assert RefactorType.SIMPLIFY.value == "simplify"
        assert RefactorType.DECOMPOSE.value == "decompose"


class TestSecurityIssue:
    """Tests for SecurityIssue dataclass."""

    def test_create_issue(self):
        """Test creating a security issue."""
        issue = SecurityIssue(
            issue_id="test123",
            Severity="high",
            category="hardcoded_secret",
            file_path="test.py",
            line_number=10,
            description="Found hardcoded password",
            Recommendation="Use environment variables",
        )

        assert issue.issue_id == "test123"
        assert issue.Severity == "high"


class TestSemanticMatch:
    """Tests for SemanticMatch dataclass."""

    def test_create_match(self):
        """Test creating a semantic match."""
        match = SemanticMatch(
            file_path="summary",
            content_preview="Experienced engineer...",
            similarity_score=0.85,
        )

        assert match.file_path == "summary"
        assert match.similarity_score == 0.85


class TestRefactorProposal:
    """Tests for RefactorProposal dataclass."""

    def test_create_proposal(self):
        """Test creating a refactor proposal."""
        proposal = RefactorProposal(
            proposal_id="prop123",
            refactor_type=RefactorType.SIMPLIFY,
            target="summary",
            description="Shorten summary",
            before_snippet="Long text...",
            after_snippet="Short text",
            confidence=0.8,
        )

        assert proposal.proposal_id == "prop123"
        assert proposal.refactor_type == RefactorType.SIMPLIFY


class TestSecurityHardener:
    """Tests for SecurityHardener class."""

    def test_init(self, ctx):
        """Test SecurityHardener initialization."""
        hardener = SecurityHardener(ctx)

        assert hardener.ctx == ctx
        assert hardener.level == SecurityLevel.STANDARD

    def test_scan_content_clean(self, ctx):
        """Test scanning clean content."""
        hardener = SecurityHardener(ctx)

        content = "def hello():\n    return 'world'"
        issues = hardener.scan_content(content, "test.py")

        assert len(issues) == 0

    def test_scan_content_hardcoded_secret(self, ctx):
        """Test detecting hardcoded secrets."""
        hardener = SecurityHardener(ctx)

        content = "password = 'secret123'\napi_key = 'abc123'"
        issues = hardener.scan_content(content, "test.py")

        assert len(issues) >= 1
        assert any(i.category == "hardcoded_secret" for i in issues)

    def test_scan_content_eval(self, ctx):
        """Test detecting eval usage."""
        hardener = SecurityHardener(ctx)

        content = "result = eval(user_input)"
        issues = hardener.scan_content(content, "test.py")

        assert len(issues) >= 1
        assert any(i.category == "command_injection" for i in issues)

    def test_scan_resume_pii(self, ctx, valid_resume):
        """Test scanning resume for PII."""
        hardener = SecurityHardener(ctx)

        resume_with_pii = valid_resume.copy()
        resume_with_pii["contact"] = "email@example.com, 555-123-4567"

        issues = hardener.scan_resume(resume_with_pii)

        assert len(issues) >= 1

    def test_get_issues_by_severity(self, ctx):
        """Test getting issues by Severity."""
        hardener = SecurityHardener(ctx)

        content = "password = 'secret'\nrandom.random()"
        hardener.scan_content(content, "test.py")

        high_issues = hardener.get_issues_by_severity("high")

        assert all(i.Severity == "high" for i in high_issues)

    def test_get_stats(self, ctx):
        """Test getting security statistics."""
        hardener = SecurityHardener(ctx)
        hardener.scan_content("password = 'test'", "test.py")

        stats = hardener.get_stats()

        assert stats["scans_performed"] == 1
        assert stats["total_issues"] >= 1


class TestSemanticAnalyzer:
    """Tests for SemanticAnalyzer class."""

    def test_init(self, ctx):
        """Test SemanticAnalyzer initialization."""
        analyzer = SemanticAnalyzer(ctx)

        assert analyzer.ctx == ctx

    def test_analyze_content_strong(self, ctx):
        """Test analyzing strong content."""
        analyzer = SemanticAnalyzer(ctx)

        content = "Led a team of 10 engineers and delivered a project that increased revenue by 25%."
        result = analyzer.analyze_content(content)

        assert result["metrics"]["quality_score"] > 50
        assert result["metrics"]["quantified_achievements"] >= 2

    def test_analyze_content_weak(self, ctx):
        """Test analyzing weak content."""
        analyzer = SemanticAnalyzer(ctx)

        content = "Helped with various tasks and assisted the team."
        result = analyzer.analyze_content(content)

        assert len(result["issues"]) > 0
        assert any(i["type"] == "weak_language" for i in result["issues"])

    def test_analyze_content_no_metrics(self, ctx):
        """Test detecting Missing metrics."""
        analyzer = SemanticAnalyzer(ctx)

        content = "Developed software applications for clients."
        result = analyzer.analyze_content(content)

        assert any(i["type"] == "no_metrics" for i in result["issues"])

    def test_analyze_resume(self, ctx, valid_resume):
        """Test analyzing a complete resume."""
        analyzer = SemanticAnalyzer(ctx)

        result = analyzer.analyze_resume(valid_resume)

        assert "overall_score" in result
        assert "sections" in result
        assert "recommendations" in result

    def test_analyze_weak_resume(self, ctx, weak_resume):
        """Test analyzing a weak resume."""
        analyzer = SemanticAnalyzer(ctx)

        result = analyzer.analyze_resume(weak_resume)

        # Weak resume should have issues detected
        # The score may vary but should have weak language issues
        assert any(
            "issues" in section_data and len(section_data.get("issues", [])) > 0
            for section_data in result.get("sections", {}).values()
            if isinstance(section_data, dict)
        )

    def test_get_stats(self, ctx):
        """Test getting analyzer statistics."""
        analyzer = SemanticAnalyzer(ctx)
        analyzer.analyze_content("Test content")

        stats = analyzer.get_stats()

        assert stats["total_analyses"] == 1


class TestStrategicAdvisor:
    """Tests for StrategicAdvisor class."""

    def test_init(self, ctx):
        """Test StrategicAdvisor initialization."""
        advisor = StrategicAdvisor(ctx)

        assert advisor.ctx == ctx

    def test_analyze_structure(self, ctx, valid_resume):
        """Test analyzing resume structure."""
        advisor = StrategicAdvisor(ctx)

        proposals = advisor.analyze_structure(valid_resume)

        assert isinstance(proposals, list)

    def test_analyze_long_summary(self, ctx):
        """Test detecting long summary."""
        advisor = StrategicAdvisor(ctx)

        resume = {
            "summary": "A" * 600,  # Very long summary
        }

        proposals = advisor.analyze_structure(resume)

        assert len(proposals) >= 1
        assert any(p.refactor_type == RefactorType.SIMPLIFY for p in proposals)

    def test_analyze_many_skills(self, ctx):
        """Test detecting too many skills."""
        advisor = StrategicAdvisor(ctx)

        resume = {
            "skills": [f"Skill{i}" for i in range(20)],
        }

        proposals = advisor.analyze_structure(resume)

        assert len(proposals) >= 1

    def test_get_ats_recommendations(self, ctx, valid_resume):
        """Test getting ATS recommendations."""
        advisor = StrategicAdvisor(ctx)

        recs = advisor.get_ats_recommendations(valid_resume)

        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_get_ats_with_job_description(self, ctx, valid_resume):
        """Test ATS recommendations with job description."""
        advisor = StrategicAdvisor(ctx)

        jd = "Looking for Python developer with AWS experience"
        recs = advisor.get_ats_recommendations(valid_resume, jd)

        assert isinstance(recs, list)

    def test_get_stats(self, ctx, valid_resume):
        """Test getting advisor statistics."""
        advisor = StrategicAdvisor(ctx)
        advisor.analyze_structure(valid_resume)

        stats = advisor.get_stats()

        assert "total_proposals" in stats


class TestOmniContext:
    """Tests for OmniContext class."""

    def test_init(self, ctx):
        """Test OmniContext initialization."""
        omni = OmniContext(ctx)

        assert omni.ctx == ctx

    def test_build_context(self, ctx, valid_resume):
        """Test building context from resume."""
        omni = OmniContext(ctx)

        buffer = omni.build_context(valid_resume)

        assert len(buffer) > 0
        assert "SUMMARY" in buffer

    def test_search(self, ctx, valid_resume):
        """Test searching context."""
        omni = OmniContext(ctx)
        omni.build_context(valid_resume)

        matches = omni.search("engineer")

        assert len(matches) > 0
        assert matches[0].similarity_score > 0

    def test_search_no_results(self, ctx, valid_resume):
        """Test search with no results."""
        omni = OmniContext(ctx)
        omni.build_context(valid_resume)

        matches = omni.search("xyznonexistent")

        assert len(matches) == 0

    def test_get_section(self, ctx, valid_resume):
        """Test getting a specific section."""
        omni = OmniContext(ctx)
        omni.build_context(valid_resume)

        section = omni.get_section("summary")

        assert section is not None
        assert "SUMMARY" in section

    def test_get_stats(self, ctx, valid_resume):
        """Test getting context statistics."""
        omni = OmniContext(ctx)
        omni.build_context(valid_resume)
        omni.search("test")

        stats = omni.get_stats()

        assert stats["sections_indexed"] > 0
        assert stats["queries_performed"] == 1


class TestUnifiedOrchestrator:
    """Tests for UnifiedOrchestratorAgent class."""

    def test_init(self, ctx):
        """Test UnifiedOrchestratorAgent initialization."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        assert orchestrator.ctx == ctx
        assert orchestrator.security is not None
        assert orchestrator.semantic is not None

    @pytest.mark.asyncio
    async def test_run_mission(self, ctx, valid_resume):
        """Test running a mission."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        result = await orchestrator.run_mission(valid_resume)

        assert "success" in result
        assert "cycles" in result
        assert "phases" in result

    @pytest.mark.asyncio
    async def test_run_mission_with_job_description(self, ctx, valid_resume):
        """Test running a mission with job description."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        jd = "Looking for Python developer"
        result = await orchestrator.run_mission(valid_resume, jd)

        assert result["cycles"] >= 1

    def test_get_comprehensive_stats(self, ctx):
        """Test getting comprehensive statistics."""
        orchestrator = UnifiedOrchestratorAgent(ctx)

        stats = orchestrator.get_comprehensive_stats()

        assert "security" in stats
        assert "semantic" in stats
        assert "strategic" in stats
        assert "omni" in stats


class TestPhase6Orchestrator:
    """Tests for Phase6OrchestratorAgent class."""

    def test_init(self, ctx):
        """Test Phase6OrchestratorAgent initialization."""
        orchestrator = Phase6OrchestratorAgent(ctx)

        assert orchestrator.ctx == ctx
        assert orchestrator.security is not None
        assert orchestrator.semantic is not None
        assert orchestrator.strategic is not None
        assert orchestrator.omni is not None
        assert orchestrator.unified is not None

    @pytest.mark.asyncio
    async def test_analyze_resume(self, ctx, valid_resume):
        """Test analyzing a resume."""
        orchestrator = Phase6OrchestratorAgent(ctx)

        result = await orchestrator.analyze_resume(valid_resume)

        assert "security" in result
        assert "semantic" in result
        assert "strategic" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_analyze_resume_with_job_description(self, ctx, valid_resume):
        """Test analyzing with job description."""
        orchestrator = Phase6OrchestratorAgent(ctx)

        jd = "Python developer with AWS experience"
        result = await orchestrator.analyze_resume(valid_resume, jd)

        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_run_full_mission(self, ctx, valid_resume):
        """Test running a full mission."""
        orchestrator = Phase6OrchestratorAgent(ctx)

        result = await orchestrator.run_full_mission(valid_resume)

        assert "success" in result
        assert "cycles" in result

    def test_search_context(self, ctx, valid_resume):
        """Test searching context."""
        orchestrator = Phase6OrchestratorAgent(ctx)
        orchestrator.omni.build_context(valid_resume)

        matches = orchestrator.search_context("engineer")

        assert isinstance(matches, list)

    def test_get_comprehensive_stats(self, ctx):
        """Test getting comprehensive statistics."""
        orchestrator = Phase6OrchestratorAgent(ctx)

        stats = orchestrator.get_comprehensive_stats()

        assert "security" in stats
        assert "semantic" in stats
        assert "strategic" in stats
        assert "omni" in stats
        assert "unified" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
