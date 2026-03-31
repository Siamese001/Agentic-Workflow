"""
Activation gate seam contract — re-exports L5 activation guard for L2 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from agentic_core.L5_safety.enforcement.activation_gate import (
    assert_activation_allowed,
)

__all__ = ["assert_activation_allowed"]
