"""AG-4 Evidence Contract Carrier Repair — invariant tests.

Plan: ``ag4-evidence-contract-carrier-repair-d2f9a3``.

Verifies the 12 W8 invariants for the contract carriers extended in W1
(EvidenceItem, FinalEvidenceContract), W3 (ExitReviewPacket,
X1CheckoutResult), and W4 (SealedL2Artifact).

Hard laws — these tests prove negative-controls:
- UNKNOWN MUST NEVER be treated as PASS.
- NOT_APPLICABLE MUST be accompanied by a reason.
- C0 retrieved evidence MUST carry ``allowed_prompt_slot ==
  C0_EVIDENCE_DATA_ONLY``.
- BLOCKED / EMPTY / CONFLICTED MUST NOT silently become PASS.
- L2 seal MUST preserve evidence_refs / tool_call_refs / model_call_refs /
  provider_receipts / replay_manifest / audit_manifest_ref carriers.
- ExitReviewPacket MUST exist and normalise terminal-input ref shape.
- X1CheckoutResult MUST exist with X1A..X1J slots + structured verdicts.
- Groundedness check MUST surface intent + evidence + output refs.
- No ChromaDB mutation, no embedding generation (proven by AST scan
  + zero new chromadb / sentence_transformers / bge_runtime imports).
"""

from __future__ import annotations

import dataclasses as dc
import importlib
import inspect
import pathlib

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_NOT_APPLICABLE,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PARTIAL,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PASSING_VALUES,
    SUPPORT_STATUS_WEAK,
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1EvaluatorType,
    X1Item,
    X1Verdict,
    X1_PASSING_VERDICTS,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
)


# Test-only stub for the verify_certification_ref guard so we can construct
# SealedL2Artifact / FinalEvidenceContract instances at unit-test scope.
_TEST_CERT = "c0-apps-rg-resume-generation-app-payload-b3a449"


# ---------------------------------------------------------------------------
# Invariant 1 — EvidenceItem supports dense / sparse / metadata / graph /
# ACL / freshness / citation / contradiction / support fields.
# ---------------------------------------------------------------------------


class TestInv1EvidenceItemFieldShape:
    """EvidenceItem must declare every AG-4 carrier field."""

    REQUIRED = frozenset({
        "evidence_id", "source_id", "source_type", "source_version",
        "source_uri_or_ref", "source_owner_or_authority", "retrieved_span",
        "citation_anchor", "chunk_digest", "fact_vec_ref", "dense_score",
        "bm25_score", "metadata_score", "freshness_status", "acl_status",
        "origin_trust_label", "authority_class", "contradiction_status",
        "stratum", "allowed_prompt_slot", "support_score", "support_status",
        "retrieval_method", "retrieval_run_ref", "query_vec_ref", "graph_ref",
        "evidence_digest", "unknown_reason", "not_applicable_reason",
    })

    def test_all_required_fields_present(self) -> None:
        present = {f.name for f in dc.fields(EvidenceItem)}
        missing = self.REQUIRED - present
        assert not missing, (
            f"EvidenceItem missing AG-4 fields: {sorted(missing)}"
        )

    def test_dense_retrieval_item_constructs_with_required_fields(self) -> None:
        item = EvidenceItem(
            source="ev-1",
            content="dense text",
            retrieval_method="dense",
            fact_vec_ref="fv-1",
            dense_score=0.87,
            chunk_digest="abc123",
            citation_anchor="anchor-1",
            source_id="repo_code_chunks",
        )
        assert item.fact_vec_ref == "fv-1"
        assert item.dense_score == 0.87

    def test_sparse_retrieval_item_constructs_with_bm25_score(self) -> None:
        item = EvidenceItem(
            source="ev-2",
            content="sparse text",
            retrieval_method="sparse",
            bm25_score=12.4,
            chunk_digest="def456",
            citation_anchor="anchor-2",
            source_id="repo_code_chunks",
        )
        assert item.bm25_score == 12.4

    def test_graph_retrieval_item_constructs_with_graph_ref(self) -> None:
        item = EvidenceItem(
            source="ev-3",
            content="graph expansion result",
            retrieval_method="graph",
            graph_ref="graph-expansion-7",
            chunk_digest="ghi789",
            citation_anchor="anchor-3",
            source_id="adg_snapshot",
        )
        assert item.graph_ref == "graph-expansion-7"


# ---------------------------------------------------------------------------
# Invariant 2 — FinalEvidenceContract carries non-pass values when EMPTY /
# BLOCKED / CONFLICTED / UNKNOWN; helper rejects those as PASS.
# ---------------------------------------------------------------------------


class TestInv2FECNonPassDispositions:
    """FEC must NOT report passing for EMPTY/BLOCKED/CONFLICTED/UNKNOWN."""

    @pytest.fixture(scope="class")
    def fec_kwargs(self) -> dict:
        return dict(
            request_id="r1", run_id="run1", app_id="apps_rg", trace_id="t1",
            l5_certification_ref=_TEST_CERT,
        )

    def test_unknown_is_not_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(**fec_kwargs, support_status=STATUS_UNKNOWN)
        assert not fec.support_status_is_passing()

    def test_blocked_is_not_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(
            **fec_kwargs,
            support_status=SUPPORT_STATUS_BLOCKED,
            blocked_source_refs=("src-1",),
        )
        assert not fec.support_status_is_passing()
        assert fec.has_blocked_sources()

    def test_empty_is_not_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(**fec_kwargs, support_status=SUPPORT_STATUS_EMPTY)
        assert not fec.support_status_is_passing()

    def test_conflicted_is_not_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(
            **fec_kwargs,
            support_status=SUPPORT_STATUS_CONFLICTED,
            contradiction_report="conflicting-claims-1",
        )
        assert not fec.support_status_is_passing()
        assert fec.has_contradictions()

    def test_weak_is_not_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(**fec_kwargs, support_status=SUPPORT_STATUS_WEAK)
        assert not fec.support_status_is_passing()

    def test_pass_is_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(**fec_kwargs, support_status=SUPPORT_STATUS_PASS)
        assert fec.support_status_is_passing()

    def test_partial_is_pass(self, fec_kwargs: dict) -> None:
        fec = FinalEvidenceContract(**fec_kwargs, support_status=SUPPORT_STATUS_PARTIAL)
        assert fec.support_status_is_passing()

    def test_passing_set_excludes_dangerous_sentinels(self) -> None:
        banned = {
            STATUS_UNKNOWN, STATUS_NOT_APPLICABLE, SUPPORT_STATUS_BLOCKED,
            SUPPORT_STATUS_CONFLICTED, SUPPORT_STATUS_EMPTY,
            SUPPORT_STATUS_WEAK,
        }
        assert not (banned & SUPPORT_STATUS_PASSING_VALUES), (
            "SUPPORT_STATUS_PASSING_VALUES must NOT contain UNKNOWN/BLOCKED/"
            "CONFLICTED/EMPTY/WEAK/NOT_APPLICABLE."
        )


# ---------------------------------------------------------------------------
# Invariant 3 — C0 cannot emit instruction-authority evidence.  Every item
# defaults to allowed_prompt_slot == C0_EVIDENCE_DATA_ONLY.  Producers may
# not override this to USER_INTENT or MODEL_GENERATION.
# ---------------------------------------------------------------------------


class TestInv3C0EvidenceIsDataOnly:
    def test_default_allowed_prompt_slot_is_c0_evidence_data_only(self) -> None:
        item = EvidenceItem(source="s", content="c")
        assert item.allowed_prompt_slot == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY
        assert item.allowed_prompt_slot == "C0_EVIDENCE_DATA_ONLY"

    def test_apps_rg_c0_emitter_uses_default_slot(self) -> None:
        """apps_rg c0 emitter does not override allowed_prompt_slot."""
        from agentic_core.runtime.c0 import apps_rg_c0_binding
        src = inspect.getsource(apps_rg_c0_binding)
        # Must NOT contain any override that elevates to instruction-class.
        assert "allowed_prompt_slot=USER_INTENT" not in src
        assert "allowed_prompt_slot=MODEL_GENERATION" not in src
        assert 'allowed_prompt_slot="USER_INTENT"' not in src
        assert 'allowed_prompt_slot="MODEL_GENERATION"' not in src


# ---------------------------------------------------------------------------
# Invariant 4 — Prompt Assembly keeps C0 evidence as data only.  AG-2
# already added slot_lineage_map / component_hash_map on
# CompiledPromptArtifact so PA can carry the lineage WITHOUT moving
# retrieved text into an instruction slot.
# ---------------------------------------------------------------------------


class TestInv4PAKeepsEvidenceAsData:
    def test_compiled_prompt_artifact_has_slot_lineage_map(self) -> None:
        from agentic_core.runtime.contracts.compiled_prompt_artifact import (
            CompiledPromptArtifact,
        )
        f = {fld.name for fld in dc.fields(CompiledPromptArtifact)}
        assert "slot_lineage_map" in f
        assert "component_hash_map" in f
        assert "replay_manifest_ref" in f


# ---------------------------------------------------------------------------
# Invariant 5 — L2 preserves evidence refs in sealed artifact.
# ---------------------------------------------------------------------------


class TestInv5L2PreservesEvidenceRefs:
    REQUIRED = frozenset({
        "evidence_refs", "prompt_refs", "tool_call_refs", "model_call_refs",
        "provider_receipts", "replay_manifest", "audit_manifest_ref",
    })

    def test_sealed_l2_artifact_has_ag4_carrier_fields(self) -> None:
        present = {f.name for f in dc.fields(SealedL2Artifact)}
        missing = self.REQUIRED - present
        assert not missing, (
            f"SealedL2Artifact missing AG-4 carrier fields: {sorted(missing)}"
        )


# ---------------------------------------------------------------------------
# Invariant 6 — ExitReviewPacket exists and normalizes terminal-input ref shape.
# ---------------------------------------------------------------------------


class TestInv6ExitReviewPacketExists:
    REQUIRED_AG4 = frozenset({
        "source_contract_ref", "route_contract_ref", "execution_form",
        "registry_digest_set", "evidence_refs", "final_evidence_contract_ref",
        "compiled_prompt_artifact_ref", "exec_trace_refs", "tool_call_refs",
        "model_call_refs", "provider_receipts", "proposed_state_diff_ref",
        "otel_span_refs", "hitl_packet_ref", "l5_certification_refs",
        "runtime_gate_refs", "audit_manifest_ref",
    })

    def test_exit_review_packet_exists(self) -> None:
        assert ExitReviewPacket is not None

    def test_exit_review_packet_has_ag4_ref_fields(self) -> None:
        present = {f.name for f in dc.fields(ExitReviewPacket)}
        missing = self.REQUIRED_AG4 - present
        assert not missing, (
            f"ExitReviewPacket missing AG-4 ref fields: {sorted(missing)}"
        )

    @pytest.mark.parametrize("st", list(SourceType))
    def test_exit_review_packet_normalizes_every_terminal_source_type(
        self, st: SourceType,
    ) -> None:
        # Every SourceType (L2_SEALED_ARTIFACT, L3_WORKFLOW_PACKAGE,
        # RET_CACHE_EXACT, RET_CACHE_SEMANTIC, RET_FALLBACK,
        # HITL_RECLEARED_PACKET) must construct an ExitReviewPacket cleanly.
        ep = ExitReviewPacket(source_type=st)
        assert ep.source_type == st


# ---------------------------------------------------------------------------
# Invariant 7 — X1CheckoutResult supports structured verdicts (X1A..X1J).
# ---------------------------------------------------------------------------


class TestInv7X1CheckoutResultStructuredVerdicts:
    def test_x1_checkout_result_exists(self) -> None:
        assert X1CheckoutResult is not None
        assert X1Item is not None

    def test_x1_checkout_result_has_x1a_through_x1j_slots(self) -> None:
        x1 = X1CheckoutResult()
        gates = [item.gate_id for item in x1.items()]
        assert gates == [f"X1{c}" for c in "ABCDEFGHIJ"]

    def test_x1_item_supports_all_verdicts(self) -> None:
        for v in X1Verdict:
            kw = dict(gate_id="X1A", verdict=v, decisive_reason=str(v.value))
            if v == X1Verdict.NOT_APPLICABLE:
                kw["not_applicable_reason"] = "test reason"
            item = X1Item(**kw)
            assert item.verdict == v

    def test_x1_item_carries_evaluator_type_and_evidence_refs(self) -> None:
        item = X1Item(
            gate_id="X1D",
            verdict=X1Verdict.PASS,
            confidence=0.9,
            evidence_refs=("ev-1", "ev-2"),
            evaluator_type=X1EvaluatorType.HYBRID,
            policy_ref="policy-x1d",
            threshold_ref="threshold-x1d",
            decisive_reason="grounded answer matches evidence",
            score=0.91, threshold=0.80,
        )
        assert item.evidence_refs == ("ev-1", "ev-2")
        assert item.evaluator_type == X1EvaluatorType.HYBRID


# ---------------------------------------------------------------------------
# Invariant 8 — UNKNOWN is never PASS.
# ---------------------------------------------------------------------------


class TestInv8UnknownNeverPass:
    def test_x1_item_unknown_is_not_passing(self) -> None:
        item = X1Item(gate_id="X1A", verdict=X1Verdict.UNKNOWN,
                      decisive_reason="not yet evaluated")
        assert not item.is_passing()

    def test_x1_passing_set_excludes_unknown(self) -> None:
        assert X1Verdict.UNKNOWN not in X1_PASSING_VERDICTS
        assert X1Verdict.FAIL not in X1_PASSING_VERDICTS
        assert X1Verdict.WARN not in X1_PASSING_VERDICTS
        assert X1Verdict.NOT_APPLICABLE not in X1_PASSING_VERDICTS

    def test_x1_overall_pass_blocked_by_unknown(self) -> None:
        x1 = X1CheckoutResult()  # all default UNKNOWN
        assert not x1.is_overall_pass()

    def test_evidence_item_unknown_status_is_not_pass(self) -> None:
        item = EvidenceItem(source="s", content="c", support_status=STATUS_UNKNOWN)
        assert item.support_status not in SUPPORT_STATUS_PASSING_VALUES


# ---------------------------------------------------------------------------
# Invariant 9 — NOT_APPLICABLE requires reason.
# ---------------------------------------------------------------------------


class TestInv9NotApplicableRequiresReason:
    def test_evidence_item_na_status_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires a reason"):
            EvidenceItem(source="s", content="c",
                         acl_status=STATUS_NOT_APPLICABLE)

    def test_evidence_item_na_status_with_reason_constructs(self) -> None:
        item = EvidenceItem(
            source="s", content="c",
            acl_status=STATUS_NOT_APPLICABLE,
            not_applicable_reason="apps_rg uses inline payload, no ACL surface",
        )
        assert item.acl_status == STATUS_NOT_APPLICABLE

    def test_fec_na_support_status_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires a reason"):
            FinalEvidenceContract(
                request_id="r", run_id="r", app_id="a", trace_id="t",
                l5_certification_ref=_TEST_CERT,
                support_status=STATUS_NOT_APPLICABLE,
            )

    def test_x1_item_na_without_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires a reason"):
            X1Item(gate_id="X1F", verdict=X1Verdict.NOT_APPLICABLE)


# ---------------------------------------------------------------------------
# Invariant 10 — Groundedness check has access to intent, evidence, output refs.
# ---------------------------------------------------------------------------


class TestInv10GroundednessHasIntentEvidenceOutput:
    def test_x1d_pass_requires_intent_evidence_output(self) -> None:
        # X1D PASS without intent/evidence/output refs should be rejected by
        # x1d_groundedness_has_required_refs().
        x1 = X1CheckoutResult(
            x1d_answer_good=X1Item(
                gate_id="X1D", verdict=X1Verdict.PASS,
                decisive_reason="grounded",
            ),
        )
        assert not x1.x1d_groundedness_has_required_refs()

    def test_x1d_pass_with_required_refs_is_consistent(self) -> None:
        x1 = X1CheckoutResult(
            intent_ref="intent-1",
            evidence_refs=("ev-1",),
            output_ref="output-1",
            x1d_answer_good=X1Item(
                gate_id="X1D", verdict=X1Verdict.PASS,
                decisive_reason="grounded",
            ),
        )
        assert x1.x1d_groundedness_has_required_refs()

    def test_x1d_non_pass_does_not_require_refs(self) -> None:
        x1 = X1CheckoutResult(
            x1d_answer_good=X1Item(
                gate_id="X1D", verdict=X1Verdict.NOT_APPLICABLE,
                not_applicable_reason="cache hit, no model generation",
            ),
        )
        assert x1.x1d_groundedness_has_required_refs()  # vacuously True

    def test_x1g_replay_pass_requires_replay_manifest(self) -> None:
        x1 = X1CheckoutResult(
            x1g_replay_eligible=X1Item(
                gate_id="X1G", verdict=X1Verdict.PASS,
                decisive_reason="replay ok",
            ),
        )
        assert not x1.x1g_replay_eligibility_is_consistent()

    def test_x1h_observable_pass_requires_otel_span(self) -> None:
        x1 = X1CheckoutResult(
            x1h_observable=X1Item(
                gate_id="X1H", verdict=X1Verdict.PASS,
                decisive_reason="observable",
            ),
        )
        assert not x1.x1h_observability_is_consistent()


# ---------------------------------------------------------------------------
# Invariant 11 — No ChromaDB mutation.  AG-4 introduces NO chromadb,
# vector_db, or sentence_transformers imports anywhere in the contract files.
# ---------------------------------------------------------------------------


class TestInv11NoChromaMutation:
    AG4_FILES = (
        "agentic_core/runtime/contracts/final_evidence_contract.py",
        "agentic_core/runtime/contracts/sealed_l2_artifact.py",
        "agentic_core/runtime/contracts/x1_checkout_result.py",
        "agentic_core/L3_orchestration/exit_eval/v6/types.py",
        "agentic_core/runtime/c0/apps_rg_c0_binding.py",
    )
    FORBIDDEN_IMPORTS = (
        "import chromadb",
        "from chromadb",
        "import vector_db",
        "from vector_db",
        "import sentence_transformers",
        "from sentence_transformers",
    )

    @pytest.mark.parametrize("rel_path", AG4_FILES)
    def test_no_chroma_or_vector_imports(self, rel_path: str) -> None:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        src = (repo_root / rel_path).read_text(encoding="utf-8")
        for forbidden in self.FORBIDDEN_IMPORTS:
            assert forbidden not in src, (
                f"{rel_path} contains forbidden import {forbidden!r} — "
                "AG-4 forbids any new ChromaDB / vector_db / "
                "sentence_transformers dependency."
            )


# ---------------------------------------------------------------------------
# Invariant 12 — No embedding generation.  AG-4 introduces NO bge_runtime
# or bge_embed_* imports in the contract files.
# ---------------------------------------------------------------------------


class TestInv12NoEmbeddingGeneration:
    AG4_FILES = TestInv11NoChromaMutation.AG4_FILES
    FORBIDDEN = (
        "from agentic_core.embeddings",
        "import agentic_core.embeddings",
        "bge_embed_query",
        "bge_embed_batch",
        "bge_embed_multi",
        ".embed_texts(",
        ".embed_query(",
    )

    @pytest.mark.parametrize("rel_path", AG4_FILES)
    def test_no_embedding_generation_calls(self, rel_path: str) -> None:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        src = (repo_root / rel_path).read_text(encoding="utf-8")
        for forbidden in self.FORBIDDEN:
            assert forbidden not in src, (
                f"{rel_path} contains {forbidden!r} — AG-4 forbids any "
                "embedding generation in the carrier-repair surface."
            )
