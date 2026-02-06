"""Tests for DomainAgentMixin."""

from agentic_core.primitives.feature_flags import FeatureFlagManager
from apps_shared.integration.domain_agent_mixin import (
    DomainAgentMixin,
    LICDomainMixin,
    RGDomainMixin,
)


class MockDomainAgent(DomainAgentMixin):
    """Mock agent for testing."""

    def __init__(self, domain: str = "test"):
        super().__init__(domain=domain)


class MockRGAgent(RGDomainMixin):
    """Mock RG agent for testing."""

    def __init__(self):
        super().__init__()


class MockLICAgent(LICDomainMixin):
    """Mock LIC agent for testing."""

    def __init__(self):
        super().__init__()


class TestDomainAgentMixin:
    """Tests for DomainAgentMixin."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_init_sets_domain(self):
        """Test that init sets domain correctly."""
        agent = MockDomainAgent(domain="test")
        assert agent.domain == "test"
        assert agent.domain_prefix == "apps_test"

    def test_init_with_apps_prefix(self):
        """Test that apps_ prefix is not doubled."""
        agent = MockDomainAgent(domain="apps_rg")
        assert agent.domain_prefix == "apps_rg"

    def test_get_namespaced_key(self):
        """Test namespaced key generation."""
        agent = MockDomainAgent(domain="test")
        key = agent.get_namespaced_key("my_key")
        assert key == "apps_test:MockDomainAgent:my_key"

    def test_validate_domain_pattern_same_domain(self):
        """Test pattern validation for same domain."""
        agent = MockDomainAgent(domain="test")
        pattern = {"_domain": "apps_test", "data": "value"}
        assert agent.validate_domain_pattern(pattern) is True

    def test_validate_domain_pattern_different_domain(self):
        """Test pattern validation rejects different domain."""
        agent = MockDomainAgent(domain="test")
        pattern = {"_domain": "apps_other", "data": "value"}
        assert agent.validate_domain_pattern(pattern) is False

    def test_validate_domain_pattern_no_domain(self):
        """Test pattern validation with no domain field."""
        agent = MockDomainAgent(domain="test")
        pattern = {"data": "value"}
        assert agent.validate_domain_pattern(pattern) is True

    def test_get_domain_context(self):
        """Test getting domain context."""
        agent = MockDomainAgent(domain="test")
        context = agent.get_domain_context()

        assert context["domain"] == "test"
        assert context["domain_prefix"] == "apps_test"
        assert context["agent_name"] == "MockDomainAgent"
        assert "feature_flags" in context

    def test_domain_heal_with_verification(self):
        """Test domain healing adds context."""
        agent = MockDomainAgent(domain="test")

        violation = {"file_path": "/test.py", "message": "test"}

        def heal_fn(v):
            return {
                "status": "success",
                "violations_found": 1,
                "violations_fixed": 1,
                "errors": [],
                "skipped": [],
            }

        result = agent.domain_heal_with_verification(violation, heal_fn)

        assert result["_domain"] == "apps_test"

    def test_domain_log_audit_event_disabled(self):
        """Test audit logging when disabled."""
        agent = MockDomainAgent(domain="test")
        result = agent.domain_log_audit_event("test_event", {"key": "value"})
        assert result is None

    def test_domain_log_audit_event_enabled(self):
        """Test audit logging when enabled."""
        FeatureFlagManager.set_override("ENABLE_AUDIT_TRAIL", True)
        agent = MockDomainAgent(domain="test")
        result = agent.domain_log_audit_event("test_event", {"key": "value"})
        assert result is not None
        assert result.startswith("AUDIT-")


class TestRGDomainMixin:
    """Tests for RGDomainMixin."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_init_sets_rg_domain(self):
        """Test that RG domain is set correctly."""
        agent = MockRGAgent()
        assert agent.domain == "rg"
        assert agent.domain_prefix == "apps_rg"

    def test_similarity_threshold(self):
        """Test RG similarity threshold."""
        agent = MockRGAgent()
        assert agent._similarity_threshold == 0.85

    def test_ttl_seconds(self):
        """Test RG TTL setting."""
        agent = MockRGAgent()
        assert agent._ttl_seconds == 3600

    def test_store_resume_pattern(self):
        """Test storing resume pattern."""
        agent = MockRGAgent()
        result = agent.store_resume_pattern("pattern-001", {"quality": "high"})
        assert result is True

    def test_get_rg_context(self):
        """Test getting RG context."""
        agent = MockRGAgent()
        context = agent.get_rg_context()

        assert context["domain"] == "rg"
        assert context["similarity_threshold"] == 0.85
        assert context["ttl_seconds"] == 3600


class TestLICDomainMixin:
    """Tests for LICDomainMixin."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_init_sets_lic_domain(self):
        """Test that LIC domain is set correctly."""
        agent = MockLICAgent()
        assert agent.domain == "lic"
        assert agent.domain_prefix == "apps_lic"

    def test_similarity_threshold_stricter(self):
        """Test LIC similarity threshold is stricter."""
        agent = MockLICAgent()
        assert agent._similarity_threshold == 0.92
        # Verify it's stricter than RG
        rg_agent = MockRGAgent()
        assert agent._similarity_threshold > rg_agent._similarity_threshold

    def test_ttl_seconds_longer(self):
        """Test LIC TTL is longer than RG."""
        agent = MockLICAgent()
        assert agent._ttl_seconds == 7200
        # Verify it's longer than RG
        rg_agent = MockRGAgent()
        assert agent._ttl_seconds > rg_agent._ttl_seconds

    def test_store_campaign_pattern(self):
        """Test storing campaign pattern."""
        agent = MockLICAgent()
        result = agent.store_campaign_pattern("campaign-001", {"type": "outreach"})
        assert result is True

    def test_get_lic_context(self):
        """Test getting LIC context."""
        agent = MockLICAgent()
        context = agent.get_lic_context()

        assert context["domain"] == "lic"
        assert context["similarity_threshold"] == 0.92
        assert context["ttl_seconds"] == 7200


class TestMixinInheritance:
    """Tests for mixin inheritance chain."""

    def test_rg_inherits_from_domain_mixin(self):
        """Test RG inherits from DomainAgentMixin."""
        assert issubclass(RGDomainMixin, DomainAgentMixin)

    def test_lic_inherits_from_domain_mixin(self):
        """Test LIC inherits from DomainAgentMixin."""
        assert issubclass(LICDomainMixin, DomainAgentMixin)

    def test_domain_mixin_inherits_from_feature_flagged(self):
        """Test DomainAgentMixin inherits from FeatureFlaggedAgentMixin."""
        from agentic_core.mixins.feature_flagged_agent_mixin import (
            FeatureFlaggedAgentMixin,
        )

        assert issubclass(DomainAgentMixin, FeatureFlaggedAgentMixin)
