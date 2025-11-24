from __future__ import annotations

"""Stable entry point for the core set of "thinking" agents.

This file exists so that older and newer parts of the system can all refer
to the same collection of cognitive agents, even if they import them using
slightly different paths. In business terms, it is a stable front door to
the agents that plan, reason, and review during the resume workflow.

By keeping this entry point consistent while the code evolves underneath, the
project can improve its internal design without disrupting the way resumes
are analyzed and upgraded. That stability helps maintain output quality over
time and reduces the risk of regressions in how experience, skills, and job
fit are evaluated.
"""

from cognitive_agents import *  # noqa: F401,F403
