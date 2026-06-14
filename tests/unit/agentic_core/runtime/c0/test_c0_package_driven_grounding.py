"""Unit tests for agentic_core.runtime.c0.c0_package_driven_grounding.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core C0 binding
(fan_in P2, L_RUNTIME). App-agnostic grounding builder. Covers the pure/deterministic
surface: enum membership, frozen evidence dataclasses + defaults, the digest helper's
determinism, and the report builders (source register, claim map, freshness,
contradiction, support-status) that operate on plain EvidenceItems with no live IO.
The top-level ``c0_ground_package_driven`` orchestrator needs a constructed RouteContract
(__post_init__ requires a valid l5_certification_ref) + YAML/graph-rag IO and is out of
this pure-surface scope.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.c0.c0_package_driven_grounding import (
    ClaimEvidenceMapping,
    ContradictionReport,
    DataBoundaryLabel,
    EvidenceItem,
    EvidenceSupportStatus,
    FreshnessReport,
    SourceRegisterEntry,
    _compute_digest,
    c0_build_claim_evidence_map,
    c0_build_contradiction_report,
    c0_build_freshness_report,
    c0_build_source_register,
    c0_compute_support_status,
)


def _evidence(
    evidence_id: str = "ev-1",
    *,
    freshness_status: str = "FRESH",
    source_ref: str = "src-1",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_ref=source_ref,
        content_snippet="snippet",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
        freshness_status=freshness_status,
        support_status="PASS",
        citation_info={"source_url": "https://example.com", "inline": "[1]"},
    )


class TestEnums:
    def test_support_status_members(self) -> None:
        assert {s.value for s in EvidenceSupportStatus} == {
            "EMPTY",
            "WEAK_INSUFFICIENT",
            "WEAK_WITH_CAVEATS",
            "PASS",
            "STRONG",
            "CONFLICTED",
        }

    def test_data_boundary_members(self) -> None:
        assert {d.value for d in DataBoundaryLabel} == {
            "EVIDENCE_DATA_ONLY",
            "INSTRUCTION_SPACE",
        }


class TestEvidenceItem:
    def test_defaults(self) -> None:
        item = _evidence()
        assert item.data_boundary_label == "EVIDENCE_DATA_ONLY"
        assert item.claim_extractions == []
        assert item.confidence_score == 0.0
        assert item.contradiction_flags == []

    def test_frozen(self) -> None:
        item = _evidence()
        with pytest.raises(dataclasses.FrozenInstanceError):
            item.evidence_id = "mutated"  # type: ignore[misc]


class TestComputeDigest:
    def test_determinism_same_input_same_digest(self) -> None:
        payload = {"a": 1, "b": ["x", "y"]}
        assert _compute_digest(payload) == _compute_digest(payload)

    def test_digest_length_is_16(self) -> None:
        assert len(_compute_digest("anything")) == 16

    def test_different_input_different_digest(self) -> None:
        assert _compute_digest("alpha") != _compute_digest("beta")


class TestSourceRegister:
    def test_one_entry_per_evidence_item(self) -> None:
        items = [_evidence("ev-1", source_ref="src-1"), _evidence("ev-2", source_ref="src-2")]
        register = c0_build_source_register(items, {})
        assert len(register) == 2
        assert all(isinstance(e, SourceRegisterEntry) for e in register)
        assert {e.source_id for e in register} == {"src-1", "src-2"}

    def test_empty_input_empty_register(self) -> None:
        assert c0_build_source_register([], {}) == []

    def test_source_url_pulled_from_citation_info(self) -> None:
        entry = c0_build_source_register([_evidence()], {})[0]
        assert entry.source_url == "https://example.com"


class TestClaimEvidenceMap:
    def test_one_mapping_per_evidence_item(self) -> None:
        items = [_evidence("ev-1"), _evidence("ev-2")]
        mappings = c0_build_claim_evidence_map(items, {})
        assert len(mappings) == 2
        assert all(isinstance(m, ClaimEvidenceMapping) for m in mappings)

    def test_claim_ids_zero_padded_and_ordered(self) -> None:
        mappings = c0_build_claim_evidence_map([_evidence("ev-1"), _evidence("ev-2")], {})
        assert [m.claim_id for m in mappings] == ["claim-000", "claim-001"]

    def test_supporting_refs_point_at_evidence(self) -> None:
        mapping = c0_build_claim_evidence_map([_evidence("ev-1")], {})[0]
        assert mapping.supporting_evidence_refs == ["ev-1"]
        assert mapping.contradicting_evidence_refs == []


class TestFreshnessReport:
    def test_counts_fresh_and_stale(self) -> None:
        items = [
            _evidence("ev-1", freshness_status="FRESH"),
            _evidence("ev-2", freshness_status="STALE"),
            _evidence("ev-3", freshness_status="FRESH"),
        ]
        report = c0_build_freshness_report(items, {})
        assert isinstance(report, FreshnessReport)
        assert report.sources_checked == 3
        assert report.sources_fresh == 2
        assert report.sources_stale == 1

    def test_empty_input_zero_counts(self) -> None:
        report = c0_build_freshness_report([], {})
        assert report.sources_checked == 0
        assert report.sources_fresh == 0
        assert report.sources_stale == 0


class TestContradictionReport:
    def test_no_contradictions_low_materiality(self) -> None:
        items = [_evidence("ev-1")]
        cmap = c0_build_claim_evidence_map(items, {})
        report = c0_build_contradiction_report(items, cmap, {})
        assert isinstance(report, ContradictionReport)
        assert report.contradictions_detected == 0
        assert report.materiality_assessment == "LOW"

    def test_contradicting_refs_raise_materiality(self) -> None:
        items = [_evidence("ev-1")]
        cmap = [
            ClaimEvidenceMapping(
                claim_id="claim-000",
                claim_text="t",
                claim_type="factual",
                supporting_evidence_refs=["ev-1"],
                contradicting_evidence_refs=["ev-9"],
                confidence_assessment="PASS",
                materiality_flag=True,
            )
        ]
        report = c0_build_contradiction_report(items, cmap, {})
        assert report.contradictions_detected == 1
        assert report.materiality_assessment == "HIGH"


class TestComputeSupportStatus:
    def test_empty_evidence_returns_empty_status(self) -> None:
        status, score, profile = c0_compute_support_status(
            [], [], c0_build_freshness_report([], {}), c0_build_contradiction_report([], [], {}), {}
        )
        assert status == EvidenceSupportStatus.EMPTY.value
        assert score == 0.0
        assert profile == {}

    @pytest.mark.parametrize(
        "n_items,expected_status",
        [
            (1, EvidenceSupportStatus.WEAK_INSUFFICIENT.value),  # score=10 < weak_max=30
            (3, EvidenceSupportStatus.WEAK_WITH_CAVEATS.value),  # score=30 -> weak_max band
            (7, EvidenceSupportStatus.PASS.value),               # score=70 -> pass_min
            (9, EvidenceSupportStatus.STRONG.value),             # score=90 -> strong_min
        ],
    )
    def test_score_bands_with_default_thresholds(self, n_items: int, expected_status: str) -> None:
        items = [_evidence(f"ev-{i}") for i in range(n_items)]
        freshness = c0_build_freshness_report(items, {})
        cmap = c0_build_claim_evidence_map(items, {})
        contra = c0_build_contradiction_report(items, cmap, {})
        status, score, profile = c0_compute_support_status(
            items, c0_build_source_register(items, {}), freshness, contra, {}
        )
        assert status == expected_status
        assert profile["evidence_count"] == n_items

    def test_contradictions_force_conflicted_status(self) -> None:
        items = [_evidence("ev-1")]
        contra = ContradictionReport(
            contradictions_detected=2,
            contradiction_details=[],
            resolution_recommendations=[],
            materiality_assessment="HIGH",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        status, score, _ = c0_compute_support_status(
            items, c0_build_source_register(items, {}), c0_build_freshness_report(items, {}), contra, {}
        )
        assert status == EvidenceSupportStatus.CONFLICTED.value
        assert score >= 0  # score floored at 0
