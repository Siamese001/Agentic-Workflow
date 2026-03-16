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
from typing import Any

import yaml

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .injection_layer_config import InjectionLayer, InstructionalPattern

_emit_applies_guardrail("p0", "yaml_injection_loader", "p0_governance")
_emit_reads_policy_state("p0", "yaml_injection_loader", "policy_binding")
_emit_snapshots_state("p0", "yaml_injection_loader", "state_snapshot")
emit_replay_key("p0", "yaml_injection_loader")
emit_determinism_digest("p0", "yaml_injection_loader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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

    def __init__(self, yaml_root: pathlib.Path | None = None):
        """Initialize the YAML loader.

        Args:
            yaml_root: Root path to YAML injections directory.
                      Defaults to data/prompt_governance/injections
        """
        if yaml_root is None:
            yaml_root = Path("data/prompt_governance/injections")
        self.yaml_root = Path(yaml_root)
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "YamlInjectionLoader.enumerate_yaml_files")

        if not self.yaml_root.exists():
            raise FileNotFoundError(f"YAML root directory not found: {self.yaml_root}")
        yaml_files = list(self.yaml_root.rglob("*.y*ml"))
        yaml_files.sort()
        return yaml_files

    def load_all_patterns(self) -> dict[str, list[InstructionalPattern]]:
        """Load all injection patterns from YAML files.

        Returns:
            Dict mapping layer names to lists of InstructionalPattern objects.

        Raises:
            YamlValidationError: If any YAML file fails validation.
        """
        if "all_patterns" in self._cache:
            return self._cache["all_patterns"]
        patterns_by_layer: dict[str, list[InstructionalPattern]] = {
            layer.value: [] for layer in InjectionLayer
        }
        for yaml_file in self.enumerate_yaml_files():
            try:
                layer_patterns = self._load_yaml_file(yaml_file)
                layer_name = self._determine_layer_from_path(yaml_file)
                patterns_by_layer[layer_name].extend(layer_patterns)
            except YamlValidationError:
                raise
            except Exception as e:
                raise YamlValidationError(
                    filename=str(yaml_file), parse_error=f"Unexpected error: {e}"
                ) from e
        for layer_patterns in patterns_by_layer.values():
            layer_patterns.sort(key=lambda p: p.id)
        self._cache["all_patterns"] = patterns_by_layer
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
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise YamlValidationError(filename=str(yaml_file), parse_error=str(e)) from e
        if not isinstance(data, dict):
            raise YamlValidationError(
                filename=str(yaml_file), parse_error="Root element must be a dictionary"
            )
        patterns = []
        for root_key, root_value in data.items():
            if isinstance(root_value, dict):
                patterns.extend(self._extract_patterns_from_dict(root_key, root_value, yaml_file))
        return patterns

    def _extract_patterns_from_dict(
        self, root_key: str, pattern_dict: Dict[str, Any], yaml_file: Path
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
        for pattern_name in sorted_pattern_names:
            pattern_data = pattern_dict[pattern_name]
            if not isinstance(pattern_data, dict):
                continue
            has_description = isinstance(pattern_data.get("description"), str)
            has_template = isinstance(pattern_data.get("prompt_template"), str)
            if not (has_description and has_template):
                logger.debug(
                    f"Skipping pattern {pattern_name} in {yaml_file}: missing description or prompt_template"
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
                enabled=pattern_data.get("enabled", True),
                required=pattern_data.get("required", False),
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
