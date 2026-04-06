"""Structure Blueprint YAML Loader.

Loads territory and layer definitions from YAML files.
Maintains backward compatibility with existing Python imports.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Cache for loaded data
_loaded_data: dict[str, Any] = {}


def _get_config_dir() -> Path:
    """Get the config directory path."""
    return Path(__file__).parent.parent.parent.parent.parent / "config" / "structure_blueprint"


def load_territories() -> dict[str, Any]:
    """Load territory definitions from YAML."""
    if "territories" not in _loaded_data:
        config_path = _get_config_dir() / "territories.yaml"
        with open(config_path) as f:
            _loaded_data["territories"] = yaml.safe_load(f)
    return _loaded_data["territories"]


def load_layer_overrides() -> dict[str, Any]:
    """Load layer override definitions from YAML."""
    if "layers" not in _loaded_data:
        config_path = _get_config_dir() / "layers.yaml"
        with open(config_path) as f:
            _loaded_data["layers"] = yaml.safe_load(f)
    return _loaded_data["layers"]


def load_ast_signals() -> dict[str, Any]:
    """Load AST signal definitions from YAML."""
    if "ast_signals" not in _loaded_data:
        config_path = _get_config_dir() / "ast_signals.yaml"
        with open(config_path) as f:
            _loaded_data["ast_signals"] = yaml.safe_load(f)
    return _loaded_data["ast_signals"]


def get_territory(name: str) -> dict[str, Any] | None:
    """Get a specific territory definition."""
    data = load_territories()
    return data.get("territories", {}).get(name)


def get_layer_override(layer: str) -> dict[str, Any] | None:
    """Get override for a specific layer."""
    data = load_layer_overrides()
    return data.get("overrides", {}).get(layer)


def match_wildcard_territory(name: str) -> dict[str, Any] | None:
    """Match a name against wildcard patterns."""
    data = load_territories()
    wildcards = data.get("wildcards", {})

    import re
    for pattern_name, definition in wildcards.items():
        pattern = definition.get("pattern", "")
        if re.match(pattern, name):
            return definition
    return None


def get_all_territory_names() -> list[str]:
    """Get list of all territory names."""
    data = load_territories()
    return list(data.get("territories", {}).keys())


def get_all_layer_names() -> list[str]:
    """Get list of all layer names with overrides."""
    data = load_layer_overrides()
    return list(data.get("overrides", {}).keys())


__all__ = [
    "load_territories",
    "load_layer_overrides",
    "load_ast_signals",
    "get_territory",
    "get_layer_override",
    "match_wildcard_territory",
    "get_all_territory_names",
    "get_all_layer_names",
]
