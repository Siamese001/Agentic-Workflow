"""ADG importability contract for agentic_core/prompt_governance/core/evaluation_loader.py."""
from __future__ import annotations

import agentic_core.prompt_governance.core.evaluation_loader  # noqa: F401


def test_module_importable():
    """Module evaluation_loader must be importable."""
    assert agentic_core.prompt_governance.core.evaluation_loader is not None
