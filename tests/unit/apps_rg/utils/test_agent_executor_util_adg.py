"""ADG importability contract for apps_rg/utils/agent_executor_util.py."""
from __future__ import annotations



def test_module_importable():
    """Module agent_executor_util must be importable."""
    import apps_rg.utils.agent_executor_util  # noqa: F401

    assert apps_rg.utils.agent_executor_util is not None