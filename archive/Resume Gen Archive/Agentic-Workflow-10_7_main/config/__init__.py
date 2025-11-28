"""Centralised configuration helpers for Agentic Workflow v10.7."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from mcp import get_schema


def load_master_config() -> Dict[str, Any]:
    """Return a mutable copy of the shared master configuration."""

    schema = get_schema("master_config_v10_7.json")
    return deepcopy(schema)


CONFIG: Dict[str, Any] = load_master_config()

__all__ = ["CONFIG", "load_master_config"]
