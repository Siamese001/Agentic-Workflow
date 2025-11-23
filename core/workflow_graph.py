from __future__ import annotations

"""Core workflow_graph shim for v10_10 tests.

Re-exports the snapshot-local ``workflow_graph`` module so imports like
``from core.workflow_graph import run_workflow_graph`` work when tests are
run with rootdir=Agentic-Workflow-10_10.
"""

from workflow_graph import *  # noqa: F401,F403
