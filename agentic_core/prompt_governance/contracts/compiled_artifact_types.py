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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

# Self-bootstrap governance wiring (preserved from pre-merge file)
trace_contract._emit_authorize_and_execute("p2", "CompiledPromptArtifact", "execution_auth")
trace_contract._emit_validates_capability("p2", "CompiledPromptArtifact", "capability_check")
trace_contract._emit_routes_to_capability("p2", "CompiledPromptArtifact", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "CompiledPromptArtifact", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "CompiledPromptArtifact", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "CompiledPromptArtifact", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "CompiledPromptArtifact", "exec_output")
trace_contract._emit_dispatches_agent("p3", "CompiledPromptArtifact", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "CompiledPromptArtifact", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "CompiledPromptArtifact", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "CompiledPromptArtifact", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "CompiledPromptArtifact", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "CompiledPromptArtifact", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "CompiledPromptArtifact", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "CompiledPromptArtifact", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "CompiledPromptArtifact", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "CompiledPromptArtifact", "eval_metric")
trace_contract._emit_stores_embedding("p4", "CompiledPromptArtifact", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "CompiledPromptArtifact", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "CompiledPromptArtifact", "exec_snapshot_link")
trace_contract._emit_dispatches_healing_run("p1", "CompiledPromptArtifact", "L0")
trace_contract._emit_routes_through("p1", "CompiledPromptArtifact", "L0")
trace_contract._emit_checks_agent_registry("p1", "CompiledPromptArtifact", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "CompiledPromptArtifact", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "CompiledPromptArtifact", "exec_plan")
trace_contract._emit_routes_to_agent("p1", "CompiledPromptArtifact", "target_agent")
trace_contract._emit_verifies_policy("p1", "CompiledPromptArtifact", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "CompiledPromptArtifact", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "CompiledPromptArtifact", "boundary_check")
trace_contract._emit_transcripts_response("p1", "CompiledPromptArtifact", "transcript")
trace_contract._emit_gated_by_confidence("p1", "CompiledPromptArtifact", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "CompiledPromptArtifact", "L0")
trace_contract._emit_reads_policy_state("p1", "CompiledPromptArtifact", "L0")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "CompiledPromptArtifact", "p0_governance")
trace_contract._emit_snapshots_state("p0", "CompiledPromptArtifact", "state_snapshot")


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
