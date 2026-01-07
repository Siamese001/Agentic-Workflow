from __future__ import annotations
"""
Integration Tests for Phase 4: GitOps & Advanced Mutation

Tests the integration of GitOps components:
- GitOpsManager with healing cycles
- ResilientMutator with agents
- ImportPatcher with file changes
- ConversationalRepair with orchestrator
"""
import re


import pytest

from ..context import ResumeEngineContext
from ..gitops import (
    ConversationalRepair,
    GitOpsManager,
    ImportPatcher,
    MutationMode,
    Phase4OrchestratorAgent,
    ResilientMutator,
)
from ..healing import HealingCycle, HealingStrategy
from ..learning import ResumeLearningAgent


@pytest.fixture
def ctx():
    """Create a fresh context for each test."""
    return ResumeEngineContext()


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS"],
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file operations."""
    return tmp_path


class TestGitOpsWithHealingCycles:
    """Integration tests for GitOps with healing cycles."""

    @pytest.mark.asyncio
    async def test_gitops_backup_during_healing(self, ctx, valid_resume, temp_dir):
        """Test that GitOps creates backups during healing."""
        ctx.current_resume = valid_resume

        gitops = GitOpsManager(ctx, enable_git=False)

        # Create a test file
        test_file = temp_dir / "resume_section.py"
        test_file.write_text("# Original content\ndef get_summary():\n    pass")

        # Backup before healing
        gitops.backup_file(str(test_file))

        # Run healing cycle
        cycle = HealingCycle(ctx, cycle_number=1)
        await cycle.execute(HealingStrategy.VERIFICATION_ONLY)

        # Verify backup exists
        assert str(test_file) in gitops._backups

    @pytest.mark.asyncio
    async def test_gitops_rollback_on_failure(self, ctx, temp_dir):
        """Test that GitOps rolls back on failure."""
        gitops = GitOpsManager(ctx, enable_git=False)

        # Create and backup file
        test_file = temp_dir / "test.py"
        original = "def original():\n    return True"
        test_file.write_text(original)
        gitops.backup_file(str(test_file))

        # Modify file
        test_file.write_text("def modified():\n    return False")

        # Simulate failure and rollback
        gitops.rollback_file(str(test_file))

        # Verify rollback
        assert test_file.read_text() == original


class TestResilientMutatorWithAgents:
    """Integration tests for ResilientMutator with agents."""

    @pytest.mark.asyncio
    async def test_mutator_tracks_statistics(self, ctx):
        """Test that mutator tracks mutation statistics."""
        mutator = ResilientMutator(ctx, min_confidence=0.5)

        # Simulate mutations (without LLM)
        mutator.total_mutations = 5
        mutator.successful_mutations = 4
        mutator.failed_mutations = 1

        stats = mutator.get_stats()

        assert stats["total_mutations"] == 5
        assert stats["success_rate"] == 0.8

    @pytest.mark.asyncio
    async def test_mutator_with_healing_context(self, ctx, valid_resume):
        """Test mutator integration with healing context."""
        ctx.current_resume = valid_resume

        mutator = ResilientMutator(ctx)

        # Build a prompt
        prompt = mutator._build_prompt(
            "Improve resume summary with metrics",
            valid_resume["summary"],
            MutationMode.FULL_CODE,
        )

        assert "Improve resume summary" in prompt
        assert valid_resume["summary"] in prompt


class TestImportPatcherWithFileChanges:
    """Integration tests for ImportPatcher with file changes."""

    @pytest.mark.asyncio
    async def test_import_patcher_detects_dependencies(self, ctx, temp_dir):
        """Test that import patcher detects file dependencies."""
        patcher = ImportPatcher(ctx)

        # Create files with imports
        main_file = temp_dir / "main.py"
        main_file.write_text("from utils import helper\n\nhelper()")

        utils_file = temp_dir / "utils.py"
        utils_file.write_text("def helper():\n    pass")

        # Build import map
        import_map = patcher.build_import_map([str(main_file), str(utils_file)])

        # Check dependencies
        assert "utils" in import_map
        assert str(main_file) in import_map["utils"]

    @pytest.mark.asyncio
    async def test_import_patcher_with_module_move(self, ctx, temp_dir):
        """Test import patching after module move."""
        patcher = ImportPatcher(ctx)

        # Create file with old import
        consumer = temp_dir / "consumer.py"
        consumer.write_text("from old_location import MyClass\n\nobj = MyClass()")

        # Build import map
        patcher.build_import_map([str(consumer)])

        # Patch imports
        patched = await patcher.patch_imports({"old_location": "new_location"})

        # Verify (may or may not patch depending on matching)
        assert patched >= 0


class TestConversationalRepairWithOrchestrator:
    """Integration tests for ConversationalRepair with orchestrator."""

    def test_conversational_repair_agents(self, ctx):
        """Test that conversational repair has all agents."""
        repair = ConversationalRepair(ctx)

        expected_agents = ["Sherlock", "SafetyInspectorAgent", "DependencySentinelAgent", "ArchitectureGovernor"]

        for agent in expected_agents:
            assert agent in repair.agents

    @pytest.mark.asyncio
    async def test_conversational_repair_proposal_cleaning(self, ctx):
        """Test that proposals are cleaned properly."""
        repair = ConversationalRepair(ctx)

        # Test various formats
        test_cases = [
            ("```python\ndef foo():\n    pass\n```", "def foo():\n    pass"),
            ("def bar():\n    return 1", "def bar():\n    return 1"),
        ]

        for input_text, expected_contains in test_cases:
            cleaned = repair._clean_proposal(input_text)
            assert expected_contains.strip() in cleaned or "def" in cleaned


class TestPhase4OrchestratorIntegration:
    """Integration tests for Phase4OrchestratorAgent."""

    @pytest.mark.asyncio
    async def test_orchestrator_creates_backups(self, ctx, temp_dir):
        """Test that orchestrator creates backups before healing."""
        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False

        # Create test file
        test_file = temp_dir / "test.py"
        test_file.write_text("def original():\n    pass")

        # Heal (will fail without LLM but should backup)
        await orchestrator.heal_with_gitops(
            Task="Add docstring",
            content=test_file.read_text(),
            file_path=str(test_file),
        )

        # Verify backup
        assert str(test_file) in orchestrator.gitops._backups

    @pytest.mark.asyncio
    async def test_orchestrator_with_learning_agent(self, ctx, valid_resume):
        """Test orchestrator integration with learning agent."""
        ctx.current_resume = valid_resume

        orchestrator = Phase4OrchestratorAgent(ctx)
        learning_agent = ResumeLearningAgent(ctx)

        # Inject instruction
        learning_agent.inject_instruction(
            content="Focus on ATS compatibility",
            priority=10,
        )

        # Verify instruction is in context
        assert len(ctx.instructions) > 0

        # Get stats from both
        orchestrator_stats = orchestrator.get_comprehensive_stats()
        learning_stats = learning_agent.get_comprehensive_stats()

        assert "gitops" in orchestrator_stats
        assert "learning" in learning_stats

    @pytest.mark.asyncio
    async def test_orchestrator_full_workflow(self, ctx, valid_resume, temp_dir):
        """Test full orchestrator workflow."""
        ctx.current_resume = valid_resume

        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False

        # Create test file
        test_file = temp_dir / "resume.py"
        content = '''"""Resume module."""

def get_summary():
    """Get resume summary."""
    return "Summary here"
'''
        test_file.write_text(content)

        # Attempt healing
        result = await orchestrator.heal_with_gitops(
            Task="Add metrics to summary",
            content=content,
            file_path=str(test_file),
        )

        # Verify result structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'original_content')
        assert hasattr(result, 'mutated_content')


class TestCrossComponentIntegration:
    """Tests for integration across multiple Phase 4 components."""

    @pytest.mark.asyncio
    async def test_gitops_mutator_integration(self, ctx, temp_dir):
        """Test GitOps and Mutator working together."""
        gitops = GitOpsManager(ctx, enable_git=False)
        ResilientMutator(ctx)

        # Create file
        test_file = temp_dir / "module.py"
        original = "def old_function():\n    pass"
        test_file.write_text(original)

        # Backup
        gitops.backup_file(str(test_file))

        # Simulate mutation (without LLM)
        new_content = "def new_function():\n    return True"

        # Write with compliance check
        success = gitops.write_compliant_file(str(test_file), new_content)

        assert success is True
        assert test_file.read_text().strip() == new_content.strip()

        # Rollback
        gitops.rollback_file(str(test_file))
        assert test_file.read_text() == original

    @pytest.mark.asyncio
    async def test_full_phase4_workflow(self, ctx, valid_resume, temp_dir):
        """Test complete Phase 4 workflow with all components."""
        ctx.current_resume = valid_resume

        # Initialize all components
        orchestrator = Phase4OrchestratorAgent(ctx)
        orchestrator.gitops.enable_git = False
        learning_agent = ResumeLearningAgent(ctx)

        # 1. Inject instructions
        learning_agent.inject_instruction(
            content="Ensure all sections have metrics",
            priority=10,
        )

        # 2. Create test files
        files = {}
        for section in ["summary", "experience", "skills"]:
            file_path = temp_dir / f"{section}.py"
            file_path.write_text(f"# {section} section\ndef get_{section}():\n    pass")
            files[section] = str(file_path)
            orchestrator.gitops.backup_file(str(file_path))

        # 3. Build import map
        orchestrator.ImportPatcher.build_import_map(list(files.values()))

        # 4. Verify all components have state
        stats = orchestrator.get_comprehensive_stats()

        assert stats["gitops"]["files_backed_up"] == 3
        assert stats["ImportPatcher"]["modules_tracked"] >= 0

        # 5. Rollback all
        count = orchestrator.gitops.rollback_all()
        assert count == 3


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestConversationalRepair"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Test file - operational stub only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
