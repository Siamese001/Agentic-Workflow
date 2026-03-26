"""ADG importability contract for agentic_core/L5_safety/reasoning/GitHygieneAgent.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.reasoning.GitHygieneAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.reasoning.GitHygieneAgent  # noqa: F401
    """Module GitHygieneAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.GitHygieneAgent is not None
