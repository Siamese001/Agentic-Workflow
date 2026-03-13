"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

import importlib as _importlib

_mod = _importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
DagRuntimeInspectorAgent = _mod.InspectorExecutor
__all__ = ["DagRuntimeInspectorAgent"]
