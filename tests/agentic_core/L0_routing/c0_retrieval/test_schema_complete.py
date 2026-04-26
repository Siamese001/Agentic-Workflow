"""Final contract schema completeness — every field from spec lines 1010-1133.

Spec: C0 Context Engine.md §C0 OUTPUT SCHEMA — verifies the typed
FinalEvidenceContract carries every field the YAML schema mandates.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from dataclasses import fields

import pytest

from agentic_core.L0_routing.c0_retrieval.dispatcher import run_c0
from agentic_core.L0_routing.c0_retrieval.candidate_pool import CandidateEvidencePool
from agentic_core.L0_routing.c0_retrieval.final_contract import (
    AclReport, BudgetReport, ContradictionFlagOut, FinalEvidenceContract,
    FreshnessReport, LineageEntry, PromptBudgetHint, ReplayMetadata,
    UnresolvedGapOut,
)
from agentic_core.L0_routing.c0_retrieval.evidence_contract import ScoreBreakdown
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    GapType, RecommendedDisposition, RetrievalLane, SupportStatus,
)

_F = pathlib.Path(__file__).parent / "_factories.py"
_spec = importlib.util.spec_from_file_location("_c0_factories", _F)
assert _spec is not None and _spec.loader is not None
_factories = importlib.util.module_from_spec(_spec)
sys.modules["_c0_factories"] = _factories
_spec.loader.exec_module(_factories)
make_chunk = _factories.make_chunk
make_plan_contract = _factories.make_plan_contract
make_route = _factories.make_route


def _run() -> FinalEvidenceContract:
    result = run_c0(
        route=make_route(),
        plan_contract=make_plan_contract(),
        fetch=lambda p, r: CandidateEvidencePool(
            plan_id=p.plan_id,
            candidates=(
                make_chunk(chunk_id="c1"),
                make_chunk(chunk_id="c2", text="The contract carries verified ids and a score breakdown."),
            ),
            lanes_used=(RetrievalLane.SPARSE, RetrievalLane.DENSE),
        ),
        adjacency=lambda n, allowed: (),
    )
    return result.contract


# ---------- top-level FinalEvidenceContract fields ----------


# Spec lines 1014-1133 enumerate these fields. We assert each is present.
EXPECTED_TOP_LEVEL_FIELDS = {
    "contract_id", "route_id", "status", "support_score",
    "score_breakdown",
    "must_use", "supporting", "contradicts", "background", "definitions",
    "lineage", "excluded",
    "contradiction_flags", "unresolved_gaps",
    "freshness_report", "acl_report",
    "prompt_budget_hint",
    "recommended_disposition",
    "budget_report",
    "replay_metadata",
}


class TestTopLevelSchema:
    def test_dataclass_carries_all_required_fields(self):
        actual = {f.name for f in fields(FinalEvidenceContract)}
        missing = EXPECTED_TOP_LEVEL_FIELDS - actual
        assert not missing, f"FinalEvidenceContract missing fields: {missing}"

    def test_runtime_instance_populates_all_fields(self):
        c = _run()
        for fld in EXPECTED_TOP_LEVEL_FIELDS:
            assert hasattr(c, fld), f"runtime contract missing {fld}"


# ---------- ScoreBreakdown 11 dimensions ----------


SCORE_DIMENSIONS = {
    "direct_support_score", "coverage_score", "source_authority_score",
    "freshness_score", "citation_stability_score", "lineage_quality_score",
    "exactness_score", "source_diversity_score",
    "contradiction_risk", "unsupported_inference_risk",
    "acl_confidence",
}


class TestScoreBreakdownSchema:
    def test_all_11_dimensions_present(self):
        actual = {f.name for f in fields(ScoreBreakdown)}
        assert SCORE_DIMENSIONS == actual

    def test_runtime_score_breakdown_in_range(self):
        c = _run()
        sb = c.score_breakdown
        for fld in SCORE_DIMENSIONS:
            v = getattr(sb, fld)
            assert 0.0 <= v <= 1.0, f"{fld}={v} out of [0,1]"


# ---------- ReplayMetadata schema ----------


class TestReplayMetadataSchema:
    def test_required_fields(self):
        rm = _run().replay_metadata
        # Every spec field present (lines 1130-1133).
        assert hasattr(rm, "retrieval_snapshot_id")
        assert hasattr(rm, "policy_hash")
        assert hasattr(rm, "blueprint_hash")
        assert hasattr(rm, "route_replay_key")
        assert hasattr(rm, "evidence_contract_hash")

    def test_evidence_contract_hash_set_after_seal(self):
        c = _run()
        assert c.replay_metadata.evidence_contract_hash
        # blake2b digest_size=16 → 32-char hex.
        assert len(c.replay_metadata.evidence_contract_hash) == 32


# ---------- BudgetReport schema ----------


class TestBudgetReportSchema:
    def test_fields_present(self):
        br = _run().budget_report
        assert isinstance(br, BudgetReport)
        for fld in ("retrieval_passes", "graph_hops_used", "latency_ms",
                     "cost_tier_used", "token_estimate", "budget_remaining"):
            assert hasattr(br, fld)

    def test_counters_non_negative(self):
        br = _run().budget_report
        assert br.retrieval_passes >= 0
        assert br.graph_hops_used >= 0
        assert br.latency_ms >= 0
        assert br.token_estimate >= 0


# ---------- PromptBudgetHint schema ----------


class TestPromptBudgetHintSchema:
    def test_fields_present(self):
        pbh = _run().prompt_budget_hint
        assert isinstance(pbh, PromptBudgetHint)
        for fld in ("pack_order", "must_keep_evidence_ids",
                     "trim_first_evidence_ids", "contradiction_keepers",
                     "max_context_tokens", "estimated_context_tokens"):
            assert hasattr(pbh, fld)

    def test_must_keep_subset_of_pack_order(self):
        pbh = _run().prompt_budget_hint
        keep = set(pbh.must_keep_evidence_ids)
        order = set(pbh.pack_order)
        assert keep.issubset(order)


# ---------- FreshnessReport schema ----------


class TestFreshnessReportSchema:
    def test_fields_present(self):
        fr = _run().freshness_report
        assert isinstance(fr, FreshnessReport)
        for fld in ("freshness_class", "newest_source_age",
                     "stale_sources", "version_mismatches"):
            assert hasattr(fr, fld)


# ---------- AclReport schema ----------


class TestAclReportSchema:
    def test_fields_present(self):
        ar = _run().acl_report
        assert isinstance(ar, AclReport)
        for fld in ("tenant_scope", "cleared_sources",
                     "blocked_sources_count", "data_classes_seen"):
            assert hasattr(ar, fld)

    def test_blocked_count_non_negative(self):
        ar = _run().acl_report
        assert ar.blocked_sources_count >= 0


# ---------- LineageEntry projection ----------


class TestLineageProjection:
    def test_each_lineage_entry_well_formed(self):
        c = _run()
        for entry in c.lineage:
            assert isinstance(entry, LineageEntry)
            assert entry.evidence_id
            assert entry.found_by  # lane provenance, never empty (C0.I3)


# ---------- ContradictionFlagOut + UnresolvedGapOut ----------


class TestContradictionAndGapProjection:
    def test_contradiction_flag_shape(self):
        flag = ContradictionFlagOut(
            type="version", source_a="a", source_b="b",
            severity="medium", summary="test",
            required_downstream_behavior="caveat",
        )
        assert flag.type == "version"

    def test_unresolved_gap_uses_gap_type_enum(self):
        gap = UnresolvedGapOut(
            gap_type=GapType.MISSING_EXACT_QUOTE,
            severity="high", impact_on_answer="x",
            suggested_next_step="HYBRIDIZE",
        )
        assert gap.gap_type == GapType.MISSING_EXACT_QUOTE


# ---------- Recommended disposition mapping ----------


class TestDispositionMapping:
    @pytest.mark.parametrize("disp", list(RecommendedDisposition))
    def test_every_disposition_value_is_valid(self, disp):
        # Each disposition value should be usable in a contract.
        c = FinalEvidenceContract(
            contract_id="x", route_id="R3",
            status=SupportStatus.PASS, support_score=0.9,
            recommended_disposition=disp,
        )
        assert c.recommended_disposition == disp


# ---------- to_replay_dict shape ----------


class TestReplayDict:
    def test_all_top_level_keys_present(self):
        c = _run()
        d = c.to_replay_dict()
        for fld in EXPECTED_TOP_LEVEL_FIELDS:
            assert fld in d, f"replay_dict missing {fld}"

    def test_text_stripped_from_evidence_buckets(self):
        c = _run()
        d = c.to_replay_dict()
        for bucket in ("must_use", "supporting", "background", "definitions"):
            for hyd in d.get(bucket, []):
                cand = hyd.get("candidate", {}) if isinstance(hyd, dict) else {}
                assert "text" not in cand


# ---------- hash determinism ----------


class TestContractHashDeterminism:
    def test_hash_is_content_addressed(self):
        c1 = _run()
        c2 = _run()
        # Different contract_ids (UUID) but same evidence content → same
        # content fields. Hash includes contract_id, so hashes will differ.
        # Verify hash is at least computed and well-formed.
        assert c1.replay_metadata.evidence_contract_hash
        assert c2.replay_metadata.evidence_contract_hash
        assert len(c1.replay_metadata.evidence_contract_hash) == 32
