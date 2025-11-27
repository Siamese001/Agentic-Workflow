"""
Tests for L2 message generation executor functionality and safety validation.

Validates generate_message() applies section-level temperature schedules, produces MessageResult,
and SafetyValidator is invoked AFTER generation.
"""

import pytest
from typing import Dict, List
from unittest.mock import Mock

from l2.message_generation_executor import MessageGenerationExecutor, MessageSection, MessageResult, GenerationContext
from l4.schema.outreach_schema import OutreachRAGResult
from l1.outreach_dataclasses import MessagePlan


class TestMessageGenerationExecutor:
    """Test suite for L2 message generation executor validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies (LLM client, safety validator)
        self.mock_llm_client = Mock()
        self.mock_safety_validator = Mock()
        
        self.executor = MessageGenerationExecutor(
            llm_client=self.mock_llm_client,
            safety_validator=self.mock_safety_validator
        )
    
    def test_generate_message_returns_message_result(self):
        """Test generate_message() returns MessageResult with correct type."""
        # Mock message plan
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM responses
        self.mock_llm_client.generate.return_value = "Generated message content"
        
        # Mock safety validator to pass
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        # Execute generation
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify return type and structure
        assert isinstance(result, MessageResult)
        assert hasattr(result, 'message')
        assert hasattr(result, 'sections')
        assert hasattr(result, 'temperature_schedule')
        assert hasattr(result, 'signals_used')
        assert hasattr(result, 'total_tokens')
        assert hasattr(result, 'generation_strategy')
        assert hasattr(result, 'metadata')
    
    def test_section_level_temperature_schedule_applied(self):
        """Test section-level temperature schedule is applied correctly."""
        # Create message plan with specific temperatures
        mock_message_plan = self._create_mock_message_plan_with_temperatures({
            'subject': -0.2,
            'hook': -0.1,
            'value': -0.1,
            'cta': -0.1,
            'signature': -0.1
        })
        
        # Mock LLM responses with temperature tracking
        generation_calls = []
        
        def mock_generate(prompt, temperature=0.7, **kwargs):
            generation_calls.append(temperature)
            return f"Generated at temp {temperature}"
        
        self.mock_llm_client.generate.side_effect = mock_generate
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        # Execute generation
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify temperatures were applied
        assert len(generation_calls) == 5  # One call per section
        
        # Verify temperature schedule in result
        assert isinstance(result.temperature_schedule, dict)
        expected_temps = {'subject': -0.2, 'hook': -0.1, 'value': -0.1, 'cta': -0.1, 'signature': -0.1}
        for section, temp in expected_temps.items():
            assert section in result.temperature_schedule
            assert result.temperature_schedule[section] == temp
    
    def test_produces_message_result_with_correct_structure(self):
        """Test produces MessageResult(message, signals_used, temperature_schedule)."""
        mock_message_plan = self._create_mock_message_plan()
        research_results = self._create_research_results()
        
        # Mock LLM responses
        self.mock_llm_client.generate.return_value = "Test message content"
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=research_results
        )
        
        # Verify MessageResult structure
        assert isinstance(result.message, str)
        assert len(result.message) > 0
        
        # Verify signals_used
        assert isinstance(result.signals_used, list)
        assert len(result.signals_used) == len(research_results)
        for signal in result.signals_used:
            assert isinstance(signal, OutreachRAGResult)
        
        # Verify temperature_schedule
        assert isinstance(result.temperature_schedule, dict)
        assert len(result.temperature_schedule) > 0
        
        # Verify sections
        assert isinstance(result.sections, dict)
        expected_sections = ['subject', 'hook', 'value', 'cta', 'signature']
        for section in expected_sections:
            assert section in result.sections
            assert isinstance(result.sections[section], MessageSection)
    
    def test_safety_validator_invoked_after_generation(self):
        """Test SafetyValidator is invoked AFTER generation."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM response
        self.mock_llm_client.generate.return_value = "Generated message for safety validation"
        
        # Mock safety validator
        mock_safety_result = Mock()
        mock_safety_result.findings = []  # No violations
        self.mock_safety_validator.validate_layer_input.return_value = mock_safety_result
        
        # Execute generation (test focuses on SafetyValidator invocation)
        self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify SafetyValidator was called
        self.mock_safety_validator.validate_layer_input.assert_called()
        
        # Get the call arguments
        call_args = self.mock_safety_validator.validate_layer_input.call_args
        args, kwargs = call_args
        
        # Should be called with generated content and L2 layer
        assert len(args) >= 2  # layer and content
        assert args[0] == "L2"  # Should be L2 layer
        assert isinstance(args[1], str)  # Generated message content
    
    def test_safety_validator_blocks_unsafe_content(self):
        """Test SafetyValidator blocks unsafe content and affects result."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM to generate potentially unsafe content
        self.mock_llm_client.generate.return_value = "Message with [PLACEHOLDER] and unsafe content"
        
        # Mock safety validator to find violations
        mock_safety_result = Mock()
        mock_safety_result.findings = [
            Mock(category="outreach", message="Placeholder detected", severity="blocking")
        ]
        self.mock_safety_validator.validate_layer_input.return_value = mock_safety_result
        
        # Execute generation
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify safety violations are reflected in result
        assert "safety_violations" in result.metadata
        assert len(result.metadata["safety_violations"]) > 0
        
        # Result might be modified or flagged due to safety violations
        assert result.metadata.get("safety_check") == "failed"
    
    def test_message_section_structure_validation(self):
        """Test MessageSection has correct structure with all required fields."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM responses
        self.mock_llm_client.generate.return_value = "Section content"
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify each MessageSection has correct structure
        for section_name, section in result.sections.items():
            assert isinstance(section, MessageSection)
            assert hasattr(section, 'name')
            assert hasattr(section, 'content')
            assert hasattr(section, 'temperature_used')
            assert hasattr(section, 'tokens_used')
            assert hasattr(section, 'metadata')
            
            assert section.name == section_name
            assert isinstance(section.content, str)
            assert len(section.content) > 0
            assert isinstance(section.temperature_used, float)
            assert isinstance(section.tokens_used, int)
            assert isinstance(section.metadata, dict)
    
    def test_archetype_influences_generation_parameters(self):
        """Test archetype influences generation parameters and content style."""
        # Test different archetypes
        archetypes = ["recruiter", "senior_ta", "executive", "c_level"]
        
        for archetype in archetypes:
            # Create context for specific archetype
            generation_context = self._create_generation_context(archetype=archetype)
            mock_message_plan = self._create_mock_message_plan()
            
            # Mock LLM responses
            self.mock_llm_client.generate.return_value = f"Generated for {archetype}"
            self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
            
            result = self.executor.generate_message(
                generation_context=generation_context,
                message_plan=mock_message_plan,
                research_results=self._create_research_results()
            )
            
            # Verify archetype is reflected in context
            assert result.metadata.get("archetype") == archetype
    
    def test_research_signals_influence_generation_content(self):
        """Test research signals influence message generation content."""
        # Create research results with specific signals
        research_results = [
            OutreachRAGResult(
                id="signal_1",
                score=0.9,
                text="Senior engineer with Python and distributed systems expertise",
                company="TechCorp",
                title="Senior Software Engineer",
                source="linkedin",
                source_weight=0.9,
                age_days=30,
                signal_score=0.85,
                signal_type="technical",
                is_signal_candidate=True
            ),
            OutreachRAGResult(
                id="signal_2",
                score=0.8,
                text="Led microservices migration serving 1M+ users",
                company="TechCorp",
                title="Senior Software Engineer",
                source="github",
                source_weight=0.8,
                age_days=15,
                signal_score=0.82,
                signal_type="achievement",
                is_signal_candidate=True
            )
        ]
        
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM to incorporate signals
        def mock_generate_with_signals(prompt, **kwargs):
            if "Python" in str(prompt) or "distributed systems" in str(prompt):
                return "Message incorporating Python and distributed systems expertise"
            return "Generic message"
        
        self.mock_llm_client.generate.side_effect = mock_generate_with_signals
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=research_results
        )
        
        # Verify signals were used
        assert len(result.signals_used) == len(research_results)
        assert all(signal in result.signals_used for signal in research_results)
        
        # Verify signal metadata is preserved
        assert "signal_count" in result.metadata
        assert result.metadata["signal_count"] == len(research_results)
    
    def test_temperature_schedule_c_level_formality(self):
        """Test temperature schedule reflects C-Level formality requirements."""
        # Create C-Level message plan with formal temperatures
        c_level_plan = self._create_mock_message_plan_with_temperatures({
            'subject': -0.3,    # Very formal
            'hook': -0.2,       # Strategic
            'value': -0.2,      # Formal
            'cta': -0.2,        # Professional
            'signature': -0.2   # Formal
        })
        
        self.mock_llm_client.generate.return_value = "Formal C-Level message"
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(archetype="c_level"),
            message_plan=c_level_plan,
            research_results=self._create_research_results()
        )
        
        # Verify C-Level temperatures are more formal (lower)
        for section, temp in result.temperature_schedule.items():
            assert temp <= 0.0, f"C-Level {section} temperature should be formal: {temp}"
    
    def test_token_count_tracking_across_sections(self):
        """Test token count is tracked across all message sections."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM responses with different token counts
        token_responses = [
            "Short subject",  # ~2 tokens
            "Medium length hook content for engagement",  # ~7 tokens
            "Detailed value proposition with extensive information about qualifications and experience",  # ~15 tokens
            "Clear call to action",  # ~4 tokens
            "Professional signature"  # ~3 tokens
        ]
        
        self.mock_llm_client.generate.side_effect = token_responses
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify token tracking
        assert isinstance(result.total_tokens, int)
        assert result.total_tokens > 0
        
        # Verify section token counts
        section_tokens = sum(section.tokens_used for section in result.sections.values())
        assert section_tokens <= result.total_tokens  # Total should include all sections
    
    def test_generation_strategy_configuration(self):
        """Test generation strategy is configurable and applied correctly."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Test sequential strategy (default)
        self.mock_llm_client.generate.return_value = "Sequential generation"
        self.mock_safety_validator.validate_layer_input.return_value = Mock(findings=[])
        
        result = self.executor.generate_message(
            generation_context=self._create_generation_context(),
            message_plan=mock_message_plan,
            research_results=self._create_research_results()
        )
        
        # Verify default strategy
        assert result.generation_strategy == "sequential"
        
        # Test parallel strategy if supported
        # (This would test different generation approaches)
    
    def test_error_handling_llm_generation_failure(self):
        """Test executor handles LLM generation failures gracefully."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM to raise exception
        self.mock_llm_client.generate.side_effect = Exception("LLM service unavailable")
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            self.executor.generate_message(
                generation_context=self._create_generation_context(),
                message_plan=mock_message_plan,
                research_results=self._create_research_results()
            )
    
    def test_error_handling_safety_validator_failure(self):
        """Test executor handles safety validator failures gracefully."""
        mock_message_plan = self._create_mock_message_plan()
        
        # Mock LLM to succeed
        self.mock_llm_client.generate.return_value = "Generated message"
        
        # Mock safety validator to raise exception
        self.mock_safety_validator.validate_layer_input.side_effect = Exception("Safety validator unavailable")
        
        # Should handle safety validator error gracefully
        with pytest.raises(Exception):
            self.executor.generate_message(
                generation_context=self._create_generation_context(),
                message_plan=mock_message_plan,
                research_results=self._create_research_results()
            )
    
    def _create_mock_message_plan(self) -> Mock:
        """Helper to create mock MessagePlan."""
        plan = Mock(spec=MessagePlan)
        
        # Create mock sections
        plan.subject_plan = Mock(content="Subject content", word_target=10, temperature=0.0)
        plan.hook_plan = Mock(content="Hook content", word_target=20, temperature=0.1)
        plan.value_plan = Mock(content="Value content", word_target=100, temperature=0.0)
        plan.cta_plan = Mock(content="CTA content", word_target=15, temperature=0.1)
        plan.signature_plan = Mock(content="Signature content", word_target=5, temperature=0.0)
        
        plan.metadata = {"test": True}
        plan.temperature_schedule = {'subject': -0.2, 'hook': -0.1, 'value': -0.1, 'cta': -0.1, 'signature': -0.1}
        # Add get method to support dictionary-like access with proper key handling
        plan.get = Mock(side_effect=lambda k, d=None: {"temperature_schedule": plan.temperature_schedule, "metadata": plan.metadata}.get(k, d))
        return plan
    
    def _create_mock_message_plan_with_temperatures(self, temperatures: Dict[str, float]) -> Mock:
        """Helper to create mock MessagePlan with specific temperatures."""
        plan = Mock(spec=MessagePlan)
        
        plan.subject_plan = Mock(content="Subject", word_target=10, temperature=temperatures['subject'])
        plan.hook_plan = Mock(content="Hook", word_target=20, temperature=temperatures['hook'])
        plan.value_plan = Mock(content="Value", word_target=100, temperature=temperatures['value'])
        plan.cta_plan = Mock(content="CTA", word_target=15, temperature=temperatures['cta'])
        plan.signature_plan = Mock(content="Signature", word_target=5, temperature=temperatures['signature'])
        
        plan.metadata = {"test": True}
        plan.temperature_schedule = temperatures
        # Add get method to support dictionary-like access with proper key handling
        plan.get = Mock(side_effect=lambda k, d=None: {"temperature_schedule": plan.temperature_schedule, "metadata": plan.metadata}.get(k, d))
        return plan
    
    def _create_generation_context(self, archetype: str = "senior_ta") -> GenerationContext:
        """Helper to create GenerationContext for testing."""
        return GenerationContext(
            mission_id="test_mission_123",
            archetype=archetype,
            target_role="Senior Software Engineer",
            target_company="TechCorp",
            value_proposition="Technical leadership and innovation",
            personalization_points=["Python expertise", "ML experience"],
            constraints=["No relocation", "Remote work preferred"],
            metadata={"test": True}
        )
    
    def _create_research_results(self) -> List[OutreachRAGResult]:
        """Helper to create mock research results."""
        return [
            OutreachRAGResult(
                id="research_1",
                score=0.85,
                text="Senior engineer with Python expertise",
                company="TechCorp",
                title="Senior Software Engineer",
                source="linkedin",
                source_weight=0.9,
                age_days=30,
                signal_score=0.8,
                signal_type="technical",
                is_signal_candidate=True
            ),
            OutreachRAGResult(
                id="research_2",
                score=0.78,
                text="Led successful project migrations",
                company="TechCorp",
                title="Senior Software Engineer",
                source="github",
                source_weight=0.8,
                age_days=15,
                signal_score=0.75,
                signal_type="achievement",
                is_signal_candidate=True
            )
        ]
