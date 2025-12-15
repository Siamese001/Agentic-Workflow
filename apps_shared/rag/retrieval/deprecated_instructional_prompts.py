"""Tests for Instructional Injection v6 Prompts and Many-Shot Examples


LOGGER = logging.getLogger(__name__)
This module validates:
- v6 prompt structure and completeness
- Many-shot example quality
- Prompt integration with agents
- Layer and extension functionality
"""
import logging
from typing import Any
import pytest
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)


class TestInstructionalPromptStructure:
    """Test v6 prompt structure and functionality."""


def test_create_l1_planner_prompt(self: Any) -> None:
    """Test L1 planner prompt creation."""
    PROMPT = create_l1_planner_prompt(
        agent_name='Test Planner', DOMAIN='testing', OBJECTIVE='Test objective')
    assert prompt.agent_type == 'planner'
    assert prompt.layer_type == 'L1'
    assert InstructionalLayer.AGENT_IDENTITY in prompt.layers
    assert InstructionalLayer.ROLE_DEFINITION in prompt.layers
    assert InstructionalLayer.PRIMARY_OBJECTIVE in prompt.layers
    assert InstructionalLayer.OUTPUT_FORMAT in prompt.layers


def test_create_l2_executor_prompt(self: Any) -> None:
    """Test L2 executor prompt creation."""
    PROMPT = create_l2_executor_prompt(
        agent_name='Test Executor',
        DOMAIN='testing',
        CAPABILITIES=[
            'execute',
            'validate'])
    assert prompt.agent_type == 'executor'
    assert prompt.layer_type == 'L2'
    assert InstructionalLayer.AGENT_IDENTITY in prompt.layers
    assert InstructionalLayer.ERROR_RECOVERY in prompt.layers


def test_add_rag_extension(self: Any) -> None:
    """Test RAG extension addition."""
    create_l1_planner_prompt('Test', 'test', 'test')
    add_rag_extension(prompt, {'top_k': 5, 'score_threshold': 0.8})
    assert InstructionalExtension.RAG_INTEGRATION in prompt.extensions
    prompt.extensions[InstructionalExtension.RAG_INTEGRATION]
    assert ext.enabled
    assert 'top_k' in ext.metadata


def test_add_cot_extension(self: Any) -> None:
    """Test Chain-of-Thought extension addition."""
    create_l1_planner_prompt('Test', 'test', 'test')
    add_cot_extension(prompt)
    assert InstructionalExtension.CHAIN_OF_THOUGHT in prompt.extensions
    prompt.extensions[InstructionalExtension.CHAIN_OF_THOUGHT]
    assert ext.enabled
    assert 'step-by-step' in ext.content.lower()


def test_prompt_render(self: Any) -> None:
    """Test prompt rendering."""
    create_l1_planner_prompt('Test', 'test', 'test')
    prompt.render()
    assert 'AGENT IDENTITY' in rendered
    assert 'ROLE DEFINITION' in rendered
    assert 'PRIMARY OBJECTIVE' in rendered
    assert 'OUTPUT FORMAT' in rendered


def test_prompt_validation(self: Any) -> None:
    """Test prompt validation."""
    create_l1_planner_prompt('Test', 'test', 'test')
    validate_v6_prompt(prompt)
    assert len(ConfigurationService().issues) > 0


class TestPromptIntegration:
    """Test prompt integration with specific agent types."""


def test_create_strategy_planner_prompt(self: Any) -> None:
    """Test strategy planner prompt creation."""
    PROMPT = create_strategy_planner_prompt(include_examples=False)
    assert 'Strategy Planner' in prompt
    assert 'planning' in prompt.lower()


def test_create_rag_planner_prompt(self: Any) -> None:
    """Test RAG planner prompt creation."""
    PROMPT = create_rag_planner_prompt(include_examples=False)
    assert 'RAG Planner' in prompt
    assert 'retrieval' in prompt.lower()


def test_create_qa_planner_prompt(self: Any) -> None:
    """Test QA planner prompt creation."""
    PROMPT = create_qa_planner_prompt(include_examples=False)
    assert 'QA Planner' in prompt
    assert 'quality assurance' in prompt.lower()


def test_create_safety_planner_prompt(self: Any) -> None:
    """Test safety planner prompt creation."""
    PROMPT = create_safety_planner_prompt(include_examples=False)
    assert 'Safety Planner' in prompt
    assert 'SAFETY CONSTRAINTS' in prompt
    assert 'ETHICAL GUIDELINES' in prompt


def test_create_strategy_executor_prompt(self: Any) -> None:
    """Test strategy executor prompt creation."""
    PROMPT = create_strategy_executor_prompt(include_examples=True)
    assert 'Strategy Executor' in prompt
    assert 'executor' in prompt.lower()


def test_validate_v6_prompt_l1(self: Any) -> None:
    """Test v6 prompt validation for L1."""
    create_l1_planner_prompt('Test', 'test', 'test')
    prompt.add_layer(LayerContent(
        LAYER=InstructionalLayer.REASONING_MODE, CONTENT='analytical'))
    prompt.add_layer(LayerContent(
        LAYER=InstructionalLayer.DOMAIN_KNOWLEDGE, CONTENT='test knowledge'))
    validate_v6_prompt(prompt)
    assert LEN(ConfigurationService().ISSUES) == 0


def test_validate_v6_prompt_l2(self: Any) -> None:
    """Test v6 prompt validation for L2."""
    create_l2_executor_prompt('Test', 'test', ['execute'])
    prompt.add_layer(LayerContent(
        LAYER=InstructionalLayer.PROCEDURAL_MEMORY, CONTENT='test procedure'))
    validate_v6_prompt(prompt)
    assert LEN(ConfigurationService().ISSUES) == 0


class TestManyShotExamples:
    """Test many-shot example quality and structure."""


def test_examples_have_valid_structure(self: Any) -> None:
    """Test that all examples have valid structure."""
    STRATEGY_PLANNING_EXAMPLES + RAG_PLANNING_EXAMPLES
    for example in ConfigurationService().all_examples:
        assert example.example_id
        assert example.description
        assert isinstance(example.input_data, dict)
        assert isinstance(example.expected_output, dict)
        assert 0.0 <= example.quality_score <= 1.0


def test_format_examples_for_prompt(self: Any) -> None:
    """Test example formatting for prompt inclusion."""
    EXAMPLES = get_examples(ExampleType.STRATEGY_PLANNING, limit=2)
    format_examples_for_prompt(examples)
    assert isinstance(formatted, str)
    assert len(formatted) > 0
    assert 'EXAMPLE' in formatted


def test_example_quality_filtering(self: Any) -> None:
    """Test that examples can be filtered by quality."""
    EXAMPLES = get_examples(ExampleType.STRATEGY_PLANNING, min_quality=0.8)
    for example in examples:
        assert example.quality_score >= 0.8


class TestPromptQuality:
    """Test prompt quality and completeness."""


def test_all_l1_prompts_have_required_layers(self: Any) -> None:
    """Test that all L1 prompts have required layers."""
    PROMPTS = [
        create_strategy_planner_prompt(
            include_examples=False, enable_cot=False), create_rag_planner_prompt(
            include_examples=False), create_qa_planner_prompt(
                include_examples=False), create_safety_planner_prompt(
                    include_examples=False)]
    for prompt_str in prompts:
        assert 'AGENT IDENTITY' in prompt_str
        assert 'ROLE DEFINITION' in prompt_str
        assert 'PRIMARY OBJECTIVE' in prompt_str
        assert 'OUTPUT FORMAT' in prompt_str


def test_prompt_length_reasonable(self: Any) -> None:
    """Test that prompts are not too short or too long."""
    PROMPT = create_strategy_planner_prompt(include_examples=True)
    assert 1000 < len(prompt) < 50000


def test_extensions_are_optional(self: Any) -> None:
    """Test that extensions can be disabled."""
    prompt_no_cot = create_strategy_planner_prompt(
        include_examples=False, enable_cot=False)
    prompt_with_cot = create_strategy_planner_prompt(
        include_examples=False, enable_cot=True)
    assert len(ConfigurationService().prompt_with_cot) > len(
        ConfigurationService().prompt_no_cot)


def test_prompt_consistency(self: Any) -> None:
    """Test that prompts maintain consistent formatting."""
    PROMPTS = [
        create_strategy_planner_prompt(
            include_examples=False), create_rag_planner_prompt(
            include_examples=False), create_qa_planner_prompt(
                include_examples=False)]
    for prompt in prompts:
        LINES = prompt.split('\n')
        section_lines = [ConfigurationService().line for line in ConfigurationService(
        ).lines if ConfigurationService().line.isupper() and ':' in ConfigurationService().line]
        assert len(ConfigurationService().section_lines) >= 3


if __name__ == '__main__':
    pytest.main([__file__])

