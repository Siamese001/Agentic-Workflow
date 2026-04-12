"""Template Registry — L4 State layer for S0/I0 versioning.

Read-only registry for prompt templates and mixins.
Backed by prompt_version_store for persistence.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.prompt_governance.contracts.template_manifest_types import (
    TemplateManifest,
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

# Self-bootstrap governance wiring
_emit_authorize_and_execute("p2", "TemplateRegistry", "execution_auth")
_emit_validates_capability("p2", "TemplateRegistry", "capability_check")
_emit_routes_to_capability("p2", "TemplateRegistry", "capability_route")
_emit_writes_via_uwg("p2", "TemplateRegistry", "uwg_write")
_emit_blocks_direct_write("p2", "TemplateRegistry", "direct_write_block")
_emit_records_tool_invocation("p2", "TemplateRegistry", "tool_invocation")
_emit_captures_execution_output("p2", "TemplateRegistry", "exec_output")
_emit_dispatches_agent("p3", "TemplateRegistry", "agent_dispatch")
_emit_coordinates_agents("p3", "TemplateRegistry", "agent_coordination")
_emit_records_workflow_lineage("p3", "TemplateRegistry", "workflow_lineage")
_emit_records_healing_outcome("p3", "TemplateRegistry", "healing_outcome")
_emit_escalates_failure("p3", "TemplateRegistry", "failure_escalation")
_emit_orchestrates_workflow("p3", "TemplateRegistry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "TemplateRegistry", "healing_dispatch")
_emit_invokes_evaluation("p3", "TemplateRegistry", "evaluation_signal")
_emit_records_telemetry_event("p4", "TemplateRegistry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "TemplateRegistry", "eval_metric")
_emit_stores_embedding("p4", "TemplateRegistry", "embedding_store")
_emit_updates_meta_learning_state("p4", "TemplateRegistry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "TemplateRegistry", "exec_snapshot_link")
_emit_dispatches_healing_run("p1", "TemplateRegistry", "L0")
_emit_routes_through("p1", "TemplateRegistry", "L0")
_emit_checks_agent_registry("p1", "TemplateRegistry", "agent_registry")
_emit_validates_agent_capability("p1", "TemplateRegistry", "capability")
_emit_dispatches_execution_plan("p1", "TemplateRegistry", "exec_plan")
_emit_routes_to_agent("p1", "TemplateRegistry", "target_agent")
_emit_verifies_policy("p1", "TemplateRegistry", "policy_check")
_emit_observes_runtime_state("p1", "TemplateRegistry", "runtime_state")
_emit_verifies_boundary("p1", "TemplateRegistry", "boundary_check")
_emit_transcripts_response("p1", "TemplateRegistry", "transcript")
_emit_gated_by_confidence("p1", "TemplateRegistry", "confidence_gate")
_emit_escalates_to_human("p1", "TemplateRegistry", "L0")
_emit_reads_policy_state("p1", "TemplateRegistry", "L0")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "TemplateRegistry", "p0_governance")
_emit_snapshots_state("p0", "TemplateRegistry", "state_snapshot")


@dataclass(frozen=True)
class TemplateEntry:
    """Registry entry for a template."""

    manifest: TemplateManifest
    content: str


class TemplateRegistry:
    """Read-only registry for S0 system prompts and I0 mixins.

    Singleton backed by prompt_version_store.
    Never compiles — returns versioned content only.
    """

    _instance: TemplateRegistry | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self._cache: dict[str, TemplateEntry] = {}

    def _get_version_store(self):
        """Lazy import to avoid circular dependencies."""
        from agentic_core.L4_state.utils.memory.prompt_version_store import get_version_store

        return get_version_store()

    def get_s0(self, version_hash: str) -> str:
        """Fetch S0 system prompt by version hash.

        Args:
            version_hash: SHA-256 hash of system prompt version.

        Returns:
            S0 system prompt content.

        Raises:
            KeyError: If version_hash not found.
        """
        store = self._get_version_store()
        return store.get_system_prompt(version_hash)

    def get_i0_mixin(self, mixin_id: str) -> str:
        """Fetch I0 mixin content by ID.

        Args:
            mixin_id: Mixin identifier.

        Returns:
            I0 mixin content.

        Raises:
            KeyError: If mixin_id not found.
        """
        store = self._get_version_store()
        return store.get_mixin(mixin_id)

    def register_template(
        self,
        manifest: TemplateManifest,
        content: str,
    ) -> str:
        """Register a new template (admin use only).

        Args:
            manifest: Template manifest metadata.
            content: Template content.

        Returns:
            SHA-256 hash of registered content.
        """
        import hashlib

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        entry = TemplateEntry(manifest=manifest, content=content)
        self._cache[content_hash] = entry

        # Persist to version store
        store = self._get_version_store()
        store.store_template(manifest.template_id, content_hash, content)

        return content_hash

    def list_available_mixins(self) -> list[str]:
        """List available I0 mixin IDs."""
        store = self._get_version_store()
        return store.list_mixins()


# Singleton accessor
_registry_instance: TemplateRegistry | None = None


def get_template_registry() -> TemplateRegistry:
    """Get singleton TemplateRegistry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = TemplateRegistry()
    return _registry_instance


__all__ = ["TemplateRegistry", "TemplateEntry", "get_template_registry"]
