#!/usr/bin/env python3
"""W1: D16 contract proof — spine graph authority + c0_graph_lane receipt shape."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "graph-skills-deferred-followup-d7f2a8"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT = REPORTS / "graph_skills_deferred_followup_w1_receipt.json"
PYTEST = "tests/unit/apps_rg/test_graph_skills_deferred_followup.py"


def main() -> int:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", PYTEST, "-q", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    pytest_ok = proc.returncode == 0
    tail = (proc.stdout or "") + (proc.stderr or "")

    from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF, _resolve_spine_graph_expansion_refs
    from apps_rg.runtime.bindings.l0_binding import APPS_RG_L0_CERT_REF
    from apps_rg.runtime.spine.c0_graph_lane_receipt import build_c0_graph_lane_receipt_from_spine_retrieve

    policy = GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=1,
        max_nodes=32,
        max_edges=64,
        allowed_relation_types=("EVIDENCE", "RELATED_TO"),
        graph_adapter_ref="apps_rg.integrations.c0_graph_adapter",
        live_wiring_deferred=False,
        wiring_gate="LIVE",
    )
    route = RouteContract(
        request_id="w1",
        run_id="w1",
        app_id="apps_rg",
        trace_id="w1",
        route_id="R3",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id="apps_rg",
        route_family="R3",
        execution_form="SINGLE_STEP",
        graph_traverse_policy=policy,
        l5_certification_ref=APPS_RG_L0_CERT_REF,
    )
    evidence = [
        type(
            "E",
            (),
            {
                "evidence_id": "ev:fact_engineering_platform_001",
                "source_ref": "fact_engineering_platform_001",
                "content_snippet": "platform",
            },
        )()
    ]
    refs = _resolve_spine_graph_expansion_refs(route, evidence)
    spine_receipt = {
        "section_id": "executive_summary",
        "graph_expansion_refs": list(refs),
        "graph_lane_na_ref": refs[0] if refs else C0_GRAPH_LANE_NA_REF,
        "graph_lane_deferred": refs[0] == C0_GRAPH_LANE_NA_REF if refs else True,
        "canonical_c0_3_graph_claimed": refs[0] != C0_GRAPH_LANE_NA_REF if refs else False,
    }
    graph_receipt = build_c0_graph_lane_receipt_from_spine_retrieve(spine_receipt)
    d16_pass = bool(graph_receipt.get("canonical_c0_3_graph_rag_claimed")) and pytest_ok

    receipt = {
        "schema": "graph_skills_deferred_followup_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W1",
        "status": "PASS" if d16_pass else "PARTIAL",
        "pytest_pass": pytest_ok,
        "pytest_tail": tail[-1500:],
        "d16_real_llm_pass": False,
        "d16_contract_pass": d16_pass,
        "spine_graph_expansion_refs": list(refs),
        "c0_graph_lane_receipt_sample": graph_receipt,
        "ds11_spine_authority_contract": pytest_ok,
        "phase_gate": f"PHASE_GATE: wave=W1 status={'PASS' if d16_pass else 'PARTIAL'} gate=G-W1",
        "notes": "REAL_LLM Brown exec_summary run required for d16_real_llm_pass=true (W1 pilot).",
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "d16_contract_pass": d16_pass}, indent=2))
    return 0 if d16_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
