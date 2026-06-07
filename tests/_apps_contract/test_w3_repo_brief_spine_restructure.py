"""
P3.14 — W3 Governance Contract Tests for apps_repo_brief spine restructure.

44 tests covering:
- P3.3  IngestionEngine retirement guard
- P3.4  C0 adapter + C0 request spec
- P3.5  BriefAssemblyEngine split notices
- P3.6  StyleGate split notices
- P3.7  RepoBriefFinalEvidenceContract.v1 schema
- P3.8  PA compiler full slot rendering
- P3.9  C0 depth profiles (graduated thresholds — AG P3.1 Option A)
- P3.10 BriefingCoverageMatrix schema
- P3.11 SourcePortfolio, ClaimEvidenceMap, ContradictionMatrix, FreshnessReport schemas
- P3.12 Board gate config
- P3.13 Cache strict compat enforcement
- Regression: W2 tests still pass (spot-checks)

Plan: docs/archive/windsurf/legacy-tree/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.14
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APP_ROOT = _REPO_ROOT / "apps_repo_brief"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(rel: str) -> dict[str, Any]:
    p = _APP_ROOT / rel
    assert p.exists(), f"Missing file: {p}"
    with open(p, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), f"Expected dict at {p}"
    return data


# ---------------------------------------------------------------------------
# P3.3 — IngestionEngine retirement
# ---------------------------------------------------------------------------

class TestIngestionRetirement:
    def test_retirement_guards_module_exists(self) -> None:
        p = _APP_ROOT / "engines" / "retirement_guards.py"
        assert p.exists(), "retirement_guards.py must exist"

    def test_retirement_reason_string_present(self) -> None:
        import apps_repo_brief.engines.retirement_guards as m
        assert hasattr(m, "_RETIREMENT_REASON")
        assert "repo_brief_docs" in m._RETIREMENT_REASON

    def test_ingestion_engine_retired_raises(self) -> None:
        from apps_repo_brief.engines.retirement_guards import ingestion_engine_retired
        with pytest.raises(RuntimeError, match="IngestionEngine"):
            ingestion_engine_retired()

    def test_engines_init_mentions_all_retired_engines(self) -> None:
        p = _APP_ROOT / "engines" / "__init__.py"
        content = p.read_text(encoding="utf-8")
        assert "IngestionEngine" in content
        assert "CapabilityExtractionEngine" in content
        assert "BriefAssemblyEngine" in content


# ---------------------------------------------------------------------------
# P3.4 — C0 adapter
# ---------------------------------------------------------------------------

class TestC0Adapter:
    def test_c0_adapter_import(self) -> None:
        from apps_repo_brief.c0 import RepoBriefC0Adapter
        assert RepoBriefC0Adapter is not None

    def test_build_c0_request_standard_profile(self) -> None:
        from apps_repo_brief.c0 import RepoBriefC0Adapter
        adapter = RepoBriefC0Adapter()
        spec = adapter.build_c0_request({
            "depth_profile": "REPO_BRIEF_STANDARD",
            "audience": "cto",
            "emphasis_areas": ["governance"],
            "persona_schema_version": "v1",
            "policy_hash": "abc123",
            "blueprint_hash": "def456",
            "repo_snapshot_id": "snap1",
            "replay_key": "rk1",
            "trace_id": "t1",
            "normalized_request_hash": "h1",
        })
        assert spec.retrieval_surface_id == "repo_brief_docs"
        assert spec.depth_profile.value == "REPO_BRIEF_STANDARD"
        assert "bm25_exact_phrase" in spec.retrieval_lanes
        assert spec.depth_thresholds["min_sources"] == 10

    def test_build_c0_request_board_profile(self) -> None:
        from apps_repo_brief.c0 import RepoBriefC0Adapter
        adapter = RepoBriefC0Adapter()
        spec = adapter.build_c0_request({"depth_profile": "REPO_BRIEF_BOARD_DOSSIER"})
        assert spec.depth_thresholds["min_sources"] == 30
        assert spec.depth_thresholds["auth_governance_anchor_required"] is True
        assert spec.depth_thresholds["semantic_cache_terminal_return"] is False

    def test_c0_retrieval_lanes_count(self) -> None:
        from apps_repo_brief.c0.repo_brief_c0_adapter import C0_RETRIEVAL_LANES
        assert len(C0_RETRIEVAL_LANES) == 7

    def test_c0_adapter_invalid_profile_falls_back_to_standard(self) -> None:
        from apps_repo_brief.c0 import RepoBriefC0Adapter
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        adapter = RepoBriefC0Adapter()
        spec = adapter.build_c0_request({"depth_profile": "INVALID_PROFILE"})
        assert spec.depth_profile == DepthProfile.REPO_BRIEF_STANDARD


# ---------------------------------------------------------------------------
# P3.5 + P3.6 — Spine restructure notices
# ---------------------------------------------------------------------------

class TestSpineRestructureNotices:
    def test_brief_assembly_engine_retired_raises(self) -> None:
        from apps_repo_brief.engines.retirement_guards import brief_assembly_engine_retired
        with pytest.raises(RuntimeError, match="BriefAssemblyEngine"):
            brief_assembly_engine_retired()

    def test_style_gate_validator_retired_raises(self) -> None:
        from apps_repo_brief.engines.retirement_guards import style_gate_validator_retired
        with pytest.raises(RuntimeError, match="StyleGateValidator"):
            style_gate_validator_retired()

    def test_brief_assembly_split_owner(self) -> None:
        from apps_repo_brief.engines.retirement_guards import BRIEF_ASSEMBLY_ENGINE_OWNER
        assert "PA" in BRIEF_ASSEMBLY_ENGINE_OWNER
        assert "L2" in BRIEF_ASSEMBLY_ENGINE_OWNER

    def test_style_gate_split_owner(self) -> None:
        from apps_repo_brief.engines.retirement_guards import STYLE_GATE_VALIDATOR_OWNER
        assert "L2.E4" in STYLE_GATE_VALIDATOR_OWNER
        assert "Exit" in STYLE_GATE_VALIDATOR_OWNER


# ---------------------------------------------------------------------------
# P3.7 — RepoBriefFinalEvidenceContract.v1
# ---------------------------------------------------------------------------

class TestFinalEvidenceContract:
    def test_fec_import(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        assert RepoBriefFinalEvidenceContract is not None

    def test_fec_schema_version(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        fec = RepoBriefFinalEvidenceContract()
        assert fec.schema_version == "apps_repo_brief.FinalEvidenceContract/v1"

    def test_fec_authoritative_always_true(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        fec = RepoBriefFinalEvidenceContract()
        assert fec.authoritative is True

    def test_fec_retrieval_surface(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        fec = RepoBriefFinalEvidenceContract()
        assert fec.retrieval_surface_id == "repo_brief_docs"

    def test_fec_is_grounded_pass(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        from apps_repo_brief.c0.repo_brief_final_contract import EvidenceStatus
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.PASS)
        assert fec.is_grounded() is True

    def test_fec_is_grounded_missing(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        from apps_repo_brief.c0.repo_brief_final_contract import EvidenceStatus
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.MISSING)
        assert fec.is_grounded() is False

    def test_fec_requires_abstain_when_missing(self) -> None:
        from apps_repo_brief.c0 import RepoBriefFinalEvidenceContract
        from apps_repo_brief.c0.repo_brief_final_contract import EvidenceStatus
        fec = RepoBriefFinalEvidenceContract(evidence_status=EvidenceStatus.MISSING)
        assert fec.requires_abstain() is True


# ---------------------------------------------------------------------------
# P3.8 — PA compiler full slot rendering
# ---------------------------------------------------------------------------

class TestPACompilerFullRendering:
    def test_pa_compiler_import(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        assert RepoBriefPACompiler is not None

    def test_pa_compiler_loads(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        compiler.load()
        assert compiler._loaded is True

    def test_list_templates(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        templates = compiler.list_templates()
        assert len(templates) >= 3
        assert "repo_brief_synthesis_v1" in templates

    @staticmethod
    def _full_evidence_bundle() -> dict[str, Any]:
        return {
            "normalized_repo_brief_task": {"task_id": "t1"},
            "FinalEvidenceContract": {"contract_type": "apps_repo_brief.FinalEvidenceContract.v1"},
            "BriefingCoverageMatrix": {"briefing_profile_id": "bpm1"},
            "ClaimEvidenceMap": {"map_id": "cem1"},
            "SourcePortfolioSummary": {"surface_id": "rbd"},
            "ContradictionMatrix": {"matrix_id": "cm1"},
            "FreshnessReport": {"report_id": "fr1"},
            "SynthesisGuidanceForPA": {
                "caveat_injection_policy": "inline",
                "gap_handling": "omit",
                "unsupported_claim_policy": "caveat_required",
                "weak_claim_policy": "caveat_required",
                "stale_source_policy": "caveat",
            },
            "repo_brief_depth_profile": "REPO_BRIEF_STANDARD",
            "audience_schema_ref": "cto_v1",
            "output_schema_ref": "governed_repo_brief_packet_v1",
            "policy_hash": "ph1",
            "blueprint_hash": "bh1",
            "replay_key": "rk1",
        }

    def test_no_scaffold_stub_in_compiled_output(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        compiler.load()
        evidence_bundle = self._full_evidence_bundle()
        artifact = compiler.compile(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=evidence_bundle,
            request_id="req1",
            run_id="run1",
            trace_id="t1",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="repo_brief",
            policy_hash="ph1",
            blueprint_hash="bh1",
            replay_key="rk1",
        )
        # No scaffold stub in rendered slots
        for slot_id, body in artifact["rendered_slots"].items():
            assert "full rendering in W3" not in body, (
                f"Slot {slot_id!r} still contains W2 scaffold stub"
            )
        # No _scaffold_w2 flag
        assert "_scaffold_w2" not in artifact

    def test_compiled_artifact_has_required_fields(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        evidence_bundle = self._full_evidence_bundle()
        artifact = compiler.compile(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=evidence_bundle,
            request_id="r1", run_id="ru1", trace_id="t1",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="repo_brief",
            policy_hash="ph", blueprint_hash="bh", replay_key="rk",
        )
        for field in [
            "artifact_id", "manifest_hash", "rendered_slots",
            "canonical_slot_bytes_hash", "artifact_hash",
            "provider_lane", "output_schema_ref",
        ]:
            assert field in artifact, f"Missing field: {field}"

    def test_token_substitution(self) -> None:
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        result = compiler._substitute_tokens(
            "Hello {{NAME}}, status={{STATUS}}",
            {"NAME": "World", "STATUS": "PASS"},
        )
        assert result == "Hello World, status=PASS"

    def test_unresolved_token_preserved(self) -> None:
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        result = compiler._substitute_tokens(
            "Hello {{UNKNOWN_KEY}}",
            {"OTHER_KEY": "val"},
        )
        assert "{{UNKNOWN_KEY}}" in result

    def test_caveat_injected_for_weak_evidence(self) -> None:
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        result = compiler._inject_caveat("Some claim text.", "WEAK")
        assert "[Caveat:" in result
        assert "WEAK" in result

    def test_gap_abstain_policy(self) -> None:
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        result = compiler._render_single_slot(
            slot_id="S0",
            body_def=None,
            evidence_value=None,
            evidence_bundle={},
            caveat_policy="caveat_required",
            gap_handling="abstain",
            required=True,
        )
        assert "ABSTAIN" in result

    def test_optional_slot_absent_from_bundle_omitted(self) -> None:
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        template = {
            "required_slots": ["S0"],
            "optional_slots": ["O0"],
            "slot_bodies": {"S0": "Body for S0"},
        }
        rendered = compiler._render_slots(template, {"S0": "evidence_val"})
        assert "O0" not in rendered
        assert "S0" in rendered


# ---------------------------------------------------------------------------
# P3.9 — C0 depth profiles (AG P3.1 Option A)
# ---------------------------------------------------------------------------

class TestC0DepthProfiles:
    def test_depth_profiles_yaml_exists(self) -> None:
        p = _APP_ROOT / "config" / "c0_depth_profiles.yaml"
        assert p.exists()

    def test_all_four_profiles_present(self) -> None:
        data = _load_yaml("config/c0_depth_profiles.yaml")
        profiles = data.get("profiles", {})
        for name in ["REPO_BRIEF_LIGHT", "REPO_BRIEF_STANDARD", "REPO_BRIEF_DEEP", "REPO_BRIEF_BOARD_DOSSIER"]:
            assert name in profiles, f"Missing profile: {name}"

    def test_graduated_thresholds_increasing_min_sources(self) -> None:
        data = _load_yaml("config/c0_depth_profiles.yaml")
        profiles = data["profiles"]
        light = profiles["REPO_BRIEF_LIGHT"]["min_sources"]
        standard = profiles["REPO_BRIEF_STANDARD"]["min_sources"]
        deep = profiles["REPO_BRIEF_DEEP"]["min_sources"]
        board = profiles["REPO_BRIEF_BOARD_DOSSIER"]["min_sources"]
        assert light < standard < deep < board, (
            f"Expected graduated min_sources: {light} < {standard} < {deep} < {board}"
        )

    def test_board_dossier_requires_auth_anchor(self) -> None:
        data = _load_yaml("config/c0_depth_profiles.yaml")
        board = data["profiles"]["REPO_BRIEF_BOARD_DOSSIER"]
        assert board["auth_governance_anchor_required"] is True

    def test_board_dossier_stale_policy_is_block(self) -> None:
        data = _load_yaml("config/c0_depth_profiles.yaml")
        board = data["profiles"]["REPO_BRIEF_BOARD_DOSSIER"]
        assert board["stale_source_policy"] == "block"

    def test_light_stale_policy_is_caveat(self) -> None:
        data = _load_yaml("config/c0_depth_profiles.yaml")
        light = data["profiles"]["REPO_BRIEF_LIGHT"]
        assert light["stale_source_policy"] == "caveat"

    def test_python_constants_match_yaml(self) -> None:
        from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS
        from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
        data = _load_yaml("config/c0_depth_profiles.yaml")
        profiles = data["profiles"]
        assert (
            DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_LIGHT]["min_sources"]
            == profiles["REPO_BRIEF_LIGHT"]["min_sources"]
        )
        assert (
            DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_BOARD_DOSSIER]["min_sources"]
            == profiles["REPO_BRIEF_BOARD_DOSSIER"]["min_sources"]
        )


# ---------------------------------------------------------------------------
# P3.10 — BriefingCoverageMatrix schema
# ---------------------------------------------------------------------------

class TestBriefingCoverageMatrix:
    def test_import(self) -> None:
        from apps_repo_brief.c0 import BriefingCoverageMatrix
        assert BriefingCoverageMatrix is not None

    def test_selected_section_ids(self) -> None:
        from apps_repo_brief.c0 import BriefingCoverageMatrix
        from apps_repo_brief.c0.repo_brief_final_contract import (
            DepthProfile, EvidenceStatus, SectionCoverage,
        )
        bcm = BriefingCoverageMatrix(
            depth_profile=DepthProfile.REPO_BRIEF_STANDARD,
            audience="cto",
            sections=[
                SectionCoverage("sec_a", True, EvidenceStatus.PASS, 5, 80.0, False),
                SectionCoverage("sec_b", False, EvidenceStatus.MISSING, 0, 0.0, True),
            ],
        )
        assert bcm.selected_section_ids() == ["sec_a"]


# ---------------------------------------------------------------------------
# P3.11 — SourcePortfolio, ClaimEvidenceMap, ContradictionMatrix, FreshnessReport
# ---------------------------------------------------------------------------

class TestP311Schemas:
    def test_source_portfolio_import(self) -> None:
        from apps_repo_brief.c0 import SourcePortfolioSummary
        sp = SourcePortfolioSummary(
            total_sources=15,
            by_source_type={"adr": 5, "test_file": 10},
            authority_distribution={"high": 5, "medium": 8, "low": 2},
            stale_count=1,
            freshness_window_days=90,
        )
        assert sp.total_sources == 15

    def test_claim_evidence_map_get_entry(self) -> None:
        from apps_repo_brief.c0 import ClaimEvidenceMap
        from apps_repo_brief.c0.repo_brief_final_contract import ClaimEvidenceEntry, EvidenceStatus
        cem = ClaimEvidenceMap(
            entries=[
                ClaimEvidenceEntry("c1", "Claim text", EvidenceStatus.PASS, ["s1"], False)
            ]
        )
        entry = cem.get_entry("c1")
        assert entry is not None
        assert entry.status == EvidenceStatus.PASS
        assert cem.get_entry("missing") is None

    def test_contradiction_matrix_has_critical(self) -> None:
        from apps_repo_brief.c0 import ContradictionMatrix
        from apps_repo_brief.c0.repo_brief_final_contract import ContradictionEntry
        cm = ContradictionMatrix(
            entries=[ContradictionEntry("x1", "a", "b", "omit_both", True)],
            has_critical=True,
        )
        assert cm.has_critical is True

    def test_freshness_report_fields(self) -> None:
        from apps_repo_brief.c0 import FreshnessReport
        fr = FreshnessReport(
            stale_sources=["s1", "s2"],
            freshness_caveats={"s1": "old ADR"},
            max_age_days=180,
            policy_freshness_window_days=90,
        )
        assert len(fr.stale_sources) == 2


# ---------------------------------------------------------------------------
# P3.12 — Board gate config
# ---------------------------------------------------------------------------

class TestBoardGateConfig:
    def test_board_gates_yaml_exists(self) -> None:
        p = _APP_ROOT / "config" / "c0_board_gates.yaml"
        assert p.exists()

    def test_applies_to_board_dossier_only(self) -> None:
        data = _load_yaml("config/c0_board_gates.yaml")
        applies = data.get("applies_to_profiles", [])
        assert "REPO_BRIEF_BOARD_DOSSIER" in applies

    def test_required_gates_present(self) -> None:
        data = _load_yaml("config/c0_board_gates.yaml")
        gates = data.get("gates", {})
        for gate_name in [
            "section_coverage", "auth_governance_anchor", "stale_source",
            "critical_contradiction", "cache_terminal_return",
            "min_sources", "min_citation_anchors",
        ]:
            assert gate_name in gates, f"Missing board gate: {gate_name}"

    def test_section_coverage_threshold(self) -> None:
        data = _load_yaml("config/c0_board_gates.yaml")
        threshold = data["gates"]["section_coverage"]["threshold_pct"]
        assert threshold == 95.0

    def test_r1b_terminal_return_forbidden(self) -> None:
        data = _load_yaml("config/c0_board_gates.yaml")
        allowed = data["gates"]["cache_terminal_return"]["semantic_cache_terminal_return_allowed"]
        assert allowed is False

    def test_board_gate_thresholds_dataclass(self) -> None:
        from apps_repo_brief.c0.repo_brief_final_contract import BoardGateThresholds
        t = BoardGateThresholds()
        assert t.min_section_coverage_pct == 95.0
        assert t.auth_governance_anchor_required is True
        assert t.critical_contradiction_policy == "escalate_hitl"


# ---------------------------------------------------------------------------
# P3.13 — Cache strict compat enforcement
# ---------------------------------------------------------------------------

class TestCacheCompatEnforcement:
    def test_cache_compat_enforcement_import(self) -> None:
        from apps_repo_brief.c0.cache_compat_enforcement import (
            CacheCompatViolation,
            enforce_r1a_strict_compat,
            enforce_r1b_semantic_cache_policy,
        )
        assert CacheCompatViolation is not None

    def test_r1b_board_dossier_terminal_return_raises(self) -> None:
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1b_semantic_cache_policy, CacheCompatViolation,
        )
        with pytest.raises(CacheCompatViolation, match="BOARD_DOSSIER"):
            enforce_r1b_semantic_cache_policy(
                depth_profile="REPO_BRIEF_BOARD_DOSSIER",
                is_terminal_return=True,
            )

    def test_r1b_board_dossier_non_terminal_allowed(self) -> None:
        from apps_repo_brief.c0.cache_compat_enforcement import enforce_r1b_semantic_cache_policy
        # Should not raise
        enforce_r1b_semantic_cache_policy(
            depth_profile="REPO_BRIEF_BOARD_DOSSIER",
            is_terminal_return=False,
        )

    def test_r1b_standard_terminal_return_allowed(self) -> None:
        from apps_repo_brief.c0.cache_compat_enforcement import enforce_r1b_semantic_cache_policy
        # Should not raise
        enforce_r1b_semantic_cache_policy(
            depth_profile="REPO_BRIEF_STANDARD",
            is_terminal_return=True,
        )

    def test_r1a_missing_required_fields_raises(self) -> None:
        from apps_repo_brief.c0.cache_compat_enforcement import (
            enforce_r1a_strict_compat, CacheCompatViolation,
        )
        with pytest.raises(CacheCompatViolation, match="missing required key fields"):
            enforce_r1a_strict_compat(
                candidate_key={"partial_key": "only"},
                depth_profile="REPO_BRIEF_STANDARD",
            )


# ---------------------------------------------------------------------------
# Regression: W2 spot-checks
# ---------------------------------------------------------------------------

class TestW2Regression:
    def test_pa_compiler_still_loads(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        c = RepoBriefPACompiler()
        c.load()
        assert c._loaded

    def test_prompt_bom_still_has_required_slots(self) -> None:
        data = _load_yaml("prompt_assembly/prompt_bom.yaml")
        slots_raw = data.get("slots", {})
        # slots may be a dict {slot_id: {...}} or a list [{slot_id: ...}]
        if isinstance(slots_raw, dict):
            slot_ids = set(slots_raw.keys())
        else:
            slot_ids = {s["slot_id"] for s in slots_raw}
        assert "S0" in slot_ids
        assert "I0" in slot_ids

    def test_observability_adapter_canonical_namespace(self) -> None:
        p = _APP_ROOT / "integrations" / "observability_adapter.py"
        content = p.read_text(encoding="utf-8")
        assert "apps_repo_brief" in content
        assert "apps_exec" in content
