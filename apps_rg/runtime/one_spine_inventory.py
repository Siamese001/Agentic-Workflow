"""Read-only one-spine path inventory (Wave 1) — section CLI vs integrated R4 spine."""
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


def build_one_spine_section_path_inventory() -> dict[str, Any]:
    """Structured inventory for docs/reports/apps_rg/one_spine_section_path_inventory.json."""
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "one_spine_section_path_inventory_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "waves_completed": ["1"],
        "two_paths_found": True,
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "path_a_section_cli": {
            "entry": "apps_rg/__main__.py",
            "dispatch": "apps_rg/runtime/orchestration/canonical_dispatch.py::run_canonical_apps_rg_from_cli_primitives",
            "branch": "section id in {executive_summary, headline, unify_bullets, ...} → _run_*_lane_from_cli",
            "exemplar_lane": "executive_summary",
            "exemplar_module": "apps_rg/runtime/sections/executive_summary_lane.py",
            "observed_chain": list(SECTION_LANE_CHAIN),
            "proof_pool": "apps_rg/runtime/proof_pool_resolver.py → augmented_skills_graph (exec summary graph-only)",
            "graph_binding": f"apps_rg/runtime/c03_graphrag_bound.py → {LEGACY_C03_ARTIFACT_BASENAME}",
            "pa": "apps_rg/runtime/dispatch/executive_summary_pa.py",
            "l2": "section provider gateway (qwen_vllm / stub)",
            "exit_surface": "section-local x3_disposition.json + x2_gate_outputs.json (not spine ExitDispositionReceipt)",
            "uwg_l4": "not invoked",
            "l6": "apps_rg/runtime/shadow/executive_summary_l6.py (shadow only)",
        },
        "path_b_canonical_r4": {
            "entry": "apps_rg/__main__.py (no --section) OR dispatch_apps_rg_run",
            "dispatch": "canonical_dispatch → run_integrated_r4_deterministic_pipeline",
            "spine_module": "agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py",
            "c0_pa_wiring": "agentic_core/runtime/entry/apps_rg_dispatch.py::run_ag2_retrieval_and_prompt (ValidatedRequest → c0_retrieve_apps_rg → pa_compose_apps_rg)",
            "dense_c0_optional": "apps_rg/runtime/bindings/c0_binding.py (Chroma C0.2 when EMBEDDING_ENABLED + CHROMA_PERSIST_DIR)",
            "observed_chain": list(CANONICAL_SPINE_CHAIN),
        },
        "contract_bypass_matrix": _contract_bypass_matrix(),
        "section_cli_status": {
            "user_facing_command_preserved": True,
            "classification": "lane_scoped_invocation_target",
            "missing_canonical_contracts": list(SECTION_LANE_MISSING_CANONICAL_CONTRACTS),
            "lane_local_artifacts": [
                "runtime_payload.json",
                LEGACY_C03_ARTIFACT_BASENAME,
                LEGACY_FEC_SNAPSHOT_BASENAME,
                "selected_role_fact_set_ref.json",
                "compiled_prompt.txt",
                "compiled_prompt_artifact.json",
                "provider_request.json",
                "provider_response.json",
                "l2_output.json",
                "x2_gate_outputs.json",
                "x1d_llm_judge_outputs.json",
                "x3_disposition.json",
                "section_metric_receipt.json",
                "runtime_exhaust_bundle.json",
                "section_runtime_proof_bundle.json",
                "artifact_inventory.json",
                "section_input_usage_ledger.json",
            ],
            "srfs_proof_pool": "selected_role_fact_set / SRFS modes on other lanes",
            "graph_proof_pool": "augmented_skills_graph + section_graph_binding_shim",
        },
        "misnamed_c0_artifacts": _misnamed_c0_artifacts(),
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
        "open_gaps": _open_gaps(),
    }


def _contract_bypass_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    section_substitutes = {
        "ValidatedRequest": "CLI args + runtime_payload.json (unvalidated spine contract)",
        "L1PlanContract": "none",
        "RouteContract": "none",
        "FinalEvidenceContract": f"{LEGACY_FEC_SNAPSHOT_BASENAME} (FEC-shaped snapshot only; fec_shape_only)",
        "PromptEnvelope": "compiled_prompt_artifact.json (section-local, not spine PromptEnvelope)",
        "CompiledPromptArtifact": "compiled_prompt_artifact.json (section CPA shape)",
        "L2ExecutionPacket": "l2_output.json + provider_* (section-local)",
        "SealedL2Artifact": "none",
        "ExitDispositionReceipt": "x3_disposition.json (section X3 aggregate, not spine Exit receipt)",
        "RuntimeExhaustBundle": "runtime_exhaust_bundle.json (lane-local refs bundle)",
    }
    for ct in SECTION_LANE_MISSING_CANONICAL_CONTRACTS:
        rows.append(
            {
                "contract_type": ct,
                "section_cli_emits_canonical": False,
                "section_cli_substitute": section_substitutes.get(ct, "none"),
                "canonical_r4_emits": True,
            }
        )
    return rows


def _misnamed_c0_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "path": "apps_rg/runtime/c03_graphrag_bound.py",
            "current_name": "C0.3 GraphRAG binding",
            "recommended_name": "section_graph_binding_shim (C0.3-compatible receipt only)",
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
            "reason": "Filename kept for compat; doc now marks fec_shape_only",
        },
        {
            "path": "apps_rg/runtime/dispatch/input_authority_prompt_block.py",
            "current_name": "C0.3 GraphRAG-bound",
            "recommended_name": "section graph binding (C0.3-shim)",
            "changed_now": True,
            "reason": "Prompt INPUT_AUTHORITY must not imply full C0.3",
        },
        {
            "path": "apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py",
            "current_name": "C0.3 GraphRAG live proof",
            "recommended_name": "section graph binding live proof",
            "changed_now": "docstring",
            "reason": "Validator checks lane graph pool, not spine C0",
        },
        {
            "path": "runtime_exhaust_bundle.json",
            "current_name": "runtime_exhaust_bundle",
            "recommended_name": "section_runtime_exhaust_bundle (spine alias documented in proof bundle)",
            "changed_now": "spine_classification metadata in proof bundle builder",
            "reason": "Same basename as spine contract but lane-local schema",
        },
    ]


def _open_gaps() -> list[str]:
    return [
        "Broad tests/_apps_contract suite needs bounded follow-up triage: full run aborted "
        "~22 minutes at ~48% with no final summary and many F markers (non-dispositive)",
        "Route section lanes through U0 package validation → ValidatedRequest before proof pool",
        "Emit spine RouteContract + call agentic_core c0_retrieve_apps_rg for grounded lanes",
        "Replace section_graph_binding_shim with C0 output or wrap shim as explicit C0.3 sub-step under route",
        "Consume spine FinalEvidenceContract in section PA (or merge section PA into spine PA)",
        "Emit spine ExitDispositionReceipt + SealedL2Artifact; map section X3 to Exit only as read-only mirror",
        "Optional UWG/L4 only when product requests durable write",
    ]


__all__ = ["build_one_spine_section_path_inventory"]
