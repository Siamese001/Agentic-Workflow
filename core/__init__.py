"""Central engine that wires together planning, execution, agent reasoning, routing, and workflow graphs so resumes are improved in a consistent, high-quality way over time.

Note: Layer modules (l1, l2, l3, l4, l5), cognitive_agents, and workflow_graph
are now imported directly from the root level, not from core.

Example:
    import l1
    from cognitive_agents import StrategyLLMAgent
    from workflow_graph import run_workflow_graph
"""

from . import routing  # noqa: F401
