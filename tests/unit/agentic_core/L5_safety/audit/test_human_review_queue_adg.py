"""ADG importability contract for agentic_core/L5_safety/audit/human_review_queue.py."""
from __future__ import annotations

import agentic_core.L5_safety.audit.human_review_queue  # noqa: F401


def test_module_importable():
    """Module human_review_queue must be importable."""
    assert agentic_core.L5_safety.audit.human_review_queue is not None
