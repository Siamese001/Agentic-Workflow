"""Contract tests: env kill-switch cleanup (W1–W3) — negative controls, no live runtime proof."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.c0.c02_hybrid_receipt_truth import FORBIDDEN_RECEIPT_REASON
from apps_rg.runtime.c0.c02_product_hybrid_retrieval import perform_product_hybrid_retrieval
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.product_runtime_guards import (
    ENV_APPS_RG_C0_EVIDENCE_ROOM,
    ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH,
    ProductRuntimeEnvForbiddenError,
    assert_canonical_product_section_env,
    product_fec_bridge_mandatory,
)
from apps_rg.runtime.c0_mandatory_policy import apps_rg_c0_dense_sparse_mandatory
from apps_rg.runtime.product_output_policy import product_fail_closed_runtime
from apps_rg.runtime.spine.c0_fec_compose import (
    SectionFecBridgePreconditionError,
    assert_section_pa_fec_preconditions,
)

REPO = Path(__file__).resolve().parents[2]
APPS_RG = REPO / "apps_rg"

REQUIRED_TRUTH_KEYS = frozenset(
    {
        "retrieval_profile_ref",
        "product_hybrid_required",
        "product_hybrid_attempted",
        "dense_attempted",
        "sparse_attempted",
        "bm25_available",
        "failure_reason",
        "proof_classification",
    }
)


def _truth_keys(receipt: dict) -> set[str]:
    return {k for k in REQUIRED_TRUTH_KEYS if k in receipt}


@pytest.fixture(autouse=True)
def _product_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)


class TestForbiddenProductEnv:
    def test_c0_evidence_room_zero_forbidden_on_product_lane(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_APPS_RG_C0_EVIDENCE_ROOM, "0")
        assert product_fail_closed_runtime()
        with pytest.raises(ProductRuntimeEnvForbiddenError, match=ENV_APPS_RG_C0_EVIDENCE_ROOM):
            assert_canonical_product_section_env("executive_summary")

    def test_fec_bridge_kill_switch_zero_forbidden_on_product_lane(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH, "0")
        assert product_fail_closed_runtime()
        with pytest.raises(
            ProductRuntimeEnvForbiddenError, match=ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH
        ):
            assert_canonical_product_section_env("executive_summary")

    def test_harness_allows_c0_evidence_room_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
        monkeypatch.setenv(ENV_APPS_RG_C0_EVIDENCE_ROOM, "0")
        assert_canonical_product_section_env("executive_summary")

    def test_product_fec_bridge_mandatory_by_default(self) -> None:
        assert product_fec_bridge_mandatory() is True

    def test_pa_requires_bridge_when_product_mandatory(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "apps_rg.runtime.spine.c0_fec_compose.fixture_dev_bypass_active",
            lambda: False,
        )
        payload = {
            "product_visible": True,
            "selected_fact_plan": {"facts": [{"fact_id": "f1", "claim_text": "x"}]},
            "allowed_fact_ids": ["f1"],
        }
        with pytest.raises(SectionFecBridgePreconditionError):
            assert_section_pa_fec_preconditions(payload)


class TestSpineEnrichEnvRemoved:
    def test_no_spine_chroma_enrich_in_apps_rg(self) -> None:
        hits = list(APPS_RG.rglob("*.py"))
        matches = []
        for path in hits:
            text = path.read_text(encoding="utf-8", errors="replace")
            if "APPS_RG_SPINE_CHROMA_ENRICH" in text:
                matches.append(str(path.relative_to(REPO)))
        assert matches == [], matches

    def test_c05_signature_has_no_spine_params(self) -> None:
        import inspect

        sig = inspect.signature(build_c05_final_evidence_contract)
        assert "spine_chroma_enrich" not in sig.parameters
        assert "merge_canonical_c0" not in sig.parameters


class TestPositiveReceiptTruth:
    def test_c05_emits_required_truth_fields(self) -> None:
        _, receipt = build_c05_final_evidence_contract(
            section_id="headline",
            atoms=[],
            strata={},
            graph_bindings=[],
            front_spine=None,
            allowed_fact_ids=[],
            product_hybrid={
                "required": False,
                "c02_vector_query": {
                    "product_hybrid_required": False,
                    "product_hybrid_attempted": False,
                },
            },
        )
        vq = receipt["c02_vector_query"]
        assert REQUIRED_TRUTH_KEYS <= _truth_keys(vq)
        assert vq["failure_reason"] != FORBIDDEN_RECEIPT_REASON
        assert "spine_chroma_enrich_disabled" not in json.dumps(vq)

    def test_hybrid_not_required_truth(self) -> None:
        out = perform_product_hybrid_retrieval(
            section_id="early_career",
            app_payload={},
            evidence_digest="abc",
            timestamp_iso="2026-01-01T00:00:00Z",
        )
        vq = out["c02_vector_query"]
        assert REQUIRED_TRUTH_KEYS <= _truth_keys(vq)
        assert vq["product_hybrid_required"] is False
        assert vq["failure_reason"] == "product_hybrid_not_required"


class TestBm25UnavailableFailClosed:
    def test_mandatory_sparse_unavailable_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        if not apps_rg_c0_dense_sparse_mandatory():
            pytest.skip("dense/sparse mandatory off")
        from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

        monkeypatch.setenv("CHROMA_PERSIST_DIR", str(REPO / "data" / "cache" / "chromadb"))
        monkeypatch.setenv("APPS_RG_EMBEDDING_ENABLED", "true")
        try:
            perform_product_hybrid_retrieval(
                section_id="executive_summary",
                app_payload={"jd_text": "lead AI strategy"},
                evidence_digest="deadbeef",
                timestamp_iso="2026-01-01T00:00:00Z",
            )
        except C0EvidenceGapError as exc:
            assert "BM25" in str(exc) or "sparse" in str(exc).lower()
        else:
            vq = {}
            pytest.skip("BM25 available in this environment — gap error not triggered")


class TestArtifactStringGuard:
    def test_forbidden_reason_not_emitted_in_receipt_builders(self) -> None:
        """Guard constant may exist; receipt builders must not emit the legacy string."""
        allow = {"c02_hybrid_receipt_truth.py", "c07_handoff_audit.py"}
        matches = []
        for path in (APPS_RG / "runtime" / "c0").rglob("*.py"):
            if path.name in allow:
                continue
            if "spine_chroma_enrich_disabled" in path.read_text(encoding="utf-8", errors="replace"):
                matches.append(path.name)
        assert matches == [], matches
