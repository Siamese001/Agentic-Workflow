"""ADG importability contract for agentic_core/evaluation/judges/llm_judge.py."""
from __future__ import annotations

import agentic_core.evaluation.judges.llm_judge  # noqa: F401


def test_module_importable():
    """Module llm_judge must be importable."""
    assert agentic_core.evaluation.judges.llm_judge is not None
