"""
Phase 5 Optimization Tests - Prompt Optimizer
Tests for LLM prompt optimization utilities.
"""

import pytest
from apps_shared.llm.prompt_optimizer_types import (
    PromptOptimizer,
    PromptTemplate,
    OptimizedPrompt,
)


class TestPromptTemplate:
    """Test PromptTemplate dataclass."""

    def test_prompt_template_creation(self):
        """Test creating PromptTemplate."""
        template = PromptTemplate(
            system="You are a helpful assistant",
            user="Please help with {task}",
            variables=["task"],
            examples=[],
            metadata={},
        )

        assert template.system == "You are a helpful assistant"
        assert template.user == "Please help with {task}"
        assert template.variables == ["task"]


class TestOptimizedPrompt:
    """Test OptimizedPrompt dataclass."""

    def test_optimized_prompt_creation(self):
        """Test creating OptimizedPrompt."""
        prompt = OptimizedPrompt(
            prompt="Test prompt",
            token_count=3,
            variables_used={"task": "testing"},
            optimization_applied=["test"],
        )

        assert prompt.prompt == "Test prompt"
        assert prompt.token_count == 3


class TestPromptOptimizer:
    """Test PromptOptimizer functionality."""

    def test_create_template_simple(self):
        """Test creating simple template."""
        template = PromptOptimizer.create_template(system="System message", user="User message")

        assert template.system == "System message"
        assert template.user == "User message"
        assert template.variables == []
        assert template.examples == []

    def test_create_template_with_variables(self):
        """Test creating template with variables."""
        template = PromptOptimizer.create_template(
            system="System", user="Task: {task}", variables=["task"]
        )

        assert template.variables == ["task"]

    def test_format_prompt_simple(self):
        """Test formatting simple prompt."""
        template = PromptOptimizer.create_template(
            system="You are helpful", user="Help with {task}"
        )
        template.variables = ["task"]

        result = PromptOptimizer.format_prompt(template, task="testing")

        assert "testing" in result.prompt
        assert result.variables_used == {"task": "testing"}

    def test_format_prompt_with_examples(self):
        """Test formatting prompt with examples."""
        template = PromptOptimizer.create_template(
            system="System",
            user="Task: {task}",
            examples=[{"input": "test input", "output": "test output"}],
        )
        template.variables = ["task"]

        result = PromptOptimizer.format_prompt(template, task="new task")

        assert "Example" in result.prompt
        assert "test input" in result.prompt
        assert "Added few-shot examples" in result.optimization_applied

    def test_format_prompt_missing_variable(self):
        """Test formatting with missing variable."""
        template = PromptOptimizer.create_template(system="System", user="Task: {task}")
        template.variables = ["task"]

        result = PromptOptimizer.format_prompt(template)

        assert any("Missing variable" in opt for opt in result.optimization_applied)

    def test_compress_prompt_within_limit(self):
        """Test compressing prompt within limit."""
        prompt = "Short prompt"
        result = PromptOptimizer.compress_prompt(prompt, max_tokens=100)

        assert result == prompt

    def test_compress_prompt_exceeds_limit(self):
        """Test compressing prompt that exceeds limit."""
        prompt = "A" * 1000
        result = PromptOptimizer.compress_prompt(prompt, max_tokens=50)

        assert len(result) < len(prompt)
        assert "truncated" in result

    def test_add_context_empty(self):
        """Test adding empty context."""
        prompt = "Original prompt"
        result = PromptOptimizer.add_context(prompt, {})

        assert result == prompt

    def test_add_context_with_items(self):
        """Test adding context with items."""
        prompt = "Task"
        context = {"user": "John", "role": "admin"}
        result = PromptOptimizer.add_context(prompt, context)

        assert "Context:" in result
        assert "user: John" in result
        assert "role: admin" in result

    def test_add_context_max_items(self):
        """Test adding context with max items limit."""
        prompt = "Task"
        context = {f"key{i}": f"value{i}" for i in range(10)}
        result = PromptOptimizer.add_context(prompt, context, max_context_items=3)

        # Should only include first 3 items
        assert "key0" in result
        assert "key1" in result
        assert "key2" in result

    def test_create_chain_of_thought_prompt(self):
        """Test creating chain-of-thought prompt."""
        task = "Solve math problem"
        steps = ["Understand the problem", "Break it down", "Solve each part"]

        result = PromptOptimizer.create_chain_of_thought_prompt(task, steps)

        assert "Task: Solve math problem" in result
        assert "step-by-step" in result
        assert "1. Understand the problem" in result
        assert "2. Break it down" in result

    def test_create_structured_output_prompt(self):
        """Test creating structured output prompt."""
        task = "Analyze text"
        output_format = {"sentiment": "positive/negative", "score": "0-1"}

        result = PromptOptimizer.create_structured_output_prompt(task, output_format)

        assert "Analyze text" in result
        assert "sentiment" in result
        assert "score" in result
        assert "format" in result.lower()

    def test_optimize_for_cost_compress(self):
        """Test cost optimization with compress strategy."""
        prompt = "  Line 1  \n\n  Line 2  \n  "
        result = PromptOptimizer.optimize_for_cost(prompt, strategy="compress")

        assert "Line 1" in result
        assert "Line 2" in result
        assert len(result) < len(prompt)

    def test_optimize_for_cost_simplify(self):
        """Test cost optimization with simplify strategy."""
        prompt = "Please note that you should make sure to complete the task"
        result = PromptOptimizer.optimize_for_cost(prompt, strategy="simplify")

        assert "please note that" not in result
        assert "make sure to" not in result

    def test_validate_prompt_quality_high(self):
        """Test validating high quality prompt."""
        prompt = "Task: Complete this. Example: input -> output. Format: JSON"
        result = PromptOptimizer.validate_prompt_quality(prompt)

        assert result["has_clear_task"] is True
        assert result["has_examples"] is True
        assert result["has_format"] is True
        assert result["quality_score"] == 1.0

    def test_validate_prompt_quality_low(self):
        """Test validating low quality prompt."""
        prompt = "Do something"
        result = PromptOptimizer.validate_prompt_quality(prompt)

        assert result["quality_score"] < 1.0

    def test_validate_prompt_quality_metrics(self):
        """Test prompt quality metrics."""
        prompt = "Test prompt"
        result = PromptOptimizer.validate_prompt_quality(prompt)

        assert "length" in result
        assert "estimated_tokens" in result
        assert "quality_score" in result
        assert result["length"] == len(prompt)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
