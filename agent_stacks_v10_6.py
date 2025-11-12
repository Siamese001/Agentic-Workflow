"""Compatibility layer that re-exports stack agents for v10.6."""

from stacks_v10_6 import *  # noqa: F401,F403
from stacks_v10_6 import __all__ as _STACK_EXPORTS

__all__ = list(_STACK_EXPORTS)
