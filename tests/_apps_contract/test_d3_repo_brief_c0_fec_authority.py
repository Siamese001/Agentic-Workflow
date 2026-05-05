"""
D3 — apps_repo_brief C0 authoritative FEC binding + C0→PA→Exit handoff
     integration tests.

Covers §20.2 gates:
  #3  apps_repo_brief aligned to C0 briefing-grade repo retrieval standard
  #6  Authoritative FEC at C0 (cert_projection_adapter is READ-ONLY; fec_producer retired)

Deferred scope item closed:
  DS-1  C0 authoritative FEC binding (highest priority)

Plan: .windsurf/plans/apps-repo-brief-plan3-deferred-scope-b9e4c1.md D3
"""

from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fec(
    depth_profile: str = "REPO_BRIEF_STANDARD",
    evidence_status: str = "PASS",
    total_sources: int = 12,
    overall_coverage_pct: float = 80.0,
    stale_sources: list[str] | None = None,
    board_gate_passed: bool | None = None,
    authoritative: bool = True,
) -> Any:
    from apps_repo_brief.c0.repo_brief_final_contract import (
        RepoBriefFinalEvidenceContract,
        DepthProfile,
        EvidenceStatus,
        SourcePortfolioSummary,
        BriefingCoverageMatrix,
        FreshnessReport,
    )
    sp = SourcePortfolioSummary(
        total_sources=total_sources,
        by_source_type={"architecture_doc": total_sources},
        authority_distribution={"high": total_sources},
        stale_count=len(stale_sources or []),
        freshness_window_days=90,
    )
    bcm = BriefingCoverageMatrix(
        depth_profile=DepthProfile(depth_profile),
        audience="cto",
        overall_coverage_pct=overall_coverage_pct,
        meets_depth_floor=overall_coverage_pct >= 75.0,
    )
    fr = FreshnessReport(
        stale_sources=stale_sources or [],
        freshness_caveats={},
        max_age_days=30,
        policy_freshness_window_days=90,
    )
    return RepoBriefFinalEvidenceContract(
        depth_profile=DepthProfile(depth_profile),
        evidence_status=EvidenceStatus(evidence_status),
        source_portfolio=sp,
        briefing_coverage_matrix=bcm,
        freshness_report=fr,
        board_gate_passed=board_gate_passed,
        authoritative=authoritative,
    )


# ---------------------------------------------------------------------------
# Gate #6 — Authoritative FEC at C0 (cert_projection_adapter is READ-ONLY)
# ---------------------------------------------------------------------------

class TestFECAuthorityAtC0:
    """
    Gate #6: The authoritative FEC is minted by C0, not by cert tools.

    - RepoBriefFinalEvidenceContract.authoritative=True by default.
    - CertProjectionAdapter.project() is READ-ONLY — it never sets authoritative.
    - fec_producer.produce_fec() is retired — logs a WARNING and returns a
      legacy-shape dict, never a RepoBriefFinalEvidenceContract.
    - The legacy produce_fec() output is DISTINCT from the C0 FEC type.
    """

    def test_fec_authoritative_default_is_true(self) -> None:
        """RepoBriefFinalEvidenceContract.authoritative must default to True."""
        from apps_repo_brief.c0.repo_brief_final_contract import RepoBriefFinalEvidenceContract
        fec = RepoBriefFinalEvidenceContract()
        assert fec.authoritative is True, (
            "FEC.authoritative must default to True — only C0 mints the FEC"
        )

    def test_validate_fec_fails_if_authoritative_false(self) -> None:
        """validate_fec must flag FEC where authoritative=False (non-C0 mint)."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(authoritative=False)
        adapter = RepoBriefC0Adapter()
        violations = adapter.validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        assert any("authoritative" in v for v in violations), (
            f"Expected authoritative violation, got: {violations}"
        )

    def test_validate_fec_passes_authoritative_true(self) -> None:
        """validate_fec must NOT flag FEC where authoritative=True."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(authoritative=True)
        adapter = RepoBriefC0Adapter()
        violations = adapter.validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        auth_violations = [v for v in violations if "authoritative" in v]
        assert not auth_violations, f"Unexpected authoritative violations: {auth_violations}"

    def test_cert_projection_adapter_is_read_only(self) -> None:
        """
        CertProjectionAdapter.project() must not set or modify FEC fields.
        The returned CertProjection is a read-only view, not a new FEC mint.
        """
        from apps_repo_brief.cert.cert_projection_adapter import (
            CertProjectionAdapter,
            CertProjection,
        )
        fec_dict: dict[str, Any] = {
            "schema_version": "apps_repo_brief.FinalEvidenceContract/v1",
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": "repo_brief_docs",
            "evidence_status": "PASS",
            "depth_profile": "REPO_BRIEF_STANDARD",
        }
        adapter = CertProjectionAdapter()
        projection = adapter.project(fec_dict)

        # Must return CertProjection, not a new FEC
        assert isinstance(projection, CertProjection)
        # Must not contain an 'authoritative' field (not a FEC)
        assert not hasattr(projection, "authoritative"), (
            "CertProjection must not carry FEC.authoritative — it is a projection, not a mint"
        )
        # Original dict must be unmodified
        assert "authoritative" not in fec_dict, "project() must not mutate the input dict"

    def test_cert_projection_adapter_does_not_accept_fec_dataclass(self) -> None:
        """
        CertProjectionAdapter.project() expects a dict, not a FEC dataclass.
        Passing a non-dict must raise ValueError (type guard).
        """
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        adapter = CertProjectionAdapter()
        fec_obj = _make_fec()
        with pytest.raises(ValueError, match="expects a dict"):
            adapter.project(fec_obj)  # type: ignore[arg-type]

    def test_fec_producer_is_retired_logs_warning(self, caplog: Any) -> None:
        """
        fec_producer.produce_fec() is retired — must log a WARNING containing
        'RETIRED'. It still returns a legacy dict (graceful degradation),
        but callers must switch to CertProjectionAdapter.
        """
        import logging
        from apps_repo_brief.cert.fec_producer import produce_fec, _FEC_PRODUCER_RETIRED
        with caplog.at_level(logging.WARNING, logger="apps_repo_brief.cert.fec_producer"):
            result = produce_fec({})
        assert any("RETIRED" in r.message for r in caplog.records), (
            "produce_fec() must log a WARNING containing 'RETIRED'"
        )
        # Returns legacy-shape dict, not RepoBriefFinalEvidenceContract
        assert isinstance(result, dict)
        assert result.get("schema_version") == "1.0"

    def test_fec_producer_output_distinct_from_c0_fec_type(self) -> None:
        """
        The legacy produce_fec() output shape is DISTINCT from
        RepoBriefFinalEvidenceContract — not interchangeable.
        """
        from apps_repo_brief.cert.fec_producer import produce_fec
        from apps_repo_brief.c0.repo_brief_final_contract import RepoBriefFinalEvidenceContract
        result = produce_fec({"c0_retrieval_sources": ["src_001"]})
        assert not isinstance(result, RepoBriefFinalEvidenceContract), (
            "Legacy produce_fec() must not return a RepoBriefFinalEvidenceContract instance"
        )
        # Legacy shape: schema_version="1.0" (not the C0 schema)
        assert result["schema_version"] == "1.0"
        assert "apps_repo_brief.FinalEvidenceContract" not in result["schema_version"]

    def test_cert_projection_validates_retrieval_surface(self) -> None:
        """validate_projection must warn when retrieval_surface_id != 'repo_brief_docs'."""
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        wrong_surface: dict[str, Any] = {
            "schema_version": "apps_repo_brief.FinalEvidenceContract/v1",
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": "wrong_surface",
            "evidence_status": "PASS",
            "depth_profile": "REPO_BRIEF_STANDARD",
        }
        adapter = CertProjectionAdapter()
        projection = adapter.project(wrong_surface)
        warnings = adapter.validate_projection(projection)
        assert any("retrieval_surface_id" in w for w in warnings), (
            f"Expected retrieval_surface_id warning, got: {warnings}"
        )

    def test_cert_projection_unknown_evidence_status_warns(self) -> None:
        """validate_projection must warn when evidence_status=UNKNOWN."""
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        fec_dict: dict[str, Any] = {
            "schema_version": "apps_repo_brief.FinalEvidenceContract/v1",
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": "repo_brief_docs",
            # evidence_status absent → defaults to UNKNOWN
            "depth_profile": "REPO_BRIEF_STANDARD",
        }
        adapter = CertProjectionAdapter()
        projection = adapter.project(fec_dict)
        warnings = adapter.validate_projection(projection)
        assert any("UNKNOWN" in w for w in warnings), (
            f"Expected UNKNOWN warning, got: {warnings}"
        )


# ---------------------------------------------------------------------------
# Gate #3 — C0 briefing-grade repo retrieval standard
# ---------------------------------------------------------------------------

class TestC0BriefingGradeStandard:
    """
    Gate #3: apps_repo_brief aligned to C0 briefing-grade repo retrieval standard.

    - C0Adapter.build_c0_request uses all 7 canonical retrieval lanes.
    - Depth profiles enforce minimum source counts and coverage floors.
    - validate_fec enforces stale-source block policy for DEEP/BOARD.
    - FEC→CertProjection coherence: is_grounded/requires_abstain align.
    """

    _REQUIRED_LANES = {
        "bm25_exact_phrase",
        "dense_semantic",
        "metadata",
        "graph",
        "code_symbol",
        "proof",
        "prior_artifact",
    }

    def test_c0_adapter_uses_all_seven_lanes(self) -> None:
        """build_c0_request must include all 7 canonical C0 retrieval lanes."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        adapter = RepoBriefC0Adapter()
        spec = adapter.build_c0_request({
            "depth_profile": "REPO_BRIEF_STANDARD",
            "audience": "cto",
            "emphasis_areas": [],
            "persona_schema_version": "v1",
            "policy_hash": "ph",
            "blueprint_hash": "bph",
            "repo_snapshot_id": "snap_001",
            "replay_key": "rk",
            "trace_id": "tr",
            "normalized_request_hash": "nh",
        })
        missing = self._REQUIRED_LANES - set(spec.retrieval_lanes)
        assert not missing, f"C0RequestSpec missing retrieval lanes: {missing}"

    def test_c0_adapter_retrieval_surface_is_repo_brief_docs(self) -> None:
        """C0RequestSpec must target retrieval_surface_id='repo_brief_docs'."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        spec = RepoBriefC0Adapter().build_c0_request({"depth_profile": "REPO_BRIEF_LIGHT"})
        assert spec.retrieval_surface_id == "repo_brief_docs"

    def test_c0_adapter_depth_profile_defaults_to_standard(self) -> None:
        """Unknown depth_profile must fall back to REPO_BRIEF_STANDARD."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        spec = RepoBriefC0Adapter().build_c0_request({"depth_profile": "NONEXISTENT_PROFILE"})
        assert spec.depth_profile == DepthProfile.REPO_BRIEF_STANDARD

    def test_standard_profile_min_sources_threshold(self) -> None:
        """validate_fec must flag STANDARD FEC when total_sources < 10."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(depth_profile="REPO_BRIEF_STANDARD", total_sources=5)
        violations = RepoBriefC0Adapter().validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        assert any("total_sources" in v for v in violations), (
            f"Expected source count violation, got: {violations}"
        )

    def test_standard_profile_passes_min_sources(self) -> None:
        """validate_fec must NOT flag STANDARD FEC when total_sources >= 10."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(depth_profile="REPO_BRIEF_STANDARD", total_sources=10)
        violations = RepoBriefC0Adapter().validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        source_violations = [v for v in violations if "total_sources" in v]
        assert not source_violations, f"Unexpected source violations: {source_violations}"

    def test_deep_profile_stale_source_block_policy(self) -> None:
        """DEEP profile must block when stale sources are present (stale_source_policy=block)."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(
            depth_profile="REPO_BRIEF_DEEP",
            total_sources=25,
            overall_coverage_pct=90.0,
            stale_sources=["stale_doc_001"],
        )
        violations = RepoBriefC0Adapter().validate_fec(fec, DepthProfile.REPO_BRIEF_DEEP)
        assert any("stale" in v.lower() for v in violations), (
            f"DEEP profile must block stale sources. Got: {violations}"
        )

    def test_standard_profile_stale_caveat_not_block(self) -> None:
        """STANDARD profile must NOT block stale sources (policy=caveat, not block)."""
        from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        fec = _make_fec(
            depth_profile="REPO_BRIEF_STANDARD",
            total_sources=10,
            stale_sources=["stale_doc_001"],
        )
        violations = RepoBriefC0Adapter().validate_fec(fec, DepthProfile.REPO_BRIEF_STANDARD)
        stale_violations = [v for v in violations if "stale" in v.lower()]
        assert not stale_violations, (
            f"STANDARD profile must not block stale sources: {stale_violations}"
        )

    def test_all_four_depth_profiles_have_thresholds(self) -> None:
        """All four DepthProfile enum values must be in DEPTH_PROFILE_THRESHOLDS."""
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        for dp in DepthProfile:
            assert dp in DEPTH_PROFILE_THRESHOLDS, (
                f"DepthProfile.{dp.name} missing from DEPTH_PROFILE_THRESHOLDS"
            )

    def test_depth_profile_thresholds_have_required_keys(self) -> None:
        """Every depth profile threshold dict must declare the required keys."""
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        required_keys = {"min_sources", "min_coverage_pct", "min_citation_anchors",
                         "stale_source_policy", "board_gate_required",
                         "semantic_cache_terminal_return"}
        for dp, thresholds in DEPTH_PROFILE_THRESHOLDS.items():
            missing = required_keys - set(thresholds.keys())
            assert not missing, (
                f"DepthProfile.{dp.name} thresholds missing keys: {missing}"
            )


# ---------------------------------------------------------------------------
# D3.2 — C0→CertProjection→ExitV6 handoff integration (gate #3 + #6)
# ---------------------------------------------------------------------------

class TestC0ToExitHandoffIntegration:
    """
    End-to-end coherence: FEC (C0) → CertProjection (adapter) → ExitV6 (gate).

    Verifies that the three-stage handoff maintains evidence semantics
    without any stage minting a new authoritative FEC.
    """

    def _fec_to_dict(self, fec: Any) -> dict[str, Any]:
        """Serialize a RepoBriefFinalEvidenceContract to a dict for CertProjectionAdapter."""
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
        )
        assert isinstance(fec, RepoBriefFinalEvidenceContract)
        return {
            "schema_version": fec.schema_version,
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": fec.retrieval_surface_id,
            "evidence_status": fec.evidence_status.value,
            "depth_profile": fec.depth_profile.value,
            "board_gate_passed": fec.board_gate_passed,
            "freshness_report": {
                "stale_sources": (
                    fec.freshness_report.stale_sources if fec.freshness_report else []
                )
            },
        }

    def test_pass_fec_projects_to_grounded_true(self) -> None:
        """FEC with evidence_status=PASS → CertProjection.is_grounded=True."""
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        fec = _make_fec(evidence_status="PASS")
        projection = CertProjectionAdapter().project(self._fec_to_dict(fec))
        assert projection.is_grounded is True
        assert projection.requires_abstain is False

    def test_missing_fec_projects_to_requires_abstain_true(self) -> None:
        """FEC with evidence_status=MISSING → CertProjection.requires_abstain=True."""
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        fec = _make_fec(evidence_status="MISSING")
        projection = CertProjectionAdapter().project(self._fec_to_dict(fec))
        assert projection.requires_abstain is True
        assert projection.is_grounded is False

    def test_exit_citation_integrity_blocks_below_minimum(self) -> None:
        """Exit citation check must BLOCK when citation count < profile minimum."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        # STANDARD requires ≥ 8 citations — provide only 3
        rendered_slots = {
            "S0": "No [src:doc_1] no extra [src:doc_2] and [src:doc_3].",
        }
        checker = ExitV6Checker()
        result = checker.check_citation_integrity(rendered_slots, "REPO_BRIEF_STANDARD")
        assert result.x3_triggered is True, (
            f"Expected BLOCK, got {result.verdict}: {result.detail}"
        )

    def test_exit_citation_integrity_passes_at_minimum(self) -> None:
        """Exit citation check must PASS when citation count meets profile minimum."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        # LIGHT requires ≥ 3 citations
        anchors = " ".join(f"[src:doc_{i}]" for i in range(4))
        rendered_slots = {"S0": anchors}
        checker = ExitV6Checker()
        result = checker.check_citation_integrity(rendered_slots, "REPO_BRIEF_LIGHT")
        assert result.x3_triggered is False, (
            f"Expected PASS, got {result.verdict}: {result.detail}"
        )

    def test_exit_board_readiness_skips_non_board_profiles(self) -> None:
        """Board readiness check must SKIP for non-BOARD_DOSSIER profiles."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker, ExitCheckVerdict
        result = ExitV6Checker().check_board_readiness({}, "REPO_BRIEF_STANDARD")
        assert result.verdict == ExitCheckVerdict.SKIP

    def test_exit_board_readiness_blocks_low_coverage(self) -> None:
        """Board readiness check must BLOCK when E5 coverage_pct < 95%."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        receipt = {
            "e5": {"coverage_pct": 80.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "PASS"},
        }
        result = ExitV6Checker().check_board_readiness(receipt, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered is True, (
            f"Expected BLOCK on low coverage, got {result.verdict}: {result.detail}"
        )

    def test_exit_board_readiness_passes_at_full_coverage(self) -> None:
        """Board readiness check must PASS when all E5/E4/E1 conditions met."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        receipt = {
            "e5": {"coverage_pct": 96.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "PASS"},
        }
        result = ExitV6Checker().check_board_readiness(receipt, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered is False, (
            f"Expected PASS, got {result.verdict}: {result.detail}"
        )

    def test_exit_board_readiness_blocks_on_missing_evidence_status(self) -> None:
        """Board readiness check must BLOCK when E1 evidence_status is MISSING."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        receipt = {
            "e5": {"coverage_pct": 96.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "MISSING"},
        }
        result = ExitV6Checker().check_board_readiness(receipt, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered is True

    def test_exit_board_readiness_blocks_on_escalated_slots(self) -> None:
        """Board readiness check must BLOCK when E4 has unresolved style escalations."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        receipt = {
            "e5": {"coverage_pct": 96.0},
            "e4": {"escalated_slot_ids": ["S0", "I0"]},
            "e1": {"evidence_status": "PASS"},
        }
        result = ExitV6Checker().check_board_readiness(receipt, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered is True

    def test_exit_check_result_to_dict_shape(self) -> None:
        """ExitV6CheckResult.to_dict() must include all required fields."""
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker
        checker = ExitV6Checker()
        result = checker.check_citation_integrity(
            {"S0": "[src:doc_1] [src:doc_2] [src:doc_3] [src:doc_4]"},
            "REPO_BRIEF_LIGHT",
        )
        d = result.to_dict()
        required = {"check_name", "verdict", "detail", "metrics", "x3_triggered"}
        assert required <= set(d.keys()), f"to_dict() missing keys: {required - set(d.keys())}"

    def test_full_pipeline_fec_to_exit_coherent(self) -> None:
        """
        Full coherence test: C0 FEC (PASS, STANDARD, 12 sources)
          → CertProjection (is_grounded=True)
          → ExitV6 citation check (8 anchors, STANDARD → PASS)

        No stage mints a new FEC. End result is ExitCheckVerdict.PASS.
        """
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        from apps_repo_brief.exit.exit_v6_checks import ExitV6Checker, ExitCheckVerdict

        # Stage 1: C0 produces FEC (simulated via dataclass)
        fec = _make_fec(
            depth_profile="REPO_BRIEF_STANDARD",
            evidence_status="PASS",
            total_sources=12,
            overall_coverage_pct=80.0,
        )
        assert fec.authoritative is True, "FEC must be authoritative (C0-minted)"

        # Stage 2: CertProjectionAdapter projects FEC → CertProjection (READ-ONLY)
        fec_dict = {
            "schema_version": fec.schema_version,
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": fec.retrieval_surface_id,
            "evidence_status": fec.evidence_status.value,
            "depth_profile": fec.depth_profile.value,
        }
        projection = CertProjectionAdapter().project(fec_dict)
        assert projection.is_grounded is True, "PASS FEC must project to is_grounded=True"
        assert projection.requires_abstain is False

        # Stage 3: ExitV6 citation integrity (8 anchors for STANDARD ≥ 8)
        rendered = {"C0": " ".join(f"[src:doc_{i}]" for i in range(8))}
        exit_result = ExitV6Checker().check_citation_integrity(
            rendered, "REPO_BRIEF_STANDARD"
        )
        assert exit_result.verdict == ExitCheckVerdict.PASS, (
            f"Expected PASS, got {exit_result.verdict}: {exit_result.detail}"
        )
        assert exit_result.x3_triggered is False
