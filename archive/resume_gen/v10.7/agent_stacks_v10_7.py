"""Compatibility layer that re-exports stack agents for v10.7."""

from stacks_v10_7 import *  # noqa: F401,F403
from stacks_v10_7 import __all__ as _STACK_EXPORTS

from core_v10_7 import wrap_mcp

__all__ = list(_STACK_EXPORTS) + ["wrap_mcp"]
