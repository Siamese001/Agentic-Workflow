"""Centralised configuration helpers for Agentic Workflow v10.7."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.mcp import get_schema  # INVALID: Cannot import from path with hyphens


def load_master_config() -> Dict[str, object]:
    """Return a mutable copy of the shared master configuration."""

    schema = get_schema("master_config_v10_7.json")
    return deepcopy(schema)


CONFIG: Dict[str, object] = load_master_config()

__all__ = ["CONFIG", "load_master_config"]
