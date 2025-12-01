"""Human-in-the-loop interface module."""

import copy


def apply_hil_feedback(state, feedback):
    """Return a deep-copied state updated with human-in-the-loop feedback."""

    new_state = copy.deepcopy(state) if state is not None else {}
    new_state["hil_feedback"] = feedback
    return new_state
