"""Tests for tier-aware I0 instructional enrichment provider."""

import pytest

from agentic_core.prompt_governance.core.tier_instructional_enrichment import (
    TIER_ENRICHMENT_TABLE,
    EnrichmentTier,
    InstructionalEnrichment,
    enrich_i0_for_tier,
    get_tier_enrichment,
)


class TestEnrichmentTier:
    """Test EnrichmentTier enum."""

    def test_all_tiers_exist(self):
        assert EnrichmentTier.LOW == "low"
        assert EnrichmentTier.MEDIUM == "medium"
        assert EnrichmentTier.HIGH == "high"
        assert EnrichmentTier.CRITICAL == "critical"

    def test_tier_count(self):
        assert len(EnrichmentTier) == 4


class TestInstructionalEnrichment:
    """Test InstructionalEnrichment dataclass."""

    def test_frozen(self):
        enrichment = InstructionalEnrichment(
            tier=EnrichmentTier.LOW,
            preamble="test",
            constraints=("c1",),
            guidance=("g1",),
            examples_hint="hint",
        )
        with pytest.raises(AttributeError):
            enrichment.preamble = "modified"

    def test_to_i0_content_includes_preamble(self):
        enrichment = InstructionalEnrichment(
            tier=EnrichmentTier.LOW,
            preamble="You are in LOW mode.",
            constraints=("No branching.",),
            guidance=("Be concise.",),
            examples_hint="Follow format.",
        )
        content = enrichment.to_i0_content()
        assert "You are in LOW mode." in content
        assert "CONSTRAINTS:" in content
        assert "No branching." in content
        assert "GUIDANCE:" in content
        assert "Be concise." in content
        assert "EXAMPLES: Follow format." in content

    def test_to_i0_content_empty_fields(self):
        enrichment = InstructionalEnrichment(
            tier=EnrichmentTier.HIGH,
            preamble="",
            constraints=(),
            guidance=(),
            examples_hint="",
        )
        content = enrichment.to_i0_content()
        assert content == ""


class TestTierEnrichmentTable:
    """Test TIER_ENRICHMENT_TABLE completeness."""

    def test_all_tiers_covered(self):
        for tier in EnrichmentTier:
            assert tier in TIER_ENRICHMENT_TABLE, f"Missing enrichment for {tier}"

    def test_low_tier_has_rich_content(self):
        low = TIER_ENRICHMENT_TABLE[EnrichmentTier.LOW]
        assert len(low.constraints) >= 4, "LOW tier should have >= 4 constraints"
        assert len(low.guidance) >= 4, "LOW tier should have >= 4 guidance items"
        assert low.preamble, "LOW tier must have a preamble"
        assert low.examples_hint, "LOW tier should have examples hint"

    def test_high_tier_less_prescriptive(self):
        high = TIER_ENRICHMENT_TABLE[EnrichmentTier.HIGH]
        low = TIER_ENRICHMENT_TABLE[EnrichmentTier.LOW]
        assert len(high.constraints) < len(low.constraints), (
            "HIGH tier should have fewer constraints than LOW"
        )

    def test_critical_tier_enables_reflexion(self):
        critical = TIER_ENRICHMENT_TABLE[EnrichmentTier.CRITICAL]
        content = critical.to_i0_content()
        assert "reflexion" in content.lower()


class TestGetTierEnrichment:
    """Test get_tier_enrichment function."""

    def test_string_input(self):
        result = get_tier_enrichment("low")
        assert result.tier == EnrichmentTier.LOW

    def test_enum_input(self):
        result = get_tier_enrichment(EnrichmentTier.MEDIUM)
        assert result.tier == EnrichmentTier.MEDIUM

    def test_case_insensitive(self):
        result = get_tier_enrichment("LOW")
        assert result.tier == EnrichmentTier.LOW

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError, match="Unknown reasoning tier"):
            get_tier_enrichment("ultra")

    def test_all_tiers_return_enrichment(self):
        for tier_str in ("low", "medium", "high", "critical"):
            result = get_tier_enrichment(tier_str)
            assert isinstance(result, InstructionalEnrichment)


class TestEnrichI0ForTier:
    """Test enrich_i0_for_tier function."""

    def test_empty_existing_i0(self):
        result = enrich_i0_for_tier("", "low")
        assert "LOW reasoning mode" in result
        assert "CONSTRAINTS:" in result

    def test_placeholder_i0_replaced(self):
        result = enrich_i0_for_tier("instructional", "low")
        assert "LOW reasoning mode" in result
        assert "instructional" not in result.split("\n")[0]

    def test_existing_i0_preserved(self):
        result = enrich_i0_for_tier("Custom agent instructions here.", "low")
        assert "AGENT-SPECIFIC INSTRUCTIONS:" in result
        assert "Custom agent instructions here." in result
        assert "LOW reasoning mode" in result

    def test_high_tier_minimal(self):
        result = enrich_i0_for_tier("", "high")
        assert "Standard reasoning mode" in result

    def test_medium_tier_moderate(self):
        result = enrich_i0_for_tier("", "medium")
        assert "MEDIUM reasoning mode" in result
        assert "2 alternatives" in result

    def test_deterministic_output(self):
        r1 = enrich_i0_for_tier("test", "low")
        r2 = enrich_i0_for_tier("test", "low")
        assert r1 == r2, "Enrichment must be deterministic"
