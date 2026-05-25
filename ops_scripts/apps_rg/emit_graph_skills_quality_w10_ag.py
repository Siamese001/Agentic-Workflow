#!/usr/bin/env python3
"""W10-AG: unified C0.3 pipeline bind receipt + stress contract proof."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT = REPORTS / "graph_skills_quality_w10_ag_receipt.json"
BIND_JSON = REPORTS / "graph_skills_c03_unified_pipeline_bind.json"
PYTEST_TARGET = "tests/unit/apps_rg/test_graph_skills_w10_ag_pipeline.py"
PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
ADAPTER_REF = "apps_rg.integrations.c0_graph_adapter"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _run_pytest() -> tuple[bool, str]:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", PYTEST_TARGET, "-q", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    tail = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, tail[-3000:]


def _adapter_stress() -> dict[str, object]:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        AdapterResolutionStatus,
        resolve_graph_adapter,
    )
    from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract
    from agentic_core.runtime.c0.c0_3_graph_rag_executor import maybe_run_graph_rag
    from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF, _resolve_spine_graph_expansion_refs
    from apps_rg.runtime.bindings.l0_binding import APPS_RG_L0_CERT_REF

    resolution = resolve_graph_adapter(ADAPTER_REF)
    policy = GraphTraversePolicy(
        graph_expansion_allowed=True,
        max_hops=1,
        max_nodes=32,
        max_edges=64,
        allowed_relation_types=("EVIDENCE", "RELATED_TO", "DERIVED_FROM"),
        graph_adapter_ref=ADAPTER_REF,
        live_wiring_deferred=False,
        wiring_gate="LIVE",
    )
    route = RouteContract(
        request_id="w10ag-emit",
        run_id="w10ag-emit",
        app_id="apps_rg",
        trace_id="w10ag-emit",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        tenant_id="apps_rg",
        route_family="R3_SIMPLE_GROUNDED_READ",
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
                "content_snippet": "platform engineering",
            },
        )()
    ]
    gr = maybe_run_graph_rag(route, evidence)
    refs = _resolve_spine_graph_expansion_refs(route, evidence)
    return {
        "adapter_resolution": resolution.status.value,
        "adapter_healthy": resolution.adapter.health_check().healthy if resolution.adapter else False,
        "maybe_run_graph_rag_executed": gr.executed,
        "skip_reason": gr.skip_reason,
        "accepted_neighbors": len(gr.pool.accepted_graph_neighbors) if gr.pool else 0,
        "spine_graph_expansion_refs": list(refs),
        "graph_lane_deferred": not refs or refs[0] == C0_GRAPH_LANE_NA_REF,
        "unified_pipeline_bound": bool(refs) and refs[0] != C0_GRAPH_LANE_NA_REF,
    }


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    pytest_ok, pytest_tail = _run_pytest()
    stress = _adapter_stress()
    unified = bool(stress.get("unified_pipeline_bound"))
    status = "PASS" if pytest_ok and unified else "PARTIAL" if pytest_ok else "FAIL"

    bind_doc = {
        "schema": "graph_skills_c03_unified_pipeline_bind_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W10-AG",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "adapter_ref": ADAPTER_REF,
        "pipeline_stages": [
            "l0_route_profiles.yaml",
            "c0_retrieve_apps_rg",
            "maybe_run_graph_rag",
            "run_graph_traverse",
            "FinalEvidenceContract.graph_expansion_refs",
            "proof_pool / c03_graphrag_bound",
        ],
        "stress": stress,
        "claims_c03_unified_pipeline_bound": unified,
        "claims_dynamic_graphrag_traverse": bool(stress.get("maybe_run_graph_rag_executed")),
        "claims_agentic_core_changed": False,
        "status": status,
    }
    BIND_JSON.write_text(json.dumps(bind_doc, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W10-AG",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": "python ops_scripts/apps_rg/emit_graph_skills_quality_w10_ag.py",
        "command_argv": [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w10_ag.py"],
        "cwd": str(REPO),
        "exit_code": 0 if status == "PASS" else 1,
        "status": status,
        "pytest_pass": pytest_ok,
        "pytest_tail": pytest_tail,
        "author_gate": {
            "decision_captured": (
                "DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg, "
                "selected=unified_c03_bind, outcome=executed, confidence=0.92, "
                "precedent=user-accepted-graph-skills-plan"
            ),
            "selected_option": "unified_c03_bind",
        },
        "artifact_paths": [
            "docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json",
            "docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json",
        ],
        "stress": stress,
        "phase_gate": f"PHASE_GATE: wave=W10-AG status={status} gate=G-W10-AG",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "unified": unified, "pytest_ok": pytest_ok}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
