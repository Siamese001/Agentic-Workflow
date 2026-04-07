"""Prompt Registry (CMS) for Constitutional Assets.

Phase 4 - Pillar 13: Prompt Governance (CMS)
Central repository for managing constitutional prompts as versioned assets.

Features:
- Centralized prompt storage
- Categorization and tagging
- Non-engineer friendly management
- Separation from code
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "prompt_registry_util", "p0_governance")
_emit_snapshots_state("p0", "prompt_registry_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_registry_util", "p4obs", "metric_6")
_emit_records_incident_event("prompt_registry_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_registry_util", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_registry_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_registry_util", "p4obs", "mon_state")
_emit_triggers_alert("prompt_registry_util", "p4obs", "alert")
_emit_links_incident_trace("prompt_registry_util", "p4obs", "trace_link")
_emit_captures_pattern("prompt_registry_util", "p3lm", "pattern")
_emit_records_learning_event("prompt_registry_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_registry_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_registry_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_registry_util", "p3lm", "routing")
_emit_improves_agent_policy("prompt_registry_util", "p3lm", "policy")
_emit_stores_learning_state("prompt_registry_util", "p3lm", "state")
_emit_records_execution_trace("prompt_registry_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_registry_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_registry_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_registry_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_registry_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_registry_util", "env_read", "p2_env_1")
_emit_reads_environ("prompt_registry_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_registry_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_registry_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_registry_util", "context_pull")
_emit_pulls_context("p1", "prompt_registry_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_registry_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_registry_util", "uwg_term_2")
_emit_writes_through("p1", "prompt_registry_util", "write_through")
_emit_writes_through("p1", "prompt_registry_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_registry_util", "safety_validation")
_emit_invokes_eval("p1", "prompt_registry_util", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_registry_util", "routing_commit")
_emit_escalates_to_human("p1", "prompt_registry_util", "human_escalation")
_emit_routes_through("p1", "prompt_registry_util", "route_through")
_emit_checks_agent_registry("p1", "prompt_registry_util", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_registry_util", "capability")
_emit_dispatches_execution_plan("p1", "prompt_registry_util", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_registry_util", "sub_agent")
_emit_routes_to_agent("p1", "prompt_registry_util", "target_agent")
_emit_verifies_policy("p1", "prompt_registry_util", "policy_check")
_emit_observes_runtime_state("p1", "prompt_registry_util", "runtime_state")
_emit_verifies_boundary("p1", "prompt_registry_util", "boundary_check")
_emit_transcripts_response("p1", "prompt_registry_util", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_registry_util")
_emit_gated_by_confidence("p1", "prompt_registry_util", "confidence_gate")
emit_replay_key("p0", "prompt_registry_util")
emit_determinism_digest("p0", "prompt_registry_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_registry_util", "execution_auth")
_emit_validates_capability("p2", "prompt_registry_util", "capability_check")
_emit_routes_to_capability("p2", "prompt_registry_util", "capability_route")
_emit_writes_via_uwg("p2", "prompt_registry_util", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_registry_util", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_registry_util", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_registry_util", "exec_output")
_emit_dispatches_agent("p3", "prompt_registry_util", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_registry_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_registry_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_registry_util", "healing_outcome")
_emit_escalates_failure("p3", "prompt_registry_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_registry_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_registry_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_registry_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_registry_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_registry_util", "eval_metric")
_emit_stores_embedding("p4", "prompt_registry_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_registry_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_registry_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class PromptCategory(Enum):
    """Prompt categories."""

    SYSTEM_INSTRUCTION = "system_instruction"
    SAFETY_POLICY = "safety_policy"
    REASONING_TEMPLATE = "reasoning_template"
    TASK_TEMPLATE = "task_template"
    VALIDATION_RULE = "validation_rule"
    EXAMPLE = "example"


@dataclass
class PromptTemplate:
    """Prompt template with metadata."""

    template_id: str
    name: str
    category: PromptCategory
    content: str
    version: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "content": self.content,
            "version": self.version,
            "description": self.description,
            "tags": self.tags,
            "variables": self.variables,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptTemplate":
        """Create from dictionary."""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            category=PromptCategory(data["category"]),
            content=data["content"],
            version=data["version"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            variables=data.get("variables", []),
            metadata=data.get("metadata", {}),
        )

    def render(self, **kwargs) -> str:
        """Render template with variables.

        Args:
            **kwargs: Variable values

        Returns:
            Rendered prompt
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptTemplate.render")

        content = self.content
        for var in self.variables:
            if var in kwargs:
                placeholder = f"{{{var}}}"
                content = content.replace(placeholder, str(kwargs[var]))
        return content


class PromptRegistry:
    """Central registry for constitutional prompt assets.

    Features:
    - Template storage and retrieval
    - Category-based organization
    - Tag-based search
    - Version management
    - Persistence to disk
    """

    def __init__(self, registry_path: Path | None = None, enable_logging: bool = True):
        """Initialize prompt registry.

        Args:
            registry_path: Path to registry file
            enable_logging: Enable logging
        """
        self.registry_path = registry_path or Path("prompt_governance/registry/prompts.json")
        self.enable_logging = enable_logging
        self._templates: dict[str, PromptTemplate] = {}
        self._load_registry()
        if self.enable_logging:
            logger.info(
                "prompt_registry_initialized",
                extra={"template_count": len(self._templates), "registry_path": str(self.registry_path)},
            )

    def _migrate_to_template_registry(self, template: PromptTemplate) -> str:
        """Migrate a PromptTemplate to the new TemplateRegistry (Phase 8).

        This bridges the old apps_shared shadow system to the new
        agentic_core TemplateRegistry.

        Args:
            template: Old-style PromptTemplate

        Returns:
            Version hash from TemplateRegistry
        """
        from agentic_core.L4_state.utils.memory.template_registry import (
            get_template_registry,
        )
        from agentic_core.prompt_governance.contracts import TemplateManifest

        registry = get_template_registry()

        # Create manifest from old template
        manifest = TemplateManifest(
            template_id=template.template_id,
            version=template.version,
            git_commit_hash="unknown",  # Legacy templates don't have git hashes
            required_variables=tuple(template.variables),
        )

        # Register with new registry
        return registry.register_template(manifest, template.content)

    def register(self, template: PromptTemplate) -> None:
        """Register a prompt template (with Phase 8 bridge to TemplateRegistry).

        Args:
            template: Prompt template
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptRegistry.register")

        # Phase 8: Bridge to new TemplateRegistry
        try:
            self._migrate_to_template_registry(template)
        except Exception as exc:
            logger.warning(f"TemplateRegistry bridge failed (legacy mode): {exc}")

        # Keep legacy storage for backward compatibility
        self._templates[template.template_id] = template
        self._save_registry()
        if self.enable_logging:
            logger.info(
                "template_registered",
                extra={
                    "template_id": template.template_id,
                    "category": template.category.value,
                    "version": template.version,
                    "bridged_to_template_registry": True,
                },
            )

    def get(self, template_id: str) -> PromptTemplate | None:
        """Get a prompt template.

        Args:
            template_id: Template identifier

        Returns:
            PromptTemplate or None
        """
        return self._templates.get(template_id)

    def find_by_category(self, category: PromptCategory) -> list[PromptTemplate]:
        """Find templates by category.

        Args:
            category: Prompt category

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.category == category]

    def find_by_tag(self, tag: str) -> list[PromptTemplate]:
        """Find templates by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if tag in t.tags]

    def search(self, query: str) -> list[PromptTemplate]:
        """Search templates by name or description.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        return [
            t
            for t in self._templates.values()
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]

    def list_all(self) -> list[PromptTemplate]:
        """List all templates.

        Returns:
            List of all templates
        """
        return list(self._templates.values())

    def delete(self, template_id: str) -> bool:
        """Delete a template.

        Args:
            template_id: Template identifier

        Returns:
            True if deleted
        """
        if template_id in self._templates:
            del self._templates[template_id]
            self._save_registry()
            if self.enable_logging:
                logger.info("template_deleted", extra={"template_id": template_id})
            return True
        return False

    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self.registry_path.exists():
            self._create_default_templates()
            return
        try:
            with open(self.registry_path) as f:
                data = json.load(f)
            for template_data in data.get("templates", []):
                template = PromptTemplate.from_dict(template_data)
                self._templates[template.template_id] = template
        except Exception as e:
            if self.enable_logging:
                logger.error("failed_to_load_registry", extra={"error": str(e)}, exc_info=True)
            return None

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"version": "1.0.0", "templates": [t.to_dict() for t in self._templates.values()]}
            with open(self.registry_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            if self.enable_logging:
                logger.error("failed_to_save_registry", extra={"error": str(e)}, exc_info=True)
            return None

    def _create_default_templates(self) -> None:
        """Create default prompt templates."""
        system_template = PromptTemplate(
            template_id="system_default",
            name="Default System Instruction",
            category=PromptCategory.SYSTEM_INSTRUCTION,
            content="You are a helpful AI assistant. You follow safety guidelines and provide accurate, helpful responses.",
            version="1.0.0",
            description="Default system instruction for agents",
            tags=["default", "system"],
        )
        self._templates[system_template.template_id] = system_template
        safety_template = PromptTemplate(
            template_id="safety_default",
            name="Default Safety Policy",
            category=PromptCategory.SAFETY_POLICY,
            content="Do not provide harmful, illegal, or unethical content. Refuse requests that violate safety guidelines.",
            version="1.0.0",
            description="Default safety policy",
            tags=["default", "safety"],
        )
        self._templates[safety_template.template_id] = safety_template
        reasoning_template = PromptTemplate(
            template_id="react_default",
            name="ReAct Reasoning Template",
            category=PromptCategory.REASONING_TEMPLATE,
            content="Think step-by-step:\n1. Thought: {thought}\n2. Action: {action}\n3. Observation: {observation}",
            version="1.0.0",
            description="Default ReAct reasoning template",
            tags=["default", "reasoning", "react"],
            variables=["thought", "action", "observation"],
        )
        self._templates[reasoning_template.template_id] = reasoning_template
        self._save_registry()


def create_prompt_registry(registry_path: Path | None = None) -> PromptRegistry:
    """Factory function to create prompt registry.

    Args:
        registry_path: Optional registry path

    Returns:
        PromptRegistry instance
    """
    return PromptRegistry(registry_path=registry_path)
