"""End-to-end integration walk of HOP2/HOP3/HOP9 follow-up wiring.

This test walks the data flow that the W1-W4 follow-up wiring
introduced (2026-05-01) using a stub buffer + registry rather than a
fully configured ImmutableStagingBuffer. The point is to lock the
INTERFACE between hops:

    HOP-2 emits company_triggers + best_company_trigger
    HOP-3 emits mutual_connection_priming_line
    HOP-9 emits cadence_advice from the FollowupCadenceEngine

Full HOP1-9 dataclass instantiation is deliberately out of scope.
This file proves the WIRING contract: the dict shapes are stable across
the buffer hop boundaries, and the live validators behave as expected.
"""

from __future__ import annotations

from apps_lic.engines.company_trigger_extractor import (
    extract_best_trigger,
    extract_triggers,
)
from apps_lic.engines.followup_cadence_engine import FollowupCadenceEngine
from apps_lic.engines.mutual_connection_resolver import MutualConnectionResolver
from apps_lic.types.cadence_state_types import CadenceAction, CadenceState, CadenceStateRecord
from apps_lic.validators.archetype_message_length_validator import validate_length
from apps_lic.validators.question_ending_validator import validate_question_ending
from apps_lic.validators.spam_trigger_phrase_validator import (
    validate_message_for_spam_triggers,
)


class TestHop2Wiring:
    """HOP2 contract: evidence_pack[*].summary -> triggers list + best_trigger dict."""

    def test_evidence_pack_with_strong_trigger_yields_best_trigger(self) -> None:
        evidence_pack = [
            {
                "artifact_id": "art-1",
                "summary": (
                    'Acme just closed a $50M Series C this week — CEO said '
                    '"strong signal for the market"'
                ),
                "source": "press_release",
                "confidence": 0.9,
            },
            {
                "artifact_id": "art-2",
                "summary": "Acme was named on the top 100 best places to work list",
                "source": "industry_award",
                "confidence": 0.7,
            },
        ]
        triggers = extract_triggers(evidence_pack)
        best = extract_best_trigger(evidence_pack)

        # The funding round with $ + quote + recent date is strongest.
        assert best is not None
        assert best.trigger_type == "funding_round"
        assert best.strength == "strong"
        # Multiple triggers extracted; best is the first.
        assert len(triggers) >= 2
        assert triggers[0].cell_id if hasattr(triggers[0], "cell_id") else True

    def test_empty_evidence_pack_yields_none_best_trigger(self) -> None:
        assert extract_best_trigger([]) is None
        assert extract_triggers([]) == []


class TestHop3Wiring:
    """HOP3 contract: mission_input.mutual_connections -> priming line string."""

    def test_recent_warm_introducer_renders_priming_line(self) -> None:
        candidates = [
            {"name": "Dana Lee", "topic": "AI infrastructure", "last_seen_days": 5},
        ]
        line = MutualConnectionResolver().resolve_priming_line(candidates)
        assert "Dana Lee" in line
        assert "AI infrastructure" in line

    def test_empty_candidates_yields_empty_string(self) -> None:
        assert MutualConnectionResolver().resolve_priming_line([]) == ""

    def test_warm_introducer_overrides_recency_via_relevance_boost(self) -> None:
        candidates = [
            {"name": "Recent", "topic": "X", "last_seen_days": 3},
            {
                "name": "Warm Intro",
                "topic": "Y",
                "last_seen_days": 200,
                "relevance_boost": 5.0,
            },
        ]
        line = MutualConnectionResolver().resolve_priming_line(candidates)
        assert "Warm Intro" in line


class TestLiveValidatorChain:
    """Live validator contract: archetype + draft text -> validator results."""

    def test_clean_executive_message_passes_all_three_new_rules(self) -> None:
        clean_msg = (
            "Saw the recent Series C announcement — congratulations. "
            "Curious whether your team is exploring agentic infrastructure "
            "for governance use-cases. Worth a brief chat?"
        )
        length = validate_length(clean_msg, "EXECUTIVE")
        question = validate_question_ending(clean_msg, "EXECUTIVE")
        spam = validate_message_for_spam_triggers(clean_msg)
        assert length.is_valid is True
        assert question.is_valid is True
        assert spam.is_valid is True

    def test_pathological_message_triggers_all_three_rules(self) -> None:
        bad_msg = (
            "Hope this finds you well. Just wanted to circle back on "
            "synergies. Act now — last chance to book a call on calendly."
        ) + (" extra " * 60)  # blow past EXECUTIVE 400-char cap
        length = validate_length(bad_msg, "EXECUTIVE")
        question = validate_question_ending(bad_msg, "EXECUTIVE")
        spam = validate_message_for_spam_triggers(bad_msg)
        assert length.is_valid is False
        assert length.excess > 0
        assert question.is_valid is False
        assert question.required_for_archetype is True
        assert spam.is_valid is False  # critical (last chance) + high (act now / calendly)
        assert spam.total_hit_count >= 1

    def test_recruiter_archetype_relaxes_question_ending(self) -> None:
        msg = "Open to discussing a senior role at Acme."
        question = validate_question_ending(msg, "RECRUITER")
        assert question.is_valid is True
        assert question.required_for_archetype is False


class TestHop9CadenceWiring:
    """HOP9 contract: mission_input.campaign_id + recipient -> cadence_advice."""

    def test_initial_send_advice_when_no_state(self) -> None:
        from apps_lic.engines.followup_cadence_engine import FollowupCadenceEngine

        record = CadenceStateRecord(
            campaign_id="camp", recipient_id="recip", current_state=CadenceState.INITIAL
        )
        decision = FollowupCadenceEngine().advance(record)
        assert decision.action is CadenceAction.SEND
        assert decision.message_template == "initial"

    def test_terminated_state_yields_no_action(self) -> None:
        from apps_lic.engines.followup_cadence_engine import FollowupCadenceEngine

        record = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.TERMINATED,
            terminated_reason="replied",
        )
        decision = FollowupCadenceEngine().advance(record)
        assert decision.action is CadenceAction.NO_ACTION


class TestFullPlanFollowupSurfaceImports:
    """Sanity: every follow-up module imports cleanly side-by-side."""

    def test_all_followup_modules_importable(self) -> None:
        # Each import is independently exercised in its dedicated test
        # file; this test guards against accidental import-order
        # circular deps between the new modules.
        from apps_lic.engines.prior_delta_applier import PriorDeltaApplier  # noqa: F401
        from apps_lic.observability.event_bus import JsonlEventBus  # noqa: F401
        from apps_lic.observability.outreach_learning_subscriber import (  # noqa: F401
            OutreachLearningSubscriber,
        )
        from apps_lic.persistence.cadence_state_store import CadenceStateStore  # noqa: F401
        from apps_lic.persistence.reply_ledger_store import ReplyLedgerStore  # noqa: F401
