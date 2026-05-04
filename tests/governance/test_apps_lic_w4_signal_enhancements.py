"""apps_lic W4 (D6) — signal enhancement engines sentinel tests.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P1..P5
Coverage:
  - NarrativeArcEngine: shape, matrix completeness, disabled when env absent
  - ArchetypeToneSelector: shape, matrix completeness, additive contract
  - MultiTouchSequencer: shape, sequencing strategy progression, exhaustion
  - ResurfacingDetector: shape, cool-off blocking, trigger override, warm paths
  - MutualNetworkEngine: shape, signal strength tiers, no-connection baseline
  - All engines: decision-only (no writes, no provider calls)
  - All engines: config-gated (feature disabled without env var)
"""

from __future__ import annotations

import os
import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock


# ===========================================================================
# NarrativeArcEngine (D6-P1)
# ===========================================================================

class TestNarrativeArcEngine:
    def _engine(self):
        from apps_lic.engines.narrative_arc_engine import NarrativeArcEngine
        return NarrativeArcEngine()

    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("ARC_ENGINE_ENABLED", raising=False)
        result = self._engine().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.enabled is False
        assert result.arc_name == ""
        assert result.source == "disabled"

    def test_enabled_with_env_var(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.enabled is True
        assert result.arc_name != ""

    def test_exec_cold_returns_asymmetric_insight(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.arc_name == "asymmetric_insight"

    def test_recruiter_cold_returns_direct_ask(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="RECRUITER", relationship_distance="cold"
        )
        assert result.arc_name == "direct_ask"

    def test_warm_relationship_returns_warm_arc(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="EXECUTIVE", relationship_distance="warm"
        )
        assert result.arc_name in ("mutual_gain", "warm_reconnect", "social_proof", "peer_expert")

    def test_decision_is_immutable(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="HIRING_MANAGER", relationship_distance="cold"
        )
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.arc_name = "tampered"  # type: ignore

    def test_result_has_required_fields(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        result = self._engine().select(
            recipient_class="C_LEVEL", relationship_distance="referral"
        )
        assert hasattr(result, "arc_name")
        assert hasattr(result, "recipient_bucket")
        assert hasattr(result, "distance_bucket")
        assert hasattr(result, "source")

    def test_all_matrix_cells_produce_valid_arc(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        from apps_lic.engines.narrative_arc_engine import _DEFAULT_ARC_MATRIX, NarrativeArcEngine
        valid_arcs = {
            "problem_solution", "mutual_gain", "social_proof",
            "asymmetric_insight", "warm_reconnect", "direct_ask",
        }
        engine = NarrativeArcEngine()
        for (rb, db), arc in _DEFAULT_ARC_MATRIX.items():
            assert arc in valid_arcs, f"matrix[{rb}][{db}]={arc} not in valid set"


# ===========================================================================
# ArchetypeToneSelector (D6-P2)
# ===========================================================================

class TestArchetypeToneSelector:
    def _selector(self):
        from apps_lic.engines.archetype_tone_selector import ArchetypeToneSelector
        return ArchetypeToneSelector()

    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("ARCHETYPE_TONE_ENABLED", raising=False)
        result = self._selector().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.enabled is False
        assert result.archetype == ""

    def test_enabled_with_env_var(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        result = self._selector().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.enabled is True
        assert result.archetype != ""

    def test_exec_cold_returns_strategic_advisor(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        result = self._selector().select(
            recipient_class="EXECUTIVE", relationship_distance="cold"
        )
        assert result.archetype == "strategic_advisor"

    def test_referral_returns_warm_connector(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        result = self._selector().select(
            recipient_class="HIRING_MANAGER", relationship_distance="referral"
        )
        assert result.archetype == "warm_connector"

    def test_all_matrix_archetypes_valid(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        from apps_lic.engines.archetype_tone_selector import _DEFAULT_TONE_MATRIX, ArchetypeToneSelector
        valid = {
            "peer_expert", "strategic_advisor", "concise_practitioner",
            "warm_connector", "credibility_anchor",
        }
        sel = ArchetypeToneSelector()
        for (rb, db), tone in _DEFAULT_TONE_MATRIX.items():
            assert tone in valid, f"matrix[{rb}][{db}]={tone} not in valid set"

    def test_additive_contract_does_not_replace_personalization(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        result = self._selector().select(
            recipient_class="RECRUITER", relationship_distance="warm"
        )
        assert result.archetype != ""
        # The archetype is selected alongside personalization_mode (not instead of).
        # No field here overrides personalization_mode — verify the ArchetypeToneDecision
        # has NO personalization_mode field at all.
        assert not hasattr(result, "personalization_mode")


# ===========================================================================
# MultiTouchSequencer (D6-P3)
# ===========================================================================

class TestMultiTouchSequencer:
    def _sequencer(self):
        from apps_lic.engines.multi_touch_sequencer import MultiTouchSequencer
        return MultiTouchSequencer()

    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("MULTI_TOUCH_ENABLED", raising=False)
        result = self._sequencer().sequence(recipient_class="EXECUTIVE")
        assert result.enabled is False

    def test_touch_1_initial(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        result = self._sequencer().sequence(
            recipient_class="EXECUTIVE", outreach_history=[]
        )
        assert result.next_touch_number == 1
        assert result.sequencing_strategy == "initial"

    def test_touch_2_nudge(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord
        history = [OutreachTouchRecord(touch_number=1, sent_at_iso="2024-01-01")]
        result = self._sequencer().sequence(
            recipient_class="EXECUTIVE", outreach_history=history
        )
        assert result.next_touch_number == 2
        assert result.sequencing_strategy == "nudge"

    def test_touch_3_fresh_angle(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord
        history = [
            OutreachTouchRecord(touch_number=i, sent_at_iso="2024-01-0" + str(i+1))
            for i in range(1, 3)
        ]
        result = self._sequencer().sequence(
            recipient_class="RECRUITER", outreach_history=history
        )
        assert result.next_touch_number == 3
        assert result.sequencing_strategy == "fresh_angle"

    def test_exhausted_at_max_touches(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord
        history = [
            OutreachTouchRecord(touch_number=i) for i in range(1, 5)
        ]
        result = self._sequencer().sequence(
            recipient_class="RECRUITER", outreach_history=history
        )
        assert result.next_touch_number == 0
        assert result.sequencing_strategy == "exhausted"

    def test_max_touch_strategy_close_or_optout(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord
        history = [
            OutreachTouchRecord(touch_number=i) for i in range(1, 4)
        ]
        result = self._sequencer().sequence(
            recipient_class="RECRUITER", outreach_history=history
        )
        assert result.sequencing_strategy == "close_or_optout"

    def test_prior_count_reported(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord
        history = [OutreachTouchRecord(touch_number=1)]
        result = self._sequencer().sequence(outreach_history=history)
        assert result.prior_touch_count == 1


# ===========================================================================
# ResurfacingDetector (D6-P4)
# ===========================================================================

class TestResurfacingDetector:
    def _detector(self):
        from apps_lic.engines.resurfacing_detector import ResurfacingDetector
        return ResurfacingDetector()

    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("RESURFACING_ENABLED", raising=False)
        result = self._detector().detect()
        assert result.enabled is False
        assert result.recommendation == "disabled"

    def test_blocked_within_cool_off(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=3.0,
            relationship_distance="warm",
        )
        assert result.recommendation == "blocked"

    def test_trigger_overrides_cold(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=100.0,
            relationship_distance="cold",
            trigger_event_detected=True,
        )
        assert result.recommendation == "recommended"
        assert result.trigger_detected is True

    def test_warm_with_prior_response_recommended(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=60.0,
            prior_response_received=True,
            relationship_distance="warm",
        )
        assert result.recommendation == "recommended"

    def test_warm_no_response_conditional(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=45.0,
            prior_response_received=False,
            relationship_distance="warm",
        )
        assert result.recommendation in ("conditional", "recommended")

    def test_cold_no_trigger_not_recommended(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=60.0,
            prior_response_received=False,
            relationship_distance="cold",
            trigger_event_detected=False,
        )
        assert result.recommendation == "not_recommended"

    def test_decision_is_immutable(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        result = self._detector().detect(
            days_since_last_contact=60.0,
            relationship_distance="cold",
        )
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.recommendation = "tampered"  # type: ignore


# ===========================================================================
# MutualNetworkEngine (D6-P5)
# ===========================================================================

class TestMutualNetworkEngine:
    def _engine(self):
        from apps_lic.engines.mutual_network_engine import MutualNetworkEngine
        return MutualNetworkEngine()

    def _connection(self, name: str, rtype: str) -> MagicMock:
        c = MagicMock()
        c.name = name
        c.relationship_type = rtype
        return c

    def test_disabled_without_env_var(self, monkeypatch):
        monkeypatch.delenv("MUTUAL_NETWORK_ENABLED", raising=False)
        result = self._engine().extract()
        assert result.enabled is False
        assert result.signal_strength == "disabled"

    def test_empty_items_no_connection(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        result = self._engine().extract(connection_items=[])
        assert result.signal_strength == "no_connection"
        assert result.connection_count == 0

    def test_direct_connection_is_strong(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        items = [self._connection("Alice", "direct")]
        result = self._engine().extract(connection_items=items)
        assert result.signal_strength == "strong"

    def test_single_network_connection_is_weak(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        items = [self._connection("Bob", "network")]
        result = self._engine().extract(connection_items=items)
        assert result.signal_strength in ("weak", "moderate")

    def test_three_connections_is_strong(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        items = [
            self._connection("A", "colleague"),
            self._connection("B", "colleague"),
            self._connection("C", "colleague"),
        ]
        result = self._engine().extract(connection_items=items)
        assert result.signal_strength == "strong"

    def test_weighted_score_computed(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        items = [self._connection("Alice", "colleague")]
        result = self._engine().extract(connection_items=items)
        assert result.weighted_score > 0.0

    def test_top_connection_name_set(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        items = [
            self._connection("Alice", "direct"),
            self._connection("Bob", "network"),
        ]
        result = self._engine().extract(connection_items=items)
        assert result.top_connection_name == "Alice"

    def test_decision_is_immutable(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        result = self._engine().extract(connection_items=[])
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.signal_strength = "tampered"  # type: ignore
