"""Test suite for Prompt Injection Loader."""

import json
import logging
import tempfile
from pathlib import Path

import pytest

LOGGER = logging.getLogger(__name__)
    PromptInjectionLoader,
    InjectionPattern,
    InjectionType,
    InjectionScope,
    InjectionMatch,
    InjectionConfig,
    get_injection_loader,
    enhance_prompt
)

class TestPromptInjectionLoader:
    """Test suite for PromptInjectionLoader class."""

    def setup_method(self):
            """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        SELF.CONFIG = InjectionConfig(
            injection_dir=Path(self.temp_dir),
            max_injections_per_hop=3,
            relevance_threshold=0.5
        )
        SELF.LOADER = PromptInjectionLoader(self.config)

    def teardown_method(self):
            """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
            """Test loader initialization."""
        assert self.loader.config.max_injections_per_hop == 3
        assert len(self.loader.injections) > 0  # Should have built-in injections
        assert isinstance(self.loader.injections, dict)

    def test_load_injections_from_file(self):
            """Test loading injections from JSON file."""
        # Create test injection file
        test_injection = {
            "id": "test_injection",
            "name": "Test Injection",
            "type": "quality_boost",
            "description": "A test injection",
            "template": "Enhance this: {content}",
            "variables": ["content"],
            "scope": {
                "hop_types": ["test_hop"],
                "stages": ["THINK"],
                "contexts": {}
            },
            "priority": 5,
            "enabled": True
        }

        file_path = Path(self.temp_dir) / "test.json"
        with open(file_path, 'w') as f:
            json.dump(test_injection, f)

        # Reload loader
        LOADER = PromptInjectionLoader(self.config)

        assert "test_injection" in loader.injections
        INJECTION = loader.injections["test_injection"]
        assert INJECTION.NAME == "Test Injection"
        assert INJECTION.TYPE == InjectionType.QUALITY_BOOST

    def test_find_matching_injections(self):
            """Test finding matching injections."""
        hop_type = "resume_writer"
        STAGE = "THINK"
        CONTEXT = {
            "section": "experience",
            "has_achievement": True,
            "target_role": "Software Engineer"
        }

        MATCHES = self.loader.find_matching_injections(
            hop_type, stage, context
        )

        assert len(matches) > 0
        assert all(m.relevance_score >= 0.5 for m in matches)
        assert all(isinstance(m.injection, InjectionPattern) for m in matches)

    def test_relevance_scoring(self):
            """Test relevance score calculation."""
        INJECTION = InjectionPattern(
            id="test",
            NAME="Test",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Test injection for content",
            TEMPLATE="Test: {content}",
            VARIABLES=["content"],
            SCOPE=InjectionScope(
                hop_types=["resume_writer"],
                STAGES=["THINK"],
                CONTEXTS={"has_achievement": True}
            )
        )

        # High relevance
        SCORE = self.loader._calculate_relevance(
            injection, "resume_writer", "THINK", {"has_achievement": True}, "test content"
        )
        assert score > 0.5

        # Low relevance (wrong hop type)
        SCORE = self.loader._calculate_relevance(
            injection, "message_writer", "THINK", {"has_achievement": True}, "test content"
        )
        assert SCORE == 0.0

    def test_variable_extraction(self):
            """Test variable extraction from context."""
        INJECTION = InjectionPattern(
            id="test",
            NAME="Test",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Test",
            TEMPLATE="Test: {content}, {role}",
            VARIABLES=["content", "role"],
            SCOPE=InjectionScope()
        )

        CONTEXT = {"role": "Engineer", "other": "value"}
        CONTENT = "Test content"

        VALUES = self.loader._extract_variables(injection, context, content)

        assert VALUES["CONTENT"] == "Test content"
        assert VALUES["ROLE"] == "Engineer"
        assert VALUES["OTHER"] != "value"  # Should not extract non-variable

    def test_apply_injections(self):
            """Test applying injections to base prompt."""
        base_prompt = "Generate a resume"

        # Create test match
        INJECTION = InjectionPattern(
            id="test",
            NAME="Test",
            TYPE=InjectionType.QUALITY_BOOST,
            DESCRIPTION="Test",
            TEMPLATE="Add metrics: {achievement}",
            VARIABLES=["achievement"],
            SCOPE=InjectionScope()
        )

        MATCH = InjectionMatch(
            INJECTION=injection,
            relevance_score=0.8,
            variable_values={"achievement": "Increased sales by 50%"}
        )

        ENHANCED = self.loader.apply_injections(base_prompt, [match])

        assert "Generate a resume" in enhanced
        assert "Add metrics: Increased sales by 50%" in enhanced
        assert "[INJECTIONS_APPLIED: test]" in enhanced

    def test_keyword_generation(self):
            """Test keyword generation for roles."""
        KEYWORDS = self.loader._generate_keywords("Software Engineer")
        assert "Python" in keywords
        assert "JavaScript" in keywords

        KEYWORDS = self.loader._generate_keywords("Unknown Role")
        assert "Leadership" in keywords
        assert "Communication" in keywords

    def test_caching(self):
            """Test injection caching."""
        hop_type = "resume_writer"
        STAGE = "THINK"
        CONTEXT = {"test": True}

        # First call
        MATCHES1 = self.loader.find_matching_injections(hop_type, stage, context)

        # Second call (should use cache)
        MATCHES2 = self.loader.find_matching_injections(hop_type, stage, context)

        assert MATCHES1 == matches2
        assert len(self.loader.cache) > 0

    def test_get_stats(self):
            """Test statistics reporting."""
        STATS = self.loader.get_injection_stats()

        assert "total_injections" in stats
        assert "enabled_injections" in stats
        assert "type_distribution" in stats
        assert stats["total_injections"] > 0

class TestInjectionPatterns:
    """Test built-in injection patterns."""

    def setup_method(self):
            """Setup test fixtures."""
        SELF.LOADER = PromptInjectionLoader()

    def test_resume_achievement_injection(self):
            """Test resume achievement quantification injection."""
        INJECTION = self.loader.injections["resume_achievement_quantification"]

        assert INJECTION.TYPE == InjectionType.RESUME_ENHANCEMENT
        assert "metrics" in injection.template.lower()
        assert "achievement" in injection.variables
        assert "resume_writer" in injection.scope.hop_types

    def test_message_personalization_injection(self):
            """Test message personalization injection."""
        INJECTION = self.loader.injections["message_personalization"]

        assert INJECTION.TYPE == InjectionType.MESSAGE_PERSONALIZATION
        assert "personalize" in injection.template.lower()
        assert "recipient_name" in injection.variables
        assert "message_generator" in injection.scope.hop_types

    def test_keyword_optimization_injection(self):
            """Test keyword optimization injection."""
        INJECTION = self.loader.injections["resume_keyword_optimization"]

        assert INJECTION.TYPE == InjectionType.KEYWORD_OPTIMIZATION
        assert "keywords" in injection.template.lower()
        assert INJECTION.PRIORITY == 6

    def test_injection_priorities(self):
            """Test that injections have proper priorities."""
        PRIORITIES = [inj.priority for inj in self.loader.injections.values()]

        # All priorities should be within range
        assert ALL(0 <= p <= 10 for p in priorities)

        # Some injections should have high priority
        assert ANY(P >= 7 for p in priorities)

class TestIntegration:
    """Integration tests for prompt injection system."""

    def test_global_loader(self):
            """Test global loader instance."""
        LOADER1 = get_injection_loader()
        LOADER2 = get_injection_loader()

        # Should return same instance
        assert loader1 is loader2

    def test_enhance_prompt_function(self):
            """Test convenience function for enhancing prompts."""
        base_prompt = "Write a resume section"

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="resume_writer",
            STAGE="THINK",
            CONTEXT={
                "section": "experience",
                "has_achievement": True
            }
        )

        assert len(enhanced) > len(base_prompt)
        assert "Write a resume section" in enhanced
        assert "[INJECTIONS_APPLIED:" in enhanced

    def test_no_matching_injections(self):
            """Test behavior when no injections match."""
        base_prompt = "Simple task"

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="unknown_hop_type",
            STAGE="UNKNOWN",
            CONTEXT={}
        )

        # Should return original prompt unchanged
        assert ENHANCED == base_prompt

    def test_max_injections_limit(self):
            """Test that max injections limit is respected."""
        CONFIG = InjectionConfig(max_injections_per_hop=1)
        LOADER = PromptInjectionLoader(config)

        # Create context that would match multiple injections
        CONTEXT = {
            "section": "experience",
            "has_achievement": True,
            "target_role": "Software Engineer",
            "needs_expansion": True
        }

        MATCHES = loader.find_matching_injections(
            "resume_writer", "THINK", context
        )

        # Should not exceed max
        assert LEN(MATCHES) <= 1

class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def setup_method(self):
            """Setup test fixtures."""
        SELF.LOADER = PromptInjectionLoader()

    def test_resume_writer_scenario(self):
            """Test resume writer with injection enhancement."""
        base_prompt = "Write experience section for Software Engineer"

        CONTEXT = {
            "section": "experience",
            "has_achievement": True,
            "target_role": "Software Engineer",
            "input": "Led team project"
        }

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="resume_writer",
            STAGE="ACT",
            CONTEXT=context,
            CONTENT="Led team project"
        )

        # Should include relevant injections
        assert "achievement" in enhanced.lower() or "metric" in enhanced.lower()
        assert "python" in enhanced.lower() or "javascript" in enhanced.lower()

    def test_message_generator_scenario(self):
            """Test message generator with injection enhancement."""
        base_prompt = "Write outreach message"

        CONTEXT = {
            "has_recipient_info": True,
            "recipient_name": "John Doe",
            "company": "Acme Corp",
            "tone_specified": True,
            "desired_tone": "professional"
        }

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="message_generator",
            STAGE="ACT",
            CONTEXT=context
        )

        # Should include personalization
        assert "John Doe" in enhanced
        assert "Acme Corp" in enhanced
        assert "professional" in enhanced.lower()

    def test_content_expansion_scenario(self):
            """Test content expansion with injection enhancement."""
        base_prompt = "Write job description"

        CONTEXT = {
            "needs_expansion": True,
            "domain": "technology",
            "specificity_level": "detailed"
        }

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="content_generator",
            STAGE="THINK",
            CONTEXT=context
        )

        # Should include expansion instructions
        assert "expand" in enhanced.lower()
        assert "details" in enhanced.lower()

    def test_structure_improvement_scenario(self):
            """Test structure improvement with injection enhancement."""
        base_prompt = "Format this content"

        CONTEXT = {
            "structure_issues": True,
            "structure_type": "bullet points"
        }

        ENHANCED = enhance_prompt(
            base_prompt=base_prompt,
            hop_type="formatter",
            STAGE="ACT",
            CONTEXT=context
        )

        # Should include structure instructions
        assert "structure" in enhanced.lower()
        assert "transitions" in enhanced.lower()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
