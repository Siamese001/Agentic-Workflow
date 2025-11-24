from __future__ import annotations

"""Entry point for the workflow's shared state layer.

This file provides a stable ``core.l4`` import path that forwards to the
snapshot-specific ``l4`` module. In practice, this is the layer that manages
shared state across steps in the workflow — for example, keeping track of
what has already been analyzed, drafted, or flagged for review.

Reliable handling of this state is important for resume quality and
traceability. It helps ensure that decisions made earlier in the process are
respected later on, so the final resume tells a consistent story and avoids
contradictions or repeated work.
"""

from l4 import *  # noqa: F401,F403
