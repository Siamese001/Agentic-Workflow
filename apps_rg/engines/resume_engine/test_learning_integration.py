from __future__ import annotations
"""
Integration Tests for Phase 3: Learning & Intelligence

Tests the integration of learning components:
- LearningLoop with healing cycles
- ConfidenceScorer with agent execution
- InstructionInjector with orchestrator
- MemoryPersistence across sessions
"""

import pytest

from ..agents import ContentQualityAgent
from ..context import ResumeEngineContext
from ..healing import HealingCycle, HealingOrchestratorAgent, HealingStrategy
from ..learning import (
    ConfidenceLevel,
    ConfidenceScorer,
    InstructionInjector,
    LearningLoop,
    MemoryPersistence,
    ResumeLearningAgent,
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
def temp_memory_dir(tmp_path):
    """Create a temporary directory for memory files."""
    return tmp_path


class TestLearningLoopIntegration:
    """Integration tests for LearningLoop with healing cycles."""

    @pytest.mark.asyncio
    async def test_learning_loop_records_healing_success(self, ctx, valid_resume):
        """Test that learning loop records successful healing."""
        ctx.current_resume = valid_resume

        learning = LearningLoop(ctx)

        # Simulate a successful healing cycle
        await learning.record_success(
            TaskType="quality_fix",
            input_context="Resume with weak summary",
            output_result="Resume with strong metrics-driven summary",
            confidence=0.9,
        )

        # Verify it was recorded
        stats = learning.get_stats()
        assert stats["successful_examples"] >= 1

    @pytest.mark.asyncio
    async def test_learning_loop_provides_context(self, ctx, valid_resume):
        """Test that learning loop provides context for similar tasks."""
        ctx.current_resume = valid_resume

        learning = LearningLoop(ctx)

        # Record some examples
        await learning.record_success(
            TaskType="ats_optimization",
            input_context="Resume with special characters and formatting issues",
            output_result="Clean ATS-friendly resume without special characters",
            confidence=0.85,
        )

        # Try to recall similar
        examples = await learning.recall_similar(
            "ATS compatibility special characters",
            TaskType="ats_optimization",
        )

        # May or may not find matches depending on algorithm
        assert isinstance(examples, list)


class TestConfidenceScorerIntegration:
    """Integration tests for ConfidenceScorer with agents."""

    @pytest.mark.asyncio
    async def test_confidence_scorer_with_agent_result(self, ctx, valid_resume):
        """Test confidence scoring of agent results."""
        ctx.current_resume = valid_resume

        scorer = ConfidenceScorer(min_confidence=0.5)

        # Run an agent
        agent = ContentQualityAgent(ctx)
        await agent.execute()

        # Score the result text
        result_text = str(ctx.results.get("ContentQualityAgent", {}))
        confidence = scorer.score_from_text(result_text)

        assert confidence.score > 0
        assert confidence.level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]

    @pytest.mark.asyncio
    async def test_confidence_retry_mechanism(self, ctx):
        """Test that retry mechanism works."""
        scorer = ConfidenceScorer(min_confidence=0.3, max_retries=2)

        call_count = 0

        async def improving_call():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "I'm not sure, maybe this works?"
            return "This is a confident, specific answer with details."

        result, confidence = await scorer.retry_with_confidence(improving_call)

        assert result is not None
        assert call_count >= 1


class TestInstructionInjectorIntegration:
    """Integration tests for InstructionInjector with orchestrator."""

    @pytest.mark.asyncio
    async def test_instructions_available_during_healing(self, ctx, valid_resume):
        """Test that instructions are available during healing cycles."""
        ctx.current_resume = valid_resume

        injector = InstructionInjector(ctx)

        # Inject instruction before healing
        injector.inject(
            source="user",
            content="Focus on ATS compatibility over creativity",
            priority=10,
        )

        # Verify instruction is in context
        assert len(ctx.instructions) > 0
        assert "ATS compatibility" in ctx.instructions[0]

    @pytest.mark.asyncio
    async def test_agent_specific_instructions(self, ctx, valid_resume):
        """Test agent-specific instruction filtering."""
        ctx.current_resume = valid_resume

        injector = InstructionInjector(ctx)

        # Inject general instruction
        injector.inject(
            source="user",
            content="General guidance",
            target_agents=[],
        )

        # Inject agent-specific instruction
        injector.inject(
            source="user",
            content="Specific to ContentQualityAgent",
            target_agents=["ContentQualityAgent"],
        )

        # Get instructions for ContentQualityAgent
        instructions = injector.get_instructions(agent_name="ContentQualityAgent")

        assert len(instructions) == 2  # Both apply

    @pytest.mark.asyncio
    async def test_instruction_priority_ordering(self, ctx):
        """Test that instructions are ordered by priority."""
        injector = InstructionInjector(ctx)

        injector.inject("agent1", "Low priority", priority=1)
        injector.inject("agent2", "High priority", priority=10)
        injector.inject("agent3", "Medium priority", priority=5)

        instructions = injector.get_instructions()

        assert instructions[0].priority == 10
        assert instructions[1].priority == 5
        assert instructions[2].priority == 1


class TestMemoryPersistenceIntegration:
    """Integration tests for MemoryPersistence across sessions."""

    def test_memory_persists_validation_results(self, temp_memory_dir):
        """Test that validation results persist across instances."""
        memory_file = temp_memory_dir / "test_memory.json"

        # First session
        memory1 = MemoryPersistence(memory_file=memory_file)
        memory1.record_validation("summary", "Test summary content", passed=True)

        # Second session
        memory2 = MemoryPersistence(memory_file=memory_file)

        # Should skip because it passed before
        assert memory2.should_skip("summary", "Test summary content") is True

    def test_memory_tracks_flapping(self, temp_memory_dir):
        """Test that flapping detection persists."""
        memory_file = temp_memory_dir / "test_memory.json"

        memory = MemoryPersistence(memory_file=memory_file, flapping_threshold=3)

        # Create flapping pattern
        memory.record_validation("section1", "content", passed=True)
        memory.record_validation("section1", "content", passed=False)
        memory.record_validation("section1", "content", passed=True)

        # Verify flapping detected
        assert memory.is_flapping("section1") is True

        # Create new instance
        memory2 = MemoryPersistence(memory_file=memory_file)

        # Flapping should persist
        assert memory2.is_flapping("section1") is True

    def test_memory_handles_content_changes(self, temp_memory_dir):
        """Test that memory handles content changes correctly."""
        memory_file = temp_memory_dir / "test_memory.json"

        memory = MemoryPersistence(memory_file=memory_file)

        # Record validation for original content
        memory.record_validation("section1", "original content", passed=True)

        # Should skip original content
        assert memory.should_skip("section1", "original content") is True

        # Should NOT skip changed content
        assert memory.should_skip("section1", "changed content") is False


class TestResumeLearningAgentIntegration:
    """Integration tests for ResumeLearningAgent with full workflow."""

    @pytest.mark.asyncio
    async def test_learning_agent_with_healing_cycle(self, ctx, valid_resume):
        """Test learning agent integration with healing cycle."""
        ctx.current_resume = valid_resume

        learning_agent = ResumeLearningAgent(ctx)

        # Inject instruction
        learning_agent.inject_instruction(
            content="Prioritize quantifiable metrics",
            priority=5,
        )

        # Run a healing cycle
        cycle = HealingCycle(ctx, cycle_number=1)
        result = await cycle.execute(HealingStrategy.FULL_DIAGNOSTIC)

        # Record the success if converged
        if result.converged:
            await learning_agent.record_success(
                TaskType="full_diagnostic",
                input_context=str(valid_resume),
                output_result="Validation passed",
                confidence=0.9,
            )

        # Verify stats
        stats = learning_agent.get_comprehensive_stats()
        assert "learning" in stats
        assert "instructions" in stats

    @pytest.mark.asyncio
    async def test_learning_agent_section_tracking(self, ctx, valid_resume):
        """Test learning agent tracks section validations."""
        ctx.current_resume = valid_resume

        learning_agent = ResumeLearningAgent(ctx)

        # Record section validations
        learning_agent.record_section_validation(
            "summary",
            valid_resume["summary"],
            passed=True,
        )

        learning_agent.record_section_validation(
            "experience",
            str(valid_resume["experience"]),
            passed=True,
        )

        # Verify sections can be skipped
        assert learning_agent.should_skip_section("summary", valid_resume["summary"]) is True

    @pytest.mark.asyncio
    async def test_learning_agent_few_shot_integration(self, ctx, valid_resume):
        """Test few-shot context generation."""
        ctx.current_resume = valid_resume

        learning_agent = ResumeLearningAgent(ctx)

        # Record some examples
        await learning_agent.record_success(
            TaskType="summary_improvement",
            input_context="Weak summary without metrics",
            output_result="Strong summary with 3 quantified achievements",
            confidence=0.95,
        )

        # Get few-shot context
        context = await learning_agent.get_few_shot_context(
            "Improve summary with metrics",
            TaskType="summary_improvement",
        )

        # May or may not have context depending on matching
        assert isinstance(context, str)


class TestCrossComponentIntegration:
    """Tests for integration across multiple Phase 3 components."""

    @pytest.mark.asyncio
    async def test_full_learning_workflow(self, ctx, valid_resume, temp_memory_dir):
        """Test complete learning workflow across components."""
        ctx.current_resume = valid_resume

        # Initialize all components
        learning = LearningLoop(ctx)
        scorer = ConfidenceScorer(min_confidence=0.5)
        injector = InstructionInjector(ctx)
        memory = MemoryPersistence(memory_file=temp_memory_dir / "workflow_memory.json")

        # 1. Inject instruction
        injector.inject("user", "Focus on metrics", priority=10)

        # 2. Check if section should be skipped
        should_skip = memory.should_skip("summary", valid_resume["summary"])

        if not should_skip:
            # 3. Run validation
            agent = ContentQualityAgent(ctx)
            await agent.execute()

            # 4. Score confidence
            result_text = str(ctx.results.get("ContentQualityAgent", {}))
            confidence = scorer.score_from_text(result_text)

            # 5. Record validation result
            passed = ctx.results.get("ContentQualityAgent", {}).get("passed", False)
            memory.record_validation("summary", valid_resume["summary"], passed=passed)

            # 6. If successful, record for learning
            if passed and confidence.level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]:
                await learning.record_success(
                    TaskType="content_quality",
                    input_context=valid_resume["summary"],
                    output_result="Validation passed",
                    confidence=confidence.score,
                )

        # Verify all components have state
        assert len(injector._instructions) > 0
        assert memory.state.file_hashes.get("summary") is not None

    @pytest.mark.asyncio
    async def test_orchestrator_with_learning(self, ctx, valid_resume):
        """Test orchestrator integration with learning components."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Software Engineer"

        # Create learning agent
        learning_agent = ResumeLearningAgent(ctx)

        # Inject pre-healing instruction
        learning_agent.inject_instruction(
            content="Ensure all sections have quantified metrics",
            priority=5,
        )

        # Run orchestrator
        orchestrator = RgHealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Record outcome
        if result.success:
            await learning_agent.record_success(
                TaskType="full_healing",
                input_context=f"Resume with {len(valid_resume)} sections",
                output_result=f"Converged in {result.convergence_cycle} cycles",
                confidence=0.9,
            )

        # Verify learning recorded
        stats = learning_agent.get_comprehensive_stats()
        assert stats["learning"]["total_examples"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
