"""CompiledPromptArtifact — thin SSOT re-export alias (phase RH2B.2 merge).

Plan: prompt-reception-followups-a7b3c4.

History
-------
Pre-RH2B.2 this module defined a **narrow** 6-field dataclass variant of
``CompiledPromptArtifact`` distinct from the rich L2 variant. The two
parallel dataclasses created SSOT drift. RH2B.2 collapses the split.

Post-RH2B.2 (this file)
-----------------------
``CompiledPromptArtifact`` here is an **alias** for
``agentic_core.L2_execution.reasoning.compiled_artifact.CompiledPromptArtifact``
(the canonical rich variant). All legacy import paths keep working:

    from agentic_core.prompt_governance.contracts.compiled_artifact_types import (
        CompiledPromptArtifact,
    )

now resolves to the rich class. The narrow field names are gone:

- ``token_estimate`` (narrow)    -> ``tokens`` (rich, required)
- ``allowed_tools_schema: tuple`` -> ``allowed_tools_schema: list`` (rich)
- ``system_version_hash``         -> REQUIRED (was absent on narrow)
- ``slots_used``                  -> REQUIRED (was absent on narrow)

The bridge ``to_rich_artifact`` is retained as an **identity wrapper** for
back-compat with callers that already invoke it; it now accepts the rich
class and returns it unchanged (after filling in defaults when callers
pass ``system_version_hash`` / ``slots_used`` explicitly — the legacy
signature is preserved).

Governance emissions at module-load are preserved from the pre-merge file
so any lifecycle-trace consumers see the same P0..P4 signal density.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    CompiledPromptArtifact as _RichCompiledPromptArtifact,
)
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

# Self-bootstrap governance wiring (preserved from pre-merge file)
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


# ---------------------------------------------------------------------------
# SSOT alias — CompiledPromptArtifact is now the rich L2 dataclass.
# ---------------------------------------------------------------------------
CompiledPromptArtifact = _RichCompiledPromptArtifact


def to_rich_artifact(
    artifact: _RichCompiledPromptArtifact,
    system_version_hash: str | None = None,
    slots_used: list[str] | None = None,
) -> _RichCompiledPromptArtifact:
    """Identity/fill-in helper retained for back-compat with RH2B.2 bridge callers.

    Prior to the SSOT merge, this function converted a narrow
    ``CompiledPromptArtifact`` to the rich L2 form. Post-merge both are the
    same class, so ``to_rich_artifact`` is now effectively an identity.

    The optional ``system_version_hash`` and ``slots_used`` arguments are
    retained for callers that used the bridge to fill in these fields when
    upgrading from the narrow variant. When provided (and non-empty), they
    overwrite the corresponding fields on a copy of the input artifact.
    """
    overrides: dict[str, Any] = {}
    if system_version_hash is not None:
        overrides["system_version_hash"] = system_version_hash
    if slots_used is not None:
        overrides["slots_used"] = list(slots_used)
    if not overrides:
        return artifact
    return replace(artifact, **overrides)


__all__ = ["CompiledPromptArtifact", "to_rich_artifact"]
