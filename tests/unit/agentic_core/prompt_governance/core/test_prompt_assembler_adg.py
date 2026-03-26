"""ADG importability contract for agentic_core/prompt_governance/core/prompt_assembler.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.core.prompt_assembler  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.core.prompt_assembler  # noqa: F401
    """Module prompt_assembler must be importable."""
    assert agentic_core.prompt_governance.core.prompt_assembler is not None
