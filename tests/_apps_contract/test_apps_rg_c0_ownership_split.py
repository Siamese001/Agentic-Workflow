"""Hardened contract tests: apps_rg section C0 ownership split from agentic_core C0 builders.

Guards the architecture law:
- apps_rg owns resume section evidence room + FEC builder
- agentic_core owns contracts, GateVerdict law, FinalEvidenceContract shape
- no default core c0_retrieve merge on section lanes
"""

from __future__ import annotations

import ast
import inspect
import json
import os
from pathlib import Path
import pytest

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem
from apps_rg.runtime.bindings.c0_metrics_writer import _DEFAULT_SUPPORT_TARGET
from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff
from apps_rg.runtime.c0.c0_section_authority import (
    AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
    AUTHORITY_CLASS_SPINE_ENRICHMENT,
    C01_ARTIFACT,
    C02_ATOMS_ARTIFACT,
    C02_VECTOR_QUERY_ARTIFACT,
    NON_PROOF_CONTEXT_PREFIXES,
    bridge_authority_fields,
    proof_support_target,
    resolve_spine_chroma_enrich,
    section_chroma_write_in_c02,
)
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES

REPO = Path(__file__).resolve().parents[2]
EVIDENCE_ROOM = REPO / "apps_rg/runtime/c0/evidence_room.py"
C05_MODULE = REPO / "apps_rg/runtime/c0/c05_fec_packet.py"
RUNTIME_PROOF = REPO / "artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof"


def _module_ast(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _import_names(tree: ast.Module) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
    return out


class TestEvidenceRoomImportBoundary:
    """Section room must not import core C0 builders or fake C0.6."""

    def test_evidence_room_no_core_c0_retrieve_import(self) -> None:
        imports = _import_names(_module_ast(EVIDENCE_ROOM))
        assert "apps_rg.runtime.bindings.c0_binding" not in imports
        assert "agentic_core.runtime.c0.apps_rg_c0_binding" not in imports

    def test_evidence_room_no_c06_weak_refine_import(self) -> None:
        tree = _module_ast(EVIDENCE_ROOM)
        imports = _import_names(tree)
        assert "apps_rg.runtime.c0.c06_weak_refine" not in imports
        src = EVIDENCE_ROOM.read_text(encoding="utf-8")
        assert "maybe_c06_weak_refine" not in src

    def test_evidence_room_no_core_retrieval_plan_builder(self) -> None:
        imports = _import_names(_module_ast(EVIDENCE_ROOM))
        assert "agentic_core.runtime.c0.c0_package_driven_grounding" not in imports


class TestSpineEnrichDefaults:
    def test_default_off_without_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_SPINE_CHROMA_ENRICH", raising=False)
        assert resolve_spine_chroma_enrich() is False

    def test_env_enables_spine_enrich(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APPS_RG_SPINE_CHROMA_ENRICH", "1")
        assert resolve_spine_chroma_enrich() is True

    def test_merge_canonical_c0_legacy_alias(self) -> None:
        assert resolve_spine_chroma_enrich(merge_canonical_c0=True) is True
        assert resolve_spine_chroma_enrich(merge_canonical_c0=False) is False

    def test_c05_default_spine_enrich_false(self) -> None:
        sig = inspect.signature(build_c05_final_evidence_contract)
        assert sig.parameters["spine_chroma_enrich"].default is None
        assert sig.parameters["merge_canonical_c0"].default is None


class TestChromaPolicy:
    def test_write_and_enrich_mutually_exclusive_by_default(self) -> None:
        assert section_chroma_write_in_c02(spine_chroma_enrich=False) in (True, False)
        assert section_chroma_write_in_c02(spine_chroma_enrich=True) is False


class TestMetricsProofTarget:
    def test_support_target_excludes_non_proof_context(self) -> None:
        prefixes = proof_support_target().required_source_prefixes
        for bad in NON_PROOF_CONTEXT_PREFIXES:
            assert bad not in prefixes
        assert _DEFAULT_SUPPORT_TARGET.required_source_prefixes == prefixes

    def test_jd_resume_sources_do_not_satisfy_proof_target(self) -> None:
        from agentic_core.runtime.c0.evidence_metrics_extractor import extract_evidence_metrics
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract

        fec = FinalEvidenceContract(
            request_id="r",
            run_id="r",
            app_id="apps_rg",
            trace_id="r",
            evidence_items=(
                EvidenceItem(source="jd_payload:jd_text", content="jd"),
                EvidenceItem(source="resume_payload:resume_text", content="resume"),
            ),
            retrieval_sources=("jd_payload:jd_text", "resume_payload:resume_text"),
            support_target_met=False,
            l5_certification_ref="test",
        )
        metrics = extract_evidence_metrics(fec, proof_support_target())
        assert metrics.support_target_met is False


class TestC03SkillsGraphDisambiguation:
    def test_c03_flags_never_claim_core_graphrag(self) -> None:
        flags = expand_c03_graph_bindings(
            section_id="headline",
            atoms=[],
            role_family_key="",
            repo_root=REPO,
        )
        assert flags["schema_version"] == "c03_skills_graph_v1"
        assert flags["step_id"] == "C0.3_skills_graph"
        assert flags["apps_rg_c03_skills_graph_used"] is True
        assert flags["core_c03_graph_rag_used"] is False
        assert flags["canonical_c0_3_claimed"] is False


class TestC05Authority:
    def test_allowed_fact_ids_ssot(self) -> None:
        fec, receipt = build_c05_final_evidence_contract(
            section_id="competencies",
            atoms=[
                {
                    "fact_id": "allowed_1",
                    "text_to_embed": "Quantified platform outcome for insurer transformation.",
                    "source_type": "proof_pool",
                    "source_span_ref": "span:1",
                    "proof_status": "proof_eligible",
                },
                {
                    "fact_id": "blocked_2",
                    "text_to_embed": "Must not appear in FEC.",
                    "source_type": "proof_pool",
                    "source_span_ref": "span:2",
                    "proof_status": "proof_eligible",
                },
            ],
            strata={},
            graph_bindings=[],
            front_spine=None,
            allowed_fact_ids=["allowed_1"],
            spine_chroma_enrich=False,
        )
        assert receipt["section_fec_authority"] == "apps_rg_c0_evidence_room"
        assert receipt["spine_chroma_enrich"] is False
        assert receipt["merge_canonical_c0"] is False
        assert all(getattr(i, "authority_class", "") == AUTHORITY_CLASS_LEDGER_GRAPH_PROOF for i in fec.evidence_items)
        assert all(getattr(i, "source_id", "") == "allowed_1" for i in fec.evidence_items)

    def test_default_does_not_call_spine_c0_retrieve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.c0 import c05_fec_packet as c05_mod

        def _boom(*_a: object, **_k: object) -> None:
            raise AssertionError("c0_retrieve_apps_rg must not run when spine_chroma_enrich=False")

        monkeypatch.setattr(c05_mod, "c0_retrieve_apps_rg", _boom)
        build_c05_final_evidence_contract(
            section_id="headline",
            atoms=[],
            strata={},
            graph_bindings=[],
            front_spine=object(),
            allowed_fact_ids=[],
            spine_chroma_enrich=False,
        )

    def test_spine_enrich_marks_non_authoritative(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.c0 import c05_fec_packet as c05_mod

        spine_item = EvidenceItem(
            source="chromadb:fact_vectors:chunk-1",
            content="enrichment only",
            source_id="chunk-1",
            source_type="chromadb",
        )

        class _SpineFec:
            evidence_items = (spine_item,)

        class _Spine:
            route = object()
            validated_request = object()

        monkeypatch.setattr(c05_mod, "c0_retrieve_apps_rg", lambda *_a, **_k: _SpineFec())
        fec, receipt = build_c05_final_evidence_contract(
            section_id="headline",
            atoms=[],
            strata={},
            graph_bindings=[],
            front_spine=_Spine(),
            allowed_fact_ids=[],
            spine_chroma_enrich=True,
        )
        assert receipt["spine_enrichment_item_count"] == 1
        assert fec.evidence_items[0].authority_class == AUTHORITY_CLASS_SPINE_ENRICHMENT

    def test_spine_item_in_allowed_set_not_admitted_as_proof(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.c0 import c05_fec_packet as c05_mod

        spine_item = EvidenceItem(
            source="chromadb:fact_vectors:chunk-1",
            content="enrichment only",
            source_id="allowed_1",
            source_type="chromadb",
        )

        class _SpineFec:
            evidence_items = (spine_item,)

        class _Spine:
            route = object()
            validated_request = object()

        monkeypatch.setattr(c05_mod, "c0_retrieve_apps_rg", lambda *_a, **_k: _SpineFec())
        fec, receipt = build_c05_final_evidence_contract(
            section_id="headline",
            atoms=[],
            strata={},
            graph_bindings=[],
            front_spine=_Spine(),
            allowed_fact_ids=["allowed_1"],
            spine_chroma_enrich=True,
        )
        assert receipt["spine_enrichment_item_count"] == 0
        assert not fec.evidence_items


class TestC07Handoff:
    def test_rejects_proof_outside_allowed_fact_ids(self) -> None:
        fec, c05 = build_c05_final_evidence_contract(
            section_id="competencies",
            atoms=[
                {
                    "fact_id": "f1",
                    "text_to_embed": "claim text with enough length for ingest rules.",
                    "source_type": "proof_pool",
                    "source_span_ref": "s",
                    "proof_status": "proof_eligible",
                }
            ],
            strata={},
            graph_bindings=[],
            front_spine=None,
            allowed_fact_ids=["f1"],
            spine_chroma_enrich=False,
        )
        # Simulate stray item (should not happen if C0.5 is correct — guard either way)
        stray = EvidenceItem(
            source="fact:stray",
            content="stray",
            source_id="stray",
            authority_class=AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
        )
        from dataclasses import replace

        fec_bad = replace(fec, evidence_items=(*fec.evidence_items, stray))
        c07 = audit_c07_handoff(
            fec=fec_bad,
            c02_receipt={"graph_inference_performed": False},
            c03_receipt={
                "new_atoms_created": 0,
                "pending_trace_promoted": False,
                "core_c03_graph_rag_used": False,
            },
            graph_bindings=[],
            allowed_fact_ids=["f1"],
            c05_receipt=c05,
        )
        assert c07["handoff_safe"] is False
        assert any("proof_not_in_allowed_fact_ids" in v for v in c07["violations"])

    def test_adjacency_as_proof_violation(self) -> None:
        fec, c05 = build_c05_final_evidence_contract(
            section_id="competencies",
            atoms=[
                {
                    "fact_id": "f1",
                    "text_to_embed": "claim",
                    "source_type": "proof_pool",
                    "source_span_ref": "s",
                    "proof_status": "proof_eligible",
                }
            ],
            strata={},
            graph_bindings=[],
            front_spine=None,
            allowed_fact_ids=["f1"],
            spine_chroma_enrich=False,
        )
        c07 = audit_c07_handoff(
            fec=fec,
            c02_receipt={"graph_inference_performed": False},
            c03_receipt={"new_atoms_created": 0, "pending_trace_promoted": False},
            graph_bindings=[
                {
                    "fact_id": "f1",
                    "graph_support_strength": "ADJACENT_ONLY",
                    "claim_support_allowed": True,
                }
            ],
            allowed_fact_ids=["f1"],
            c05_receipt=c05,
        )
        assert c07["handoff_safe"] is False


class TestBridgeAuthorityFields:
    def test_ledger_graph_primary_default_bridge(self) -> None:
        fields = bridge_authority_fields(spine_chroma_enrich=False)
        assert fields["c0_authority_mode"] == "ledger_graph_primary"
        assert fields["spine_chroma_enrich"] is False
        assert fields["jd_targeting_only"] is True


class TestArtifactNames:
    def test_c0_artifact_names_ssot(self) -> None:
        assert C01_ARTIFACT == "c01_retrieval_plan.json"
        assert C02_ATOMS_ARTIFACT == "c02_atoms.json"
        assert C02_VECTOR_QUERY_ARTIFACT == "c02_vector_query.json"


class TestForbiddenProofSources:
    def test_jd_in_forbidden_set(self) -> None:
        assert "jd_payload" in FORBIDDEN_PROOF_SOURCE_TYPES


@pytest.mark.skipif(not RUNTIME_PROOF.is_dir(), reason="headline runtime proof dir missing")
class TestRuntimeProofArtifacts:
    """Pin runtime receipts from canonical CLI proof run (when present)."""

    def test_headline_runtime_c0_ownership_receipts(self) -> None:
        bridge = json.loads(
            (RUNTIME_PROOF / "final_evidence_contract_bridge.json").read_text(encoding="utf-8")
        )
        assert bridge.get("spine_chroma_enrich") is False
        assert bridge.get("canonical_c0_3_claimed") is False
        assert bridge.get("apps_rg_c03_skills_graph_used") is True
        assert bridge.get("c0_authority_mode") == "ledger_graph_primary"
        assert (RUNTIME_PROOF / C01_ARTIFACT).is_file()
        assert (RUNTIME_PROOF / C02_ATOMS_ARTIFACT).is_file()
        assert (RUNTIME_PROOF / C02_VECTOR_QUERY_ARTIFACT).is_file()

        metrics = json.loads((RUNTIME_PROOF / "c0_metrics.json").read_text(encoding="utf-8"))
        for bad in ("jd_payload", "resume_payload"):
            assert bad not in str(metrics.get("retrieval_sources") or [])
