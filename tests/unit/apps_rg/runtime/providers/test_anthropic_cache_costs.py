from __future__ import annotations

import pytest

from apps_rg.runtime.providers.anthropic_prompt_cache import build_cache_receipt_from_usage


def test_cost_receipt_uses_anthropic_5m_1h_and_read_multipliers() -> None:
    receipt = build_cache_receipt_from_usage(
        seed={
            "cache_enabled": True,
            "cache_strategy": "test",
            "active_cache_ttls": ["1h", "5m"],
            "input_usd_per_million": 2.0,
        },
        provider="external_claude",
        model="claude-sonnet-5",
        section_id="competencies",
        usage={
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_creation_input_tokens": 300,
            "cache_read_input_tokens": 600,
            "cache_creation": {
                "ephemeral_5m_input_tokens": 200,
                "ephemeral_1h_input_tokens": 100,
            },
        },
    )

    assert receipt["estimated_uncached_input_tokens"] == 1000
    assert receipt["estimated_cached_input_tokens"] == 610
    assert receipt["estimated_input_token_savings"] == pytest.approx(390.0)
    assert receipt["estimated_input_cost_without_cache_usd"] == pytest.approx(0.002)
    assert receipt["estimated_input_cost_with_cache_usd"] == pytest.approx(0.00122)
    assert receipt["estimated_input_cost_savings_usd"] == pytest.approx(0.00078)
    assert receipt["cache_creation_5m_input_tokens"] == 200
    assert receipt["cache_creation_1h_input_tokens"] == 100
    assert receipt["cache_hit_ratio"] == pytest.approx(2 / 3)
    assert receipt["cache_hit_ratio_definition"].startswith("cache_read_input_tokens/")


def test_aggregate_creation_without_breakdown_uses_conservative_active_ttl() -> None:
    receipt = build_cache_receipt_from_usage(
        seed={"cache_enabled": True, "active_cache_ttls": ["1h", "5m"]},
        provider="external_claude",
        model="claude-sonnet-5",
        usage={"input_tokens": 0, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 0},
    )

    assert receipt["estimated_uncached_input_tokens"] == 100
    assert receipt["estimated_cached_input_tokens"] == 200
    assert receipt["estimated_input_token_savings"] == -100.0
    assert receipt["cache_creation_cost_basis"] == "aggregate_creation_conservative_multiplier"
