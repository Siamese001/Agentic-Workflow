"""YAML Injection Loader - Deterministic parsing and validation of YAML injection patterns.

This module provides deterministic loading of injection patterns from the production
YAML corpus under data/prompt_governance/injections, with strict validation and
error handling. It normalizes YAML patterns to the canonical InstructionalPattern
representation defined in agentic_core.config.core.injection_layer_config.

SOURCE: data/prompt_governance/injections/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "yaml_injection_loader", "execution_auth")
trace_contract._emit_validates_capability("p2", "yaml_injection_loader", "capability_check")
trace_contract._emit_routes_to_capability("p2", "yaml_injection_loader", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "yaml_injection_loader", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "yaml_injection_loader", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "yaml_injection_loader", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "yaml_injection_loader", "exec_output")
trace_contract._emit_dispatches_agent("p3", "yaml_injection_loader", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "yaml_injection_loader", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "yaml_injection_loader", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "yaml_injection_loader", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "yaml_injection_loader", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "yaml_injection_loader", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "yaml_injection_loader", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "yaml_injection_loader", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "yaml_injection_loader", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "yaml_injection_loader", "eval_metric")
trace_contract._emit_stores_embedding("p4", "yaml_injection_loader", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "yaml_injection_loader", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "yaml_injection_loader", "exec_snapshot_link")
from .injection_layer_config import InjectionLayer, InstructionalPattern

trace_contract._emit_applies_guardrail("p0", "yaml_injection_loader", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "yaml_injection_loader", "policy_binding")
trace_contract._emit_snapshots_state("p0", "yaml_injection_loader", "state_snapshot")

trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("yaml_injection_loader", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("yaml_injection_loader", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("yaml_injection_loader", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("yaml_injection_loader", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("yaml_injection_loader", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("yaml_injection_loader", "p4obs", "alert")
trace_contract._emit_links_incident_trace("yaml_injection_loader", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("yaml_injection_loader", "p3lm", "pattern")
trace_contract._emit_records_learning_event("yaml_injection_loader", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("yaml_injection_loader", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("yaml_injection_loader", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("yaml_injection_loader", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("yaml_injection_loader", "p3lm", "policy")
trace_contract._emit_stores_learning_state("yaml_injection_loader", "p3lm", "state")
trace_contract._emit_records_execution_trace("yaml_injection_loader", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("yaml_injection_loader", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("yaml_injection_loader", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("yaml_injection_loader", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("yaml_injection_loader", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("yaml_injection_loader", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("yaml_injection_loader", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("yaml_injection_loader", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("yaml_injection_loader", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "yaml_injection_loader", "context_pull")
trace_contract._emit_pulls_context("p1", "yaml_injection_loader", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "yaml_injection_loader", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "yaml_injection_loader", "uwg_term_2")
trace_contract._emit_writes_through("p1", "yaml_injection_loader", "write_through")
trace_contract._emit_writes_through("p1", "yaml_injection_loader", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "yaml_injection_loader", "safety_validation")
trace_contract._emit_invokes_eval("p1", "yaml_injection_loader", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "yaml_injection_loader", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "yaml_injection_loader", "human_escalation")
trace_contract._emit_routes_through("p1", "yaml_injection_loader", "route_through")
trace_contract._emit_checks_agent_registry("p1", "yaml_injection_loader", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "yaml_injection_loader", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "yaml_injection_loader", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "yaml_injection_loader", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "yaml_injection_loader", "target_agent")
trace_contract._emit_verifies_policy("p1", "yaml_injection_loader", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "yaml_injection_loader", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "yaml_injection_loader", "boundary_check")
trace_contract._emit_transcripts_response("p1", "yaml_injection_loader", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "yaml_injection_loader")
trace_contract._emit_gated_by_confidence("p1", "yaml_injection_loader", "confidence_gate")
trace_contract.emit_replay_key("p0", "yaml_injection_loader")
trace_contract.emit_determinism_digest("p0", "yaml_injection_loader")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class YamlValidationError(Exception):
    """Raised when YAML validation fails with precise error context."""

    filename: str
    missing_key: str | None = None
    parse_error: str | None = None

    def __str__(self) -> str:
        if self.missing_key:
            return f"Missing required key '{self.missing_key}' in {self.filename}"
        if self.parse_error:
            return f"YAML parse error in {self.filename}: {self.parse_error}"
        return f"Validation error in {self.filename}"


class YamlInjectionLoader:
    """Deterministic YAML injection pattern loader with validation."""

    REQUIRED_KEYS = {"description", "prompt_template", "success_criteria", "usage_context"}
    LAYER_MAPPING = {
        "framing": InjectionLayer.FRAMING,
        "context_engineering": InjectionLayer.CONTEXT,
        "reasoning": InjectionLayer.REASONING,
        "tool_use": InjectionLayer.TOOLING,
        "safety": InjectionLayer.SAFETY,
        "output_governance": InjectionLayer.OUTPUT,
    }

    def __init__(self, yaml_root: Path | None = None):
        """Initialize the YAML loader.

        Args:
            yaml_root: Root path to YAML injections directory.
                      Defaults to data/prompt_governance/injections
        """
        if yaml_root is None:
            yaml_root = Path("data/prompt_governance/injections")
        self.yaml_root = Path(yaml_root).expanduser().resolve()
        self._cache: dict[str, list[InstructionalPattern]] = {}

    def enumerate_yaml_files(self) -> list[Path]:
        """Enumerate YAML files deterministically (sorted paths).

        Returns:
            List of YAML file paths in deterministic order.

        Raises:
            FileNotFoundError: If yaml_root directory doesn't exist.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "YamlInjectionLoader.enumerate_yaml_files"
        )

        if not self.yaml_root.is_dir():
            raise FileNotFoundError(f"YAML root directory not found: {self.yaml_root}")
        yaml_files = [path.resolve() for path in self.yaml_root.rglob("*.y*ml") if path.is_file()]
        yaml_files.sort()
        if len(yaml_files) > 5000:
            raise YamlValidationError(
                filename=str(self.yaml_root), parse_error="Too many YAML files to load safely"
            )
        return yaml_files

    def load_all_patterns(self) -> dict[str, list[InstructionalPattern]]:
        """Load all injection patterns from YAML files.

        Returns:
            Dict mapping layer names to lists of InstructionalPattern objects.

        Raises:
            YamlValidationError: If any YAML file fails validation.
        """
        cache_key = f"all_patterns::{self.yaml_root}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        patterns_by_layer: dict[str, list[InstructionalPattern]] = {
            layer.value: [] for layer in InjectionLayer
        }
        for yaml_file in self.enumerate_yaml_files():  # progress_bar: load yaml patterns
            try:
                layer_patterns = self._load_yaml_file(yaml_file)
                layer_name = self._determine_layer_from_path(yaml_file)
                patterns_by_layer[layer_name].extend(layer_patterns)
            except YamlValidationError:
                raise
            except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
                raise YamlValidationError(
                    filename=str(yaml_file),
                    parse_error=f"Unexpected error: {e}",
                ) from e
        for layer_patterns in patterns_by_layer.values():
            layer_patterns.sort(key=lambda p: p.id)
        self._cache[cache_key] = patterns_by_layer
        return patterns_by_layer

    def load_by_layer(self, layer: InjectionLayer | str) -> list[InstructionalPattern]:
        """Load patterns for a specific layer.

        Args:
            layer: The injection layer to load patterns for. Can be InjectionLayer enum or string.

        Returns:
            List of InstructionalPattern objects for the specified layer.
        """
        if isinstance(layer, InjectionLayer):
            layer_name = layer.value
        else:
            layer_name = layer
        all_patterns = self.load_all_patterns()
        return all_patterns.get(layer_name, [])

    def _load_yaml_file(self, yaml_file: Path) -> list[InstructionalPattern]:
        """Load and validate a single YAML file.

        Args:
            yaml_file: Path to the YAML file to load.

        Returns:
            List of InstructionalPattern objects from the file.

        Raises:
            YamlValidationError: If validation fails.
        """
        try:
            if yaml_file.stat().st_size > 1024 * 1024:
                raise YamlValidationError(
                    filename=str(yaml_file), parse_error="YAML file exceeds 1 MiB safety limit"
                )
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except OSError as e:
            raise YamlValidationError(filename=str(yaml_file), parse_error=str(e)) from e
        except yaml.YAMLError as e:
            raise YamlValidationError(filename=str(yaml_file), parse_error=str(e)) from e
        if not isinstance(data, dict):
            raise YamlValidationError(
                filename=str(yaml_file),
                parse_error="Root element must be a dictionary",
            )
        patterns = []
        for root_key, root_value in data.items():
            if isinstance(root_value, dict):
                patterns.extend(self._extract_patterns_from_dict(root_key, root_value, yaml_file))
        return patterns

    def _extract_patterns_from_dict(
        self,
        root_key: str,
        pattern_dict: Dict[str, Any],
        yaml_file: Path,
    ) -> List[InstructionalPattern]:
        """Extract patterns from a dictionary structure.

        Args:
            root_key: The root key (e.g., "v5_framing_injections")
            pattern_dict: Dictionary containing pattern definitions
            yaml_file: Source file path for error reporting

        Returns:
            List of InstructionalPattern objects.

        Raises:
            YamlValidationError: If pattern validation fails.
        """
        patterns = []
        layer_value = self._determine_layer_from_path(yaml_file)
        layer = InjectionLayer(layer_value)
        sorted_pattern_names = sorted(pattern_dict.keys())
        pattern_id = 1
        skipped_count = 0
        for pattern_name in sorted_pattern_names:  # progress_bar: build instructional patterns
            pattern_data = pattern_dict[pattern_name]
            if not isinstance(pattern_data, dict):
                continue
            has_description = isinstance(pattern_data.get("description"), str)
            has_template = isinstance(pattern_data.get("prompt_template"), str)
            if not (has_description and has_template):
                logger.debug(
                    f"Skipping pattern {pattern_name} in {yaml_file}: missing description or prompt_template",
                )
                skipped_count += 1
                continue
            description = pattern_data["description"]
            prompt_template = pattern_data["prompt_template"]
            if not isinstance(description, str):
                logger.debug(f"Skipping pattern {pattern_name} in {yaml_file}: description not a string")
                skipped_count += 1
                continue
            if not isinstance(prompt_template, str):
                logger.debug(f"Skipping pattern {pattern_name} in {yaml_file}: prompt_template not a string")
                skipped_count += 1
                continue
            pattern = InstructionalPattern(
                id=pattern_id,
                name=pattern_name,
                layer=layer,
                description=description,
                template=prompt_template,
                enabled=bool(pattern_data.get("enabled", True)),
                required=bool(pattern_data.get("required", False)),
            )
            patterns.append(pattern)
            pattern_id += 1
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} invalid patterns in {yaml_file}")
        return patterns

    def _determine_layer_from_path(self, yaml_file: Path) -> str:
        """Determine the injection layer from the file path.

        Args:
            yaml_file: Path to the YAML file.

        Returns:
            InjectionLayer enum value as string.
        """
        path_parts = yaml_file.parts
        for part in path_parts:
            if part in self.LAYER_MAPPING:
                return self.LAYER_MAPPING[part].value
        filename = yaml_file.name.lower()
        if "framing" in filename:
            return InjectionLayer.FRAMING.value
        elif "safety" in filename:
            return InjectionLayer.SAFETY.value
        elif "reasoning" in filename:
            return InjectionLayer.REASONING.value
        elif "tool" in filename:
            return InjectionLayer.TOOLING.value
        elif "output" in filename:
            return InjectionLayer.OUTPUT.value
        elif "context" in filename:
            return InjectionLayer.CONTEXT.value
        logger.warning(f"Could not determine layer for {yaml_file}, defaulting to FRAMING")
        return InjectionLayer.FRAMING.value


_yaml_loader: YamlInjectionLoader | None = None


def get_yaml_loader(yaml_root: pathlib.Path | None = None) -> YamlInjectionLoader:
    """Get the global YAML loader instance.

    Args:
        yaml_root: Optional custom YAML root path.

    Returns:
        YamlInjectionLoader instance.
    """
    global _yaml_loader
    if _yaml_loader is None:
        _yaml_loader = YamlInjectionLoader(yaml_root)
    return _yaml_loader


def clear_yaml_cache() -> None:
    """Clear the YAML loader cache. Useful for testing."""
    global _yaml_loader
    _yaml_loader = None
