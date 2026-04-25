"""
configuration Loader.

Handles loading, parsing, and validating JSON configurations against Pydantic schemas.
"""

import json
import logging
from pathlib import Path

from .archetype_indicator_config import AgentSpecs
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    THRESHOLD,
)

# Configuration constants

# Module-level cache
_AGENT_SPECS_CACHE: AgentSpecs | None = None


def get_config_path() -> Path:
    """Returns the directory containing configuration files."""
    return Path(__file__).parent


def load_agent_specs(force_reload: bool = False) -> AgentSpecs:
    """
    Loads and validates the agent_specs.json file.

    Args:
        force_reload: If True, ignores cache and reloads from disk.

    Returns:
        AgentSpecs: A validated, type-safe configuration object.

    Raises:
        FileNotFoundError: If the config file is missing.
        ValidationError: If the JSON does not match the schema.
    """
    global _AGENT_SPECS_CACHE

    if _AGENT_SPECS_CACHE and not force_reload:
        return _AGENT_SPECS_CACHE

    config_path = get_config_path() / "agent_specs.json"

    if not config_path.exists():
        raise FileNotFoundError(f"configuration file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            raw_data = json.load(f)

        # Validate via Pydantic
        specs = AgentSpecs(**raw_data)

        # Update cache
        _AGENT_SPECS_CACHE = specs
        return specs

    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        logging.error(f"Failed to load agent specs: {e}")
        raise
