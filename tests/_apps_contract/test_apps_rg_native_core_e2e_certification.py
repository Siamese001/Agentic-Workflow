"""W6: Consolidated certification assertions for the opt-in native-core proof harness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import (
    scan_generic_bindings_tree_for_apps_imports,
    validate_app_binding_package,
)
from agentic_core.runtime.bindings.native_contract_chain import (
    build_ag5_terminal_dict_for_native_proof,
    build_native_core_contract_chain_from_binding,
    build_native_runtime_exhaust_l6_proof,
)
from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH
from agentic_core.runtime.exit.exit_review_normalizer import normalize_ag5_terminal_input
from agentic_core.runtime.exit.x1_checkout_runner import run_ag5_x1_checkout
from agentic_core.runtime.exit.x2_aggregator import aggregate_x1_for_exit
from agentic_core.runtime.exit.x3_emitter import emit_ag5_exit_disposition_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_native_core_certification_smoke_bundle() -> None:
    assert scan_generic_bindings_tree_for_apps_imports() == []
    pkg = load_app_binding_package(FIXTURE_PKG)
    vr = validate_app_binding_package(pkg)
    assert vr.status == "PASS"
    chain = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    raw = build_ag5_terminal_dict_for_native_proof(chain)
    pkt = normalize_ag5_terminal_input(raw)
    x1 = run_ag5_x1_checkout(pkt)
    x2 = aggregate_x1_for_exit(x1)
    receipt = emit_ag5_exit_disposition_receipt(
        packet=pkt,
        x1=x1,
        x2=x2,
        supplementary_refs={
            "user_visible_response_ref": "resp://cert-bundle",
            "deterministic_digest": "digest://cert-bundle",
            "gate_mesh_result_ref": "mesh://cert-bundle",
        },
    )
    assert receipt.x3_code == X3D_ALLOW_FINISH
    exhaust = build_native_runtime_exhaust_l6_proof(
        exit_disposition_digest=receipt.deterministic_digest or "digest-fallback",
        gate_mesh_ref="mesh",
        route_contract_ref=pkt.route_contract_ref or "route",
        sealed_result_ref="sealed",
        x1_summary_digest="x1",
        x2_summary_digest="x2",
    )
    assert exhaust.promotion_allowed is False

    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
