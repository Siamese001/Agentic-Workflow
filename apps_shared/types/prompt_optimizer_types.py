"""
Prompt Optimizer - Phase 5 Optimization
LLM prompt optimization utilities for high-reasoning agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PromptTemplate:
    """Structured prompt template."""

    system: str
    user: str
    variables: list[str]
    examples: list[dict[str, str]]
    metadata: dict[str, Any]


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization."""

    prompt: str
    token_count: int
    variables_used: dict[str, Any]
    optimization_applied: list[str]


class PromptOptimizer:
    """LLM prompt optimization utilities."""

    @staticmethod
    def create_template(
        system: str,
        user: str,
        variables: list[str] | None = None,
        examples: list[dict[str, str]] | None = None,
    ) -> PromptTemplate:
        """
        Create a structured prompt template.

        Args:
            system: System message
            user: User message template
            variables: List of variable names in template
            examples: Optional few-shot examples

        Returns:
            PromptTemplate instance
        """
        return PromptTemplate(
            system=system,
            user=user,
            variables=variables or [],
            examples=examples or [],
            metadata={},
        )

    @staticmethod
    def format_prompt(template: PromptTemplate, **kwargs: Any) -> OptimizedPrompt:
        """
        Format prompt template with variables.

        Args:
            template: PromptTemplate to format
            **kwargs: Variable values

        Returns:
            OptimizedPrompt with formatted prompt
        """
        optimizations = []
        user_prompt = template.user

        # Replace variables
        variables_used = {}
        for var in template.variables:
            if var in kwargs:
                value = kwargs[var]
                variables_used[var] = value
                user_prompt = user_prompt.replace(f"{{{var}}}", str(value))
            else:
                optimizations.append(f"Missing variable: {var}")

        # Add examples if provided
        if template.examples:
            examples_text = "\n\n".join(
                f"Example {i + 1}:\nInput: {ex.get('input', '')}\nOutput: {ex.get('output', '')}"
                for i, ex in enumerate(template.examples)
            )
            user_prompt = f"{examples_text}\n\n{user_prompt}"
            optimizations.append("Added few-shot examples")

        # Combine system and user
        full_prompt = f"{template.system}\n\n{user_prompt}"

        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        token_count = len(full_prompt) // 4

        return OptimizedPrompt(
            prompt=full_prompt,
            token_count=token_count,
            variables_used=variables_used,
            optimization_applied=optimizations,
        )

    @staticmethod
    # guardian: allow-magic-config
    def compress_prompt(prompt: str, max_tokens: int = 4000) -> str:
        """
        Compress prompt to fit within token limit.

        Args:
            prompt: Prompt to compress
            max_tokens: Maximum token limit

        Returns:
            Compressed prompt
        """
        # Rough token estimation
        estimated_tokens = len(prompt) // 4

        if estimated_tokens <= max_tokens:
            return prompt

        # Calculate target character count
        target_chars = max_tokens * 4

        # Simple truncation with ellipsis
        if len(prompt) > target_chars:
            return prompt[: target_chars - 10] + "\n...[truncated]"

        return prompt

    @staticmethod
    # guardian: allow-magic-config
    def add_context(prompt: str, context: dict[str, Any], max_context_items: int = 5) -> str:
        """
        Add context information to prompt.

        Args:
            prompt: Base prompt
            context: Context dictionary
            max_context_items: Maximum context items to include

        Returns:
            Prompt with context
        """
        if not context:
            return prompt

        context_items = list(context.items())[:max_context_items]
        context_text = "\n".join(f"- {key}: {value}" for key, value in context_items)

        return f"Context:\n{context_text}\n\n{prompt}"

    @staticmethod
    def create_chain_of_thought_prompt(task: str, steps: list[str]) -> str:
        """
        Create chain-of-thought prompt.

        Args:
            task: Task description
            steps: Reasoning steps

        Returns:
            Chain-of-thought prompt
        """
        steps_text = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps))

        return f"""Task: {task}

Let's approach this step-by-step:
{steps_text}

Please provide your reasoning for each step and then the final answer."""

    @staticmethod
    def create_structured_output_prompt(task: str, output_format: dict[str, str]) -> str:
        """
        Create prompt for structured output.

        Args:
            task: Task description
            output_format: Expected output format

        Returns:
            Structured output prompt
        """
        format_text = "\n".join(f"- {key}: {desc}" for key, desc in output_format.items())

        return f"""{task}

Please provide your response in the following format:
{format_text}"""

    @staticmethod
    def optimize_for_cost(prompt: str, strategy: str = "compress") -> str:
        """
        Optimize prompt for cost reduction.

        Args:
            prompt: Prompt to optimize
            strategy: Optimization strategy ('compress', 'simplify')

        Returns:
            Optimized prompt
        """
        if strategy == "compress":
            # Remove extra whitespace
            lines = [line.strip() for line in prompt.split("\n") if line.strip()]
            return "\n".join(lines)

        elif strategy == "simplify":
            # Remove redundant phrases
            redundant = [
                "please note that",
                "it is important to",
                "you should",
                "make sure to",
            ]
            optimized = prompt
            for phrase in redundant:
                optimized = optimized.replace(phrase, "")
            return optimized

        return prompt

    @staticmethod
    def validate_prompt_quality(prompt: str) -> dict[str, Any]:
        """
        Validate prompt quality.

        Args:
            prompt: Prompt to validate

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "length": len(prompt),
            "estimated_tokens": len(prompt) // 4,
            "has_clear_task": "task:" in prompt.lower() or "please" in prompt.lower(),
            "has_examples": "example" in prompt.lower(),
            "has_format": "format" in prompt.lower(),
            "quality_score": 0.0,
        }

        # Calculate quality score
        score = 0.0
        if metrics["has_clear_task"]:
            score += 0.4
        if metrics["has_examples"]:
            score += 0.3
        if metrics["has_format"]:
            score += 0.3

        metrics["quality_score"] = score

        return metrics
