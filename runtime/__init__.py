"""Snapshot-local runtime package shim for v10_10 tests.

When tests are run with rootdir=Agentic-Workflow-10_10, the name ``runtime``
resolves to this package. This shim ensures that imports like
``from runtime.observability import start_span`` are forwarded to the real
runtime package defined at the repo root.
"""

from __future__ import annotations

import importlib
import os
import sys

# Ensure the repo root (parent of Agentic-Workflow-10_10) is on sys.path
_PARENT = os.path.dirname(os.path.dirname(__file__))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

# Import the real top-level runtime package
_real_runtime = importlib.import_module("runtime")

# Ensure key submodules are importable via this shim
for _sub in [
    "runtime.observability",
    "runtime.runtime_utils",
    "runtime.trace",
    "runtime.trace.trace_reconstruction",
]:
    try:
        sys.modules[_sub] = importlib.import_module(_sub)
    except Exception:
        # Best-effort; tests should still be able to import these modules
        # if they exist in the real package at the repo root.
        pass

# Re-export everything from the real runtime package for convenience
from runtime import *  # noqa: F401,F403
