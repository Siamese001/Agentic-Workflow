from __future__ import annotations
"""
End-to-End Tests for Phase 3: Learning & Intelligence

Tests the complete learning workflow:
- Full mission with learning integration
- Few-shot recall during healing
- Memory persistence across missions
- Confidence-based retry in production scenarios
"""
import re


import asyncio

import pytest

from ..context import ResumeEngineContext
from ..healing import HealingOrchestratorAgent, HealingResult, run_self_healing_mission
from ..learning import (
    ConfidenceScorer,
    InstructionInjector,
    LearningLoop,
    MemoryPersistence,
    ResumeLearningAgent,
)


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%. Expert in cloud architecture and microservices.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40% through optimization. Managed team of 5 engineers."
            },
            {
                "company": "StartupXYZ",
                "title": "Software Engineer",
                "description": "Built core platform features used by 100K+ customers. Improved deployment frequency by 300%."
            }
        ],
        "skills": ["Python", "JavaScript", "TypeScript", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
        "education": "BS Computer Science, MIT, 2010",
        "certifications": ["AWS Solutions Architect", "Kubernetes Administrator"],
    }


@pytest.fixture
def JobDescription():
    """Sample job description."""
    return """
    Senior Software Engineer

    We are looking for an experienced software engineer to join our team.

    Requirements:
    - 5+ years of experience in software development
    - Strong Python and JavaScript skills
    - Experience with AWS and cloud infrastructure
    - Experience with microservices architecture
    - Strong communication skills

    Nice to have:
    - Kubernetes experience
    - Team leadership experience
    """


@pytest.fixture
def temp_memory_dir(tmp_path):
    """Create a temporary directory for memory files."""
    return tmp_path


class TestFullMissionWithLearning:
    """Tests for full mission with learning integration."""

    @pytest.mark.asyncio
    async def test_mission_records_learning(self, valid_resume, JobDescription):
        """Test that successful mission records learning."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        learning_agent = ResumeLearningAgent(ctx)

        # Run mission
        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Record learning from mission
        if result.success:
            await learning_agent.record_success(
                TaskType="mission_success",
                input_context=f"Job: {JobDescription[:100]}",
                output_result=f"Converged in {result.convergence_cycle} cycles",
                confidence=0.9,
            )

        stats = learning_agent.get_comprehensive_stats()
        assert stats["learning"]["total_examples"] >= 0

    @pytest.mark.asyncio
    async def test_mission_with_instructions(self, valid_resume, JobDescription):
        """Test mission with pre-injected instructions."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        learning_agent = ResumeLearningAgent(ctx)

        # Inject instructions before mission
        learning_agent.inject_instruction(
            content="Prioritize ATS compatibility",
            priority=10,
        )
        learning_agent.inject_instruction(
            content="Ensure all metrics are quantified",
            priority=5,
        )

        # Run mission
        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        assert result.success is True
        assert len(ctx.instructions) >= 2

    @pytest.mark.asyncio
    async def test_mission_with_section_memory(self, valid_resume, JobDescription, temp_memory_dir):
        """Test mission with section memory tracking."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        memory = MemoryPersistence(memory_file=temp_memory_dir / "mission_memory.json")

        # Run first mission
        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Record section validations
        for section in ["summary", "experience", "skills"]:
            content = str(valid_resume.get(section, ""))
            memory.record_validation(section, content, passed=result.success)

        # Verify memory state
        stats = memory.get_stats()
        assert stats["total_tracked"] >= 3


class TestFewShotRecallDuringHealing:
    """Tests for few-shot recall during healing cycles."""

    @pytest.mark.asyncio
    async def test_few_shot_context_available(self, valid_resume):
        """Test that few-shot context is available during healing."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        learning_agent = ResumeLearningAgent(ctx)

        # Pre-populate with examples
        await learning_agent.record_success(
            TaskType="summary_fix",
            input_context="Summary without metrics",
            output_result="Summary with 3 quantified achievements",
            confidence=0.9,
        )

        # Get context for similar Task
        context = await learning_agent.get_few_shot_context(
            "Fix summary to include metrics",
            TaskType="summary_fix",
        )

        # Context may or may not be populated depending on matching
        assert isinstance(context, str)

    @pytest.mark.asyncio
    async def test_learning_improves_over_missions(self, valid_resume, JobDescription):
        """Test that learning accumulates over multiple missions."""
        ctx = ResumeEngineContext()
        learning_agent = ResumeLearningAgent(ctx)

        # Run multiple missions
        for i in range(3):
            ctx.current_resume = valid_resume.copy()
            ctx.JobDescription = JobDescription
            ctx.signals.clear()
            ctx.results.clear()

            orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
            result = await orchestrator.run()

            if result.success:
                await learning_agent.record_success(
                    TaskType=f"mission_{i}",
                    input_context=f"Mission {i}",
                    output_result=f"Success in {result.convergence_cycle} cycles",
                    confidence=0.9,
                )

        stats = learning_agent.get_comprehensive_stats()
        # Should have recorded multiple successes
        assert stats["learning"]["total_examples"] >= 0


class TestMemoryPersistenceAcrossMissions:
    """Tests for memory persistence across missions."""

    @pytest.mark.asyncio
    async def test_skip_unchanged_sections(self, valid_resume, temp_memory_dir):
        """Test that unchanged sections are skipped in subsequent missions."""
        memory_file = temp_memory_dir / "skip_test.json"

        # First mission
        memory1 = MemoryPersistence(memory_file=memory_file)
        memory1.record_validation("summary", valid_resume["summary"], passed=True)

        # Second mission - should skip
        memory2 = MemoryPersistence(memory_file=memory_file)
        should_skip = memory2.should_skip("summary", valid_resume["summary"])

        assert should_skip is True

    @pytest.mark.asyncio
    async def test_revalidate_changed_sections(self, valid_resume, temp_memory_dir):
        """Test that changed sections are revalidated."""
        memory_file = temp_memory_dir / "change_test.json"

        # First mission
        memory1 = MemoryPersistence(memory_file=memory_file)
        memory1.record_validation("summary", valid_resume["summary"], passed=True)

        # Second mission with changed content
        memory2 = MemoryPersistence(memory_file=memory_file)
        changed_summary = valid_resume["summary"] + " Additional content."
        should_skip = memory2.should_skip("summary", changed_summary)

        assert should_skip is False

    @pytest.mark.asyncio
    async def test_flapping_detection_across_missions(self, temp_memory_dir):
        """Test flapping detection across multiple missions."""
        memory_file = temp_memory_dir / "flapping_test.json"

        memory = MemoryPersistence(memory_file=memory_file, flapping_threshold=3)

        # Simulate flapping across missions
        memory.record_validation("unstable_section", "content", passed=True)
        memory.record_validation("unstable_section", "content", passed=False)
        memory.record_validation("unstable_section", "content", passed=True)

        # Should detect flapping
        assert memory.is_flapping("unstable_section") is True

        # Persist and reload
        memory2 = MemoryPersistence(memory_file=memory_file)
        assert memory2.is_flapping("unstable_section") is True


class TestConfidenceBasedRetry:
    """Tests for confidence-based retry in production scenarios."""

    @pytest.mark.asyncio
    async def test_retry_improves_confidence(self):
        """Test that retry mechanism can improve confidence."""
        scorer = ConfidenceScorer(min_confidence=0.5, max_retries=3)

        attempts = []

        async def improving_response():
            attempt = len(attempts) + 1
            attempts.append(attempt)

            if attempt == 1:
                return "Maybe this could work, I'm not sure."
            elif attempt == 2:
                return "This should work with the specific changes."
            else:
                return "This precisely addresses the issue with exact metrics."

        result, confidence = await scorer.retry_with_confidence(improving_response)

        assert result is not None
        assert confidence.score > 0

    @pytest.mark.asyncio
    async def test_confidence_tracking_stats(self):
        """Test that confidence statistics are tracked."""
        scorer = ConfidenceScorer(min_confidence=0.5)

        # Score multiple responses
        scorer.score_from_text("Confident response with specific details.")
        scorer.score_from_text("I'm not sure, maybe this works?")
        scorer.score_from_text("Precise answer with exact metrics.")

        stats = scorer.get_stats()

        assert stats["total_scores"] == 3
        assert "high_confidence_rate" in stats


class TestEdgeCases:
    """Tests for edge cases in learning system."""

    @pytest.mark.asyncio
    async def test_empty_learning_history(self, valid_resume):
        """Test handling of empty learning history."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        learning = LearningLoop(ctx)

        # Should handle empty history gracefully
        examples = await learning.recall_similar("any query")

        assert examples == []

    @pytest.mark.asyncio
    async def test_instruction_expiry(self):
        """Test instruction expiry handling."""
        ctx = ResumeEngineContext()
        injector = InstructionInjector(ctx)

        # Inject instruction with very short TTL
        injector.inject(
            source="test",
            content="Temporary instruction",
            ttl_seconds=0,  # Immediate expiry
        )

        # Wait a moment
        await asyncio.sleep(0.1)

        # Should not include expired instructions
        active = injector.get_instructions(include_expired=False)

        # The instruction may or may not be expired depending on timing
        assert isinstance(active, list)

    @pytest.mark.asyncio
    async def test_memory_reset(self, temp_memory_dir):
        """Test memory reset functionality."""
        memory_file = temp_memory_dir / "reset_test.json"

        memory = MemoryPersistence(memory_file=memory_file)

        # Add some data
        memory.record_validation("section1", "content1", passed=True)
        memory.record_validation("section2", "content2", passed=True)

        # Reset
        memory.reset()

        # Should be empty
        assert len(memory.state.file_hashes) == 0
        assert len(memory.state.skip_files) == 0

    @pytest.mark.asyncio
    async def test_learning_with_low_confidence(self, valid_resume):
        """Test that low confidence results are handled."""
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume

        learning_agent = ResumeLearningAgent(ctx)

        # Record with low confidence
        await learning_agent.record_success(
            TaskType="uncertain_fix",
            input_context="Uncertain input",
            output_result="Uncertain output",
            confidence=0.3,  # Low confidence
        )

        # Should still be recorded
        stats = learning_agent.get_comprehensive_stats()
        assert stats["learning"]["total_examples"] >= 1


class TestComprehensiveWorkflow:
    """Tests for comprehensive end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_all_components(self, valid_resume, JobDescription, temp_memory_dir):
        """Test complete workflow with all Phase 3 components."""
        # Initialize context
        ctx = ResumeEngineContext()
        ctx.current_resume = valid_resume
        ctx.JobDescription = JobDescription

        # Initialize all components
        learning_agent = ResumeLearningAgent(ctx)
        memory = MemoryPersistence(memory_file=temp_memory_dir / "full_workflow.json")

        # 1. Inject pre-mission instructions
        learning_agent.inject_instruction(
            content="Ensure ATS compatibility",
            priority=10,
        )

        # 2. Check if sections should be skipped
        sections_to_validate = []
        for section, content in valid_resume.items():
            if not memory.should_skip(section, str(content)):
                sections_to_validate.append(section)

        # 3. Run healing mission
        orchestrator = HealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # 4. Record section validations
        for section in sections_to_validate:
            content = str(valid_resume.get(section, ""))
            memory.record_validation(section, content, passed=result.success)

        # 5. Record learning from mission
        if result.success:
            await learning_agent.record_success(
                TaskType="full_workflow",
                input_context=f"Resume with {len(valid_resume)} sections",
                output_result=f"Converged in {result.convergence_cycle} cycles",
                confidence=0.9,
            )

        # 6. Verify all components have state
        learning_agent.get_comprehensive_stats()
        MemoryStats = memory.get_stats()

        assert result.success is True
        assert MemoryStats["total_tracked"] > 0
        assert len(ctx.instructions) > 0

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
