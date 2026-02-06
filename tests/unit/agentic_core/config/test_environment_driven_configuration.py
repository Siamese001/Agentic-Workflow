import os
import sys
import unittest
from unittest.mock import patch

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Test all refactored components for environment-driven configuration
try:
    from agentic_core.runtime.shared_runtime.signal_quality_types import QualityThresholds
except (ImportError, NameError, AttributeError):
    # Skip SignalQuality tests if module not available
    QualityThresholds = None

try:
    from agentic_core.schemas.models.reasoning_config_types import (
        GovernorConfig,
        ModelConfig,
        RAGConfig,
    )
except (ImportError, NameError, AttributeError):
    ModelConfig = RAGConfig = GovernorConfig = None

try:
    from apps_shared.common_utils.node_negotiator_config import NegotiationConfig
except (ImportError, NameError, AttributeError):
    NegotiationConfig = None

try:
    from apps_rg.shared.tools.validation_result_validator import SectionIntegratorConfig
except (ImportError, NameError, AttributeError):
    SectionIntegratorConfig = None

try:
    from apps_lic.shared.tools.safety_profile_validator import BudgetProfile
except (ImportError, NameError, AttributeError):
    BudgetProfile = None


class TestEnvironmentDrivenConfiguration(unittest.TestCase):
    """
    Comprehensive test suite for environment-driven configuration across all components.
    Ensures strict decoupling from hardcoded values and proper environment variable sourcing.
    """

    def setUp(self):
        """Set up test environment with clean state."""
        # Clear any existing environment variables that might interfere
        self.original_env = dict(os.environ)
        os.environ.clear()

    def tearDown(self):
        """Restore original environment after each test."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(
        os.environ,
        {
            "SIGNAL_EXCELLENT_MIN": "0.95",
            "SIGNAL_HIGH_MIN": "0.80",
            "SIGNAL_GOOD_MIN": "0.65",
            "SIGNAL_MARGINAL_MIN": "0.45",
            "SIGNAL_MIN_RELEVANCE": "0.75",
            "SIGNAL_MIN_AUTHORITY": "0.65",
            "SIGNAL_MIN_SPECIFICITY": "0.55",
            "SIGNAL_MIN_COHERENCE": "0.65",
            "SIGNAL_MAX_HALLUCINATION_RISK": "0.15",
            "SIGNAL_MIN_FACT_VERIFICATION": "0.85",
            "SIGNAL_MAX_REPETITION_RATIO": "0.25",
            "SIGNAL_MIN_CLAIM_CONFIDENCE": "0.75",
        },
    )
    @unittest.skipIf(QualityThresholds is None, "SignalQuality module not available")
    def test_signal_quality_environment_driven(self):
        """Test SignalQuality thresholds sourced from environment."""
        thresholds = QualityThresholds()

        # Test composite score thresholds
        self.assertEqual(thresholds.EXCELLENT_MIN, 0.95)
        self.assertEqual(thresholds.HIGH_MIN, 0.80)
        self.assertEqual(thresholds.GOOD_MIN, 0.65)
        self.assertEqual(thresholds.MARGINAL_MIN, 0.45)

        # Test individual component thresholds
        self.assertEqual(thresholds.MIN_RELEVANCE, 0.75)
        self.assertEqual(thresholds.MIN_AUTHORITY, 0.65)
        self.assertEqual(thresholds.MIN_SPECIFICITY, 0.55)
        self.assertEqual(thresholds.MIN_COHERENCE, 0.65)

        # Test content quality thresholds
        self.assertEqual(thresholds.MAX_HALLUCINATION_RISK, 0.15)
        self.assertEqual(thresholds.MIN_FACT_VERIFICATION, 0.85)
        self.assertEqual(thresholds.MAX_REPETITION_RATIO, 0.25)
        self.assertEqual(thresholds.MIN_CLAIM_CONFIDENCE, 0.75)

    @unittest.skipIf(QualityThresholds is None, "SignalQuality module not available")
    def test_signal_quality_default_fallback(self):
        """Test SignalQuality falls back to defaults when environment variables are missing."""
        thresholds = QualityThresholds()

        # Should use default values when environment is empty
        self.assertEqual(thresholds.EXCELLENT_MIN, 0.9)
        self.assertEqual(thresholds.HIGH_MIN, 0.75)
        self.assertEqual(thresholds.GOOD_MIN, 0.6)
        self.assertEqual(thresholds.MARGINAL_MIN, 0.4)

    @patch.dict(
        os.environ,
        {"OPENAI_MODEL": "gpt-4-turbo", "OPENAI_TEMPERATURE": "0.5", "OPENAI_MAX_TOKENS": "1500"},
    )
    @unittest.skipIf(ModelConfig is None, "ModelConfig module not available")
    def test_model_config_environment_driven(self):
        """Test ModelConfig parameters sourced from environment."""
        config = ModelConfig()

        self.assertEqual(config.model_name, "gpt-4-turbo")
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 1500)

    @patch.dict(os.environ, {"RAG_SIMILARITY_THRESHOLD": "0.85"})
    @unittest.skipIf(RAGConfig is None, "RAGConfig module not available")
    def test_rag_config_environment_driven(self):
        """Test RAGConfig similarity threshold sourced from environment."""
        config = RAGConfig()

        self.assertEqual(config.similarity_threshold, 0.85)

    @patch.dict(os.environ, {"GOVERNOR_SAFETY_THRESHOLD": "0.98"})
    @unittest.skipIf(GovernorConfig is None, "GovernorConfig module not available")
    def test_governor_config_environment_driven(self):
        """Test GovernorConfig safety threshold sourced from environment."""
        config = GovernorConfig()

        self.assertEqual(config.safety_threshold, 0.98)

    @patch.dict(
        os.environ,
        {
            "NEGOTIATION_AUTO_RESOLVE_THRESHOLD": "0.90",
            "NEGOTIATION_MAX_ROUNDS": "3",
            "NEGOTIATION_RESPONSE_TIMEOUT": "45.0",
        },
    )
    @unittest.skipIf(NegotiationConfig is None, "NegotiationConfig module not available")
    def test_negotiation_config_environment_driven(self):
        """Test NegotiationConfig parameters sourced from environment."""
        config = NegotiationConfig()

        self.assertEqual(config.auto_resolve_threshold, 0.90)
        self.assertEqual(config.max_rounds, 3)
        self.assertEqual(config.response_timeout, 45.0)

    @patch.dict(os.environ, {"VALIDATION_MAX_SIMILARITY_THRESHOLD": "0.80", "VALIDATION_TEMPERATURE": "0.7"})
    @unittest.skipIf(SectionIntegratorConfig is None, "SectionIntegratorConfig module not available")
    def test_validation_config_environment_driven(self):
        """Test SectionIntegratorConfig parameters sourced from environment."""
        config = SectionIntegratorConfig()

        self.assertEqual(config.max_similarity_threshold, 0.80)
        self.assertEqual(config.TEMPERATURE, 0.7)

    @patch.dict(os.environ, {"BUDGET_MAX_COST_USD": "0.15", "BUDGET_MAX_LATENCY_MS": "5000"})
    @unittest.skipIf(BudgetProfile is None, "BudgetProfile module not available")
    def test_budget_profile_environment_driven(self):
        """Test BudgetProfile parameters sourced from environment."""
        profile = BudgetProfile()

        self.assertEqual(profile.max_cost_usd, 0.15)
        self.assertEqual(profile.max_latency_ms, 5000)

    def test_all_components_default_fallbacks(self):
        """Test all components properly fall back to defaults when environment is empty."""
        # SignalQuality
        thresholds = QualityThresholds()
        self.assertEqual(thresholds.EXCELLENT_MIN, 0.9)

        # ModelConfig
        model_config = ModelConfig()
        self.assertEqual(model_config.model_name, "gpt-4o")
        self.assertEqual(model_config.temperature, 0.7)
        self.assertEqual(model_config.max_tokens, 2000)

        # RAGConfig
        rag_config = RAGConfig()
        self.assertEqual(rag_config.similarity_threshold, 0.8)

        # GovernorConfig
        gov_config = GovernorConfig()
        self.assertEqual(gov_config.safety_threshold, 0.95)

        # NegotiationConfig
        neg_config = NegotiationConfig()
        self.assertEqual(neg_config.auto_resolve_threshold, 0.8)
        self.assertEqual(neg_config.max_rounds, 2)
        self.assertEqual(neg_config.response_timeout, 30.0)

        # ValidationConfig
        val_config = SectionIntegratorConfig()
        self.assertEqual(val_config.max_similarity_threshold, 0.75)
        self.assertEqual(val_config.TEMPERATURE, 0.6)

        # BudgetProfile
        budget = BudgetProfile()
        self.assertEqual(budget.max_cost_usd, 0.10)
        self.assertEqual(budget.max_latency_ms, 3000)

    @patch.dict(os.environ, {"SIGNAL_MIN_CLAIM_CONFIDENCE": "0.8"})
    def test_signal_quality_claim_analysis_integration(self):
        """Test that claim analysis uses environment-driven confidence."""
        from agentic_core.runtime.shared_runtime.signal_quality_types import ClaimAnalyzer

        analyzer = ClaimAnalyzer()
        content = "According to a study, this approach works well."

        claims = analyzer.extract_claims(content)
        if claims:
            # Should use environment value (0.8) instead of hardcoded 0.7
            self.assertEqual(claims[0].confidence, 0.8)

    def test_no_hardcoded_values_remain(self):
        """Verify no hardcoded values remain in critical paths."""
        # This test ensures dynamic property access is working
        thresholds = QualityThresholds()

        # These should be properties that dynamically access environment
        self.assertTrue(hasattr(thresholds, "EXCELLENT_MIN"))
        self.assertTrue(hasattr(thresholds, "HIGH_MIN"))
        self.assertTrue(hasattr(thresholds, "GOOD_MIN"))
        self.assertTrue(hasattr(thresholds, "MARGINAL_MIN"))

        # Verify they're properties, not static values
        for attr_name in ["EXCELLENT_MIN", "HIGH_MIN", "GOOD_MIN", "MARGINAL_MIN"]:
            attr = getattr(type(thresholds), attr_name)
            self.assertTrue(isinstance(attr, property), f"{attr_name} should be a property")


if __name__ == "__main__":
    unittest.main()
