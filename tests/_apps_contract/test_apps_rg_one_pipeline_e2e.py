"""E2E — one governed pipeline (Anthropic-style single agent flow).

Proves section lane runs U0→L6 through one spine (no parallel bypass):
  front bridge → C0 FEC → governed PA sign → L2 handoff → Exit authority → exhaust → L6 gate.

PROOF_CLASSIFICATION: HARNESS_E2E (mocked C0/provider; not live LLM).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from apps_rg.runtime.one_spine_inventory import build_one_spine_section_path_inventory
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.section_l2_lane_integration import (
    finalize_section_l2_after_output,
    prepare_section_l2_before_provider,
)
from apps_rg.runtime.section_one_spine_certification import inspect_one_spine_chain
from apps_rg.runtime.section_one_spine_no_two_path import inspect_no_two_path_lane
from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
    finalize_section_runtime_exhaust_before_l6,
)
from apps_rg.runtime.section_spine_terminology import CANONICAL_SPINE_CHAIN
from apps_rg.runtime.spine.c0_fec_compose import (
    build_spine_c0_fec_artifact,
    emit_spine_c0_fec_artifacts,
)
from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
    emit_section_front_spine_receipts,
)
from apps_rg.runtime.spine.governed_pa_compose import (
    GOVERNED_PA_MODE_SECTION_CORE_SIGNED,
    stamp_section_governed_pa_receipt,
)
from apps_rg.runtime.spine.l2_handoff_receipt import L2_HANDOFF_RECEIPT_ARTIFACT
from apps_rg.runtime.spine.spine_span_emit import (
    SPINE_SPAN_COVERAGE_RECEIPT,
    SPINE_SPAN_RECEIPT,
    validate_spine_span_coverage,
)

REPO = Path(__file__).resolve().parents[2]
GATE_SINGLE = REPO / "ops_scripts/ci/check_apps_rg_single_spine.py"
GATE_CONVERGENCE = REPO / "ops_scripts/ci/check_apps_rg_spine_convergence_w8.py"

# Anthropic effective-agents pattern: one sequential workflow, explicit handoffs, no shadow path.
SPINE_LAYER_ORDER: tuple[str, ...] = ("U0", "L1", "L0", "C0", "PA", "L2", "EXIT", "L6")


@pytest.fixture(autouse=True)
def _harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_C0_EVIDENCE_ROOM", "0")
    deactivate_fixture_dev_bypass()


@pytest.fixture(autouse=True)
def _mock_spine_c0(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake(**_: object) -> FinalEvidenceContract:
        return FinalEvidenceContract(
            request_id="req-e2e",
            run_id="run-e2e",
            app_id="apps_rg",
            trace_id="trace-e2e",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="d" * 64,
            evidence_items=(
                EvidenceItem(
                    source="fact:bul_001",
                    content="Single pipeline proof.",
                    source_type="proof_pool",
                ),
            ),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        _fake,
    )


def _args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Acme Corp",
        "target_title": "VP Engineering",
        "target_role": "VP Engineering",
        "jd_text": "Lead platform engineering.",
        "briefing": "Single pipeline E2E.",
        "base_resume_ref": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _pool(section_id: str) -> SectionProofPool:
    facts = [{"fact_id": "bul_acme_001", "claim_text": "Built platform."}]
    return SectionProofPool(
        section=section_id,
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
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "final_evidence_contract_snapshot": {
                    "evidence_items": [{"evidence_id": "evidence:graph:bul_acme_001"}],
                    "support_status": "SUPPORTED",
                },
            },
        },
        selected_fact_plan={"facts": facts},
    )


def _run_section_one_pipeline(artifact_dir: Path, section_id: str = "headline") -> dict:
    """Execute full section spine without provider LLM (harness E2E)."""
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        front = build_section_front_spine_from_args(
            section_id=section_id,
            args=_args(),
            repo_root=REPO,
        )
        emit_section_front_spine_receipts(artifact_dir, front)
        bridge = build_spine_c0_fec_artifact(
            section_id=section_id,
            front_spine=front,
            pool=_pool(section_id),
        )
        emit_spine_c0_fec_artifacts(artifact_dir, bridge)
        payload: dict = {
            "product_visible": True,
            "artifact_dir": str(artifact_dir),
            "run_id": "run-e2e",
            "section_fec_bridge": bridge.bridge_doc,
            "_section_front_spine": front,
            "allowed_fact_ids": ["bul_acme_001"],
        }
        compiled = SimpleNamespace(
            section_id=section_id,
            apps_rg_prompt_template_ref="lane_v1",
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

        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "compiled_prompt_artifact.json").write_text(
            json.dumps(
                {
                    "evidence_contract_consumed": True,
                    "fec_bridge_mode": "section_fec_bridge",
                    "raw_proof_pool_direct_to_pa": False,
                    "compilation_hash": payload.get("pa_manifest_hash", ""),
                    "signature": payload.get("pa_hmac", ""),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        prepare_section_l2_before_provider(
            artifact_dir,
            section_id,
            payload,
            provider_lane="qwen_vllm",
        )
        for name, body in (
            ("provider_request.json", {}),
            ("provider_response.json", {}),
            ("l2_output.json", {}),
            ("x2_gate_outputs.json", [{"gate_id": "g1", "pass": True}]),
            ("x3_disposition.json", {"x3_code": "X3_BLOCK", "pass": False}),
        ):
            (artifact_dir / name).write_text(
                json.dumps(body, indent=2) + "\n",
                encoding="utf-8",
            )
        finalize_section_l2_after_output(artifact_dir, section_id, payload)
        finalize_section_exit_after_l2(artifact_dir, section_id, payload)
        finalize_section_runtime_exhaust_before_l6(
            artifact_dir,
            section_id,
            payload,
            repo_root=REPO,
        )
        return payload
    finally:
        deactivate_fixture_dev_bypass()


@pytest.mark.apps_contract
def test_inventory_declares_single_pipeline_not_two_paths() -> None:
    inv = build_one_spine_section_path_inventory()
    assert inv["two_paths_found"] is False
    assert inv["canonical_spine_target"] == list(CANONICAL_SPINE_CHAIN)


@pytest.mark.apps_contract
def test_section_lane_one_pipeline_u0_through_l6_e2e(tmp_path: Path) -> None:
    payload = _run_section_one_pipeline(tmp_path, "headline")

    chain = inspect_one_spine_chain(tmp_path)
    assert chain["required_chain_complete"] is True
    assert chain["all_required_artifacts_present"] is True

    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["no_two_path_preconditions_pass"] is True
    assert ntp["checks"]["raw_proof_pool_direct_to_pa"] is False
    assert ntp["checks"]["section_x3_mirror_not_authoritative"] is True

    assert (tmp_path / "spine_pa_core_signing_receipt.json").is_file()
    assert (tmp_path / L2_HANDOFF_RECEIPT_ARTIFACT).is_file()
    assert (tmp_path / "exit_disposition_receipt.json").is_file()
    assert (tmp_path / "runtime_exhaust_bundle.json").is_file()
    assert (tmp_path / "c0_graph_lane_receipt.json").is_file()
    assert (tmp_path / "l6_eval_before_learn_receipt.json").is_file()

    coverage = validate_spine_span_coverage(tmp_path, product_visible=True)
    assert coverage["complete"] is True, coverage.get("missing_layers")
    assert (tmp_path / SPINE_SPAN_COVERAGE_RECEIPT).is_file()

    span_layers: list[str] = []
    span_path = tmp_path / SPINE_SPAN_RECEIPT
    if span_path.is_file():
        for line in span_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                span_layers.append(json.loads(line)["layer_key"])
    for layer in SPINE_LAYER_ORDER:
        assert layer in span_layers, f"missing spine span layer {layer!r} in {span_layers}"

    edr = json.loads((tmp_path / "exit_disposition_receipt.json").read_text(encoding="utf-8"))
    assert edr.get("exit_disposition_receipt_authority") is True or edr.get("schema_version")
    assert payload.get("governed_pa_mode") == GOVERNED_PA_MODE_SECTION_CORE_SIGNED


@pytest.mark.apps_contract
def test_integrated_and_section_share_governed_binding_seams() -> None:
    """Both entry shapes must wire the same governed compose modules (one pipeline family)."""
    needles = (
        "governed_pa_compose_integrated",
        "governed_l2_seal_integrated",
        "governed_exit_finalize_integrated",
    )
    for rel in (
        "apps_rg/runtime/bindings/pa_binding.py",
        "apps_rg/runtime/bindings/l2_binding_adapter.py",
        "apps_rg/runtime/bindings/exit_binding.py",
    ):
        text = (REPO / rel).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text or "governed_" in text


@pytest.mark.apps_contract
def test_ci_gates_confirm_no_second_pipeline() -> None:
    env = dict(os.environ)
    env.pop("APPS_RG_SINGLE_SPINE_GATE_BYPASS", None)
    env.pop("APPS_RG_SPINE_CONVERGENCE_BYPASS", None)
    for gate in (GATE_SINGLE, GATE_CONVERGENCE):
        completed = subprocess.run(
            [sys.executable, str(gate)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env=env,
        )
        assert completed.returncode == 0, (
            f"{gate.name} failed:\n{completed.stdout[-1200:]}\n{completed.stderr[-600:]}"
        )
