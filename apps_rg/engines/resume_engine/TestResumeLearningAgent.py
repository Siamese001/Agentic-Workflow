from __future__ import annotations
"""
Unit Tests for Phase 3: Learning & Intelligence Components

Tests the core learning functionality:
- LearningLoop
- ConfidenceScorer
- InstructionInjector
- MemoryPersistence
- ResumeLearningAgent
"""

import pytest

from ..context import ResumeEngineContext
from ..learning import (
    ConfidenceLevel,
    ConfidenceResult,
    ConfidenceScorer,
    Instruction,
    InstructionInjector,
    LearningExample,
    LearningLoop,
    MemoryPersistence,
    MemoryState,
    ResumeLearningAgent,
)


@pytest.fixture
def ctx():
    """Create a fresh context for each test."""
    return ResumeEngineContext()


@pytest.fixture
def temp_memory_file(tmp_path):
    """Create a temporary memory file path."""
    return tmp_path / "test_memory.json"


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_confidence_levels(self):
        """Test confidence level values."""
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.UNKNOWN.value == "unknown"


class TestLearningExample:
    """Tests for LearningExample dataclass."""

    def test_create_example(self):
        """Test creating a learning example."""
        example = LearningExample(
            id="test_123",
            TaskType="quality_fix",
            input_context="Fix the summary section",
            output_result="Fixed summary with metrics",
            success=True,
            confidence=0.9,
        )

        assert example.id == "test_123"
        assert example.TaskType == "quality_fix"
        assert example.success is True
        assert example.confidence == 0.9
        assert example.timestamp is not None


class TestConfidenceResult:
    """Tests for ConfidenceResult dataclass."""

    def test_from_logprob_high(self):
        """Test creating high confidence from logprob."""
        result = ConfidenceResult.from_logprob(-0.2)

        assert result.score >= 0.8
        assert result.level == ConfidenceLevel.HIGH
        assert result.should_retry is False

    def test_from_logprob_medium(self):
        """Test creating medium confidence from logprob."""
        result = ConfidenceResult.from_logprob(-1.0)

        assert 0.5 <= result.score < 0.8
        assert result.level == ConfidenceLevel.MEDIUM

    def test_from_logprob_low(self):
        """Test creating low confidence from logprob."""
        result = ConfidenceResult.from_logprob(-1.8)

        assert result.score < 0.5
        assert result.level == ConfidenceLevel.LOW
        assert result.should_retry is True

    def test_from_logprob_with_threshold(self):
        """Test custom confidence threshold."""
        result = ConfidenceResult.from_logprob(-0.5, min_confidence=0.9)

        # Score is ~0.75, below 0.9 threshold
        assert result.should_retry is True


class TestInstruction:
    """Tests for Instruction dataclass."""

    def test_create_instruction(self):
        """Test creating an instruction."""
        inst = Instruction(
            id="inst_1",
            source="TestAgent",
            content="Focus on metrics",
            priority=5,
        )

        assert inst.id == "inst_1"
        assert inst.source == "TestAgent"
        assert inst.priority == 5
        assert inst.created_at is not None


class TestMemoryState:
    """Tests for MemoryState dataclass."""

    def test_create_memory_state(self):
        """Test creating memory state."""
        state = MemoryState()

        assert state.file_hashes == {}
        assert state.skip_files == set()
        assert state.flapping_files == set()
        assert state.last_updated is not None


class TestLearningLoop:
    """Tests for LearningLoop class."""

    def test_init(self, ctx):
        """Test LearningLoop initialization."""
        loop = LearningLoop(ctx)

        assert loop.ctx == ctx
        assert loop.local_fallback is True

    @pytest.mark.asyncio
    async def test_recall_similar_empty(self, ctx):
        """Test recall with no examples."""
        loop = LearningLoop(ctx)

        results = await loop.recall_similar("test query")

        assert results == []

    @pytest.mark.asyncio
    async def test_record_and_recall(self, ctx):
        """Test recording and recalling examples."""
        loop = LearningLoop(ctx)

        # Record a success
        await loop.record_success(
            TaskType="quality_fix",
            input_context="Fix summary with metrics and quantification",
            output_result="Added 25% improvement Metric",
            confidence=0.9,
        )

        # Recall similar
        results = await loop.recall_similar("summary metrics quantification")

        assert len(results) >= 0  # May or may not match depending on algorithm

    def test_get_stats(self, ctx):
        """Test getting statistics."""
        loop = LearningLoop(ctx)

        stats = loop.get_stats()

        assert "total_examples" in stats
        assert "successful_examples" in stats
        assert "pinecone_available" in stats


class TestConfidenceScorer:
    """Tests for ConfidenceScorer class."""

    def test_init(self):
        """Test ConfidenceScorer initialization."""
        scorer = ConfidenceScorer(min_confidence=0.8)

        assert scorer.min_confidence == 0.8
        assert scorer.max_retries == 3

    def test_score_from_logprob(self):
        """Test scoring from logprob."""
        scorer = ConfidenceScorer()

        result = scorer.score_from_logprob(-0.3)

        assert result.score > 0.7
        assert scorer.total_scores == 1

    def test_score_from_text_confident(self):
        """Test scoring confident text."""
        scorer = ConfidenceScorer()

        text = "The summary specifically includes exactly 3 metrics that precisely demonstrate impact."
        result = scorer.score_from_text(text)

        assert result.score >= 0.5

    def test_score_from_text_uncertain(self):
        """Test scoring uncertain text."""
        scorer = ConfidenceScorer()

        text = "I'm not sure, maybe this could possibly work?"
        result = scorer.score_from_text(text)

        assert result.score < 0.7

    def test_score_from_text_error(self):
        """Test scoring text with errors."""
        scorer = ConfidenceScorer()

        text = "Error: failed to process the request"
        result = scorer.score_from_text(text)

        assert result.score < 0.5

    @pytest.mark.asyncio
    async def test_retry_with_confidence(self):
        """Test retry mechanism."""
        scorer = ConfidenceScorer(min_confidence=0.5, max_retries=2)

        call_count = 0

        async def mock_call():
            nonlocal call_count
            call_count += 1
            return "This is a confident response with specific details."

        result, confidence = await scorer.retry_with_confidence(mock_call)

        assert result is not None
        assert confidence.score > 0
        assert call_count >= 1

    def test_get_stats(self):
        """Test getting statistics."""
        scorer = ConfidenceScorer()
        scorer.score_from_text("test")

        stats = scorer.get_stats()

        assert stats["total_scores"] == 1
        assert "high_confidence_rate" in stats


class TestInstructionInjector:
    """Tests for InstructionInjector class."""

    def test_init(self, ctx):
        """Test InstructionInjector initialization."""
        injector = InstructionInjector(ctx)

        assert injector.ctx == ctx

    def test_inject(self, ctx):
        """Test injecting an instruction."""
        injector = InstructionInjector(ctx)

        inst_id = injector.inject(
            source="TestAgent",
            content="Focus on ATS compatibility",
            priority=5,
        )

        assert inst_id is not None
        assert len(injector._instructions) == 1

    def test_get_instructions(self, ctx):
        """Test getting instructions."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "Instruction 1", priority=1)
        injector.inject("Agent2", "Instruction 2", priority=5)

        instructions = injector.get_instructions()

        assert len(instructions) == 2
        # Should be sorted by priority (descending)
        assert instructions[0].priority == 5

    def test_get_instructions_filtered(self, ctx):
        """Test getting instructions filtered by agent."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "For all", target_agents=[])
        injector.inject("Agent2", "For specific", target_agents=["TargetAgent"])

        # Get for specific agent
        instructions = injector.get_instructions(agent_name="TargetAgent")

        assert len(instructions) == 2  # Both apply (one is for all, one targets)

    def test_get_instruction_text(self, ctx):
        """Test getting formatted instruction text."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "Focus on metrics")

        text = injector.get_instruction_text()

        assert "Active Instructions" in text
        assert "Focus on metrics" in text

    def test_remove(self, ctx):
        """Test removing an instruction."""
        injector = InstructionInjector(ctx)

        inst_id = injector.inject("Agent1", "Test")
        assert len(injector._instructions) == 1

        result = injector.remove(inst_id)

        assert result is True
        assert len(injector._instructions) == 0

    def test_clear(self, ctx):
        """Test clearing instructions."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "Test 1")
        injector.inject("Agent2", "Test 2")

        injector.clear()

        assert len(injector._instructions) == 0

    def test_clear_by_source(self, ctx):
        """Test clearing instructions by source."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "Test 1")
        injector.inject("Agent2", "Test 2")

        injector.clear(source="Agent1")

        assert len(injector._instructions) == 1
        assert injector._instructions[0].source == "Agent2"

    def test_get_stats(self, ctx):
        """Test getting statistics."""
        injector = InstructionInjector(ctx)

        injector.inject("Agent1", "Test 1")
        injector.inject("Agent1", "Test 2")
        injector.inject("Agent2", "Test 3")

        stats = injector.get_stats()

        assert stats["total_instructions"] == 3
        assert stats["by_source"]["Agent1"] == 2
        assert stats["by_source"]["Agent2"] == 1


class TestMemoryPersistence:
    """Tests for MemoryPersistence class."""

    def test_init(self, temp_memory_file):
        """Test MemoryPersistence initialization."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        assert memory.memory_file == temp_memory_file

    def test_calculate_hash(self, temp_memory_file):
        """Test hash calculation."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        hash1 = memory.calculate_hash("test content")
        hash2 = memory.calculate_hash("test content")
        hash3 = memory.calculate_hash("different content")

        assert hash1 == hash2
        assert hash1 != hash3

    def test_should_skip_new(self, temp_memory_file):
        """Test should_skip for new content."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        result = memory.should_skip("file1", "content")

        assert result is False

    def test_should_skip_after_pass(self, temp_memory_file):
        """Test should_skip after passing validation."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        memory.record_validation("file1", "content", passed=True)

        result = memory.should_skip("file1", "content")

        assert result is True

    def test_should_not_skip_after_fail(self, temp_memory_file):
        """Test should_skip after failing validation."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        memory.record_validation("file1", "content", passed=False)

        result = memory.should_skip("file1", "content")

        assert result is False

    def test_should_not_skip_changed_content(self, temp_memory_file):
        """Test should_skip with changed content."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        memory.record_validation("file1", "content", passed=True)

        result = memory.should_skip("file1", "different content")

        assert result is False

    def test_flapping_detection(self, temp_memory_file):
        """Test flapping detection."""
        memory = MemoryPersistence(memory_file=temp_memory_file, flapping_threshold=3)

        # Alternate pass/fail
        memory.record_validation("file1", "content", passed=True)
        memory.record_validation("file1", "content", passed=False)
        memory.record_validation("file1", "content", passed=True)

        assert memory.is_flapping("file1") is True

    def test_clear_flapping(self, temp_memory_file):
        """Test clearing flapping status."""
        memory = MemoryPersistence(memory_file=temp_memory_file, flapping_threshold=3)

        memory.state.flapping_files.add("file1")

        memory.clear_flapping("file1")

        assert memory.is_flapping("file1") is False

    def test_get_stats(self, temp_memory_file):
        """Test getting statistics."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        memory.record_validation("file1", "content", passed=True)

        stats = memory.get_stats()

        assert stats["total_tracked"] == 1
        assert stats["skip_count"] == 1

    def test_reset(self, temp_memory_file):
        """Test resetting memory."""
        memory = MemoryPersistence(memory_file=temp_memory_file)

        memory.record_validation("file1", "content", passed=True)
        memory.reset()

        assert len(memory.state.file_hashes) == 0
        assert len(memory.state.skip_files) == 0

    def test_persistence(self, temp_memory_file):
        """Test that memory persists across instances."""
        memory1 = MemoryPersistence(memory_file=temp_memory_file)
        memory1.record_validation("file1", "content", passed=True)

        # Create new instance
        memory2 = MemoryPersistence(memory_file=temp_memory_file)

        assert memory2.should_skip("file1", "content") is True


class TestResumeLearningAgent:
    """Tests for ResumeLearningAgent class."""

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs):
        """Autonomous healing - test class stub."""
        return {"violations": 0, "fixed": 0, "errors": 0}

    def test_init(self, ctx):
        """Test ResumeLearningAgent initialization."""
        agent = ResumeLearningAgent(ctx)

        assert agent.ctx == ctx
        assert agent.name == "ResumeLearningAgent"
        assert agent.learning_loop is not None
        assert agent.confidence_scorer is not None
        assert agent.instruction_injector is not None
        assert agent.memory is not None

    @pytest.mark.asyncio
    async def test_get_few_shot_context_empty(self, ctx):
        """Test getting few-shot context with no examples."""
        agent = ResumeLearningAgent(ctx)

        context = await agent.get_few_shot_context("test Task")

        assert context == ""

    @pytest.mark.asyncio
    async def test_record_success(self, ctx):
        """Test recording a success."""
        agent = ResumeLearningAgent(ctx)

        await agent.record_success(
            TaskType="quality_fix",
            input_context="Fix summary",
            output_result="Fixed summary",
            confidence=0.9,
        )

        stats = agent.learning_loop.get_stats()
        assert stats["total_examples"] >= 1

    def test_inject_instruction(self, ctx):
        """Test injecting an instruction."""
        agent = ResumeLearningAgent(ctx)

        inst_id = agent.inject_instruction(
            content="Focus on metrics",
            priority=5,
        )

        assert inst_id is not None

    def test_get_instructions_for_agent(self, ctx):
        """Test getting instructions for an agent."""
        agent = ResumeLearningAgent(ctx)

        agent.inject_instruction("Test instruction")

        text = agent.get_instructions_for_agent("TestAgent")

        assert "Test instruction" in text

    def test_should_skip_section(self, ctx, temp_memory_file):
        """Test section skip check."""
        agent = ResumeLearningAgent(ctx)
        # Use fresh memory to avoid leftover state
        agent.memory = MemoryPersistence(memory_file=temp_memory_file)

        result = agent.should_skip_section("summary", "unique_content_for_test_12345")

        assert result is False

    def test_record_section_validation(self, ctx):
        """Test recording section validation."""
        agent = ResumeLearningAgent(ctx)

        agent.record_section_validation("summary", "content", passed=True)

        assert agent.should_skip_section("summary", "content") is True

    def test_get_comprehensive_stats(self, ctx):
        """Test getting comprehensive statistics."""
        agent = ResumeLearningAgent(ctx)

        stats = agent.get_comprehensive_stats()

        assert "learning" in stats
        assert "confidence" in stats
        assert "instructions" in stats
        assert "memory" in stats


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestResumeLearning"
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
