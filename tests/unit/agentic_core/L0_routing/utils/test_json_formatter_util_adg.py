"""ADG importability contract for agentic_core/L0_routing/utils/json_formatter_util.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L0_routing.utils.json_formatter_util  # noqa: F401


def test_module_importable():
    import agentic_core.L0_routing.utils.json_formatter_util  # noqa: F401
    """Module json_formatter_util must be importable."""
    assert agentic_core.L0_routing.utils.json_formatter_util is not None
