from __future__ import annotations

"""Business-facing entry point for the first planning layer.

This file exists to keep older and newer parts of the system using the same
"L1" planning logic, even if they import it in different ways. By acting as
a stable front door to the underlying planning functions, it helps ensure the
résumé workflow continues to run reliably as the codebase evolves. That
stability protects résumé quality over time, avoiding hidden breakages that
could degrade how experience is analyzed and improved for each job.
"""

from l1 import *  # noqa: F401,F403
