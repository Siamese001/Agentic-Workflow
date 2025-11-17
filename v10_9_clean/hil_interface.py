"""Human-in-the-loop interface module."""

from __future__ import annotations

import copy
from typing import Any, Dict


def apply_hil_feedback(state: Dict[str, Any], feedback: Any) -> Dict[str, Any]:
    """Return a deep-copied state updated with human-in-the-loop feedback."""
    new_state = copy.deepcopy(state) if state is not None else {}
    new_state["hil_feedback"] = feedback
    return new_state

