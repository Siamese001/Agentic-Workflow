"""End-to-end AG-5 chain smoke (normalizer → X1 → X2 → emitter)."""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.native_contract_chain import (
    build_ag5_terminal_dict_for_native_proof,
    build_native_core_contract_chain_from_binding,
)
from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH
from agentic_core.runtime.exit.exit_review_normalizer import normalize_ag5_terminal_input
from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout
from agentic_core.runtime.exit.x2_aggregator import aggregate_x1_for_exit
from agentic_core.runtime.exit.x3_emitter import emit_ag5_exit_disposition_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_ag5_contract_chain_native_terminal_dict() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    chain = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    raw = build_ag5_terminal_dict_for_native_proof(chain)
    pkt = normalize_ag5_terminal_input(raw)
    x1 = run_ag5_x1_checkout(pkt)
    assert x1.is_overall_pass()
    x2 = aggregate_x1_for_exit(x1)
    receipt = emit_ag5_exit_disposition_receipt(
        packet=pkt,
        x1=x1,
        x2=x2,
        supplementary_refs={
            "user_visible_response_ref": "resp://ag5-chain",
            "deterministic_digest": "digest://ag5-chain",
            "gate_mesh_result_ref": "mesh://ag5-chain",
        },
    )
    assert receipt.x3_code == X3D_ALLOW_FINISH
