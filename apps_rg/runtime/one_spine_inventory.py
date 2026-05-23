"""Read-only one-spine path inventory — section CLI via front bridge (W2)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps_rg.runtime.section_spine_terminology import (
    CANONICAL_SPINE_CHAIN,
    LEGACY_C03_ARTIFACT_BASENAME,
    LEGACY_FEC_SNAPSHOT_BASENAME,
    RECOMMENDED_BINDING_ARTIFACT_BASENAME,
    RECOMMENDED_FEC_SNAPSHOT_BASENAME,
    SECTION_LANE_CHAIN,
    SECTION_LANE_MISSING_CANONICAL_CONTRACTS,
    EXPLICIT_NON_CLAIMS,
)
from apps_rg.runtime.spine.front_contracts import FRONT_SPINE_CONTRACTS

# Front bridge emits these before proof_pool; downstream spine contracts remain lane-local or deferred.
SECTION_FRONT_EMITTED_CONTRACTS: tuple[str, ...] = FRONT_SPINE_CONTRACTS


def build_one_spine_section_path_inventory() -> dict[str, Any]:
    """Structured inventory for docs/reports/apps_rg/one_spine_section_path_inventory.json."""
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "one_spine_section_path_inventory_v2",
        "generated_at_utc": ts,
        "plan_slug": "pa-exec-flowchart-gap-f2a8c3",
        "waves_completed": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
        "two_paths_found": False,
        "single_entry_rationale": (
            "Section CLI and integrated dispatch both require U0 package ingest + "
            "section_front_spine_bridge (U0→L1→L0) before proof_pool; no parallel "
            "unvalidated ingress envelope."
        ),
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "path_a_section_cli": {
            "entry": "apps_rg/__main__.py --section <lane>",
            "dispatch": "apps_rg/runtime/c0/section_proof_loader.py::load_section_proof_for_lane",
            "front_bridge": "apps_rg/runtime/spine/front_contracts.py (alias section_front_spine_bridge.py)",
            "u0": "apps_rg/runtime/bindings/u0_binding.py::u0_validate_apps_rg + RuntimePackageRegistry",
            "observed_chain": list(SECTION_LANE_CHAIN),
            "exemplar_lane": "executive_summary",
            "proof_pool": "apps_rg/runtime/proof_pool_resolver.py (requires SectionFrontSpineBridge)",
            "downstream": "section lane modular PA/L2/Exit (not full spine Exit yet)",
        },
        "path_b_canonical_r4": {
            "entry": "apps_rg/__main__.py (no --section) OR dispatch_apps_rg_run",
            "dispatch": "canonical_dispatch → run_integrated_single_action_spine",
            "u0": "same u0_validate_apps_rg + runtime customization package",
            "observed_chain": list(CANONICAL_SPINE_CHAIN),
        },
        "contract_bypass_matrix": _contract_bypass_matrix(),
        "section_cli_status": {
            "user_facing_command_preserved": True,
            "classification": "lane_scoped_invocation_target",
            "front_spine_contracts_emitted": list(SECTION_FRONT_EMITTED_CONTRACTS),
            "missing_canonical_contracts": [
                c
                for c in SECTION_LANE_MISSING_CANONICAL_CONTRACTS
                if c not in SECTION_FRONT_EMITTED_CONTRACTS
            ],
            "u0_package_path_required": True,
            "lane_local_artifacts": [
                "section_front_spine_receipt.json",
                "validated_request.json",
                "l1_plan_contract.json",
                "route_contract.json",
                "runtime_payload.json",
                LEGACY_C03_ARTIFACT_BASENAME,
                LEGACY_FEC_SNAPSHOT_BASENAME,
                "compiled_prompt_artifact.json",
                "l2_output.json",
                "x3_disposition.json",
            ],
        },
        "misnamed_c0_artifacts": _misnamed_c0_artifacts(),
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
        "open_gaps": _open_gaps(),
    }


def _contract_bypass_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    section_substitutes = {
        "ValidatedRequest": "u0_validate_apps_rg + runtime_customization_package (W1/W2)",
        "L1PlanContract": "l1_plan_apps_rg after front bridge",
        "RouteContract": "l0_route_apps_rg after front bridge",
        "FinalEvidenceContract": f"{LEGACY_FEC_SNAPSHOT_BASENAME} or section_fec_bridge (fec_shape_only)",
        "PromptEnvelope": "compiled_prompt_artifact.json (section-local)",
        "CompiledPromptArtifact": "compiled_prompt_artifact.json",
        "L2ExecutionPacket": "l2_output.json + provider_* (section-local)",
        "SealedL2Artifact": "none",
        "ExitDispositionReceipt": "x3_disposition.json (section aggregate, not spine Exit)",
        "RuntimeExhaustBundle": "runtime_exhaust_bundle.json (lane-local)",
    }
    for ct in SECTION_LANE_MISSING_CANONICAL_CONTRACTS:
        emits = ct in SECTION_FRONT_EMITTED_CONTRACTS
        rows.append(
            {
                "contract_type": ct,
                "section_cli_emits_canonical": emits,
                "section_cli_substitute": (
                    section_substitutes.get(ct, "none") if not emits else "spine front bridge"
                ),
                "canonical_r4_emits": True,
            }
        )
    return rows


def _misnamed_c0_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "path": "apps_rg/runtime/c03_graphrag_bound.py",
            "current_name": "C0.3 GraphRAG binding",
            "recommended_name": "section graph binding (SECTION_GRAPH_CONTEXT_BINDING_NOT_PRODUCT_C0_3)",
            "artifact_file": LEGACY_C03_ARTIFACT_BASENAME,
            "recommended_artifact_file": RECOMMENDED_BINDING_ARTIFACT_BASENAME,
            "changed_now": "metadata_fields_added",
            "reason": "Static ledger neighbor expansion is not agentic_core graph traverse",
        },
        {
            "path": LEGACY_FEC_SNAPSHOT_BASENAME,
            "current_name": "final_evidence_contract_snapshot",
            "recommended_name": RECOMMENDED_FEC_SNAPSHOT_BASENAME,
            "changed_now": False,
            "reason": "Filename kept for compat; doc marks fec_shape_only",
        },
    ]


def _open_gaps() -> list[str]:
    return [
        "GAP-SPINE-OTEL: dual-write bridge + emit-site gate; full semconv OTEL on all lanes still open (P1)",
        "GAP-SPINE-PA-CORE: section slots remain primary; core assemble_prompt signs manifest (section_slot_bom_core_signed)",
        "GAP-C0-3-ENGINE: core Graph RAG engine deferred; c0_graph_lane_receipt.json proves NA/skills-bound only",
        "GAP-L6-PROMOTION: l6_eval_before_learn_receipt.json blocks promotion; human eval+gauntlet execution deferred",
        "GAP-LIVE-ALL-LANES: live_section_spine_smoke_all_lanes.py BLOCKED without Chroma+provider (dry-run manifest only)",
    ]


__all__ = ["build_one_spine_section_path_inventory", "SECTION_FRONT_EMITTED_CONTRACTS"]
