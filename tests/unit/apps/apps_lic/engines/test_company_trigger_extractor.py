"""Unit tests for company_trigger_extractor (W2-P4)."""

from __future__ import annotations

import pytest

from apps_lic.engines.company_trigger_extractor import (
    extract_best_trigger,
    extract_triggers,
)
from apps_lic.types.outreach_trigger_types import (
    STRENGTH_BANDS,
    TRIGGER_TYPES,
    CompanyTrigger,
)


def _artifact(artifact_id: str, summary: str) -> dict:
    return {"artifact_id": artifact_id, "summary": summary}


class TestTriggerTypeMatching:
    def test_funding_round_series(self) -> None:
        triggers = extract_triggers(
            [_artifact("a1", "Acme just closed their Series C round raising $45M this week")]
        )
        assert triggers
        assert triggers[0].trigger_type == "funding_round"
        assert triggers[0].source_id == "a1"

    def test_leadership_appointment(self) -> None:
        triggers = extract_triggers(
            [_artifact("a2", "The board appointed Jane Doe as CEO yesterday")]
        )
        types = {t.trigger_type for t in triggers}
        assert "leadership" in types

    def test_product_launch(self) -> None:
        triggers = extract_triggers(
            [_artifact("a3", "Acme launched their new platform in general availability")]
        )
        types = {t.trigger_type for t in triggers}
        assert "product_launch" in types

    def test_earnings_beat(self) -> None:
        triggers = extract_triggers(
            [_artifact("a4", "Q3 earnings beat consensus by 12%")]
        )
        types = {t.trigger_type for t in triggers}
        assert "earnings" in types

    def test_acquisition(self) -> None:
        triggers = extract_triggers(
            [_artifact("a5", "Acme acquired BetaCorp for $200M last quarter")]
        )
        types = {t.trigger_type for t in triggers}
        assert "acquisition" in types

    def test_expansion(self) -> None:
        triggers = extract_triggers(
            [_artifact("a6", "The firm is expanding into the APAC market this year")]
        )
        types = {t.trigger_type for t in triggers}
        assert "expansion" in types

    def test_award(self) -> None:
        triggers = extract_triggers(
            [_artifact("a7", "Acme was named on the top 100 best places to work list")]
        )
        types = {t.trigger_type for t in triggers}
        assert "award" in types


class TestStrengthScoring:
    def test_dollar_amount_upgrades_strength(self) -> None:
        weak = extract_triggers([_artifact("w", "They raised Series A")])
        strong = extract_triggers([_artifact("s", 'They raised $50M Series A this week, CEO said "exciting milestone"')])
        assert weak
        assert strong
        # Strong excerpt has dollar + quote + recent_date = score >= 3 -> strong
        assert strong[0].strength == "strong"
        # Weak excerpt has no quantifiers -> weak
        assert weak[0].strength == "weak"

    def test_recent_date_upgrades(self) -> None:
        triggers = extract_triggers(
            [_artifact("a", "CEO transition announced yesterday")]
        )
        assert triggers
        assert triggers[0].strength in {"moderate", "strong"}


class TestRankingAndBest:
    def test_best_trigger_is_strongest(self) -> None:
        triggers = extract_triggers(
            [
                _artifact("weak", "Awarded recognition"),
                _artifact("strong", 'Raised $100M Series D this week — "strong signal" per the CEO'),
            ]
        )
        assert triggers[0].strength == "strong"
        best = extract_best_trigger(
            [
                _artifact("weak", "Awarded recognition"),
                _artifact("strong", 'Raised $100M Series D this week — "strong signal" per the CEO'),
            ]
        )
        assert best is not None
        assert best.strength == "strong"

    def test_empty_evidence_pack_returns_empty(self) -> None:
        assert extract_triggers([]) == []
        assert extract_best_trigger([]) is None

    def test_ranking_is_deterministic(self) -> None:
        pack = [
            _artifact("a1", "Series A raise"),
            _artifact("a2", "Awarded top 50 list"),
        ]
        r1 = extract_triggers(pack)
        r2 = extract_triggers(pack)
        assert [t.trigger_type for t in r1] == [t.trigger_type for t in r2]


class TestResilience:
    def test_missing_summary_tolerated(self) -> None:
        triggers = extract_triggers([{"artifact_id": "x"}])
        assert triggers == []

    def test_non_string_summary_tolerated(self) -> None:
        triggers = extract_triggers([{"artifact_id": "x", "summary": 12345}])
        assert triggers == []

    def test_blank_summary_tolerated(self) -> None:
        triggers = extract_triggers([{"artifact_id": "x", "summary": "   "}])
        assert triggers == []

    def test_missing_artifact_id_uses_empty(self) -> None:
        triggers = extract_triggers(
            [{"summary": "Series B round closed for $25M this week"}]
        )
        assert triggers
        assert triggers[0].source_id == ""


class TestTaxonomyInvariants:
    def test_all_trigger_types_match_canonical_taxonomy(self) -> None:
        from apps_lic.engines.company_trigger_extractor import _TRIGGER_RULES

        assert set(_TRIGGER_RULES.keys()) == set(TRIGGER_TYPES)

    def test_excerpt_respects_max_chars(self) -> None:
        long_text = "x" * 500 + " Series A raise for $10M. " + "y" * 500
        triggers = extract_triggers([_artifact("a", long_text)])
        assert triggers
        assert len(triggers[0].raw_excerpt) <= 240

    def test_strength_values_are_canonical(self) -> None:
        triggers = extract_triggers(
            [_artifact("a", "Acme raised Series A")]
        )
        for t in triggers:
            assert t.strength in STRENGTH_BANDS
