"""Test suite for Reflection Engine integration with Subatomic Hop."""

import pytest
import asyncio

    ReflectionEngine,
    ReflectionConfig,
    CritiqueResult,
    ValidationCriterion,
    get_reflection_engine,
    evaluate_content,
    STANDARD_CRITERIA,
    STRICT_CRITERIA
)

    SubatomicHop,
    SubatomicHopConfig,
    ReflectionConfig as HopReflectionConfig,
    MicroStage,
    HopState,
    QualityGateFailure
)

class TestReflectionEngine:
    """Test suite for ReflectionEngine."""

    def setup_method(self):
            """Setup test fixtures."""
        self.config = ReflectionConfig(
            use_fast_model=True,
            max_critique_loops=3,
            confidence_threshold=0.7
        )
        self.engine = ReflectionEngine(self.config)

    def test_initialization(self):
            """Test ReflectionEngine initialization."""
        assert self.engine.config.max_critique_loops == 3
        assert self.engine.config.confidence_threshold == 0.7
        assert len(self.engine.builtin_criteria) > 0
        assert self.engine.stats["total_critiques"] == 0

    @pytest.mark.asyncio
    async def test_fast_path_validation(self):
            """Test fast path validation with regex patterns."""
        content = {"result": "success", "data": [1, 2, 3]}
        criteria = ["json_valid", "no_empty_fields"]

        result = await self.engine.evaluate(content, criteria)

        assert result.is_valid is True
        assert result.validation_type == "regex"
        assert result.confidence_score >= 0.7

    @pytest.mark.asyncio
    async def test_fast_path_failure(self):
            """Test fast path validation failure."""
        content = {"result": None, "data": ""}  # Empty values
        criteria = ["json_valid", "no_empty_fields"]

        result = await self.engine.evaluate(content, criteria)

        assert result.is_valid is False
        assert result.validation_type == "regex"
        assert "Failed" in result.critique_reasoning

    @pytest.mark.asyncio
    async def test_llm_path_validation(self):
            """Test LLM path validation for semantic criteria."""
        content = "This is some text content"
        custom_criteria = [
            ValidationCriterion(
                name="semantic_check",
                description="Must be meaningful content",
                validator=lambda x: False  # Force LLM path
            )
        ]

        result = await self.engine.evaluate(content, custom_criteria)

        assert result.validation_type in ["llm", "llm_error"]
        assert isinstance(result.confidence_score, float)

    @pytest.mark.asyncio
    async def test_mixed_criteria(self):
            """Test evaluation with mixed criteria types."""
        content = {"status": "ok", "message": "All good"}
        criteria = [
            "json_valid",  # Built-in
            ValidationCriterion(
                name="custom_check",
                description="Custom validation",
                validator=lambda x: True
            )
        ]

        result = await self.engine.evaluate(content, criteria)

        assert result.is_valid is True
        assert result.confidence_score > 0

    def test_statistics_tracking(self):
            """Test statistics tracking."""
        initial_stats = self.engine.get_stats()
        assert initial_stats["total_critiques"] == 0

        # Reset and check
        self.engine.reset_stats()
        stats = self.engine.get_stats()
        assert stats["total_critiques"] == 0

    @pytest.mark.asyncio
    async def test_regex_validation(self):
            """Test regex pattern validation."""
        content = "Contact us at support@example.com"

        # Email regex pattern
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        criterion = ValidationCriterion(
            name="contains_email",
            description="Must contain email address",
            validator=pattern
        )

        result = await self.engine.evaluate(content, [criterion])

        assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
            """Test confidence threshold enforcement."""
        # Set high threshold
        config = ReflectionConfig(confidence_threshold=0.9)
        engine = ReflectionEngine(config)

        content = {"partial": "data"}  # Partially valid
        criteria = ["json_valid", "no_empty_fields"]

        result = await engine.evaluate(content, criteria)

        # Should fail if confidence below threshold
        if result.confidence_score < 0.9:
            assert result.is_valid is False

class TestSubatomicHopReflection:
    """Test suite for SubatomicHop with Reflection Engine integration."""

    def setup_method(self):
            """Setup test fixtures."""
        self.reflection_config = HopReflectionConfig(
            max_critique_loops=2,
            confidence_threshold=0.7
        )
        self.config = SubatomicHopConfig(
            reflection_config=self.reflection_config,
            critique_criteria=["json_valid", "no_empty_fields"]
        )

    @pytest.mark.asyncio
    async def test_successful_execution_with_reflection(self):
            """Test successful hop execution with reflection validation."""
        def good_hop(x):
                """Docstring."""
            return {"result": x * 2, "status": "success"}

        hop = SubatomicHop(good_hop, self.config)
        result = await hop.run(x=5)

        assert result["result"] == 10
        assert hop.state == HopState.COMPLETED
        assert hop.critique_loop_count == 0

        # Check critique result was stored
        assert "critique_result" in hop.context
        assert hop.context["critique_result"]["is_valid"] is True

    @pytest.mark.asyncio
    async def test_critique_failure_and_retry(self):
            """Test hop execution with critique failure and retry."""
        attempt_count = 0

        def flaky_hop(x):
                """Docstring."""
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count == 1:
                return {"result": None}  # Will fail validation
            else:
                return {"result": x * 3, "fixed": True}

        hop = SubatomicHop(flaky_hop, self.config)
        result = await hop.run(x=5)

        assert result["result"] == 15
        assert result["fixed"] is True
        assert hop.critique_loop_count == 1
        assert hop.state == HopState.COMPLETED

    @pytest.mark.asyncio
    async def test_critique_max_loops_exceeded(self):
            """Test failure when max critique loops exceeded."""
        def always_bad_hop(x):
                """Docstring."""
            return {"result": None}  # Always fails validation

        hop = SubatomicHop(always_bad_hop, self.config)

        with pytest.raises(QualityGateFailure, match="Failed quality validation"):
            await hop.run(x=5)

        assert hop.critique_loop_count > self.reflection_config.max_critique_loops
        assert hop.state == HopState.FAILED

    @pytest.mark.asyncio
    async def test_critique_feedback_incorporation(self):
            """Test that critique feedback is incorporated in retry."""
        def learning_hop(x):
                """Docstring."""
            plan = hop.context.get("execution_plan", {})

            if "feedback" in plan:
                # Incorporate feedback
                return {"result": x * 4, "improved": True}
            else:
                return {"result": None}  # Will fail

        hop = SubatomicHop(learning_hop, self.config)
        result = await hop.run(x=5)

        assert result["result"] == 20
        assert result["improved"] is True
        assert hop.critique_loop_count == 1

    @pytest.mark.asyncio
    async def test_custom_validation_criteria(self):
            """Test hop with custom validation criteria."""
        custom_config = SubatomicHopConfig(
            reflection_config=self.reflection_config,
            critique_criteria=[
                ValidationCriterion(
                    name="has_result_field",
                    description="Must have 'result' field",
                    validator=lambda x: isinstance(x, dict) and "result" in x
                )
            ]
        )

        def test_hop(x):
                """Docstring."""
            return {"output": x}  # Missing 'result' field

        hop = SubatomicHop(test_hop, custom_config)

        with pytest.raises(QualityGateFailure):
            await hop.run(x=5)

    @pytest.mark.asyncio
    async def test_reflection_statistics(self):
            """Test reflection engine statistics during hop execution."""
        def good_hop(x):
                """Docstring."""
            return {"data": x}

        hop = SubatomicHop(good_hop, self.config)
        await hop.run(x=10)

        stats = hop.reflection_engine.get_stats()
        assert stats["total_critiques"] > 0
        assert stats["passes"] > 0
        assert stats["average_confidence"] > 0

class TestReflectionIntegration:
    """Integration tests for reflection system."""

    @pytest.mark.asyncio
    async def test_global_reflection_engine(self):
            """Test global reflection engine instance."""
        engine1 = get_reflection_engine()
        engine2 = get_reflection_engine()

        # Should return same instance
        assert engine1 is engine2

    @pytest.mark.asyncio
    async def test_convenience_function(self):
            """Test convenience evaluation function."""
        content = {"test": "data"}
        result = await evaluate_content(
            content,
            ["json_valid"],
            context={"test": True}
        )

        assert isinstance(result, CritiqueResult)
        assert result.is_valid is True

    def test_predefined_criteria_sets(self):
            """Test predefined criteria sets."""
        assert len(STANDARD_CRITERIA) > 0
        assert len(STRICT_CRITERIA) > len(STANDARD_CRITERIA)
        assert "json_valid" in STANDARD_CRITERIA
        assert "no_empty_fields" in STANDARD_CRITERIA

# Performance tests
class TestReflectionPerformance:
    """Test performance of reflection system."""

    @pytest.mark.asyncio
    async def test_fast_path_performance(self):
            """Test that fast path is indeed fast."""
        engine = ReflectionEngine()
        content = {"data": "test" * 100}

        start_time = asyncio.get_event_loop().time()
        result = await engine.evaluate(content, ["json_valid"])
        end_time = asyncio.get_event_loop().time()

        assert result.is_valid is True
        assert result.validation_type == "regex"
        assert (end_time - start_time) < 0.1  # Should be very fast

    @pytest.mark.asyncio
    async def test_concurrent_evaluations(self):
            """Test concurrent reflection evaluations."""
        engine = ReflectionEngine()

        tasks = []
        for i in range(10):
            task = engine.evaluate({"id": i}, ["json_valid"])
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        assert all(r.is_valid for r in results)
        assert engine.stats["total_critiques"] == 10

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
