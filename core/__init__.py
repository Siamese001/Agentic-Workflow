"""Core orchestration and cognitive logic (L1–L5).

This package provides the primary entrypoints for planning and execution
layers when running tests with rootdir=Agentic-Workflow-10_10.

Top-level modules (l1, l2, cognitive_agents, routing, workflow_graph) are maintained as
shims for backward compatibility with the snapshot layout.
"""

from . import l1  # noqa: F401
from . import l2  # noqa: F401
from . import cognitive_agents  # noqa: F401
from . import routing  # noqa: F401
from . import workflow_graph  # noqa: F401
