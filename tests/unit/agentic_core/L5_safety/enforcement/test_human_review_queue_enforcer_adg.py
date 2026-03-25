"""ADG importability contract for agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.human_review_queue_enforcer  # noqa: F401


def test_module_importable():
    """Module human_review_queue_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.human_review_queue_enforcer is not None
