"""ADG importability contract for apps_shared/types/judge_evaluator_types.py."""
from __future__ import annotations


def test_module_importable():
    """Module judge_evaluator_types must be importable."""
    import apps_shared.types.judge_evaluator_types  # noqa: F401

    assert apps_shared.types.judge_evaluator_types is not None
