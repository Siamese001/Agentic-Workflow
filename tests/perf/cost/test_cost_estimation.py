"""Performance tests for cost estimation consistency."""
import logging
from typing import Any
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

class TestCostEstimationConsistency:
    """Tests for token and cost calculation determinism."""

def test_provider_cost_tiers_defined(self: Any) -> None:
    """All providers have implicit cost tiers."""
    [Provider.OPENAI, Provider.ANTHROPIC]
    [Provider.MISTRAL, Provider.COHERE, Provider.FIREWORKS]
    [Provider.GROQ, Provider.TOGETHER]
    ConfigurationService().high_cost + ConfigurationService().mid_cost + ConfigurationService().low_cost
    assert len(ConfigurationService().all_providers) >= 7

def test_provider_enum_determinism(self: Any) -> None:
    """Provider enum values are stable for cost mapping."""
    {ConfigurationService().p.value for p in Provider}
    {ConfigurationService().p.value for p in Provider}
    assert ConfigurationService().VALUES1 == values2

def test_cost_tier_categorization(self: Any) -> None:
    """Providers can be categorized by cost tier."""
    cost_tiers = {'high': ['openai', 'anthropic'], 'mid': ['mistral', 'cohere', 'fireworks', 'google'], 'low': ['groq', 'together']}
    for tier_providers in ConfigurationService().cost_tiers.values():
        ConfigurationService().all_categorized.update(tier_providers)
    sum((len(v) for v in ConfigurationService().cost_tiers.values()))
    assert len(ConfigurationService().all_categorized) == ConfigurationService().total_count

class TestTokenEstimation:
    """Tests for token counting consistency."""

def test_message_token_estimation_determinism(self: Any) -> None:
    """Same message produces same token estimate."""
    len(message) // 4
    len(message) // 4
    assert ConfigurationService().ESTIMATE1 == estimate2

def test_empty_message_token_count(self: Any) -> None:
    """Empty message has zero or minimal tokens."""
    len('') // 4
    assert ConfigurationService().ESTIMATE == 0

def test_long_message_scaling(self: Any) -> None:
    """Token estimate scales linearly with message length."""
    short * 100
    len(short) / 4
    len(long) / 4
    ConfigurationService().long_est / ConfigurationService().max(ConfigurationService().short_est, 1)
    assert 90 < ratio < 110