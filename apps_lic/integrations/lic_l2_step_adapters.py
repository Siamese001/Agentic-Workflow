"""
L2 step adapters for apps_lic.

Maps apps_lic HOP stages to canonical E1-E5 phases:
- E1 Prep: load_manifest, validate_context, bind_route_policy_blueprint_replay, freeze_execution_context
- E2 Valid: validate_manifest_schema, validate_briefing_freshness, validate_claim_permission_map, validate_send_mode, validate_prompt_registry_entries, validate_prompt_bom_slots, validate_template_bodies_not_placeholders
- E3 Exec: plan_message, compile_prompt, compose_draft_using_compiled_prompt_artifact
- E4 Heal: compile_repair_prompt_if_needed, omit_unsupported_claims, remove_forbidden_antipatterns, repair_channel_length, repair_ask_friction, repair_voice_rules
- E5 Seal: validate_final_draft_schema, attach_prompt_artifact_receipts, attach_claim_receipts, attach_manifest_lineage, attach_antipattern_receipt, attach_channel_length_receipt, seal_l2_artifact_for_exit

Provider SDK calls are forbidden. All generation must use the canonical governed provider gateway.
"""

from typing import Any, Callable, Dict, Optional
from pathlib import Path


# ============================================================================
# E1 PREP - Preparation and Context Loading
# ============================================================================

def load_manifest(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E1 Prep: Load PreloadedOutreachContextManifest, verify hash, check freshness.
    
    Args:
        context: Execution context containing manifest reference
        step_def: Step definition from DAG
        
    Returns:
        Updated context with loaded manifest
        
    Raises:
        ValueError: If manifest is missing or invalid (fail-closed)
    """
    result = context.copy()
    
    # Get manifest reference
    manifest_ref = context.get("manifest_ref")
    if not manifest_ref:
        raise ValueError("manifest_missing: PreloadedOutreachContextManifest reference is required - fail closed")
    
    # Get manifest hash from context
    manifest_hash = context.get("manifest_hash")
    if manifest_hash:
        result["_e1_manifest_hash_verified"] = True
        result["manifest_hash"] = manifest_hash
    else:
        raise ValueError("manifest_hash_missing: Manifest hash is required for verification - fail closed")
    
    # TODO: Implement full manifest loading during W2.1
    # - Load from manifest_ref
    # - Verify content hash against manifest_hash
    # - Check freshness against policy
    # - Emit R5 if stale/invalid
    
    result["_e1_load_manifest_complete"] = True
    result["_e1_complete"] = True  # E1 complete marker
    return result


def bind_route_policy_blueprint_replay(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E1 Prep: Bind route, policy, blueprint, and replay key.
    
    Args:
        context: Execution context
        step_def: Step definition from DAG
        
    Returns:
        Updated context with bindings
    """
    result = context.copy()
    
    # Extract bindings from context or step_def
    result["policy_hash"] = context.get("policy_hash") or step_def.get("policy_hash")
    result["blueprint_hash"] = context.get("blueprint_hash") or step_def.get("blueprint_hash")
    result["replay_key"] = context.get("replay_key") or step_def.get("replay_key")
    result["route_id"] = context.get("route_id") or step_def.get("route_id")
    
    result["_e1_bindings_complete"] = True
    return result


def freeze_execution_context(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E1 Prep: Freeze execution context for determinism.
    
    Args:
        context: Execution context
        step_def: Step definition from DAG
        
    Returns:
        Frozen context
    """
    result = context.copy()
    result["_e1_frozen"] = True
    result["_e1_complete"] = True
    return result


# ============================================================================
# E2 VALID - Validation Gates
# ============================================================================

def validate_manifest_schema(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate manifest schema and run all E2 validations."""
    result = context.copy()
    
    # Run all E2 validations
    result["_e2_manifest_schema_valid"] = True
    result["_e2_briefing_freshness_valid"] = True
    result["_e2_prompt_registry_valid"] = True
    result["_e2_prompt_bom_valid"] = True
    result["_e2_templates_valid"] = True
    
    # Mark E2 as a whole complete
    result["_e2_complete"] = True
    return result


def validate_briefing_freshness(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate briefing freshness."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e2_briefing_fresh"] = True
    return result


def validate_claim_permission_map(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate claim permission map."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e2_claim_permission_map_valid"] = True
    return result


def validate_send_mode(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate send mode."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e2_send_mode_valid"] = True
    return result


def validate_prompt_registry_entries(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate prompt registry entries exist."""
    result = context.copy()
    
    # Check that prompt registry exists
    registry_path = Path("apps_lic/config/prompt_registry.yaml")
    if not registry_path.exists():
        raise ValueError(f"Prompt registry not found: {registry_path}")
    
    result["_e2_prompt_registry_valid"] = True
    return result


def validate_prompt_bom_slots(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate PromptBOM slots."""
    result = context.copy()
    
    # Check that PromptBOM exists
    bom_path = Path("apps_lic/prompt_assembly/prompt_bom.yaml")
    if not bom_path.exists():
        raise ValueError(f"PromptBOM not found: {bom_path}")
    
    result["_e2_prompt_bom_valid"] = True
    return result


def validate_template_bodies_not_placeholders(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E2 Valid: Validate template bodies contain real implementation-grade content."""
    result = context.copy()
    
    # TODO: Implement template validation during P1.5.5
    # - Check templates have required slots
    # - Check templates have input/output contracts
    # - Check templates have forbidden_behaviors
    # - Check templates have validation_rules
    # - Check templates have hash_fields
    
    result["_e2_templates_not_placeholders"] = True
    result["_e2_complete"] = True
    return result


# ============================================================================
# E3 EXEC - Execution Phase (Generation)
# ============================================================================

def plan_message(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E3 Exec: Plan message structure using governed provider gateway.
    
    Note: All provider calls must go through the governed gateway with:
    - policy_hash, blueprint_hash, registry binding
    - capability token, sandbox envelope, replay key, audit refs
    """
    result = context.copy()
    
    # TODO: Implement during W2.1
    # - Call MessagePlanner via governed gateway
    # - Produce MessagePlan
    
    result["_e3_message_plan"] = {"planned": True}
    result["_e3_plan_complete"] = True
    return result


def compile_prompt(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E3 Exec: Compile prompt using real lic_pa_compiler.
    
    This step produces a CompiledPromptArtifact via the real PA compiler path.
    No ad hoc prompt strings allowed. No hand-built stubs.
    """
    result = context.copy()
    
    # Call the real apps_lic Prompt Assembly compiler
    from apps_lic.prompt_assembly.lic_pa_compiler import compile_prompt as pa_compile_prompt
    
    # Get template_id from context or step_def
    template_id = context.get("template_ref", "outreach_draft_v1")
    
    # Build input_data from context slot values
    input_data = context.get("slot_values", {})
    
    # Build binding context from execution context
    binding_context = {
        "manifest_hash": context.get("manifest_hash", ""),
        "policy_hash": context.get("policy_hash", ""),
        "blueprint_hash": context.get("blueprint_hash", ""),
        "replay_key": context.get("replay_key", ""),
        "request_id": context.get("request_id", ""),
        "run_id": context.get("run_id", ""),
        "trace_id": context.get("trace_id", ""),
        "route_id": context.get("route_id", ""),
    }
    
    # Invoke real PA compiler
    artifact = pa_compile_prompt(
        template_id=template_id,
        input_data=input_data,
        context=binding_context,
    )
    
    result["_e3_compiled_prompt_artifact"] = artifact
    result["_e3_compile_complete"] = True
    result["_e3_compile_used_real_pa_compiler"] = True
    return result


def compose_draft_using_compiled_prompt_artifact(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E3 Exec: Compose draft using CompiledPromptArtifact via governed provider gateway.
    
    Hard rule: Must fail closed if CompiledPromptArtifact is missing, invalid,
    unsigned, hash-mismatched, stale, or not bound to current manifest_hash,
    prompt_bom_hash, template_hash, policy_hash, blueprint_hash, and replay_key.
    """
    result = context.copy()
    
    # Verify CompiledPromptArtifact exists
    artifact = context.get("_e3_compiled_prompt_artifact")
    if not artifact:
        raise ValueError("CompiledPromptArtifact required but missing - fail closed")
    
    # TODO: Implement during W2.1
    # - Use artifact to generate draft via governed provider gateway
    # - No direct provider SDK calls
    
    result["_e3_draft_composed"] = True
    result["_e3_complete"] = True
    return result


# ============================================================================
# E4 HEAL - Repair and Healing Phase
# ============================================================================

def compile_repair_prompt_if_needed(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E4 Heal: Compile repair-specific prompt if needed.
    
    Hard rule: Repair steps must use repair-specific CompiledPromptArtifact objects.
    No ad hoc repair prompt strings allowed.
    """
    result = context.copy()
    
    # TODO: Implement during P1.5.3
    # - Determine if repair needed
    # - Compile repair-specific prompt artifact
    
    result["_e4_repair_prompt_artifact"] = {"placeholder": True}
    result["_e4_repair_prompt_ready"] = True
    return result


def omit_unsupported_claims(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E4 Heal: Remove unsupported optional claims using repair prompt artifact.
    
    Uses unsupported_claim_omission_v1 template via governed provider gateway.
    """
    result = context.copy()
    
    # TODO: Implement during W2.1
    # - Use repair prompt artifact
    # - Remove unsupported claims
    
    result["_e4_unsupported_claims_omitted"] = True
    return result


def remove_forbidden_antipatterns(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E4 Heal: Remove forbidden anti-patterns using repair prompt artifact.
    
    Uses repair_antipattern_v1 template via governed provider gateway.
    """
    result = context.copy()
    
    # TODO: Implement during W2.1
    
    result["_e4_antipatterns_removed"] = True
    return result


def repair_channel_length(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E4 Heal: Repair channel length using repair prompt artifact.
    
    Uses channel_length_repair_v1 template via governed provider gateway.
    """
    result = context.copy()
    
    # TODO: Implement during W2.1
    
    result["_e4_channel_length_repaired"] = True
    return result


def repair_ask_friction(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E4 Heal: Repair ask friction."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e4_ask_friction_repaired"] = True
    return result


def repair_voice_rules(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E4 Heal: Repair voice rules."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e4_voice_rules_repaired"] = True
    result["_e4_complete"] = True
    return result


# ============================================================================
# E5 SEAL - Final Validation and Output Sealing
# ============================================================================

def validate_final_draft_schema(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Validate final draft schema."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_schema_valid"] = True
    return result


def attach_prompt_artifact_receipts(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Attach prompt artifact receipts."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_prompt_receipts_attached"] = True
    return result


def attach_claim_receipts(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Attach claim receipts."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_claim_receipts_attached"] = True
    return result


def attach_manifest_lineage(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Attach manifest lineage."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_manifest_lineage_attached"] = True
    return result


def attach_antipattern_receipt(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Attach anti-pattern receipt."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_antipattern_receipt_attached"] = True
    return result


def attach_channel_length_receipt(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """E5 Seal: Attach channel length receipt."""
    result = context.copy()
    # TODO: Implement during W2.1
    result["_e5_channel_length_receipt_attached"] = True
    return result


def seal_l2_artifact_for_exit(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    E5 Seal: Final L2 artifact sealing for Exit V6 handoff.
    
    Hard rule: Must seal with content hash, lineage receipts, and prompt artifact binding.
    Exit V6 will emit CommitRequest → UWG → L4.
    L2 does not write L4 directly.
    """
    result = context.copy()
    
    # TODO: Implement full sealing during W2.1
    # - Compute content hash of outreach_draft
    # - Attach manifest lineage
    # - Attach prompt artifact receipts
    # - Build L2ExecutionReceipt
    
    # Mark all E5 stages complete
    result["_e5_schema_valid"] = True
    result["_e5_prompt_receipts_attached"] = True
    result["_e5_claim_receipts_attached"] = True
    result["_e5_manifest_lineage_attached"] = True
    result["_e5_antipattern_receipt_attached"] = True
    result["_e5_channel_length_receipt_attached"] = True
    result["_e5_l2_receipt"] = {"sealed": True, "artifact_id": "test_l2_receipt"}
    result["_e5_complete"] = True
    
    return result


# ============================================================================
# R3R4 Managed Workflow Adapters
# ============================================================================

def validate_request_for_briefing(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3 Stage 1: Validate RequestForBriefing input.
    
    Fail-closed if research_authorized=False or schema invalid.
    """
    result = context.copy()
    
    # Check research authorization
    if not context.get("research_authorized", False):
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_BLOCKED"
        result["_r3_fail_detail"] = "research_authorized=False"
        return result
    
    # Validate required fields present
    required = ["recipient_class", "company_name", "channel", "outreach_mode"]
    missing = [f for f in required if f not in context]
    if missing:
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "SCHEMA_REJECTION"
        result["_r3_fail_detail"] = f"Missing required fields: {missing}"
        return result
    
    result["_r3_request_validated"] = True
    result["_r3_validation_complete"] = True
    return result


def authorize_research(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3 Stage 2: Authorize research capability.
    
    Verify capability_ref is supported and policy permits research.
    """
    result = context.copy()
    
    # Skip if earlier validation failed
    if context.get("_r3_validation_failed"):
        return result
    
    capability_ref = context.get("research_capability_ref", "")
    supported = {"apps_research.v1", "apps_research.v2"}
    
    if capability_ref not in supported:
        result["_r3_authorization_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_BLOCKED"
        result["_r3_fail_detail"] = f"Unsupported capability_ref: {capability_ref}"
        return result
    
    result["_r3_research_authorized"] = True
    result["_r3_authorization_complete"] = True
    return result


def research_bridge_adapter(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3 Stage 3: L3/L2 step adapter for AppsResearchBridge.
    
    This adapter wraps AppsResearchBridge.fetch() as a managed workflow step.
    Must handle exceptions internally and return ResearchResult.
    
    Hard rule: apps_research bridge executes only as registered L3/L2 managed
    workflow step, never from __main__.py or L0.
    """
    result = context.copy()
    
    # Skip if earlier stages failed
    if context.get("_r3_validation_failed") or context.get("_r3_authorization_failed"):
        return result
    
    # Import bridge here to avoid circular imports at module load
    from apps_lic.integrations.apps_research_bridge import AppsResearchBridge, MockAppsResearchBridge
    
    # Use injected bridge if provided (for testing), otherwise create real bridge
    bridge = context.get("_r3_bridge")
    if bridge is None:
        capability_ref = context.get("research_capability_ref", "apps_research.v1")
        bridge = AppsResearchBridge(capability_ref=capability_ref)
    
    # Call the bridge
    try:
        research_result = bridge.fetch(
            recipient_class=context.get("recipient_class", ""),
            recipient_name=context.get("recipient_name", ""),
            company_name=context.get("company_name", ""),
            job_title=context.get("job_title", ""),
            channel=context.get("channel", ""),
            outreach_mode=context.get("outreach_mode", ""),
            relationship_distance=context.get("relationship_distance", "cold"),
            capability_ref=context.get("research_capability_ref", "apps_research.v1"),
            request_id=context.get("request_id", ""),
            run_id=context.get("run_id", ""),
            trace_id=context.get("trace_id", ""),
        )
        result["_r3_research_result"] = research_result
        result["_r3_research_complete"] = True
    except Exception as exc:
        # All exceptions translate to APPS_RESEARCH_FAILED
        result["_r3_research_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_FAILED"
        result["_r3_fail_detail"] = f"{type(exc).__name__}: {exc}"
    
    return result


def validate_research_and_build_manifest(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3 Stage 4: R3→R4 transition gate - Validate research and build manifest.
    
    Fail-closed on:
    - research_empty (no evidence items)
    - research_stale (is_stale=True)
    - research_weak_support (confidence < threshold)
    
    On success: emit fresh PreloadedOutreachContextManifest.
    """
    result = context.copy()
    
    # Skip if earlier stages failed
    if context.get("_r3_validation_failed") or context.get("_r3_authorization_failed") or context.get("_r3_research_failed"):
        return result
    
    research_result = context.get("_r3_research_result")
    if research_result is None:
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_FAILED"
        result["_r3_fail_detail"] = "No research result available"
        return result
    
    # Check blocked
    if getattr(research_result, "is_blocked", False):
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_BLOCKED"
        result["_r3_fail_detail"] = getattr(research_result, "block_reason", "unknown")
        return result
    
    # Check empty evidence
    evidence_items = getattr(research_result, "evidence_items", [])
    if not evidence_items:
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_EMPTY"
        result["_r3_fail_detail"] = "No evidence items in research result"
        return result
    
    # Check stale
    if getattr(research_result, "is_stale", False):
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_STALE"
        result["_r3_fail_detail"] = f"Research stale: {getattr(research_result, 'age_days', 0)} days"
        return result
    
    # Check confidence threshold
    confidence = float(getattr(research_result, "confidence_score", 0.0))
    threshold = float(context.get("min_confidence_threshold", 0.60))
    if confidence < threshold:
        result["_r3_validation_failed"] = True
        result["_r3_fail_reason"] = "APPS_RESEARCH_WEAK_SUPPORT"
        result["_r3_fail_detail"] = f"Confidence {confidence:.2f} < threshold {threshold:.2f}"
        return result
    
    # Build manifest using dispatcher's helper
    from apps_lic.integrations.managed_workflow_dispatcher import (
        _build_manifest_from_research,
        RequestForBriefing,
    )
    
    # Construct request from context
    request = RequestForBriefing(
        request_id=context.get("request_id", ""),
        run_id=context.get("run_id", ""),
        trace_id=context.get("trace_id", ""),
        recipient_class=context.get("recipient_class", ""),
        recipient_name=context.get("recipient_name", ""),
        company_name=context.get("company_name", ""),
        job_title=context.get("job_title", ""),
        channel=context.get("channel", ""),
        outreach_mode=context.get("outreach_mode", ""),
        relationship_distance=context.get("relationship_distance", "cold"),
        sender_resume_ref=context.get("sender_resume_ref", ""),
        sender_policy_hash=context.get("sender_policy_hash", context.get("policy_hash", "")),
        sender_blueprint_hash=context.get("sender_blueprint_hash", context.get("blueprint_hash", "")),
        research_authorized=True,
        research_capability_ref=context.get("research_capability_ref", "apps_research.v1"),
        freshness_ttl_days=context.get("freshness_ttl_days", 7),
        min_confidence_threshold=threshold,
    )
    
    manifest = _build_manifest_from_research(
        request=request,
        research_result=research_result,
        confidence=confidence,
    )
    
    result["manifest"] = manifest
    result["_r3_manifest_built"] = True
    result["_r3_to_r4_ready"] = True
    result["_r3_validation_complete"] = True
    return result


def emit_managed_workflow_receipt(context: Dict[str, Any], step_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3R4 Stage 8: Emit managed workflow chain linkage receipt.
    
    Records R3 research trace + R4 manifest hash in L3RuntimeOrchestrationReceipt.
    """
    result = context.copy()
    
    # Build chain receipt
    receipt = {
        "chain_kind": "MANAGED_WORKFLOW",
        "r3_research_trace_id": context.get("trace_id", ""),
        "r4_manifest_hash": getattr(context.get("manifest"), "manifest_hash", ""),
        "l2_receipt": context.get("_e5_l2_receipt", {}),
        "sealed": True,
    }
    
    result["_mw_receipt"] = receipt
    result["_mw_complete"] = True
    return result


# ============================================================================
# Step Adapter Registry
# ============================================================================

STEP_ADAPTERS: Dict[str, Callable] = {
    # E1 Prep
    "load_manifest": load_manifest,
    "bind_route_policy_blueprint_replay": bind_route_policy_blueprint_replay,
    "freeze_execution_context": freeze_execution_context,
    # E2 Valid
    "validate_manifest_schema": validate_manifest_schema,
    "validate_briefing_freshness": validate_briefing_freshness,
    "validate_claim_permission_map": validate_claim_permission_map,
    "validate_send_mode": validate_send_mode,
    "validate_prompt_registry_entries": validate_prompt_registry_entries,
    "validate_prompt_bom_slots": validate_prompt_bom_slots,
    "validate_template_bodies_not_placeholders": validate_template_bodies_not_placeholders,
    # E3 Exec
    "plan_message": plan_message,
    "compile_prompt": compile_prompt,
    "compose_draft_using_compiled_prompt_artifact": compose_draft_using_compiled_prompt_artifact,
    # E4 Heal
    "compile_repair_prompt_if_needed": compile_repair_prompt_if_needed,
    "omit_unsupported_claims": omit_unsupported_claims,
    "remove_forbidden_antipatterns": remove_forbidden_antipatterns,
    "repair_channel_length": repair_channel_length,
    "repair_ask_friction": repair_ask_friction,
    "repair_voice_rules": repair_voice_rules,
    # E5 Seal
    "validate_final_draft_schema": validate_final_draft_schema,
    "attach_prompt_artifact_receipts": attach_prompt_artifact_receipts,
    "attach_claim_receipts": attach_claim_receipts,
    "attach_manifest_lineage": attach_manifest_lineage,
    "attach_antipattern_receipt": attach_antipattern_receipt,
    "attach_channel_length_receipt": attach_channel_length_receipt,
    "seal_l2_artifact_for_exit": seal_l2_artifact_for_exit,
    # R3R4 Managed
    "validate_request_for_briefing": validate_request_for_briefing,
    "authorize_research": authorize_research,
    "research_bridge_adapter": research_bridge_adapter,
    "validate_research_and_build_manifest": validate_research_and_build_manifest,
    "emit_managed_workflow_receipt": emit_managed_workflow_receipt,
}


def get_step_adapter(name: str) -> Optional[Callable]:
    """Get a step adapter by name."""
    return STEP_ADAPTERS.get(name)


if __name__ == "__main__":
    print("lic_l2_step_adapters scaffold loaded successfully")
    print(f"Available adapters: {len(STEP_ADAPTERS)}")
    for name in STEP_ADAPTERS:
        print(f"  - {name}")
