"""W5: Runtime exhaust bundle + observer-only L6 handoff shape."""

from __future__ import annotations

import hashlib
from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.native_contract_chain import (
    build_ag5_terminal_dict_for_native_proof,
    build_native_core_contract_chain_from_binding,
    build_native_runtime_exhaust_l6_proof,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_runtime_exhaust_bundle_fields_observer_only() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    chain = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    terminal = build_ag5_terminal_dict_for_native_proof(chain)
    digest = hashlib.sha256(str(terminal).encode("utf-8")).hexdigest()
    proof = build_native_runtime_exhaust_l6_proof(
        exit_disposition_digest=digest,
        gate_mesh_ref="mesh-native-proof",
        route_contract_ref=str(terminal.get("route_contract_ref") or ""),
        sealed_result_ref="sealed-native-proof",
        x1_summary_digest="x1summ",
        x2_summary_digest="x2summ",
    )
    assert "EXIT" in proof.stage_map
    assert "ExitDispositionReceipt" in proof.contract_inventory
    assert proof.x3_ref.startswith("x3:")
    assert proof.l6_handoff_refs
    assert proof.l6_approval_authority == "NONE"
    assert proof.learning_mutation_performed is False
    assert proof.promotion_allowed is False
    assert proof.memory_promotion_refs == ()
    assert proof.current_run_boundary_receipt_ref.startswith("boundary:")
