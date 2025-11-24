from __future__ import annotations

"""Entry point for the workflow's safety and gating layer.

This file exposes a stable ``core.l5`` import path that forwards to the
snapshot-specific ``l5`` module. Conceptually, this layer is where safety
gates and final checks live — the logic that decides whether a resume output
is acceptable to return or needs to be revised or blocked.

By keeping this safety entry point stable, the system can evolve how it
detects and handles risky or low-quality content without breaking callers.
That flexibility is important for maintaining trustworthy, professional
resumes that reflect well on both candidates and the organizations using the
workflow.
"""

from l5 import *  # noqa: F401,F403
