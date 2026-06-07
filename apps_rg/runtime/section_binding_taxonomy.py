"""Shared artifact lists and design-law owner mapping (breaks import cycles)."""
from __future__ import annotations

L7_CORE_ARTIFACTS: tuple[str, ...] = (
    "agentic_core_how_trace.json",
    "agentic_core_l7_route_family_coverage.json",
    "agentic_core_spine_proof.json",
    "integrated_runtime_artifact_manifest.json",
    "runtime_trace_snapshot.json",
    "runtime_gate_verdict_bundle.json",
)

# W4: hash-only verified external refs when a correlated integrated cli_* run exists.
W4_VERIFIED_EXTERNAL_ARTIFACTS: tuple[str, ...] = (
    "agentic_core_how_trace.json",
    "agentic_core_l7_route_family_coverage.json",
    "agentic_core_spine_proof.json",
    "integrated_runtime_artifact_manifest.json",
    "runtime_trace_snapshot.json",
)

W4_INTEGRATED_PARENT_BUNDLE_INDEX = "RUN_BUNDLE_INDEX.json"

APPS_RG_DOMAIN_ARTIFACTS: tuple[str, ...] = (
    "selected_fact_plan.json",
    "canonical_claim_ledger_v2.json",
    "claim_ledger.json",
    "x2_gate_outputs.json",
    "x1d_llm_judge_outputs.json",
    "executive_summary_judge_packet.json",
    "l2_output.json",
    "parsed_output.json",
    "provider_request.json",
    "provider_response.json",
    "section_metric_receipt.json",
    "product_certification_receipt.json",
    "proof_eligibility_receipt.json",
)

APPS_RG_SHIM_ARTIFACTS: tuple[str, ...] = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "c0_fec_bridge_receipt.json",
    "final_evidence_contract_bridge.json",
    "compiled_prompt_artifact.json",
    "l2_execution_packet.json",
    "sealed_l2_artifact.json",
    "exit_review_packet.json",
    "exit_disposition_receipt.json",
    "runtime_exhaust_bundle.json",
    "l6_shadow_handoff_receipt.json",
    "l6_shadow_eval_package.json",
    "section_runtime_proof_bundle.json",
    "one_spine_certification_receipt.json",
)

APPS_RG_SECTION_SHIM_PREFERRED_NAMES: dict[str, str] = {
    "validated_request.json": "apps_rg_section_validated_request.json",
    "l1_plan_contract.json": "apps_rg_section_l1_plan_contract.json",
    "route_contract.json": "apps_rg_section_route_contract.json",
    "c0_fec_bridge_receipt.json": "apps_rg_section_c0_fec_bridge_receipt.json",
    "final_evidence_contract_bridge.json": "apps_rg_section_final_evidence_contract_bridge.json",
    "compiled_prompt_artifact.json": "apps_rg_section_compiled_prompt_artifact.json",
    "l2_execution_packet.json": "apps_rg_section_l2_execution_packet.json",
    "sealed_l2_artifact.json": "apps_rg_section_sealed_l2_artifact.json",
    "exit_review_packet.json": "apps_rg_section_exit_review_packet.json",
    "exit_disposition_receipt.json": "apps_rg_section_exit_disposition_receipt.json",
    "runtime_exhaust_bundle.json": "apps_rg_section_runtime_exhaust_bundle.json",
    "l6_shadow_handoff_receipt.json": "apps_rg_section_l6_shadow_handoff_receipt.json",
    "l6_shadow_eval_package.json": "apps_rg_section_l6_shadow_eval_package.json",
    "section_runtime_proof_bundle.json": "apps_rg_section_runtime_proof_bundle.json",
    "one_spine_certification_receipt.json": "apps_rg_section_one_spine_certification_receipt.json",
}

# W6A: quarantine assertion (apps_rg binding; not 99 proof).
W6A_NO_DIRECT_CHROMA_ASSERTION = "no_direct_chroma_write_bypass_assertion.json"

CORE_99_DESIGN_ONLY_ARTIFACTS: tuple[str, ...] = (
    "runtime_proof_bundle.json",
    "no_bypass_assertions.json",
    "negative_control_results.json",
    "reconstruction_report.json",
    "replay_report.json",
    "proof_observability.json",
)


def design_law_owner_for_artifact(
    filename: str,
    *,
    legacy_class: str,
    trusted: bool,
    present: bool,
) -> str:
    if filename == "x2_gate_outputs.json":
        return "APP_DOMAIN_EVIDENCE"
    if filename == "section_runtime_proof_bundle.json":
        return "APP_SHIM"
    if filename in CORE_99_DESIGN_ONLY_ARTIFACTS:
        return "DRIFT" if present else "DESIGN_ONLY"
    if filename in APPS_RG_DOMAIN_ARTIFACTS:
        return "APP_DOMAIN_EVIDENCE"
    if filename in APPS_RG_SHIM_ARTIFACTS:
        return "APP_SHIM"
    if filename in APPS_RG_SECTION_SHIM_PREFERRED_NAMES.values():
        return "APP_SHIM"
    if filename == "one_spine_certification_receipt.json":
        return "APP_SHIM"
    if filename in L7_CORE_ARTIFACTS:
        if not present:
            if filename == "runtime_gate_verdict_bundle.json":
                return "NOT_APPLICABLE"
            return "MISSING"
        if trusted:
            return "CORE_L7_PROJECTION"
        return "DRIFT"
    if "ADAPTER" in legacy_class:
        return "APP_ADAPTER"
    return "APP_ADAPTER"


__all__ = [
    "APPS_RG_DOMAIN_ARTIFACTS",
    "APPS_RG_SECTION_SHIM_PREFERRED_NAMES",
    "APPS_RG_SHIM_ARTIFACTS",
    "CORE_99_DESIGN_ONLY_ARTIFACTS",
    "L7_CORE_ARTIFACTS",
    "W4_INTEGRATED_PARENT_BUNDLE_INDEX",
    "W4_VERIFIED_EXTERNAL_ARTIFACTS",
    "W6A_NO_DIRECT_CHROMA_ASSERTION",
    "design_law_owner_for_artifact",
]
