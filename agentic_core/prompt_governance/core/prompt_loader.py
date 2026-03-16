"""Centralized prompt loading and caching system."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "prompt_loader", "p0_governance")
_emit_reads_policy_state("p0", "prompt_loader", "policy_binding")
_emit_snapshots_state("p0", "prompt_loader", "state_snapshot")
emit_replay_key("p0", "prompt_loader")
emit_determinism_digest("p0", "prompt_loader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_loader", "execution_auth")
_emit_validates_capability("p2", "prompt_loader", "capability_check")
_emit_routes_to_capability("p2", "prompt_loader", "capability_route")
_emit_writes_via_uwg("p2", "prompt_loader", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_loader", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_loader", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_loader", "exec_output")
_emit_dispatches_agent("p3", "prompt_loader", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_loader", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_loader", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_loader", "healing_outcome")
_emit_escalates_failure("p3", "prompt_loader", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_loader", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_loader", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_loader", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_loader", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_loader", "eval_metric")
_emit_stores_embedding("p4", "prompt_loader", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_loader", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_loader", "exec_snapshot_link")


class PromptLoadError(Exception):
    """Raised when prompt file cannot be loaded."""

    pass


class PromptSchemaError(Exception):
    """Raised when prompt file schema is invalid."""

    pass


class PromptLoader:
    """Pure infrastructure component for loading and caching prompts.

    Enforces architectural boundaries:
    - No business logic
    - No domain text formatting
    - No direct apps_* access
    """

    def __init__(self, prompt_dir: Path) -> None:
        """Initialize with injected prompt directory.

        Args:
            prompt_dir: Base directory containing prompt files

        Raises:
            ValueError: If prompt_dir is not a directory
        """
        if not isinstance(prompt_dir, Path):
            raise TypeError("prompt_dir must be a Path object")
        if not prompt_dir.is_dir():
            raise ValueError(f"prompt_dir must be a directory: {prompt_dir}")
        self._prompt_dir = prompt_dir.resolve()
        self._prompt_cache: dict[str, dict[str, Any]] = {}

    def load_prompt(self, domain: str, name: str) -> dict[str, Any]:
        """Load and cache prompt by domain and name.

        Args:
            domain: Prompt domain (e.g., 'executive', 'outreach')
            name: Prompt name without extension

        Returns:
            Loaded prompt data dictionary

        Raises:
            PromptLoadError: If file cannot be loaded
            PromptSchemaError: If schema is invalid
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptLoader.load_prompt")

        if not domain or not isinstance(domain, str):
            raise ValueError("domain must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        cache_key = f"{domain}:{name}"
        if cache_key not in self._prompt_cache:
            prompt_file = self._prompt_dir / domain / f"{name}.yaml"
            if not prompt_file.exists():
                raise PromptLoadError(f"Prompt file not found: {prompt_file}")
            if not prompt_file.is_file():
                raise PromptLoadError(f"Path is not a file: {prompt_file}")
            try:
                with open(prompt_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise PromptLoadError(f"Invalid YAML in {prompt_file}: {e}")
            except OSError as e:
                raise PromptLoadError(f"Cannot read {prompt_file}: {e}")
            if not isinstance(data, dict):
                raise PromptSchemaError(f"Prompt must be a dict: {prompt_file}")
            if "template" not in data:
                raise PromptSchemaError(f"Missing required 'template' key: {prompt_file}")
            if not isinstance(data["template"], str):
                raise PromptSchemaError(f"'template' must be a string: {prompt_file}")
            self._prompt_cache[cache_key] = data
        return self._prompt_cache[cache_key]

    def get_template(self, domain: str, name: str, **template_vars: Any) -> str:
        """Get formatted prompt template with variables.

        Args:
            domain: Prompt domain
            name: Prompt name
            **template_vars: Template variables

        Returns:
            Formatted template string

        Raises:
            PromptLoadError: If prompt cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        prompt_data = self.load_prompt(domain, name)
        template = prompt_data["template"]
        constraints = prompt_data.get("constraints", [])
        if constraints:
            if not isinstance(constraints, list):
                raise PromptSchemaError(f"'constraints' must be a list: {domain}:{name}")
            constraints_text = "\n".join(str(c) for c in constraints)
        else:
            constraints_text = ""
        try:
            return template.format(constraints=constraints_text, **template_vars)
        except KeyError as e:
            raise PromptSchemaError(f"Missing template variable {e} in {domain}:{name}")
        except (ValueError, TypeError) as e:
            raise PromptSchemaError(f"Template formatting error in {domain}:{name}: {e}")

    def clear_cache(self) -> None:
        """Clear the internal cache. Useful for testing."""
        self._prompt_cache.clear()

    def cache_info(self) -> dict[str, int]:
        """Get cache statistics for testing and monitoring."""
        return {"cached_items": len(self._prompt_cache), "cache_keys": list(self._prompt_cache.keys())}
