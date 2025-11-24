"""Tests for Instructional Injection v6 Prompts and Many-Shot Examples

This module validates:
- v6 prompt structure and completeness
- Many-shot example quality
- Prompt integration with agents
- Layer and extension functionality
"""

import pytest
from prompts.instructional_injection_v6 import (
    InstructionalPrompt,
    InstructionalLayer,
    InstructionalExtension,
    LayerContent,
    ExtensionContent,
    create_l1_planner_prompt,
    create_l2_executor_prompt,
    add_rag_extension,
    add_cot_extension,
)
from prompts.many_shot_examples import (
    ExampleType,
    get_examples,
    format_examples_for_prompt,
    STRATEGY_PLANNING_EXAMPLES,
    RAG_PLANNING_EXAMPLES,
)
from prompts.v6_prompt_integration import (
    create_strategy_planner_prompt,
    create_rag_planner_prompt,
    create_qa_planner_prompt,
    create_safety_planner_prompt,
    create_strategy_executor_prompt,
    validate_v6_prompt,
)


class TestInstructionalInjectionV6:
    """Test v6 prompt structure and functionality."""
    
    def test_create_l1_planner_prompt(self):
        """Test L1 planner prompt creation."""
        prompt = create_l1_planner_prompt(
            agent_name="Test Planner",
            domain="testing",
            objective="Test objective",
        )
        
        assert prompt.agent_type == "planner"
        assert prompt.layer_type == "L1"
        assert InstructionalLayer.AGENT_IDENTITY in prompt.layers
        assert InstructionalLayer.ROLE_DEFINITION in prompt.layers
        assert InstructionalLayer.PRIMARY_OBJECTIVE in prompt.layers
        assert InstructionalLayer.OUTPUT_FORMAT in prompt.layers
    
    def test_create_l2_executor_prompt(self):
        """Test L2 executor prompt creation."""
        prompt = create_l2_executor_prompt(
            agent_name="Test Executor",
            domain="testing",
            capabilities=["execute", "validate"],
        )
        
        assert prompt.agent_type == "executor"
        assert prompt.layer_type == "L2"
        assert InstructionalLayer.AGENT_IDENTITY in prompt.layers
        assert InstructionalLayer.ERROR_RECOVERY in prompt.layers
    
    def test_add_rag_extension(self):
        """Test RAG extension addition."""
        prompt = create_l1_planner_prompt("Test", "test", "test")
        add_rag_extension(prompt, {"top_k": 5, "score_threshold": 0.8})
        
        assert InstructionalExtension.RAG_INTEGRATION in prompt.extensions
        ext = prompt.extensions[InstructionalExtension.RAG_INTEGRATION]
        assert ext.enabled
        assert "top_k" in ext.metadata
    
    def test_add_cot_extension(self):
        """Test Chain-of-Thought extension addition."""
        prompt = create_l1_planner_prompt("Test", "test", "test")
        add_cot_extension(prompt)
        
        assert InstructionalExtension.CHAIN_OF_THOUGHT in prompt.extensions
        ext = prompt.extensions[InstructionalExtension.CHAIN_OF_THOUGHT]
        assert ext.enabled
        assert "step-by-step" in ext.content.lower()
    
    def test_prompt_render(self):
        """Test prompt rendering."""
        prompt = create_l1_planner_prompt("Test", "test", "test")
        rendered = prompt.render()
        
        assert "AGENT IDENTITY" in rendered
        assert "ROLE DEFINITION" in rendered
        assert "PRIMARY OBJECTIVE" in rendered
        assert "OUTPUT FORMAT" in rendered
    
    def test_prompt_validation(self):
        """Test prompt validation."""
        # Valid prompt
        prompt = create_l1_planner_prompt("Test", "test", "test")
        issues = prompt.validate()
        assert len(issues) == 0
        
        # Invalid prompt (missing required layer)
        invalid_prompt = InstructionalPrompt(
            prompt_id="invalid",
            agent_type="planner",
            layer_type="L1",
        )
        issues = invalid_prompt.validate()
        assert len(issues) > 0
        assert any("agent_identity" in issue.lower() for issue in issues)


class TestManyShotExamples:
    """Test many-shot example functionality."""
    
    def test_strategy_planning_examples(self):
        """Test strategy planning examples."""
        assert len(STRATEGY_PLANNING_EXAMPLES) >= 2
        
        for example in STRATEGY_PLANNING_EXAMPLES:
            assert example.example_type == ExampleType.L1_STRATEGY_PLANNING
            assert "job_title" in example.input_data
            assert "strategy_id" in example.expected_output
            assert 0.0 <= example.quality_score <= 1.0
    
    def test_rag_planning_examples(self):
        """Test RAG planning examples."""
        assert len(RAG_PLANNING_EXAMPLES) >= 2
        
        for example in RAG_PLANNING_EXAMPLES:
            assert example.example_type == ExampleType.L1_RAG_PLANNING
            assert "queries" in example.expected_output
            assert example.quality_score > 0.0
    
    def test_get_examples(self):
        """Test example retrieval."""
        examples = get_examples(
            example_type=ExampleType.L1_STRATEGY_PLANNING,
            max_examples=2,
            min_quality=0.9,
        )
        
        assert len(examples) <= 2
        assert all(ex.quality_score >= 0.9 for ex in examples)
        
        # Check sorting (descending quality)
        if len(examples) > 1:
            for i in range(len(examples) - 1):
                assert examples[i].quality_score >= examples[i + 1].quality_score
    
    def test_format_examples_for_prompt(self):
        """Test example formatting."""
        examples = get_examples(
            example_type=ExampleType.L1_STRATEGY_PLANNING,
            max_examples=1,
        )
        
        formatted = format_examples_for_prompt(examples)
        
        assert "## EXAMPLES" in formatted
        assert "**Input:**" in formatted
        assert "**Expected Output:**" in formatted
        assert "```json" in formatted


class TestV6PromptIntegration:
    """Test v6 prompt integration with agents."""
    
    def test_create_strategy_planner_prompt(self):
        """Test strategy planner prompt creation."""
        # Without examples
        prompt = create_strategy_planner_prompt(include_examples=False)
        assert "AGENT IDENTITY" in prompt
        assert "Strategy Planner" in prompt
        
        # With examples
        prompt_with_examples = create_strategy_planner_prompt(include_examples=True)
        assert "## EXAMPLES" in prompt_with_examples
        assert len(prompt_with_examples) > len(prompt)
    
    def test_create_rag_planner_prompt(self):
        """Test RAG planner prompt creation."""
        prompt = create_rag_planner_prompt(
            include_examples=True,
            rag_config={"top_k": 10, "score_threshold": 0.75},
        )
        
        assert "RAG Planner" in prompt
        assert "EXTENSIONS" in prompt
        assert "RAG INTEGRATION" in prompt
        assert "top_k" in prompt.lower() or "Top K" in prompt
    
    def test_create_qa_planner_prompt(self):
        """Test QA planner prompt creation."""
        prompt = create_qa_planner_prompt(include_examples=False)
        
        assert "QA Planner" in prompt
        assert "quality assurance" in prompt.lower()
    
    def test_create_safety_planner_prompt(self):
        """Test safety planner prompt creation."""
        prompt = create_safety_planner_prompt(include_examples=False)
        
        assert "Safety Planner" in prompt
        assert "SAFETY CONSTRAINTS" in prompt
        assert "ETHICAL GUIDELINES" in prompt
    
    def test_create_strategy_executor_prompt(self):
        """Test strategy executor prompt creation."""
        prompt = create_strategy_executor_prompt(include_examples=True)
        
        assert "Strategy Executor" in prompt
        assert "executor" in prompt.lower()
    
    def test_validate_v6_prompt_l1(self):
        """Test v6 prompt validation for L1."""
        prompt = create_l1_planner_prompt("Test", "test", "test")
        
        # Add required layers for L1
        prompt.add_layer(LayerContent(
            layer=InstructionalLayer.REASONING_MODE,
            content="analytical",
        ))
        prompt.add_layer(LayerContent(
            layer=InstructionalLayer.DOMAIN_KNOWLEDGE,
            content="test knowledge",
        ))
        
        issues = validate_v6_prompt(prompt)
        assert len(issues) == 0
    
    def test_validate_v6_prompt_l2(self):
        """Test v6 prompt validation for L2."""
        prompt = create_l2_executor_prompt("Test", "test", ["execute"])
        
        # L2 already has ERROR_RECOVERY, add PROCEDURAL_MEMORY
        prompt.add_layer(LayerContent(
            layer=InstructionalLayer.PROCEDURAL_MEMORY,
            content="test procedure",
        ))
        
        issues = validate_v6_prompt(prompt)
        assert len(issues) == 0


class TestPromptQuality:
    """Test prompt quality and completeness."""
    
    def test_all_l1_prompts_have_required_layers(self):
        """Test that all L1 prompts have required layers."""
        prompts = [
            create_strategy_planner_prompt(include_examples=False, enable_cot=False),
            create_rag_planner_prompt(include_examples=False),
            create_qa_planner_prompt(include_examples=False),
            create_safety_planner_prompt(include_examples=False),
        ]
        
        for prompt_str in prompts:
            assert "AGENT IDENTITY" in prompt_str
            assert "ROLE DEFINITION" in prompt_str
            assert "PRIMARY OBJECTIVE" in prompt_str
            assert "OUTPUT FORMAT" in prompt_str
    
    def test_examples_have_valid_structure(self):
        """Test that all examples have valid structure."""
        all_examples = (
            STRATEGY_PLANNING_EXAMPLES +
            RAG_PLANNING_EXAMPLES
        )
        
        for example in all_examples:
            assert example.example_id
            assert example.description
            assert isinstance(example.input_data, dict)
            assert isinstance(example.expected_output, dict)
            assert 0.0 <= example.quality_score <= 1.0
    
    def test_prompt_length_reasonable(self):
        """Test that prompts are not too short or too long."""
        prompt = create_strategy_planner_prompt(include_examples=True)
        
        # Should be substantial but not excessive
        assert 1000 < len(prompt) < 50000
    
    def test_extensions_are_optional(self):
        """Test that extensions can be disabled."""
        # Create prompt without CoT
        prompt_no_cot = create_strategy_planner_prompt(
            include_examples=False,
            enable_cot=False,
        )
        
        # Create prompt with CoT
        prompt_with_cot = create_strategy_planner_prompt(
            include_examples=False,
            enable_cot=True,
        )
        
        assert "CHAIN OF THOUGHT" not in prompt_no_cot
        assert "CHAIN OF THOUGHT" in prompt_with_cot


if __name__ == "__main__":
    pytest.main([__file__, "-v"])






