from __future__ import annotations

"""Core L5 safety shim for v10_10 tests.

Re-exports the snapshot-local ``l5`` module so imports like
``from core.l5 import safety_gate`` work when tests are run with
rootdir=Agentic-Workflow-10_10.
"""

from l5 import *  # noqa: F401,F403
