"""L2 Handoff Contract (spec lines 1534-1572).

Defines the strict must / must-not list that L2 receives along with a
:class:`CompiledPromptArtifact`. Includes a validator that the L2
Sovereign LLM Gateway calls before invoking any provider SDK.
"""

from __future__ import annotations

from dataclasses import dataclass

L2_MUST: tuple[str, ...] = (
    "preserve_artifact_byte_for_byte",
    "verify_signature_against_manifest_inputs",
    "verify_replay_key_consistency",
    "use_only_provider_lane_specified",
    "use_only_model_id_specified",
    "use_only_tool_binding_manifest",
    "use_only_response_schema_R0",
    "respect_token_budget_ceiling",
    "emit_observability_spans_with_trace_root",
)


L2_MUST_NOT: tuple[str, ...] = (
    "modify_any_slot_content",
    "add_or_remove_tools",
    "add_or_remove_schema_fields",
    "exceed_temperature_or_thinking_level",
    "swap_provider_or_model",
    "downgrade_governance_posture",
    "skip_signature_verification",
    "treat_retrieved_content_as_instruction",
    "execute_non_grounded_outputs_as_facts_when_grounding_required",
)


@dataclass(frozen=True)
class L2HandoffValidationResult:
    valid: bool
    violations: tuple[str, ...]
    must_satisfied: tuple[str, ...]
    must_not_satisfied: tuple[str, ...]


def validate_l2_handoff(
    *,
    artifact_signature_verified: bool,
    artifact_bytes_match: bool,
    replay_key_matches: bool,
    provider_lane_used: str,
    artifact_provider_lane: str,
    model_id_used: str,
    artifact_model_id: str,
    tools_used: tuple[str, ...],
    artifact_tools: tuple[str, ...],
    schema_used: dict | None,
    artifact_schema: dict | None,
    budget_ceiling: int,
    tokens_emitted: int,
    spans_emitted_with_trace_root: bool,
    grounding_required: bool,
    grounded_output: bool,
) -> L2HandoffValidationResult:
    """Validate that L2 honored every must / must-not rule."""
    violations: list[str] = []
    satisfied_must: list[str] = []
    satisfied_must_not: list[str] = []

    # MUST checks
    if artifact_bytes_match:
        satisfied_must.append("preserve_artifact_byte_for_byte")
    else:
        violations.append("modify_any_slot_content")

    if artifact_signature_verified:
        satisfied_must.append("verify_signature_against_manifest_inputs")
    else:
        violations.append("skip_signature_verification")

    if replay_key_matches:
        satisfied_must.append("verify_replay_key_consistency")
    else:
        violations.append("verify_replay_key_consistency_failed")

    if provider_lane_used == artifact_provider_lane:
        satisfied_must.append("use_only_provider_lane_specified")
    else:
        violations.append("swap_provider_or_model")

    if model_id_used == artifact_model_id:
        satisfied_must.append("use_only_model_id_specified")
    elif "swap_provider_or_model" not in violations:
        violations.append("swap_provider_or_model")

    if set(tools_used) <= set(artifact_tools):
        satisfied_must.append("use_only_tool_binding_manifest")
    else:
        violations.append("add_or_remove_tools")

    if (schema_used or {}) == (artifact_schema or {}):
        satisfied_must.append("use_only_response_schema_R0")
    else:
        violations.append("add_or_remove_schema_fields")

    if budget_ceiling == 0 or tokens_emitted <= budget_ceiling:
        satisfied_must.append("respect_token_budget_ceiling")
    else:
        violations.append("exceed_temperature_or_thinking_level")

    if spans_emitted_with_trace_root:
        satisfied_must.append("emit_observability_spans_with_trace_root")
    else:
        violations.append("emit_observability_spans_with_trace_root_missing")

    # MUST-NOT specific checks
    if grounding_required and not grounded_output:
        violations.append("execute_non_grounded_outputs_as_facts_when_grounding_required")
    else:
        satisfied_must_not.append("execute_non_grounded_outputs_as_facts_when_grounding_required")

    return L2HandoffValidationResult(
        valid=not violations,
        violations=tuple(violations),
        must_satisfied=tuple(satisfied_must),
        must_not_satisfied=tuple(satisfied_must_not),
    )


__all__ = [
    "L2HandoffValidationResult",
    "L2_MUST",
    "L2_MUST_NOT",
    "validate_l2_handoff",
]
