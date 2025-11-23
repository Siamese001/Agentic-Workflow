"""Snapshot-local core.routing façade for v10_10 tests.

When running tests with rootdir=Agentic-Workflow-10_10, the ``core`` package
resolves to this directory. This module re-exports the v10_10 routing module
so imports like ``from core.routing import RoutingPolicy`` continue to work.
"""

from routing import *  # noqa: F401,F403
