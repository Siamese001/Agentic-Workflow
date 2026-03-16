"""
Centralized Configuration Loader System
Phase 1 Optimization - Configuration Extraction

Provides unified configuration loading for all agents with support for:
- YAML and JSON configuration files
- Environment variable overrides
- Configuration validation
- Hot reloading capabilities
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "config_loader_util", "p0_governance")
_emit_reads_policy_state("p0", "config_loader_util", "policy_binding")
_emit_snapshots_state("p0", "config_loader_util", "state_snapshot")
emit_replay_key("p0", "config_loader_util")
emit_determinism_digest("p0", "config_loader_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class ConfigLoadResult:
    """Result of configuration loading operation."""

    success: bool
    config: dict[str, Any]
    errors: list[str]
    source: str


class ConfigLoader:
    """
    Centralized configuration loader for agent configurations.

    Supports loading from:
    - YAML files in config/agent_configs/
    - JSON files in config/agent_configs/
    - Environment variable overrides
    - Fallback to hardcoded values
    """

    def __init__(self, config_root: str | Path | None = None):
        """Initialize config loader with root directory."""
        self.config_root = Path(config_root or "config/agent_configs")
        self._cache: dict[str, ConfigLoadResult] = {}

    def load_config(
        self,
        agent_name: str,
        config_file: str | None = None,
        fallback_config: dict[str, Any] | None = None,
    ) -> ConfigLoadResult:
        """
        Load configuration for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., "ats_compatibility")
            config_file: Optional specific config file name
            fallback_config: Optional fallback configuration if file not found

        Returns:
            ConfigLoadResult with loaded configuration or errors
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigLoader.load_config")

        cache_key = f"{agent_name}:{config_file or 'default'}"

        # Check cache first
        # guardian: allow-config-with-logic
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Determine config file path
        # guardian: allow-config-with-logic
        if config_file:
            config_path = self.config_root / config_file
        else:
            config_path = self._find_config_file(agent_name)

        result = self._load_from_file(config_path, fallback_config)

        # Apply environment variable overrides
        # guardian: allow-config-with-logic
        if result.success:
            result = self._apply_env_overrides(result, agent_name)

        # Cache the result
        self._cache[cache_key] = result
        return result

    def _find_config_file(self, agent_name: str) -> Path:
        """Find configuration file for agent name."""
        # Try YAML first
        yaml_path = self.config_root / f"{agent_name}.yaml"
        if yaml_path.exists():
            return yaml_path

        # Try JSON
        json_path = self.config_root / f"{agent_name}.json"
        if json_path.exists():
            return json_path

        # Return default YAML path (will trigger file not found error)
        return yaml_path

    def _load_from_file(
        self,
        config_path: Path,
        fallback_config: dict[str, Any] | None = None,
    ) -> ConfigLoadResult:
        """Load configuration from file."""
        try:
            if not config_path.exists():
                if fallback_config:
                    return ConfigLoadResult(
                        success=True,
                        config=fallback_config,
                        errors=[f"Config file {config_path} not found, using fallback"],
                        source="fallback",
                    )
                else:
                    return ConfigLoadResult(
                        success=False,
                        config={},
                        errors=[f"Config file {config_path} not found and no fallback provided"],
                        source="none",
                    )

            with open(config_path, encoding="utf-8") as f:
                if config_path.suffix.lower() == ".yaml" or config_path.suffix.lower() == ".yml":
                    if not YAML_AVAILABLE:
                        return ConfigLoadResult(
                            success=False,
                            config={},
                            errors=["PyYAML not installed. Install with: pip install pyyaml"],
                            source="none",
                        )
                    config = yaml.safe_load(f)
                elif config_path.suffix.lower() == ".json":
                    config = json.load(f)
                else:
                    return ConfigLoadResult(
                        success=False,
                        config={},
                        errors=[f"Unsupported config file format: {config_path.suffix}"],
                        source="none",
                    )

            return ConfigLoadResult(
                success=True,
                config=config or {},
                errors=[],
                source=str(config_path),
            )

        except Exception as e:
            return ConfigLoadResult(
                success=False,
                config={},
                errors=[f"Failed to load config from {config_path}: {str(e)}"],
                source="none",
            )

    def _apply_env_overrides(self, result: ConfigLoadResult, agent_name: str) -> ConfigLoadResult:
        """Apply environment variable overrides to configuration."""
        env_prefix = f"AGENT_CONFIG_{agent_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix) :].lower()

                # Try to parse as JSON, fallback to string
                try:
                    parsed_value = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    parsed_value = value

                # Set nested key using dot notation
                self._set_nested_key(result.config, config_key, parsed_value)

        return result

    def _set_nested_key(self, config: dict[str, Any], key: str, value: Any) -> None:
        """Set nested configuration key using dot notation."""
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def reload_config(self, agent_name: str, config_file: str | None = None) -> ConfigLoadResult:
        """Force reload of configuration (clears cache)."""
        cache_key = f"{agent_name}:{config_file or 'default'}"
        # guardian: allow-config-with-logic
        if cache_key in self._cache:
            del self._cache[cache_key]
        return self.load_config(agent_name, config_file)

    def validate_config(
        self,
        config: dict[str, Any],
        schema: dict[str, Any] | None = None,
    ) -> ConfigLoadResult:
        """Validate configuration against optional schema."""
        errors = []

        # Basic validation - ensure config is a dictionary
        # guardian: allow-config-with-logic
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return ConfigLoadResult(success=False, config={}, errors=errors, source="validation")

        # Schema validation if provided
        # guardian: allow-config-with-logic
        if schema:
            errors.extend(self._validate_against_schema(config, schema))

        return ConfigLoadResult(
            success=len(errors) == 0,
            config=config,
            errors=errors,
            source="validation",
        )

    def _validate_against_schema(self, config: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Validate configuration against schema (basic implementation)."""
        errors = []

        for key, expected_type in schema.items():
            if key not in config:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(config[key], expected_type):
                errors.append(
                    f"Key {key} should be {expected_type.__name__}, got {type(config[key]).__name__}",
                )

        return errors


# Global config loader instance
_config_loader = None


def get_config_loader(config_root: str | Path | None = None) -> ConfigLoader:
    """Get global config loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_root)
    return _config_loader


def load_agent_config(
    agent_name: str,
    config_file: str | None = None,
    fallback_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convenience function to load agent configuration.

    Args:
        agent_name: Name of the agent
        config_file: Optional specific config file
        fallback_config: Optional fallback configuration

    Returns:
        Loaded configuration dictionary

    Raises:
        RuntimeError: If configuration fails to load and no fallback provided
    """
    loader = get_config_loader()
    result = loader.load_config(agent_name, config_file, fallback_config)

    # guardian: allow-config-with-logic
    if not result.success:
        raise RuntimeError(f"Failed to load config for {agent_name}: {'; '.join(result.errors)}")

    return result.config
