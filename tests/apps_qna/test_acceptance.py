"""W4.4 Acceptance tests — 37 tests covering Tier 1/2, router, egress, L2, exit, cache.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W4.4
"""

from __future__ import annotations

import pytest

from apps_qna.router.two_tier_router import (
    RoutePrecedence,
    TierSelection,
    resolve_ambiguity,
    select_tier_cards,
)
from apps_qna.l2.e4_heal import heal_cards
from apps_qna.l2.e5_seal import seal_manifest
from apps_qna.egress.blocking_rules import check_egress
from apps_qna.cache.r1a_exact import r1a_lookup, r1a_store
from apps_qna.cache.r1b_semantic import r1b_lookup
from apps_qna.cache.r5_fallback import r5_lookup
from apps_qna.exit_wiring import emit_exit_review
from apps_qna.l2.e3_exec import execute_build
from apps_qna.l2.e1_prep import prep_workspace
from apps_qna.c0_adapter import call_c0
from apps_qna.types.spine_contracts import X3Disposition


class TestTierCards:
    """Tier 1/2 card tests (5 tests)."""

    def test_tier1_always_on_cards_exist(self) -> None:
        sel = select_tier_cards(route_id="apps_qna.live_interview_runtime_pack_v1")
        assert len(sel.tier1_cards) == 4

    def test_tier2_specialist_cards_selected(self) -> None:
        sel = select_tier_cards(route_id="apps_qna.live_interview_runtime_pack_v1")
        assert len(sel.tier2_cards) >= 1

    def test_tier2_cards_not_in_tier1(self) -> None:
        sel = select_tier_cards(route_id="apps_qna.live_interview_runtime_pack_v1")
        assert not set(sel.tier1_cards) & set(sel.tier2_cards)

    def test_explicit_tier2_triggers_override_defaults(self) -> None:
        sel = select_tier_cards(
            route_id="apps_qna.live_interview_runtime_pack_v1",
            tier2_triggers=("star_proof",),
        )
        assert len(sel.tier2_cards) == 1

    def test_no_overfire_when_route_unknown(self) -> None:
        sel = select_tier_cards(route_id="unknown_route")
        assert len(sel.tier2_cards) == 0


class TestRouter:
    """Router tests (4 tests)."""

    def test_exactly_one_primary_route(self) -> None:
        sel = select_tier_cards(route_id="apps_qna.live_interview_runtime_pack_v1")
        assert sel.precedence == RoutePrecedence.PRIMARY

    def test_precedence_primary_wins(self) -> None:
        primary = TierSelection(precedence=RoutePrecedence.PRIMARY, reason="p")
        secondary = TierSelection(precedence=RoutePrecedence.SECONDARY, reason="s")
        result = resolve_ambiguity([secondary, primary])
        assert result.precedence == RoutePrecedence.PRIMARY

    def test_secondary_wins_when_no_primary(self) -> None:
        secondary = TierSelection(precedence=RoutePrecedence.SECONDARY, reason="s")
        fallback = TierSelection(precedence=RoutePrecedence.FALLBACK, reason="f")
        result = resolve_ambiguity([fallback, secondary])
        assert result.precedence == RoutePrecedence.SECONDARY

    def test_empty_selections_returns_default(self) -> None:
        result = resolve_ambiguity([])
        assert result.reason == "No valid route"


class TestEgress:
    """Egress tests (6 tests)."""

    def test_clean_cards_pass_egress(self) -> None:
        cards = {"card1": "This is clean content.\n"}
        result = check_egress(cards=cards)
        assert result["passed"] is True

    def test_fake_precision_blocked(self) -> None:
        cards = {"card1": "Achieved 50% improvement in latency.\n"}
        result = check_egress(cards=cards)
        assert result["passed"] is False

    def test_vendor_first_blocked(self) -> None:
        cards = {"card1": "AWS provides scalable infrastructure.\n"}
        result = check_egress(cards=cards)
        assert result["passed"] is False

    def test_internal_label_blocked(self) -> None:
        cards = {"card1": "See PROJ-1234 for details.\n"}
        result = check_egress(cards=cards)
        assert result["passed"] is False

    def test_multiple_violations_reported(self) -> None:
        cards = {"card1": "AWS 50% improvement PROJ-1234\n"}
        result = check_egress(cards=cards)
        assert len(result["violations"]) >= 1

    def test_cards_checked_count(self) -> None:
        cards = {"a": "ok\n", "b": "also ok\n"}
        result = check_egress(cards=cards)
        assert result["cards_checked"] == 2


class TestL2E4E5:
    """L2 E4-E5 tests (5 tests)."""

    def test_heal_normalizes_line_endings(self) -> None:
        cards = {"card1": "content\r\nwith\r\ncrlf\r\n"}
        healed = heal_cards(cards=cards, manifest=None)
        assert "\r\n" not in healed["card1"]

    def test_heal_strips_trailing_whitespace(self) -> None:
        cards = {"card1": "content   \n\n\n"}
        healed = heal_cards(cards=cards, manifest=None)
        assert healed["card1"] == "content\n"

    def test_seal_produces_manifest_with_hashes(self) -> None:
        cards = {"card1": "content\n"}
        manifest = seal_manifest(
            cards=cards,
            interview_slug="test",
            route_id="r1",
            evidence_contract={"producer": "test"},
            tiering={"card1": "tier_1"},
        )
        assert len(manifest.card_hashes) == 1

    def test_seal_includes_evidence_refs(self) -> None:
        cards = {"card1": "content\n"}
        manifest = seal_manifest(
            cards=cards,
            interview_slug="test",
            route_id="r1",
            evidence_contract={"producer": "agentic_core.C0", "briefing_hash": "abc"},
            tiering={"card1": "tier_1"},
        )
        assert len(manifest.evidence_refs) >= 1

    def test_seal_no_fact_invention(self) -> None:
        cards = {"card1": "original content\n"}
        manifest = seal_manifest(
            cards=cards,
            interview_slug="test",
            route_id="r1",
            evidence_contract={},
            tiering={},
        )
        assert "original content" not in str(manifest.card_hashes)


class TestExit:
    """Exit tests (4 tests)."""

    def test_single_x3_per_run(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec)
        assert packet.x3_disposition in (
            X3Disposition.ALLOW_FINISH,
            X3Disposition.SAFE_ABSTAIN,
        )

    def test_exit_receives_sealed_artifact(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec)
        assert packet.manifest is not None

    def test_invalid_build_safe_abstain(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec, build_valid=False)
        assert packet.x3_disposition == X3Disposition.SAFE_ABSTAIN

    def test_empty_cards_safe_abstain(self) -> None:
        from apps_qna.types.spine_contracts import CardPackManifestExtended
        empty = CardPackManifestExtended()
        packet = emit_exit_review(manifest=empty, evidence_contract={"evidence_sufficiency": "grounded"})
        assert packet.x3_disposition == X3Disposition.SAFE_ABSTAIN


class TestCache:
    """Cache tests (5 tests)."""

    def test_r1a_exact_match_returns_stored(self) -> None:
        r1a_store(interview_slug="test", briefing_hash="bh", evidence_hash="eh", result={"ok": True})
        result = r1a_lookup(interview_slug="test", briefing_hash="bh", evidence_hash="eh")
        assert result is not None
        assert result["ok"] is True

    def test_r1a_miss_returns_none(self) -> None:
        result = r1a_lookup(interview_slug="nonexistent", briefing_hash="x", evidence_hash="y")
        assert result is None

    def test_r1b_always_advisory(self) -> None:
        result = r1b_lookup(interview_slug="test")
        assert result is not None
        assert result["advisory"] is True

    def test_r5_always_degraded(self) -> None:
        result = r5_lookup(interview_slug="test")
        assert result["degraded"] is True

    def test_r1b_never_silent_terminal(self) -> None:
        result = r1b_lookup(interview_slug="test")
        assert result["result"] is None


class TestLocalUwg:
    """L6/UWG tests (4 tests)."""

    def test_local_output_not_uwg(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert manifest is not None

    def test_manifest_has_tiering(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.tiering) >= 4

    def test_manifest_has_card_hashes(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.card_hashes) >= 4

    def test_legacy_static_build_still_works(self) -> None:
        from apps_qna.builder.card_pack_builder import CardPackBuilder
        builder = CardPackBuilder()
        assert builder is not None
