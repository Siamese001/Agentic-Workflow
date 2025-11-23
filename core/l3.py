from __future__ import annotations

"""Core L3 orchestration shim for v10_10 tests.

Re-exports the snapshot-local ``l3`` module so imports like
``from core.l3 import run_dag`` work when tests are run with
rootdir=Agentic-Workflow-10_10.
"""

from l3 import *  # noqa: F401,F403
