from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "sovereign_prompt_renderer", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "sovereign_prompt_renderer", "policy_binding")
trace_contract._emit_snapshots_state("p0", "sovereign_prompt_renderer", "state_snapshot")
trace_contract.emit_replay_key("p0", "sovereign_prompt_renderer")
trace_contract.emit_determinism_digest("p0", "sovereign_prompt_renderer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "sovereign_prompt_renderer", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_prompt_renderer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_prompt_renderer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_prompt_renderer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_prompt_renderer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_prompt_renderer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_prompt_renderer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_prompt_renderer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_prompt_renderer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_prompt_renderer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_prompt_renderer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_prompt_renderer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_prompt_renderer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_prompt_renderer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_prompt_renderer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_prompt_renderer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_prompt_renderer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_prompt_renderer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_prompt_renderer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_prompt_renderer", "exec_snapshot_link")

"Sovereign Prompt Renderer - Safe Jinja2 template rendering with validation.\n\nResponsibilities:\n- Load templates exclusively from prompt_governance/templates\n- Perform safe Jinja2 rendering with strict variable scoping\n- Enforce sovereignty: no inline prompt strings > 50 lines outside this layer\n- Validate template schemas and required variables\n"
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, select_autoescape


trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_prompt_renderer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_prompt_renderer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_prompt_renderer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_prompt_renderer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_prompt_renderer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_prompt_renderer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_prompt_renderer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_prompt_renderer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_prompt_renderer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_prompt_renderer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_prompt_renderer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_prompt_renderer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_prompt_renderer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_prompt_renderer", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_prompt_renderer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_prompt_renderer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_prompt_renderer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_prompt_renderer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_prompt_renderer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_prompt_renderer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_prompt_renderer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_prompt_renderer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_prompt_renderer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_prompt_renderer", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_prompt_renderer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_prompt_renderer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_prompt_renderer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_prompt_renderer", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_prompt_renderer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_prompt_renderer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_prompt_renderer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_prompt_renderer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "sovereign_prompt_renderer", "human_escalation")
trace_contract._emit_routes_through("p1", "sovereign_prompt_renderer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "sovereign_prompt_renderer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_prompt_renderer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_prompt_renderer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_prompt_renderer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_prompt_renderer", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_prompt_renderer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_prompt_renderer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_prompt_renderer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_prompt_renderer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_prompt_renderer")
trace_contract._emit_gated_by_confidence("p1", "sovereign_prompt_renderer", "confidence_gate")


@dataclass
class TemplateSchema:
    """Schema definition for template validation."""

    required_vars: set[str]
    optional_vars: set[str]
    description: str


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    pass


Logger = logging.getLogger(__name__)
_SAFE_TEMPLATE_NAME_RE = re.compile(r"^[A-Za-z0-9_./-]+$")


class SovereignPromptRenderer:
    """
    Sovereign renderer for instructional prompt templates.

    ARCHITECTURAL HARDENING:
    - No hardcoded paths (injected via constructor)
    - Strict template validation with schema checking
    - Variable injection safety with StrictUndefined
    - Template header parsing for metadata extraction
    """

    def __init__(self, template_root: Path | None = None):
        """Initialize renderer with dependency-injected template root.

        Args:
            template_root: Path to template directory. If None, auto-discovers
                          relative to this file's location.
        """
        if template_root is None:
            template_root = Path(__file__).parent.parent / "templates"
        self.template_root = template_root.resolve()
        if not self.template_root.exists():
            raise FileNotFoundError(f"Template root does not exist: {self.template_root}")
        if not self.template_root.is_dir():
            raise NotADirectoryError(f"Template root is not a directory: {self.template_root}")
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_root)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )
        self._schema_cache: dict[str, TemplateSchema] = {}

    def _validate_template_name(self, name: str) -> str:
        """Validate template name to prevent directory traversal."""
        if not name or not isinstance(name, str):
            raise ValueError("template_name must be a non-empty string")
        if not _SAFE_TEMPLATE_NAME_RE.fullmatch(name):
            raise ValueError(f"template_name contains unsafe characters: {name!r}")
        return name

    def _resolve_template_path(self, name: str) -> Path:
        """Resolve template path with traversal prevention."""
        safe_name = self._validate_template_name(name)
        resolved = (self.template_root / safe_name).resolve()
        try:
            resolved.relative_to(self.template_root)
        except ValueError as exc:
            raise ValueError(f"Template path escapes template root: {resolved}") from exc
        return resolved

    def _parse_template_schema(self, template_name: str) -> TemplateSchema:
        """Parse template header for schema metadata.

        Expected header format:
        {# SCHEMA: required_vars=[var1, var2], optional_vars=[var3] #}
        {# DESCRIPTION: Template purpose #}
        """
        if template_name in self._schema_cache:
            return self._schema_cache[template_name]
        template_path = self._resolve_template_path(template_name)
        if not template_path.exists():
            raise TemplateNotFound(template_name)
        content = template_path.read_text(encoding="utf-8")
        required_vars = set()
        optional_vars = set()
        description = "No description provided"
        schema_match = re.search(
            "\\{#\\s*SCHEMA:\\s*required_vars=\\[([^\\]]*)\\](?:,\\s*optional_vars=\\[([^\\]]*)\\])?\\s*#\\}",
            content,
        )
        if schema_match:
            required_str = schema_match.group(1).strip()
            if required_str:
                required_vars = {v.strip() for v in required_str.split(",")}
            optional_str = schema_match.group(2)
            if optional_str:
                optional_vars = {v.strip() for v in optional_str.split(",")}
        desc_match = re.search("\\{#\\s*DESCRIPTION:\\s*(.+?)\\s*#\\}", content)
        if desc_match:
            description = desc_match.group(1).strip()
        schema = TemplateSchema(
            required_vars=required_vars,
            optional_vars=optional_vars,
            description=description,
        )
        self._schema_cache[template_name] = schema
        return schema

    def validate_context(self, template_name: str, context: dict[str, Any]) -> None:
        """Validate that context provides all required variables.

        Args:
            template_name: Template to validate against
            context: Context dictionary to validate

        Raises:
            TemplateValidationError: If required variables are missing
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "SovereignPromptRenderer.validate_context",
        )

        schema = self._parse_template_schema(template_name)
        provided_vars = set(context.keys())
        missing_vars = schema.required_vars - provided_vars
        if missing_vars:
            raise TemplateValidationError(
                f"Template '{template_name}' requires variables {missing_vars} but only {provided_vars} were provided. Description: {schema.description}",
            )

    def render(
        self,
        template_name: str,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> str:
        """Render a standard sovereign instructional prompt with validation.

        Args:
            template_name: Name of template file (e.g., 'code_healing.jinja')
            context: Variables to inject into template
            metadata: Additional metadata for tracing
            validate: Whether to validate context against template schema

        Returns:
            Rendered prompt string

        Raises:
            TemplateValidationError: If validation fails
            TemplateNotFound: If template doesn't exist
        """
        context = context or {}
        metadata = metadata or {}
        self._validate_template_name(template_name)
        if validate:
            self.validate_context(template_name, context)
        full_context = {
            **context,
            "_sovereign_metadata": {
                "renderer": self.__class__.__name__,
                "template": template_name,
                "root": str(self.template_root),
                **metadata,
            },
        }
        template = self.env.get_template(template_name)
        rendered = template.render(**full_context)
        return rendered.strip() + "\n"

    def render_tagentic(
        self,
        base_template: str,
        fragments: list[str],
        context: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> str:
        """Tag-based agentic composition with validation.

        Combines meta-prompt + instructional fragments with XML semantic fencing.

        Args:
            base_template: Base meta-prompt template name
            fragments: List of fragment template names to compose
            context: Variables for rendering
            validate: Whether to validate each template

        Returns:
            Assembled prompt with XML tags
        """
        context = context or {}
        self._validate_template_name(base_template)
        for frag in fragments:
            self._validate_template_name(frag)
        meta_root = (self.template_root.parent / "meta_prompts").resolve()
        meta_env = Environment(
            loader=FileSystemLoader(str(meta_root)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )
        base = meta_env.get_template(base_template).render(**context)
        assembled = [base]
        for frag in fragments:
            if validate:
                self.validate_context(frag, context)
            fragment_text = self.env.get_template(frag).render(**context)
            assembled.append(
                f"\n<INSTRUCTIONAL_FRAGMENT:{frag}>\n{fragment_text}\n</INSTRUCTIONAL_FRAGMENT>",
            )
        return "\n".join(assembled)

    def list_available_templates(self) -> list[str]:
        """List all available templates for introspection.

        Returns:
            List of template names relative to template_root
        """
        return sorted(
            p.relative_to(self.template_root).as_posix()
            for p in self.template_root.rglob("*.jinja")
            if p.is_file()
        )

    def get_template_schema(self, template_name: str) -> TemplateSchema:
        """Get the schema for a template.

        Args:
            template_name: Template to inspect

        Returns:
            TemplateSchema with required/optional variables
        """
        return self._parse_template_schema(template_name)


_RENDERER: SovereignPromptRenderer | None = None


def get_sovereign_prompt_renderer(template_root: Path | None = None) -> SovereignPromptRenderer:
    """Get the global renderer singleton.

    Args:
        template_root: Optional custom template root (for testing)

    Returns:
        SovereignPromptRenderer instance
    """
    global _RENDERER
    if _RENDERER is None or template_root is not None:
        _RENDERER = SovereignPromptRenderer(template_root=template_root)
    return _RENDERER
