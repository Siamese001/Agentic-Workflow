"""Structure Blueprint YAML Loader.

Loads territory and layer definitions from hardcoded constants.
Maintains backward compatibility with existing Python imports.
"""

from __future__ import annotations

from typing import Any

# Cache for loaded data
_loaded_data: dict[str, Any] = {}


def load_territories() -> dict[str, Any]:
    """Load territory definitions from hardcoded constants."""
    if "territories" not in _loaded_data:
        _loaded_data["territories"] = {
            "schema_version": "1.0.0",
            "last_updated": "2026-04-05",
            "territories": {
                "__root__": {
                    "depth": 0,
                    "type": "root",
                    "purpose": "Project root — allowed files only, no subdirectories except whitelisted territories",
                    "allowed_files": [
                        "README.md",
                        "AGENTS.md",
                        "ARCHITECTURE_LAYERS.md",
                        "conftest.py",
                        "pyproject.toml",
                        "pyrightconfig.json",
                        "pytest.ini",
                        ".codeiumignore",
                        ".env",
                        ".gitattributes",
                        ".gitignore",
                        ".pre-commit-config.yaml",
                        ".pylintrc",
                    ],
                    "allowed_patterns": [
                        "trace_*.jsonl",
                        "mission_*.log",
                        "*.bat",
                        "*.sh",
                        "root_drift_*.py",
                    ],
                },
                "config": {
                    "depth": 2,
                    "type": "configuration",
                    "purpose": "Project configuration and SSOT definitions",
                    "subfolders": {
                        "structure_blueprint": {
                            "depth": 2,
                            "purpose": "SSOT territory and layer definitions",
                            "allowed_suffixes": [".yaml"],
                            "forbidden_suffixes": [".py"],
                        },
                        "schemas": {
                            "depth": 2,
                            "purpose": "JSON schema definitions",
                            "allowed_suffixes": [".json"],
                            "forbidden_suffixes": [".yaml", ".py"],
                        },
                    },
                },
            },
        }
    return _loaded_data["territories"]


def load_layer_overrides() -> dict[str, Any]:
    """Load layer override definitions from hardcoded constants."""
    if "layers" not in _loaded_data:
        _loaded_data["layers"] = {
            "schema_version": "1.1.0",
            "last_updated": "2026-04-06",
            "overrides": {
                "L0_routing": {
                    "purpose": "Core Logic & Routing + Control-Plane Core — ingestion, route election, capability arbitration, policy-aware dispatch; plus boot integrity, SSOT discovery, and guardian runner health checks.",
                    "forbidden_capabilities": [
                        "debate",
                        "synthesis",
                        "complex_reasoning",
                        "multi_agent_coordination",
                    ],
                    "routing_rules": {
                        "*_guardian.py": "enforcement",
                        "*_boot*.py": "enforcement",
                        "*_routing*.py": "enforcement",
                        "*_dispatch*.py": "enforcement",
                        "*_config.py": "config",
                        "*_types.py": "types",
                        "*Agent.py": "reasoning",
                    },
                    "extra_subfolders": {
                        "scripts": {
                            "purpose": "Operational scripts (Zero-Ambiguity Standard)",
                            "subfolders": {
                                ".github": {"purpose": "GitHub workflow scripts"},
                                "ci": {"purpose": "CI/CD pipeline scripts"},
                                "config": {"purpose": "Configuration scripts"},
                                "installation": {"purpose": "Installation and setup scripts"},
                                "general_scripts": {"purpose": "General maintenance scripts"},
                            },
                        }
                    },
                }
            },
        }
    return _loaded_data["layers"]


def load_ast_signals() -> dict[str, Any]:
    """Load AST signal definitions from hardcoded constants."""
    if "ast_signals" not in _loaded_data:
        _loaded_data["ast_signals"] = {"schema_version": "1.0.0", "last_updated": "2026-04-05", "signals": {}}
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
