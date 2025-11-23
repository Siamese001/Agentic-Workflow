from __future__ import annotations

"""Core L4 state shim for v10_10 tests.

Re-exports the snapshot-local ``l4`` module so imports like
``from core.l4 import *`` work when tests are run with
rootdir=Agentic-Workflow-10_10.
"""

from l4 import *  # noqa: F401,F403
