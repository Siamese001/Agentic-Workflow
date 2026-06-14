"""Unit tests for agentic_core.L0_routing.c0_retrieval.final_contract.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 C0 output contract.
``final_contract`` (fan_in=14, L0_routing) defines FinalEvidenceContract — C0's
only output to Prompt Assembly — plus the sub-reports and sealing helpers. Hard
invariants: support_score in [0,1], status-coherence (BLOCKED/CONFLICTED/
WEAK_WITH_CAVEATS), C0.I11 no-answer denylist, and replay-metadata agreement.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.c0_retrieval.final_contract import (
    FORBIDDEN_CONTRACT_FIELDS,
    AclReport,
    BudgetReport,
    ContradictionFlagOut,
    FinalEvidenceContract,
    FreshnessReport,
    LineageEntry,
    PromptBudgetHint,
    ReplayMetadata,
    UnresolvedGapOut,
    compute_source_manifest_hash,
    seal_final_contract,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    EvidenceClass,
    GapType,
    RecommendedDisposition,
    SupportStatus,
)


def _contract(**overrides: object) -> FinalEvidenceContract:
    base: dict[str, object] = {"contract_id": "ct-1", "route_id": "R3"}
    base.update(overrides)
    return FinalEvidenceContract(**base)  # type: ignore[arg-type]


class TestForbiddenFields:
    def test_denylist_contents(self) -> None:
        for key in ("final_answer", "route_decision", "tool_call", "capability_token"):
            assert key in FORBIDDEN_CONTRACT_FIELDS

    def test_denylist_is_frozenset(self) -> None:
        assert isinstance(FORBIDDEN_CONTRACT_FIELDS, frozenset)


class TestSubReports:
    def test_acl_report_negative_blocked_count_raises(self) -> None:
        with pytest.raises(ValueError, match="blocked_sources_count must be >= 0"):
            AclReport(tenant_scope="t", blocked_sources_count=-1)

    def test_prompt_budget_hint_negative_max_raises(self) -> None:
        with pytest.raises(ValueError, match="max_context_tokens must be >= 0"):
            PromptBudgetHint(max_context_tokens=-1)

    def test_prompt_budget_hint_negative_estimate_raises(self) -> None:
        with pytest.raises(ValueError, match="estimated_context_tokens must be >= 0"):
            PromptBudgetHint(estimated_context_tokens=-1)

    def test_budget_report_negative_counter_raises(self) -> None:
        with pytest.raises(ValueError, match="counters must be non-negative"):
            BudgetReport(retrieval_passes=-1)

    def test_budget_report_negative_latency_raises(self) -> None:
        with pytest.raises(ValueError, match="latency/token counters"):
            BudgetReport(latency_ms=-5)

    def test_budget_report_defaults(self) -> None:
        b = BudgetReport()
        assert b.cost_tier_used == "standard"
        assert b.retrieval_passes == 0

    def test_freshness_report_defaults(self) -> None:
        fr = FreshnessReport(freshness_class="current")
        assert fr.stale_sources == ()

    def test_lineage_entry_defaults(self) -> None:
        le = LineageEntry(evidence_id="e1", found_by="dense")
        assert le.expanded_by == ""

    def test_contradiction_flag_defaults(self) -> None:
        cf = ContradictionFlagOut(type="version", source_a="a", source_b="b")
        assert cf.severity == "medium"
        assert cf.required_downstream_behavior == "caveat"

    def test_unresolved_gap_defaults(self) -> None:
        g = UnresolvedGapOut(gap_type=GapType.MISSING_DIRECT_SUPPORT)
        assert g.severity == "medium"


class TestFinalContractConstruction:
    def test_minimal_defaults(self) -> None:
        c = _contract()
        assert c.status is SupportStatus.EMPTY
        assert c.support_score == 0.0
        assert c.recommended_disposition is RecommendedDisposition.PROCEED
        assert c.must_use == ()
        assert c.extras == {}

    def test_construct_with_pass_status(self) -> None:
        c = _contract(status=SupportStatus.PASS, support_score=0.9)
        assert c.status is SupportStatus.PASS

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _contract().route_id = "R4"  # type: ignore[misc]


class TestFinalContractInvariants:
    @pytest.mark.parametrize("score", [-0.01, 1.01, 5.0])
    def test_support_score_out_of_range_raises(self, score: float) -> None:
        with pytest.raises(ValueError, match=r"support_score=.* must be in"):
            _contract(support_score=score)

    def test_blocked_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="BLOCKED contract must include blocked_reason"):
            _contract(status=SupportStatus.BLOCKED)

    def test_blocked_with_reason_ok(self) -> None:
        c = _contract(status=SupportStatus.BLOCKED, blocked_reason="G0 scope fail")
        assert c.blocked_reason == "G0 scope fail"

    def test_conflicted_without_flags_raises(self) -> None:
        with pytest.raises(ValueError, match="CONFLICTED contract must include contradiction_flags"):
            _contract(status=SupportStatus.CONFLICTED)

    def test_conflicted_with_flags_ok(self) -> None:
        flag = ContradictionFlagOut(type="version", source_a="a", source_b="b")
        c = _contract(status=SupportStatus.CONFLICTED, contradiction_flags=(flag,))
        assert len(c.contradiction_flags) == 1

    def test_weak_with_caveats_without_gaps_or_flags_raises(self) -> None:
        with pytest.raises(ValueError, match="WEAK_WITH_CAVEATS must surface"):
            _contract(status=SupportStatus.WEAK_WITH_CAVEATS)

    def test_weak_with_caveats_with_gap_ok(self) -> None:
        gap = UnresolvedGapOut(gap_type=GapType.MISSING_VALIDATION)
        c = _contract(status=SupportStatus.WEAK_WITH_CAVEATS, unresolved_gaps=(gap,))
        assert len(c.unresolved_gaps) == 1

    def test_replay_metadata_route_replay_key_drift_raises(self) -> None:
        rm = ReplayMetadata(route_replay_key="rrk-A")
        with pytest.raises(ValueError, match="route_replay_key drift"):
            _contract(route_replay_key="rrk-B", replay_metadata=rm)

    def test_replay_metadata_policy_hash_drift_raises(self) -> None:
        rm = ReplayMetadata(policy_hash="ph-A")
        with pytest.raises(ValueError, match="policy_hash drift"):
            _contract(policy_hash="ph-B", replay_metadata=rm)

    def test_extras_with_forbidden_key_raises(self) -> None:
        with pytest.raises(ValueError, match="C0 is read-only"):
            _contract(extras={"final_answer": "42"})


class TestByClass:
    def test_by_class_dispatch(self) -> None:
        c = _contract()
        assert c.by_class(EvidenceClass.MUST_USE) == c.must_use
        assert c.by_class(EvidenceClass.SUPPORTING) == c.supporting
        assert c.by_class(EvidenceClass.CONTRADICTS) == c.contradicts
        assert c.by_class(EvidenceClass.BACKGROUND) == c.background
        assert c.by_class(EvidenceClass.DEFINITIONS) == c.definitions

    def test_by_class_unmapped_returns_empty(self) -> None:
        assert _contract().by_class(EvidenceClass.EXCLUDED) == ()


class TestHashAndSeal:
    def test_hash_deterministic(self) -> None:
        c1 = _contract()
        c2 = _contract()
        assert c1.hash() == c2.hash()

    def test_hash_changes_with_content(self) -> None:
        assert _contract(support_score=0.1).hash() != _contract(support_score=0.2).hash()

    def test_seal_stamps_evidence_contract_hash(self) -> None:
        c = _contract()
        sealed = seal_final_contract(c)
        assert sealed.replay_metadata.evidence_contract_hash != ""
        assert sealed.replay_metadata.evidence_contract_hash == c.hash()

    def test_seal_idempotent(self) -> None:
        sealed = seal_final_contract(_contract())
        resealed = seal_final_contract(sealed)
        assert resealed.replay_metadata.evidence_contract_hash == (
            sealed.replay_metadata.evidence_contract_hash
        )


class TestComputeSourceManifestHash:
    def test_empty_input_returns_empty(self) -> None:
        assert compute_source_manifest_hash(()) == ""

    def test_order_and_dup_independent(self) -> None:
        a = compute_source_manifest_hash(("s2", "s1", "s1"))
        b = compute_source_manifest_hash(("s1", "s2"))
        assert a == b

    def test_distinct_inputs_differ(self) -> None:
        assert compute_source_manifest_hash(("s1",)) != compute_source_manifest_hash(("s2",))
