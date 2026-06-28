"""W8 follow-up — close deferred partials: section PA core signing, L2 handoff, span emit."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import (
    build_spine_c0_fec_artifact,
    emit_spine_c0_fec_artifacts,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
    emit_section_front_spine_receipts,
)
from apps_rg.runtime.spine.governed_pa_compose import (
    GOVERNED_PA_MODE_SECTION_CORE_SIGNED,
    governed_pa_sign_section_core,
    stamp_section_governed_pa_receipt,
)
from apps_rg.runtime.spine.l2_handoff_receipt import (
    L2_HANDOFF_RECEIPT_ARTIFACT,
    build_section_l2_handoff_receipt,
)
from apps_rg.runtime.spine.spine_span_emit import SPINE_SPAN_RECEIPT, emit_spine_span_event


REPO = Path(__file__).resolve().parents[2]


def _args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Acme Corp",
        "target_title": "VP Engineering",
        "target_role": "VP Engineering",
        "jd_text": "Lead platform engineering.",
        "briefing": "Emphasize delivery.",
        "base_resume_ref": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _minimal_pool() -> SectionProofPool:
    facts = [{"fact_id": "bul_acme_001", "claim_text": "Built platform."}]
    return SectionProofPool(
        section="executive_summary",
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fixtures/graph.json",
        proof_pool_digest="abc",
        allowed_fact_ids_ordered=("bul_acme_001",),
        allowed_fact_ids=frozenset({"bul_acme_001"}),
        bullet_rows=(),
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        base_resume_override_used=False,
        srfs_present=False,
        srfs_ref="",
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "augmented_skills_graph_present": True,
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "graph_lineage_refs": ["ref:graph:version:v1"],
                "final_evidence_contract_snapshot": {
                    "evidence_items": [{"evidence_id": "evidence:graph:bul_acme_001"}],
                    "support_status": "SUPPORTED",
                },
            },
        },
        selected_fact_plan={"facts": facts},
    )


@pytest.fixture(autouse=True)
def _patch_spine_c0_retrieve(monkeypatch: pytest.MonkeyPatch) -> None:
    deactivate_fixture_dev_bypass()
    from agentic_core.runtime.contracts.final_evidence_contract import (
        FinalEvidenceContract,
        SUPPORT_STATUS_PASS,
    )
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF

    def _fake_c0_retrieve(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-def",
            run_id="run-def",
            app_id="apps_rg",
            trace_id="trace-def",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="d" * 64,
            evidence_items=(
                EvidenceItem(
                    source="fact:bul_001",
                    content="Governed platform delivery.",
                    source_type="proof_pool",
                ),
            ),
            graph_lane_ref=C0_GRAPH_LANE_NA_REF,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake_c0_retrieve,
    )


def test_section_core_pa_signing_and_span_emit() -> None:
    activate_fixture_dev_bypass()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp)
            front = build_section_front_spine_from_args(
                section_id="executive_summary",
                args=_args(),
                repo_root=REPO,
            )
            emit_section_front_spine_receipts(artifact_dir, front)
            pool = _minimal_pool()
            bridge = build_spine_c0_fec_artifact(
                section_id="executive_summary",
                front_spine=front,
                pool=pool,
            )
            emit_spine_c0_fec_artifacts(artifact_dir, bridge)
            payload = {
                "product_visible": True,
                "artifact_dir": str(artifact_dir),
                "section_fec_bridge": bridge.bridge_doc,
                "_section_front_spine": front,
                "run_id": "run-def",
            }
            compiled = SimpleNamespace(
                section_id="executive_summary",
                apps_rg_prompt_template_ref="exec_v1",
                artifact=SimpleNamespace(
                    slot_payloads=(),
                    template_id="t1",
                    prompt_hash="h1",
                    canonical_slot_order=(),
                    component_hash_map={},
                    provider_render_manifest={},
                ),
            )
            bom = stamp_section_governed_pa_receipt(
                payload,
                compiled,
                artifact_dir=artifact_dir,
            )
            assert bom.get("core_assemble_prompt_invoked") is True
            assert payload.get("governed_pa_mode") == GOVERNED_PA_MODE_SECTION_CORE_SIGNED
            assert (artifact_dir / "spine_pa_core_signing_receipt.json").is_file()
            span_log = artifact_dir / SPINE_SPAN_RECEIPT
            assert span_log.is_file()
            emit_spine_span_event(
                artifact_dir,
                layer_key="U0",
                binding_seam="apps_rg/runtime/bindings/u0_binding.py",
            )
            lines = [json.loads(ln) for ln in span_log.read_text(encoding="utf-8").splitlines() if ln.strip()]
            layers = {row["layer_key"] for row in lines}
            assert "PA" in layers
            assert "U0" in layers
    finally:
        deactivate_fixture_dev_bypass()


def test_l2_handoff_receipt_passes_with_pa_hmac() -> None:
    payload = {
        "product_visible": True,
        "compiled_prompt_artifact_summary": {"signature": "a" * 64, "target_provider": "local_model_server"},
        "trace_root": "trace-1",
        "grounding_required": True,
    }
    receipt = build_section_l2_handoff_receipt(payload, section_id="executive_summary")
    assert receipt["handoff_status"] == "PASS"
    assert receipt["validation"]["valid"] is True
    assert L2_HANDOFF_RECEIPT_ARTIFACT


def test_emit_spine_span_respects_kill_switch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_SPINE_SPAN_EMIT", "0")
    with tempfile.TemporaryDirectory() as tmp:
        path = emit_spine_span_event(Path(tmp), layer_key="U0", binding_seam="test")
        assert path is None
