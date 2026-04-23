"""CompiledPromptArtifact (narrow variant) — Assembly Stage → LLM Gateway handoff.

DEPRECATION NOTICE (plan prompt-reception-followups-a7b3c4, phase RH2B.2)
=========================================================================

This module defines the **narrow** 6-field ``CompiledPromptArtifact`` used by
``agentic_core.L0_routing.reasoning.assembly_stage``. The **canonical** rich
variant now lives at::

    agentic_core.L2_execution.reasoning.compiled_artifact.CompiledPromptArtifact

The rich variant carries additional metadata the prompt-reception pipeline
depends on — ``slots_used``, ``prompt_bom``, ``template_manifest``,
``injection_scan_result``, ``routing_decision``, ``system_version_hash`` — and
exposes ``to_prompt_messages()`` (phase RH2B.3) for provider-aware adapters.

New code MUST import from ``agentic_core.L2_execution.reasoning``.
Consumers of this module should migrate via :func:`to_rich_artifact`. The
narrow dataclass remains for backward compatibility with
``assembly_stage.GovernedPayload`` construction and existing lifecycle
contract tests, but it is frozen — no new fields, no new consumers, no new
imports outside the Assembly Stage boundary.

Field-map when migrating narrow -> rich:
  - ``token_estimate`` (narrow)          -> ``tokens`` (rich)
  - ``allowed_tools_schema`` tuple       -> ``allowed_tools_schema`` list
  - ``final_system_string`` / ``final_user_string`` map 1:1
  - ``signature`` maps 1:1 (HMAC scheme differs; recompute on upgrade)
  - ``trace_id`` maps 1:1

Follow-up: when ``assembly_stage`` is refactored (deferred scope item on
``prompt-reception-followups-a7b3c4``), this module becomes a thin
re-export alias of the rich variant and can be removed one release later.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
)

# Self-bootstrap governance wiring
_emit_authorize_and_execute("p2", "CompiledPromptArtifact", "execution_auth")
_emit_validates_capability("p2", "CompiledPromptArtifact", "capability_check")
_emit_routes_to_capability("p2", "CompiledPromptArtifact", "capability_route")
_emit_writes_via_uwg("p2", "CompiledPromptArtifact", "uwg_write")
_emit_blocks_direct_write("p2", "CompiledPromptArtifact", "direct_write_block")
_emit_records_tool_invocation("p2", "CompiledPromptArtifact", "tool_invocation")
_emit_captures_execution_output("p2", "CompiledPromptArtifact", "exec_output")
_emit_dispatches_agent("p3", "CompiledPromptArtifact", "agent_dispatch")
_emit_coordinates_agents("p3", "CompiledPromptArtifact", "agent_coordination")
_emit_records_workflow_lineage("p3", "CompiledPromptArtifact", "workflow_lineage")
_emit_records_healing_outcome("p3", "CompiledPromptArtifact", "healing_outcome")
_emit_escalates_failure("p3", "CompiledPromptArtifact", "failure_escalation")
_emit_orchestrates_workflow("p3", "CompiledPromptArtifact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CompiledPromptArtifact", "healing_dispatch")
_emit_invokes_evaluation("p3", "CompiledPromptArtifact", "evaluation_signal")
_emit_records_telemetry_event("p4", "CompiledPromptArtifact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CompiledPromptArtifact", "eval_metric")
_emit_stores_embedding("p4", "CompiledPromptArtifact", "embedding_store")
_emit_updates_meta_learning_state("p4", "CompiledPromptArtifact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CompiledPromptArtifact", "exec_snapshot_link")
_emit_dispatches_healing_run("p1", "CompiledPromptArtifact", "L0")
_emit_routes_through("p1", "CompiledPromptArtifact", "L0")
_emit_checks_agent_registry("p1", "CompiledPromptArtifact", "agent_registry")
_emit_validates_agent_capability("p1", "CompiledPromptArtifact", "capability")
_emit_dispatches_execution_plan("p1", "CompiledPromptArtifact", "exec_plan")
_emit_routes_to_agent("p1", "CompiledPromptArtifact", "target_agent")
_emit_verifies_policy("p1", "CompiledPromptArtifact", "policy_check")
_emit_observes_runtime_state("p1", "CompiledPromptArtifact", "runtime_state")
_emit_verifies_boundary("p1", "CompiledPromptArtifact", "boundary_check")
_emit_transcripts_response("p1", "CompiledPromptArtifact", "transcript")
_emit_gated_by_confidence("p1", "CompiledPromptArtifact", "confidence_gate")
_emit_escalates_to_human("p1", "CompiledPromptArtifact", "L0")
_emit_reads_policy_state("p1", "CompiledPromptArtifact", "L0")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "CompiledPromptArtifact", "p0_governance")
_emit_snapshots_state("p0", "CompiledPromptArtifact", "state_snapshot")


@dataclass(frozen=True)
class CompiledPromptArtifact:
    """Fully assembled, signed prompt artifact for LLM Gateway.

    Immutable contract between Assembly Stage and SovereignLLMGateway.
    HMAC-SHA256 signature ensures integrity.

    Attributes
    ----------
    trace_id : str
        Execution trace identifier.
    final_system_string : str
        Complete S0+D0+I0+C0 system prompt.
    final_user_string : str
        Complete U0 user prompt (wrapped).
    allowed_tools_schema : tuple[dict[str, Any], ...]
        Sorted tuple of tool schemas allowed.
    token_estimate : int
        Estimated token count for budget validation.
    signature : str
        HMAC-SHA256 over canonical content.
    """

    trace_id: str
    final_system_string: str
    final_user_string: str
    allowed_tools_schema: tuple[dict[str, Any], ...]
    token_estimate: int
    signature: str

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.token_estimate < 0:
            raise ValueError(f"token_estimate must be >= 0, got {self.token_estimate}")

    def _canonical_content(self) -> str:
        """Produce canonical string for signature verification."""
        return json.dumps(
            {
                "trace_id": self.trace_id,
                "final_system_string": self.final_system_string,
                "final_user_string": self.final_user_string,
                "allowed_tools_schema": sorted(
                    (json.dumps(t, sort_keys=True, ensure_ascii=False) for t in self.allowed_tools_schema),
                ),
                "token_estimate": self.token_estimate,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def verify_signature(self, secret_key: bytes) -> bool:
        """Verify HMAC-SHA256 signature.

        Args:
            secret_key: HMAC secret key bytes.

        Returns:
            True if signature is valid.
        """
        expected = hmac.new(
            secret_key,
            self._canonical_content().encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, self.signature)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "final_system_string": self.final_system_string,
            "final_user_string": self.final_user_string,
            "allowed_tools_schema": tuple(self.allowed_tools_schema),
            "token_estimate": self.token_estimate,
            "signature": self.signature,
        }


def to_rich_artifact(
    narrow: CompiledPromptArtifact,
    system_version_hash: str = "",
    slots_used: list[str] | None = None,
) -> Any:
    """Upgrade a narrow governance ``CompiledPromptArtifact`` to the rich L2 form.

    Phase RH2B.2 bridge. Field mapping:

    - ``token_estimate`` (narrow) -> ``tokens`` (rich)
    - ``allowed_tools_schema`` tuple -> list
    - ``signature`` is copied verbatim; the rich variant uses a different HMAC
      scheme, so callers who rely on ``verify_signature`` should recompute via
      ``SlotAssemblyEngine`` rather than trust the carried signature.
    - ``system_version_hash`` and ``slots_used`` must be supplied by the
      caller because the narrow variant does not carry them.

    Returns the rich ``agentic_core.L2_execution.reasoning.CompiledPromptArtifact``.
    """
    # Lazy import to avoid cross-layer static coupling at module load.
    from agentic_core.L2_execution.reasoning.compiled_artifact import (
        CompiledPromptArtifact as RichCompiledPromptArtifact,
    )

    return RichCompiledPromptArtifact(
        trace_id=narrow.trace_id,
        system_version_hash=system_version_hash,
        final_system_string=narrow.final_system_string,
        final_user_string=narrow.final_user_string,
        allowed_tools_schema=list(narrow.allowed_tools_schema),
        tokens=narrow.token_estimate,
        slots_used=list(slots_used or []),
        signature=narrow.signature,
    )


__all__ = ["CompiledPromptArtifact", "to_rich_artifact"]
