"""Compatibility exports for the runtime ADG materializer.

The canonical implementation lives in
``agentic_core.L6_system_learning.runtime_adg.materializer``.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.runtime_adg.materializer import (
    RuntimeADGMaterializer,
    _TRUNCATED_SUFFIX,
    _cap_attributes_json,
    _extract_node,
    _extract_semantic_edges,
    _redact_tool_content,
)

__all__ = [
    "RuntimeADGMaterializer",
    "_TRUNCATED_SUFFIX",
    "_cap_attributes_json",
    "_extract_node",
    "_extract_semantic_edges",
    "_redact_tool_content",
]
