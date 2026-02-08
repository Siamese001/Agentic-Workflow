"""
agentic_core.core — Zero-dependency foundation modules.

This package contains foundational definitions (enums, types, kernel logic)
that ANY layer (L0–L6, Runtime, Apps) can safely import without risking
circular dependencies.

RULE: Modules in this package must use ONLY the Python standard library.
"""
