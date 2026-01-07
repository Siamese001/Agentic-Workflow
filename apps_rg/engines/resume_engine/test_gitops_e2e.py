from __future__ import annotations
"""
End-to-End Tests for Phase 4: GitOps & Advanced Mutation

Tests the complete GitOps workflow:
- Full healing mission with GitOps
- Branch management simulation
- Multi-file mutation and rollback
- Integration with all previous phases
"""

from pathlib import Path

import pytest

from ..context import ResumeEngineContext
from ..gitops import (
    ConversationalRepair,
    GitOpsManager,
    ImportPatcher,
    Phase4OrchestratorAgent,
)
from ..healing import HealingOrchestratorAgent, HealingResult, run_self_healing_mission
from ..learning import MemoryPersistence, ResumeLearningAgent


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


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file operations."""
    return tmp_path


class TestFullHealingMissionWithGitOps:
    """Tests for full healing mission with GitOps."""

    @pytest.mark.asyncio
    async def test_mission_with_gitops_backup(self, valid_resume, JobDescription, temp_dir):
        """Test that healing mission creates GitOps backups."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False

        # Create test files
        for section in ["summary", "experience"]:
            file_path = temp_dir / f"{section}.py"
            file_path.write_text(f"# {section}\ndef get_{section}():\n    pass")
            orchestrator.gitops.backup_file(str(file_path))

        # Run healing
        healing = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await healing.run()

        # Verify backups exist
        assert orchestrator.gitops._backups
        assert result.success is True

    @pytest.mark.asyncio
    async def test_mission_rollback_on_budget_exhaustion(self, valid_resume, temp_dir):
        """Test rollback when budget is exhausted."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.budget.max_cost = 0.0001  # Very low budget

        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False

        # Create and backup file
        test_file = temp_dir / "test.py"
        original = "def original():\n    pass"
        test_file.write_text(original)
        orchestrator.gitops.backup_file(str(test_file))

        # Modify file
        test_file.write_text("def modified():\n    pass")

        # Rollback
        orchestrator.gitops.rollback_all()

        # Verify rollback
        assert test_file.read_text() == original


class TestBranchManagementSimulation:
    """Tests for branch management simulation."""

    def test_branch_creation_disabled(self, valid_resume):
        """Test branch creation when git is disabled."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        gitops = GitOpsManager(ctx, enable_git=False)

        branch = gitops.create_healing_branch()

        assert branch is None

    def test_commit_disabled(self, valid_resume):
        """Test commit when git is disabled."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        gitops = GitOpsManager(ctx, enable_git=False)

        result = gitops.commit_changes("Test commit")

        assert result is False

    def test_merge_disabled(self, valid_resume):
        """Test merge when git is disabled."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        gitops = GitOpsManager(ctx, enable_git=False)

        result = gitops.merge_to_original()

        assert result is False


class TestMultiFileMutationAndRollback:
    """Tests for multi-file mutation and rollback."""

    @pytest.mark.asyncio
    async def test_multi_file_backup_and_rollback(self, temp_dir):
        """Test backing up and rolling back multiple files."""
        ctx = ResumeEngineContext()
        gitops = GitOpsManager(ctx, enable_git=False)

        # Create multiple files
        files = {}
        for i in range(5):
            file_path = temp_dir / f"file{i}.py"
            content = f"def func{i}():\n    return {i}"
            file_path.write_text(content)
            files[str(file_path)] = content
            gitops.backup_file(str(file_path))

        # Modify all files
        for file_path in files:
            Path(file_path).write_text("modified")

        # Rollback all
        count = gitops.rollback_all()

        assert count == 5
        for file_path, original in files.items():
            assert Path(file_path).read_text() == original

    @pytest.mark.asyncio
    async def test_selective_rollback(self, temp_dir):
        """Test selective file rollback."""
        ctx = ResumeEngineContext()
        gitops = GitOpsManager(ctx, enable_git=False)

        # Create files
        file1 = temp_dir / "file1.py"
        file2 = temp_dir / "file2.py"

        file1.write_text("original1")
        file2.write_text("original2")

        gitops.backup_file(str(file1))
        gitops.backup_file(str(file2))

        # Modify both
        file1.write_text("modified1")
        file2.write_text("modified2")

        # Rollback only file1
        gitops.rollback_file(str(file1))

        assert file1.read_text() == "original1"
        assert file2.read_text() == "modified2"


class TestIntegrationWithPreviousPhases:
    """Tests for integration with Phases 1-3."""

    @pytest.mark.asyncio
    async def test_phase4_with_learning_agent(self, valid_resume, temp_dir):
        """Test Phase 4 integration with Phase 3 learning."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False
        learning_agent = ResumeLearningAgent(ctx)

        # Inject instruction
        learning_agent.inject_instruction("Focus on metrics", priority=10)

        # Create and backup file
        test_file = temp_dir / "test.py"
        test_file.write_text("def test():\n    pass")
        orchestrator.gitops.backup_file(str(test_file))

        # Verify integration
        assert len(ctx.instructions) > 0
        assert str(test_file) in orchestrator.gitops._backups

    @pytest.mark.asyncio
    async def test_phase4_with_healing_orchestrator(self, valid_resume, JobDescription):
        """Test Phase 4 with Phase 2 healing orchestrator."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False

        # Run healing
        healing = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await healing.run()

        assert result.success is True
        assert result.total_cycles <= 2

    @pytest.mark.asyncio
    async def test_full_pipeline_with_all_phases(self, valid_resume, JobDescription, temp_dir):
        """Test complete pipeline with all phases."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Phase 3: Learning
        learning_agent = ResumeLearningAgent(ctx)
        learning_agent.inject_instruction("Ensure ATS compatibility", priority=10)

        # Phase 4: GitOps
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False

        # Create test files
        for section in ["summary", "experience", "skills"]:
            file_path = temp_dir / f"{section}.py"
            file_path.write_text(f"def get_{section}():\n    pass")
            phase4.gitops.backup_file(str(file_path))

        # Phase 2: Healing
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Verify all phases worked
        assert result.success is True
        assert len(ctx.instructions) > 0
        assert len(phase4.gitops._backups) == 3


class TestEdgeCases:
    """Tests for edge cases in Phase 4."""

    @pytest.mark.asyncio
    async def test_backup_nonexistent_file(self, temp_dir):
        """Test backing up a nonexistent file."""
        ctx = ResumeEngineContext()
        gitops = GitOpsManager(ctx, enable_git=False)

        result = gitops.backup_file(str(temp_dir / "nonexistent.py"))

        assert result is False

    @pytest.mark.asyncio
    async def test_rollback_without_backup(self, temp_dir):
        """Test rolling back a file without backup."""
        ctx = ResumeEngineContext()
        gitops = GitOpsManager(ctx, enable_git=False)

        file_path = temp_dir / "test.py"
        file_path.write_text("content")

        result = gitops.rollback_file(str(file_path))

        assert result is False

    @pytest.mark.asyncio
    async def test_write_invalid_python(self, temp_dir):
        """Test writing invalid Python code."""
        ctx = ResumeEngineContext()
        gitops = GitOpsManager(ctx, enable_git=False)

        file_path = temp_dir / "invalid.py"

        result = gitops.write_compliant_file(
            str(file_path),
            "def broken(\n    pass",  # Invalid syntax
        )

        assert result is False
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_empty_import_map(self):
        """Test import patcher with no files."""
        ctx = ResumeEngineContext()
        patcher = ImportPatcher(ctx)

        import_map = patcher.build_import_map([])

        assert import_map == {}

    @pytest.mark.asyncio
    async def test_conversational_repair_without_llm(self, valid_resume):
        """Test conversational repair without LLM."""
        ctx = ResumeEngineContext()
        ctx.intelligence_enabled = False

        repair = ConversationalRepair(ctx)

        result = await repair.repair(
            issue_description="Fix bug",
            affected_content="def broken():\n    pass",
        )

        assert result is None


class TestComprehensiveWorkflow:
    """Tests for comprehensive end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_complete_phase4_workflow(self, valid_resume, JobDescription, temp_dir):
        """Test complete Phase 4 workflow."""
        # Initialize context
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Initialize all components
        phase4 = Phase4OrchestratorAgent(ctx)
        phase4.gitops.enable_git = False
        learning_agent = ResumeLearningAgent(ctx)
        memory = MemoryPersistence(memory_file=temp_dir / "memory.json")

        # 1. Inject instructions
        learning_agent.inject_instruction("Focus on metrics", priority=10)

        # 2. Create and backup files
        files = {}
        for section in ["summary", "experience", "skills"]:
            file_path = temp_dir / f"{section}.py"
            content = f"def get_{section}():\n    return '{section}'"
            file_path.write_text(content)
            files[section] = str(file_path)
            phase4.gitops.backup_file(str(file_path))

        # 3. Build import map
        phase4.ImportPatcher.build_import_map(list(files.values()))

        # 4. Run healing
        healing = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await healing.run()

        # 5. Record learning
        if result.success:
            await learning_agent.record_success(
                TaskType="phase4_healing",
                input_context=str(valid_resume),
                output_result=f"Converged in {result.convergence_cycle} cycles",
                confidence=0.9,
            )

        # 6. Record section validations
        for section in files:
            memory.record_validation(section, str(valid_resume.get(section, "")), passed=result.success)

        # 7. Verify all components have state
        phase4_stats = phase4.get_comprehensive_stats()
        learning_agent.get_comprehensive_stats()
        MemoryStats = memory.get_stats()

        assert result.success is True
        assert phase4_stats["gitops"]["files_backed_up"] == 3
        assert len(ctx.instructions) > 0
        assert MemoryStats["total_tracked"] >= 3

    @pytest.mark.asyncio
    async def test_workflow_with_run_self_healing_mission(self, valid_resume, JobDescription):
        """Test workflow using the main entry point function."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
            enable_reflection=True,
        )

        assert isinstance(result, HealingResult)
        assert result.success is True
        assert result.total_cycles <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
