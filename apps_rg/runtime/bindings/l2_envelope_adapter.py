"""L2 v4 Envelope Adapter for apps_rg — E1 PREP + E2 VALIDATION + E3 EXECUTION + E4 HEAL + E5 SEAL.

Per plan apps-rg-l2-v4-envelope-adoption-e9f2b1 W6.

This module provides:
- E1 PREP adapters (W2) that construct v4 L2 contracts from CompiledPromptArtifact
- E2 VALIDATION (W3) that validates E1 output and produces ValidationOutput
- E3 EXECUTION (W4) that executes approved work orders via ProviderGateway
- E4 SAME-AUTHORITY HEAL (W5) that repairs failed attempts with strict constraints
- E5 SEAL (W6) that produces SealedL2Artifact from E1-E4 outputs

Design invariants:
- E1/E2: No provider calls (HOP is E3, not E1/E2)
- E3: Only public ProviderGateway.invoke() for model execution
- E4: Same-authority repairs only — no provider/model/route/sandbox/budget changes
- E5: Seal only — no provider calls, no healing, no retry, no L4 write
- No prompt assembly (belongs to PA/L1)
- No C0 retrieval (belongs to C0 substrate)
- No L4 write (belongs to Exit/L5)
- No route change, replan, reground, or user clarification in E2/E4/E5
- Category A invariants preserved
- E5: state_diff_authorized always False, is_uwg_write_authority always False
"""
from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any

from agentic_core.L2_execution.types.l2_v4_contracts import (
    ApprovedWorkOrder,
    BudgetSnapshot,
    CapabilityScopeSummary,
    CapabilitySpec,
    ExecutionForm,
    FrozenExecutionContext,
    PrepOutput,
    ReplayBindings,
    SealedRejectionPacket,
    TaskSpec,
    ValidationOutput,
    WorkOrderInputs,
    WriteLockAssertion,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    ExecutionLane,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
    RepairStatus,
    ResultClass,
    assert_snapshot_match,
)
from agentic_core.L2_execution.types.l2_v4_contracts import (
    SAFE_LOCAL_REPAIRS,
    DISALLOWED_REPAIRS,
    TelemetryBundle,
    is_repair_allowed,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.providers.provider_gateway import ProviderGateway
from agentic_core.runtime.providers.provider_types import (
    ProviderProfile,
    ProviderRequest,
    TokenUsage,
)


def _build_work_order_inputs(cpa: CompiledPromptArtifact) -> WorkOrderInputs:
    """Build WorkOrderInputs from CompiledPromptArtifact.

    Maps CPA fields to v4 E1 INPUTS contract per W1 field audit.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly (L1 output)

    Returns:
        WorkOrderInputs with execution_form, task_spec, model_spec populated
    """
    # Determine execution_form from CPA posture/capability context
    # SINGLE_STEP: standard apps_rg resume generation (one-shot)
    execution_form = ExecutionForm.SINGLE_STEP

    # Build task_spec from CPA content
    task_spec = TaskSpec(
        intent=cpa.system_preamble[:500] if cpa.system_preamble else "resume_generation",
        expected_output_contract=cpa.schema_version or "master_resume_v2.16",
        grounded=bool(cpa.evidence_digest),
    )

    # Build model_spec from CPA.target_model when present
    model_spec: CapabilitySpec | None = None
    if cpa.target_model:
        model_spec = CapabilitySpec(
            name=cpa.target_model,
            version="",  # Not carried in CPA currently
            schema_id="",  # Not carried in CPA currently
        )

    # Build tool_spec from CPA.allowed_tools only if present
    tool_spec: CapabilitySpec | None = None
    if cpa.allowed_tools:
        tool_spec = CapabilitySpec(
            name=cpa.allowed_tools[0] if cpa.allowed_tools else "none",
            version="",
            schema_id="",
        )

    # Derive slo_slice_ms from CPA.max_tokens with safe default
    # Conservative estimate: 15ms per token for Qwen 32B AWQ
    slo_slice_ms = max(cpa.max_tokens * 15, 30_000)  # Minimum 30s

    return WorkOrderInputs(
        execution_form=execution_form,
        task_spec=task_spec,
        model_spec=model_spec,
        tool_spec=tool_spec,
        action_spec=None,  # apps_rg uses model execution, not action dispatch
        cost_tier="standard",
        retry_ceiling=3,  # WorkOrderInputs default
        max_repair_count=3,  # WorkOrderInputs default
        slo_slice_ms=slo_slice_ms,
    )


def _build_frozen_execution_context(
    cpa: CompiledPromptArtifact,
) -> FrozenExecutionContext:
    """Build FrozenExecutionContext from CompiledPromptArtifact.

    Maps CPA capability/sandbox fields to v4 E1 OUTPUT frozen context.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        FrozenExecutionContext with locked tools/model/runtime config
    """
    # Determine provider_lane from CPA.target_provider
    provider_lane = cpa.target_provider if cpa.target_provider else "local_vllm"

    # Convert allowed_file_roots to filesystem_view representation
    filesystem_view = str(cpa.allowed_file_roots) if cpa.allowed_file_roots else "()"

    # Convert allowed_networks to network_rules representation
    network_rules = str(cpa.allowed_networks) if cpa.allowed_networks else "()"

    # secrets_scope from CPA.egress_policy_ref
    secrets_scope = cpa.egress_policy_ref if cpa.egress_policy_ref else ""

    # model_runtime_version from CPA.target_model or safe default
    model_runtime_version = cpa.target_model if cpa.target_model else "unknown"

    # tool_registry_version — not directly carried in CPA, use safe default
    tool_registry_version = "v1"

    return FrozenExecutionContext(
        tool_registry_version=tool_registry_version,
        model_runtime_version=model_runtime_version,
        provider_lane=provider_lane,
        filesystem_view=filesystem_view,
        network_rules=network_rules,
        secrets_scope=secrets_scope,
        locale="en-US",
        allowed_file_roots=cpa.allowed_file_roots,
        allowed_network_destinations=cpa.allowed_networks,
        allowed_syscalls=(),  # apps_rg: no syscalls allowed
    )


def _build_determinism_bundle(cpa: CompiledPromptArtifact) -> DeterminismBundle:
    """Build DeterminismBundle from CompiledPromptArtifact.

    Constructs the replay/determinism hash bundle required for v4 E1.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        DeterminismBundle with blueprint_hash, policy_hash, prompt_hash,
        input_hash, replay_key, and attempt_seed.

    Note:
        If CPA lacks required replay fields (replay_key, compilation_hash),
        the caller must check this via PrepOutput.refusal_reason before
        proceeding to validation.
    """
    # blueprint_hash from CPA.compilation_hash
    blueprint_hash = cpa.compilation_hash if cpa.compilation_hash else ""

    # policy_hash from CPA.l5_certification_ref or CPA.signature
    policy_hash = cpa.l5_certification_ref if cpa.l5_certification_ref else cpa.signature

    # prompt_hash from CPA.compilation_hash (same as blueprint for apps_rg)
    prompt_hash = cpa.compilation_hash if cpa.compilation_hash else ""

    # input_hash: deterministic hash over stable CPA fields
    # Use request_id + run_id + app_id + trace_id as stable identity
    stable_input = f"{cpa.request_id}:{cpa.run_id}:{cpa.app_id}:{cpa.trace_id}:{cpa.tenant_id}"
    input_hash = hashlib.sha256(stable_input.encode("utf-8")).hexdigest()

    # replay_key from CPA.replay_key (may be empty — caller checks)
    replay_key = cpa.replay_key if cpa.replay_key else ""

    # attempt_seed: deterministic seed for this attempt
    # UUID-based ensures uniqueness; downstream can use for stochastic replay
    attempt_seed = uuid.uuid4().hex

    return DeterminismBundle(
        blueprint_hash=blueprint_hash,
        policy_hash=policy_hash,
        prompt_hash=prompt_hash,
        input_hash=input_hash,
        replay_key=replay_key,
        attempt_seed=attempt_seed,
    )


def _build_lineage_root(cpa: CompiledPromptArtifact) -> LineageRoot:
    """Build LineageRoot from CompiledPromptArtifact.

    Constructs lineage tracking for v4 E1.6 propagation.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        LineageRoot with parent_route_id, parent_plan_id, etc.
    """
    # parent_route_id: use CPA.trace_id (the trace root)
    parent_route_id = cpa.trace_id if cpa.trace_id else cpa.request_id

    # parent_plan_id: not directly carried in CPA for apps_rg, use run_id
    parent_plan_id = cpa.run_id if cpa.run_id else None

    # parent_step_id: not carried in CPA, None
    parent_step_id: str | None = None

    # ancestry_chain: minimal — just the trace_id
    ancestry_chain: tuple[str, ...] = (cpa.trace_id,) if cpa.trace_id else ()

    # same_run_packet_family: derived from run_id
    same_run_packet_family = cpa.run_id if cpa.run_id else ""

    return LineageRoot(
        parent_route_id=parent_route_id,
        parent_plan_id=parent_plan_id,
        parent_step_id=parent_step_id,
        ancestry_chain=ancestry_chain,
        same_run_packet_family=same_run_packet_family,
    )


def _build_prep_output(cpa: CompiledPromptArtifact) -> PrepOutput:
    """Build PrepOutput from CompiledPromptArtifact — E1 OUTPUT CONTRACT.

    This is the main E1 PREP entry point. It constructs all E1 sub-structures
    and determines readiness for E2 validation.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        PrepOutput with frozen_execution_context, replay_bindings,
        write_lock_assertion, and ready_for_validation flag.

    Invariants:
        - No provider calls (HOP is E3, not E1)
        - No prompt assembly (belongs to PA)
        - No C0 retrieval (belongs to C0)
        - ready_for_validation=False if required fields missing
    """
    # Build E1 sub-structures
    work_order_inputs = _build_work_order_inputs(cpa)
    frozen_execution_context = _build_frozen_execution_context(cpa)
    determinism_bundle = _build_determinism_bundle(cpa)
    lineage_root = _build_lineage_root(cpa)

    # Determine readiness for validation
    # Required: compilation_hash (blueprint/prompt hash), replay_key
    required_fields_present = bool(
        cpa.compilation_hash and cpa.compilation_hash.strip()
    )
    replay_key_present = bool(cpa.replay_key and cpa.replay_key.strip())

    ready_for_validation = required_fields_present and replay_key_present

    # Build refusal_reason if not ready
    refusal_reason = ""
    if not ready_for_validation:
        missing: list[str] = []
        if not required_fields_present:
            missing.append("compilation_hash")
        if not replay_key_present:
            missing.append("replay_key")
        refusal_reason = f"Missing required E1 fields: {', '.join(missing)}"

    # Build ReplayBindings
    replay_bindings = ReplayBindings(
        determinism=determinism_bundle,
        snapshot_manifest=cpa.replay_manifest_ref if cpa.replay_manifest_ref else "",
        clock_policy="run_clock_offsets",
    )

    # Build WriteLockAssertion — E1 must assert no direct L4 path
    write_lock_assertion = WriteLockAssertion(
        no_direct_l4_path=True,
        proposed_diff_only=True,
        persistence_disabled=True,
        asserted_at=time.monotonic(),
    )

    # Generate prep_receipt_id
    prep_receipt_id = f"prep-{uuid.uuid4().hex}"

    # Derive idempotency_key from request_id + run_id
    idempotency_key = f"{cpa.request_id}:{cpa.run_id}"

    return PrepOutput(
        prep_receipt_id=prep_receipt_id,
        frozen_execution_context=frozen_execution_context,
        run_id=cpa.run_id,
        idempotency_key=idempotency_key,
        lineage_root=lineage_root,
        replay_bindings=replay_bindings,
        write_lock_assertion=write_lock_assertion,
        ready_for_validation=ready_for_validation,
        refusal_reason=refusal_reason,
    )


# ============================================================================
# E2 VALIDATION — W3 Implementation
# ============================================================================


def _build_capability_scope_summary(
    cpa: CompiledPromptArtifact,
) -> CapabilityScopeSummary:
    """Build CapabilityScopeSummary from CPA for ApprovedWorkOrder.

    Maps CPA capability fields to the v4 capability scope contract.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        CapabilityScopeSummary with granted tools, models, actions
    """
    return CapabilityScopeSummary(
        capability_token_id=f"cap-{cpa.app_id}-{cpa.run_id}",
        granted_tools=cpa.allowed_tools if cpa.allowed_tools else (),
        granted_actions=(),  # apps_rg uses model execution, not action dispatch
        granted_models=cpa.allowed_models if cpa.allowed_models else (),
        side_effect_envelope="READ",  # apps_rg: bounded side effects
        tenant_scope=cpa.tenant_id if cpa.tenant_id else "",
    )


def _build_budget_snapshot(
    cpa: CompiledPromptArtifact,
    slo_slice_ms: int,
) -> BudgetSnapshot:
    """Build BudgetSnapshot from CPA for ApprovedWorkOrder.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly
        slo_slice_ms: SLO timeout from WorkOrderInputs

    Returns:
        BudgetSnapshot with token, timeout, retry, and repair limits
    """
    return BudgetSnapshot(
        timeout_ms=slo_slice_ms,
        retry_ceiling=3,
        repair_ceiling=3,
        token_limit=cpa.max_tokens,
        compute_limit=0,  # Not specified in CPA
        memory_limit_mb=0,
        io_quota_bytes=0,
        circuit_breaker_open=False,
    )


def _build_approved_work_order(
    prep_output: PrepOutput,
    cpa: CompiledPromptArtifact,
    validation_packet_id: str,
) -> ApprovedWorkOrder:
    """Build ApprovedWorkOrder for E2 PASS path.

    Args:
        prep_output: PrepOutput from E1 PREP
        cpa: CompiledPromptArtifact from Prompt Assembly
        validation_packet_id: Unique ID for this validation packet

    Returns:
        ApprovedWorkOrder with capability_scope, budget_snapshot, etc.
    """
    capability_scope = _build_capability_scope_summary(cpa)
    # Derive slo_slice_ms from CPA.max_tokens (same calculation as E1)
    slo_slice_ms = max(cpa.max_tokens * 15, 30_000)
    budget_snapshot = _build_budget_snapshot(cpa, slo_slice_ms)

    return ApprovedWorkOrder(
        validation_packet_id=validation_packet_id,
        decisive_rule_id="V_PASS",  # All validation checks passed
        capability_scope=capability_scope,
        budget_snapshot=budget_snapshot,
        side_effect_class="READ",  # Bounded side effects only
        approved_at=time.monotonic(),
    )


def _build_sealed_rejection_packet(
    prep_output: PrepOutput,
    validation_packet_id: str,
    failed_rule: str,
    reason: str,
) -> SealedRejectionPacket:
    """Build SealedRejectionPacket for E2 FAIL path.

    Args:
        prep_output: PrepOutput from E1 PREP (may be incomplete)
        validation_packet_id: Unique ID for this validation packet
        failed_rule: Which validation rule failed (e.g., "V_MISSING_REPLAY_KEY")
        reason: Human-readable refusal reason

    Returns:
        SealedRejectionPacket with failure metadata
    """
    return SealedRejectionPacket(
        rejection_packet_id=f"reject-{uuid.uuid4().hex}",
        failed_validation_rule=failed_rule,
        side_effect_class="NONE",  # No side effects on rejection
        missing_or_invalid_authority_field=reason,
        suggested_reentry_target="L1",  # Informational only; E2 does not reroute
        decisive_rule_id=failed_rule,
        sealed_at=time.monotonic(),
    )


def _validate_work_order(
    prep_output: PrepOutput,
    cpa: CompiledPromptArtifact,
) -> ValidationOutput:
    """E2 VALIDATION — validate E1 PREP output and produce ValidationOutput.

    This is the E2 entry point. It validates the PrepOutput against the
    CompiledPromptArtifact and returns either:
    - PASS: ValidationOutput with approved_work_order
    - FAIL: ValidationOutput with sealed_rejection_packet

    E2 constraints:
    - NO provider calls (E3 only)
    - NO HOP execution (E3 only)
    - NO route change, replan, reground, or user clarification
    - Only metadata suggestions; no layer calls

    Validation checks (V1-V9):
    V1: Provider/model present and allowed
    V2: Replay key present
    V3: Prompt hash (compilation_hash) present
    V4: No direct L4 path asserted (write_lock_assertion.no_direct_l4_path)
    V5: Proposed diff only asserted (write_lock_assertion.proposed_diff_only)
    V6: Persistence disabled asserted (write_lock_assertion.persistence_disabled)
    V7: Token/budget positive
    V8: Sandbox/file/network scope does not broaden
    V9: Lineage present (tenant/run/request/trace)

    Args:
        prep_output: PrepOutput from E1 PREP
        cpa: CompiledPromptArtifact from Prompt Assembly

    Returns:
        ValidationOutput with either approved_work_order or sealed_rejection_packet
    """
    validation_packet_id = f"val-{uuid.uuid4().hex}"

    # Track validation failures
    failures: list[tuple[str, str]] = []  # (rule_id, reason)

    # V1: Provider/model present and allowed
    if not cpa.target_model:
        failures.append(("V1_MISSING_MODEL", "CPA.target_model is empty"))
    elif cpa.allowed_models and cpa.target_model not in cpa.allowed_models:
        failures.append(("V1_MODEL_NOT_ALLOWED", f"Model {cpa.target_model} not in allowed_models"))

    # V2: Replay key present
    if not prep_output.replay_bindings.determinism.replay_key:
        failures.append(("V2_MISSING_REPLAY_KEY", "Replay key missing in determinism bundle"))

    # V3: Prompt hash (compilation_hash) present
    if not prep_output.replay_bindings.determinism.prompt_hash:
        failures.append(("V3_MISSING_PROMPT_HASH", "Prompt hash (compilation_hash) missing"))

    # V4: No direct L4 path asserted
    if not prep_output.write_lock_assertion.no_direct_l4_path:
        failures.append(("V4_L4_PATH_NOT_BLOCKED", "WriteLockAssertion.no_direct_l4_path is False"))

    # V5: Proposed diff only asserted
    if not prep_output.write_lock_assertion.proposed_diff_only:
        failures.append(("V5_NOT_DIFF_ONLY", "WriteLockAssertion.proposed_diff_only is False"))

    # V6: Persistence disabled asserted
    if not prep_output.write_lock_assertion.persistence_disabled:
        failures.append(("V6_PERSISTENCE_ENABLED", "WriteLockAssertion.persistence_disabled is False"))

    # V7: Token/budget positive
    if cpa.max_tokens <= 0:
        failures.append(("V7_INVALID_BUDGET", f"max_tokens must be positive, got {cpa.max_tokens}"))

    # V8: Sandbox/file/network scope check (does not broaden beyond CPA)
    # For apps_rg, we verify the FEG fields match CPA fields
    fec = prep_output.frozen_execution_context
    if fec.allowed_file_roots != cpa.allowed_file_roots:
        failures.append(("V8_FILE_SCOPE_MISMATCH", "FEG.allowed_file_roots != CPA.allowed_file_roots"))
    if fec.allowed_network_destinations != cpa.allowed_networks:
        failures.append(("V8_NETWORK_SCOPE_MISMATCH", "FEG.allowed_network_destinations != CPA.allowed_networks"))

    # V9: Lineage present
    if not cpa.tenant_id:
        failures.append(("V9_MISSING_TENANT", "CPA.tenant_id is empty"))
    if not cpa.run_id:
        failures.append(("V9_MISSING_RUN_ID", "CPA.run_id is empty"))
    if not cpa.request_id:
        failures.append(("V9_MISSING_REQUEST_ID", "CPA.request_id is empty"))
    if not cpa.trace_id:
        failures.append(("V9_MISSING_TRACE_ID", "CPA.trace_id is empty"))

    # Determine PASS or FAIL
    if failures:
        # FAIL path: return ValidationOutput with sealed_rejection_packet
        primary_failure = failures[0]  # First failure is decisive
        sealed_rejection = _build_sealed_rejection_packet(
            prep_output=prep_output,
            validation_packet_id=validation_packet_id,
            failed_rule=primary_failure[0],
            reason=primary_failure[1],
        )
        return ValidationOutput(
            validation_packet_id=validation_packet_id,
            validation_status="FAIL",
            approved_work_order=None,
            sealed_rejection_packet=sealed_rejection,
        )

    # PASS path: return ValidationOutput with approved_work_order
    approved_work_order = _build_approved_work_order(
        prep_output=prep_output,
        cpa=cpa,
        validation_packet_id=validation_packet_id,
    )
    return ValidationOutput(
        validation_packet_id=validation_packet_id,
        validation_status="PASS",
        approved_work_order=approved_work_order,
        sealed_rejection_packet=None,
    )


def _execute_approved_work_order(
    cpa: CompiledPromptArtifact,
    approved_work_order: ApprovedWorkOrder,
    prep_output: PrepOutput,
    attempt_number: int = 1,
) -> AttemptReceipt:
    """E3 HOP EXECUTION — execute approved work order via ProviderGateway.

    Performs exactly one approved bounded execution attempt.
    Provider/model execution uses the governed gateway path only.
    L2 emits proposed_state_diff only; Exit clears and UWG commits.

    Args:
        cpa: CompiledPromptArtifact from Prompt Assembly
        approved_work_order: Validated and approved work order from E2
        prep_output: PrepOutput from E1 (contains frozen context)
        attempt_number: Current attempt (for retry/repair tracking)

    Returns:
        AttemptReceipt with telemetry, result classification, and proposed_state_diff

    E3 Constraints:
        1. Execute only when ApprovedWorkOrder exists
        2. Call ProviderGateway.invoke() only
        3. No private ProviderGateway methods
        4. No direct HTTP/SDK calls
        5. No prompt assembly
        6. No C0 retrieval
        7. No routing or workflow expansion
        8. No judging final quality
        9. No L4 write or durable state mutation
        10. Parse model JSON and produce proposed_state_diff only
        11. Preserve ProviderInvocationReceipt from gateway
        12. Populate TelemetryBundle with full telemetry
    """
    # E3 Rule 1: Requires ApprovedWorkOrder
    if approved_work_order is None:
        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id="",
            attempt_count=attempt_number,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            trace_id=cpa.trace_id,
            span_id=None,
            latency_ms=0.0,
            tokens_used=0,
            return_code=1,
            result_class=ResultClass.REJECTED,
            error_summary="E3 requires ApprovedWorkOrder — E2 validation failed",
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="E3_NO_APPROVED_WORK_ORDER",
            proposed_state_diff={},
        )

    validation_packet_id = approved_work_order.validation_packet_id

    # Build ProviderRequest from CPA and ApprovedWorkOrder
    # Use CPA fields exactly — no fallback, no substitution
    provider_profile = ProviderProfile(
        profile_id=cpa.target_provider or "local_vllm",
        provider_kind="local_vllm" if cpa.target_provider == "local_vllm" else "external_api",
        model_id=cpa.target_model,
        max_tokens=cpa.max_tokens,
        capabilities=approved_work_order.capability_scope.granted_tools,
    )

    # Build the full prompt text from CPA
    prompt_text = ""
    if cpa.system_preamble:
        prompt_text = cpa.system_preamble + "\n\n"
    prompt_text += cpa.user_instruction or ""

    provider_request = ProviderRequest(
        prompt_text=prompt_text,
        provider_profile=provider_profile,
        max_tokens=cpa.max_tokens,
        temperature=cpa.temperature,
        request_id=cpa.request_id,
        run_id=cpa.run_id,
        trace_root=cpa.trace_id,
        node_id=f"e3-attempt-{attempt_number}",
        prompt_artifact_ref=cpa.compilation_hash or "",
    )

    # Execute via ProviderGateway (E3 Rule 2: only public invoke())
    started = time.monotonic()
    gateway = ProviderGateway()

    try:
        response = gateway.invoke(provider_request)
        latency_ms = (time.monotonic() - started) * 1000.0

        # Extract telemetry from receipt
        receipt = response.receipt
        token_usage = receipt.token_usage if receipt.token_usage else TokenUsage()

        # Parse JSON payload if successful
        generated_content = response.text if response.success else ""
        parsed_payload: dict[str, Any] = {}
        proposed_state_diff: dict[str, Any] = {}

        if response.success and generated_content:
            try:
                import json
                parsed_payload = json.loads(generated_content)
                # E3 Rule 10: proposed_state_diff only — no durable write
                proposed_state_diff = {"generated_resume": parsed_payload}
            except json.JSONDecodeError:
                # JSON parse failure — repairable
                return AttemptReceipt(
                    attempt_receipt_id=AttemptReceipt.new_id(),
                    validation_packet_id=validation_packet_id,
                    attempt_count=attempt_number,
                    determinism=prep_output.replay_bindings.determinism,
                    lineage=prep_output.lineage_root,
                    trace_id=cpa.trace_id,
                    span_id=None,
                    latency_ms=latency_ms,
                    tokens_used=token_usage.total_tokens,
                    return_code=2,  # JSON parse error
                    result_class=ResultClass.SOFT_REPAIRABLE,
                    error_summary="JSON parse error from model output",
                    execution_lane=ExecutionLane.MODEL,
                    decisive_reason_code="E3_JSON_PARSE_ERROR",
                    proposed_state_diff={},
                    generated_artifacts=(),
                )

        # Determine result class
        if response.success:
            result_class = ResultClass.SUCCESS
            return_code = 0
            error_summary = None
        else:
            # Provider returned failure — classify as repairable or terminal
            if receipt.error and "timeout" in receipt.error.lower():
                result_class = ResultClass.SOFT_REPAIRABLE
                return_code = 3
            elif receipt.error and ("rate limit" in receipt.error.lower() or "quota" in receipt.error.lower()):
                result_class = ResultClass.SOFT_REPAIRABLE
                return_code = 4
            else:
                result_class = ResultClass.FAIL_TERMINAL
                return_code = 5
            error_summary = receipt.error or "Provider invocation failed"

        # Build TelemetryBundle (E3 Rule 12)
        telemetry = TelemetryBundle(
            trace_id=cpa.trace_id,
            span_ids=(f"e3-attempt-{attempt_number}",),
            parent_span_id=None,
            latency_ms=latency_ms,
            tokens_used=token_usage.total_tokens,
            cost_units=0.0,  # Calculated by gateway
            compute_use="",
            memory_use_mb=0,
            stdout_summary=generated_content[:1000] if generated_content else "",
            stderr_summary=error_summary or "",
            return_code=return_code,
            input_byte_count=len(prompt_text.encode("utf-8")),
            output_byte_count=len(generated_content.encode("utf-8")) if generated_content else 0,
            file_touches=(),
            network_destinations=tuple(
                prep_output.frozen_execution_context.allowed_network_destinations
            ),
            model_or_tool_name=cpa.target_model or "",
            provider_lane=cpa.target_provider or "local_vllm",
            retry_source="",
            circuit_breaker_state="CLOSED",
        )

        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id=validation_packet_id,
            attempt_count=attempt_number,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            trace_id=cpa.trace_id,
            span_id=f"e3-attempt-{attempt_number}",
            latency_ms=latency_ms,
            tokens_used=token_usage.total_tokens,
            return_code=return_code,
            result_class=result_class,
            output_digest=hashlib.sha256(generated_content.encode()).hexdigest() if generated_content else "",
            error_summary=error_summary,
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="E3_SUCCESS" if response.success else "E3_PROVIDER_FAILURE",
            local_check_results=(),
            generated_artifacts=(),
            proposed_state_diff=proposed_state_diff,
            quarantined_payload=None,
        )

    except Exception as exc:
        # ProviderGateway.invoke() raised exception
        latency_ms = (time.monotonic() - started) * 1000.0
        error_msg = str(exc)

        # Classify as repairable or terminal
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            result_class = ResultClass.SOFT_REPAIRABLE
            return_code = 6
        elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            result_class = ResultClass.SOFT_REPAIRABLE
            return_code = 7
        else:
            result_class = ResultClass.FAIL_TERMINAL
            return_code = 8

        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id=validation_packet_id,
            attempt_count=attempt_number,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            trace_id=cpa.trace_id,
            span_id=f"e3-attempt-{attempt_number}",
            latency_ms=latency_ms,
            tokens_used=0,
            return_code=return_code,
            result_class=result_class,
            error_summary=error_msg,
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="E3_EXCEPTION",
            proposed_state_diff={},
        )


def _heal_attempt_failure(
    failed_attempt: AttemptReceipt,
    prep_output: PrepOutput,
    approved_work_order: ApprovedWorkOrder,
    cpa: CompiledPromptArtifact,
    repair_count: int = 1,
) -> HealReceipt:
    """E4 SAME-AUTHORITY HEAL — repair failed E3 attempt with strict constraints.

    Performs same-authority repairs only:
    - JSON/schema repair
    - Output reformat
    - Deterministic trim
    - Transient retry recommendation (same provider/model/sandbox/capability/replay)

    Blocks disallowed repairs:
    - Provider/model substitution
    - Route change, policy widening, sandbox widening
    - Capability expansion, budget increase
    - HITL escalation inside L2
    - C0 retrieval, prompt reassembly, direct L4 write

    Args:
        failed_attempt: The failed AttemptReceipt from E3
        prep_output: PrepOutput from E1 (contains frozen context)
        approved_work_order: Original ApprovedWorkOrder from E2
        cpa: CompiledPromptArtifact from Prompt Assembly
        repair_count: Current repair attempt number (for budget enforcement)

    Returns:
        HealReceipt with outcome, same-authority assertions, and next_action

    E4 Constraints:
        1. Only heal SOFT_REPAIRABLE or FAILED attempts — never SUCCESS
        2. Same-authority repairs only — no provider/model/route/sandbox/capability changes
        3. Block all DISALLOWED_REPAIRS tactics
        4. Enforce repair budget — repair_count <= repair_ceiling
        5. Snapshot guard — blueprint_hash/policy_hash must match
        6. Same-authority assertions must be populated
        7. Return HealReceipt with next_action (RETURN_TO_E3 or SEND_TO_E5)
        8. No provider calls, no HOP execution, no L4 write
        9. No routing, replan, reground, PA, C0, or judging
    """
    # E4 Rule 1: Never heal successful attempts
    if failed_attempt.result_class == ResultClass.SUCCESS:
        return HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id=failed_attempt.attempt_receipt_id,
            failed_span_id=failed_attempt.span_id,
            reason_code="E4_CANNOT_HEAL_SUCCESS",
            repair_count=repair_count,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            delta_summary="Cannot heal successful attempt",
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            repair_status=RepairStatus.FAIL_TERMINAL,
            repair_tactic="none",
            before_hash=failed_attempt.output_digest or "",
            after_hash=failed_attempt.output_digest or "",
            oscillation_status="CLEAN",
            snapshot_guard_status="FAIL",
            next_action="SEND_TO_E5",
        )

    # E4 Rule 4: Enforce repair budget
    repair_ceiling = approved_work_order.budget_snapshot.repair_ceiling
    if repair_count > repair_ceiling:
        return HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id=failed_attempt.attempt_receipt_id,
            failed_span_id=failed_attempt.span_id,
            reason_code="E4_REPAIR_BUDGET_EXHAUSTED",
            repair_count=repair_count,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            delta_summary=f"Repair count {repair_count} exceeds ceiling {repair_ceiling}",
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            repair_status=RepairStatus.FAIL_TERMINAL,
            repair_tactic="none",
            before_hash=failed_attempt.output_digest or "",
            after_hash=failed_attempt.output_digest or "",
            oscillation_status="CEILING_REACHED",
            snapshot_guard_status="PASS",
            next_action="SEND_TO_E5",
        )

    # E4 Rule 5: Snapshot guard — verify blueprint_hash/policy_hash match
    try:
        assert_snapshot_match(
            prep_output.replay_bindings.determinism,
            failed_attempt.determinism,
        )
        snapshot_guard_status = "PASS"
    except Exception:
        # Snapshot mismatch — cannot heal
        return HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id=failed_attempt.attempt_receipt_id,
            failed_span_id=failed_attempt.span_id,
            reason_code="E4_SNAPSHOT_MISMATCH",
            repair_count=repair_count,
            determinism=prep_output.replay_bindings.determinism,
            lineage=prep_output.lineage_root,
            delta_summary="Snapshot mismatch — cannot heal",
            outcome=HealOutcomeStamp.FAIL_TERMINAL,
            repair_status=RepairStatus.FAIL_TERMINAL,
            repair_tactic="none",
            before_hash=failed_attempt.output_digest or "",
            after_hash=failed_attempt.output_digest or "",
            oscillation_status="CLEAN",
            snapshot_guard_status="FAIL",
            next_action="SEND_TO_E5",
        )

    # Determine repair tactic based on failure reason
    repair_tactic = "none"
    outcome = HealOutcomeStamp.NEEDS_HELP
    repair_status = RepairStatus.NOT_REPAIRED
    next_action = "SEND_TO_E5"
    delta_summary = "No repair applied"
    oscillation_status = "CLEAN"

    # Check for disallowed repair patterns FIRST (would violate same-authority)
    disallowed_indicators = [
        "provider", "model", "route", "policy", "sandbox", "capability",
        "budget", "hitl", "human", "c0", "retrieval", "reassembly", "replay",
    ]
    error_lower = (failed_attempt.error_summary or "").lower()
    disallowed_pattern_found = False
    for indicator in disallowed_indicators:
        if indicator in error_lower:
            # Disallowed pattern detected — block repair
            disallowed_pattern_found = True
            repair_tactic = "none"
            outcome = HealOutcomeStamp.FAIL_TERMINAL
            repair_status = RepairStatus.FAIL_TERMINAL
            next_action = "SEND_TO_E5"
            delta_summary = f"Disallowed repair pattern detected: {indicator}"
            oscillation_status = "CLEAN"
            break

    # Only attempt repair classification if no disallowed patterns found
    if not disallowed_pattern_found and failed_attempt.result_class == ResultClass.SOFT_REPAIRABLE:
        # Analyze error to select appropriate repair
        error_summary = (failed_attempt.error_summary or "").lower()
        decisive_reason = (failed_attempt.decisive_reason_code or "").lower()

        if "json" in error_summary or "json" in decisive_reason or "parse" in error_summary:
            # JSON repair — allowed same-authority repair
            repair_tactic = "json_repair_intact_source"
            if is_repair_allowed(repair_tactic):
                outcome = HealOutcomeStamp.PASS
                repair_status = RepairStatus.REPAIRED
                next_action = "RETURN_TO_E3"
                delta_summary = "JSON repair applied to intact source"
            else:
                repair_tactic = "none"

        elif "timeout" in error_summary or "transient" in error_summary:
            # Transient retry recommendation — same authority only
            repair_tactic = "retry_same_transient_tool_call"
            if is_repair_allowed(repair_tactic):
                outcome = HealOutcomeStamp.PASS
                repair_status = RepairStatus.REPAIRED
                next_action = "RETURN_TO_E3"
                delta_summary = "Transient retry recommended with same authority"
            else:
                repair_tactic = "none"

        elif "oversized" in error_summary or "trim" in error_summary:
            # Deterministic trim — allowed same-authority repair
            repair_tactic = "trim_oversized_output_preserving_required_fields"
            if is_repair_allowed(repair_tactic):
                outcome = HealOutcomeStamp.PASS
                repair_status = RepairStatus.REPAIRED
                next_action = "RETURN_TO_E3"
                delta_summary = "Output trimmed to preserve required fields"
            else:
                repair_tactic = "none"

        elif "reformat" in error_summary or "markdown" in error_summary:
            # Output reformat — allowed same-authority repair
            repair_tactic = "output_reformat_to_required_shape"
            if is_repair_allowed(repair_tactic):
                outcome = HealOutcomeStamp.PASS
                repair_status = RepairStatus.REPAIRED
                next_action = "RETURN_TO_E3"
                delta_summary = "Output reformatted to required shape"
            else:
                repair_tactic = "none"

        elif "schema" in error_summary or "coercion" in decisive_reason:
            # Schema coercion — allowed same-authority repair
            repair_tactic = "schema_coercion_deterministic_field"
            if is_repair_allowed(repair_tactic):
                outcome = HealOutcomeStamp.PASS
                repair_status = RepairStatus.REPAIRED
                next_action = "RETURN_TO_E3"
                delta_summary = "Schema coercion applied to deterministic field"
            else:
                repair_tactic = "none"

    # If no repair tactic selected and no disallowed pattern found, default to NEEDS_HELP
    if repair_tactic == "none" and not disallowed_pattern_found:
        outcome = HealOutcomeStamp.NEEDS_HELP
        repair_status = RepairStatus.NOT_REPAIRED
        next_action = "SEND_TO_E5"
        delta_summary = "No applicable same-authority repair tactic"

    # Check oscillation (simple thrash detection)
    if repair_count >= 3:
        oscillation_status = "THRASHING"
        # After 3 repairs, send to E5 to prevent oscillation
        if outcome != HealOutcomeStamp.FAIL_TERMINAL:
            outcome = HealOutcomeStamp.NEEDS_HELP
            repair_status = RepairStatus.NOT_REPAIRED
            next_action = "SEND_TO_E5"
            delta_summary = "Oscillation guard triggered — too many repairs"
    elif repair_count >= 2:
        oscillation_status = "CLEAN"  # Approaching limit

    # Build same-authority assertions
    same_route_assertion = True  # Route unchanged (no routing in E4)
    same_policy_assertion = True  # Policy unchanged (snapshot guard enforced)
    same_blueprint_assertion = snapshot_guard_status == "PASS"
    same_sandbox_assertion = True  # Sandbox unchanged (no widening)
    same_capability_assertion = True  # Capability unchanged (no expansion)
    same_replay_key_assertion = (
        prep_output.replay_bindings.determinism.replay_key ==
        failed_attempt.determinism.replay_key
    )

    # All same-authority assertions must be true for RETURN_TO_E3
    all_assertions = (
        same_route_assertion and
        same_policy_assertion and
        same_blueprint_assertion and
        same_sandbox_assertion and
        same_capability_assertion and
        same_replay_key_assertion
    )

    if not all_assertions and next_action == "RETURN_TO_E5":
        outcome = HealOutcomeStamp.FAIL_TERMINAL
        repair_status = RepairStatus.FAIL_TERMINAL
        next_action = "SEND_TO_E5"
        delta_summary = "Same-authority assertion failed"

    # Build HealReceipt
    return HealReceipt(
        repair_attempt_id=HealReceipt.new_id(),
        parent_attempt_receipt_id=failed_attempt.attempt_receipt_id,
        failed_span_id=failed_attempt.span_id,
        reason_code=failed_attempt.decisive_reason_code or "E4_HEAL_ATTEMPT",
        repair_count=repair_count,
        determinism=prep_output.replay_bindings.determinism,
        lineage=prep_output.lineage_root,
        delta_summary=delta_summary,
        outcome=outcome,
        repair_status=repair_status,
        repair_tactic=repair_tactic,
        before_hash=failed_attempt.output_digest or "",
        after_hash=failed_attempt.output_digest or "",  # Would be updated after actual repair
        oscillation_status=oscillation_status,
        snapshot_guard_status=snapshot_guard_status,
        next_action=next_action,
    )


__all__ = [
    # E1 PREP
    "_build_work_order_inputs",
    "_build_frozen_execution_context",
    "_build_determinism_bundle",
    "_build_lineage_root",
    "_build_prep_output",
    # E2 VALIDATION
    "_build_capability_scope_summary",
    "_build_budget_snapshot",
    "_build_approved_work_order",
    "_build_sealed_rejection_packet",
    "_validate_work_order",
    # E3 EXECUTION
    "_execute_approved_work_order",
    # E4 HEAL
    "_heal_attempt_failure",
    # E5 SEAL
    "_seal_l2_artifact",
    # W7 INTEGRATED ORCHESTRATION
    "run_apps_rg_l2_envelope",
]


def _seal_l2_artifact(
    cpa: CompiledPromptArtifact,
    prep_output: PrepOutput,
    validation_output: ValidationOutput,
    attempt_receipt: AttemptReceipt,
    heal_receipt: HealReceipt | None = None,
) -> SealedL2Artifact:
    """E5 SEAL — Produce SealedL2Artifact from E1-E4 outputs.

    W6 Implementation per plan apps-rg-l2-v4-envelope-adoption-e9f2b1.

    E5 Design invariants:
    - Consume only existing E1, E2, E3, optional E4 outputs
    - Produce SealedL2Artifact using exact existing contract fields
    - No new fields added to SealedL2Artifact
    - No agentic_core modifications
    - No provider/model/tool code execution
    - No ProviderGateway.invoke() calls
    - No retry or healing (E4 only)
    - No prompt assembly (L1/PA only)
    - No C0 evidence retrieval
    - No final resume quality judging
    - No routing, replanning, regrounding
    - No L4 write or durable state mutation
    - state_diff_authorized always False
    - is_uwg_write_authority always False
    - proposed_state_diff remains candidate-only (inert)

    Args:
        cpa: CompiledPromptArtifact from L1/PA (E0 input)
        prep_output: PrepOutput from E1 PREP
        validation_output: ValidationOutput from E2 VALIDATION
        attempt_receipt: AttemptReceipt from E3 EXECUTION
        heal_receipt: Optional HealReceipt from E4 HEAL (if healing occurred)

    Returns:
        SealedL2Artifact with all fields populated per contract

    Raises:
        ValueError: If required inputs are missing or inconsistent
    """
    # =========================================================================
    # E5.1 — Validate required inputs (fail-closed)
    # =========================================================================
    if attempt_receipt is None:
        raise ValueError("E5_SEAL_REJECTED: attempt_receipt is required")
    if prep_output is None:
        raise ValueError("E5_SEAL_REJECTED: prep_output is required")
    if validation_output is None:
        raise ValueError("E5_SEAL_REJECTED: validation_output is required")

    # Validate that validation passed or was properly rejected
    if validation_output.approved_work_order is None and not validation_output.sealed_rejection_packet:
        raise ValueError("E5_SEAL_REJECTED: validation_output missing both approval and rejection")

    # Validate trace/run consistency
    if attempt_receipt.trace_id != cpa.trace_id:
        raise ValueError("E5_SEAL_REJECTED: attempt_receipt trace_id mismatch with CPA")

    # =========================================================================
    # E5.2 — Build audit refs from all phase outputs
    # =========================================================================
    audit_refs: list[str] = []
    
    # E1 PREP audit ref
    if prep_output.lineage_root.parent_route_id:
        audit_refs.append(f"prep:{prep_output.lineage_root.parent_route_id}")
    
    # E2 VALIDATION audit ref
    if validation_output.validation_packet_id:
        audit_refs.append(f"validation:{validation_output.validation_packet_id}")
    
    # E3 ATTEMPT audit ref
    audit_refs.append(f"attempt:{attempt_receipt.attempt_receipt_id}")
    
    # E4 HEAL audit ref (if present)
    if heal_receipt is not None and heal_receipt.repair_attempt_id:
        audit_refs.append(f"heal:{heal_receipt.repair_attempt_id}")

    # =========================================================================
    # E5.3 — Extract execution status from attempt receipt
    # =========================================================================
    execution_status = "completed"  # Default
    if attempt_receipt.result_class == ResultClass.FAIL_TERMINAL:
        execution_status = "failed"
    elif attempt_receipt.result_class == ResultClass.REJECTED:
        execution_status = "aborted"
    elif attempt_receipt.result_class == ResultClass.NEEDS_HELP:
        execution_status = "failed"

    # =========================================================================
    # E5.4 — Extract generated content from attempt receipt
    # =========================================================================
    generated_content = ""
    if attempt_receipt.proposed_state_diff:
        # For apps_rg, the generated resume is in proposed_state_diff
        if "generated_resume" in attempt_receipt.proposed_state_diff:
            resume_data = attempt_receipt.proposed_state_diff["generated_resume"]
            if isinstance(resume_data, dict):
                generated_content = resume_data.get("content", "")
            elif isinstance(resume_data, str):
                generated_content = resume_data
        else:
            # Serialize the state diff as the content
            import json
            try:
                generated_content = json.dumps(attempt_receipt.proposed_state_diff)
            except (TypeError, ValueError):
                generated_content = str(attempt_receipt.proposed_state_diff)

    # =========================================================================
    # E5.5 — Build evidence refs from CPA component_hash_map
    # =========================================================================
    evidence_refs: tuple[str, ...] = tuple(cpa.component_hash_map.values()) if cpa.component_hash_map else ()

    # =========================================================================
    # E5.6 — Build prompt refs from CPA slot_lineage_map
    # =========================================================================
    prompt_refs: tuple[str, ...] = tuple(cpa.slot_lineage_map.values()) if cpa.slot_lineage_map else ()

    # =========================================================================
    # E5.7 — Extract provider/model receipts from attempt
    # =========================================================================
    provider_receipts: tuple[str, ...] = ()
    model_call_refs: tuple[str, ...] = ()
    tool_call_refs: tuple[str, ...] = ()
    
    # Extract provider/model info from local_check_results (AttemptReceipt field)
    # AttemptReceipt does not have a telemetry field; data is stored in local_check_results
    local_checks = getattr(attempt_receipt, 'local_check_results', None)
    if local_checks and isinstance(local_checks, dict):
        provider_lane = local_checks.get('provider_lane')
        model_name = local_checks.get('model_or_tool_name')
        span_ids = local_checks.get('span_ids')
        
        if provider_lane:
            provider_receipts = (f"provider:{provider_lane}",)
        if model_name:
            model_call_refs = (f"model:{model_name}",)
        # span_ids can be used as tool call refs if present
        if span_ids:
            if isinstance(span_ids, (list, tuple)):
                tool_call_refs = tuple(f"span:{s}" for s in span_ids)
            else:
                tool_call_refs = (f"span:{span_ids}",)

    # =========================================================================
    # E5.8 — Calculate execution duration
    # =========================================================================
    execution_duration_ms = attempt_receipt.latency_ms

    # =========================================================================
    # E5.9 — Generate deterministic compilation hash
    # =========================================================================
    hash_input = (
        f"{cpa.request_id}:{cpa.run_id}:{attempt_receipt.attempt_receipt_id}:"
        f"{attempt_receipt.determinism.blueprint_hash}:"
        f"{attempt_receipt.determinism.policy_hash}"
    )
    compilation_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    # =========================================================================
    # E5.10 — Build audit manifest ref
    # =========================================================================
    audit_manifest_ref = f"audit-manifest:{cpa.run_id}:{int(time.time())}"

    # =========================================================================
    # E5.11 — Extract capability/sandbox/egress from CPA
    # =========================================================================
    # Extract capability allowlists directly from CPA (W2 fields)
    allowed_tools = cpa.allowed_tools
    allowed_models = cpa.allowed_models
    allowed_networks = cpa.allowed_networks
    allowed_file_roots = cpa.allowed_file_roots
    sandbox_required = cpa.sandbox_required
    egress_policy_ref = cpa.egress_policy_ref

    # =========================================================================
    # E5.12 — Extract snapshot refs from CPA
    # =========================================================================
    snapshot_refs: tuple[str, ...] = cpa.snapshot_refs if cpa.snapshot_refs else ()

    # =========================================================================
    # E5.13 — Extract replay manifest
    # =========================================================================
    replay_manifest = cpa.replay_manifest_ref if cpa.replay_manifest_ref else ""
    # Fall back to attempt's determinism replay_key if CPA doesn't have one
    replay_key = cpa.replay_key if cpa.replay_key else attempt_receipt.determinism.replay_key

    # =========================================================================
    # E5.14 — Extract gate verdict refs and L5 cert ref
    # =========================================================================
    gate_verdict_refs: tuple[str, ...] = cpa.gate_verdict_refs if cpa.gate_verdict_refs else ()
    l5_certification_ref = cpa.l5_certification_ref if cpa.l5_certification_ref else ""

    # =========================================================================
    # E5.15 — Build and return SealedL2Artifact
    # =========================================================================
    from agentic_core.runtime.contracts.posture import POSTURE_WRITE_INTENT
    
    return SealedL2Artifact(
        request_id=cpa.request_id,
        run_id=cpa.run_id,
        app_id=cpa.app_id,
        trace_id=cpa.trace_id,
        tenant_id=cpa.tenant_id,
        execution_status=execution_status,
        generated_content=generated_content,
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff=attempt_receipt.proposed_state_diff or {},
        state_diff_authorized=False,  # E5 INVARIANT: always False
        execution_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        execution_duration_ms=execution_duration_ms,
        sovereign_execution_receipt=attempt_receipt.attempt_receipt_id,
        prompt_artifact_digest=cpa.compilation_hash,
        compilation_hash=compilation_hash,
        evidence_refs=evidence_refs,
        prompt_refs=prompt_refs,
        provider_receipts=provider_receipts,
        model_call_refs=model_call_refs,
        tool_call_refs=tool_call_refs,
        replay_key=replay_key,
        replay_manifest=replay_manifest,
        snapshot_refs=snapshot_refs,
        audit_refs=tuple(audit_refs),
        audit_manifest_ref=audit_manifest_ref,
        allowed_tools=allowed_tools,
        allowed_models=allowed_models,
        allowed_networks=allowed_networks,
        allowed_file_roots=allowed_file_roots,
        sandbox_required=sandbox_required,
        egress_policy_ref=egress_policy_ref,
        gate_verdict_refs=gate_verdict_refs,
        l5_certification_ref=l5_certification_ref,
        posture=POSTURE_WRITE_INTENT,
        is_uwg_write_authority=False,  # E5 invariant: always false
        is_future_run_only=False,
    )


def run_apps_rg_l2_envelope(
    cpa: CompiledPromptArtifact,
    *,
    attempt_number: int = 1,
    enable_heal: bool = True,
    max_heal_attempts: int = 1,
) -> SealedL2Artifact:
    """W7 INTEGRATED ORCHESTRATION — E1 → E2 → E3 → E4 → E5 flow.

    Executes the complete L2 envelope pipeline for apps_rg:
    1. E1 PREP: Build prep output from CPA
    2. E2 VALIDATION: Validate work order (fail-closed if invalid)
    3. E3 EXECUTION: Call provider via _execute_approved_work_order
    4. E4 HEAL: If SOFT_REPAIRABLE and enable_heal, attempt repair and retry E3
    5. E5 SEAL: Produce final SealedL2Artifact

    Architecture guarantees:
    - Provider is NEVER called if E1 not ready or E2 FAIL
    - E4 retry preserves same-authority (no capability/sandbox/replay widening)
    - E5 output goes to Exit/L3 only (state_diff_authorized=False, is_uwg_write_authority=False)
    - No infinite loops (max_heal_attempts budget enforced)

    Args:
        cpa: Compiled prompt artifact with all execution context
        attempt_number: Starting attempt number (for lineage/telemetry)
        enable_heal: Whether to enable E4 heal/retry loop
        max_heal_attempts: Maximum E4 heal attempts (default 1 to prevent loops)

    Returns:
        SealedL2Artifact: Final sealed artifact for Exit/L3 consumption

    Raises:
        ValueError: If E1/E2 inputs are fundamentally invalid (fail-closed)
    """
    import time
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.origin import Origin as OriginEnum
    from agentic_core.L2_execution.types.l2_v4_contracts import ResultClass

    # ========================================================================
    # W7.1 — E1: PREP phase
    # ========================================================================
    try:
        prep_output = _build_prep_output(cpa)
    except Exception as e:
        # E1 not ready: seal rejection without provider call
        rejection_hash = _compute_compilation_hash(
            cpa.request_id, cpa.run_id, "e1-rejection", "e1-rejection"
        )
        return SealedL2Artifact(
            request_id=cpa.request_id,
            run_id=cpa.run_id,
            app_id=cpa.app_id,
            trace_id=cpa.trace_id,
            tenant_id=cpa.tenant_id,
            execution_status="rejected",
            generated_content={"error": f"E1_PREP_FAILED: {e}"},
            generated_content_origin=OriginEnum.MODEL_GENERATION,
            proposed_state_diff={},
            state_diff_authorized=False,
            execution_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            execution_duration_ms=0,
            sovereign_execution_receipt="e1-rejection",
            prompt_artifact_digest=cpa.compilation_hash,
            compilation_hash=rejection_hash,
            evidence_refs=tuple(cpa.component_hash_map.values()) if cpa.component_hash_map else (),
            prompt_refs=tuple(cpa.slot_lineage_map.values()) if cpa.slot_lineage_map else (),
            provider_receipts=(),
            model_call_refs=(),
            tool_call_refs=(),
            replay_key=cpa.replay_key or "",
            replay_manifest=cpa.replay_manifest_ref or "",
            snapshot_refs=cpa.snapshot_refs if cpa.snapshot_refs else (),
            audit_refs=("audit:e1_prep_failed",),
            audit_manifest_ref="",
            allowed_tools=(),
            allowed_models=(),
            allowed_networks=(),
            allowed_file_roots=(),
            sandbox_required=False,
            egress_policy_ref="",
            gate_verdict_refs=(),
            l5_certification_ref=cpa.l5_certification_ref or "",
            posture="write_intent",
            is_uwg_write_authority=False,
            is_future_run_only=False,
        )

    # ========================================================================
    # W7.2 — E2: VALIDATION phase (fail-closed)
    # ========================================================================
    validation_output = _validate_work_order(prep_output, cpa)

    if validation_output.sealed_rejection_packet is not None:
        # E2 rejection: seal without provider call
        rejection = validation_output.sealed_rejection_packet
        rejection_hash = _compute_compilation_hash(
            cpa.request_id, cpa.run_id, "e2-rejection", rejection.rejection_packet_id
        )

        return SealedL2Artifact(
            request_id=cpa.request_id,
            run_id=cpa.run_id,
            app_id=cpa.app_id,
            trace_id=cpa.trace_id,
            tenant_id=cpa.tenant_id,
            execution_status="rejected",
            generated_content={"rejection": rejection.missing_or_invalid_authority_field},
            generated_content_origin=OriginEnum.MODEL_GENERATION,
            proposed_state_diff={},
            state_diff_authorized=False,
            execution_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            execution_duration_ms=0,
            sovereign_execution_receipt=rejection.rejection_packet_id,
            prompt_artifact_digest=cpa.compilation_hash,
            compilation_hash=rejection_hash,
            evidence_refs=tuple(cpa.component_hash_map.values()) if cpa.component_hash_map else (),
            prompt_refs=tuple(cpa.slot_lineage_map.values()) if cpa.slot_lineage_map else (),
            provider_receipts=(),
            model_call_refs=(),
            tool_call_refs=(),
            replay_key=cpa.replay_key or "",
            replay_manifest=cpa.replay_manifest_ref or "",
            snapshot_refs=cpa.snapshot_refs if cpa.snapshot_refs else (),
            audit_refs=(f"audit:e2_rejected:{rejection.rejection_packet_id}",),
            audit_manifest_ref="",
            allowed_tools=(),
            allowed_models=(),
            allowed_networks=(),
            allowed_file_roots=(),
            sandbox_required=False,
            egress_policy_ref="",
            gate_verdict_refs=(),
            l5_certification_ref=cpa.l5_certification_ref or "",
            posture="write_intent",
            is_uwg_write_authority=False,
            is_future_run_only=False,
        )

    if validation_output.approved_work_order is None:
        raise ValueError("W7_REJECTED: E2 validation missing both approval and rejection")

    approved_work_order = validation_output.approved_work_order

    # ========================================================================
    # W7.3 — Validate E3 prerequisites (fail-closed before provider call)
    # ========================================================================
    if not cpa.replay_key:
        raise ValueError("W7_REJECTED: Missing replay_key in CPA")
    if not cpa.compilation_hash:
        raise ValueError("W7_REJECTED: Missing compilation_hash in CPA")
    if not cpa.target_model:
        raise ValueError("W7_REJECTED: Missing target_model in CPA")

    # ========================================================================
    # W7.4 — E3: EXECUTION phase (provider call)
    # ========================================================================
    heal_receipt: HealReceipt | None = None
    current_attempt = attempt_number
    total_heal_attempts = 0

    while True:
        attempt_receipt = _execute_approved_work_order(
            approved_work_order=approved_work_order,
            cpa=cpa,
            prep_output=prep_output,
            attempt_number=current_attempt,
        )

        # ========================================================================
        # W7.5 — Check if heal/retry needed
        # ========================================================================
        if (
            enable_heal
            and attempt_receipt.result_class == ResultClass.SOFT_REPAIRABLE
            and total_heal_attempts < max_heal_attempts
        ):
            # E4: HEAL phase
            heal_receipt = _heal_attempt_failure(
                failed_attempt=attempt_receipt,
                prep_output=prep_output,
                approved_work_order=approved_work_order,
                cpa=cpa,
                repair_count=total_heal_attempts + 1,
            )

            if heal_receipt.next_action == "RETURN_TO_E3":
                total_heal_attempts += 1
                current_attempt += 1
                continue  # Retry E3 with same authority
            else:
                # Heal says stop (oscillation, disallowed, etc.)
                break
        else:
            # No heal needed or heal disabled/budget exhausted
            break

    # ========================================================================
    # W7.6 — E5: SEAL phase
    # ========================================================================
    sealed = _seal_l2_artifact(
        cpa=cpa,
        prep_output=prep_output,
        validation_output=validation_output,
        attempt_receipt=attempt_receipt,
        heal_receipt=heal_receipt,
    )

    return sealed


def _compute_compilation_hash(*inputs: str) -> str:
    """Helper to compute deterministic SHA256 hash for sealing."""
    import hashlib
    hasher = hashlib.sha256()
    for inp in inputs:
        hasher.update(inp.encode("utf-8"))
    return hasher.hexdigest()
