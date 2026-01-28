import pytest
from pathlib import Path
import sys

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDeepHarvest:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Verifies that the Deep Harvest patterns correctly identify target content.
    """

    def test_weak_opening_detection(self):
        """Verify ProfileAnalysisAgent patterns catch weak language."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()

        weak_samples = [
            "I hope this finds you well.",
            "Just checking in on my previous email.",
            "I was wondering if you had time.",
            "I wanted to reach out about the opportunity.",
            "Perhaps we could discuss this further.",
            "If you're interested, I can share more details.",
        ]

        strong_samples = [
            "I have an idea for your team.",
            "Here is the strategy document.",
            "Our proposal for Q1 shows significant growth.",
            "The solution addresses your core challenges.",
            "My analysis reveals three key opportunities.",
            "We should connect to discuss the implementation.",
        ]

        # Test weak samples - all should be detected
        for sample in weak_samples:
            match = LegacyArtifacts.get_weak_opening_match(sample)
            assert match is not None, f"Failed to detect weak opening: {sample}"

        # Test strong samples - none should be detected
        for sample in strong_samples:
            match = LegacyArtifacts.get_weak_opening_match(sample)
            assert match is None, f"False positive on strong opening: {sample}"

    def test_placeholder_detection(self):
        """Verify OutreachValidationExecutor patterns catch unreplaced tags."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        dirty_samples = [
            "Hello [your name],",
            "I love [COMPANY] products.",
            "Please [INSERT ACTION] here.",
            "Contact us at {company} for details.",
            "This is a TODO item.",
            "The project is still TBD.",
            "Dear <NAME>,",
            "Welcome to <COMPANY>!",
        ]

        clean_samples = [
            "Hello John,",
            "I love Acme Corp products.",
            "Please sign here.",
            "Contact us at Google for details.",
            "This is a completed item.",
            "The project is scheduled for Q3.",
            "Dear Sarah,",
            "Welcome to Microsoft!",
        ]

        # Test dirty samples - all should be detected
        for sample in dirty_samples:
            match = LegacyArtifacts.get_placeholder_match(sample)
            assert match is not None, f"Failed to detect placeholder: {sample}"

        # Test clean samples - none should be detected
        for sample in clean_samples:
            match = LegacyArtifacts.get_placeholder_match(sample)
            assert match is None, f"False positive on clean text: {sample}"

    def test_cognitive_modes_availability(self):
        """Verify core_v107.py meta-prompts are accessible."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()

        # Check that all required modes exist
        required_modes = [
            "ADVERSARIAL",
            "SYNTHESIS",
            "ANALYTICAL",
            "ETHICAL",
            "SECURITY",
            "STRATEGY",
            "META",
            "NLI",
        ]

        for mode in required_modes:
            assert mode in artifacts.COGNITIVE_MODES, f"Missing cognitive mode: {mode}"

        # Verify specific content in key modes
        adversarial_template = artifacts.COGNITIVE_MODES["ADVERSARIAL"]
        assert "MODE: ADVERSARIAL" in adversarial_template
        assert "weaknesses" in adversarial_template

        security_template = artifacts.COGNITIVE_MODES["SECURITY"]
        assert "MODE: SECURITY" in security_template
        assert "prompt injection" in security_template

        synthesis_template = artifacts.COGNITIVE_MODES["SYNTHESIS"]
        assert "MODE: SYNTHESIS" in synthesis_template
        assert "synthesize" in synthesis_template

    def test_weak_opening_patterns_completeness(self):
        """Verify all weak opening patterns are properly compiled."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()
        patterns = artifacts.WEAK_OPENING_PATTERNS

        # Check that all expected patterns exist
        expected_patterns = [
            "i_hope",
            "just_checking",
            "just_wanted",
            "just_reaching",
            "just_following",
            "wondering",
            "connect",
            "perhaps",
            "if_interested",
        ]

        for pattern_name in expected_patterns:
            assert pattern_name in patterns, f"Missing weak opening pattern: {pattern_name}"
            assert patterns[pattern_name] is not None, f"Pattern {pattern_name} is None"

        # Test each pattern individually
        test_cases = {
            "i_hope": "I hope this email finds you well",
            "just_checking": "Just checking in on my previous email",
            "just_wanted": "Just wanted to follow up",
            "just_reaching": "Just reaching out about the opportunity",
            "just_following": "Just following up on our conversation",
            "wondering": "I was wondering if you had time",
            "connect": "I would like to connect with you",
            "perhaps": "Perhaps we could discuss this",
            "if_interested": "If you're interested, I can share more",
        }

        for pattern_name, test_text in test_cases.items():
            pattern = patterns[pattern_name]
            assert pattern.search(test_text), f"Pattern {pattern_name} failed to match: {test_text}"

    def test_placeholder_patterns_completeness(self):
        """Verify all placeholder patterns are properly compiled."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()
        patterns = artifacts.CRITICAL_PLACEHOLDERS

        # Check that all expected patterns exist
        expected_patterns = [
            "bracket_company",
            "curly_company",
            "bracket_name",
            "bracket_title",
            "bracket_insert",
            "generic_placeholder",
            "todo_placeholder",
            "angle_bracket_name",
            "angle_bracket_company",
        ]

        for pattern_name in expected_patterns:
            assert pattern_name in patterns, f"Missing placeholder pattern: {pattern_name}"
            assert patterns[pattern_name] is not None, f"Pattern {pattern_name} is None"

        # Test each pattern individually
        test_cases = {
            "bracket_company": "Welcome to [COMPANY]",
            "curly_company": "Contact us at {company}",
            "bracket_name": "Hello [your name]",
            "bracket_title": "Position: [TITLE]",
            "bracket_insert": "Please [INSERT DETAILS]",
            "generic_placeholder": "This is a [placeholder]",
            "todo_placeholder": "This needs TODO review",
            "angle_bracket_name": "Dear <NAME>",
            "angle_bracket_company": "Welcome to <COMPANY>",
        }

        for pattern_name, test_text in test_cases.items():
            pattern = patterns[pattern_name]
            assert pattern.search(test_text), f"Pattern {pattern_name} failed to match: {test_text}"

    def test_legacy_artifacts_class_structure(self):
        """Verify LegacyArtifacts class has proper structure."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()

        # Check that required attributes exist
        assert hasattr(artifacts, "WEAK_OPENING_PATTERNS")
        assert hasattr(artifacts, "CRITICAL_PLACEHOLDERS")
        assert hasattr(artifacts, "COGNITIVE_MODES")

        # Check that required methods exist
        assert hasattr(LegacyArtifacts, "get_weak_opening_match")
        assert hasattr(LegacyArtifacts, "get_placeholder_match")
        assert hasattr(LegacyArtifacts, "get_artifact")

        # Verify methods are callable
        assert callable(LegacyArtifacts.get_weak_opening_match)
        assert callable(LegacyArtifacts.get_placeholder_match)
        assert callable(LegacyArtifacts.get_artifact)

    def test_cognitive_modes_template_format(self):
        """Verify cognitive mode templates have proper format."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Create instance to access field defaults
        artifacts = LegacyArtifacts()

        for mode_name, template in artifacts.COGNITIVE_MODES.items():
            # Each template should contain the mode declaration
            assert f"MODE: {mode_name}" in template, (
                f"Template for {mode_name} missing mode declaration"
            )

            # Each template should contain at least one placeholder
            assert "{" in template and "}" in template, (
                f"Template for {mode_name} missing placeholders"
            )

            # Each template should be a string
            assert isinstance(template, str), f"Template for {mode_name} is not a string"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
