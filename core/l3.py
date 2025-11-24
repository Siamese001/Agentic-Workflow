from __future__ import annotations

"""Entry point for the orchestration layer that runs the workflow.

This file exists so that higher-level code can call orchestration helpers
through a consistent ``core.l3`` path, even as the underlying implementation
lives in a snapshot-specific ``l3`` module. In business terms, it is the
stable doorway into the part of the system that actually runs the sequence of
steps which improve a resume.

By keeping this entry point stable, teams can evolve how the workflow is
scheduled and executed without breaking existing integrations. That makes it
safer to refine the orchestration that decides the order of planning,
retrieval, drafting, and review, which directly impacts how thorough and
well-structured the final resume is.
"""

from l3 import *  # noqa: F401,F403
