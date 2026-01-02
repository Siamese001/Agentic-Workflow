from __future__ import annotations
"""Airlock: tools — Code Transformation and Analysis Tools."""

from agentic_core.L2_execution.ToolRegistry.tools.code_transform import (
    CodeTransformArgs,
    TransformOperation,
    TransformResult,
    code_transform,
    rename_symbol,
    extract_function,
    add_decorator,
    remove_decorator,
    quick_rename,
    quick_extract,
)

__all__ = [
    "CodeTransformArgs",
    "TransformOperation",
    "TransformResult",
    "code_transform",
    "rename_symbol",
    "extract_function",
    "add_decorator",
    "remove_decorator",
    "quick_rename",
    "quick_extract",
]
