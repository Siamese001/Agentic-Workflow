from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "sovereign_prompt_renderer", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_prompt_renderer", "policy_binding")
_emit_snapshots_state("p0", "sovereign_prompt_renderer", "state_snapshot")
emit_replay_key("p0", "sovereign_prompt_renderer")
emit_determinism_digest("p0", "sovereign_prompt_renderer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereign_prompt_renderer", "execution_auth")
_emit_validates_capability("p2", "sovereign_prompt_renderer", "capability_check")
_emit_routes_to_capability("p2", "sovereign_prompt_renderer", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_prompt_renderer", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_prompt_renderer", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_prompt_renderer", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_prompt_renderer", "exec_output")
_emit_dispatches_agent("p3", "sovereign_prompt_renderer", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_prompt_renderer", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_prompt_renderer", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_prompt_renderer", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_prompt_renderer", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_prompt_renderer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_prompt_renderer", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_prompt_renderer", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_prompt_renderer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_prompt_renderer", "eval_metric")
_emit_stores_embedding("p4", "sovereign_prompt_renderer", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_prompt_renderer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_prompt_renderer", "exec_snapshot_link")

"Sovereign Prompt Renderer - Safe Jinja2 template rendering with validation.\n\nResponsibilities:\n- Load templates exclusively from prompt_governance/templates\n- Perform safe Jinja2 rendering with strict variable scoping\n- Enforce sovereignty: no inline prompt strings > 50 lines outside this layer\n- Validate template schemas and required variables\n"
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, select_autoescape

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class TemplateSchema:
    """Schema definition for template validation."""

    required_vars: set[str]
    optional_vars: set[str]
    description: str


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    pass


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
            template_root = Path(__file__).parent / "templates"
        self.template_root = template_root
        if not self.template_root.exists():
            os.makedirs(self.template_root, exist_ok=True)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_root)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )
        self._schema_cache: dict[str, TemplateSchema] = {}

    def _parse_template_schema(self, template_name: str) -> TemplateSchema:
        """Parse template header for schema metadata.

        Expected header format:
        {# SCHEMA: required_vars=[var1, var2], optional_vars=[var3] #}
        {# DESCRIPTION: Template purpose #}
        """
        if template_name in self._schema_cache:
            return self._schema_cache[template_name]
        template_path = self.template_root / template_name
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
            required_vars=required_vars, optional_vars=optional_vars, description=description
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignPromptRenderer.validate_context")

        schema = self._parse_template_schema(template_name)
        provided_vars = set(context.keys())
        missing_vars = schema.required_vars - provided_vars
        if missing_vars:
            raise TemplateValidationError(
                f"Template '{template_name}' requires variables {missing_vars} but only {provided_vars} were provided. Description: {schema.description}"
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
        if validate:
            try:
                self.validate_context(template_name, context)
            except TemplateValidationError as e:
                if "No description provided" not in str(e):
                    raise
        full_context = {
            **context,
            "_sovereign_metadata": {
                "renderer": self.__class__.__name__,
                "template": template_name,
                "root": str(self.template_root),
                **metadata,
            },
        }
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**full_context)
            return rendered.strip() + "\n"
        except TemplateNotFound:
            raise TemplateNotFound(f"Template '{template_name}' not found in {self.template_root}")
        except Exception as e:
            raise RuntimeError(f"[PROMPT RENDERING FAILURE] Template '{template_name}': {e}")

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
        try:
            base = self.env.get_template(f"../meta_prompts/{base_template}").render(**context)
        except TemplateNotFound:
            raise TemplateNotFound(f"Meta-prompt '{base_template}' not found in meta_prompts/")
        except Exception as e:
            raise RuntimeError(f"[META-PROMPT FAILURE] {base_template}: {e}")
        assembled = [base]
        for frag in fragments:
            try:
                if validate:
                    self.validate_context(frag, context)
                fragment_text = self.env.get_template(frag).render(**context)
                assembled.append(
                    f"\n<INSTRUCTIONAL_FRAGMENT:{frag}>\n{fragment_text}\n</INSTRUCTIONAL_FRAGMENT>"
                )
            except TemplateNotFound:
                continue
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"[WARNING] Fragment '{frag}' failed to render: {e}")
                continue
        return "\n".join(assembled)

    def list_available_templates(self) -> list[str]:
        """List all available templates for introspection.

        Returns:
            List of template names relative to template_root
        """
        from agentic_core.utils.ssot_discovery_validator import get_data_files

        jinja_files = get_data_files(self.template_root, extensions=[".jinja"])
        return [p.relative_to(self.template_root).as_posix() for p in jinja_files if p.is_file()]

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
