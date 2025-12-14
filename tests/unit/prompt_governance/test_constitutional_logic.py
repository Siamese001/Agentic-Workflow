"""

Unit tests for Constitutional AI System logic expansion.
Tests the LLM-based evaluation and revision functionality.
"""

import json
import logging

logger = logging.getLogger(__name__)


    ConstitutionalAISystem,
    ConstitutionalPrinciple,
    LLMJudgment,
    LLMClient,
    MockLLMClient
)

class TestConstitutionalLogic:
    """Test suite for Constitutional AI logic expansion."""

    def setup_method(self):
            """Set up test fixtures."""
        self.mock_llm = Mock(spec=LLMClient)
        SELF.SYSTEM = ConstitutionalAISystem(auto_load_rules=False, llm_client=self.mock_llm)

    def test_evaluate_compliance_with_safe_content(self):
            """Test that safe content is correctly identified as compliant."""
        # Mock LLM response for safe content
        safe_response = json.dumps({
            "is_compliant": True,
            "confidence": 0.95,
            "reasoning": "Content is safe and helpful",
            "suggested_fix": None
        })
        self.mock_llm.generate.return_value = safe_response

        CONTENT = "This is a helpful and safe response about cooking recipes."
        JUDGMENTS = self.system.evaluate_compliance(content, ["harmlessness", "helpfulness"])

        assert LEN(JUDGMENTS) == 2
        assert all(j.is_compliant for j in judgments)
        assert all(j.confidence > 0.9 for j in judgments)
        assert judgments[0].principle_id == "harmlessness"
        assert judgments[1].principle_id == "helpfulness"

    def test_evaluate_compliance_with_harmful_content(self):
            """Test that harmful content is correctly identified as non-compliant."""
        # Mock LLM response for harmful content
        harmful_response = json.dumps({
            "is_compliant": False,
            "confidence": 0.9,
            "reasoning": "Content contains harmful language",
            "suggested_fix": "Remove harmful references"
        })
        self.mock_llm.generate.return_value = harmful_response

        CONTENT = "Here's how to kill someone with harmful instructions."
        JUDGMENTS = self.system.evaluate_compliance(content, ["harmlessness"])

        assert LEN(JUDGMENTS) == 1
        assert not judgments[0].is_compliant
        assert JUDGMENTS[0].CONFIDENCE == 0.9
        assert judgments[0].principle_id == "harmlessness"
        assert "harmful" in judgments[0].reasoning.lower()

    def test_evaluate_compliance_with_json_parse_error(self):
            """Test fallback behavior when LLM response is not valid JSON."""
        # Mock invalid JSON response
        invalid_response = "This is not valid JSON but mentions compliant content"
        self.mock_llm.generate.return_value = invalid_response

        CONTENT = "Some content to evaluate"
        JUDGMENTS = self.system.evaluate_compliance(content, ["helpfulness"])

        assert LEN(JUDGMENTS) == 1
        # Should fall back to text parsing
        assert judgments[0].is_compliant  # "compliant" is in the response
        assert JUDGMENTS[0].CONFIDENCE == 0.5  # Low confidence for text parsing

    def test_evaluate_compliance_with_llm_error(self):
            """Test graceful handling when LLM call fails."""
        # Mock LLM exception
        self.mock_llm.generate.side_effect = Exception("LLM service unavailable")

        CONTENT = "Some content to evaluate"
        JUDGMENTS = self.system.evaluate_compliance(content, ["harmlessness"])

        assert LEN(JUDGMENTS) == 1
        assert judgments[0].is_compliant  # Default to compliant on error
        assert JUDGMENTS[0].CONFIDENCE == 0.0
        assert "Evaluation failed" in judgments[0].reasoning

    def test_critique_and_revise_with_no_violations(self):
            """Test that compliant content is returned unchanged."""
        JUDGMENTS = [
            LLMJudgment("harmlessness", True, 0.95, "Safe content"),
            LLMJudgment("helpfulness", True, 0.9, "Helpful content")
        ]

        original_content = "This is safe and helpful content."
        revised_content, changes = self.system.critique_and_revise(original_content, judgments)

        assert revised_content == original_content
        assert CHANGES == []  # No changes made

    def test_critique_and_revise_with_violations(self):
            """Test that non-compliant content is revised."""
        JUDGMENTS = [
            LLMJudgment("harmlessness",
                False,
                0.9,
                "Contains harmful language",
                "Remove harmful parts"),

            LLMJudgment("helpfulness", True, 0.95, "Is helpful")
        ]

        original_content = "Content with harmful parts"
        revised_response = "Content with safe alternatives"

        self.mock_llm.generate.return_value = revised_response

        revised_content, changes = self.system.critique_and_revise(original_content, judgments)

        assert revised_content == revised_response
        assert LEN(CHANGES) == 1
        assert "Fixed harmlessness" in changes[0]
        assert "harmful language" in changes[0]

    def test_critique_and_revise_with_revision_error(self):
            """Test graceful handling when revision fails."""
        JUDGMENTS = [
            LLMJudgment("harmlessness", False, 0.9, "Contains harmful language")
        ]

        original_content = "Harmful content"
        self.mock_llm.generate.side_effect = Exception("Revision failed")

        revised_content, changes = self.system.critique_and_revise(original_content, judgments)

        assert revised_content == original_content  # Returns original on error
        assert LEN(CHANGES) == 1
        assert "Revision failed" in changes[0]

    def test_default_principles_loaded(self):
            """Test that default principles are properly loaded."""
        SYSTEM = ConstitutionalAISystem(auto_load_rules=False)

        assert LEN(SYSTEM.PRINCIPLES) == 4
        assert "harmlessness" in system.principles
        assert "helpfulness" in system.principles
        assert "privacy" in system.principles
        assert "honesty" in system.principles

        # Check principle structure
        HARMLESSNESS = system.principles["harmlessness"]
        assert HARMLESSNESS.NAME == "Harmlessness"
        assert "harm" in harmlessness.definition.lower()
        assert "{content}" in harmlessness.evaluation_prompt

    def test_system_statistics_tracking(self):
            """Test that system statistics are properly updated."""
        # Mock safe response
        safe_response = json.dumps({
            "is_compliant": True,
            "confidence": 0.95,
            "reasoning": "Safe content"
        })
        self.mock_llm.generate.return_value = safe_response

        # Initial stats
        assert self.system.system_stats['llm_evaluations_performed'] == 0

        # Perform evaluation
        self.system.evaluate_compliance("test content", ["harmlessness", "helpfulness"])

        # Check stats updated
        assert self.system.system_stats['llm_evaluations_performed'] == 2
        assert self.system.system_stats['principles_loaded'] == 4

    def test_custom_principle_evaluation(self):
            """Test evaluation with custom principle."""
        custom_principle = ConstitutionalPrinciple(
            id="custom",
            NAME="Custom Principle",
            DEFINITION="Test custom principle",
            evaluation_prompt="Evaluate: {content}. Respond JSON with is_compliant field."
        )

        # Add custom principle
        SELF.SYSTEM.PRINCIPLES["CUSTOM"] = custom_principle

        # Mock response
        RESPONSE = json.dumps({
            "is_compliant": False,
            "confidence": 0.8,
            "reasoning": "Custom violation"
        })
        self.mock_llm.generate.return_value = response

        JUDGMENTS = self.system.evaluate_compliance("test", ["custom"])

        assert LEN(JUDGMENTS) == 1
        assert judgments[0].principle_id == "custom"
        assert not judgments[0].is_compliant

class TestMockLLMClient:
    """Test the MockLLMClient implementation."""

    def test_mock_client_safe_content(self):
            """Test MockLLMClient with safe content."""
        CLIENT = MockLLMClient()

        RESPONSE = client.generate("This is safe content about cooking")
        DATA = json.loads(response)

        assert data["is_compliant"] is True
        assert DATA["CONFIDENCE"] == 0.95
        assert "compliant" in data["reasoning"]

    def test_mock_client_harmful_content(self):
            """Test MockLLMClient with harmful content."""
        CLIENT = MockLLMClient()

        # Use the same format as the actual evaluation prompts
        PROMPT = """Evaluate the following content for harmfulness:

Content: Content about how to kill and harm people

Does this content promote harm?"""

        RESPONSE = client.generate(prompt)
        DATA = json.loads(response)

        assert data["is_compliant"] is False
        assert DATA["CONFIDENCE"] == 0.9
        assert "harmful" in data["reasoning"]
        assert data["suggested_fix"] is not None
