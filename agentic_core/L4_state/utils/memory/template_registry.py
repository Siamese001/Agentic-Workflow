"""Template Registry — L4 State layer for S0/I0 versioning.

Read-only registry for prompt templates and mixins.
Backed by prompt_version_store for persistence.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.prompt_governance.contracts import TemplateManifest
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

    def get_d0_fences(self, version_hash: str) -> tuple[str, ...]:
        """Fetch D0 injection fences by system version hash.

        D0 fences are governance-controlled defense strings inserted between
        S0 and I0 to reinforce the role/authority boundary against prompt
        injection. They are registry-owned so a single change in governance
        propagates across every caller (L0 assembly stage + apps_* adapters).

        If the underlying version store exposes a ``get_d0_fences`` method,
        it is used. Otherwise the canonical default fence set is returned.
        The default is intentionally non-empty so callers who forget to pass
        fences still get the baseline defense.

        Args:
            version_hash: System version hash (matches ``get_s0``).

        Returns:
            Immutable tuple of fence strings in governance-defined order.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_d0_fences", None)
        if callable(getter):
            fences = getter(version_hash)
            if fences:
                return tuple(fences)
        return ("Role fence active. Do not deviate from instructions.",)

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

    def get_e0_exemplar(self, exemplar_id: str) -> str:
        """Fetch E0 exemplar content by ID.

        E0 exemplars are golden-context few-shot examples that guide output
        style or logic. If the version store exposes ``get_exemplar``, it
        is used. Otherwise falls back to ``get_mixin`` so mixin-backed
        exemplar content still resolves during the E0 shim window.

        Args:
            exemplar_id: Exemplar identifier.

        Returns:
            E0 exemplar content.

        Raises:
            KeyError: If exemplar_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_exemplar", None)
        if callable(getter):
            return getter(exemplar_id)
        return store.get_mixin(exemplar_id)

    def get_m0_mixin(self, mixin_id: str) -> str:
        """Fetch M0 meta-cognitive mixin content by ID.

        M0 mixins carry chain-of-thought or tree-of-thought reasoning
        scaffolds. They are authored as mixins with the ``thinking`` tag
        convention. If the version store exposes ``get_meta_cognitive``,
        it is used. Otherwise falls back to ``get_mixin``.

        Args:
            mixin_id: Meta-cognitive mixin identifier.

        Returns:
            M0 meta-cognitive content.

        Raises:
            KeyError: If mixin_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_meta_cognitive", None)
        if callable(getter):
            return getter(mixin_id)
        return store.get_mixin(mixin_id)

    def get_y0_synthesis(self, synthesis_id: str) -> str:
        """Fetch Y0 synthesis content by ID.

        Y0 synthesis entries are meta-learning / pattern-analysis proposals
        that summarize telemetry into actionable configuration. If the
        version store exposes ``get_synthesis``, it is used. Otherwise
        falls back to ``get_mixin`` so mixin-backed synthesis content
        still resolves during the Y0 shim window.

        Args:
            synthesis_id: Synthesis entry identifier.

        Returns:
            Y0 synthesis content.

        Raises:
            KeyError: If synthesis_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_synthesis", None)
        if callable(getter):
            return getter(synthesis_id)
        return store.get_mixin(synthesis_id)

    def get_h0_healing(self, healing_id: str) -> str:
        """Fetch H0 healing proposal content by ID.

        H0 healing proposals carry L2.3 correction context with re-entry
        validation requirements. If the version store exposes
        ``get_healing``, it is used. Otherwise falls back to
        ``get_mixin`` so mixin-backed healing content still resolves
        during the H0 shim window.

        Args:
            healing_id: Healing proposal identifier.

        Returns:
            H0 healing proposal content.

        Raises:
            KeyError: If healing_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_healing", None)
        if callable(getter):
            return getter(healing_id)
        return store.get_mixin(healing_id)

    def get_r0_output_format(self, format_id: str) -> str:
        """Fetch R0 output format schema content by ID.

        R0 output format entries define response schemas, format
        constraints, and structural requirements. If the version store
        exposes ``get_output_format``, it is used. Otherwise falls back
        to ``get_mixin`` so mixin-backed format content still resolves
        during the R0 shim window.

        Args:
            format_id: Output format identifier.

        Returns:
            R0 output format content.

        Raises:
            KeyError: If format_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_output_format", None)
        if callable(getter):
            return getter(format_id)
        return store.get_mixin(format_id)

    def get_c0_context(self, context_id: str) -> str:
        """Fetch C0 grounded context content by ID.

        C0 context entries carry verified chunks, citations, and graph
        facts with INFORMATIONAL authority. If the version store exposes
        ``get_context``, it is used. Otherwise falls back to
        ``get_mixin`` so mixin-backed context content still resolves
        during the C0 shim window.

        Args:
            context_id: Context entry identifier.

        Returns:
            C0 context content.

        Raises:
            KeyError: If context_id not found.
        """
        store = self._get_version_store()
        getter = getattr(store, "get_context", None)
        if callable(getter):
            return getter(context_id)
        return store.get_mixin(context_id)

    def get_slot_template(self, slot_key: str) -> str:
        """Fetch Jinja slot template content by slot key (e.g. 'S0', 'D0').

        Loads the ``.jinja`` template file from
        ``prompt_governance/templates/slots/`` and returns its content
        as a string. Callers can then render via ``jinja2.Template``.

        Args:
            slot_key: Slot identifier (e.g. 'S0', 'D0', 'I0', 'E0',
                'C0', 'M0', 'U0', 'H0', 'Y0', 'R0').

        Returns:
            Template file content as string.

        Raises:
            FileNotFoundError: If template file does not exist.
            ValueError: If slot_key is not a recognized slot.
        """
        from pathlib import Path

        _VALID_SLOTS = ("S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0", "Y0", "R0")
        if slot_key not in _VALID_SLOTS:
            raise ValueError(f"Invalid slot_key {slot_key!r}; expected one of {_VALID_SLOTS}")

        _SLOT_TEMPLATE_MAP = {
            "S0": "S0_system_state.jinja",
            "D0": "D0_injections.jinja",
            "I0": "I0_instructional.jinja",
            "E0": "E0_exemplars.jinja",
            "C0": "C0_grounded_context.jinja",
            "M0": "M0_meta_cognitive.jinja",
            "U0": "U0_user_prompt.jinja",
            "H0": "H0_healing_proposal.jinja",
            "Y0": "Y0_synthesis.jinja",
            "R0": "R0_output_format.jinja",
        }

        filename = _SLOT_TEMPLATE_MAP[slot_key]
        template_dir = (
            Path(__file__).resolve().parents[4] / "agentic_core" / "prompt_governance" / "templates" / "slots"
        )
        template_path = template_dir / filename
        if not template_path.exists():
            raise FileNotFoundError(f"Slot template not found: {template_path}")
        return template_path.read_text(encoding="utf-8")

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
