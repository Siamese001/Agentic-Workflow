from __future__ import annotations

"""Snapshot-local runtime.trace package for v10_10 tests.

This ensures that imports like
    from runtime.trace.trace_reconstruction import get_routing_trace
resolve correctly when tests are run with rootdir=Agentic-Workflow-10_10.

The implementation of get_routing_trace lives in trace_reconstruction.py in
this package and mirrors the real runtime.trace helper at the repo root.
"""

from .trace_reconstruction import get_routing_trace  # noqa: F401
