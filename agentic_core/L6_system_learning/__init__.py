"""Forward-import alias for `system_learning` (L6 active surface).

Doctrinally, `system_learning` is the active half of L6 (the passive half is
`agentic_core.L6_observability`). For historical reasons the package sits at
repo root rather than under `agentic_core/L6_<name>/`. This alias provides
the doctrinally-prefixed import path without forcing the rename.

Both paths are first-class. There is **no DeprecationWarning** and **no
removal target**. Use whichever fits the calling code's conventions:

    from system_learning import meta_learning           # historical
    from agentic_core.L6_system_learning import meta_learning  # doctrinal

The alias re-binds existing module objects via `sys.modules` so submodule
state is shared (no double-load).

Plan: `.windsurf/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md` W2.
"""
from __future__ import annotations

import importlib
import sys

import system_learning as _sl

# Inherit layer markers from the canonical package so introspection works
# identically through either path.
__layer__ = getattr(_sl, "__layer__", "L6")
__l6_surface__ = getattr(_sl, "__l6_surface__", "active")

# Mirror __all__ when the canonical package defines one; otherwise leave
# unset so star-import surfaces match upstream behavior.
_sl_all = getattr(_sl, "__all__", None)
if _sl_all is not None:
    __all__ = list(_sl_all)

# Re-bind every existing system_learning.<sub> module under this alias so
# `from agentic_core.L6_system_learning import <sub>` and
# `from agentic_core.L6_system_learning.<sub>.<x> import Y` both work and
# share state with the canonical path.
_SUBPACKAGES = (
    "adapters",
    "adg",
    "arbitration",
    "buses",
    "confidence",
    "config",
    "constraints",
    "correlation",
    "embedding",
    "enforcement",
    "engines",
    "fingerprinting",
    "golden",
    "invariants",
    "logs",
    "memory",
    "meta_learning",
    "ml_integration",
    "monitoring",
    "output",
    "pipelines",
    "policy",
    "ports",
    "provenance",
    "raw",
    "rubrics",
    "runtime",
    "runtime_adg",
    "scripts",
    "snapshots",
    "state",
    "stores",
    "telemetry",
    "types",
    "validators",
)

for _sub in _SUBPACKAGES:
    try:
        _mod = importlib.import_module(f"system_learning.{_sub}")
    except ImportError:
        # Subpackage may have no __init__.py (data dir) or may have been
        # removed. Skip silently — alias is best-effort, not authoritative.
        continue
    sys.modules[f"agentic_core.L6_system_learning.{_sub}"] = _mod

# Also re-bind top-level non-package modules that callers may import directly.
for _topmod in ("runtime_hitl_consumer", "v6_contract_map", "_tracing"):
    try:
        _mod = importlib.import_module(f"system_learning.{_topmod}")
    except ImportError:
        continue
    sys.modules[f"agentic_core.L6_system_learning.{_topmod}"] = _mod

# Clean up loop locals so they don't pollute the package namespace.
# Use globals().pop with default to tolerate the (unreachable) case where
# every importlib call skipped and a loop variable was never bound.
for _name in ("_sub", "_topmod", "_mod", "_sl_all"):
    globals().pop(_name, None)
del _name
