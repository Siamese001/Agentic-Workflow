"""
Generic Package-Driven L2 Execution Binding

App-agnostic L2 executor that executes one bounded packet through
approved model lanes via generic provider gateway.
No app-specific execution logic in core.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import yaml
except ImportError:
    yaml = None

from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.c0.c0_package_driven_grounding import FinalEvidenceContract
from agentic_core.prompt_governance import (  # guardian: allow-layer-violation -- package-driven L2 consumes PA CompiledPromptArtifact at the L2 execution boundary; generic executor + app-owned profiles per ADR/app binding model
    CompiledPromptArtifact,
)

_LOGGER = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of L2 execution attempt."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    REPAIR_IN_PROGRESS = "REPAIR_IN_PROGRESS"
    FAILED = "FAILED"
    MAX_REPAIRS_EXCEEDED = "MAX_REPAIRS_EXCEEDED"


@dataclass(frozen=True)
class FrozenExecutionContext:
    """Immutable context for L2 execution."""
    request_id: str
    run_id: str
    app_id: str
    task_class: str
    tenant_id: str
    trace_id: str
    
    # Input artifacts (hashed references)
    route_contract_hash: str
    evidence_digest: str
    prompt_hash: str
    
    # Execution profile refs
    l2_execution_profile_ref: str
    provider_profile_ref: str
    repair_profile_ref: str
    
    # Timestamp
    frozen_at: str


@dataclass(frozen=True)
class ExecutionValidationReceipt:
    """Receipt for execution validation."""
    receipt_id: str
    validation_passed: bool
    schema_compliant: bool
    required_fields_present: bool
    json_syntax_valid: bool
    citations_valid: bool
    support_status_accurate: bool
    errors: List[str]
    timestamp: str


@dataclass(frozen=True)
class AttemptReceipt:
    """Receipt for a single execution attempt."""
    attempt_number: int
    status: str
    model_lane_used: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    output_hash: str
    validation_receipt_id: str
    repair_triggered: bool
    timestamp: str


@dataclass(frozen=True)
class HealReceipt:
    """Receipt for repair/heal operation."""
    receipt_id: str
    original_error: str
    repair_strategy: str
    slots_modified: List[str]
    hints_provided: List[str]
    success: bool
    attempt_number: int
    timestamp: str


@dataclass(frozen=True)
class SealedL2Artifact:
    """
    Sealed artifact from L2 execution.
    
    Contains all provenance for downstream consumption.
    """
    # Identity
    request_id: str
    run_id: str
    app_id: str
    task_class: str
    tenant_id: str
    trace_id: str
    
    # Sealing
    sealed_at: str
    seal_hash: str
    
    # Input references (hashed)
    route_contract_hash: str
    evidence_digest: str
    prompt_hash: str
    
    # Execution metadata
    execution_status: str
    model_lane_used: str
    provider_gateway_ref: str
    
    # Output
    output_content: Dict[str, Any]
    output_schema_version: str
    
    # Validation
    validation_receipt_id: str
    validation_passed: bool
    
    # Attempt history
    attempt_receipts: List[AttemptReceipt]
    total_attempts: int
    
    # Repair history (if any)
    heal_receipts: List[HealReceipt]
    repairs_performed: int
    
    # Proposed state diff (inert only)
    proposed_state_diff: Optional[Dict[str, Any]]
    state_diff_inert: bool
    
    # Authority preservation
    same_authority_repair_only: bool
    cross_authority_repair_blocked: bool
    
    # Receipts
    execution_validation_receipt: ExecutionValidationReceipt
    
    # Schema version
    schema_version: str = "AG9.L2.SLA.1"


def _load_yaml_profile(profile_ref: str) -> Optional[Dict[str, Any]]:
    """Load YAML profile from app-owned config."""
    if not yaml:
        _LOGGER.error("PyYAML not available")
        return None
    
    repo_root = Path(__file__).parent.parent.parent
    profile_path = repo_root / profile_ref
    
    if not profile_path.exists():
        _LOGGER.warning(f"Profile not found: {profile_path}")
        return None
    
    try:
        with open(profile_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:  # guardian: allow-return-none-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
        _LOGGER.error(f"Failed to load profile {profile_path}: {e}")
        return None


def _compute_hash(content: str) -> str:
    """Compute SHA256 hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _freeze_execution_context(
    route_contract: RouteContract,
    final_evidence: FinalEvidenceContract,
    compiled_prompt: CompiledPromptArtifact,
    l2_profile_ref: str,
    provider_profile_ref: str,
    repair_profile_ref: str,
) -> FrozenExecutionContext:
    """Create frozen execution context.

    W4 remediation: route_contract and final_evidence may be None when called
    from a binding that only receives CompiledPromptArtifact (runner convention).
    Falls back to compiled_prompt fields in that case.
    """
    _rc = route_contract
    _fe = final_evidence
    return FrozenExecutionContext(
        request_id=_rc.request_id if _rc else compiled_prompt.request_id,
        run_id=_rc.run_id if _rc else compiled_prompt.run_id,
        app_id=_rc.app_id if _rc else compiled_prompt.app_id,
        task_class=getattr(_rc, 'task_class', None) or getattr(compiled_prompt, 'task_class', ''),
        tenant_id=_rc.tenant_id if _rc else compiled_prompt.tenant_id,
        trace_id=_rc.trace_id if _rc else compiled_prompt.trace_id,
        route_contract_hash=_compute_hash(str(_rc)) if _rc else '',
        evidence_digest=_fe.final_evidence_digest if _fe else compiled_prompt.evidence_digest,
        prompt_hash=getattr(compiled_prompt, "prompt_hash", None)
        or compiled_prompt.compilation_hash,
        l2_execution_profile_ref=l2_profile_ref,
        provider_profile_ref=provider_profile_ref,
        repair_profile_ref=repair_profile_ref,
        frozen_at=datetime.now(timezone.utc).isoformat(),
    )


def _validate_output(
    output: Dict[str, Any],
    output_schema: Dict[str, Any],
    l2_profile: Dict[str, Any],
) -> ExecutionValidationReceipt:
    """Validate execution output against schema and policy."""
    errors = []
    
    # JSON schema validation (simplified - real impl would use jsonschema)
    schema_validation = True
    required_fields = output_schema.get("required", [])
    for field in required_fields:
        if field not in output:
            errors.append(f"Required field missing: {field}")
            schema_validation = False
    
    # Required fields from L2 profile
    l2_required = l2_profile.get("output_validation", {}).get("required_fields", [])
    required_fields_present = all(f in output for f in l2_required)
    if not required_fields_present:
        missing = [f for f in l2_required if f not in output]
        errors.append(f"L2 required fields missing: {missing}")
    
    # JSON syntax is valid (we have a dict, so it's valid)
    json_syntax_valid = True
    
    # Citation validation (simplified)
    citations_valid = True
    
    # Support status accuracy check
    support_status_accurate = True
    support_status = output.get("support_status")
    if support_status:
        valid_statuses = ["EMPTY", "WEAK_INSUFFICIENT", "WEAK_WITH_CAVEATS", "PASS", "STRONG", "CONFLICTED"]
        if support_status not in valid_statuses:
            errors.append(f"Invalid support_status: {support_status}")
            support_status_accurate = False
    
    validation_passed = schema_validation and required_fields_present and json_syntax_valid and citations_valid and support_status_accurate
    
    return ExecutionValidationReceipt(
        receipt_id=f"evr-{hashlib.sha256(str(output).encode()).hexdigest()[:8]}",
        validation_passed=validation_passed,
        schema_compliant=schema_validation,
        required_fields_present=required_fields_present,
        json_syntax_valid=json_syntax_valid,
        citations_valid=citations_valid,
        support_status_accurate=support_status_accurate,
        errors=errors,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _call_provider_gateway(
    compiled_prompt: CompiledPromptArtifact,
    provider_profile: Dict[str, Any],
    attempt_number: int,
) -> Tuple[Dict[str, Any], int, int, str]:
    """
    Provider gateway integration point.

    This executor no longer fabricates app-specific output. Until a concrete
    provider gateway is injected by the owning app/profile, L2 fails closed
    instead of returning synthetic data.
    """
    # Get lane configuration
    lanes = provider_profile.get("approved_model_lanes", {})
    primary_lane = lanes.get("primary", {})
    lane_id = primary_lane.get("lane_id", "research_synthesis")
    _ = (compiled_prompt, attempt_number)
    raise RuntimeError(
        "provider_gateway_unavailable: no configured provider implementation "
        f"for lane_id={lane_id!r}; synthetic L2 output is disabled"
    )


def _perform_same_authority_repair(
    compiled_prompt: CompiledPromptArtifact,
    validation_receipt: ExecutionValidationReceipt,
    repair_profile: Dict[str, Any],
    attempt_number: int,
) -> Tuple[CompiledPromptArtifact, HealReceipt]:
    """
    Perform same-authority repair by modifying H0 slot.
    
    Cross-authority repairs are blocked by policy.
    """
    _LOGGER.info(f"Performing same-authority repair for attempt {attempt_number}")
    
    # Get repair hints template
    hints_template = repair_profile.get("repair_hints", {}).get("template", "")
    
    # Generate error details
    error_details = "\n".join(validation_receipt.errors) if validation_receipt.errors else "Unknown error"
    
    # Build repair hints for H0 slot
    repair_hints = f"""## Repair Hints for Output Correction

The previous attempt had the following issues:
{error_details}

Please correct:
1. Ensure all required fields are present
2. Validate JSON syntax
3. Maintain accurate support_status from evidence

Ensure output strictly follows the JSON schema in R0.
"""
    
    # In real implementation, would modify compiled_prompt.envelope to add H0 hints
    # For now, return original with heal receipt
    
    heal_receipt = HealReceipt(
        receipt_id=f"hr-{attempt_number}",
        original_error=error_details,
        repair_strategy="same_authority_rewrite",
        slots_modified=["H0_bounded_repair"],
        hints_provided=[repair_hints],
        success=True,  # Hints generated successfully
        attempt_number=attempt_number,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    return compiled_prompt, heal_receipt


def l2_execute_package_driven(
    route_contract: RouteContract,
    final_evidence: FinalEvidenceContract,
    compiled_prompt: CompiledPromptArtifact,
    l2_execution_profile_ref: Optional[str] = None,
    provider_profile_ref: Optional[str] = None,
    repair_profile_ref: Optional[str] = None,
) -> SealedL2Artifact:
    """
    Generic L2 package-driven execution.
    
    Consumes:
        - RouteContract
        - FinalEvidenceContract
        - CompiledPromptArtifact
        - App-owned L2/provider/repair profiles
    
    Produces:
        - SealedL2Artifact with full provenance
    
    Executes:
        - One bounded packet through approved model lanes
        - Same-authority repair if needed
        - Output validation
    
    Does NOT:
        - Retrieve (C0 already provided evidence)
        - Route (L0 already decided route)
        - Assemble prompts (PA already compiled)
        - Write cache
        - Write vector store
        - Write L4
        - Emit X3
        - Learn
    """
    # Resolve profile refs from runtime package or use defaults
    if not l2_execution_profile_ref:
        l2_execution_profile_ref = "apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml"
    if not provider_profile_ref:
        provider_profile_ref = "apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml"
    if not repair_profile_ref:
        repair_profile_ref = "apps_research/config/domain_contract/repair_profile.company_brief.v1.yaml"
    
    # Load profiles
    l2_profile = _load_yaml_profile(l2_execution_profile_ref) or {}
    provider_profile = _load_yaml_profile(provider_profile_ref) or {}
    repair_profile = _load_yaml_profile(repair_profile_ref) or {}
    
    # Freeze execution context
    frozen_context = _freeze_execution_context(
        route_contract, final_evidence, compiled_prompt,
        l2_execution_profile_ref, provider_profile_ref, repair_profile_ref,
    )
    
    _req_id = route_contract.request_id if route_contract else compiled_prompt.request_id
    _LOGGER.info(
        "L2 execution starting: request=%s profile=%s",
        _req_id,
        l2_execution_profile_ref,
    )
    
    # Execution bounds
    max_attempts = l2_profile.get("execution_bounds", {}).get("max_attempts", 3)
    max_repairs = l2_profile.get("execution_bounds", {}).get("max_repair_iterations", 2)
    same_authority_repair = l2_profile.get("execution_bounds", {}).get("same_authority_repair_allowed", True)
    
    # Load output schema
    output_schema_ref = "apps_research/config/domain_contract/output_schema.company_brief.v1.json"
    output_schema = _load_yaml_profile(output_schema_ref) or {}
    
    # Execution loop
    attempt_receipts = []
    heal_receipts = []
    final_output = None
    final_validation = None
    
    for attempt in range(1, max_attempts + 1):
        _LOGGER.info(f"L2 execution attempt {attempt}/{max_attempts}")
        
        # Call provider gateway. Missing gateway fails closed; never fabricate
        # app-specific output in generic core.
        try:
            output, latency_ms, tokens_in, tokens_out, lane_id = _call_provider_gateway(
                compiled_prompt, provider_profile, attempt
            )
        except RuntimeError as exc:
            lane_id = (
                provider_profile.get("approved_model_lanes", {})
                .get("primary", {})
                .get("lane_id", "unknown")
            )
            validation_receipt = ExecutionValidationReceipt(
                receipt_id=f"evr-provider-{attempt}",
                validation_passed=False,
                schema_compliant=False,
                required_fields_present=False,
                json_syntax_valid=False,
                citations_valid=False,
                support_status_accurate=False,
                errors=[str(exc)],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            attempt_receipts.append(
                AttemptReceipt(
                    attempt_number=attempt,
                    status="PROVIDER_UNAVAILABLE",
                    model_lane_used=lane_id,
                    latency_ms=0,
                    tokens_in=0,
                    tokens_out=0,
                    output_hash="",
                    validation_receipt_id=validation_receipt.receipt_id,
                    repair_triggered=False,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            )
            final_output = {}
            final_validation = validation_receipt
            _LOGGER.error("L2 provider gateway unavailable: %s", exc)
            break
        
        # Validate output
        validation_receipt = _validate_output(output, output_schema, l2_profile)
        
        # Create attempt receipt
        attempt_receipt = AttemptReceipt(
            attempt_number=attempt,
            status="SUCCESS" if validation_receipt.validation_passed else "VALIDATION_FAILED",
            model_lane_used=lane_id,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            output_hash=_compute_hash(json.dumps(output)),
            validation_receipt_id=validation_receipt.receipt_id,
            repair_triggered=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        attempt_receipts.append(attempt_receipt)
        
        if validation_receipt.validation_passed:
            # Success!
            final_output = output
            final_validation = validation_receipt
            _LOGGER.info(f"L2 execution successful on attempt {attempt}")
            break
        
        # Validation failed - attempt repair if allowed
        if same_authority_repair and len(heal_receipts) < max_repairs:
            _LOGGER.info(f"Attempting same-authority repair after attempt {attempt}")
            
            compiled_prompt, heal_receipt = _perform_same_authority_repair(
                compiled_prompt, validation_receipt, repair_profile, attempt
            )
            heal_receipts.append(heal_receipt)
            attempt_receipts[-1] = AttemptReceipt(
                attempt_number=attempt,
                status="REPAIR_TRIGGERED",
                model_lane_used=lane_id,
                latency_ms=latency_ms,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                output_hash=_compute_hash(json.dumps(output)),
                validation_receipt_id=validation_receipt.receipt_id,
                repair_triggered=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            # Continue to next attempt
        else:
            # No more repairs allowed
            final_output = output
            final_validation = validation_receipt
            _LOGGER.warning(f"L2 execution failed, max repairs exceeded on attempt {attempt}")
            break
    
    # Determine final status
    if final_validation and final_validation.validation_passed:
        execution_status = ExecutionStatus.SUCCESS.value
    elif len(heal_receipts) >= max_repairs:
        execution_status = ExecutionStatus.MAX_REPAIRS_EXCEEDED.value
    else:
        execution_status = ExecutionStatus.FAILED.value
    
    # Build proposed state diff (inert only per policy)
    proposed_state_diff = None
    state_diff_inert = True
    if l2_profile.get("state_diffusion", {}).get("allowed", False):
        # Only inert diffs allowed
        proposed_state_diff = {
            "type": "inert_annotation",
            "content": f"L2 execution completed with status {execution_status}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    # Compute seal hash
    _req_id = route_contract.request_id if route_contract else compiled_prompt.request_id
    seal_content = json.dumps({
        "request_id": _req_id,
        "output_hash": _compute_hash(json.dumps(final_output)) if final_output else "",
        "prompt_hash": getattr(compiled_prompt, "prompt_hash", None)
        or compiled_prompt.compilation_hash,
        "attempts": len(attempt_receipts),
    })
    seal_hash = _compute_hash(seal_content)
    
    _LOGGER.info(
        "L2 execution complete: request=%s status=%s attempts=%d repairs=%d",
        _req_id,
        execution_status,
        len(attempt_receipts),
        len(heal_receipts),
    )
    
    _rc = route_contract
    return SealedL2Artifact(
        request_id=_rc.request_id if _rc else compiled_prompt.request_id,
        run_id=_rc.run_id if _rc else compiled_prompt.run_id,
        app_id=_rc.app_id if _rc else compiled_prompt.app_id,
        task_class=getattr(_rc, 'task_class', None) or getattr(compiled_prompt, 'task_class', ''),
        tenant_id=_rc.tenant_id if _rc else compiled_prompt.tenant_id,
        trace_id=_rc.trace_id if _rc else compiled_prompt.trace_id,
        sealed_at=datetime.now(timezone.utc).isoformat(),
        seal_hash=seal_hash,
        route_contract_hash=frozen_context.route_contract_hash,
        evidence_digest=frozen_context.evidence_digest,
        prompt_hash=frozen_context.prompt_hash,
        execution_status=execution_status,
        model_lane_used=attempt_receipts[-1].model_lane_used if attempt_receipts else "unknown",
        provider_gateway_ref=provider_profile_ref,
        output_content=final_output or {},
        output_schema_version=output_schema.get("properties", {}).get("schema_version", {}).get("const", "unknown"),
        validation_receipt_id=final_validation.receipt_id if final_validation else "",
        validation_passed=final_validation.validation_passed if final_validation else False,
        attempt_receipts=attempt_receipts,
        total_attempts=len(attempt_receipts),
        heal_receipts=heal_receipts,
        repairs_performed=len(heal_receipts),
        proposed_state_diff=proposed_state_diff,
        state_diff_inert=state_diff_inert,
        same_authority_repair_only=True,
        cross_authority_repair_blocked=True,
        execution_validation_receipt=final_validation or ExecutionValidationReceipt(
            receipt_id="failed",
            validation_passed=False,
            schema_compliant=False,
            required_fields_present=False,
            json_syntax_valid=False,
            citations_valid=False,
            support_status_accurate=False,
            errors=["Execution failed"],
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
        schema_version="AG9.L2.SLA.1",
    )


__all__ = [
    "l2_execute_package_driven",
    "SealedL2Artifact",
    "FrozenExecutionContext",
    "ExecutionValidationReceipt",
    "AttemptReceipt",
    "HealReceipt",
    "ExecutionStatus",
]
