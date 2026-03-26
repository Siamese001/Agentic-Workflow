"""ADG importability contract for agentic_core/prompt_governance/scripts/file_intent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.scripts.file_intent  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.scripts.file_intent  # noqa: F401
    """Module file_intent must be importable."""
    assert agentic_core.prompt_governance.scripts.file_intent is not None
