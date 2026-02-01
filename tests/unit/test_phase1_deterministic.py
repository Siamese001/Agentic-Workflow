"""
Phase 1 Test Suite: Pure Deterministic Layer Validation

Comprehensive testing of Phase 1 deterministic components:
- CampaignBalanceDeterministic (100% deterministic)
- DeliverabilityDeterministic (100% deterministic)
- LeadQualityDeterministic (100% deterministic)
- IntelligenceLibrarianDeterministic (100% deterministic)

All tests must pass 100% before Phase 1 commit.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_maintenance.deterministic.CampaignBalanceDeterministic import (
    BalanceResult,
    CampaignBalanceDeterministic,
)
from agentic_core.L0_maintenance.deterministic.DeliverabilityDeterministic import (
    DeliverabilityDeterministic,
    DeliverabilityResult,
)
from agentic_core.L0_maintenance.deterministic.LeadQualityDeterministic import (
    LeadQualityDeterministic,
    LeadQualityResult,
)
from agentic_core.L0_maintenance.deterministic.IntelligenceLibrarianDeterministic import (
    IntelligenceLibrarianDeterministic,
    IntelligenceQueryResult,
)


class TestCampaignBalanceDeterministic:
    """Test Campaign Balance Deterministic Layer - 100% pass required."""

    @pytest.fixture
    def validator(self) -> CampaignBalanceDeterministic:
        """Campaign balance validator for testing."""
        thresholds = {"max_leads_per_message": 100, "min_leads_per_message": 1}
        return CampaignBalanceDeterministic(thresholds)

    def test_ratio_calculation_deterministic(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 1: Ratio calculation is 100% deterministic."""
        campaign = {"name": "Test Campaign", "goal": "Generate leads"}
        leads = ["lead1", "lead2", "lead3", "lead4", "lead5"]
        messages = ["msg1", "msg2"]

        result = validator.validate_campaign_balance(campaign, leads, messages)

        assert isinstance(result, BalanceResult)
        assert result.ratio == 2.5
        assert result.passed

    def test_threshold_validation_max_exceeded(
        self, validator: CampaignBalanceDeterministic
    ) -> None:
        """Test 2: Max threshold validation is deterministic."""
        leads = [f"lead{i}" for i in range(150)]
        messages = ["msg1"]

        result = validator.validate_campaign_balance({}, leads, messages)

        assert not result.passed
        assert result.ratio == 150.0
        assert "Too many leads per message template" in result.issues

    def test_threshold_validation_min_exceeded(
        self, validator: CampaignBalanceDeterministic
    ) -> None:
        """Test 3: Min threshold validation is deterministic."""
        leads = ["lead1"]
        messages = ["msg1", "msg2", "msg3", "msg4"]

        result = validator.validate_campaign_balance({}, leads, messages)

        assert not result.passed
        assert result.ratio == 0.25
        assert "More templates than leads" in result.issues

    def test_required_fields_validation(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 4: Required field validation is deterministic."""
        campaign_missing_name = {"goal": "Generate leads"}
        campaign_missing_goal = {"name": "Test Campaign"}
        campaign_complete = {"name": "Test Campaign", "goal": "Generate leads"}

        result1 = validator.validate_campaign_balance(campaign_missing_name, [], [])
        result2 = validator.validate_campaign_balance(campaign_missing_goal, [], [])
        result3 = validator.validate_campaign_balance(campaign_complete, [], [])

        assert not result1.passed
        assert "Campaign missing name" in result1.issues
        assert not result2.passed
        assert "Campaign missing goal" in result2.issues
        assert result3.passed

    def test_balance_score_calculation(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 5: Balance score calculation is deterministic."""
        campaign = {"name": "Test", "goal": "Generate leads"}
        leads = ["lead1", "lead2", "lead3"]
        messages = ["msg1", "msg2"]

        score = validator.calculate_balance_score(campaign, leads, messages)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score == 1.0

    def test_improvement_suggestions(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 6: Improvement suggestions are deterministic."""
        campaign = {"name": "Test"}
        leads = ["lead1", "lead2"]
        messages = ["msg1", "msg2", "msg3", "msg4"]

        suggestions = validator.suggest_improvements(campaign, leads, messages)

        assert isinstance(suggestions, list)
        assert "Define a clear campaign goal" in suggestions

    def test_empty_inputs(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 7: Empty inputs handled correctly."""
        result = validator.validate_campaign_balance({}, [], [])

        assert result.ratio is None
        assert "Campaign missing name" in result.issues
        assert "Campaign missing goal" in result.issues

    def test_perfect_balance(self, validator: CampaignBalanceDeterministic) -> None:
        """Test 8: Perfect balance scenario."""
        campaign = {"name": "Perfect", "goal": "Success"}
        leads = ["lead1", "lead2", "lead3", "lead4", "lead5"]
        messages = ["msg1", "msg2", "msg3", "msg4", "msg5"]

        result = validator.validate_campaign_balance(campaign, leads, messages)

        assert result.passed
        assert result.ratio == 1.0
        assert len(result.issues) == 0


class TestDeliverabilityDeterministic:
    """Test Deliverability Deterministic Layer - 100% pass required."""

    @pytest.fixture
    def validator(self) -> DeliverabilityDeterministic:
        """Deliverability validator for testing."""
        return DeliverabilityDeterministic()

    def test_spam_trigger_detection(self, validator: DeliverabilityDeterministic) -> None:
        """Test 1: Spam trigger detection is deterministic."""
        messages = [{"content": "Get FREE money $$$"}]

        result = validator.validate_deliverability(messages)

        assert not result.passed
        assert any("Spam trigger" in issue for issue in result.issues)

    def test_link_count_validation(self, validator: DeliverabilityDeterministic) -> None:
        """Test 2: Link count validation is deterministic."""
        messages = [{"content": "http://a.com http://b.com http://c.com http://d.com http://e.com"}]

        result = validator.validate_deliverability(messages)

        assert not result.passed
        assert any("Too many links" in issue for issue in result.issues)

    def test_image_count_validation(self, validator: DeliverabilityDeterministic) -> None:
        """Test 3: Image count validation is deterministic."""
        messages = [{"content": "<img src='a'><img src='b'><img src='c'><img src='d'>"}]

        result = validator.validate_deliverability(messages)

        assert not result.passed
        assert any("Too many images" in issue for issue in result.issues)

    def test_clean_message_passes(self, validator: DeliverabilityDeterministic) -> None:
        """Test 4: Clean message passes validation."""
        messages = [{"content": "Hello, this is a professional message."}]

        result = validator.validate_deliverability(messages)

        assert result.passed
        assert len(result.issues) == 0
        assert result.score == 1.0

    def test_empty_messages(self, validator: DeliverabilityDeterministic) -> None:
        """Test 5: Empty messages handled correctly."""
        result = validator.validate_deliverability([])

        assert result.passed
        assert result.score == 1.0
        assert result.metadata["message_count"] == 0

    def test_multiple_messages(self, validator: DeliverabilityDeterministic) -> None:
        """Test 6: Multiple messages validated correctly."""
        messages = [
            {"content": "Clean message 1"},
            {"content": "BUY NOW special offer"},
            {"content": "Clean message 2"},
        ]

        result = validator.validate_deliverability(messages)

        assert not result.passed
        assert any("Message 1" in issue for issue in result.issues)

    def test_single_message_convenience(self, validator: DeliverabilityDeterministic) -> None:
        """Test 7: Single message convenience method works."""
        result = validator.check_single_message("Professional content here")

        assert result.passed
        assert len(result.issues) == 0

    def test_content_risk_analysis(self, validator: DeliverabilityDeterministic) -> None:
        """Test 8: Content risk analysis is deterministic."""
        content = "FREE offer http://a.com http://b.com http://c.com http://d.com"

        analysis = validator.analyze_content_risk(content)

        assert analysis["spam_trigger_count"] >= 1
        assert analysis["link_count"] == 4
        assert analysis["risk_level"] in ["low", "medium", "high"]


class TestLeadQualityDeterministic:
    """Test Lead Quality Deterministic Layer - 100% pass required."""

    @pytest.fixture
    def validator(self) -> LeadQualityDeterministic:
        """Lead quality validator for testing."""
        return LeadQualityDeterministic()

    def test_required_fields_validation(self, validator: LeadQualityDeterministic) -> None:
        """Test 1: Required fields validation is deterministic."""
        leads = [{"email": "test@example.com"}]

        result = validator.validate_lead_quality(leads)

        assert not result.passed
        assert any("Missing company" in issue for issue in result.issues)

    def test_contact_info_validation(self, validator: LeadQualityDeterministic) -> None:
        """Test 2: Contact info validation is deterministic."""
        leads = [{"company": "Test Corp"}]

        result = validator.validate_lead_quality(leads)

        assert not result.passed
        assert any("Missing contact info" in issue for issue in result.issues)

    def test_suspicious_domain_detection(self, validator: LeadQualityDeterministic) -> None:
        """Test 3: Suspicious domain detection is deterministic."""
        leads = [{"company": "Test Corp", "email": "test@spam.xyz"}]

        result = validator.validate_lead_quality(leads)

        assert not result.passed
        assert any("Suspicious email domain" in issue for issue in result.issues)

    def test_spam_indicator_detection(self, validator: LeadQualityDeterministic) -> None:
        """Test 4: Spam indicator detection is deterministic."""
        leads = [{"company": "Test Corp", "email": "noreply@example.com"}]

        result = validator.validate_lead_quality(leads)

        assert not result.passed
        assert any("Spam indicator" in issue for issue in result.issues)

    def test_valid_lead_passes(self, validator: LeadQualityDeterministic) -> None:
        """Test 5: Valid lead passes validation."""
        leads = [{"company": "Test Corp", "email": "john@example.com", "contact_name": "John"}]

        result = validator.validate_lead_quality(leads)

        assert result.passed
        assert len(result.issues) == 0
        assert result.score == 1.0

    def test_empty_leads(self, validator: LeadQualityDeterministic) -> None:
        """Test 6: Empty leads handled correctly."""
        result = validator.validate_lead_quality([])

        assert result.passed
        assert result.score == 1.0
        assert result.metadata["lead_count"] == 0

    def test_multiple_leads(self, validator: LeadQualityDeterministic) -> None:
        """Test 7: Multiple leads validated correctly."""
        leads = [
            {"company": "Good Corp", "email": "good@example.com"},
            {"company": "Bad Corp", "email": "test@spam.xyz"},
            {"company": "Another Corp", "email": "another@example.com"},
        ]

        result = validator.validate_lead_quality(leads)

        assert not result.passed
        assert any("Lead 1" in issue for issue in result.issues)

    def test_lead_completeness(self, validator: LeadQualityDeterministic) -> None:
        """Test 8: Lead completeness calculation is deterministic."""
        lead = {"company": "Test Corp", "email": "test@example.com", "contact_name": "John"}

        completeness = validator.get_lead_completeness(lead)

        assert isinstance(completeness, float)
        assert 0.0 <= completeness <= 1.0
        assert completeness == 1.0

    def test_lead_risk_analysis(self, validator: LeadQualityDeterministic) -> None:
        """Test 9: Lead risk analysis is deterministic."""
        lead = {"company": "Test", "email": "noreply@spam.xyz"}

        analysis = validator.analyze_lead_risk(lead)

        assert analysis["has_suspicious_domain"] is True
        assert analysis["has_spam_indicator"] is True
        assert analysis["risk_level"] == "high"


class TestIntelligenceLibrarianDeterministic:
    """Test Intelligence Librarian Deterministic Layer - 100% pass required."""

    @pytest.fixture
    def validator(self) -> IntelligenceLibrarianDeterministic:
        """Intelligence librarian validator for testing."""
        return IntelligenceLibrarianDeterministic()

    def test_query_validation_empty(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 1: Empty query validation is deterministic."""
        result = validator.validate_query("")

        assert not result.valid
        assert "Query cannot be empty" in result.issues

    def test_query_validation_too_short(
        self, validator: IntelligenceLibrarianDeterministic
    ) -> None:
        """Test 2: Short query validation is deterministic."""
        result = validator.validate_query("ab")

        assert not result.valid
        assert any("too short" in issue for issue in result.issues)

    def test_query_validation_too_long(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 3: Long query validation is deterministic."""
        long_query = "a" * 600

        result = validator.validate_query(long_query)

        assert not result.valid
        assert any("too long" in issue for issue in result.issues)

    def test_query_validation_invalid_chars(
        self, validator: IntelligenceLibrarianDeterministic
    ) -> None:
        """Test 4: Invalid character validation is deterministic."""
        result = validator.validate_query("test <script> query")

        assert not result.valid
        assert any("invalid characters" in issue for issue in result.issues)

    def test_valid_query_passes(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 5: Valid query passes validation."""
        result = validator.validate_query("market intelligence query")

        assert result.valid
        assert len(result.issues) == 0
        assert result.cache_key is not None

    def test_filter_validation_unknown_key(
        self, validator: IntelligenceLibrarianDeterministic
    ) -> None:
        """Test 6: Unknown filter key validation is deterministic."""
        result = validator.validate_query("test query", {"unknown_filter": "value"})

        assert not result.valid
        assert any("Unknown filter key" in issue for issue in result.issues)

    def test_filter_validation_invalid_threshold(
        self, validator: IntelligenceLibrarianDeterministic
    ) -> None:
        """Test 7: Invalid threshold validation is deterministic."""
        result = validator.validate_query("test query", {"relevance_threshold": 1.5})

        assert not result.valid
        assert any("relevance_threshold" in issue for issue in result.issues)

    def test_cache_key_generation(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 8: Cache key generation is deterministic."""
        result1 = validator.validate_query("test query", {"industry": "tech"})
        result2 = validator.validate_query("test query", {"industry": "tech"})

        assert result1.cache_key == result2.cache_key

    def test_query_normalization(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 9: Query normalization is deterministic."""
        normalized = validator.normalize_query("  Test   Query  ")

        assert normalized == "test query"

    def test_result_filtering(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 10: Result filtering is deterministic."""
        results = [
            {"id": "1", "relevance": 0.9, "industry": "tech"},
            {"id": "2", "relevance": 0.5, "industry": "finance"},
            {"id": "3", "relevance": 0.8, "industry": "tech"},
        ]
        filters = {"relevance_threshold": 0.7, "industry": "tech"}

        filtered = validator.filter_results(results, filters)

        assert len(filtered) == 2
        assert all(r["industry"] == "tech" for r in filtered)
        assert all(r["relevance"] >= 0.7 for r in filtered)

    def test_query_complexity_analysis(self, validator: IntelligenceLibrarianDeterministic) -> None:
        """Test 11: Query complexity analysis is deterministic."""
        simple_query = "market trends"
        complex_query = '"artificial intelligence" AND "machine learning" OR "deep learning"'

        simple_analysis = validator.calculate_query_complexity(simple_query)
        complex_analysis = validator.calculate_query_complexity(complex_query)

        assert simple_analysis["complexity_level"] == "simple"
        assert complex_analysis["complexity_score"] > simple_analysis["complexity_score"]


class TestPhase1Integration:
    """Integration tests for Phase 1 deterministic components."""

    def test_all_validators_instantiate(self) -> None:
        """Test 1: All Phase 1 validators can be instantiated."""
        campaign_validator = CampaignBalanceDeterministic()
        deliverability_validator = DeliverabilityDeterministic()
        lead_validator = LeadQualityDeterministic()
        intelligence_validator = IntelligenceLibrarianDeterministic()

        assert campaign_validator is not None
        assert deliverability_validator is not None
        assert lead_validator is not None
        assert intelligence_validator is not None

    def test_all_validators_return_correct_types(self) -> None:
        """Test 2: All validators return correct result types."""
        campaign_result = CampaignBalanceDeterministic().validate_campaign_balance({}, [], [])
        deliverability_result = DeliverabilityDeterministic().validate_deliverability([])
        lead_result = LeadQualityDeterministic().validate_lead_quality([])
        intelligence_result = IntelligenceLibrarianDeterministic().validate_query("test")

        assert isinstance(campaign_result, BalanceResult)
        assert isinstance(deliverability_result, DeliverabilityResult)
        assert isinstance(lead_result, LeadQualityResult)
        assert isinstance(intelligence_result, IntelligenceQueryResult)

    def test_deterministic_behavior_consistency(self) -> None:
        """Test 3: All validators produce consistent results."""
        # Run same validation 10 times
        validator = CampaignBalanceDeterministic()
        campaign = {"name": "Test", "goal": "Success"}
        leads = ["lead1", "lead2"]
        messages = ["msg1"]

        results = [
            validator.validate_campaign_balance(campaign, leads, messages) for _ in range(10)
        ]

        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result.passed == first_result.passed
            assert result.ratio == first_result.ratio
            assert result.issues == first_result.issues

    def test_performance_benchmark(self) -> None:
        """Test 4: Validators perform within acceptable time."""
        import time

        validator = DeliverabilityDeterministic()
        messages = [{"content": f"Message {i} content"} for i in range(100)]

        start_time = time.time()
        for _ in range(100):
            validator.validate_deliverability(messages)
        end_time = time.time()

        # Should complete 100 validations of 100 messages each in under 2 seconds
        assert (end_time - start_time) < 2.0


# Test execution summary
def test_phase1_execution_summary() -> None:
    """Summary: All Phase 1 tests validate deterministic behavior with 100% pass requirement."""
    print("=" * 60)
    print("Phase 1 Test Suite Summary")
    print("=" * 60)
    print("✅ CampaignBalanceDeterministic: 8 tests")
    print("✅ DeliverabilityDeterministic: 8 tests")
    print("✅ LeadQualityDeterministic: 9 tests")
    print("✅ IntelligenceLibrarianDeterministic: 11 tests")
    print("✅ Phase1Integration: 4 tests")
    print("-" * 60)
    print("Total: 40 tests")
    print("=" * 60)
